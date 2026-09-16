"""Automated integration tests for POST /api/v1/documents endpoint."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.blob import DocumentStorageBlobModel
from api.db.models.document import DocumentModel
from api.db.models.session import ResearchSessionModel, SessionDocumentModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import DEFAULT_DEV_USER_ID, get_current_user, get_storage
from core.adapters.storage.local import LocalStorageAdapter
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

VALID_PDF_BYTES = b"%PDF-1.5\n%Header binary marker\n1 0 obj\n<< /Type /Catalog >>\nendobj\n"


class InMemoryAsyncSession:
    """Fast, deterministic in-memory session test double."""

    def __init__(self) -> None:
        self.blobs: dict[str, DocumentStorageBlobModel] = {}
        self.documents: dict[UUID, DocumentModel] = {}
        self.sessions: dict[UUID, ResearchSessionModel] = {}
        self.session_docs: list[SessionDocumentModel] = []
        self._added: list[object] = []

    def add(self, obj: object) -> None:
        self._added.append(obj)
        if isinstance(obj, DocumentStorageBlobModel):
            self.blobs[obj.content_hash] = obj
        elif isinstance(obj, DocumentModel):
            self.documents[obj.id] = obj
        elif isinstance(obj, ResearchSessionModel):
            self.sessions[obj.id] = obj
        elif isinstance(obj, SessionDocumentModel):
            self.session_docs.append(obj)

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

        # 1. Select DocumentStorageBlobModel by content_hash
        if "FROM document_storage_blobs" in stmt_str:
            matched_blob = None
            for b in self.blobs.values():
                if b.content_hash in params.values() or b.content_hash in str(params):
                    matched_blob = b
                    break
            result_mock.scalar_one_or_none.return_value = matched_blob

        # 2. Select ResearchSessionModel by id
        elif "FROM research_sessions" in stmt_str:
            matched_session = None
            for s in self.sessions.values():
                if s.id in params.values() or str(s.id) in str(params):
                    matched_session = s
                    break
            result_mock.scalar_one_or_none.return_value = matched_session

        # 3. Select count(*) FROM session_documents
        elif "FROM session_documents" in stmt_str and "count" in stmt_str:
            session_id = next((v for v in params.values() if isinstance(v, UUID)), None)
            if session_id is None:
                for v in params.values():
                    try:
                        session_id = UUID(str(v))
                        break
                    except (ValueError, TypeError):
                        pass

            if session_id:
                count = sum(1 for sd in self.session_docs if sd.session_id == session_id)
            else:
                count = len(self.session_docs)
            result_mock.scalar.return_value = count

        return result_mock


@pytest.fixture
def mock_storage(tmp_path: Path) -> LocalStorageAdapter:
    return LocalStorageAdapter(base_directory=tmp_path / "test_blobs")


@pytest.fixture
def mock_db() -> InMemoryAsyncSession:
    return InMemoryAsyncSession()


@pytest.fixture
def test_user() -> UserModel:
    return UserModel(
        id=DEFAULT_DEV_USER_ID,
        email="test@verischolar.org",
        full_name="Tester",
        hashed_password="hash",
        is_active=True,
    )


@pytest.fixture
def client(
    mock_storage: LocalStorageAdapter,
    mock_db: InMemoryAsyncSession,
    test_user: UserModel,
) -> Generator[AsyncClient, None, None]:
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield mock_db  # type: ignore[misc]

    app.dependency_overrides[get_storage] = lambda: mock_storage
    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = lambda: test_user

    transport = ASGITransport(app=app)
    yield AsyncClient(transport=transport, base_url="http://testserver")

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_valid_pdf_success(client: AsyncClient, mock_db: InMemoryAsyncSession) -> None:
    """Verify standard valid PDF upload returns 201 Created and Single Resource Envelope."""
    files = {"file": ("attention.pdf", VALID_PDF_BYTES, "application/pdf")}

    response = await client.post("/api/v1/documents", files=files)

    assert response.status_code == 201
    body = response.json()

    assert body["success"] is True
    assert "data" in body
    data = body["data"]

    assert data["filename"] == "attention.pdf"
    assert data["file_size_bytes"] == len(VALID_PDF_BYTES)
    assert data["status"] == "uploaded"
    assert data["stage"] == "queued"
    assert data["progress"] == 0
    assert data["is_persistent"] is False
    assert data["session_id"] is None

    # HATEOAS Links validation
    doc_id = data["id"]
    links = data["links"]
    assert links["self_url"] == f"/api/v1/documents/{doc_id}"
    assert links["status_url"] == f"/api/v1/documents/{doc_id}/status"
    assert links["file_url"] == f"/api/v1/documents/{doc_id}/file"
    assert links["parse_url"] == f"/api/v1/documents/{doc_id}:parse"

    # Verify saved in test db
    assert len(mock_db.documents) == 1
    assert len(mock_db.blobs) == 1


@pytest.mark.asyncio
async def test_upload_with_valid_session_id(
    client: AsyncClient, mock_db: InMemoryAsyncSession
) -> None:
    """Verify document upload successfully attaches to an existing research session."""
    session_id = uuid4()
    mock_session = ResearchSessionModel(
        id=session_id,
        user_id=DEFAULT_DEV_USER_ID,
        title="Attention Mechanisms Study",
        version=1,
    )
    mock_db.add(mock_session)

    files = {"file": ("transformer.pdf", VALID_PDF_BYTES, "application/pdf")}
    data_payload = {"session_id": str(session_id)}

    response = await client.post("/api/v1/documents", files=files, data=data_payload)

    assert response.status_code == 201
    body = response.json()
    assert body["data"]["session_id"] == str(session_id)

    # Verify session_documents junction table record created
    assert len(mock_db.session_docs) == 1
    assert mock_db.session_docs[0].session_id == session_id


@pytest.mark.asyncio
async def test_upload_cas_deduplication(client: AsyncClient, mock_db: InMemoryAsyncSession) -> None:
    """Verify duplicate uploads do not duplicate physical blobs and increment ref_count."""
    files_1 = {"file": ("upload_1.pdf", VALID_PDF_BYTES, "application/pdf")}
    res_1 = await client.post("/api/v1/documents", files=files_1)
    assert res_1.status_code == 201
    hash_1 = res_1.json()["data"]["content_hash"]

    # Check blob ref_count is 1
    blob = mock_db.blobs[hash_1]
    assert blob.ref_count == 1

    # Second upload with identical content
    files_2 = {"file": ("upload_2.pdf", VALID_PDF_BYTES, "application/pdf")}
    res_2 = await client.post("/api/v1/documents", files=files_2)
    assert res_2.status_code == 201
    hash_2 = res_2.json()["data"]["content_hash"]

    assert hash_1 == hash_2
    assert blob.ref_count == 2
    assert len(mock_db.documents) == 2
    assert len(mock_db.blobs) == 1


@pytest.mark.asyncio
async def test_upload_invalid_magic_bytes_rejected(client: AsyncClient) -> None:
    """Verify non-PDF file or corrupted header is rejected with HTTP 400."""
    fake_pdf = b"Plain text file disguised as a PDF document"
    files = {"file": ("fake.pdf", fake_pdf, "application/pdf")}

    response = await client.post("/api/v1/documents", files=files)

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_FILE_TYPE"
    assert "%PDF-" in body["error"]["message"]


@pytest.mark.asyncio
async def test_upload_session_not_found(client: AsyncClient) -> None:
    """Verify specifying a non-existent session_id returns HTTP 404."""
    random_session_id = uuid4()
    files = {"file": ("paper.pdf", VALID_PDF_BYTES, "application/pdf")}
    data_payload = {"session_id": str(random_session_id)}

    response = await client.post("/api/v1/documents", files=files, data=data_payload)

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_upload_session_limit_exceeded(
    client: AsyncClient, mock_db: InMemoryAsyncSession
) -> None:
    """Verify exceeding 5 documents in a session triggers HTTP 409 Conflict."""
    session_id = uuid4()
    mock_session = ResearchSessionModel(
        id=session_id,
        user_id=DEFAULT_DEV_USER_ID,
        title="Full Session",
        version=1,
    )
    mock_db.add(mock_session)

    # Pre-fill session with 5 documents
    for _ in range(5):
        mock_db.session_docs.append(
            SessionDocumentModel(
                session_id=session_id,
                document_id=uuid4(),
                added_at=datetime.now(UTC),
            )
        )

    files = {"file": ("paper_6.pdf", VALID_PDF_BYTES, "application/pdf")}
    data_payload = {"session_id": str(session_id)}

    response = await client.post("/api/v1/documents", files=files, data=data_payload)

    assert response.status_code == 409
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "SESSION_DOCUMENT_LIMIT_EXCEEDED"


@pytest.mark.asyncio
async def test_upload_oversized_file_rejected(client: AsyncClient) -> None:
    """Verify file exceeding 50MB ceiling is rejected with HTTP 413 Payload Too Large."""
    oversized_bytes = b"%PDF-1.4\n" + b"A" * 52_428_800
    files = {"file": ("oversized.pdf", oversized_bytes, "application/pdf")}

    response = await client.post("/api/v1/documents", files=files)

    assert response.status_code == 413
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "FILE_TOO_LARGE"


@pytest.mark.asyncio
async def test_openapi_swagger_schema_contains_upload_endpoint(client: AsyncClient) -> None:
    """Verify Swagger UI and OpenAPI 3.1 specification properly expose the upload endpoint."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200

    openapi = response.json()
    paths = openapi.get("paths", {})
    assert "/api/v1/documents" in paths

    post_op = paths["/api/v1/documents"]["post"]
    assert post_op["summary"] == "Tải lên PDF bài báo (nhận session_id tùy chọn)"
    assert "Module 1: Documents" in post_op["tags"]

    # Verify response codes documented in OpenAPI schema
    responses = post_op["responses"]
    assert "201" in responses
    assert "400" in responses
    assert "404" in responses
    assert "409" in responses
    assert "413" in responses
