"""Automated integration tests for GET /api/v1/documents/{id}/chunks/{chunk_id} endpoint."""

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


class InMemoryAsyncChunkDetailSession:
    """Deterministic in-memory database test double for document chunk detail tests."""

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

        # Extract target_doc_id, target_chunk_id, target_chunk_index from params
        target_doc_id = None
        target_chunk_id = None
        target_chunk_index = None

        for k, v in params.items():
            if k.startswith("document_id"):
                target_doc_id = v
            elif k.startswith("id"):
                target_chunk_id = v
            elif k.startswith("chunk_index"):
                target_chunk_index = v

        # 2. DocumentChunkModel count query
        if "count(*)" in statement_str.lower() and "document_chunks" in statement_str.lower():
            filtered = [
                c for c in self.chunks if (target_doc_id is None or c.document_id == target_doc_id)
            ]
            result_mock.scalar.return_value = len(filtered)
            return result_mock

        # 3. DocumentChunkModel queries
        if "FROM document_chunks" in statement_str:
            # Check if querying single chunk by id
            if target_chunk_id is not None:
                matched_chunk = None
                for c in self.chunks:
                    if (
                        target_doc_id is None or c.document_id == target_doc_id
                    ) and c.id == target_chunk_id:
                        matched_chunk = c
                        break
                result_mock.scalar_one_or_none.return_value = matched_chunk
                return result_mock

            # Check if querying adjacent chunk by chunk_index
            if target_chunk_index is not None:
                matched_id = None
                for c in self.chunks:
                    if (
                        target_doc_id is None or c.document_id == target_doc_id
                    ) and c.chunk_index == target_chunk_index:
                        matched_id = c.id
                        break
                result_mock.scalar_one_or_none.return_value = matched_id
                return result_mock

            # General query
            filtered = [
                c for c in self.chunks if (target_doc_id is None or c.document_id == target_doc_id)
            ]
            filtered.sort(key=lambda x: x.chunk_index)
            result_mock.scalars.return_value.all.return_value = filtered
            result_mock.scalar_one_or_none.return_value = filtered[0] if filtered else None
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


def _create_synthetic_two_page_pdf() -> bytes:
    """Create a deterministic synthetic PDF with academic headings and body text."""
    doc = pymupdf.open()
    page1 = doc.new_page(width=595, height=842)
    page1.insert_text(
        (50, 72),
        "Attention Is All You Need\nAshish Vaswani, Noam Shazeer\nGoogle Brain",
        fontsize=14,
    )
    page1.insert_text(
        (50, 140),
        "Abstract\nThe dominant sequence transduction models are based on complex recurrent "
        "or convolutional neural networks. We propose the Transformer architecture.",
        fontsize=10,
    )
    page1.insert_text(
        (50, 260),
        "1 Introduction\nRecurrent neural networks, long short-term memory and gated recurrent "
        "neural networks have been firmly established as state of the art approaches.",
        fontsize=10,
    )

    page2 = doc.new_page(width=595, height=842)
    page2.insert_text(
        (50, 72),
        "2 Model Architecture\nThe Transformer follows an overall architecture using stacked "
        "self-attention and point-wise, fully connected layers for both the encoder and decoder.",
        fontsize=10,
    )
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@pytest.fixture
def fake_db_session() -> InMemoryAsyncChunkDetailSession:
    return InMemoryAsyncChunkDetailSession()


@pytest.fixture
def fake_storage() -> InMemoryStorageDouble:
    return InMemoryStorageDouble()


@pytest.fixture
def document_service(fake_storage: InMemoryStorageDouble) -> DocumentService:
    return DocumentService(storage=fake_storage)


@pytest.fixture
def test_user() -> UserModel:
    return UserModel(
        id=DEFAULT_DEV_USER_ID,
        email="test@verischolar.org",
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
    fake_db_session: InMemoryAsyncChunkDetailSession,
    document_service: DocumentService,
    test_user: UserModel,
) -> Generator[AsyncClient, None, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield fake_db_session  # type: ignore[misc]

    def override_get_document_service() -> DocumentService:
        return document_service

    def override_get_current_user() -> UserModel:
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_document_service] = override_get_document_service
    app.dependency_overrides[get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)
    yield AsyncClient(transport=transport, base_url="http://testserver")

    app.dependency_overrides.clear()


@pytest.fixture
def seeded_document_with_chunks(
    fake_db_session: InMemoryAsyncChunkDetailSession,
    fake_storage: InMemoryStorageDouble,
    test_user: UserModel,
) -> tuple[DocumentModel, list[DocumentChunkModel]]:
    """Seed a test document with 3 sequential chunks."""
    doc_id = uuid4()
    pdf_bytes = _create_synthetic_two_page_pdf()
    fake_storage.blobs["seed_hash"] = pdf_bytes

    doc = DocumentModel(
        id=doc_id,
        user_id=test_user.id,
        filename="attention.pdf",
        file_size_bytes=len(pdf_bytes),
        content_hash="seed_hash",
        status="completed",
        stage="completed",
        progress=100,
        chunk_count=3,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    fake_db_session.add(doc)

    chunks = [
        DocumentChunkModel(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=0,
            page_number=1,
            content="Title and Abstract chunk",
            bounding_boxes=[[0.1, 0.1, 0.9, 0.25, 1]],
            token_count=30,
            embedding=[0.05] * 1536,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        DocumentChunkModel(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=1,
            page_number=1,
            content="Introduction section chunk",
            bounding_boxes=[[0.1, 0.3, 0.9, 0.5, 1]],
            token_count=45,
            embedding=[0.02] * 1536,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        DocumentChunkModel(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=2,
            page_number=2,
            content="Model Architecture section chunk",
            bounding_boxes=[[0.1, 0.1, 0.9, 0.4, 2]],
            token_count=50,
            embedding=[0.08] * 1536,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
    ]
    fake_db_session.add_all(chunks)
    return doc, chunks


@pytest.mark.asyncio
async def test_get_chunk_detail_success(
    client: AsyncClient,
    seeded_document_with_chunks: tuple[DocumentModel, list[DocumentChunkModel]],
) -> None:
    """Test retrieving middle chunk (index 1) with complete navigation links."""
    doc, chunks = seeded_document_with_chunks
    middle_chunk = chunks[1]

    response = await client.get(f"/api/v1/documents/{doc.id}/chunks/{middle_chunk.id}")
    assert response.status_code == 200

    payload = response.json()
    assert payload["success"] is True

    data = payload["data"]
    assert data["id"] == str(middle_chunk.id)
    assert data["document_id"] == str(doc.id)
    assert data["chunk_index"] == 1
    assert data["page_number"] == 1
    assert data["content"] == "Introduction section chunk"
    assert data["token_count"] == 45
    assert data["embedding_dimension"] == 1536
    assert len(data["bounding_boxes"]) == 1
    assert data["bounding_boxes"][0] == [0.1, 0.3, 0.9, 0.5, 1]

    links = data["links"]
    assert links["self"] == f"/api/v1/documents/{doc.id}/chunks/{middle_chunk.id}"
    assert links["document"] == f"/api/v1/documents/{doc.id}"
    assert links["chunks"] == f"/api/v1/documents/{doc.id}/chunks"
    assert links["prev_chunk"] == f"/api/v1/documents/{doc.id}/chunks/{chunks[0].id}"
    assert links["next_chunk"] == f"/api/v1/documents/{doc.id}/chunks/{chunks[2].id}"


@pytest.mark.asyncio
async def test_get_first_chunk_has_no_prev_chunk(
    client: AsyncClient,
    seeded_document_with_chunks: tuple[DocumentModel, list[DocumentChunkModel]],
) -> None:
    """Test retrieving first chunk (index 0) has prev_chunk=None."""
    doc, chunks = seeded_document_with_chunks
    first_chunk = chunks[0]

    response = await client.get(f"/api/v1/documents/{doc.id}/chunks/{first_chunk.id}")
    assert response.status_code == 200

    payload = response.json()
    data = payload["data"]
    assert data["chunk_index"] == 0
    assert data["links"]["prev_chunk"] is None
    assert data["links"]["next_chunk"] == f"/api/v1/documents/{doc.id}/chunks/{chunks[1].id}"


@pytest.mark.asyncio
async def test_get_last_chunk_has_no_next_chunk(
    client: AsyncClient,
    seeded_document_with_chunks: tuple[DocumentModel, list[DocumentChunkModel]],
) -> None:
    """Test retrieving last chunk (index 2) has next_chunk=None."""
    doc, chunks = seeded_document_with_chunks
    last_chunk = chunks[2]

    response = await client.get(f"/api/v1/documents/{doc.id}/chunks/{last_chunk.id}")
    assert response.status_code == 200

    payload = response.json()
    data = payload["data"]
    assert data["chunk_index"] == 2
    assert data["links"]["prev_chunk"] == f"/api/v1/documents/{doc.id}/chunks/{chunks[1].id}"
    assert data["links"]["next_chunk"] is None


@pytest.mark.asyncio
async def test_get_chunk_detail_nonexistent_chunk_returns_404(
    client: AsyncClient,
    seeded_document_with_chunks: tuple[DocumentModel, list[DocumentChunkModel]],
) -> None:
    """Test querying nonexistent chunk ID returns 404 CHUNK_NOT_FOUND."""
    doc, _ = seeded_document_with_chunks
    random_chunk_id = uuid4()

    response = await client.get(f"/api/v1/documents/{doc.id}/chunks/{random_chunk_id}")
    assert response.status_code == 404

    payload = response.json()
    err = payload["error"]
    assert err["code"] == "CHUNK_NOT_FOUND"
    assert "not found for document" in err["message"]
    assert err["field"] == "chunk_id"


@pytest.mark.asyncio
async def test_get_chunk_detail_nonexistent_document_returns_404(
    client: AsyncClient,
) -> None:
    """Test querying nonexistent document returns 404 DOCUMENT_NOT_FOUND."""
    random_doc_id = uuid4()
    random_chunk_id = uuid4()

    response = await client.get(f"/api/v1/documents/{random_doc_id}/chunks/{random_chunk_id}")
    assert response.status_code == 404

    payload = response.json()
    err = payload["error"]
    assert err["code"] == "DOCUMENT_NOT_FOUND"
    assert err["field"] == "id"


@pytest.mark.asyncio
async def test_get_chunk_detail_unauthorized_user_returns_404(
    client: AsyncClient,
    fake_db_session: InMemoryAsyncChunkDetailSession,
    other_user: UserModel,
) -> None:
    """Multi-tenant isolation: user cannot access chunks of another user's document."""
    foreign_doc = DocumentModel(
        id=uuid4(),
        user_id=other_user.id,
        filename="foreign.pdf",
        status="completed",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    foreign_chunk = DocumentChunkModel(
        id=uuid4(),
        document_id=foreign_doc.id,
        chunk_index=0,
        page_number=1,
        content="Confidential foreign text",
        bounding_boxes=[],
        token_count=10,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    fake_db_session.add(foreign_doc)
    fake_db_session.add(foreign_chunk)

    response = await client.get(f"/api/v1/documents/{foreign_doc.id}/chunks/{foreign_chunk.id}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_chunk_detail_on_demand_extraction(
    client: AsyncClient,
    fake_db_session: InMemoryAsyncChunkDetailSession,
    fake_storage: InMemoryStorageDouble,
    test_user: UserModel,
) -> None:
    """If document has 0 chunks initially, endpoint triggers on-demand extraction."""
    pdf_bytes = _create_synthetic_two_page_pdf()
    content_hash = "ondemand_hash"
    fake_storage.blobs[content_hash] = pdf_bytes

    doc = DocumentModel(
        id=uuid4(),
        user_id=test_user.id,
        filename="fresh.pdf",
        file_size_bytes=len(pdf_bytes),
        content_hash=content_hash,
        status="completed",
        stage="completed",
        progress=100,
        chunk_count=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    fake_db_session.add(doc)

    # First request on-demand extracts chunks into DB
    response_list = await client.get(f"/api/v1/documents/{doc.id}/chunks")
    assert response_list.status_code == 200
    first_chunk_id = response_list.json()["data"][0]["id"]

    # Now retrieve detail of that chunk
    response_detail = await client.get(f"/api/v1/documents/{doc.id}/chunks/{first_chunk_id}")
    assert response_detail.status_code == 200
    assert response_detail.json()["data"]["id"] == first_chunk_id
    assert response_detail.json()["data"]["content"] is not None


@pytest.mark.asyncio
async def test_get_chunk_detail_invalid_uuid_returns_422(
    client: AsyncClient,
) -> None:
    """Test passing invalid UUID strings returns 422 Unprocessable Entity."""
    response = await client.get("/api/v1/documents/not-a-uuid/chunks/not-a-uuid")
    assert response.status_code == 422
