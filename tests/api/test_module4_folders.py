"""Comprehensive integration test suite for Module 4 (Personal Paper Library & Folders).

Validates:
- CRUD Folders: POST, GET, PATCH, DELETE /api/v1/folders
- Hierarchical Folder Tree: GET /api/v1/folders/tree
- Anti-cycle detection / Circular hierarchy prevention (HTTP 400)
- Assign and unassign documents: POST, DELETE /api/v1/folders/{id}/documents
- Literature Comparison Matrix: POST /api/v1/folders/comparison-matrix, /{id}/comparison-matrix
- 2-Tier Hierarchical RAG query & Sufficiency Gate: POST /api/v1/folders/synthesis, /{id}/synthesis
- Multi-tenant isolation and security.
"""

from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.base import Base
from api.db.models.chunk import DocumentChunkModel
from api.db.models.document import DocumentModel
from api.db.models.folder import FolderModel
from api.db.models.note import ResearchNoteModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.services.auth_service import AuthService
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


@asynccontextmanager
async def folder_test_context() -> AsyncIterator[
    tuple[AsyncClient, async_sessionmaker[AsyncSession]]
]:
    """Provide isolated in-memory SQLite database and test HTTP client."""
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


async def create_user_with_token(
    session_maker: async_sessionmaker[AsyncSession],
    email: str = "researcher@verischolar.org",
    full_name: str = "Marie Curie",
) -> tuple[UserModel, str]:
    """Create test user and issue JWT Bearer token."""
    async with session_maker() as session:
        user = UserModel(
            id=uuid4(),
            email=email,
            full_name=full_name,
            hashed_password=AuthService.hash_password("Pass123456!"),
            is_active=True,
            role="researcher",
            institution="Sorbonne University",
            academic_rank="Professor",
            is_verified=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    token = AuthService.create_token(
        payload={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta_seconds=3600,
    )
    return user, token


async def create_test_document(
    session_maker: async_sessionmaker[AsyncSession],
    user_id: UUID,
    title: str = "Attention Is All You Need",
    folder_id: UUID | None = None,
) -> DocumentModel:
    """Create test document record in database."""
    async with session_maker() as session:
        doc = DocumentModel(
            id=uuid4(),
            user_id=user_id,
            filename=f"{title.lower().replace(' ', '_')}.pdf",
            title=title,
            authors=["Vaswani et al."],
            publication_year=2017,
            file_size_bytes=1024 * 512,
            content_hash=uuid4().hex,
            folder_id=folder_id,
            status="completed",
            stage="completed",
            progress=100,
            parsed_metadata={
                "methodology": "Transformer Self-Attention",
                "datasets": ["WMT-14 En-De"],
                "metrics": {"BLEU": "28.4"},
                "strengths": ["Parallel training"],
                "limitations": ["Quadratic context memory"],
            },
        )
        session.add(doc)
        await session.commit()
        await session.refresh(doc)
        return doc


# ==============================================================================
# 1. CRUD Operations on Folders
# ==============================================================================


@pytest.mark.asyncio
async def test_folder_crud_lifecycle() -> None:
    """Validate Create, Read, Update, Delete lifecycle for research folders."""
    async with folder_test_context() as (client, session_maker):
        _, token = await create_user_with_token(session_maker)
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create root folder
        resp_create = await client.post(
            "/api/v1/folders",
            headers=headers,
            json={
                "name": "Machine Learning",
                "color": "#3b82f6",
                "description": "Foundational AI papers",
            },
        )
        assert resp_create.status_code == 201
        folder_data = resp_create.json()["data"]
        folder_id = folder_data["id"]
        assert folder_data["name"] == "Machine Learning"
        assert folder_data["color"] == "#3b82f6"
        assert folder_data["parent_id"] is None
        assert folder_data["document_count"] == 0
        assert folder_data["subfolder_count"] == 0

        # 2. List folders
        resp_list = await client.get("/api/v1/folders", headers=headers)
        assert resp_list.status_code == 200
        all_folders = resp_list.json()["data"]
        assert len(all_folders) == 1
        assert all_folders[0]["id"] == folder_id

        # 3. Get single folder
        resp_get = await client.get(f"/api/v1/folders/{folder_id}", headers=headers)
        assert resp_get.status_code == 200
        assert resp_get.json()["data"]["name"] == "Machine Learning"

        # 4. Update folder metadata
        resp_update = await client.patch(
            f"/api/v1/folders/{folder_id}",
            headers=headers,
            json={
                "name": "Advanced Machine Learning",
                "color": "#10b981",
                "description": "Updated description",
            },
        )
        assert resp_update.status_code == 200
        updated = resp_update.json()["data"]
        assert updated["name"] == "Advanced Machine Learning"
        assert updated["color"] == "#10b981"
        assert updated["description"] == "Updated description"

        # 5. Delete folder
        resp_del = await client.delete(f"/api/v1/folders/{folder_id}", headers=headers)
        assert resp_del.status_code == 200
        assert resp_del.json()["data"]["status"] == "deleted"

        # 6. Verify 404 after deletion
        resp_not_found = await client.get(f"/api/v1/folders/{folder_id}", headers=headers)
        assert resp_not_found.status_code == 404


# ==============================================================================
# 2. Hierarchical Tree & Circular Prevention
# ==============================================================================


@pytest.mark.asyncio
async def test_folder_hierarchy_tree_and_cycles() -> None:
    """Validate hierarchical folder tree and anti-circular cycle prevention (HTTP 400)."""
    async with folder_test_context() as (client, session_maker):
        _, token = await create_user_with_token(session_maker)
        headers = {"Authorization": f"Bearer {token}"}

        # Create Root A
        r_a = await client.post("/api/v1/folders", headers=headers, json={"name": "Folder A"})
        id_a = r_a.json()["data"]["id"]

        # Create Subfolder A1 under A
        r_a1 = await client.post(
            "/api/v1/folders", headers=headers, json={"name": "Folder A1", "parent_id": id_a}
        )
        id_a1 = r_a1.json()["data"]["id"]

        # Create Subfolder A1_1 under A1
        r_a1_1 = await client.post(
            "/api/v1/folders", headers=headers, json={"name": "Folder A1_1", "parent_id": id_a1}
        )
        id_a1_1 = r_a1_1.json()["data"]["id"]

        # Create Root B
        r_b = await client.post("/api/v1/folders", headers=headers, json={"name": "Folder B"})
        id_b = r_b.json()["data"]["id"]

        # Test Tree endpoint
        resp_tree = await client.get("/api/v1/folders/tree", headers=headers)
        assert resp_tree.status_code == 200
        tree = resp_tree.json()["data"]
        assert len(tree) == 2  # Root A and Root B

        node_a = next(node for node in tree if node["id"] == id_a)
        node_b = next(node for node in tree if node["id"] == id_b)
        assert node_b["subfolders"] == []
        assert len(node_a["subfolders"]) == 1
        assert node_a["subfolders"][0]["id"] == id_a1
        assert len(node_a["subfolders"][0]["subfolders"]) == 1
        assert node_a["subfolders"][0]["subfolders"][0]["id"] == id_a1_1

        # Test Anti-Cycle 1: Move folder into itself -> 400
        resp_self = await client.patch(
            f"/api/v1/folders/{id_a}",
            headers=headers,
            json={"parent_id": id_a},
        )
        assert resp_self.status_code == 400
        assert "chính nó" in resp_self.text

        # Test Anti-Cycle 2: Move A into its direct child A1 -> 400 Circular hierarchy
        resp_cycle_child = await client.patch(
            f"/api/v1/folders/{id_a}",
            headers=headers,
            json={"parent_id": id_a1},
        )
        assert resp_cycle_child.status_code == 400
        assert "Circular hierarchy" in resp_cycle_child.text

        # Test Anti-Cycle 3: Move A into deep descendant A1_1 -> 400 Circular hierarchy
        resp_cycle_desc = await client.patch(
            f"/api/v1/folders/{id_a}",
            headers=headers,
            json={"parent_id": id_a1_1},
        )
        assert resp_cycle_desc.status_code == 400
        assert "Circular hierarchy" in resp_cycle_desc.text

        # Test Valid Move: Move A1_1 to Root B
        resp_valid_move = await client.patch(
            f"/api/v1/folders/{id_a1_1}",
            headers=headers,
            json={"parent_id": id_b},
        )
        assert resp_valid_move.status_code == 200
        assert resp_valid_move.json()["data"]["parent_id"] == id_b


# ==============================================================================
# 3. Duplicate Name Conflict & Validation
# ==============================================================================


@pytest.mark.asyncio
async def test_folder_duplicate_name_and_parent_validation() -> None:
    """Validate 409 Conflict on duplicate sibling names and 404 on invalid parent."""
    async with folder_test_context() as (client, session_maker):
        _, token = await create_user_with_token(session_maker)
        headers = {"Authorization": f"Bearer {token}"}

        # Create root folder
        r1 = await client.post("/api/v1/folders", headers=headers, json={"name": "BioNLP"})
        assert r1.status_code == 201

        # Attempt to create duplicate root folder with same name
        r_dup = await client.post("/api/v1/folders", headers=headers, json={"name": "BioNLP"})
        assert r_dup.status_code == 409
        assert "đã tồn tại" in r_dup.text

        # Non-existent parent_id -> 404
        r_fake_parent = await client.post(
            "/api/v1/folders",
            headers=headers,
            json={"name": "Genomics", "parent_id": str(uuid4())},
        )
        assert r_fake_parent.status_code == 404


# ==============================================================================
# 4. Document Assignment & Removal
# ==============================================================================


@pytest.mark.asyncio
async def test_assign_and_remove_documents_from_folder() -> None:
    """Validate assigning documents to folders and unassigning them."""
    async with folder_test_context() as (client, session_maker):
        user, token = await create_user_with_token(session_maker)
        headers = {"Authorization": f"Bearer {token}"}

        # Create Folder
        r_f = await client.post("/api/v1/folders", headers=headers, json={"name": "Vision Models"})
        folder_id = r_f.json()["data"]["id"]

        # Create 2 test documents
        doc1 = await create_test_document(session_maker, user.id, "ViT: Vision Transformer")
        doc2 = await create_test_document(session_maker, user.id, "Swin Transformer")

        # Assign both documents to folder
        r_assign = await client.post(
            f"/api/v1/folders/{folder_id}/documents",
            headers=headers,
            json={"document_ids": [str(doc1.id), str(doc2.id)]},
        )
        assert r_assign.status_code == 200
        assert r_assign.json()["data"]["assigned_count"] == 2

        # Check folder document count
        r_check = await client.get(f"/api/v1/folders/{folder_id}", headers=headers)
        assert r_check.json()["data"]["document_count"] == 2

        # Remove doc1 from folder
        r_remove = await client.request(
            "DELETE",
            f"/api/v1/folders/{folder_id}/documents",
            headers=headers,
            json={"document_ids": [str(doc1.id)]},
        )
        assert r_remove.status_code == 200
        assert r_remove.json()["data"]["removed_count"] == 1

        # Check folder document count is now 1
        r_check2 = await client.get(f"/api/v1/folders/{folder_id}", headers=headers)
        assert r_check2.json()["data"]["document_count"] == 1


# ==============================================================================
# 5. Delete Folder Reassigns Documents & Subfolders to Safety
# ==============================================================================


@pytest.mark.asyncio
async def test_delete_folder_preserves_documents_and_promotes_subfolders() -> None:
    """Ensure deleting a folder moves its documents to root and re-parents subfolders."""
    async with folder_test_context() as (client, session_maker):
        user, token = await create_user_with_token(session_maker)
        headers = {"Authorization": f"Bearer {token}"}

        # Create Parent Folder and Subfolder
        r_p = await client.post(
            "/api/v1/folders", headers=headers, json={"name": "Parent Category"}
        )
        parent_id = r_p.json()["data"]["id"]

        r_sub = await client.post(
            "/api/v1/folders",
            headers=headers,
            json={"name": "Child Category", "parent_id": parent_id},
        )
        sub_id = r_sub.json()["data"]["id"]

        # Create document assigned to Parent
        doc = await create_test_document(
            session_maker, user.id, "Foundation Paper", folder_id=UUID(parent_id)
        )

        # Delete Parent Folder
        r_del = await client.delete(f"/api/v1/folders/{parent_id}", headers=headers)
        assert r_del.status_code == 200

        # Verify Document was NOT deleted, but its folder_id is now None (Root)
        async with session_maker() as session:
            doc_in_db = (
                await session.execute(select(DocumentModel).where(DocumentModel.id == doc.id))
            ).scalar_one_or_none()
            assert doc_in_db is not None
            assert doc_in_db.folder_id is None

            # Verify Subfolder's parent_id is now None
            sub_in_db = (
                await session.execute(select(FolderModel).where(FolderModel.id == UUID(sub_id)))
            ).scalar_one_or_none()
            assert sub_in_db is not None
            assert sub_in_db.parent_id is None


# ==============================================================================
# 6. Literature Comparison Matrix (Global & Folder-scoped)
# ==============================================================================


@pytest.mark.asyncio
async def test_literature_comparison_matrix() -> None:
    """Validate generating cross-paper literature comparison matrix."""
    async with folder_test_context() as (client, session_maker):
        user, token = await create_user_with_token(session_maker)
        headers = {"Authorization": f"Bearer {token}"}

        # Create folder with 2 papers
        r_f = await client.post("/api/v1/folders", headers=headers, json={"name": "NLP Benchmarks"})
        folder_id = r_f.json()["data"]["id"]

        doc1 = await create_test_document(
            session_maker, user.id, "Attention Is All You Need", folder_id=UUID(folder_id)
        )
        doc2 = await create_test_document(
            session_maker, user.id, "BERT Pre-training", folder_id=UUID(folder_id)
        )

        # 1. Global Comparison Matrix with explicit document_ids
        resp_global = await client.post(
            "/api/v1/folders/comparison-matrix",
            headers=headers,
            json={
                "topic": "Sequence Modeling & Transformers",
                "document_ids": [str(doc1.id), str(doc2.id)],
            },
        )
        assert resp_global.status_code == 200
        data_g = resp_global.json()["data"]
        assert data_g["topic"] == "Sequence Modeling & Transformers"
        assert data_g["documents_compared"] == 2
        assert len(data_g["rows"]) == 2
        assert "markdown_table" in data_g
        assert "sufficiency" in data_g
        assert data_g["sufficiency"]["sufficiency_score"] > 0

        # 2. Folder-scoped Comparison Matrix
        resp_folder = await client.post(
            f"/api/v1/folders/{folder_id}/comparison-matrix",
            headers=headers,
            json={"topic": "Transformers vs Pretraining"},
        )
        assert resp_folder.status_code == 200
        data_f = resp_folder.json()["data"]
        assert data_f["folder_id"] == folder_id
        assert data_f["documents_compared"] == 2

        # 3. 404 when no documents exist for comparison
        r_empty = await client.post("/api/v1/folders", headers=headers, json={"name": "Empty Area"})
        empty_id = r_empty.json()["data"]["id"]
        resp_err = await client.post(
            f"/api/v1/folders/{empty_id}/comparison-matrix",
            headers=headers,
            json={"topic": "Empty comparison"},
        )
        assert resp_err.status_code == 404


# ==============================================================================
# 7. 2-Tier Hierarchical RAG Query & Sufficiency Gate
# ==============================================================================


@pytest.mark.asyncio
async def test_hierarchical_rag_query_and_sufficiency() -> None:
    """Validate 2-tier Hierarchical RAG query, thinking stream, and Sufficiency Gate."""
    async with folder_test_context() as (client, session_maker):
        user, token = await create_user_with_token(session_maker)
        headers = {"Authorization": f"Bearer {token}"}

        # Create folder and document
        r_f = await client.post("/api/v1/folders", headers=headers, json={"name": "Theory Hub"})
        folder_id = r_f.json()["data"]["id"]

        doc = await create_test_document(
            session_maker, user.id, "Scaled Dot-Product Attention", folder_id=UUID(folder_id)
        )

        # Seed Research Notes (Tier 1) and Chunks (Tier 2)
        async with session_maker() as session:
            note1 = ResearchNoteModel(
                id=uuid4(),
                user_id=user.id,
                document_id=doc.id,
                selected_text=(
                    "Scaled dot-product attention scales by 1/sqrt(dk) to prevent "
                    "vanishing gradients."
                ),
                bounding_boxes=[[0.1, 0.1, 0.5, 0.5]],
                page_number=3,
                user_note="Attention gradient stability proof.",
            )
            note2 = ResearchNoteModel(
                id=uuid4(),
                user_id=user.id,
                document_id=doc.id,
                selected_text=(
                    "Multi-head attention allows joint attendance across representation subspaces."
                ),
                bounding_boxes=[[0.2, 0.2, 0.6, 0.6]],
                page_number=4,
                user_note="Multi-head representation subspaces.",
            )
            chunk = DocumentChunkModel(
                id=uuid4(),
                document_id=doc.id,
                chunk_index=0,
                content="Transformers replace recurrence with self-attention mechanism.",
                bounding_boxes=[[0.0, 0.0, 1.0, 1.0]],
                token_count=10,
                page_number=1,
            )
            session.add_all([note1, note2, chunk])
            await session.commit()

        # 1. Global 2-Tier Query with enable_thinking=True
        resp_rag = await client.post(
            "/api/v1/folders/synthesis",
            headers=headers,
            json={
                "query": "How does attention scaling prevent vanishing gradients?",
                "enable_thinking": True,
            },
        )
        assert resp_rag.status_code == 200
        data_rag = resp_rag.json()["data"]
        assert data_rag["tier_used"] in ("tier1_notes", "tier2_chunks", "hybrid")
        assert data_rag["thought"] is not None
        assert "Chuỗi suy luận phân tầng" in data_rag["thought"]
        assert data_rag["sufficiency"]["is_sufficient"] is True
        assert data_rag["sufficiency"]["sufficiency_score"] >= 0.7
        assert len(data_rag["citations"]) > 0

        # 2. Query with enable_thinking=False
        resp_no_think = await client.post(
            "/api/v1/folders/synthesis",
            headers=headers,
            json={
                "query": "Explain attention subspaces",
                "enable_thinking": False,
            },
        )
        assert resp_no_think.status_code == 200
        assert resp_no_think.json()["data"]["thought"] is None

        # 3. Folder-scoped RAG Query
        resp_scoped = await client.post(
            f"/api/v1/folders/{folder_id}/synthesis",
            headers=headers,
            json={"query": "Scaled attention gradient analysis"},
        )
        assert resp_scoped.status_code == 200
        assert resp_scoped.json()["data"]["answer"] is not None


# ==============================================================================
# 8. Multi-Tenant Isolation
# ==============================================================================


@pytest.mark.asyncio
async def test_folder_multi_tenant_isolation() -> None:
    """Validate that User B cannot access, modify, or delete User A's folders."""
    async with folder_test_context() as (client, session_maker):
        _, token_a = await create_user_with_token(session_maker, email="user_a@test.org")
        _, token_b = await create_user_with_token(session_maker, email="user_b@test.org")

        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # User A creates a folder
        r_create = await client.post(
            "/api/v1/folders", headers=headers_a, json={"name": "Confidential Research A"}
        )
        folder_id = r_create.json()["data"]["id"]

        # User B attempts to GET -> 404
        r_b_get = await client.get(f"/api/v1/folders/{folder_id}", headers=headers_b)
        assert r_b_get.status_code == 404

        # User B attempts to PATCH -> 404
        r_b_patch = await client.patch(
            f"/api/v1/folders/{folder_id}", headers=headers_b, json={"name": "Hacked Name"}
        )
        assert r_b_patch.status_code == 404

        # User B attempts to DELETE -> 404
        r_b_del = await client.delete(f"/api/v1/folders/{folder_id}", headers=headers_b)
        assert r_b_del.status_code == 404

        # User B list does not include User A's folder
        r_b_list = await client.get("/api/v1/folders", headers=headers_b)
        assert r_b_list.status_code == 200
        assert len(r_b_list.json()["data"]) == 0
