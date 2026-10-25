"""Automated integration tests for Research Writing Drafts Lifecycle & OCC (Module 2)."""

import base64
import io
import shutil
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

_has_cli_compiler = bool(shutil.which("tectonic") or shutil.which("pdflatex"))
requires_cli_compiler = pytest.mark.skipif(
    not _has_cli_compiler,
    reason="Native LaTeX compiler (tectonic/pdflatex) not installed on host",
)


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
            hashed_password="mock_hashed_password",
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
async def test_draft_create_default_starter_template() -> None:
    """Verify that creating a draft with empty content automatically populates compilable academic LaTeX starter template."""
    async with drafts_test_context() as (client, session_maker):
        _, token = await create_test_user(session_maker, "author_template@verischolar.org")
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create with empty content string
        res = await client.post(
            "/api/v1/drafts",
            json={"title": "Attention Exploration", "content": ""},
            headers=headers,
        )
        assert res.status_code == 201
        draft = res.json()["data"]
        content = draft["content"]

        # Verify required LaTeX elements
        assert r"\documentclass[10pt,twocolumn,a4paper]{article}" in content
        assert r"\usepackage{amsmath,amsfonts,amssymb}" in content
        assert r"\author{" in content
        assert r"\begin{document}" in content
        assert r"\maketitle" in content
        assert r"\begin{abstract}" in content
        assert r"\section{" in content
        assert r"\end{document}" in content


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


@requires_cli_compiler
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
        assert compile_data["success"] is True or compile_data["pdf_preview_url"] is not None
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
