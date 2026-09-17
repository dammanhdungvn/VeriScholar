"""Automated integration tests for POST /api/v1/documents/{id}/summary:generate endpoint."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pymupdf
import pytest
from api import app
from api.db.models.chunk import DocumentChunkModel
from api.db.models.document import DocumentModel
from api.db.models.summary import DocumentSummaryModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import (
    DEFAULT_DEV_USER_ID,
    get_current_user,
    get_document_service,
    get_idempotency_port,
)
from api.services.document_service import DocumentService
from core.adapters.cache.idempotency import InMemoryIdempotencyAdapter
from core.ports.storage import IBlobStoragePort
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class InMemoryAsyncSummaryGenerateSession:
    """Deterministic in-memory database test double for document summary generate tests."""

    def __init__(self) -> None:
        self.documents: dict[UUID, DocumentModel] = {}
        self.chunks: list[DocumentChunkModel] = []
        self.summaries: dict[UUID, DocumentSummaryModel] = {}

    def add(self, obj: object) -> None:
        if isinstance(obj, DocumentModel):
            self.documents[obj.id] = obj
        elif isinstance(obj, DocumentChunkModel):
            self.chunks.append(obj)
        elif isinstance(obj, DocumentSummaryModel):
            self.summaries[obj.document_id] = obj

    def add_all(self, objs: list[Any]) -> None:
        for obj in objs:
            self.add(obj)

    async def flush(self) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def refresh(self, obj: object) -> None:
        pass

    async def delete(self, obj: object) -> None:
        pass

    async def get(self, model: type[Any], ident: Any) -> Any:
        if model == DocumentModel:
            return self.documents.get(ident)
        return None

    async def execute(self, statement: Any) -> MagicMock:
        result_mock = MagicMock()
        statement_str = str(statement)

        try:
            compiled = statement.compile()
            params = compiled.params or {}
        except Exception:
            params = {}

        # 1. DocumentModel lookup
        if "FROM documents" in statement_str:
            target_id = None
            target_user_id = None
            for k, v in params.items():
                if "user_id" in k:
                    target_user_id = v
                elif "id" in k and isinstance(v, UUID):
                    target_id = v

            doc = None
            if target_id and target_id in self.documents:
                cand = self.documents[target_id]
                if target_user_id is None or cand.user_id == target_user_id:
                    doc = cand

            result_mock.scalar_one_or_none.return_value = doc
            return result_mock

        # 2. DocumentSummaryModel lookup
        if "FROM document_summaries" in statement_str:
            target_doc_id = None
            for k, v in params.items():
                if "document_id" in k and isinstance(v, UUID):
                    target_doc_id = v
            summary = self.summaries.get(target_doc_id) if target_doc_id else None
            result_mock.scalar_one_or_none.return_value = summary
            return result_mock

        # 3. DocumentChunkModel lookup
        if "FROM document_chunks" in statement_str:
            target_doc_id = None
            for k, v in params.items():
                if "document_id" in k and isinstance(v, UUID):
                    target_doc_id = v
            matched_chunks = [c for c in self.chunks if c.document_id == target_doc_id]
            scalars_mock = MagicMock()
            scalars_mock.all.return_value = matched_chunks
            result_mock.scalars.return_value = scalars_mock
            return result_mock

        result_mock.scalar_one_or_none.return_value = None
        result_mock.scalars.return_value.all.return_value = []
        return result_mock


class MockBlobStorage(IBlobStoragePort):
    """In-memory mock storage port for unit and integration testing."""

    def __init__(self) -> None:
        self.blobs: dict[str, bytes] = {}

    async def store(self, content: bytes, content_hash: str) -> str:
        self.blobs[content_hash] = content
        return f"mock://{content_hash}"

    async def retrieve(self, content_hash: str) -> bytes:
        if content_hash in self.blobs:
            return self.blobs[content_hash]
        raise FileNotFoundError(f"Blob {content_hash} not found")

    async def read_blob(self, content_hash: str) -> bytes:
        return await self.retrieve(content_hash)

    async def blob_exists(self, content_hash: str) -> bool:
        return content_hash in self.blobs

    async def delete(self, content_hash: str) -> bool:
        if content_hash in self.blobs:
            del self.blobs[content_hash]
            return True
        return False


def _create_sample_pdf_bytes() -> bytes:
    """Generate minimal valid PDF bytes with PyMuPDF."""
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text(
        (50, 72),
        "Attention Is All You Need\n\n"
        "The dominant sequence models struggle with computational bottlenecks.\n"
        "In this work, we propose the Transformer architecture based on attention.\n"
        "A limitation of these models remains quadratic memory complexity.\n",
    )
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


@pytest.fixture
def test_user() -> UserModel:
    """Fixture providing standard mock user."""
    return UserModel(
        id=DEFAULT_DEV_USER_ID,
        email="developer@verischolar.org",
        full_name="VeriScholar Developer",
        hashed_password="hash",
        is_active=True,
    )


@pytest.fixture
def mock_storage() -> MockBlobStorage:
    """Fixture providing clean mock storage with sample PDF."""
    storage = MockBlobStorage()
    sample_bytes = _create_sample_pdf_bytes()
    storage.blobs["sample_summary_hash"] = sample_bytes
    return storage


@pytest.fixture
def db_session() -> InMemoryAsyncSummaryGenerateSession:
    """Fixture providing clean in-memory database session."""
    return InMemoryAsyncSummaryGenerateSession()


@pytest.fixture
def idempotency_adapter() -> InMemoryIdempotencyAdapter:
    """Fixture providing clean in-memory idempotency adapter."""
    return InMemoryIdempotencyAdapter()


@pytest.fixture
def sample_document(
    db_session: InMemoryAsyncSummaryGenerateSession,
) -> DocumentModel:
    """Fixture seeding completed document with chunks and existing summary in DB."""
    doc_id = uuid4()
    now = datetime.now(UTC)
    doc = DocumentModel(
        id=doc_id,
        user_id=DEFAULT_DEV_USER_ID,
        blob_id=None,
        filename="attention.pdf",
        title="Attention Is All You Need",
        content_hash="sample_summary_hash",
        file_size_bytes=1024,
        status="completed",
        stage="completed",
        progress=100,
        chunk_count=2,
        is_persistent=True,
        created_at=now,
        updated_at=now,
    )
    db_session.add(doc)

    chunk1 = DocumentChunkModel(
        id=uuid4(),
        document_id=doc_id,
        chunk_index=0,
        page_number=1,
        content="The dominant sequence models struggle with computational bottlenecks.",
        bounding_boxes=[[0.1, 0.1, 0.9, 0.2, 1]],
        token_count=12,
        created_at=now,
        updated_at=now,
    )
    chunk2 = DocumentChunkModel(
        id=uuid4(),
        document_id=doc_id,
        chunk_index=1,
        page_number=1,
        content="In this work, we propose the Transformer architecture based on attention.",
        bounding_boxes=[[0.1, 0.3, 0.9, 0.4, 1]],
        token_count=10,
        created_at=now,
        updated_at=now,
    )
    db_session.add(chunk1)
    db_session.add(chunk2)

    summary = DocumentSummaryModel(
        id=uuid4(),
        document_id=doc_id,
        problem_statement="Sequence models struggle with bottlenecks.",
        problem_citations=[[0.1, 0.1, 0.9, 0.2, 1]],
        contributions="We propose the Transformer.",
        contribution_citations=[[0.1, 0.3, 0.9, 0.4, 1]],
        limitations="Quadratic memory complexity remains a drawback.",
        limitation_citations=[[0.1, 0.5, 0.9, 0.6, 1]],
        total_tokens=42,
        latency_ms=5,
        created_at=now,
        updated_at=now,
    )
    db_session.add(summary)
    return doc


@pytest.fixture
def client(
    db_session: InMemoryAsyncSummaryGenerateSession,
    test_user: UserModel,
    mock_storage: MockBlobStorage,
    idempotency_adapter: InMemoryIdempotencyAdapter,
) -> Generator[AsyncClient, None, None]:
    """Provide AsyncClient wired with mocked session, user, storage, and idempotency."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session  # type: ignore[misc]

    async def override_get_current_user() -> UserModel:
        return test_user

    service = DocumentService(storage=mock_storage)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_document_service] = lambda: service
    app.dependency_overrides[get_idempotency_port] = lambda: idempotency_adapter

    transport = ASGITransport(app=app)
    async_client = AsyncClient(transport=transport, base_url="http://testserver")

    yield async_client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_generate_summary_default_cache_hit(
    client: AsyncClient,
    sample_document: DocumentModel,
) -> None:
    """Calling with force=False returns existing cached summary immediately."""
    response = await client.post(
        f"/api/v1/documents/{sample_document.id}/summary:generate",
        json={"force": False},
    )
    assert response.status_code == 200
    assert response.headers.get("X-Cache") == "Cache-Hit"
    data = response.json()
    assert data["success"] is True
    assert data["data"]["document_id"] == str(sample_document.id)
    assert data["data"]["problem_statement"]["text"] == "Sequence models struggle with bottlenecks."


@pytest.mark.asyncio
async def test_generate_summary_forced_resynthesis(
    client: AsyncClient,
    sample_document: DocumentModel,
    db_session: InMemoryAsyncSummaryGenerateSession,
) -> None:
    """Calling with force=True forces re-synthesis and updates DB record."""
    response = await client.post(
        f"/api/v1/documents/{sample_document.id}/summary:generate",
        json={"force": True},
    )
    assert response.status_code == 200
    assert response.headers.get("X-Cache") == "Generated"
    data = response.json()
    assert data["success"] is True
    assert data["data"]["document_id"] == str(sample_document.id)
    updated_record = db_session.summaries[sample_document.id]
    assert updated_record is not None
    assert updated_record.contributions != ""


@pytest.mark.asyncio
async def test_generate_summary_initial_synthesis(
    client: AsyncClient,
    db_session: InMemoryAsyncSummaryGenerateSession,
) -> None:
    """Calling when no summary exists yet synthesizes and stores new summary."""
    new_doc_id = uuid4()
    now = datetime.now(UTC)
    new_doc = DocumentModel(
        id=new_doc_id,
        user_id=DEFAULT_DEV_USER_ID,
        blob_id=None,
        filename="novel.pdf",
        title="Novel Paper",
        content_hash="sample_summary_hash",
        file_size_bytes=1024,
        status="completed",
        stage="completed",
        progress=100,
        chunk_count=0,
        is_persistent=True,
        created_at=now,
        updated_at=now,
    )
    db_session.add(new_doc)

    response = await client.post(
        f"/api/v1/documents/{new_doc_id}/summary:generate",
        json={"force": False},
    )
    assert response.status_code == 200
    assert response.headers.get("X-Cache") == "Generated"
    data = response.json()
    assert data["success"] is True
    assert data["data"]["document_id"] == str(new_doc_id)
    assert new_doc_id in db_session.summaries


@pytest.mark.asyncio
async def test_generate_summary_idempotency_hit(
    client: AsyncClient,
    sample_document: DocumentModel,
) -> None:
    """Same Idempotency-Key returns cached response with X-Cache: Idempotent-Hit."""
    idempotency_key = str(uuid4())
    headers = {"Idempotency-Key": idempotency_key}

    resp1 = await client.post(
        f"/api/v1/documents/{sample_document.id}/summary:generate",
        json={"force": True},
        headers=headers,
    )
    assert resp1.status_code == 200

    resp2 = await client.post(
        f"/api/v1/documents/{sample_document.id}/summary:generate",
        json={"force": True},
        headers=headers,
    )
    assert resp2.status_code == 200
    assert resp2.headers.get("X-Cache") == "Idempotent-Hit"
    assert resp2.json()["data"]["document_id"] == resp1.json()["data"]["document_id"]


@pytest.mark.asyncio
async def test_generate_summary_bounding_boxes_validity(
    client: AsyncClient,
    sample_document: DocumentModel,
) -> None:
    """Verify all returned bounding boxes conform to 5-element format."""
    response = await client.post(
        f"/api/v1/documents/{sample_document.id}/summary:generate",
        json={"force": True},
    )
    assert response.status_code == 200
    data = response.json()["data"]

    for key in ["problem_statement", "contributions", "limitations"]:
        boxes = data[key]["bounding_boxes"]
        assert isinstance(boxes, list)
        for box in boxes:
            assert len(box) == 5
            x0, y0, x1, y1, pg = box
            assert 0.0 <= x0 <= 1.0
            assert 0.0 <= y0 <= 1.0
            assert 0.0 <= x1 <= 1.0
            assert 0.0 <= y1 <= 1.0
            assert pg >= 1


@pytest.mark.asyncio
async def test_generate_summary_not_found(
    client: AsyncClient,
) -> None:
    """Non-existent document UUID returns 404 DOCUMENT_NOT_FOUND."""
    random_id = uuid4()
    response = await client.post(
        f"/api/v1/documents/{random_id}/summary:generate",
        json={"force": False},
    )
    assert response.status_code == 404
    payload = response.json()
    assert payload["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_generate_summary_multi_tenant_isolation(
    client: AsyncClient,
    db_session: InMemoryAsyncSummaryGenerateSession,
) -> None:
    """Document belonging to another user returns 404."""
    other_user_id = uuid4()
    doc_id = uuid4()
    now = datetime.now(UTC)
    other_doc = DocumentModel(
        id=doc_id,
        user_id=other_user_id,
        blob_id=None,
        filename="secret.pdf",
        status="completed",
        created_at=now,
        updated_at=now,
    )
    db_session.add(other_doc)

    response = await client.post(
        f"/api/v1/documents/{doc_id}/summary:generate",
        json={"force": False},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_generate_summary_conflict_processing(
    client: AsyncClient,
    db_session: InMemoryAsyncSummaryGenerateSession,
) -> None:
    """Document with status 'processing' returns 409 DOCUMENT_PROCESSING."""
    doc_id = uuid4()
    now = datetime.now(UTC)
    doc = DocumentModel(
        id=doc_id,
        user_id=DEFAULT_DEV_USER_ID,
        blob_id=None,
        filename="inflight.pdf",
        status="processing",
        created_at=now,
        updated_at=now,
    )
    db_session.add(doc)

    response = await client.post(
        f"/api/v1/documents/{doc_id}/summary:generate",
        json={"force": False},
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "DOCUMENT_PROCESSING"


@pytest.mark.asyncio
async def test_generate_summary_failed_status_unprocessable(
    client: AsyncClient,
    db_session: InMemoryAsyncSummaryGenerateSession,
) -> None:
    """Document with status 'failed' returns 422 DOCUMENT_FAILED."""
    doc_id = uuid4()
    now = datetime.now(UTC)
    doc = DocumentModel(
        id=doc_id,
        user_id=DEFAULT_DEV_USER_ID,
        blob_id=None,
        filename="failed.pdf",
        status="failed",
        created_at=now,
        updated_at=now,
    )
    db_session.add(doc)

    response = await client.post(
        f"/api/v1/documents/{doc_id}/summary:generate",
        json={"force": False},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "DOCUMENT_FAILED"


@pytest.mark.asyncio
async def test_generate_summary_invalid_uuid(
    client: AsyncClient,
) -> None:
    """Malformed UUID returns 422 Unprocessable Entity."""
    response = await client.post(
        "/api/v1/documents/not-a-valid-uuid/summary:generate",
        json={"force": False},
    )
    assert response.status_code == 422


# ==============================================================================
# 57. POST /api/v1/documents/{id}/summary:stream
# ==============================================================================
@pytest.mark.asyncio
async def test_stream_summary_success(
    client: AsyncClient,
    sample_document: DocumentModel,
) -> None:
    """Endpoint 57: Streams 3-point grounded summary via SSE with tokens and bounding boxes."""
    response = await client.post(
        f"/api/v1/documents/{sample_document.id}/summary:stream",
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    body = response.text
    assert "event: summary_start" in body
    assert "event: summary_chunk" in body
    assert "event: summary_box" in body
    assert "event: summary_end" in body
    assert "problem_statement" in body
    assert "contributions" in body
    assert "limitations" in body


@pytest.mark.asyncio
async def test_stream_summary_not_found(
    client: AsyncClient,
) -> None:
    """Endpoint 57: Returns 404 when document does not exist."""
    random_id = uuid4()
    response = await client.post(
        f"/api/v1/documents/{random_id}/summary:stream",
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_stream_summary_conflict_processing(
    client: AsyncClient,
    db_session: InMemoryAsyncSummaryGenerateSession,
) -> None:
    """Endpoint 57: Returns 409 DOCUMENT_PROCESSING when document is still processing."""
    doc_id = uuid4()
    now = datetime.now(UTC)
    doc = DocumentModel(
        id=doc_id,
        user_id=DEFAULT_DEV_USER_ID,
        blob_id=None,
        filename="inflight_stream.pdf",
        status="processing",
        chunk_count=0,
        created_at=now,
        updated_at=now,
    )
    db_session.add(doc)

    response = await client.post(
        f"/api/v1/documents/{doc_id}/summary:stream",
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "DOCUMENT_PROCESSING"


@pytest.mark.asyncio
async def test_stream_summary_failed_status(
    client: AsyncClient,
    db_session: InMemoryAsyncSummaryGenerateSession,
) -> None:
    """Endpoint 57: Returns 422 DOCUMENT_FAILED when document preprocessing failed."""
    doc_id = uuid4()
    now = datetime.now(UTC)
    doc = DocumentModel(
        id=doc_id,
        user_id=DEFAULT_DEV_USER_ID,
        blob_id=None,
        filename="failed_stream.pdf",
        status="failed",
        created_at=now,
        updated_at=now,
    )
    db_session.add(doc)

    response = await client.post(
        f"/api/v1/documents/{doc_id}/summary:stream",
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "DOCUMENT_FAILED"
