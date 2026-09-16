"""Automated integration tests for GET /api/v1/documents/{id}/structure endpoint."""

from collections.abc import AsyncGenerator, AsyncIterator, Generator
from datetime import UTC, datetime
from typing import Any
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

    async def execute(self, statement: Any) -> MagicMock:
        result_mock = MagicMock()

        try:
            compiled = statement.compile()
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

    def get_blob_path(self, content_hash: str) -> str:
        return f"storage/{content_hash}.pdf"

    async def save_blob(
        self, stream: AsyncIterator[bytes], content_hash: str
    ) -> tuple[str, int]:
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
    p3.insert_text(
        (100, 130), "In conclusion, this approach enhances research transparency.", fontsize=11
    )

    return doc.tobytes()


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
def mock_storage() -> InMemoryStorageDouble:
    storage = InMemoryStorageDouble()
    pdf_bytes = create_synthetic_pdf_with_structure()
    storage.blobs["dummyhash123"] = pdf_bytes
    return storage


@pytest.fixture
def mock_db() -> InMemoryAsyncStructureSession:
    db = InMemoryAsyncStructureSession()
    doc_id = UUID("11111111-1111-1111-1111-111111111111")
    user_id = DEFAULT_DEV_USER_ID
    doc = DocumentModel(
        id=doc_id,
        user_id=user_id,
        filename="attention.pdf",
        content_hash="dummyhash123",
        file_size_bytes=1000,
        status="completed",
        stage="completed",
        progress=100,
        parsed_metadata=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(doc)
    return db


@pytest.fixture
def client(
    mock_storage: InMemoryStorageDouble,
    mock_db: InMemoryAsyncStructureSession,
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
async def test_get_document_structure_success(
    client: AsyncClient, mock_storage: InMemoryStorageDouble
) -> None:
    doc_id = "11111111-1111-1111-1111-111111111111"
    response = await client.get(f"/api/v1/documents/{doc_id}/structure")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    data = payload["data"]

    assert data["document_id"] == doc_id
    assert "Deep Learning for Scholarly Verification" in data["title"]
    assert "end-to-end framework" in data["abstract"]
    assert len(data["sections"]) >= 3

    sec_titles = [s["title"] for s in data["sections"]]
    assert any("Introduction" in t for t in sec_titles)
    assert any("Methodology" in t for t in sec_titles)
    assert any("Conclusion" in t for t in sec_titles)

    # Verify Bounding Boxes present
    for sec in data["sections"]:
        assert "page_number" in sec
        assert isinstance(sec["bounding_boxes"], list)
        if sec["bounding_boxes"]:
            box = sec["bounding_boxes"][0]
            assert len(box) == 5
            x0, y0, x1, y1, page = box
            assert x0 <= x1
            assert y0 <= y1


@pytest.mark.asyncio
async def test_get_document_structure_cache_hit(
    client: AsyncClient, mock_storage: InMemoryStorageDouble
) -> None:
    doc_id = "11111111-1111-1111-1111-111111111111"
    # First call extracts from storage
    res1 = await client.get(f"/api/v1/documents/{doc_id}/structure")
    assert res1.status_code == 200
    assert mock_storage.read_calls == 1

    # Second call hits database cache in parsed_metadata
    res2 = await client.get(f"/api/v1/documents/{doc_id}/structure")
    assert res2.status_code == 200
    assert mock_storage.read_calls == 1  # No additional storage read!


@pytest.mark.asyncio
async def test_get_document_structure_force_refresh(
    client: AsyncClient, mock_storage: InMemoryStorageDouble
) -> None:
    doc_id = "11111111-1111-1111-1111-111111111111"
    res1 = await client.get(f"/api/v1/documents/{doc_id}/structure")
    assert res1.status_code == 200
    assert mock_storage.read_calls == 1

    # Force refresh bypasses cache
    res2 = await client.get(f"/api/v1/documents/{doc_id}/structure?force_refresh=true")
    assert res2.status_code == 200
    assert mock_storage.read_calls == 2  # Re-read blob from storage


@pytest.mark.asyncio
async def test_get_document_structure_not_found(client: AsyncClient) -> None:
    non_existent = str(uuid4())
    response = await client.get(f"/api/v1/documents/{non_existent}/structure")

    assert response.status_code == 404
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_document_structure_tenant_isolation(
    client: AsyncClient, mock_db: InMemoryAsyncStructureSession
) -> None:
    doc_id = UUID("22222222-2222-2222-2222-222222222222")
    other_user = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=other_user,
        filename="other.pdf",
        content_hash="dummyhash123",
        file_size_bytes=1000,
        status="completed",
        stage="completed",
        progress=100,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_db.add(doc)

    response = await client.get(f"/api/v1/documents/{doc_id}/structure")
    assert response.status_code == 404
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "DOCUMENT_NOT_FOUND"
