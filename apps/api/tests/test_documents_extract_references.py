"""Automated integration tests for POST /api/v1/documents/{id}:extract-references endpoint."""

from collections.abc import AsyncGenerator, AsyncIterator, Generator
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pymupdf
import pytest
from api import app
from api.db.models.document import DocumentModel
from api.db.models.reference import ReferenceItemModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import DEFAULT_DEV_USER_ID, get_current_user, get_document_service
from api.services.document_service import DocumentService
from core.ports.storage import IBlobStoragePort
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class InMemoryAsyncReferenceSession:
    """Deterministic in-memory database test double for reference extraction tests."""

    def __init__(self) -> None:
        self.documents: dict[UUID, DocumentModel] = {}
        self.references: dict[UUID, list[ReferenceItemModel]] = {}

    def add(self, obj: object) -> None:
        if isinstance(obj, DocumentModel):
            self.documents[obj.id] = obj
        elif isinstance(obj, ReferenceItemModel):
            if obj.document_id not in self.references:
                self.references[obj.document_id] = []
            self.references[obj.document_id].append(obj)

    async def flush(self) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def delete(self, obj: object) -> None:
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
        target_doc_id = params.get("document_id_1") or params.get("document_id")

        if "DELETE FROM reference_items" in stmt_str:
            if target_doc_id in self.references:
                self.references[target_doc_id] = []
            return result_mock

        if "FROM reference_items" in stmt_str:
            items = self.references.get(target_doc_id, [])
            result_mock.scalars.return_value.all.return_value = list(items)
            return result_mock

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


class InMemoryStorageDouble(IBlobStoragePort):
    """In-memory storage double serving PDF bytes."""

    def __init__(self) -> None:
        self.blobs: dict[str, bytes] = {}
        self.read_calls: int = 0

    async def save_blob(self, content_hash: str, stream: AsyncIterator[bytes]) -> int:
        chunks = []
        async for chunk in stream:
            chunks.append(chunk)
        data = b"".join(chunks)
        self.blobs[content_hash] = data
        return len(data)

    async def blob_exists(self, content_hash: str) -> bool:
        return content_hash in self.blobs

    async def read_blob(self, content_hash: str) -> bytes:
        self.read_calls += 1
        return self.blobs[content_hash]

    async def delete_blob(self, content_hash: str) -> bool:
        return self.blobs.pop(content_hash, None) is not None

    async def stream_blob_range(
        self, content_hash: str, start_byte: int = 0, end_byte: int | None = None
    ) -> AsyncIterator[bytes]:
        data = self.blobs[content_hash]
        end = len(data) if end_byte is None else end_byte + 1
        yield data[start_byte:end]


def create_synthetic_pdf_with_references() -> bytes:
    """Generate a clean synthetic PDF with a References section in memory."""
    doc = pymupdf.open()
    p1 = doc.new_page()
    p1.insert_text((50, 100), "Title: Transformer Architectures\nAbstract: State of the art NLP.")
    p2 = doc.new_page()
    ref_text = (
        "References\n"
        "[1] Jimmy Lei Ba, Jamie Ryan Kiros, and Geoffrey E Hinton. Layer normalization. "
        "arXiv preprint arXiv:1607.06450, 2016.\n"
        "[2] Dzmitry Bahdanau, Kyunghyun Cho, and Yoshua Bengio. Neural machine translation "
        "by jointly learning to align and translate. arXiv:1409.0473, 2014.\n"
        "[3] Ashish Vaswani et al. Attention is all you need. In NeurIPS, 2017. "
        "doi:10.5555/3295222.3295349\n"
    )
    p2.insert_textbox(pymupdf.Rect(50, 50, 550, 750), ref_text)
    return doc.tobytes()


def create_synthetic_pdf_without_references() -> bytes:
    """Generate a clean synthetic PDF without any References section."""
    doc = pymupdf.open()
    p1 = doc.new_page()
    p1.insert_text((50, 100), "Title: Document Without References\nJust body content.")
    return doc.tobytes()


@pytest.fixture
def fake_ref_db() -> InMemoryAsyncReferenceSession:
    """Fixture providing in-memory database double."""
    return InMemoryAsyncReferenceSession()


@pytest.fixture
def fake_storage() -> InMemoryStorageDouble:
    """Fixture providing in-memory blob storage."""
    return InMemoryStorageDouble()


@pytest.fixture
def sample_pdf_document(
    fake_ref_db: InMemoryAsyncReferenceSession,
    fake_storage: InMemoryStorageDouble,
) -> DocumentModel:
    """Register a sample document with physical PDF containing references."""
    pdf_bytes = create_synthetic_pdf_with_references()
    content_hash = "hash_with_refs_1234567890abcdef"
    fake_storage.blobs[content_hash] = pdf_bytes

    doc_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=DEFAULT_DEV_USER_ID,
        blob_id=uuid4(),
        folder_id=None,
        filename="transformer_2017.pdf",
        title="Attention Is All You Need",
        authors=["Vaswani et al."],
        publication_year=2017,
        doi="10.5555/3295222.3295349",
        content_hash=content_hash,
        file_size_bytes=len(pdf_bytes),
        page_count=2,
        chunk_count=0,
        pages_metadata=[],
        parsed_metadata=None,
        status="completed",
        stage="completed",
        progress=100,
        error_message=None,
        is_persistent=True,
    )
    fake_ref_db.add(doc)
    return doc


@pytest.fixture
def sample_no_ref_document(
    fake_ref_db: InMemoryAsyncReferenceSession,
    fake_storage: InMemoryStorageDouble,
) -> DocumentModel:
    """Register a sample document without references section."""
    pdf_bytes = create_synthetic_pdf_without_references()
    content_hash = "hash_no_refs_abcdef1234567890"
    fake_storage.blobs[content_hash] = pdf_bytes

    doc_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=DEFAULT_DEV_USER_ID,
        blob_id=uuid4(),
        folder_id=None,
        filename="no_refs.pdf",
        title="Document Without References",
        authors=["Solo Author"],
        publication_year=2024,
        doi=None,
        content_hash=content_hash,
        file_size_bytes=len(pdf_bytes),
        page_count=1,
        chunk_count=0,
        pages_metadata=[],
        parsed_metadata=None,
        status="completed",
        stage="completed",
        progress=100,
        error_message=None,
        is_persistent=False,
    )
    fake_ref_db.add(doc)
    return doc


@pytest.fixture
def client(
    fake_ref_db: InMemoryAsyncReferenceSession,
    fake_storage: InMemoryStorageDouble,
) -> Generator[AsyncClient, None, None]:
    """Test client configured with in-memory double and injected dependencies."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield fake_ref_db  # type: ignore[misc]

    async def override_get_current_user() -> UserModel:
        return UserModel(
            id=DEFAULT_DEV_USER_ID,
            email="researcher@verischolar.org",
            full_name="VeriScholar Researcher",
            hashed_password="hash",
            is_active=True,
        )

    def override_get_doc_service() -> DocumentService:
        return DocumentService(storage=fake_storage)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_document_service] = override_get_doc_service

    transport = ASGITransport(app=app)
    async_client = AsyncClient(transport=transport, base_url="http://testserver")

    yield async_client

    app.dependency_overrides.clear()


# ==============================================================================
# INTEGRATION TESTS FOR POST /api/v1/documents/{id}:extract-references
# ==============================================================================


@pytest.mark.asyncio
async def test_extract_references_success_from_stored_pdf(
    client: AsyncClient,
    sample_pdf_document: DocumentModel,
) -> None:
    """Verify successful reference extraction from a document PDF with 200 OK."""
    doc_id = sample_pdf_document.id
    response = await client.post(f"/api/v1/documents/{doc_id}:extract-references")

    assert response.status_code == 200
    payload = response.json()

    assert payload["success"] is True
    data = payload["data"]
    assert data["document_id"] == str(doc_id)
    assert data["total_extracted"] == 3
    assert len(data["references"]) == 3

    # Check item 1
    ref1 = data["references"][0]
    assert ref1["ref_index"] == 1
    assert "Layer normalization" in ref1["raw_text"]
    assert ref1["parsed"]["title"] == "Layer normalization"
    assert "Jimmy Lei Ba" in ref1["parsed"]["authors"]
    assert ref1["parsed"]["year"] == 2016
    assert ref1["parsed"]["arxiv_id"] == "1607.06450"

    # Check item 2
    ref2 = data["references"][1]
    assert ref2["ref_index"] == 2
    assert ref2["parsed"]["arxiv_id"] == "1409.0473"
    assert ref2["parsed"]["year"] == 2014

    # Check item 3
    ref3 = data["references"][2]
    assert ref3["ref_index"] == 3
    assert ref3["parsed"]["doi"] == "10.5555/3295222.3295349"
    assert ref3["parsed"]["year"] == 2017


@pytest.mark.asyncio
async def test_extract_references_idempotent_database_cache(
    client: AsyncClient,
    sample_pdf_document: DocumentModel,
    fake_storage: InMemoryStorageDouble,
) -> None:
    """Verify that second call returns cached items without reading storage again."""
    doc_id = sample_pdf_document.id

    # 1. First call extracts from storage
    resp1 = await client.post(f"/api/v1/documents/{doc_id}:extract-references")
    assert resp1.status_code == 200
    assert fake_storage.read_calls == 1

    # 2. Second call uses database cache
    resp2 = await client.post(f"/api/v1/documents/{doc_id}:extract-references")
    assert resp2.status_code == 200
    assert fake_storage.read_calls == 1  # No additional storage read!
    assert resp2.json()["data"]["total_extracted"] == 3


@pytest.mark.asyncio
async def test_extract_references_force_reextract_overwrites_cache(
    client: AsyncClient,
    sample_pdf_document: DocumentModel,
    fake_storage: InMemoryStorageDouble,
) -> None:
    """Verify that force_reextract=True bypasses cache and reads storage."""
    doc_id = sample_pdf_document.id

    # 1. Initial call
    await client.post(f"/api/v1/documents/{doc_id}:extract-references")
    assert fake_storage.read_calls == 1

    # 2. Force re-extract
    resp = await client.post(
        f"/api/v1/documents/{doc_id}:extract-references",
        json={"force_reextract": True},
    )
    assert resp.status_code == 200
    assert fake_storage.read_calls == 2
    assert resp.json()["data"]["total_extracted"] == 3


@pytest.mark.asyncio
async def test_extract_references_pdf_without_references_returns_empty(
    client: AsyncClient,
    sample_no_ref_document: DocumentModel,
) -> None:
    """Verify document with no references section returns total_extracted=0."""
    doc_id = sample_no_ref_document.id
    response = await client.post(f"/api/v1/documents/{doc_id}:extract-references")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total_extracted"] == 0
    assert data["references"] == []


@pytest.mark.asyncio
async def test_extract_references_multi_tenant_isolation(
    client: AsyncClient,
    fake_ref_db: InMemoryAsyncReferenceSession,
) -> None:
    """Verify 404 DOCUMENT_NOT_FOUND when accessing another user's document."""
    foreign_doc_id = uuid4()
    foreign_doc = DocumentModel(
        id=foreign_doc_id,
        user_id=uuid4(),  # Different user
        blob_id=uuid4(),
        folder_id=None,
        filename="foreign.pdf",
        title="Other User Paper",
        authors=[],
        publication_year=2025,
        doi=None,
        content_hash="foreign_hash",
        file_size_bytes=1000,
        page_count=1,
        chunk_count=0,
        pages_metadata=[],
        parsed_metadata=None,
        status="completed",
        stage="completed",
        progress=100,
        error_message=None,
        is_persistent=False,
    )
    fake_ref_db.add(foreign_doc)

    response = await client.post(f"/api/v1/documents/{foreign_doc_id}:extract-references")
    assert response.status_code == 404
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_extract_references_not_found(client: AsyncClient) -> None:
    """Verify 404 when document ID does not exist."""
    random_id = uuid4()
    response = await client.post(f"/api/v1/documents/{random_id}:extract-references")

    assert response.status_code == 404
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_extract_references_invalid_uuid(client: AsyncClient) -> None:
    """Verify 422 when path parameter is an invalid UUID."""
    response = await client.post("/api/v1/documents/not-a-valid-uuid:extract-references")
    assert response.status_code == 422
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_openapi_schema_contains_extract_references_endpoint() -> None:
    """Verify the endpoint is correctly registered in the OpenAPI schema."""
    schema = app.openapi()
    path = "/api/v1/documents/{document_id}:extract-references"
    assert path in schema["paths"]
    post_op = schema["paths"][path]["post"]
    assert post_op["summary"] == "Bóc tách danh mục tài liệu tham khảo"
    assert "200" in post_op["responses"]
    assert "Module 1: Documents" in post_op["tags"]
