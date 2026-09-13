"""Automated integration tests for GET /api/v1/documents/{id}/status endpoint."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
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


class InMemoryAsyncStatusSession:
    """Fast, deterministic in-memory session test double for document status queries."""

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
def mock_db() -> InMemoryAsyncStatusSession:
    return InMemoryAsyncStatusSession()


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
    mock_db: InMemoryAsyncStatusSession,
    test_user: UserModel,
) -> Generator[AsyncClient, None, None]:
    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield mock_db  # type: ignore[misc]

    app.dependency_overrides[get_db] = _get_test_db
    app.dependency_overrides[get_current_user] = lambda: test_user

    transport = ASGITransport(app=app)
    yield AsyncClient(transport=transport, base_url="http://testserver")

    app.dependency_overrides.clear()


def _create_mock_document_status(
    user_id: UUID,
    doc_id: UUID | None = None,
    filename: str = "quantum_computing.pdf",
    status: str = "processing",
    stage: str = "running_ocr",
    progress: int = 45,
    error_message: str | None = None,
    parsed_metadata: dict | None = None,
) -> DocumentModel:
    now = datetime.now(UTC)
    doc = DocumentModel(
        id=doc_id or uuid4(),
        user_id=user_id,
        filename=filename,
        content_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        file_size_bytes=1048576,
        status=status,
        stage=stage,
        progress=progress,
        error_message=error_message,
        parsed_metadata=parsed_metadata,
        pages_metadata=[],
        is_persistent=False,
        created_at=now,
        updated_at=now,
    )
    return doc


@pytest.mark.asyncio
async def test_get_document_status_processing_running_ocr(
    client: AsyncClient,
    mock_db: InMemoryAsyncStatusSession,
    test_user: UserModel,
) -> None:
    """Validate polling status during active OCR extraction stage."""
    doc = _create_mock_document_status(
        user_id=test_user.id,
        status="processing",
        stage="running_ocr",
        progress=45,
    )
    mock_db.add(doc)

    async with client as c:
        response = await c.get(f"/api/v1/documents/{doc.id}/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True

    data = payload["data"]
    assert data["id"] == str(doc.id)
    assert data["status"] == "processing"
    assert data["stage"] == "running_ocr"
    assert data["progress"] == 45
    assert data["error_message"] is None

    # Verify 5-stage pipeline breakdown
    stages = data["stages_detail"]
    assert stages["validation"] == "completed"
    assert stages["layout_detection"] == "completed"
    assert stages["ocr"] == "in_progress"
    assert stages["chunking"] == "pending"
    assert stages["embedding"] == "pending"

    assert "request_id" in payload["meta"]
    assert "timestamp" in payload["meta"]


@pytest.mark.asyncio
async def test_get_document_status_uploaded_queued(
    client: AsyncClient,
    mock_db: InMemoryAsyncStatusSession,
    test_user: UserModel,
) -> None:
    """Validate status response immediately after upload when job is queued."""
    doc = _create_mock_document_status(
        user_id=test_user.id,
        status="uploaded",
        stage="queued",
        progress=0,
    )
    mock_db.add(doc)

    async with client as c:
        response = await c.get(f"/api/v1/documents/{doc.id}/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True

    data = payload["data"]
    assert data["status"] == "uploaded"
    assert data["stage"] == "queued"
    assert data["progress"] == 0

    stages = data["stages_detail"]
    assert stages["validation"] == "pending"
    assert stages["layout_detection"] == "pending"
    assert stages["ocr"] == "pending"
    assert stages["chunking"] == "pending"
    assert stages["embedding"] == "pending"


@pytest.mark.asyncio
async def test_get_document_status_completed(
    client: AsyncClient,
    mock_db: InMemoryAsyncStatusSession,
    test_user: UserModel,
) -> None:
    """Validate status response when document processing finishes completely."""
    doc = _create_mock_document_status(
        user_id=test_user.id,
        status="completed",
        stage="completed",
        progress=100,
    )
    mock_db.add(doc)

    async with client as c:
        response = await c.get(f"/api/v1/documents/{doc.id}/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True

    data = payload["data"]
    assert data["status"] == "completed"
    assert data["stage"] == "completed"
    assert data["progress"] == 100

    stages = data["stages_detail"]
    assert stages["validation"] == "completed"
    assert stages["layout_detection"] == "completed"
    assert stages["ocr"] == "completed"
    assert stages["chunking"] == "completed"
    assert stages["embedding"] == "completed"


@pytest.mark.asyncio
async def test_get_document_status_failed_with_error_message(
    client: AsyncClient,
    mock_db: InMemoryAsyncStatusSession,
    test_user: UserModel,
) -> None:
    """Validate status response when document processing encounters an error."""
    doc = _create_mock_document_status(
        user_id=test_user.id,
        status="failed",
        stage="ocr",
        progress=30,
        error_message="Corrupted PDF font table: unable to extract text characters.",
    )
    mock_db.add(doc)

    async with client as c:
        response = await c.get(f"/api/v1/documents/{doc.id}/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True

    data = payload["data"]
    assert data["status"] == "failed"
    assert data["stage"] == "ocr"
    assert data["error_message"] == "Corrupted PDF font table: unable to extract text characters."

    stages = data["stages_detail"]
    assert stages["validation"] == "completed"
    assert stages["layout_detection"] == "completed"
    assert stages["ocr"] == "failed"
    assert stages["chunking"] == "pending"
    assert stages["embedding"] == "pending"


@pytest.mark.asyncio
async def test_get_document_status_custom_stored_stages_detail(
    client: AsyncClient,
    mock_db: InMemoryAsyncStatusSession,
    test_user: UserModel,
) -> None:
    """Validate status endpoint when worker recorded explicit stages_detail."""
    stored_stages = {
        "validation": "completed",
        "layout_detection": "completed",
        "ocr": "completed",
        "chunking": "in_progress",
        "embedding": "pending",
    }
    doc = _create_mock_document_status(
        user_id=test_user.id,
        status="processing",
        stage="chunking",
        progress=60,
        parsed_metadata={"stages_detail": stored_stages},
    )
    mock_db.add(doc)

    async with client as c:
        response = await c.get(f"/api/v1/documents/{doc.id}/status")

    assert response.status_code == 200
    payload = response.json()
    data = payload["data"]
    assert data["stages_detail"] == stored_stages


@pytest.mark.asyncio
async def test_get_document_status_not_found(
    client: AsyncClient,
    mock_db: InMemoryAsyncStatusSession,
    test_user: UserModel,
) -> None:
    """Validate HTTP 404 response with structured error envelope for non-existent document."""
    non_existent_id = uuid4()

    async with client as c:
        response = await c.get(f"/api/v1/documents/{non_existent_id}/status")

    assert response.status_code == 404
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "DOCUMENT_NOT_FOUND"
    assert str(non_existent_id) in payload["error"]["message"]


@pytest.mark.asyncio
async def test_get_document_status_multi_tenant_isolation(
    client: AsyncClient,
    mock_db: InMemoryAsyncStatusSession,
    test_user: UserModel,
) -> None:
    """Ensure user cannot poll status of documents owned by another user."""
    other_user_id = uuid4()
    doc_of_other_user = _create_mock_document_status(
        user_id=other_user_id,
        status="processing",
    )
    mock_db.add(doc_of_other_user)

    async with client as c:
        response = await c.get(f"/api/v1/documents/{doc_of_other_user.id}/status")

    assert response.status_code == 404
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_document_status_invalid_uuid(
    client: AsyncClient,
) -> None:
    """Validate HTTP 422 validation error when path parameter is an invalid UUID string."""
    async with client as c:
        response = await c.get("/api/v1/documents/not-a-valid-uuid/status")

    assert response.status_code == 422
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_openapi_schema_contains_status_endpoint(
    client: AsyncClient,
) -> None:
    """Validate that GET /api/v1/documents/{document_id}/status is registered in OpenAPI schema."""
    async with client as c:
        response = await c.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert "/api/v1/documents/{document_id}/status" in schema["paths"]
    status_op = schema["paths"]["/api/v1/documents/{document_id}/status"]["get"]
    assert "200" in status_op["responses"]
    assert "404" in status_op["responses"]
