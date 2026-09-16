"""Automated integration tests for GET /api/v1/documents/{id}/export-pdf endpoint."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pymupdf
import pytest
from api import app
from api.adapters.pdf_annotator import PyMuPdfAnnotator
from api.db.models.document import DocumentModel
from api.db.models.summary import DocumentSummaryModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import (
    DEFAULT_DEV_USER_ID,
    get_current_user,
    get_document_service,
    get_pdf_annotator,
)
from api.services.document_service import DocumentService
from core.ports.storage import IBlobStoragePort
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


def _generate_minimal_pdf() -> bytes:
    """Generate a minimal valid single-page PDF binary with selectable text."""
    doc = pymupdf.open()
    page = doc.new_page(width=600, height=800)
    page.insert_text(
        (72, 100),
        "Advancing Retrieval-Augmented Generation for Enterprise Data",
        fontsize=14,
    )
    page.insert_text(
        (72, 150),
        "Conventional RAG systems are optimized for unstructured text and fail on enterprise data.",
        fontsize=10,
    )
    page.insert_text(
        (72, 200),
        "We propose hybrid dense and sparse retrieval with structured chunking.",
        fontsize=10,
    )
    page.insert_text(
        (72, 250),
        "A limitation is higher indexing latency compared to flat indexing.",
        fontsize=10,
    )
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


class InMemoryAsyncExportSession:
    """Deterministic in-memory database test double for export PDF tests."""

    def __init__(self) -> None:
        self.documents: dict[UUID, DocumentModel] = {}
        self.summaries: dict[UUID, DocumentSummaryModel] = {}

    def add(self, obj: object) -> None:
        if isinstance(obj, DocumentModel):
            self.documents[obj.id] = obj
        elif isinstance(obj, DocumentSummaryModel):
            self.summaries[obj.document_id] = obj

    async def flush(self) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def refresh(self, obj: object) -> None:
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
            return result_mock

        # 2. DocumentSummaryModel lookup
        if "FROM document_summaries" in statement_str:
            target_doc_id = params.get("document_id_1") or params.get("document_id")
            summary = self.summaries.get(target_doc_id) if target_doc_id else None
            result_mock.scalar_one_or_none.return_value = summary
            return result_mock

        result_mock.scalar_one_or_none.return_value = None
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

    async def exists(self, content_hash: str) -> bool:
        return content_hash in self.blobs

    async def delete(self, content_hash: str) -> bool:
        return self.blobs.pop(content_hash, None) is not None

    async def save_blob(self, content: bytes, content_hash: str) -> str:
        return await self.store(content, content_hash)


@pytest.fixture
def in_memory_session() -> InMemoryAsyncExportSession:
    return InMemoryAsyncExportSession()


@pytest.fixture
def mock_storage() -> MockBlobStorage:
    storage = MockBlobStorage()
    pdf_bytes = _generate_minimal_pdf()
    storage.blobs["f69bb3aef06e2bb99be171478448ed43fc6dd3c2bbe74994e435824f067ec047"] = pdf_bytes
    return storage


@pytest.fixture
def mock_user() -> UserModel:
    return UserModel(
        id=DEFAULT_DEV_USER_ID,
        email="developer@verischolar.org",
        full_name="VeriScholar Developer",
        hashed_password="dev_dummy_password",
        is_active=True,
    )


@pytest.fixture
def client(
    in_memory_session: InMemoryAsyncExportSession,
    mock_storage: MockBlobStorage,
    mock_user: UserModel,
) -> Generator[AsyncClient, None, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield in_memory_session  # type: ignore[misc]

    def override_get_current_user() -> UserModel:
        return mock_user

    def override_get_document_service() -> DocumentService:
        return DocumentService(
            storage=mock_storage,
            pdf_annotator=PyMuPdfAnnotator(),
        )

    def override_get_pdf_annotator() -> PyMuPdfAnnotator:
        return PyMuPdfAnnotator()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_document_service] = override_get_document_service
    app.dependency_overrides[get_pdf_annotator] = override_get_pdf_annotator

    transport = ASGITransport(app=app)
    async_client = AsyncClient(transport=transport, base_url="http://testserver")

    yield async_client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_export_pdf_with_highlights_success(
    client: AsyncClient,
    in_memory_session: InMemoryAsyncExportSession,
) -> None:
    """Test exporting PDF with ISO 32000 native highlight annotations embedded."""
    doc_id = uuid4()
    now = datetime.now(UTC)

    doc = DocumentModel(
        id=doc_id,
        user_id=DEFAULT_DEV_USER_ID,
        folder_id=None,
        blob_id=uuid4(),
        filename="Test Paper.pdf",
        content_hash="f69bb3aef06e2bb99be171478448ed43fc6dd3c2bbe74994e435824f067ec047",
        title="Test Paper",
        authors=["Author One"],
        publication_year=2026,
        status="ready",
        file_size_bytes=1024,
        page_count=1,
        created_at=now,
        updated_at=now,
    )
    in_memory_session.add(doc)

    # Add summary with 3 citations
    summary = DocumentSummaryModel(
        id=uuid4(),
        document_id=doc_id,
        problem_statement="Conventional RAG fails on enterprise data.",
        problem_citations=[[0.12, 0.18, 0.85, 0.22, 1]],
        contributions="Hybrid dense and sparse retrieval.",
        contribution_citations=[[0.12, 0.24, 0.85, 0.28, 1]],
        limitations="Higher indexing latency.",
        limitation_citations=[[0.12, 0.30, 0.85, 0.34, 1]],
        total_tokens=250,
        latency_ms=120,
        created_at=now,
        updated_at=now,
    )
    in_memory_session.add(summary)

    response = await client.get(f"/api/v1/documents/{doc_id}/export-pdf?include_highlights=true")

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert "attachment" in response.headers["Content-Disposition"]
    assert "Test_Paper_annotated.pdf" in response.headers["Content-Disposition"]
    assert response.headers["X-Annotation-Count"] == "3"

    # Verify native ISO annotations inside returned PDF binary
    pdf_bytes = response.content
    assert len(pdf_bytes) > 0
    exported_doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    page = exported_doc[0]
    annots = list(page.annots())
    assert len(annots) == 3

    info_titles = [a.info.get("title", "") for a in annots]
    assert any("Problem Statement" in t for t in info_titles)
    assert any("Contributions" in t for t in info_titles)
    assert any("Limitations" in t for t in info_titles)

    # Verify Bookmarks / Outlines Navigation Tree
    toc = exported_doc.get_toc()
    assert len(toc) >= 1
    assert any("VeriScholar AI Grounded Summary" in item[1] for item in toc)

    # Verify Standardized PDF Metadata
    meta = exported_doc.metadata or {}
    assert meta.get("producer") == "VeriScholar AI Research Assistant (verischolar.org)"
    assert meta.get("title") == "Test Paper"
    assert meta.get("author") == "Author One"

    exported_doc.close()


@pytest.mark.asyncio
async def test_export_pdf_without_highlights_success(
    client: AsyncClient,
    in_memory_session: InMemoryAsyncExportSession,
) -> None:
    """Test exporting clean PDF when include_highlights=false."""
    doc_id = uuid4()
    now = datetime.now(UTC)

    doc = DocumentModel(
        id=doc_id,
        user_id=DEFAULT_DEV_USER_ID,
        folder_id=None,
        blob_id=uuid4(),
        filename="Test Paper.pdf",
        content_hash="f69bb3aef06e2bb99be171478448ed43fc6dd3c2bbe74994e435824f067ec047",
        title="Test Paper",
        authors=["Author One"],
        publication_year=2026,
        status="ready",
        file_size_bytes=1024,
        page_count=1,
        created_at=now,
        updated_at=now,
    )
    in_memory_session.add(doc)

    response = await client.get(f"/api/v1/documents/{doc_id}/export-pdf?include_highlights=false")

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert "Test_Paper.pdf" in response.headers["Content-Disposition"]
    assert response.headers["X-Annotation-Count"] == "0"

    # Verify 0 annotations
    exported_doc = pymupdf.open(stream=response.content, filetype="pdf")
    assert len(list(exported_doc[0].annots())) == 0
    exported_doc.close()


@pytest.mark.asyncio
async def test_export_pdf_when_summary_absent(
    client: AsyncClient,
    in_memory_session: InMemoryAsyncExportSession,
) -> None:
    """Test exporting PDF when summary is absent still returns 200 without annotations."""
    doc_id = uuid4()
    now = datetime.now(UTC)

    doc = DocumentModel(
        id=doc_id,
        user_id=DEFAULT_DEV_USER_ID,
        folder_id=None,
        blob_id=uuid4(),
        filename="Clean Document.pdf",
        content_hash="f69bb3aef06e2bb99be171478448ed43fc6dd3c2bbe74994e435824f067ec047",
        title="Clean Document",
        authors=["Author"],
        publication_year=2026,
        status="ready",
        file_size_bytes=1024,
        page_count=1,
        created_at=now,
        updated_at=now,
    )
    in_memory_session.add(doc)

    response = await client.get(f"/api/v1/documents/{doc_id}/export-pdf?include_highlights=true")

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert response.headers["X-Annotation-Count"] == "0"


@pytest.mark.asyncio
async def test_export_pdf_multi_tenant_isolation(
    client: AsyncClient,
    in_memory_session: InMemoryAsyncExportSession,
) -> None:
    """Test tenant isolation: User B document returns 404 for User A."""
    doc_id = uuid4()
    other_user_id = uuid4()
    now = datetime.now(UTC)

    doc = DocumentModel(
        id=doc_id,
        user_id=other_user_id,
        folder_id=None,
        blob_id=uuid4(),
        filename="Other User Paper.pdf",
        content_hash="f69bb3aef06e2bb99be171478448ed43fc6dd3c2bbe74994e435824f067ec047",
        title="Other User Paper",
        authors=["Author"],
        publication_year=2026,
        status="ready",
        file_size_bytes=1024,
        page_count=1,
        created_at=now,
        updated_at=now,
    )
    in_memory_session.add(doc)

    response = await client.get(f"/api/v1/documents/{doc_id}/export-pdf")

    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_export_pdf_nonexistent_document(client: AsyncClient) -> None:
    """Test exporting nonexistent document returns 404."""
    nonexistent_id = uuid4()
    response = await client.get(f"/api/v1/documents/{nonexistent_id}/export-pdf")

    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_export_pdf_invalid_uuid(client: AsyncClient) -> None:
    """Test exporting with invalid UUID string returns 422."""
    response = await client.get("/api/v1/documents/not-a-valid-uuid/export-pdf")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_export_pdf_missing_physical_blob(
    client: AsyncClient,
    in_memory_session: InMemoryAsyncExportSession,
) -> None:
    """Test exporting document with missing storage blob returns 404 FILE_NOT_FOUND."""
    doc_id = uuid4()
    now = datetime.now(UTC)

    doc = DocumentModel(
        id=doc_id,
        user_id=DEFAULT_DEV_USER_ID,
        folder_id=None,
        blob_id=uuid4(),
        filename="Missing Blob.pdf",
        content_hash="0000000000000000000000000000000000000000000000000000000000000000",
        title="Missing Blob",
        authors=["Author"],
        publication_year=2026,
        status="ready",
        file_size_bytes=1024,
        page_count=1,
        created_at=now,
        updated_at=now,
    )
    in_memory_session.add(doc)

    response = await client.get(f"/api/v1/documents/{doc_id}/export-pdf")

    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "FILE_NOT_FOUND"


@pytest.mark.asyncio
async def test_export_pdf_with_category_filtering(
    client: AsyncClient,
    in_memory_session: InMemoryAsyncExportSession,
) -> None:
    """Test filtering export highlights by category (e.g. only contributions)."""
    doc_id = uuid4()
    now = datetime.now(UTC)

    doc = DocumentModel(
        id=doc_id,
        user_id=DEFAULT_DEV_USER_ID,
        folder_id=None,
        blob_id=uuid4(),
        filename="Filter Paper.pdf",
        content_hash="f69bb3aef06e2bb99be171478448ed43fc6dd3c2bbe74994e435824f067ec047",
        title="Filter Paper Title",
        authors=["Researcher"],
        publication_year=2026,
        status="ready",
        file_size_bytes=1024,
        page_count=1,
        created_at=now,
        updated_at=now,
    )
    in_memory_session.add(doc)

    summary = DocumentSummaryModel(
        id=uuid4(),
        document_id=doc_id,
        problem_statement="Enterprise data search is broken.",
        problem_citations=[[0.12, 0.18, 0.85, 0.22, 1]],
        contributions="We present hybrid dense-sparse indexing.",
        contribution_citations=[[0.12, 0.24, 0.85, 0.28, 1]],
        limitations="Higher latency during cold start.",
        limitation_citations=[[0.12, 0.30, 0.85, 0.34, 1]],
        total_tokens=250,
        latency_ms=120,
        created_at=now,
        updated_at=now,
    )
    in_memory_session.add(summary)

    # 1. Single category filter
    resp = await client.get(f"/api/v1/documents/{doc_id}/export-pdf?categories=contributions")
    assert resp.status_code == 200
    assert resp.headers["X-Annotation-Count"] == "1"

    exported = pymupdf.open(stream=resp.content, filetype="pdf")
    page = exported[0]
    annots = list(page.annots())
    assert len(annots) == 1
    assert "Contributions" in annots[0].info.get("title", "")
    exported.close()

    # 2. Multi-category filter
    resp2 = await client.get(
        f"/api/v1/documents/{doc_id}/export-pdf?categories=problem_statement,limitations"
    )
    assert resp2.status_code == 200
    assert resp2.headers["X-Annotation-Count"] == "2"

    exported2 = pymupdf.open(stream=resp2.content, filetype="pdf")
    page2 = exported2[0]
    annots2 = list(page2.annots())
    assert len(annots2) == 2
    titles = [a.info.get("title", "") for a in annots2]
    assert any("Problem Statement" in t for t in titles)
    assert any("Limitations" in t for t in titles)
    assert not any("Contributions" in t for t in titles)
    exported2.close()
