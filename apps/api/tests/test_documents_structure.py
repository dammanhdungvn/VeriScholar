"""Automated integration tests for GET /api/v1/documents/{id}/structure endpoint."""

from collections.abc import AsyncGenerator, AsyncIterator, Generator
from datetime import UTC, datetime
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pymupdf
import pytest
from api import app
from api.db.models.document import DocumentModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import DEFAULT_DEV_USER_ID, get_current_user, get_document_service
from api.services.document_service import DocumentService
from core.ports.storage import IBlobStoragePort
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class InMemoryAsyncStructureSession:
    """Deterministic in-memory database test double for document structure tests."""

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

    async def delete(self, obj: object) -> None:
        pass

    async def execute(self, statement: object) -> MagicMock:
        result_mock = MagicMock()

        try:
            compiled = statement.compile()  # type: ignore[union-attr]
            params = compiled.params or {}
        except Exception:
            params = {}

        target_id = params.get("id_1") or params.get("id")
        target_user_id = params.get("user_id_1") or params.get("user_id")

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


def create_synthetic_pdf_with_structure() -> bytes:
    """Create a synthetic PDF containing Title, Abstract, and numbered Sections."""
    doc = pymupdf.open()

    # Page 1: Title and Abstract
    p1 = doc.new_page(width=612, height=792)
    p1.insert_text((150, 100), "Deep Learning for Scholarly Verification", fontsize=18)
    p1.insert_text((250, 200), "Abstract", fontsize=14)
    p1.insert_text(
        (100, 230),
        "In this paper we propose an end-to-end framework for parsing scholarly articles.\n"
        "Our method establishes state-of-the-art accuracy in visual document understanding.",
        fontsize=11,
    )

    # Page 2: Section 1 & Section 2
    p2 = doc.new_page(width=612, height=792)
    p2.insert_text((100, 100), "1 Introduction", fontsize=14)
    p2.insert_text((100, 130), "Scholarly communication has expanded rapidly...", fontsize=11)
    p2.insert_text((100, 300), "2 Methodology", fontsize=14)
    p2.insert_text((100, 330), "We formulate the verification problem as a graph...", fontsize=11)

    # Page 3: Section 3 Conclusion
    p3 = doc.new_page(width=612, height=792)
    p3.insert_text((100, 100), "3 Conclusion", fontsize=14)
    p3.insert_text((100, 130), "We have presented a robust methodology...", fontsize=11)

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@pytest.fixture
def fake_db() -> InMemoryAsyncStructureSession:
    return InMemoryAsyncStructureSession()


@pytest.fixture
def fake_storage() -> InMemoryStorageDouble:
    return InMemoryStorageDouble()


@pytest.fixture
def client(
    fake_db: InMemoryAsyncStructureSession,
    fake_storage: InMemoryStorageDouble,
) -> Generator[AsyncClient, None, None]:
    """Test client configured with in-memory double and injected dependencies."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield fake_db  # type: ignore[misc]

    async def override_get_current_user() -> UserModel:
        return UserModel(
            id=DEFAULT_DEV_USER_ID,
            email="developer@verischolar.org",
            full_name="VeriScholar Developer",
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


@pytest.mark.asyncio
async def test_get_document_structure_initial_extraction_success(
    client: AsyncClient,
    fake_db: InMemoryAsyncStructureSession,
    fake_storage: InMemoryStorageDouble,
) -> None:
    """Verify initial extraction parses Title, Abstract, and Sections with bounding boxes."""
    doc_id = uuid4()
    pdf_bytes = create_synthetic_pdf_with_structure()
    content_hash = "mock_structure_hash_1"
    fake_storage.blobs[content_hash] = pdf_bytes

    doc = DocumentModel(
        id=doc_id,
        user_id=DEFAULT_DEV_USER_ID,
        filename="deep_learning_paper.pdf",
        content_hash=content_hash,
        file_size_bytes=len(pdf_bytes),
        page_count=3,
        status="completed",
        stage="completed",
        progress=100,
        parsed_metadata=None,
    )
    fake_db.add(doc)

    response = await client.get(f"/api/v1/documents/{doc_id}/structure")
    assert response.status_code == 200

    payload = response.json()
    assert payload["success"] is True
    data = payload["data"]

    assert data["document_id"] == str(doc_id)
    assert data["title"] == "Deep Learning for Scholarly Verification"
    assert "In this paper we propose" in data["abstract"]
    assert len(data["abstract_bounding_boxes"]) == 1
    assert len(data["abstract_bounding_boxes"][0]) == 5

    assert len(data["sections"]) >= 3
    section_titles = [s["title"] for s in data["sections"]]
    assert any("Introduction" in t for t in section_titles)
    assert any("Methodology" in t for t in section_titles)
    assert any("Conclusion" in t for t in section_titles)

    # Verify storage read was performed
    assert fake_storage.read_calls == 1

    # Verify structure was cached in doc.parsed_metadata
    assert doc.parsed_metadata is not None
    assert "structure" in doc.parsed_metadata
    assert doc.title == "Deep Learning for Scholarly Verification"


@pytest.mark.asyncio
async def test_get_document_structure_database_cache_hit(
    client: AsyncClient,
    fake_db: InMemoryAsyncStructureSession,
    fake_storage: InMemoryStorageDouble,
) -> None:
    """Verify second call serves directly from database cache without reading storage blob."""
    doc_id = uuid4()
    cached_structure = {
        "title": "Cached Paper Title",
        "abstract": "This is cached abstract text.",
        "abstract_bounding_boxes": [[0.1, 0.2, 0.9, 0.3, 1]],
        "sections": [
            {"title": "1 Introduction", "page_number": 1, "bounding_boxes": [[0.1, 0.35, 0.5, 0.38, 1]]},
            {"title": "2 Background", "page_number": 2, "bounding_boxes": [[0.1, 0.15, 0.5, 0.18, 2]]},
        ],
        "extracted_at": datetime.now(UTC).isoformat(),
    }

    doc = DocumentModel(
        id=doc_id,
        user_id=DEFAULT_DEV_USER_ID,
        filename="cached_paper.pdf",
        content_hash="cached_hash_1",
        file_size_bytes=1024,
        page_count=2,
        status="completed",
        stage="completed",
        progress=100,
        parsed_metadata={"structure": cached_structure},
    )
    fake_db.add(doc)

    response = await client.get(f"/api/v1/documents/{doc_id}/structure")
    assert response.status_code == 200

    payload = response.json()
    assert payload["success"] is True
    data = payload["data"]

    assert data["title"] == "Cached Paper Title"
    assert data["abstract"] == "This is cached abstract text."
    assert len(data["sections"]) == 2
    assert data["sections"][0]["title"] == "1 Introduction"

    # Crucial: storage blob was NEVER read because cache was hit
    assert fake_storage.read_calls == 0


@pytest.mark.asyncio
async def test_get_document_structure_force_refresh(
    client: AsyncClient,
    fake_db: InMemoryAsyncStructureSession,
    fake_storage: InMemoryStorageDouble,
) -> None:
    """Verify ?force_refresh=true bypasses cached structure and re-parses from storage blob."""
    doc_id = uuid4()
    pdf_bytes = create_synthetic_pdf_with_structure()
    content_hash = "force_refresh_hash"
    fake_storage.blobs[content_hash] = pdf_bytes

    cached_structure = {
        "title": "Old Stale Title",
        "abstract": "Old stale abstract",
        "abstract_bounding_boxes": [],
        "sections": [],
        "extracted_at": datetime.now(UTC).isoformat(),
    }

    doc = DocumentModel(
        id=doc_id,
        user_id=DEFAULT_DEV_USER_ID,
        filename="refresh_paper.pdf",
        content_hash=content_hash,
        file_size_bytes=len(pdf_bytes),
        page_count=3,
        status="completed",
        stage="completed",
        progress=100,
        parsed_metadata={"structure": cached_structure},
    )
    fake_db.add(doc)

    response = await client.get(f"/api/v1/documents/{doc_id}/structure?force_refresh=true")
    assert response.status_code == 200

    payload = response.json()
    data = payload["data"]

    # Refreshed from PDF, stale cache overridden
    assert data["title"] == "Deep Learning for Scholarly Verification"
    assert len(data["sections"]) >= 3
    assert fake_storage.read_calls == 1


@pytest.mark.asyncio
async def test_get_document_structure_not_found(
    client: AsyncClient,
) -> None:
    """Verify 404 response when querying a nonexistent document UUID."""
    random_id = uuid4()
    response = await client.get(f"/api/v1/documents/{random_id}/structure")

    assert response.status_code == 404
    payload = response.json()
    assert payload["error"]["code"] == "DOCUMENT_NOT_FOUND"
    assert payload["error"]["field"] == "id"


@pytest.mark.asyncio
async def test_get_document_structure_unauthorized_user(
    client: AsyncClient,
    fake_db: InMemoryAsyncStructureSession,
) -> None:
    """Verify 404 response when document belongs to another tenant user (no data leakage)."""
    doc_id = uuid4()
    other_user_id = uuid4()

    doc = DocumentModel(
        id=doc_id,
        user_id=other_user_id,
        filename="other_user_paper.pdf",
        content_hash="other_user_hash",
        file_size_bytes=1024,
        page_count=1,
        status="completed",
        stage="completed",
        progress=100,
        parsed_metadata=None,
    )
    fake_db.add(doc)

    response = await client.get(f"/api/v1/documents/{doc_id}/structure")
    assert response.status_code == 404
    payload = response.json()
    assert payload["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_document_structure_invalid_uuid(
    client: AsyncClient,
) -> None:
    """Verify 422 Unprocessable Entity when document_id is not a valid UUID."""
    response = await client.get("/api/v1/documents/not-a-valid-uuid/structure")
    assert response.status_code == 422
