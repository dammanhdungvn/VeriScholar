"""Automated integration tests for Personal Library & Multi-Paper Synthesis (Module 4)."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.chunk import DocumentChunkModel
from api.db.models.document import DocumentModel
from api.db.models.folder import FolderModel
from api.db.models.note import ResearchNoteModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import DEFAULT_DEV_USER_ID, get_current_user
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class InMemoryLibraryStore:
    """In-memory store for personal library and synthesis tests."""

    def __init__(self) -> None:
        self.documents: dict[UUID, DocumentModel] = {}
        self.folders: dict[UUID, FolderModel] = {}
        self.notes: dict[UUID, ResearchNoteModel] = {}
        self.chunks: dict[UUID, DocumentChunkModel] = {}

    def add(self, obj: object) -> None:
        now = datetime.now(UTC)
        if isinstance(obj, DocumentModel):
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            if getattr(obj, "status", None) is None:
                obj.status = "completed"
            self.documents[obj.id] = obj
        elif isinstance(obj, FolderModel):
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()
            self.folders[obj.id] = obj
        elif isinstance(obj, ResearchNoteModel):
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()
            self.notes[obj.id] = obj
        elif isinstance(obj, DocumentChunkModel):
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()
            self.chunks[obj.id] = obj

    async def flush(self) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def refresh(self, obj: object) -> None:
        pass

    async def execute(self, statement: Any, *args: Any, **kwargs: Any) -> Any:
        stmt_str = str(statement)
        try:
            compiled = statement.compile()
            params = compiled.params or {}
        except Exception:
            params = {}

        # 1. Count query for library documents
        if "count(documents.id)" in stmt_str.lower():
            mock_res = MagicMock()
            folder_param = None
            search_param = None
            for k, v in params.items():
                if "folder_id" in k.lower() and isinstance(v, UUID):
                    folder_param = v
                elif "ilike" in k.lower() or "like" in k.lower() or "title" in k.lower():
                    search_param = str(v).replace("%", "").lower()

            matching = [
                d
                for d in self.documents.values()
                if d.user_id == DEFAULT_DEV_USER_ID and d.is_persistent
            ]
            if folder_param:
                matching = [d for d in matching if d.folder_id == folder_param]
            if search_param:
                matching = [
                    d
                    for d in matching
                    if (d.title and search_param in d.title.lower())
                    or (d.filename and search_param in d.filename.lower())
                ]
            mock_res.scalar_one.return_value = len(matching)
            return mock_res

        # 2. Select folders
        if "FROM folders" in stmt_str:
            mock_res = MagicMock()
            target_id = None
            for v in params.values():
                if isinstance(v, UUID) and v in self.folders:
                    target_id = v
                    break
            folder = self.folders.get(target_id) if target_id else None
            mock_res.scalar_one_or_none.return_value = folder
            mock_res.scalars.return_value.all.return_value = [folder] if folder else []
            return mock_res

        # 3. Select research notes
        if "FROM research_notes" in stmt_str:
            mock_res = MagicMock()
            notes = [n for n in self.notes.values() if n.user_id == DEFAULT_DEV_USER_ID]
            mock_res.scalars.return_value.all.return_value = notes
            return mock_res

        # 4. Select document chunks
        if "FROM document_chunks" in stmt_str:
            mock_res = MagicMock()
            chunks = list(self.chunks.values())
            mock_res.scalars.return_value.all.return_value = chunks
            return mock_res

        # 5. Select documents
        if "FROM documents" in stmt_str:
            mock_res = MagicMock()
            folder_param = None
            search_param = None
            doc_ids_param: set[UUID] = set()

            for k, v in params.items():
                if "folder_id" in k.lower() and isinstance(v, UUID):
                    folder_param = v
                elif "like" in k.lower() or "title" in k.lower():
                    search_param = str(v).replace("%", "").lower()
                elif isinstance(v, (list, tuple)):
                    doc_ids_param.update([item for item in v if isinstance(item, UUID)])
                elif isinstance(v, UUID) and v in self.documents:
                    doc_ids_param.add(v)

            matching = [
                d
                for d in self.documents.values()
                if d.user_id == DEFAULT_DEV_USER_ID and d.is_persistent
            ]
            if doc_ids_param:
                matching = [d for d in matching if d.id in doc_ids_param]
            if folder_param:
                matching = [d for d in matching if d.folder_id == folder_param]
            if search_param:
                matching = [
                    d
                    for d in matching
                    if (d.title and search_param in d.title.lower())
                    or (d.filename and search_param in d.filename.lower())
                ]

            mock_res.scalars.return_value.all.return_value = matching
            mock_res.scalar_one_or_none.return_value = matching[0] if matching else None
            return mock_res

        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = None
        mock_res.scalars.return_value.all.return_value = []
        return mock_res


@pytest.fixture
def library_store() -> InMemoryLibraryStore:
    return InMemoryLibraryStore()


@pytest.fixture
def mock_db_session(library_store: InMemoryLibraryStore) -> AsyncSession:
    return library_store  # type: ignore[return-value]


@pytest.fixture
def mock_user() -> UserModel:
    user = UserModel(
        email="scholar@verischolar.org",
        full_name="Prof. Veri",
        is_active=True,
    )
    user.id = DEFAULT_DEV_USER_ID
    return user


@pytest.fixture
def client(
    mock_db_session: AsyncSession,
    mock_user: UserModel,
) -> Generator[AsyncClient, None, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield mock_db_session

    async def override_get_current_user() -> UserModel:
        return mock_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)
    async_client = AsyncClient(transport=transport, base_url="http://testserver")
    yield async_client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_library_documents_empty(client: AsyncClient) -> None:
    """Empty library returns 200 with empty list and RFC 8288 links."""
    response = await client.get("/api/v1/library/documents")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"] == []
    assert body["meta"]["total"] == 0
    assert "links" in body


@pytest.mark.asyncio
async def test_list_library_documents_only_persistent(
    client: AsyncClient,
    library_store: InMemoryLibraryStore,
) -> None:
    """Only persistent (starred) documents appear in library."""
    doc_starred = DocumentModel(
        user_id=DEFAULT_DEV_USER_ID,
        filename="starred_paper.pdf",
        title="Attention Is All You Need",
        content_hash="h1",
        file_size_bytes=1000,
        is_persistent=True,
    )
    doc_temp = DocumentModel(
        user_id=DEFAULT_DEV_USER_ID,
        filename="temp_upload.pdf",
        title="Temporary Paper",
        content_hash="h2",
        file_size_bytes=500,
        is_persistent=False,
    )
    library_store.add(doc_starred)
    library_store.add(doc_temp)

    response = await client.get("/api/v1/library/documents")
    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["total"] == 1
    assert body["data"][0]["id"] == str(doc_starred.id)


@pytest.mark.asyncio
async def test_list_library_documents_filter_folder(
    client: AsyncClient,
    library_store: InMemoryLibraryStore,
) -> None:
    """Filter library documents by folder_id."""
    folder = FolderModel(user_id=DEFAULT_DEV_USER_ID, name="NLP", parent_id=None)
    library_store.add(folder)

    doc_in_folder = DocumentModel(
        user_id=DEFAULT_DEV_USER_ID,
        filename="bert.pdf",
        title="BERT Pre-training",
        content_hash="h3",
        file_size_bytes=1000,
        is_persistent=True,
        folder_id=folder.id,
    )
    doc_other = DocumentModel(
        user_id=DEFAULT_DEV_USER_ID,
        filename="resnet.pdf",
        title="Deep Residual Learning",
        content_hash="h4",
        file_size_bytes=1000,
        is_persistent=True,
        folder_id=None,
    )
    library_store.add(doc_in_folder)
    library_store.add(doc_other)

    response = await client.get(f"/api/v1/library/documents?folder_id={folder.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["total"] == 1
    assert body["data"][0]["id"] == str(doc_in_folder.id)


@pytest.mark.asyncio
async def test_bulk_import_success(client: AsyncClient) -> None:
    """Bulk import papers with DOI/arXiv IDs queues a batch import task."""
    payload = {
        "identifiers": ["10.1145/3308558.3313562", "1706.03762"],
        "target_folder_id": None,
    }
    response = await client.post("/api/v1/library/documents:bulk-import", json=payload)
    assert response.status_code == 202
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total_items"] == 2
    assert body["data"]["status"] == "queued"
    assert "batch_id" in body["data"]


@pytest.mark.asyncio
async def test_bulk_import_quota_limit(client: AsyncClient) -> None:
    """Bulk import rejects batch sizes exceeding 50 items."""
    identifiers = [f"10.1000/{i}" for i in range(51)]
    payload = {"identifiers": identifiers}
    response = await client.post("/api/v1/library/documents:bulk-import", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_library_synthesize_empty(client: AsyncClient) -> None:
    """Synthesis on an empty library returns an informative response with zero sufficiency."""
    payload = {"query": "Các kiến trúc Transformer?"}
    response = await client.post("/api/v1/library/synthesize", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["sufficiency_score"] == 0.0
    assert body["data"]["sources"] == []


@pytest.mark.asyncio
async def test_library_synthesize_with_grounding(
    client: AsyncClient,
    library_store: InMemoryLibraryStore,
) -> None:
    """Synthesis retrieves grounded sources and includes normalized bounding boxes."""
    doc = DocumentModel(
        user_id=DEFAULT_DEV_USER_ID,
        filename="transformer.pdf",
        title="Attention Is All You Need",
        content_hash="h10",
        file_size_bytes=2000,
        is_persistent=True,
    )
    library_store.add(doc)

    chunk = DocumentChunkModel(
        document_id=doc.id,
        chunk_index=0,
        page_number=1,
        content="The Transformer architecture relies entirely on an attention mechanism.",
        token_count=12,
        bounding_boxes=[[0.1, 0.2, 0.8, 0.25, 1]],
    )
    library_store.add(chunk)

    payload = {"query": "Transformer architecture"}
    response = await client.post("/api/v1/library/synthesize", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["retrieval_tier_reached"] == "tier_3_deep_raw_chunks"
    assert body["data"]["sufficiency_score"] >= 0.50
    assert len(body["data"]["sources"]) > 0
    # Normalized BoundingBox check
    bbox = body["data"]["sources"][0]["bounding_boxes"][0]
    assert len(bbox) == 5
    assert bbox[4] == 1  # 1-indexed page


@pytest.mark.asyncio
async def test_library_compare_success(
    client: AsyncClient,
    library_store: InMemoryLibraryStore,
) -> None:
    """Compare multiple papers returns comparative matrix across columns."""
    doc1 = DocumentModel(
        user_id=DEFAULT_DEV_USER_ID,
        filename="doc1.pdf",
        title="Paper A",
        content_hash="h21",
        file_size_bytes=1000,
        is_persistent=True,
    )
    doc2 = DocumentModel(
        user_id=DEFAULT_DEV_USER_ID,
        filename="doc2.pdf",
        title="Paper B",
        content_hash="h22",
        file_size_bytes=1000,
        is_persistent=True,
    )
    library_store.add(doc1)
    library_store.add(doc2)

    payload = {
        "document_ids": [str(doc1.id), str(doc2.id)],
        "columns": ["Method", "Dataset", "Results"],
    }
    response = await client.post("/api/v1/library/compare", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["columns"] == ["Method", "Dataset", "Results"]
    assert len(body["data"]["documents"]) == 2
    assert str(doc1.id) in body["data"]["comparison_matrix"]
    assert str(doc2.id) in body["data"]["comparison_matrix"]
