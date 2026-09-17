"""Automated integration tests for Research Notes CRUD & OCC endpoints (#16 - #20)."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.document import DocumentModel
from api.db.models.note import ResearchNoteModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import DEFAULT_DEV_USER_ID, get_current_user
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

OTHER_USER_ID = UUID("99999999-9999-9999-9999-999999999999")


class InMemoryNotesStore:
    """In-memory store for research notes testing."""

    def __init__(self) -> None:
        self.documents: dict[UUID, DocumentModel] = {}
        self.notes: dict[UUID, ResearchNoteModel] = {}

    def add(self, obj: object) -> None:
        now = datetime.now(UTC)
        if isinstance(obj, DocumentModel):
            self.documents[obj.id] = obj
        elif isinstance(obj, ResearchNoteModel):
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            if getattr(obj, "updated_at", None) is None:
                obj.updated_at = now
            self.notes[obj.id] = obj

    async def delete(self, obj: object) -> None:
        if isinstance(obj, ResearchNoteModel):
            self.notes.pop(obj.id, None)

    async def flush(self) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def refresh(self, obj: object) -> None:
        now = datetime.now(UTC)
        if isinstance(obj, ResearchNoteModel):
            if obj.updated_at is None:
                obj.updated_at = now

    async def execute(self, statement: Any, *args: Any, **kwargs: Any) -> Any:
        stmt_str = str(statement)
        try:
            compiled = statement.compile()
            params = compiled.params or {}
        except Exception:
            params = {}

        # 1. Count queries (explicit count( function to avoid matching page_count column)
        if "count(" in stmt_str.lower():
            mock_res = MagicMock()
            matching = [n for n in self.notes.values() if n.user_id == DEFAULT_DEV_USER_ID]
            mock_res.scalar_one.return_value = len(matching)
            return mock_res

        # 2. Select document by id
        if "FROM documents" in stmt_str:
            mock_res = MagicMock()
            target_doc_id = None
            for v in params.values():
                if isinstance(v, UUID) and v in self.documents:
                    target_doc_id = v
                    break
            doc = self.documents.get(target_doc_id) if target_doc_id else None
            mock_res.scalar_one_or_none.return_value = doc
            mock_res.scalars.return_value.all.return_value = [doc] if doc else []
            return mock_res

        # 3. Select chunk (none for simple tests)
        if "FROM document_chunks" in stmt_str:
            mock_res = MagicMock()
            mock_res.scalar_one_or_none.return_value = None
            return mock_res

        # 4. Select research_notes
        if "FROM research_notes" in stmt_str:
            mock_res = MagicMock()
            target_note_id = None
            for v in params.values():
                if isinstance(v, UUID) and v in self.notes:
                    target_note_id = v
                    break

            if target_note_id:
                note = self.notes.get(target_note_id)
                mock_res.scalar_one_or_none.return_value = note
                mock_res.scalars.return_value.all.return_value = [note] if note else []
            else:
                user_notes = [n for n in self.notes.values() if n.user_id == DEFAULT_DEV_USER_ID]
                mock_res.scalars.return_value.all.return_value = user_notes
                mock_res.scalar_one_or_none.return_value = user_notes[0] if user_notes else None
            return mock_res

        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = None
        mock_res.scalars.return_value.all.return_value = []
        return mock_res


@pytest.fixture
def notes_store() -> InMemoryNotesStore:
    return InMemoryNotesStore()


@pytest.fixture
def mock_db_session(notes_store: InMemoryNotesStore) -> AsyncSession:
    return notes_store  # type: ignore[return-value]


@pytest.fixture
def sample_document(notes_store: InMemoryNotesStore) -> DocumentModel:
    doc = DocumentModel(
        id=uuid4(),
        user_id=DEFAULT_DEV_USER_ID,
        filename="attention_is_all_you_need.pdf",
        title="Attention Is All You Need",
        authors=["Ashish Vaswani", "Noam Shazeer"],
        publication_year=2017,
        doi="10.48550/arXiv.1706.03762",
        content_hash="a" * 64,
        file_size_bytes=1024 * 1024,
        status="parsed",
        progress=100,
        parsed_metadata={"arxiv_id": "1706.03762"},
    )
    notes_store.add(doc)
    return doc


@pytest.fixture
def default_user() -> UserModel:
    return UserModel(
        id=DEFAULT_DEV_USER_ID,
        email="developer@verischolar.org",
        full_name="VeriScholar Developer",
        hashed_password="dummy",
        is_active=True,
    )


@pytest.fixture
def client(
    mock_db_session: AsyncSession, default_user: UserModel
) -> Generator[AsyncClient, None, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield mock_db_session

    async def override_get_current_user() -> UserModel:
        return default_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)
    async_client = AsyncClient(transport=transport, base_url="http://testserver")
    yield async_client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_note_with_document_success(
    client: AsyncClient, sample_document: DocumentModel
) -> None:
    """POST /api/v1/notes successfully saves quote with frozen evidence snapshot."""
    payload = {
        "document_id": str(sample_document.id),
        "selected_text": (
            "The dominant sequence transduction models are based on "
            "complex recurrent or convolutional neural networks."
        ),
        "bounding_boxes": [[0.15, 0.2, 0.3, 0.8, 1]],
        "page_number": 1,
        "user_note": "Bối cảnh nghiên cứu trước khi có Transformer.",
        "tags": ["background", "rnn-limitation"],
    }
    resp = await client.post("/api/v1/notes", json=payload)
    assert resp.status_code == 201

    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["selected_text"] == payload["selected_text"]
    assert data["page_number"] == 1
    assert data["version"] == 1
    assert data["is_source_detached"] is False
    assert resp.headers["ETag"] == '"v1"'
    assert resp.headers["Location"] == f"/api/v1/notes/{data['id']}"

    # Verify frozen snapshot preservation
    snapshot = data["frozen_snapshot"]
    assert snapshot["document_id"] == str(sample_document.id)
    assert snapshot["document_title"] == sample_document.title
    assert "Ashish Vaswani" in snapshot["authors"]
    assert snapshot["year"] == 2017


@pytest.mark.asyncio
async def test_create_free_note_without_document(client: AsyncClient) -> None:
    """POST /api/v1/notes creates free memo without attaching document_id."""
    payload = {
        "selected_text": "Ý tưởng: Thử nghiệm kỹ thuật cross-attention trên mô hình thị giác.",
        "page_number": 1,
        "tags": ["idea", "future-work"],
    }
    resp = await client.post("/api/v1/notes", json=payload)
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["document_id"] is None
    assert data["frozen_snapshot"]["document_title"] == "Ghi chú tự do (Không đính kèm văn bản)"


@pytest.mark.asyncio
async def test_create_note_non_existent_document_fails(client: AsyncClient) -> None:
    """POST /api/v1/notes returns 404 when referenced document does not exist."""
    payload = {
        "document_id": str(uuid4()),
        "selected_text": "Some text",
        "page_number": 1,
    }
    resp = await client.post("/api/v1/notes", json=payload)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_create_note_empty_text_fails(client: AsyncClient) -> None:
    """POST /api/v1/notes returns 422 on empty selected_text."""
    resp = await client.post("/api/v1/notes", json={"selected_text": ""})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_notes(
    client: AsyncClient, notes_store: InMemoryNotesStore, sample_document: DocumentModel
) -> None:
    """GET /api/v1/notes returns paginated envelope."""
    # Pre-populate 2 notes
    n1 = ResearchNoteModel(
        id=uuid4(),
        user_id=DEFAULT_DEV_USER_ID,
        document_id=sample_document.id,
        selected_text="Quote 1",
        bounding_boxes=[],
        page_number=1,
        tags=["tag1"],
        frozen_snapshot={"document_title": sample_document.title},
        version=1,
    )
    n2 = ResearchNoteModel(
        id=uuid4(),
        user_id=DEFAULT_DEV_USER_ID,
        document_id=sample_document.id,
        selected_text="Quote 2",
        bounding_boxes=[],
        page_number=2,
        tags=["tag2"],
        frozen_snapshot={"document_title": sample_document.title},
        version=1,
    )
    notes_store.add(n1)
    notes_store.add(n2)

    resp = await client.get("/api/v1/notes?page=1&per_page=10")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "data" in body
    assert "meta" in body
    assert "links" in body
    assert len(body["data"]) == 2


@pytest.mark.asyncio
async def test_get_note_by_id(
    client: AsyncClient, notes_store: InMemoryNotesStore, sample_document: DocumentModel
) -> None:
    """GET /api/v1/notes/{id} returns full note with snapshot and ETag."""
    note_id = uuid4()
    n = ResearchNoteModel(
        id=note_id,
        user_id=DEFAULT_DEV_USER_ID,
        document_id=sample_document.id,
        selected_text="Self-attention mechanism",
        bounding_boxes=[[0.1, 0.1, 0.2, 0.5, 3]],
        page_number=3,
        user_note="Điểm mấu chốt",
        tags=["attention"],
        frozen_snapshot={"document_title": sample_document.title},
        version=1,
    )
    notes_store.add(n)

    resp = await client.get(f"/api/v1/notes/{note_id}")
    assert resp.status_code == 200
    assert resp.headers["ETag"] == '"v1"'
    data = resp.json()["data"]
    assert data["id"] == str(note_id)
    assert data["selected_text"] == "Self-attention mechanism"


@pytest.mark.asyncio
async def test_update_note_occ_protocol(
    client: AsyncClient, notes_store: InMemoryNotesStore, sample_document: DocumentModel
) -> None:
    """PATCH /api/v1/notes/{id} enforces strict OCC: 428 missing, 412 mismatch, 200 match."""
    note_id = uuid4()
    n = ResearchNoteModel(
        id=note_id,
        user_id=DEFAULT_DEV_USER_ID,
        document_id=sample_document.id,
        selected_text="Formula text",
        bounding_boxes=[],
        page_number=1,
        user_note="Old note",
        tags=["old"],
        frozen_snapshot={},
        version=1,
    )
    notes_store.add(n)

    # 1. Missing If-Match -> 428 Precondition Required
    resp_no_header = await client.patch(
        f"/api/v1/notes/{note_id}",
        json={"user_note": "New note"},
    )
    assert resp_no_header.status_code == 428
    assert resp_no_header.json()["error"]["code"] == "PRECONDITION_REQUIRED"

    # 2. Version Mismatch -> 412 Precondition Failed
    resp_mismatch = await client.patch(
        f"/api/v1/notes/{note_id}",
        headers={"If-Match": '"v99"'},
        json={"user_note": "New note"},
    )
    assert resp_mismatch.status_code == 412
    assert resp_mismatch.json()["error"]["code"] == "CONCURRENCY_CONFLICT"

    # 3. Correct Version -> 200 OK + new ETag "v2"
    resp_success = await client.patch(
        f"/api/v1/notes/{note_id}",
        headers={"If-Match": '"v1"'},
        json={"user_note": "New note", "tags": ["updated", "formula"]},
    )
    assert resp_success.status_code == 200
    assert resp_success.headers["ETag"] == '"v2"'
    data = resp_success.json()["data"]
    assert data["version"] == 2
    assert data["user_note"] == "New note"
    assert "updated" in data["tags"]


@pytest.mark.asyncio
async def test_delete_note_idempotent(client: AsyncClient, notes_store: InMemoryNotesStore) -> None:
    """DELETE /api/v1/notes/{id} returns 204 idempotently."""
    note_id = uuid4()
    n = ResearchNoteModel(
        id=note_id,
        user_id=DEFAULT_DEV_USER_ID,
        document_id=None,
        selected_text="Delete me",
        bounding_boxes=[],
        page_number=1,
        version=1,
    )
    notes_store.add(n)

    resp = await client.delete(f"/api/v1/notes/{note_id}")
    assert resp.status_code == 204
    assert len(resp.content) == 0

    # Idempotent re-delete also returns 204
    resp_redelete = await client.delete(f"/api/v1/notes/{note_id}")
    assert resp_redelete.status_code == 204
