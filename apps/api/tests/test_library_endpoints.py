"""Integration and contract tests for Library Endpoints, GraphRAG Queries,
Bibliometrics, Star-toggle, and Cycle Detection.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
import pytest_asyncio
from api.db.models.document import DocumentModel
from api.db.models.folder import FolderModel
from api.db.models.user import UserModel
from api.services.auth_service import AuthService
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def current_user(auth_headers: dict[str, str], db_session: AsyncSession) -> UserModel:
    token = auth_headers["Authorization"].split(" ")[1]
    claims = AuthService.decode_token(token)
    user_id = claims["sub"]
    user = await db_session.get(UserModel, user_id)
    assert user is not None
    return user


# ==============================================================================
# 1. POST /api/v1/library/graph:query & /api/v1/library/graph-query
# ==============================================================================


@pytest.mark.asyncio
@pytest.mark.parametrize("route", ["/api/v1/library/graph:query", "/api/v1/library/graph-query"])
async def test_library_graph_query_valid_modes(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    route: str,
) -> None:
    for mode in ["hybrid", "local", "global"]:
        res = await async_client.post(
            route,
            headers=auth_headers,
            json={
                "query": f"Kiến trúc Transformer trong chế độ {mode}",
                "mode": mode,
                "top_k": 5,
            },
        )
        assert res.status_code == 200, res.text
        data = res.json()
        payload = data.get("data", data)
        assert "subgraph" in payload or "subgraph" in data
        assert "answer" in payload or "answer" in data
        assert "meta" in payload or "meta" in data
        subgraph = payload.get("subgraph") or data.get("subgraph")
        assert "nodes" in subgraph
        assert "edges" in subgraph


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_query",
    ["", "  ", "ab"],
)
async def test_library_graph_query_invalid_query_length_min(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    invalid_query: str,
) -> None:
    res = await async_client.post(
        "/api/v1/library/graph:query",
        headers=auth_headers,
        json={"query": invalid_query, "mode": "hybrid", "top_k": 5},
    )
    assert res.status_code == 400
    body = res.json()
    err_code = body.get("error", {}).get("code") or body.get("detail", {}).get("code")
    assert err_code == "INVALID_SYNTHESIS_QUERY"


@pytest.mark.asyncio
async def test_library_graph_query_invalid_query_length_max(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    too_long = "x" * 1001
    res = await async_client.post(
        "/api/v1/library/graph:query",
        headers=auth_headers,
        json={"query": too_long, "mode": "hybrid", "top_k": 5},
    )
    assert res.status_code == 400
    body = res.json()
    err_code = body.get("error", {}).get("code") or body.get("detail", {}).get("code")
    assert err_code == "INVALID_SYNTHESIS_QUERY"


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_top_k", [0, -1, 51, 100])
async def test_library_graph_query_invalid_top_k(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    invalid_top_k: int,
) -> None:
    res = await async_client.post(
        "/api/v1/library/graph:query",
        headers=auth_headers,
        json={
            "query": "Các mô hình Vision Transformer hiệu quả nhất",
            "mode": "hybrid",
            "top_k": invalid_top_k,
        },
    )
    assert res.status_code == 400
    body = res.json()
    err_code = body.get("error", {}).get("code") or body.get("detail", {}).get("code")
    assert err_code == "INVALID_TOP_K"


@pytest.mark.asyncio
async def test_library_graph_query_folder_not_found(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    fake_folder_id = uuid4()
    res = await async_client.post(
        "/api/v1/library/graph:query",
        headers=auth_headers,
        json={
            "query": "Các mô hình Vision Transformer hiệu quả nhất",
            "mode": "hybrid",
            "folder_id": str(fake_folder_id),
            "top_k": 5,
        },
    )
    assert res.status_code == 404
    body = res.json()
    err_code = body.get("error", {}).get("code") or body.get("detail", {}).get("code")
    assert err_code == "FOLDER_NOT_FOUND"


# ==============================================================================
# 2. GET /api/v1/folders/{id}/bibliometrics
# ==============================================================================


@pytest.mark.asyncio
async def test_get_folder_bibliometrics_success(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    current_user: UserModel,
    db_session: AsyncSession,
) -> None:
    # Create folder for user
    folder = FolderModel(
        id=uuid4(),
        user_id=current_user.id,
        name="Computer Vision Folder",
        color="#3B82F6",
    )
    db_session.add(folder)
    await db_session.commit()

    res = await async_client.get(
        f"/api/v1/folders/{folder.id}/bibliometrics",
        headers=auth_headers,
    )
    assert res.status_code == 200, res.text
    body = res.json()
    payload = body.get("data", body)
    assert str(payload.get("folder_id") or body.get("folder_id")) == str(folder.id)
    assert "prior_works" in payload or "prior_works" in body
    assert "derivative_works" in payload or "derivative_works" in body
    assert "coupling_edges" in payload or "coupling_edges" in body


@pytest.mark.asyncio
async def test_get_folder_bibliometrics_not_found(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    fake_folder_id = uuid4()
    res = await async_client.get(
        f"/api/v1/folders/{fake_folder_id}/bibliometrics",
        headers=auth_headers,
    )
    assert res.status_code == 404
    body = res.json()
    err_code = body.get("error", {}).get("code") or body.get("detail", {}).get("code")
    assert err_code == "FOLDER_NOT_FOUND"


# ==============================================================================
# 3. POST /api/v1/documents/{id}:toggle-star
# ==============================================================================


@pytest.mark.asyncio
async def test_toggle_star_document_lifecycle(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    current_user: UserModel,
    db_session: AsyncSession,
) -> None:
    # 1. Create unstarred document
    doc = DocumentModel(
        id=uuid4(),
        user_id=current_user.id,
        filename="test_paper.pdf",
        title="Attention Is All You Need",
        content_hash="hash_test_paper_star_01",
        file_size_bytes=2048,
        status="ready",
        access_status="open_access_pdf",
        is_starred=False,
        is_persistent=False,
    )
    folder = FolderModel(
        id=uuid4(),
        user_id=current_user.id,
        name="NLP Folder",
        color="#10B981",
    )
    db_session.add_all([doc, folder])
    await db_session.commit()

    # 2. Toggle Star ON
    res_on = await async_client.post(
        f"/api/v1/documents/{doc.id}:toggle-star",
        headers=auth_headers,
        json={"folder_id": str(folder.id)},
    )
    assert res_on.status_code == 200, res_on.text
    data_on = res_on.json()
    payload_on = data_on.get("data", data_on)
    assert payload_on.get("is_starred") is True or data_on.get("is_starred") is True
    assert (
        payload_on.get("graph_extraction_status") == "queued"
        or data_on.get("graph_extraction_status") == "queued"
    )

    # Verify db state updated
    await db_session.refresh(doc)
    assert doc.is_starred is True
    assert doc.folder_id == folder.id

    # 3. Toggle Star OFF
    res_off = await async_client.post(
        f"/api/v1/documents/{doc.id}:toggle-star",
        headers=auth_headers,
        json={},
    )
    assert res_off.status_code == 200, res_off.text
    data_off = res_off.json()
    payload_off = data_off.get("data", data_off)
    assert payload_off.get("is_starred") is False or data_off.get("is_starred") is False
    assert (
        payload_off.get("graph_extraction_status") == "pruned"
        or data_off.get("graph_extraction_status") == "pruned"
    )

    # Verify db state updated
    await db_session.refresh(doc)
    assert doc.is_starred is False


@pytest.mark.asyncio
async def test_toggle_star_document_not_found(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    fake_doc_id = uuid4()
    res = await async_client.post(
        f"/api/v1/documents/{fake_doc_id}:toggle-star",
        headers=auth_headers,
        json={},
    )
    assert res.status_code == 404
    body = res.json()
    err_code = body.get("error", {}).get("code") or body.get("detail", {}).get("code")
    assert err_code == "DOCUMENT_NOT_FOUND"


# ==============================================================================
# 4. PATCH /api/v1/folders/{id} Cycle Detection
# ==============================================================================


@pytest.mark.asyncio
async def test_update_folder_cyclic_hierarchy_rejected(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    current_user: UserModel,
    db_session: AsyncSession,
) -> None:
    # Create folder hierarchy: Parent (A) -> Child (B) -> Grandchild (C)
    folder_a = FolderModel(id=uuid4(), user_id=current_user.id, name="A", parent_id=None)
    folder_b = FolderModel(id=uuid4(), user_id=current_user.id, name="B", parent_id=folder_a.id)
    folder_c = FolderModel(id=uuid4(), user_id=current_user.id, name="C", parent_id=folder_b.id)
    db_session.add_all([folder_a, folder_b, folder_c])
    await db_session.commit()

    # Attempt 1: Move A into itself
    res_self = await async_client.patch(
        f"/api/v1/folders/{folder_a.id}",
        headers=auth_headers,
        json={"parent_id": str(folder_a.id)},
    )
    assert res_self.status_code == 400
    body_self = res_self.json()
    code_self = body_self.get("error", {}).get("code") or body_self.get("detail", {}).get("code")
    assert code_self == "CYCLIC_FOLDER_HIERARCHY"

    # Attempt 2: Move A into its descendant C
    res_descendant = await async_client.patch(
        f"/api/v1/folders/{folder_a.id}",
        headers=auth_headers,
        json={"parent_id": str(folder_c.id)},
    )
    assert res_descendant.status_code == 400
    body_desc = res_descendant.json()
    code_desc = body_desc.get("error", {}).get("code") or body_desc.get("detail", {}).get("code")
    assert code_desc == "CYCLIC_FOLDER_HIERARCHY"


@pytest.mark.asyncio
async def test_upload_duplicate_document_reuses_existing_record(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    # 1. Upload first time
    files = {"file": ("attention.pdf", b"%PDF-1.4 minimal test duplicate body", "application/pdf")}
    res1 = await async_client.post("/api/v1/documents", headers=auth_headers, files=files)
    assert res1.status_code in (200, 201, 202)
    doc1_id = res1.json()["data"]["id"]

    # 2. Upload same content second time
    files2 = {"file": ("attention_duplicate.pdf", b"%PDF-1.4 minimal test duplicate body", "application/pdf")}
    res2 = await async_client.post("/api/v1/documents", headers=auth_headers, files=files2)
    assert res2.status_code in (200, 201, 202)
    doc2_id = res2.json()["data"]["id"]

    # Both uploads should return the exact same document ID (deduplicated)
    assert doc1_id == doc2_id
