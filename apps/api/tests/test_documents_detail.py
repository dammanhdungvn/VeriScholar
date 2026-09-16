"""Automated integration tests for GET /api/v1/documents/{id} endpoint."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.document import DocumentModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import DEFAULT_DEV_USER_ID, get_current_user
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class InMemoryAsyncDetailSession:
    """Fast, deterministic in-memory session test double for document detail queries."""

    def __init__(self) -> None:
        self.documents: dict[UUID, DocumentModel] = {}
        self._added: list[object] = []

    def add(self, obj: object) -> None:
        self._added.append(obj)
        if isinstance(obj, DocumentModel):
            self.documents[obj.id] = obj

    async def flush(self) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def execute(self, statement: Any) -> MagicMock:
        result_mock = MagicMock()
        stmt_str = str(statement)

        try:
            compiled = statement.compile()  # type: ignore[union-attr]
            params = compiled.params or {}
        except Exception:
            params = {}

        target_id = params.get("id_1") or params.get("id")
        target_user_id = params.get("user_id_1") or params.get("user_id")

        if "FROM documents" in stmt_str:
            matched_doc: DocumentModel | None = None
            for d in self.documents.values():
                id_matches = target_id is None or d.id == target_id
                user_matches = target_user_id is None or d.user_id == target_user_id
                if id_matches and user_matches:
                    matched_doc = d
                    break
            result_mock.scalar_one_or_none.return_value = matched_doc
            return result_mock

        return result_mock


@pytest.fixture
def mock_db() -> InMemoryAsyncDetailSession:
    return InMemoryAsyncDetailSession()


@pytest.fixture
def test_user() -> UserModel:
    now = datetime.now(UTC)
    return UserModel(
        id=DEFAULT_DEV_USER_ID,
        email="developer@verischolar.local",
        full_name="VeriScholar Developer",
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def client(
    mock_db: InMemoryAsyncDetailSession,
    test_user: UserModel,
) -> Generator[AsyncClient, None, None]:
    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield mock_db  # type: ignore[misc]

    app.dependency_overrides[get_db] = _get_test_db
    app.dependency_overrides[get_current_user] = lambda: test_user

    transport = ASGITransport(app=app)
    yield AsyncClient(transport=transport, base_url="http://testserver")

    app.dependency_overrides.clear()


def _create_mock_document_detail(
    user_id: UUID,
    doc_id: UUID | None = None,
    filename: str = "attention_is_all_you_need.pdf",
    title: str | None = "Attention Is All You Need",
    authors: list[str] | None = None,
    publication_year: int | None = 2017,
    doi: str | None = "10.48550/arXiv.1706.03762",
    page_count: int | None = 11,
    chunk_count: int = 48,
    file_size_bytes: int = 2215144,
    status: str = "completed",
    is_persistent: bool = False,
    pages_metadata: list | None = None,
) -> DocumentModel:
    target_id = doc_id or uuid4()
    now = datetime.now(UTC)
    return DocumentModel(
        id=target_id,
        user_id=user_id,
        blob_id=uuid4(),
        filename=filename,
        title=title,
        authors=authors if authors is not None else ["Ashish Vaswani", "Noam Shazeer"],
        publication_year=publication_year,
        doi=doi,
        content_hash="b" * 64,
        file_size_bytes=file_size_bytes,
        page_count=page_count,
        chunk_count=chunk_count,
        pages_metadata=pages_metadata
        if pages_metadata is not None
        else [
            {"page_number": 1, "dimensions": [595.28, 841.89], "rotation_deg": 0},
            {"page_number": 2, "dimensions": [841.89, 595.28], "rotation_deg": 90},
        ],
        status=status,
        stage="completed",
        progress=100,
        is_persistent=is_persistent,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_get_document_detail_success(
    client: AsyncClient,
    mock_db: InMemoryAsyncDetailSession,
    test_user: UserModel,
) -> None:
    """Retrieve full metadata of an existing document belonging to current user."""
    doc = _create_mock_document_detail(user_id=test_user.id)
    mock_db.add(doc)

    response = await client.get(f"/api/v1/documents/{doc.id}")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert "data" in body
    assert "meta" in body

    data = body["data"]
    assert data["id"] == str(doc.id)
    assert data["filename"] == "attention_is_all_you_need.pdf"
    assert data["title"] == "Attention Is All You Need"
    assert data["authors"] == ["Ashish Vaswani", "Noam Shazeer"]
    assert data["publication_year"] == 2017
    assert data["doi"] == "10.48550/arXiv.1706.03762"
    assert data["page_count"] == 11
    assert data["chunk_count"] == 48
    assert data["file_size_bytes"] == 2215144
    assert data["status"] == "completed"
    assert data["is_persistent"] is False

    # Verify spatial pages_metadata
    pages = data["pages_metadata"]
    assert len(pages) == 2
    assert pages[0]["page_number"] == 1
    assert pages[0]["dimensions"] == [595.28, 841.89]
    assert pages[0]["rotation_deg"] == 0

    assert pages[1]["page_number"] == 2
    assert pages[1]["dimensions"] == [841.89, 595.28]
    assert pages[1]["rotation_deg"] == 90

    # Verify response envelope metadata
    assert "request_id" in body["meta"]
    assert "timestamp" in body["meta"]


@pytest.mark.asyncio
async def test_get_document_detail_alternative_pages_formats(
    client: AsyncClient,
    mock_db: InMemoryAsyncDetailSession,
    test_user: UserModel,
) -> None:
    """Verify normalizing pages_metadata when stored as width_pt/height_pt or raw tuples."""
    doc = _create_mock_document_detail(
        user_id=test_user.id,
        pages_metadata=[
            {"page_number": 1, "width_pt": 612.0, "height_pt": 792.0, "rotation_deg": 0},
            [2, 792.0, 612.0, 180],
        ],
    )
    mock_db.add(doc)

    response = await client.get(f"/api/v1/documents/{doc.id}")
    assert response.status_code == 200

    pages = response.json()["data"]["pages_metadata"]
    assert len(pages) == 2
    assert pages[0] == {"page_number": 1, "dimensions": [612.0, 792.0], "rotation_deg": 0}
    assert pages[1] == {"page_number": 2, "dimensions": [792.0, 612.0], "rotation_deg": 180}


@pytest.mark.asyncio
async def test_get_document_detail_empty_pages_metadata(
    client: AsyncClient,
    mock_db: InMemoryAsyncDetailSession,
    test_user: UserModel,
) -> None:
    """Document newly uploaded with no pages_metadata yet returns empty list gracefully."""
    doc = _create_mock_document_detail(
        user_id=test_user.id,
        status="uploaded",
        pages_metadata=[],
    )
    mock_db.add(doc)

    response = await client.get(f"/api/v1/documents/{doc.id}")
    assert response.status_code == 200

    data = response.json()["data"]
    assert data["pages_metadata"] == []
    assert data["status"] == "uploaded"


@pytest.mark.asyncio
async def test_get_document_detail_not_found(
    client: AsyncClient,
) -> None:
    """Non-existent document ID returns 404 with DOCUMENT_NOT_FOUND error code."""
    non_existent_id = uuid4()
    response = await client.get(f"/api/v1/documents/{non_existent_id}")
    assert response.status_code == 404

    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "DOCUMENT_NOT_FOUND"
    assert str(non_existent_id) in body["error"]["message"]
    assert body["error"]["field"] == "id"
    assert "meta" in body


@pytest.mark.asyncio
async def test_get_document_detail_multi_tenant_isolation(
    client: AsyncClient,
    mock_db: InMemoryAsyncDetailSession,
    test_user: UserModel,
) -> None:
    """Document owned by another user cannot be accessed by current user (returns 404)."""
    other_user_id = uuid4()
    doc = _create_mock_document_detail(user_id=other_user_id)
    mock_db.add(doc)

    response = await client.get(f"/api/v1/documents/{doc.id}")
    assert response.status_code == 404

    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_document_detail_invalid_uuid(
    client: AsyncClient,
) -> None:
    """Invalid UUID string in path returns 422 Unprocessable Entity."""
    response = await client.get("/api/v1/documents/not-a-valid-uuid-12345")
    assert response.status_code == 422

    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_openapi_schema_contains_document_detail_endpoint(
    client: AsyncClient,
) -> None:
    """Ensure OpenAPI JSON includes GET /api/v1/documents/{document_id} with documentation."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200

    openapi = response.json()
    paths = openapi.get("paths", {})
    assert "/api/v1/documents/{document_id}" in paths

    get_op = paths["/api/v1/documents/{document_id}"].get("get")
    assert get_op is not None
    assert "Spatial Metadata" in get_op.get("summary", "")
    assert "200" in get_op.get("responses", {})
    assert "404" in get_op.get("responses", {})
