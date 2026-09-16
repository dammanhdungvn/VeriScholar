"""Automated integration tests for POST /api/v1/documents/{id}:parse endpoint."""

from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.document import DocumentModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import (
    DEFAULT_DEV_USER_ID,
    get_current_user,
    get_idempotency_port,
)
from core.adapters.cache.idempotency import InMemoryIdempotencyAdapter
from core.ports.idempotency import IIdempotencyPort
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class InMemoryAsyncParseSession:
    """Deterministic in-memory session test double for parse triggers."""

    def __init__(self) -> None:
        self.documents: dict[UUID, DocumentModel] = {}

    def add(self, obj: object) -> None:
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
            result_mock.scalars.return_value.all.return_value = [matched_doc] if matched_doc else []

        return result_mock


@pytest.fixture
def fake_parse_db() -> InMemoryAsyncParseSession:
    """Fixture providing in-memory database double."""
    return InMemoryAsyncParseSession()


@pytest.fixture
def test_idempotency_adapter() -> InMemoryIdempotencyAdapter:
    """Fixture providing clean in-memory idempotency adapter."""
    return InMemoryIdempotencyAdapter()


@pytest.fixture
def sample_uploaded_document(fake_parse_db: InMemoryAsyncParseSession) -> DocumentModel:
    """Create and register a sample uploaded document in memory."""
    doc_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=DEFAULT_DEV_USER_ID,
        blob_id=uuid4(),
        folder_id=None,
        filename="quantum_algorithms_2026.pdf",
        title="Quantum Error Correction in Multi-Qubit Systems",
        authors=["Alice Smith", "Bob Jones"],
        publication_year=2026,
        doi="10.1038/s41586-026-0001-9",
        content_hash="parsehash0123456789abcdef0123456789abcdef0123456789abcdef01234567",
        file_size_bytes=1048576,
        page_count=12,
        chunk_count=0,
        pages_metadata=[],
        parsed_metadata=None,
        status="uploaded",
        stage="queued",
        progress=0,
        error_message=None,
        is_persistent=False,
    )
    fake_parse_db.add(doc)
    return doc


@pytest.fixture
def client(
    fake_parse_db: InMemoryAsyncParseSession,
    test_idempotency_adapter: InMemoryIdempotencyAdapter,
) -> Generator[AsyncClient, None, None]:
    """Test client configured with in-memory double and clean dependencies."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield fake_parse_db  # type: ignore[misc]

    async def override_get_current_user() -> UserModel:
        return UserModel(
            id=DEFAULT_DEV_USER_ID,
            email="researcher@verischolar.org",
            full_name="VeriScholar Researcher",
            hashed_password="hash",
            is_active=True,
        )

    def override_get_idempotency() -> IIdempotencyPort:
        return test_idempotency_adapter

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_idempotency_port] = override_get_idempotency

    transport = ASGITransport(app=app)
    async_client = AsyncClient(transport=transport, base_url="http://testserver")

    yield async_client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_parse_document_success_accepted_202(
    client: AsyncClient,
    sample_uploaded_document: DocumentModel,
) -> None:
    """Test triggering document parse returns 202 Accepted and sets status to processing."""
    doc_id = str(sample_uploaded_document.id)

    response = await client.post(
        f"/api/v1/documents/{doc_id}:parse",
        json={
            "chunk_size": 512,
            "chunk_overlap": 50,
            "extract_tables": True,
            "force_reparse": False,
        },
    )

    assert response.status_code == 202
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["id"] == doc_id
    assert data["status"] == "processing"
    assert data["stage"] == "validation"
    assert data["progress"] == 0
    assert data["links"]["status_url"] == f"/api/v1/documents/{doc_id}/status"
    assert data["links"]["detail_url"] == f"/api/v1/documents/{doc_id}"

    # Verify model state mutation in DB
    assert sample_uploaded_document.status == "processing"
    assert sample_uploaded_document.stage == "validation"
    assert sample_uploaded_document.parsed_metadata is not None
    assert sample_uploaded_document.parsed_metadata["parse_options"]["chunk_size"] == 512


@pytest.mark.asyncio
async def test_parse_document_with_custom_chunking_options(
    client: AsyncClient,
    sample_uploaded_document: DocumentModel,
) -> None:
    """Test parsing with custom chunk_size, chunk_overlap and extract_tables."""
    doc_id = str(sample_uploaded_document.id)

    response = await client.post(
        f"/api/v1/documents/{doc_id}:parse",
        json={
            "chunk_size": 1024,
            "chunk_overlap": 128,
            "extract_tables": False,
            "force_reparse": False,
        },
    )

    assert response.status_code == 202
    assert sample_uploaded_document.parsed_metadata is not None
    options = sample_uploaded_document.parsed_metadata["parse_options"]
    assert options["chunk_size"] == 1024
    assert options["chunk_overlap"] == 128
    assert options["extract_tables"] is False


@pytest.mark.asyncio
async def test_parse_document_idempotency_cache_hit(
    client: AsyncClient,
    sample_uploaded_document: DocumentModel,
) -> None:
    """Test identical Idempotency-Key returns cached response with X-Cache: Idempotent-Hit."""
    doc_id = str(sample_uploaded_document.id)
    idempotency_key = str(uuid4())
    headers = {"Idempotency-Key": idempotency_key}
    payload = {
        "chunk_size": 512,
        "chunk_overlap": 50,
        "extract_tables": True,
        "force_reparse": False,
    }

    # 1st call: Cache Miss
    resp1 = await client.post(
        f"/api/v1/documents/{doc_id}:parse",
        json=payload,
        headers=headers,
    )
    assert resp1.status_code == 202
    assert resp1.headers.get("X-Cache") == "Miss"
    body1 = resp1.json()

    # 2nd call: Cache Hit
    resp2 = await client.post(
        f"/api/v1/documents/{doc_id}:parse",
        json=payload,
        headers=headers,
    )
    assert resp2.status_code == 202
    assert resp2.headers.get("X-Cache") == "Idempotent-Hit"
    body2 = resp2.json()

    # Must return exact identical cached body
    assert body1 == body2


@pytest.mark.asyncio
async def test_parse_document_already_processing_without_force_returns_409(
    client: AsyncClient,
    sample_uploaded_document: DocumentModel,
) -> None:
    """Test triggering parse when document is already processing returns 409 Conflict."""
    sample_uploaded_document.status = "processing"
    sample_uploaded_document.stage = "ocr"
    sample_uploaded_document.progress = 45
    doc_id = str(sample_uploaded_document.id)

    response = await client.post(
        f"/api/v1/documents/{doc_id}:parse",
        json={"force_reparse": False},
    )

    assert response.status_code == 409
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "DOCUMENT_PROCESSING"
    assert "ocr" in body["error"]["message"]


@pytest.mark.asyncio
async def test_parse_document_already_processing_with_force_reparse_restarts_202(
    client: AsyncClient,
    sample_uploaded_document: DocumentModel,
) -> None:
    """Test triggering parse with force_reparse=True restarts already-processing document."""
    sample_uploaded_document.status = "processing"
    sample_uploaded_document.stage = "chunking"
    sample_uploaded_document.progress = 75
    doc_id = str(sample_uploaded_document.id)

    response = await client.post(
        f"/api/v1/documents/{doc_id}:parse",
        json={"force_reparse": True},
    )

    assert response.status_code == 202
    body = response.json()
    assert body["success"] is True
    assert body["data"]["stage"] == "validation"
    assert body["data"]["progress"] == 0
    assert sample_uploaded_document.stage == "validation"
    assert sample_uploaded_document.progress == 0


@pytest.mark.asyncio
async def test_parse_document_already_completed_without_force(
    client: AsyncClient,
    sample_uploaded_document: DocumentModel,
) -> None:
    """Test completed document without force_reparse returns guidance message."""
    sample_uploaded_document.status = "completed"
    sample_uploaded_document.stage = "completed"
    sample_uploaded_document.progress = 100
    doc_id = str(sample_uploaded_document.id)

    response = await client.post(
        f"/api/v1/documents/{doc_id}:parse",
        json={"force_reparse": False},
    )

    assert response.status_code == 202
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "completed"
    assert "already parsed" in body["data"]["message"]


@pytest.mark.asyncio
async def test_parse_document_already_completed_with_force_reparse(
    client: AsyncClient,
    sample_uploaded_document: DocumentModel,
) -> None:
    """Test completed document with force_reparse=True re-transitions to processing."""
    sample_uploaded_document.status = "completed"
    sample_uploaded_document.stage = "completed"
    sample_uploaded_document.progress = 100
    doc_id = str(sample_uploaded_document.id)

    response = await client.post(
        f"/api/v1/documents/{doc_id}:parse",
        json={"force_reparse": True},
    )

    assert response.status_code == 202
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "processing"
    assert body["data"]["stage"] == "validation"
    assert sample_uploaded_document.status == "processing"


@pytest.mark.asyncio
async def test_parse_document_not_found(client: AsyncClient) -> None:
    """Test parsing non-existent document returns 404 DOCUMENT_NOT_FOUND."""
    random_id = str(uuid4())

    response = await client.post(
        f"/api/v1/documents/{random_id}:parse",
        json={},
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_parse_document_multi_tenant_isolation(
    client: AsyncClient,
    fake_parse_db: InMemoryAsyncParseSession,
) -> None:
    """Test user cannot parse a document owned by another user."""
    other_user_id = uuid4()
    other_doc_id = uuid4()
    other_doc = DocumentModel(
        id=other_doc_id,
        user_id=other_user_id,
        filename="other_user_paper.pdf",
        content_hash="otherhash0123456789abcdef0123456789abcdef0123456789abcdef01234567",
        file_size_bytes=2048,
        status="uploaded",
        stage="queued",
        progress=0,
        is_persistent=False,
    )
    fake_parse_db.add(other_doc)

    response = await client.post(
        f"/api/v1/documents/{other_doc_id}:parse",
        json={},
    )

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_parse_document_validation_overlap_gte_chunk_size(
    client: AsyncClient,
    sample_uploaded_document: DocumentModel,
) -> None:
    """Test chunk_overlap >= chunk_size triggers validation error (422)."""
    doc_id = str(sample_uploaded_document.id)

    response = await client.post(
        f"/api/v1/documents/{doc_id}:parse",
        json={
            "chunk_size": 100,
            "chunk_overlap": 150,
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_parse_document_invalid_uuid(client: AsyncClient) -> None:
    """Test non-UUID path parameter returns 422 Unprocessable Entity."""
    response = await client.post(
        "/api/v1/documents/invalid-non-uuid-string:parse",
        json={},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_openapi_schema_contains_parse_endpoint(client: AsyncClient) -> None:
    """Test OpenAPI spec contains POST /api/v1/documents/{document_id}:parse."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()

    path_entry = spec["paths"].get("/api/v1/documents/{document_id}:parse")
    assert path_entry is not None
    assert "post" in path_entry

    post_op = path_entry["post"]
    assert "202" in post_op["responses"]
    assert "404" in post_op["responses"]
    assert "409" in post_op["responses"]
    assert "422" in post_op["responses"]
    assert post_op["summary"] == "Kích hoạt / Bóc tách lại với Idempotency"
