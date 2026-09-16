"""Automated integration tests for GET /api/v1/documents/{id}/chunks endpoint."""

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
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import DEFAULT_DEV_USER_ID, get_current_user, get_document_service
from api.services.document_service import DocumentService
from core.ports.storage import IBlobStoragePort
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class InMemoryAsyncChunkSession:
    """Deterministic in-memory database test double for document chunk tests."""

    def __init__(self) -> None:
        self.documents: dict[UUID, DocumentModel] = {}
        self.chunks: list[DocumentChunkModel] = []

    def add(self, obj: object) -> None:
        if isinstance(obj, DocumentModel):
            self.documents[obj.id] = obj
        elif isinstance(obj, DocumentChunkModel):
            self.chunks.append(obj)

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

        # Extract target_doc_id and target_page from params
        target_doc_id = None
        target_page = None
        for k, v in params.items():
            if k.startswith("document_id"):
                target_doc_id = v
            elif k.startswith("page_number"):
                target_page = v

        # 2. DocumentChunkModel count query
        if "count(*)" in statement_str.lower() and "document_chunks" in statement_str.lower():
            filtered = [
                c
                for c in self.chunks
                if (target_doc_id is None or c.document_id == target_doc_id)
                and (target_page is None or c.page_number == target_page)
            ]
            result_mock.scalar.return_value = len(filtered)
            return result_mock

        # 3. DocumentChunkModel items query
        if "FROM document_chunks" in statement_str:
            filtered = [
                c
                for c in self.chunks
                if (target_doc_id is None or c.document_id == target_doc_id)
                and (target_page is None or c.page_number == target_page)
            ]
            filtered.sort(key=lambda x: x.chunk_index)

            offset = getattr(statement, "_offset", None) or 0
            limit = getattr(statement, "_limit", None)

            if limit is not None:
                sliced = filtered[offset : offset + limit]
            else:
                sliced = filtered[offset:]

            result_mock.scalars.return_value.all.return_value = sliced
            return result_mock

        return result_mock


class InMemoryStorageDouble(IBlobStoragePort):
    """In-memory storage double serving synthetic PDF bytes."""

    def __init__(self) -> None:
        self.blobs: dict[str, bytes] = {}
        self.read_calls: int = 0

    def get_blob_path(self, content_hash: str) -> str:
        return f"storage/{content_hash}.pdf"

    async def save_blob(self, stream: AsyncIterator[bytes], content_hash: str) -> tuple[str, int]:
        chunks = []
        async for chunk in stream:
            chunks.append(chunk)
        data = b"".join(chunks)
        self.blobs[content_hash] = data
        return f"storage/{content_hash}.pdf", len(data)

    async def blob_exists(self, content_hash: str) -> bool:
        return content_hash in self.blobs

    async def read_blob(self, content_hash: str) -> bytes:
        self.read_calls += 1
        return self.blobs[content_hash]

    async def delete_blob(self, content_hash: str) -> bool:
        return self.blobs.pop(content_hash, None) is not None

    def stream_blob_range(
        self,
        content_hash: str,
        start_byte: int = 0,
        end_byte: int | None = None,
        chunk_size: int = 64 * 1024,
    ) -> AsyncIterator[bytes]:
        async def _generator():
            data = self.blobs[content_hash]
            end = len(data) if end_byte is None else end_byte + 1
            yield data[start_byte:end]

        return _generator()


def create_synthetic_pdf_for_chunks() -> bytes:
    """Create a synthetic multi-page PDF for chunk extraction testing."""
    doc = pymupdf.open()

    # Page 1: Abstract and Introduction
    p1 = doc.new_page(width=612, height=792)
    p1.insert_text((100, 100), "Deep Learning Verification of Scientific Literature", fontsize=16)
    p1.insert_text(
        (100, 140), "Abstract: We present an automated verification system.", fontsize=11
    )
    p1.insert_text(
        (100, 180),
        "Scientific literature is expanding at an unprecedented rate worldwide.\n"
        "Manual verification of claims and citations has become practically impossible.\n"
        "Automated tools are essential to maintain academic integrity and rigor.",
        fontsize=10,
    )

    # Page 2: Methodology
    p2 = doc.new_page(width=612, height=792)
    p2.insert_text((100, 100), "Methodology and Experimental Design", fontsize=14)
    p2.insert_text(
        (100, 140),
        "Our pipeline consists of layout analysis, text block extraction, and semantic chunking.\n"
        "Each chunk preserves physical bounding box coordinates for canvas visual grounding.\n"
        "Embeddings are computed using state-of-the-art transformer encoders.",
        fontsize=10,
    )

    # Page 3: Evaluation and Conclusion
    p3 = doc.new_page(width=612, height=792)
    p3.insert_text((100, 100), "Evaluation and Empirical Results", fontsize=14)
    p3.insert_text(
        (100, 140),
        "We evaluate our approach on 1,000 peer-reviewed papers from ArXiv.\n"
        "The proposed method achieves 98.5% precision in visual grounding alignment.\n"
        "In conclusion, deep reading with visual grounding improves scholar workflow.",
        fontsize=10,
    )

    return doc.tobytes()


@pytest.fixture
def test_user() -> UserModel:
    return UserModel(
        id=DEFAULT_DEV_USER_ID,
        email="tester@verischolar.org",
        full_name="Tester Scholar",
        hashed_password="hashed_pass",
        is_active=True,
    )


@pytest.fixture
def mock_storage() -> InMemoryStorageDouble:
    storage = InMemoryStorageDouble()
    pdf_bytes = create_synthetic_pdf_for_chunks()
    storage.blobs["chunkhash123"] = pdf_bytes
    return storage


@pytest.fixture
def mock_db() -> InMemoryAsyncChunkSession:
    db = InMemoryAsyncChunkSession()
    doc_id = UUID("11111111-1111-1111-1111-111111111111")
    user_id = DEFAULT_DEV_USER_ID
    doc = DocumentModel(
        id=doc_id,
        user_id=user_id,
        filename="verischolar_deep_reading.pdf",
        content_hash="chunkhash123",
        file_size_bytes=2048,
        status="completed",
        stage="completed",
        progress=100,
        chunk_count=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(doc)
    return db


@pytest.fixture
def client(
    mock_storage: InMemoryStorageDouble,
    mock_db: InMemoryAsyncChunkSession,
    test_user: UserModel,
) -> Generator[AsyncClient, None, None]:
    service = DocumentService(storage=mock_storage)

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield mock_db  # type: ignore[misc]

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_document_service] = lambda: service

    transport = ASGITransport(app=app)
    yield AsyncClient(transport=transport, base_url="http://testserver")

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_document_chunks_initial_extraction(client: AsyncClient) -> None:
    doc_id = "11111111-1111-1111-1111-111111111111"
    response = await client.get(f"/api/v1/documents/{doc_id}/chunks")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert "data" in payload
    assert "meta" in payload
    assert "links" in payload

    chunks = payload["data"]
    assert len(chunks) > 0
    assert payload["meta"]["total"] == len(chunks)
    assert payload["meta"]["page"] == 1
    assert payload["meta"]["per_page"] == 50

    # Validate RFC 8288 links
    links = payload["links"]
    assert links["self"] == f"/api/v1/documents/{doc_id}/chunks?page=1&per_page=50"
    assert links["first"] == f"/api/v1/documents/{doc_id}/chunks?page=1&per_page=50"

    # Validate chunk item structure
    first_chunk = chunks[0]
    assert "id" in first_chunk
    assert first_chunk["document_id"] == doc_id
    assert first_chunk["chunk_index"] == 0
    assert first_chunk["page_number"] >= 1
    assert first_chunk["content"] is not None
    assert len(first_chunk["content"]) > 0
    assert first_chunk["token_count"] > 0
    assert isinstance(first_chunk["bounding_boxes"], list)
    if first_chunk["bounding_boxes"]:
        box = first_chunk["bounding_boxes"][0]
        assert len(box) == 5
        x0, y0, x1, y1, page_num = box
        assert x0 <= x1
        assert y0 <= y1
        assert page_num >= 1


@pytest.mark.asyncio
async def test_get_document_chunks_include_content_false(client: AsyncClient) -> None:
    doc_id = "11111111-1111-1111-1111-111111111111"
    response = await client.get(f"/api/v1/documents/{doc_id}/chunks?include_content=false")

    assert response.status_code == 200
    payload = response.json()
    chunks = payload["data"]
    assert len(chunks) > 0

    # Content must be null/None when include_content=false
    for chunk in chunks:
        assert chunk["content"] is None
        assert chunk["token_count"] > 0
        assert "bounding_boxes" in chunk

    assert "include_content=false" in payload["links"]["self"]


@pytest.mark.asyncio
async def test_get_document_chunks_page_number_filter(client: AsyncClient) -> None:
    doc_id = "11111111-1111-1111-1111-111111111111"
    # First trigger extraction
    await client.get(f"/api/v1/documents/{doc_id}/chunks")

    # Filter page 1
    response = await client.get(f"/api/v1/documents/{doc_id}/chunks?page_number=1")
    assert response.status_code == 200
    payload = response.json()
    chunks = payload["data"]
    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk["page_number"] == 1

    assert "page_number=1" in payload["links"]["self"]


@pytest.mark.asyncio
async def test_get_document_chunks_pagination(client: AsyncClient) -> None:
    doc_id = "11111111-1111-1111-1111-111111111111"
    # First trigger extraction
    await client.get(f"/api/v1/documents/{doc_id}/chunks")

    # Request 1 item per page
    response = await client.get(f"/api/v1/documents/{doc_id}/chunks?page=1&per_page=1")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["data"]) == 1
    assert payload["meta"]["per_page"] == 1
    assert payload["meta"]["total_pages"] >= 2
    assert payload["links"]["next"] is not None


@pytest.mark.asyncio
async def test_get_document_chunks_not_found(client: AsyncClient) -> None:
    non_existent = str(uuid4())
    response = await client.get(f"/api/v1/documents/{non_existent}/chunks")
    assert response.status_code == 404
    payload = response.json()
    assert payload["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_document_chunks_tenant_isolation(
    client: AsyncClient, mock_db: InMemoryAsyncChunkSession
) -> None:
    other_user_id = uuid4()
    other_doc_id = uuid4()
    other_doc = DocumentModel(
        id=other_doc_id,
        user_id=other_user_id,
        filename="other.pdf",
        content_hash="chunkhash123",
        file_size_bytes=1000,
        status="completed",
        stage="completed",
        progress=100,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_db.add(other_doc)

    response = await client.get(f"/api/v1/documents/{other_doc_id}/chunks")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_document_chunks_validation_errors(client: AsyncClient) -> None:
    doc_id = "11111111-1111-1111-1111-111111111111"

    # Invalid page (< 1)
    res1 = await client.get(f"/api/v1/documents/{doc_id}/chunks?page=0")
    assert res1.status_code == 422

    # Invalid per_page (> 200)
    res2 = await client.get(f"/api/v1/documents/{doc_id}/chunks?per_page=500")
    assert res2.status_code == 422

    # Invalid UUID
    res3 = await client.get("/api/v1/documents/not-a-valid-uuid/chunks")
    assert res3.status_code == 422
