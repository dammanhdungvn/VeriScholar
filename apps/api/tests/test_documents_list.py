"""Automated integration tests for GET /api/v1/documents endpoint."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime, timedelta
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


class InMemoryAsyncListSession:
    """Fast, deterministic in-memory session test double for query and pagination tests."""

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

        target_user_id = params.get("user_id_1") or params.get("user_id")
        target_status = params.get("status_1") or params.get("status")

        # 1. Count query
        if "count(" in stmt_str and "FROM documents" in stmt_str:
            matched = [
                d
                for d in self.documents.values()
                if (target_user_id is None or d.user_id == target_user_id)
                and (target_status is None or d.status == target_status)
            ]
            result_mock.scalar.return_value = len(matched)
            return result_mock

        # 2. Select query with pagination
        if "FROM documents" in stmt_str:
            matched = [
                d
                for d in self.documents.values()
                if (target_user_id is None or d.user_id == target_user_id)
                and (target_status is None or d.status == target_status)
            ]
            # Order by created_at desc
            matched.sort(key=lambda d: d.created_at, reverse=True)

            # Extract limit and offset
            limit = params.get("param_1") or 20
            offset = params.get("param_2") or 0

            for k, v in params.items():
                if "offset" in k.lower():
                    offset = v
                elif "limit" in k.lower():
                    limit = v

            paginated = matched[offset : offset + limit]
            result_mock.scalars.return_value.all.return_value = paginated
            return result_mock

        return result_mock


@pytest.fixture
def mock_db() -> InMemoryAsyncListSession:
    return InMemoryAsyncListSession()


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
    mock_db: InMemoryAsyncListSession,
    test_user: UserModel,
) -> Generator[AsyncClient, None, None]:
    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield mock_db  # type: ignore[misc]

    app.dependency_overrides[get_db] = _get_test_db
    app.dependency_overrides[get_current_user] = lambda: test_user

    transport = ASGITransport(app=app)
    yield AsyncClient(transport=transport, base_url="http://testserver")

    app.dependency_overrides.clear()


def _create_mock_document(
    user_id: UUID,
    filename: str,
    status: str = "completed",
    created_offset_minutes: int = 0,
    title: str | None = None,
) -> DocumentModel:
    doc_id = uuid4()
    now = datetime.now(UTC) - timedelta(minutes=created_offset_minutes)
    return DocumentModel(
        id=doc_id,
        user_id=user_id,
        blob_id=uuid4(),
        filename=filename,
        title=title,
        content_hash="a" * 64,
        file_size_bytes=1024,
        status=status,
        stage="completed",
        progress=100,
        is_persistent=False,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_list_documents_empty(
    client: AsyncClient,
) -> None:
    """When user has no documents, return empty collection with 1 page and null RFC links."""
    response = await client.get("/api/v1/documents")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"] == []
    assert body["meta"]["total"] == 0
    assert body["meta"]["page"] == 1
    assert body["meta"]["per_page"] == 20
    assert body["meta"]["total_pages"] == 1
    assert "request_id" in body["meta"]
    assert "timestamp" in body["meta"]

    # RFC 8288 links for empty single page
    links = body["links"]
    assert links["first"] == "/api/v1/documents?page=1&per_page=20"
    assert links["self"] == "/api/v1/documents?page=1&per_page=20"
    assert links["prev"] is None
    assert links["next"] is None
    assert links["last"] == "/api/v1/documents?page=1&per_page=20"


@pytest.mark.asyncio
async def test_list_documents_pagination_first_page(
    client: AsyncClient,
    mock_db: InMemoryAsyncListSession,
    test_user: UserModel,
) -> None:
    """Pagination: page 1 of 3 returns next link and null prev link."""
    for i in range(5):
        doc = _create_mock_document(
            user_id=test_user.id,
            filename=f"paper_{i}.pdf",
            created_offset_minutes=i * 10,
            title=f"Paper {i}",
        )
        mock_db.add(doc)

    response = await client.get("/api/v1/documents?page=1&per_page=2")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 2
    assert body["data"][0]["filename"] == "paper_0.pdf"
    assert body["data"][0]["title"] == "Paper 0"
    assert body["meta"]["total"] == 5
    assert body["meta"]["page"] == 1
    assert body["meta"]["per_page"] == 2
    assert body["meta"]["total_pages"] == 3

    links = body["links"]
    assert links["first"] == "/api/v1/documents?page=1&per_page=2"
    assert links["self"] == "/api/v1/documents?page=1&per_page=2"
    assert links["prev"] is None
    assert links["next"] == "/api/v1/documents?page=2&per_page=2"
    assert links["last"] == "/api/v1/documents?page=3&per_page=2"


@pytest.mark.asyncio
async def test_list_documents_pagination_middle_page(
    client: AsyncClient,
    mock_db: InMemoryAsyncListSession,
    test_user: UserModel,
) -> None:
    """Pagination: middle page (page 2 of 3) returns valid prev and next links."""
    for i in range(5):
        doc = _create_mock_document(
            user_id=test_user.id,
            filename=f"paper_{i}.pdf",
            created_offset_minutes=i * 10,
        )
        mock_db.add(doc)

    response = await client.get("/api/v1/documents?page=2&per_page=2")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 2
    assert body["data"][0]["filename"] == "paper_2.pdf"
    assert body["meta"]["page"] == 2

    links = body["links"]
    assert links["prev"] == "/api/v1/documents?page=1&per_page=2"
    assert links["self"] == "/api/v1/documents?page=2&per_page=2"
    assert links["next"] == "/api/v1/documents?page=3&per_page=2"


@pytest.mark.asyncio
async def test_list_documents_pagination_last_page(
    client: AsyncClient,
    mock_db: InMemoryAsyncListSession,
    test_user: UserModel,
) -> None:
    """Pagination: last page (page 3 of 3) returns null next link."""
    for i in range(5):
        doc = _create_mock_document(
            user_id=test_user.id,
            filename=f"paper_{i}.pdf",
            created_offset_minutes=i * 10,
        )
        mock_db.add(doc)

    response = await client.get("/api/v1/documents?page=3&per_page=2")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["filename"] == "paper_4.pdf"

    links = body["links"]
    assert links["prev"] == "/api/v1/documents?page=2&per_page=2"
    assert links["self"] == "/api/v1/documents?page=3&per_page=2"
    assert links["next"] is None
    assert links["last"] == "/api/v1/documents?page=3&per_page=2"


@pytest.mark.asyncio
async def test_list_documents_filter_status(
    client: AsyncClient,
    mock_db: InMemoryAsyncListSession,
    test_user: UserModel,
) -> None:
    """Status filter only returns matching documents and retains filter in RFC links."""
    mock_db.add(_create_mock_document(test_user.id, "uploaded_doc.pdf", status="uploaded"))
    mock_db.add(_create_mock_document(test_user.id, "completed_doc.pdf", status="completed"))
    mock_db.add(_create_mock_document(test_user.id, "failed_doc.pdf", status="failed"))

    response = await client.get("/api/v1/documents?status=completed")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["meta"]["total"] == 1
    assert len(body["data"]) == 1
    assert body["data"][0]["status"] == "completed"
    assert body["data"][0]["filename"] == "completed_doc.pdf"

    links = body["links"]
    assert "status=completed" in links["self"]
    assert "status=completed" in links["first"]


@pytest.mark.asyncio
async def test_list_documents_multi_tenant_isolation(
    client: AsyncClient,
    mock_db: InMemoryAsyncListSession,
    test_user: UserModel,
) -> None:
    """Documents belonging to another user are strictly excluded from current user's results."""
    other_user_id = uuid4()
    mock_db.add(_create_mock_document(test_user.id, "my_paper.pdf"))
    mock_db.add(_create_mock_document(other_user_id, "other_paper.pdf"))

    response = await client.get("/api/v1/documents")
    assert response.status_code == 200

    body = response.json()
    assert body["meta"]["total"] == 1
    assert len(body["data"]) == 1
    assert body["data"][0]["filename"] == "my_paper.pdf"


@pytest.mark.asyncio
async def test_list_documents_validation_errors(
    client: AsyncClient,
) -> None:
    """Invalid query params (page < 1 or per_page > 100) return 422 Unprocessable Entity."""
    res_page = await client.get("/api/v1/documents?page=0")
    assert res_page.status_code == 422

    res_per_page = await client.get("/api/v1/documents?per_page=101")
    assert res_per_page.status_code == 422


@pytest.mark.asyncio
async def test_openapi_schema_contains_list_documents() -> None:
    """Swagger OpenAPI 3.1 documentation contains GET /api/v1/documents with RFC envelope."""
    schema = app.openapi()
    assert "/api/v1/documents" in schema["paths"]
    get_op = schema["paths"]["/api/v1/documents"]["get"]
    assert get_op["summary"] == "Danh sách bài báo (phân trang page/per_page)"
    assert "200" in get_op["responses"]
