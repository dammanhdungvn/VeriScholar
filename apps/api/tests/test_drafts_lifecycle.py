"""Automated integration tests for Research Writing Drafts Lifecycle & OCC (Module 2)."""

import base64
import io
import zipfile
from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from uuid import uuid4

import pytest
from api import app
from api.db.models.base import Base
from api.db.models.chunk import DocumentChunkModel
from api.db.models.document import DocumentModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.services.auth_service import AuthService
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


@asynccontextmanager
async def drafts_test_context() -> AsyncIterator[
    tuple[AsyncClient, async_sessionmaker[AsyncSession]]
]:
    """Provide isolated in-memory SQLite database and AsyncClient for drafts testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client, session_maker

    app.dependency_overrides.pop(get_db, None)
    await engine.dispose()


async def create_test_user(
    session_maker: async_sessionmaker[AsyncSession],
    email: str = "author@verischolar.org",
) -> tuple[UserModel, str]:
    """Helper to create an active test user in DB and return (user, jwt_token)."""
    async with session_maker() as session:
        user = UserModel(
            id=uuid4(),
            email=email,
            full_name="Lead Author",
            hashed_password=AuthService.hash_password("SecurePass123!"),
            is_active=True,
            is_verified=True,
            role="researcher",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    token = AuthService.create_token(
        payload={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta_seconds=3600,
    )
    return user, token


@pytest.mark.asyncio
async def test_draft_crud_lifecycle() -> None:
    """Verify full CRUD lifecycle: create, get, update with OCC, list, delete."""
    async with drafts_test_context() as (client, session_maker):
        _, token = await create_test_user(session_maker, "author1@verischolar.org")
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create Draft
        create_payload = {
            "title": "A Survey of Transformer Architectures",
            "content": "\\section{Introduction}\nTransformers changed NLP.",
            "format": "latex",
        }
        res = await client.post("/api/v1/drafts", json=create_payload, headers=headers)
        assert res.status_code == 201
        assert "Location" in res.headers
        assert res.headers["ETag"] == '"1"'

        body = res.json()
        assert body["data"]["title"] == "A Survey of Transformer Architectures"
        assert body["data"]["format"] == "latex"
        assert body["data"]["version"] == 1
        draft_id = body["data"]["id"]

        # 2. Get Draft
        res_get = await client.get(f"/api/v1/drafts/{draft_id}", headers=headers)
        assert res_get.status_code == 200
        assert res_get.headers["ETag"] == '"1"'
        assert res_get.json()["data"]["id"] == draft_id

        # 3. Update Draft with OCC (If-Match: "v1")
        update_payload = {
            "title": "A Survey of Vision and Language Transformers",
            "content": "\\section{Introduction}\nVision transformers also excel.",
            "version": 1,
        }
        res_update = await client.put(
            f"/api/v1/drafts/{draft_id}",
            json=update_payload,
            headers={**headers, "If-Match": '"v1"'},
        )
        assert res_update.status_code == 200
        assert res_update.headers["ETag"] == '"2"'
        updated_data = res_update.json()["data"]
        assert updated_data["version"] == 2
        assert updated_data["title"] == "A Survey of Vision and Language Transformers"

        # 4. List Drafts
        res_list = await client.get("/api/v1/drafts?page=1&per_page=10", headers=headers)
        assert res_list.status_code == 200
        list_body = res_list.json()
        assert list_body["meta"]["total"] == 1
        assert len(list_body["data"]) == 1
        assert list_body["data"][0]["id"] == draft_id

        # 5. Delete Draft
        res_del = await client.delete(f"/api/v1/drafts/{draft_id}", headers=headers)
        assert res_del.status_code == 204

        # 6. Verify Draft is deleted
        res_not_found = await client.get(f"/api/v1/drafts/{draft_id}", headers=headers)
        assert res_not_found.status_code == 404


@pytest.mark.asyncio
async def test_draft_occ_conflict_detection() -> None:
    """Verify OCC conflict returns HTTP 412 when stale version is provided."""
    async with drafts_test_context() as (client, session_maker):
        _, token = await create_test_user(session_maker, "author_occ@verischolar.org")
        headers = {"Authorization": f"Bearer {token}"}

        # Create Draft (version 1)
        res = await client.post(
            "/api/v1/drafts",
            json={"title": "Concurrent Paper", "content": "Initial", "format": "markdown"},
            headers=headers,
        )
        draft_id = res.json()["data"]["id"]

        # First update succeeds (1 -> 2)
        res1 = await client.put(
            f"/api/v1/drafts/{draft_id}",
            json={"content": "Update from Tab 1", "version": 1},
            headers={**headers, "If-Match": '"v1"'},
        )
        assert res1.status_code == 200
        assert res1.json()["data"]["version"] == 2

        # Stale update from Tab 2 providing version 1 must fail with 412 Precondition Failed
        res2 = await client.put(
            f"/api/v1/drafts/{draft_id}",
            json={"content": "Stale update from Tab 2", "version": 1},
            headers={**headers, "If-Match": '"v1"'},
        )
        assert res2.status_code == 412
        err = res2.json()
        assert err["error"]["code"] == "CONCURRENCY_CONFLICT"


@pytest.mark.asyncio
async def test_draft_multi_tenant_isolation() -> None:
    """Verify Drafts created by User A cannot be read, updated, or deleted by User B."""
    async with drafts_test_context() as (client, session_maker):
        _, token_a = await create_test_user(session_maker, "user_a@verischolar.org")
        _, token_b = await create_test_user(session_maker, "user_b@verischolar.org")
        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # User A creates a confidential draft
        res = await client.post(
            "/api/v1/drafts",
            json={"title": "Secret Research A", "content": "Private results", "format": "latex"},
            headers=headers_a,
        )
        draft_id = res.json()["data"]["id"]

        # User B lists drafts -> sees empty list
        res_b_list = await client.get("/api/v1/drafts", headers=headers_b)
        assert res_b_list.status_code == 200
        assert res_b_list.json()["meta"]["total"] == 0

        # User B attempts to read User A's draft -> 404 (ID enumeration defense)
        res_b_get = await client.get(f"/api/v1/drafts/{draft_id}", headers=headers_b)
        assert res_b_get.status_code == 404

        # User B attempts to update User A's draft -> 404
        res_b_put = await client.put(
            f"/api/v1/drafts/{draft_id}",
            json={"content": "Malicious override", "version": 1},
            headers={**headers_b, "If-Match": '"v1"'},
        )
        assert res_b_put.status_code == 404

        # User B attempts to delete User A's draft -> 404
        res_b_del = await client.delete(f"/api/v1/drafts/{draft_id}", headers=headers_b)
        assert res_b_del.status_code == 404

        # Draft is still intact for User A
        res_a_get = await client.get(f"/api/v1/drafts/{draft_id}", headers=headers_a)
        assert res_a_get.status_code == 200
        assert res_a_get.json()["data"]["title"] == "Secret Research A"


@pytest.mark.asyncio
async def test_draft_verify_facts_endpoint() -> None:
    """Verify POST /api/v1/drafts/{id}/verify-facts returns atomic claims with bounding boxes."""
    async with drafts_test_context() as (client, session_maker):
        user, token = await create_test_user(session_maker, "fact_author@verischolar.org")
        headers = {"Authorization": f"Bearer {token}"}

        # Seed literature document and chunk for user
        async with session_maker() as session:
            doc = DocumentModel(
                id=uuid4(),
                user_id=user.id,
                title="Attention Is All You Need",
                filename="attention.pdf",
                content_hash="test_sha256_hash",
                file_size_bytes=1024,
                publication_year=2017,
                authors=["Vaswani et al."],
                page_count=15,
                status="ready",
            )
            session.add(doc)
            await session.flush()

            chunk = DocumentChunkModel(
                id=uuid4(),
                document_id=doc.id,
                chunk_index=0,
                page_number=1,
                content=(
                    "The Transformer architecture achieves 28.4 BLEU on English-to-German "
                    "translation, outperforming all previous ensembles."
                ),
                bounding_boxes=[[0.1, 0.2, 0.8, 0.3, 1]],
                token_count=30,
            )
            session.add(chunk)
            await session.commit()

        # Create draft with supported claim
        create_res = await client.post(
            "/api/v1/drafts",
            json={
                "title": "NLP Survey",
                "content": (
                    "The Transformer architecture achieves 28.4 BLEU on "
                    "English-to-German translation."
                ),
                "format": "latex",
            },
            headers=headers,
        )
        assert create_res.status_code == 201
        draft_id = create_res.json()["data"]["id"]

        # Call verify-facts endpoint
        verify_res = await client.post(
            f"/api/v1/drafts/{draft_id}/verify-facts",
            headers=headers,
        )
        assert verify_res.status_code == 200
        data = verify_res.json()["data"]
        assert data["total_claims"] >= 1
        assert data["supported_claims"] == 1
        assert data["contradicted_claims"] == 0
        assert data["supported_ratio"] == 1.0
        assert len(data["claims"]) >= 1

        claim = data["claims"][0]
        assert claim["status"] == "supported"
        assert claim["evidence_page"] == 1
        assert len(claim["evidence_bounding_boxes"]) == 1
        assert claim["evidence_bounding_boxes"][0] == [0.1, 0.2, 0.8, 0.3, 1]


@pytest.mark.asyncio
async def test_draft_compilation_and_preview() -> None:
    """Verify compiling draft produces preview PDF and preview endpoint serves valid PDF bytes."""
    async with drafts_test_context() as (client, session_factory):
        user, token = await create_test_user(session_factory, email="author@verischolar.org")
        headers = {"Authorization": f"Bearer {token}"}

        # Create valid LaTeX draft
        create_res = await client.post(
            "/api/v1/drafts",
            json={
                "title": "LaTeX Draft Test",
                "content": (
                    "\\documentclass{article}\n"
                    "\\begin{document}\n"
                    "Hello VeriScholar Academic Compilation!\n"
                    "\\end{document}\n"
                ),
                "format": "latex",
            },
            headers=headers,
        )
        assert create_res.status_code == 201
        draft_id = create_res.json()["data"]["id"]

        # 1. Compile draft
        compile_res = await client.post(
            f"/api/v1/drafts/{draft_id}/compile",
            headers=headers,
        )
        assert compile_res.status_code == 200
        compile_data = compile_res.json()["data"]
        assert compile_data["success"] is True
        assert compile_data["pdf_preview_url"] == f"/api/v1/drafts/{draft_id}/preview.pdf"

        # 2. Fetch live preview PDF
        preview_res = await client.get(
            f"/api/v1/drafts/{draft_id}/preview.pdf",
            headers=headers,
        )
        assert preview_res.status_code == 200
        assert preview_res.headers["content-type"] == "application/pdf"
        assert preview_res.content.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_draft_export_bundle_zip() -> None:
    """Verify camera-ready academic submission bundle exports valid ZIP with all required assets."""
    async with drafts_test_context() as (client, session_factory):
        user, token = await create_test_user(session_factory, email="bundle_author@verischolar.org")
        headers = {"Authorization": f"Bearer {token}"}

        # Create draft with cite key
        create_res = await client.post(
            "/api/v1/drafts",
            json={
                "title": "Deep Learning Survey",
                "content": (
                    "\\documentclass{article}\n"
                    "\\begin{document}\n"
                    "As shown by \\cite{vaswani2017attention}, Transformers excel.\n"
                    "\\end{document}\n"
                ),
                "format": "latex",
            },
            headers=headers,
        )
        assert create_res.status_code == 201
        draft_id = create_res.json()["data"]["id"]

        # Call export bundle endpoint
        export_res = await client.post(
            f"/api/v1/drafts/{draft_id}:export-bundle",
            headers=headers,
        )
        assert export_res.status_code == 200
        assert export_res.headers["content-type"] == "application/zip"
        assert "Content-Disposition" in export_res.headers
        assert (
            f"draft_{draft_id.replace('-', '')[:8]}_bundle.zip"
            in export_res.headers["Content-Disposition"]
        )

        # Unpack and verify ZIP structure
        zip_bytes = export_res.content
        with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
            file_list = zf.namelist()
            assert "main.tex" in file_list
            assert "references.bib" in file_list
            assert "preview.pdf" in file_list
            assert "README.txt" in file_list
            assert "figures/.gitkeep" in file_list

            # Check references.bib has vaswani2017attention
            bib_text = zf.read("references.bib").decode("utf-8")
            assert "vaswani2017attention" in bib_text

            # Check preview.pdf is valid PDF binary
            pdf_data = zf.read("preview.pdf")
            assert pdf_data.startswith(b"%PDF")

            # Check README.txt contains instructions
            readme_text = zf.read("README.txt").decode("utf-8")
            assert "Deep Learning Survey" in readme_text
            assert "pdflatex" in readme_text


@pytest.mark.asyncio
async def test_draft_assist_endpoint() -> None:
    """Verify POST /api/v1/drafts/{id}/assist produces structured AI writing suggestions."""
    async with drafts_test_context() as (client, session_factory):
        user, token = await create_test_user(session_factory, email="assist_author@verischolar.org")
        headers = {"Authorization": f"Bearer {token}"}

        # Create base draft
        create_res = await client.post(
            "/api/v1/drafts",
            json={"title": "Draft for Assist", "content": "Initial text", "format": "latex"},
            headers=headers,
        )
        draft_id = create_res.json()["data"]["id"]

        # Call assist endpoint with action and prompt
        assist_payload = {
            "action": "polish",
            "instruction": "Improve academic formality",
            "target_selection": "Our method works well.",
            "section_title": "Results",
        }
        res = await client.post(
            f"/api/v1/drafts/{draft_id}/assist", json=assist_payload, headers=headers
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["draft_id"] == draft_id
        assert data["action"] == "polish"
        assert len(data["suggested_text"]) > 0
        assert len(data["suggested_citations"]) >= 1


@pytest.mark.asyncio
async def test_draft_assets_lifecycle() -> None:
    """Verify registering and listing assets via /api/v1/drafts/{id}/assets."""
    async with drafts_test_context() as (client, session_factory):
        user, token = await create_test_user(session_factory, email="asset_author@verischolar.org")
        headers = {"Authorization": f"Bearer {token}"}

        create_res = await client.post(
            "/api/v1/drafts",
            json={"title": "Asset Draft", "content": "Content", "format": "latex"},
            headers=headers,
        )
        draft_id = create_res.json()["data"]["id"]

        # 1. Register asset
        asset_payload = {
            "asset_type": "image",
            "filename": "arch_figure1.png",
            "caption": "Overall System Architecture",
            "latex_label": "fig:arch",
        }
        post_res = await client.post(
            f"/api/v1/drafts/{draft_id}/assets",
            json=asset_payload,
            headers=headers,
        )
        assert post_res.status_code == 201
        asset_data = post_res.json()["data"]
        assert asset_data["filename"] == "arch_figure1.png"
        assert asset_data["asset_type"] == "image"
        assert asset_data["caption"] == "Overall System Architecture"

        # 2. List assets
        list_res = await client.get(f"/api/v1/drafts/{draft_id}/assets", headers=headers)
        assert list_res.status_code == 200
        list_data = list_res.json()["data"]
        assert list_data["total"] >= 1
        assert any(a["filename"] == "arch_figure1.png" for a in list_data["items"])


@pytest.mark.asyncio
async def test_draft_share_lifecycle() -> None:
    """Verify configuring and reading share settings via /api/v1/drafts/{id}/share."""
    async with drafts_test_context() as (client, session_factory):
        user, token = await create_test_user(session_factory, email="share_author@verischolar.org")
        headers = {"Authorization": f"Bearer {token}"}

        create_res = await client.post(
            "/api/v1/drafts",
            json={"title": "Share Draft", "content": "Draft Content", "format": "latex"},
            headers=headers,
        )
        draft_id = create_res.json()["data"]["id"]

        # 1. Configure sharing with collaborator
        share_payload = {
            "target_email": "coauthor@verischolar.org",
            "permission": "editor",
            "allow_public_link": True,
        }
        post_res = await client.post(
            f"/api/v1/drafts/{draft_id}/share",
            json=share_payload,
            headers=headers,
        )
        assert post_res.status_code == 200
        share_data = post_res.json()["data"]
        assert share_data["permission"] == "editor"
        assert share_data["allow_public_link"] is True
        assert len(share_data["collaborators"]) == 1
        assert share_data["collaborators"][0]["email"] == "coauthor@verischolar.org"

        # 2. Retrieve share settings
        get_res = await client.get(f"/api/v1/drafts/{draft_id}/share", headers=headers)
        assert get_res.status_code == 200
        get_data = get_res.json()["data"]
        assert get_data["share_token"] == share_data["share_token"]
        assert get_data["allow_public_link"] is True


@pytest.mark.asyncio
async def test_collaborator_rbac_and_privacy_isolation() -> None:
    """Verify collaborator RBAC permissions and privacy isolation of assets across roles."""
    async with drafts_test_context() as (client, session_factory):
        # 1. Setup users: Owner, Editor, Commenter, Viewer, Stranger
        owner, owner_token = await create_test_user(
            session_factory, email="paper_owner@verischolar.org"
        )
        editor, editor_token = await create_test_user(
            session_factory, email="paper_editor@verischolar.org"
        )
        commenter, commenter_token = await create_test_user(
            session_factory, email="paper_commenter@verischolar.org"
        )
        viewer, viewer_token = await create_test_user(
            session_factory, email="paper_viewer@verischolar.org"
        )
        stranger, stranger_token = await create_test_user(
            session_factory, email="paper_stranger@verischolar.org"
        )

        owner_headers = {"Authorization": f"Bearer {owner_token}"}
        editor_headers = {"Authorization": f"Bearer {editor_token}"}
        commenter_headers = {"Authorization": f"Bearer {commenter_token}"}
        viewer_headers = {"Authorization": f"Bearer {viewer_token}"}
        stranger_headers = {"Authorization": f"Bearer {stranger_token}"}

        # 2. Owner creates draft
        create_res = await client.post(
            "/api/v1/drafts",
            json={
                "title": "Quantum Privacy",
                "content": "\\section{Intro}\nQuantum teleportation is instantaneous.",
                "format": "latex",
            },
            headers=owner_headers,
        )
        assert create_res.status_code == 201
        draft_id = create_res.json()["data"]["id"]

        # 3. Owner uploads an asset
        asset_res = await client.post(
            f"/api/v1/drafts/{draft_id}/assets",
            json={
                "asset_type": "image",
                "filename": "quantum_circuit.png",
                "caption": "Quantum Entanglement Circuit",
            },
            headers=owner_headers,
        )
        assert asset_res.status_code == 201

        # 4. Owner shares draft with editor, commenter, viewer
        share_res1 = await client.post(
            f"/api/v1/drafts/{draft_id}/share",
            json={"target_email": editor.email, "permission": "editor"},
            headers=owner_headers,
        )
        assert share_res1.status_code == 200

        share_res2 = await client.post(
            f"/api/v1/drafts/{draft_id}/share",
            json={"target_email": commenter.email, "permission": "commenter"},
            headers=owner_headers,
        )
        assert share_res2.status_code == 200

        share_res3 = await client.post(
            f"/api/v1/drafts/{draft_id}/share",
            json={"target_email": viewer.email, "permission": "viewer"},
            headers=owner_headers,
        )
        assert share_res3.status_code == 200

        # 5. Stranger tries to access draft -> 404 (zero leakage)
        stranger_get = await client.get(f"/api/v1/drafts/{draft_id}", headers=stranger_headers)
        assert stranger_get.status_code == 404

        # 6. Viewer checks:
        # Can read draft
        viewer_get = await client.get(f"/api/v1/drafts/{draft_id}", headers=viewer_headers)
        assert viewer_get.status_code == 200
        # Privacy isolation: viewer lists assets, storage_url must be None
        viewer_assets = await client.get(
            f"/api/v1/drafts/{draft_id}/assets", headers=viewer_headers
        )
        assert viewer_assets.status_code == 200
        for item in viewer_assets.json()["data"]["items"]:
            assert item["storage_url"] is None

        # Viewer forbidden actions -> 403
        v_update = await client.put(
            f"/api/v1/drafts/{draft_id}",
            json={"title": "Hacked Title", "version": 1},
            headers=viewer_headers,
        )
        assert v_update.status_code == 403

        v_compile = await client.post(f"/api/v1/drafts/{draft_id}/compile", headers=viewer_headers)
        assert v_compile.status_code == 403

        v_assist = await client.post(
            f"/api/v1/drafts/{draft_id}/assist",
            json={"prompt": "Rewrite", "action": "polish"},
            headers=viewer_headers,
        )
        assert v_assist.status_code == 403

        v_verify = await client.post(
            f"/api/v1/drafts/{draft_id}/verify-facts",
            headers=viewer_headers,
        )
        assert v_verify.status_code == 403

        v_asset = await client.post(
            f"/api/v1/drafts/{draft_id}/assets",
            json={"asset_type": "image", "filename": "hack.png"},
            headers=viewer_headers,
        )
        assert v_asset.status_code == 403

        v_bundle = await client.post(
            f"/api/v1/drafts/{draft_id}:export-bundle",
            headers=viewer_headers,
        )
        assert v_bundle.status_code == 403

        v_delete = await client.delete(f"/api/v1/drafts/{draft_id}", headers=viewer_headers)
        assert v_delete.status_code == 403

        v_share = await client.post(
            f"/api/v1/drafts/{draft_id}/share",
            json={"target_email": "friend@verischolar.org", "permission": "editor"},
            headers=viewer_headers,
        )
        assert v_share.status_code == 403

        # 7. Commenter checks:
        # Can read draft
        c_get = await client.get(f"/api/v1/drafts/{draft_id}", headers=commenter_headers)
        assert c_get.status_code == 200
        # Privacy isolation: storage_url is None
        c_assets = await client.get(f"/api/v1/drafts/{draft_id}/assets", headers=commenter_headers)
        assert c_assets.status_code == 200
        for item in c_assets.json()["data"]["items"]:
            assert item["storage_url"] is None

        # Commenter forbidden actions -> 403
        c_update = await client.put(
            f"/api/v1/drafts/{draft_id}",
            json={"title": "Commenter Edit", "version": 1},
            headers=commenter_headers,
        )
        assert c_update.status_code == 403

        c_compile = await client.post(
            f"/api/v1/drafts/{draft_id}/compile", headers=commenter_headers
        )
        assert c_compile.status_code == 403

        c_assist = await client.post(
            f"/api/v1/drafts/{draft_id}/assist",
            json={"prompt": "Rewrite", "action": "polish"},
            headers=commenter_headers,
        )
        assert c_assist.status_code == 403

        c_verify = await client.post(
            f"/api/v1/drafts/{draft_id}/verify-facts",
            headers=commenter_headers,
        )
        assert c_verify.status_code == 403

        c_asset = await client.post(
            f"/api/v1/drafts/{draft_id}/assets",
            json={"asset_type": "image", "filename": "comment_fig.png"},
            headers=commenter_headers,
        )
        assert c_asset.status_code == 403

        # 8. Editor checks:
        # Can update draft
        ed_update = await client.put(
            f"/api/v1/drafts/{draft_id}",
            json={"title": "Updated by Editor", "version": 1},
            headers=editor_headers,
        )
        assert ed_update.status_code == 200

        # Can compile draft
        ed_compile = await client.post(f"/api/v1/drafts/{draft_id}/compile", headers=editor_headers)
        assert ed_compile.status_code == 200

        # Can assist draft
        ed_assist = await client.post(
            f"/api/v1/drafts/{draft_id}/assist",
            json={"prompt": "Refine intro", "action": "polish"},
            headers=editor_headers,
        )
        assert ed_assist.status_code == 200

        # Can verify facts
        ed_verify = await client.post(
            f"/api/v1/drafts/{draft_id}/verify-facts",
            headers=editor_headers,
        )
        assert ed_verify.status_code == 200

        # Can upload asset
        ed_asset = await client.post(
            f"/api/v1/drafts/{draft_id}/assets",
            json={"asset_type": "image", "filename": "editor_diagram.png"},
            headers=editor_headers,
        )
        assert ed_asset.status_code == 201

        # Editor can see storage_url in assets list
        ed_assets = await client.get(f"/api/v1/drafts/{draft_id}/assets", headers=editor_headers)
        assert ed_assets.status_code == 200
        for item in ed_assets.json()["data"]["items"]:
            assert item["storage_url"] is not None

        # Editor can export submission bundle
        ed_bundle = await client.post(
            f"/api/v1/drafts/{draft_id}:export-bundle",
            headers=editor_headers,
        )
        assert ed_bundle.status_code == 200

        # Editor cannot delete draft -> 403
        ed_delete = await client.delete(f"/api/v1/drafts/{draft_id}", headers=editor_headers)
        assert ed_delete.status_code == 403

        # Editor cannot share draft -> 403
        ed_share = await client.post(
            f"/api/v1/drafts/{draft_id}/share",
            json={"target_email": "third@verischolar.org", "permission": "viewer"},
            headers=editor_headers,
        )
        assert ed_share.status_code == 403


@pytest.mark.asyncio
async def test_asset_security_zip_slip_and_macro_defense() -> None:
    """Verify 6-layer asset security: Zip-Slip traversal, macros, null bytes, validation."""
    async with drafts_test_context() as (client, session_factory):
        user, token = await create_test_user(session_factory, email="sec_author@verischolar.org")
        headers = {"Authorization": f"Bearer {token}"}

        create_res = await client.post(
            "/api/v1/drafts",
            json={"title": "Security Draft", "content": "Security testing", "format": "latex"},
            headers=headers,
        )
        draft_id = create_res.json()["data"]["id"]

        # 1. Path traversal in filename -> 400
        res = await client.post(
            f"/api/v1/drafts/{draft_id}/assets",
            json={"asset_type": "image", "filename": "../../etc/passwd.png"},
            headers=headers,
        )
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "ASSET_SECURITY_VIOLATION"

        # 2. Dangerous macro \\write18 in style file -> 400
        malicious_sty = r"\NeedsTeXFormat{LaTeX2e}\ProvidesPackage{evil}\write18{rm -rf /}"
        res = await client.post(
            f"/api/v1/drafts/{draft_id}/assets",
            json={
                "asset_type": "style",
                "filename": "evil.sty",
                "content_base64": base64.b64encode(malicious_sty.encode()).decode(),
            },
            headers=headers,
        )
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "ASSET_SECURITY_VIOLATION"

        # 3. Dangerous macro \\openout in cls file -> 400
        malicious_cls = r"\ProvidesClass{evil}\openout15=trojan.tex"
        res = await client.post(
            f"/api/v1/drafts/{draft_id}/assets",
            json={
                "asset_type": "style",
                "filename": "evil.cls",
                "content_base64": base64.b64encode(malicious_cls.encode()).decode(),
            },
            headers=headers,
        )
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "ASSET_SECURITY_VIOLATION"

        # 4. Dangerous macro \\sys_shell:nn in bibtex file -> 400
        malicious_bib = r"@article{exploit, title={\sys_shell:nn{cat}{/etc/shadow}}}"
        res = await client.post(
            f"/api/v1/drafts/{draft_id}/assets",
            json={
                "asset_type": "bibtex",
                "filename": "evil.bib",
                "content_base64": base64.b64encode(malicious_bib.encode()).decode(),
            },
            headers=headers,
        )
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "ASSET_SECURITY_VIOLATION"

        # 5. Null byte in bib file -> 400
        null_bib = b"@article{null,\x00 title={Corrupt}}"
        res = await client.post(
            f"/api/v1/drafts/{draft_id}/assets",
            json={
                "asset_type": "bibtex",
                "filename": "null.bib",
                "content_base64": base64.b64encode(null_bib).decode(),
            },
            headers=headers,
        )
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "ASSET_SECURITY_VIOLATION"

        # 6. Disallowed extension -> 400
        res = await client.post(
            f"/api/v1/drafts/{draft_id}/assets",
            json={"asset_type": "supplementary", "filename": "trojan.exe"},
            headers=headers,
        )
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "ASSET_SECURITY_VIOLATION"

        # 7. Zip-slip traversal inside ZIP archive -> 400
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("../../main.tex", b"overwritten root")
        res = await client.post(
            f"/api/v1/drafts/{draft_id}/assets",
            json={
                "asset_type": "archive",
                "filename": "slip.zip",
                "content_base64": base64.b64encode(buf.getvalue()).decode(),
            },
            headers=headers,
        )
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "ASSET_SECURITY_VIOLATION"

        # 8. Valid PNG upload -> 201
        valid_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
        res = await client.post(
            f"/api/v1/drafts/{draft_id}/assets",
            json={
                "asset_type": "image",
                "filename": "valid_chart.png",
                "content_base64": base64.b64encode(valid_png).decode(),
            },
            headers=headers,
        )
        assert res.status_code == 201
        assert res.json()["data"]["filename"] == "valid_chart.png"

        # 9. Valid BibTeX upload -> 201
        valid_bib = "@article{good,\n  author={Knuth, D.},\n  title={TeXbook},\n  year={1984}\n}"
        res = await client.post(
            f"/api/v1/drafts/{draft_id}/assets",
            json={
                "asset_type": "bibtex",
                "filename": "clean.bib",
                "content_base64": base64.b64encode(valid_bib.encode()).decode(),
            },
            headers=headers,
        )
        assert res.status_code == 201
        assert res.json()["data"]["filename"] == "clean.bib"

        # 10. Valid safe ZIP bundle extraction -> 201
        safe_buf = io.BytesIO()
        with zipfile.ZipFile(safe_buf, "w") as zf:
            zf.writestr("figures/fig1.png", valid_png)
            zf.writestr("references/ref.bib", valid_bib.encode())
        res = await client.post(
            f"/api/v1/drafts/{draft_id}/assets",
            json={
                "asset_type": "archive",
                "filename": "assets_bundle.zip",
                "content_base64": base64.b64encode(safe_buf.getvalue()).decode(),
            },
            headers=headers,
        )
        assert res.status_code == 201
