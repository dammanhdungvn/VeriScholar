"""Automated integration tests for GET /api/v1/documents/{id}/file endpoint.

Validates binary PDF streaming, HTTP 206 Partial Content (Range header),
HTTP 416 Range Not Satisfiable, multi-tenant scoping, and OpenAPI Swagger documentation.
"""

import hashlib
from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.document import DocumentModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import DEFAULT_DEV_USER_ID, get_current_user, get_document_service
from api.services.document_service import DocumentService
from core.adapters.storage.local import LocalStorageAdapter
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class InMemoryAsyncFileSession:
    """Fast, deterministic in-memory session test double for document file streaming queries."""

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

    async def execute(self, statement: object) -> MagicMock:
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
def mock_db() -> InMemoryAsyncFileSession:
    return InMemoryAsyncFileSession()


@pytest.fixture
def test_user() -> UserModel:
    user = UserModel(email="researcher@verischolar.org")
    user.id = DEFAULT_DEV_USER_ID
    return user


@pytest.fixture
def other_user() -> UserModel:
    user = UserModel(email="other@verischolar.org")
    user.id = uuid4()
    return user


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    # 256 bytes dummy PDF
    header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    payload = b"Academic Paper Content for Range Testing - " * 5
    trailer = b"\n%%EOF\n"
    return header + payload + trailer


@pytest.fixture
def temp_storage(tmp_path: Path) -> LocalStorageAdapter:
    return LocalStorageAdapter(base_directory=tmp_path / "blobs")


@pytest.fixture
def client(
    mock_db: InMemoryAsyncFileSession,
    test_user: UserModel,
    temp_storage: LocalStorageAdapter,
) -> Generator[AsyncClient, None, None]:
    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield mock_db  # type: ignore[misc]

    service = DocumentService(storage=temp_storage)

    app.dependency_overrides[get_db] = _get_test_db
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_document_service] = lambda: service

    transport = ASGITransport(app=app)
    yield AsyncClient(transport=transport, base_url="http://testserver")

    app.dependency_overrides.clear()


async def _save_test_blob(storage: LocalStorageAdapter, content: bytes) -> str:
    content_hash = hashlib.sha256(content).hexdigest()

    async def _stream():
        yield content

    await storage.save_blob(_stream(), content_hash)
    return content_hash


@pytest.mark.asyncio
async def test_stream_document_file_full_200(
    client: AsyncClient,
    mock_db: InMemoryAsyncFileSession,
    test_user: UserModel,
    temp_storage: LocalStorageAdapter,
    sample_pdf_bytes: bytes,
) -> None:
    """Test full file streaming without Range header returns 200 OK."""
    content_hash = await _save_test_blob(temp_storage, sample_pdf_bytes)
    doc_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=test_user.id,
        content_hash=content_hash,
        filename="attention_is_all_you_need.pdf",
        file_size_bytes=len(sample_pdf_bytes),
        status="ready",
        created_at=datetime.now(UTC),
    )
    mock_db.add(doc)

    response = await client.get(f"/api/v1/documents/{doc_id}/file")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert response.headers["Accept-Ranges"] == "bytes"
    assert "attention_is_all_you_need.pdf" in response.headers["Content-Disposition"]
    assert response.headers["Content-Length"] == str(len(sample_pdf_bytes))
    assert response.content == sample_pdf_bytes


@pytest.mark.asyncio
async def test_stream_document_file_partial_206_start_end(
    client: AsyncClient,
    mock_db: InMemoryAsyncFileSession,
    test_user: UserModel,
    temp_storage: LocalStorageAdapter,
    sample_pdf_bytes: bytes,
) -> None:
    """Test partial range streaming returns 206 Partial Content."""
    content_hash = await _save_test_blob(temp_storage, sample_pdf_bytes)
    doc_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=test_user.id,
        content_hash=content_hash,
        filename="paper.pdf",
        file_size_bytes=len(sample_pdf_bytes),
        status="ready",
        created_at=datetime.now(UTC),
    )
    mock_db.add(doc)

    # Request first 100 bytes (0 to 99)
    response = await client.get(
        f"/api/v1/documents/{doc_id}/file",
        headers={"Range": "bytes=0-99"},
    )
    assert response.status_code == 206
    assert response.headers["Content-Type"] == "application/pdf"
    assert response.headers["Accept-Ranges"] == "bytes"
    assert response.headers["Content-Range"] == f"bytes 0-99/{len(sample_pdf_bytes)}"
    assert response.headers["Content-Length"] == "100"
    assert response.content == sample_pdf_bytes[0:100]


@pytest.mark.asyncio
async def test_stream_document_file_partial_206_open_ended(
    client: AsyncClient,
    mock_db: InMemoryAsyncFileSession,
    test_user: UserModel,
    temp_storage: LocalStorageAdapter,
    sample_pdf_bytes: bytes,
) -> None:
    """Test open-ended range streaming (bytes=50-) returns 206 Partial Content."""
    content_hash = await _save_test_blob(temp_storage, sample_pdf_bytes)
    doc_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=test_user.id,
        content_hash=content_hash,
        filename="paper.pdf",
        file_size_bytes=len(sample_pdf_bytes),
        status="ready",
        created_at=datetime.now(UTC),
    )
    mock_db.add(doc)

    response = await client.get(
        f"/api/v1/documents/{doc_id}/file",
        headers={"Range": "bytes=50-"},
    )
    assert response.status_code == 206
    expected_content = sample_pdf_bytes[50:]
    expected_end = len(sample_pdf_bytes) - 1
    assert response.headers["Content-Range"] == f"bytes 50-{expected_end}/{len(sample_pdf_bytes)}"
    assert response.headers["Content-Length"] == str(len(expected_content))
    assert response.content == expected_content


@pytest.mark.asyncio
async def test_stream_document_file_invalid_range_416(
    client: AsyncClient,
    mock_db: InMemoryAsyncFileSession,
    test_user: UserModel,
    temp_storage: LocalStorageAdapter,
    sample_pdf_bytes: bytes,
) -> None:
    """Test out-of-bounds byte range returns 416 Range Not Satisfiable."""
    content_hash = await _save_test_blob(temp_storage, sample_pdf_bytes)
    doc_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=test_user.id,
        content_hash=content_hash,
        filename="paper.pdf",
        file_size_bytes=len(sample_pdf_bytes),
        status="ready",
        created_at=datetime.now(UTC),
    )
    mock_db.add(doc)

    response = await client.get(
        f"/api/v1/documents/{doc_id}/file",
        headers={"Range": f"bytes={len(sample_pdf_bytes) + 500}-"},
    )
    assert response.status_code == 416
    assert response.headers.get("Content-Range") == f"bytes */{len(sample_pdf_bytes)}"


@pytest.mark.asyncio
async def test_stream_document_file_not_found(
    client: AsyncClient,
) -> None:
    """Test streaming non-existent document ID returns 404."""
    non_existent_id = uuid4()
    response = await client.get(f"/api/v1/documents/{non_existent_id}/file")
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_stream_document_file_multi_tenant_isolation(
    client: AsyncClient,
    mock_db: InMemoryAsyncFileSession,
    other_user: UserModel,
    temp_storage: LocalStorageAdapter,
    sample_pdf_bytes: bytes,
) -> None:
    """Test accessing another user's document returns 404 (multi-tenant scoping)."""
    content_hash = await _save_test_blob(temp_storage, sample_pdf_bytes)
    other_doc_id = uuid4()
    doc = DocumentModel(
        id=other_doc_id,
        user_id=other_user.id,  # Owned by different user
        content_hash=content_hash,
        filename="confidential_paper.pdf",
        file_size_bytes=len(sample_pdf_bytes),
        status="ready",
        created_at=datetime.now(UTC),
    )
    mock_db.add(doc)

    response = await client.get(f"/api/v1/documents/{other_doc_id}/file")
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_stream_document_file_missing_physical_blob(
    client: AsyncClient,
    mock_db: InMemoryAsyncFileSession,
    test_user: UserModel,
) -> None:
    """Test when DB record exists but physical blob is missing returns 404 FILE_NOT_FOUND."""
    doc_id = uuid4()
    missing_hash = "a" * 64
    doc = DocumentModel(
        id=doc_id,
        user_id=test_user.id,
        content_hash=missing_hash,
        filename="lost_paper.pdf",
        file_size_bytes=1024,
        status="ready",
        created_at=datetime.now(UTC),
    )
    mock_db.add(doc)

    response = await client.get(f"/api/v1/documents/{doc_id}/file")
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "FILE_NOT_FOUND"


@pytest.mark.asyncio
async def test_openapi_schema_contains_file_stream_endpoint(
    client: AsyncClient,
) -> None:
    """Verify OpenAPI JSON contains GET /api/v1/documents/{document_id}/file documentation."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200

    openapi = response.json()
    paths = openapi.get("paths", {})
    assert "/api/v1/documents/{document_id}/file" in paths

    get_op = paths["/api/v1/documents/{document_id}/file"].get("get")
    assert get_op is not None
    assert "Stream PDF" in get_op.get("summary", "")
    responses = get_op.get("responses", {})
    assert "200" in responses
    assert "206" in responses
    assert "404" in responses
    assert "416" in responses
