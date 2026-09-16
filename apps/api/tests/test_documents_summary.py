"""Automated integration tests for GET /api/v1/documents/{id}/summary endpoint."""

from collections.abc import AsyncGenerator, AsyncIterator, Generator
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
from api.deps import DEFAULT_DEV_USER_ID, get_current_user, get_document_service
from api.services.document_service import DocumentService
from core.ports.storage import IBlobStoragePort
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class InMemoryAsyncSummarySession:
    """Deterministic in-memory database test double for document summary tests."""

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

    async def delete(self, obj: object) -> None:
        pass

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
                if k.startswith("id"):
                    target_id = v
                elif k.startswith("user_id"):
                    target_user_id = v

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

        # Extract target_doc_id
        target_doc_id = None
        for k, v in params.items():
            if k.startswith("document_id"):
                target_doc_id = v

        # 2. DocumentSummaryModel lookup
        if "FROM document_summaries" in statement_str:
            summary = self.summaries.get(target_doc_id)
            result_mock.scalar_one_or_none.return_value = summary
            return result_mock

        # 3. DocumentChunkModel queries
        if "FROM document_chunks" in statement_str:
            filtered = [
                c for c in self.chunks if (target_doc_id is None or c.document_id == target_doc_id)
            ]
            result_mock.scalars.return_value.all.return_value = filtered
            result_mock.scalar.return_value = len(filtered)
            return result_mock

        result_mock.scalar_one_or_none.return_value = None
        result_mock.scalars.return_value.all.return_value = []
        result_mock.scalar.return_value = 0
        return result_mock


class MockStoragePort(IBlobStoragePort):
    """Hermetic in-memory storage port double for tests."""

    def __init__(self) -> None:
        self.blobs: dict[str, bytes] = {}

    async def save_blob(
        self,
        stream: AsyncIterator[bytes],
        content_hash: str,
    ) -> tuple[str, int]:
        chunks = [chunk async for chunk in stream]
        data = b"".join(chunks)
        self.blobs[content_hash] = data
        return f"storage/{content_hash}.pdf", len(data)

    async def read_blob(self, content_hash: str) -> bytes:
        if content_hash not in self.blobs:
            raise FileNotFoundError(f"Blob {content_hash} not found")
        return self.blobs[content_hash]

    async def blob_exists(self, content_hash: str) -> bool:
        return content_hash in self.blobs

    async def delete_blob(self, content_hash: str) -> bool:
        if content_hash in self.blobs:
            del self.blobs[content_hash]
            return True
        return False


def _create_dummy_pdf_bytes() -> bytes:
    """Create a minimal valid 2-page PDF document for test fixtures."""
    doc = pymupdf.open()
    page1 = doc.new_page()
    page1.insert_text(
        (50, 72),
        (
            "Attention Is All You Need\n"
            "Abstract: Recurrent models struggle with sequential computation bottlenecks.\n"
            "We propose the Transformer, a novel architecture based entirely on self-attention."
        ),
    )
    page2 = doc.new_page()
    page2.insert_text(
        (50, 72),
        (
            "Limitations and Conclusion:\n"
            "Computational complexity remains O(N^2) for long context sequences.\n"
            "Future work will address sparse attention approximations."
        ),
    )
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


@pytest.fixture
def mock_db() -> InMemoryAsyncSummarySession:
    return InMemoryAsyncSummarySession()


@pytest.fixture
def mock_storage() -> MockStoragePort:
    return MockStoragePort()


@pytest.fixture
def test_user() -> UserModel:
    return UserModel(
        id=DEFAULT_DEV_USER_ID,
        email="developer@verischolar.org",
        is_active=True,
    )


@pytest.fixture
def other_user() -> UserModel:
    return UserModel(
        id=uuid4(),
        email="other@verischolar.org",
        is_active=True,
    )


@pytest.fixture
def client(
    mock_db: InMemoryAsyncSummarySession,
    mock_storage: MockStoragePort,
    test_user: UserModel,
) -> Generator[AsyncClient, None, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield mock_db  # type: ignore[misc]

    async def override_get_current_user() -> UserModel:
        return test_user

    service = DocumentService(storage=mock_storage)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_document_service] = lambda: service

    transport = ASGITransport(app=app)
    async_client = AsyncClient(transport=transport, base_url="http://testserver")

    yield async_client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_document_summary_cached_success(
    client: AsyncClient,
    mock_db: InMemoryAsyncSummarySession,
    test_user: UserModel,
) -> None:
    """1. Test successful retrieval of an existing cached summary from database."""
    now = datetime.now(UTC)
    doc_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=test_user.id,
        blob_id=None,
        filename="attention.pdf",
        title="Attention Is All You Need",
        content_hash="abc123hash",
        file_size_bytes=1024,
        status="completed",
        stage="completed",
        progress=100,
        chunk_count=2,
        is_persistent=True,
        created_at=now,
        updated_at=now,
    )
    mock_db.add(doc)

    summary = DocumentSummaryModel(
        id=uuid4(),
        document_id=doc_id,
        problem_statement=(
            "Recurrent neural networks suffer from sequential computation bottlenecks."
        ),
        problem_citations=[[0.1, 0.2, 0.9, 0.25, 1]],
        contributions="We propose the Transformer based entirely on attention mechanisms.",
        contribution_citations=[[0.1, 0.3, 0.9, 0.35, 1]],
        limitations="Quadratic computational complexity O(N^2) with sequence length.",
        limitation_citations=[[0.1, 0.5, 0.9, 0.55, 2]],
        total_tokens=180,
        latency_ms=12,
        created_at=now,
        updated_at=now,
    )
    mock_db.add(summary)

    resp = await client.get(f"/api/v1/documents/{doc_id}/summary")
    assert resp.status_code == 200
    data = resp.json()

    assert data["success"] is True
    summary_data = data["data"]
    assert summary_data["document_id"] == str(doc_id)
    assert "Recurrent neural networks" in summary_data["problem_statement"]["text"]
    assert summary_data["problem_statement"]["bounding_boxes"] == [[0.1, 0.2, 0.9, 0.25, 1]]
    assert "Transformer" in summary_data["contributions"]["text"]
    assert summary_data["contributions"]["bounding_boxes"] == [[0.1, 0.3, 0.9, 0.35, 1]]
    assert "Quadratic" in summary_data["limitations"]["text"]
    assert summary_data["limitations"]["bounding_boxes"] == [[0.1, 0.5, 0.9, 0.55, 2]]
    assert summary_data["total_tokens"] == 180


@pytest.mark.asyncio
async def test_get_document_summary_on_demand_synthesis_success(
    client: AsyncClient,
    mock_db: InMemoryAsyncSummarySession,
    mock_storage: MockStoragePort,
    test_user: UserModel,
) -> None:
    """2. Test automatic on-demand synthesis when summary is missing in database."""
    pdf_bytes = _create_dummy_pdf_bytes()
    content_hash = "dummy_attention_pdf_hash"
    mock_storage.blobs[content_hash] = pdf_bytes

    now = datetime.now(UTC)
    doc_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=test_user.id,
        blob_id=None,
        filename="Attention.pdf",
        title="Attention Is All You Need",
        content_hash=content_hash,
        file_size_bytes=len(pdf_bytes),
        status="completed",
        stage="completed",
        progress=100,
        chunk_count=0,
        is_persistent=True,
        created_at=now,
        updated_at=now,
    )
    mock_db.add(doc)

    resp = await client.get(f"/api/v1/documents/{doc_id}/summary")
    assert resp.status_code == 200
    data = resp.json()

    assert data["success"] is True
    summary_data = data["data"]
    assert summary_data["document_id"] == str(doc_id)
    assert len(summary_data["problem_statement"]["text"]) > 10
    assert len(summary_data["contributions"]["text"]) > 10
    assert len(summary_data["limitations"]["text"]) > 10
    assert summary_data["total_tokens"] > 0
    # Verify persisted in database
    assert doc_id in mock_db.summaries


@pytest.mark.asyncio
async def test_get_document_summary_bounding_boxes_validity(
    client: AsyncClient,
    mock_db: InMemoryAsyncSummarySession,
    mock_storage: MockStoragePort,
    test_user: UserModel,
) -> None:
    """3. Verify all spatial bounding boxes follow 5-tuple format and valid coordinates."""
    pdf_bytes = _create_dummy_pdf_bytes()
    content_hash = "validity_hash"
    mock_storage.blobs[content_hash] = pdf_bytes

    now = datetime.now(UTC)
    doc_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=test_user.id,
        blob_id=None,
        filename="Attention.pdf",
        title="Attention Is All You Need",
        content_hash=content_hash,
        file_size_bytes=len(pdf_bytes),
        status="completed",
        stage="completed",
        progress=100,
        chunk_count=0,
        is_persistent=True,
        created_at=now,
        updated_at=now,
    )
    mock_db.add(doc)

    resp = await client.get(f"/api/v1/documents/{doc_id}/summary")
    assert resp.status_code == 200
    summary_data = resp.json()["data"]

    for point_name in ["problem_statement", "contributions", "limitations"]:
        boxes = summary_data[point_name]["bounding_boxes"]
        assert isinstance(boxes, list)
        for box in boxes:
            assert len(box) == 5
            x0, y0, x1, y1, page = box
            assert 0.0 <= x0 <= 1.0
            assert 0.0 <= y0 <= 1.0
            assert 0.0 <= x1 <= 1.0
            assert 0.0 <= y1 <= 1.0
            assert x0 < x1
            assert y0 < y1
            assert page >= 1


@pytest.mark.asyncio
async def test_get_document_summary_not_found(
    client: AsyncClient,
) -> None:
    """4. Test 404 DOCUMENT_NOT_FOUND when querying a non-existent document ID."""
    random_id = uuid4()
    resp = await client.get(f"/api/v1/documents/{random_id}/summary")
    assert resp.status_code == 404
    payload = resp.json()
    err = payload["error"]
    assert err["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_document_summary_multi_tenant_isolation(
    client: AsyncClient,
    mock_db: InMemoryAsyncSummarySession,
    other_user: UserModel,
) -> None:
    """5. Test 404 when user attempts to access another user's document summary."""
    now = datetime.now(UTC)
    doc_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=other_user.id,  # Owned by other user
        blob_id=None,
        filename="private_doc.pdf",
        content_hash="private_hash",
        file_size_bytes=1024,
        status="completed",
        is_persistent=True,
        created_at=now,
        updated_at=now,
    )
    mock_db.add(doc)

    resp = await client.get(f"/api/v1/documents/{doc_id}/summary")
    assert resp.status_code == 404
    payload = resp.json()
    err = payload["error"]
    assert err["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_document_summary_conflict_processing(
    client: AsyncClient,
    mock_db: InMemoryAsyncSummarySession,
    test_user: UserModel,
) -> None:
    """6. Test 409 DOCUMENT_PROCESSING when document is still undergoing background ingestion."""
    now = datetime.now(UTC)
    doc_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=test_user.id,
        blob_id=None,
        filename="processing_doc.pdf",
        content_hash="processing_hash",
        file_size_bytes=1024,
        status="processing",
        stage="ocr",
        progress=45,
        is_persistent=True,
        created_at=now,
        updated_at=now,
    )
    mock_db.add(doc)

    resp = await client.get(f"/api/v1/documents/{doc_id}/summary")
    assert resp.status_code == 409
    payload = resp.json()
    err = payload["error"]
    assert err["code"] == "DOCUMENT_PROCESSING"


@pytest.mark.asyncio
async def test_get_document_summary_unprocessable_failed(
    client: AsyncClient,
    mock_db: InMemoryAsyncSummarySession,
    test_user: UserModel,
) -> None:
    """7. Test 422 DOCUMENT_FAILED when document ingestion failed."""
    now = datetime.now(UTC)
    doc_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=test_user.id,
        blob_id=None,
        filename="corrupt.pdf",
        content_hash="failed_hash",
        file_size_bytes=1024,
        status="failed",
        stage="validation",
        progress=0,
        error_message="PDF corrupted magic bytes",
        is_persistent=True,
        created_at=now,
        updated_at=now,
    )
    mock_db.add(doc)

    resp = await client.get(f"/api/v1/documents/{doc_id}/summary")
    assert resp.status_code == 422
    payload = resp.json()
    err = payload["error"]
    assert err["code"] == "DOCUMENT_FAILED"


@pytest.mark.asyncio
async def test_get_document_summary_invalid_uuid(
    client: AsyncClient,
) -> None:
    """8. Test 422 Unprocessable Entity when path parameter is an invalid UUID."""
    resp = await client.get("/api/v1/documents/invalid-uuid-string/summary")
    assert resp.status_code == 422
