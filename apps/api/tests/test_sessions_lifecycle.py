"""Automated integration tests for Research Sessions Lifecycle endpoints (#46 - #51, #55)."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.document import DocumentModel
from api.db.models.session import (
    ResearchSessionModel,
    SessionDocumentModel,
    SessionTurnModel,
)
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import DEFAULT_DEV_USER_ID, get_current_user, get_idempotency_port
from core.adapters.cache.idempotency import InMemoryIdempotencyAdapter
from core.ports.idempotency import IIdempotencyPort
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

OTHER_USER_ID = UUID("99999999-9999-9999-9999-999999999999")


class InMemoryAsyncLifecycleStore:
    """In-memory session store supporting full lifecycle queries and mutations."""

    def __init__(self) -> None:
        self.documents: dict[UUID, DocumentModel] = {}
        self.sessions: dict[UUID, ResearchSessionModel] = {}
        self.session_documents: list[SessionDocumentModel] = []
        self.session_turns: list[SessionTurnModel] = []

    def add(self, obj: object) -> None:
        now = datetime.now(UTC)
        if isinstance(obj, DocumentModel):
            self.documents[obj.id] = obj
        elif isinstance(obj, ResearchSessionModel):
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            if getattr(obj, "updated_at", None) is None:
                obj.updated_at = now
            self.sessions[obj.id] = obj
        elif isinstance(obj, SessionDocumentModel):
            if getattr(obj, "added_at", None) is None:
                obj.added_at = now
            self.session_documents.append(obj)
        elif isinstance(obj, SessionTurnModel):
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            self.session_turns.append(obj)

    async def delete(self, obj: object) -> None:
        if isinstance(obj, ResearchSessionModel):
            self.sessions.pop(obj.id, None)
            self.session_documents = [
                sd for sd in self.session_documents if sd.session_id != obj.id
            ]
            self.session_turns = [st for st in self.session_turns if st.session_id != obj.id]

    async def flush(self) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def refresh(self, obj: object) -> None:
        now = datetime.now(UTC)
        if isinstance(obj, ResearchSessionModel):
            if obj.updated_at is None:
                obj.updated_at = now

    async def execute(self, statement: Any, *args: Any, **kwargs: Any) -> Any:
        stmt_str = str(statement)
        try:
            compiled = statement.compile()
            params = compiled.params or {}
        except Exception:
            params = {}

        # 1. Count queries
        if "count(" in stmt_str.lower():
            mock_res = MagicMock()
            if "research_sessions" in stmt_str:
                matching = [
                    s
                    for s in self.sessions.values()
                    if s.user_id == DEFAULT_DEV_USER_ID and not s.is_archived
                ]
                mock_res.scalar_one.return_value = len(matching)
            elif "session_documents" in stmt_str:
                target_sess_id = None
                for v in params.values():
                    if isinstance(v, UUID) and v in self.sessions:
                        target_sess_id = v
                        break
                matching_sd = [
                    sd for sd in self.session_documents if sd.session_id == target_sess_id
                ]
                mock_res.scalar_one.return_value = len(matching_sd)
            elif "session_turns" in stmt_str:
                mock_res.scalar_one.return_value = len(self.session_turns)
            else:
                mock_res.scalar_one.return_value = 0
            return mock_res

        # 2. Select research_sessions (list or single)
        if "FROM research_sessions" in stmt_str:
            mock_res = MagicMock()
            target_sess_id = None
            for v in params.values():
                if isinstance(v, UUID) and v in self.sessions:
                    target_sess_id = v
                    break

            if target_sess_id:
                sess = self.sessions.get(target_sess_id)
                mock_res.scalar_one_or_none.return_value = sess
                mock_res.scalars.return_value.all.return_value = [sess] if sess else []
            else:
                matching_sessions = [
                    s
                    for s in self.sessions.values()
                    if s.user_id == DEFAULT_DEV_USER_ID and not s.is_archived
                ]
                mock_res.scalars.return_value.all.return_value = matching_sessions
                mock_res.scalar_one_or_none.return_value = (
                    matching_sessions[0] if matching_sessions else None
                )
            return mock_res

        # 3. Select session_documents join documents
        if "session_documents" in stmt_str and "documents" in stmt_str:
            target_sess_id = None
            for v in params.values():
                if isinstance(v, UUID) and v in self.sessions:
                    target_sess_id = v
                    break
            pairs = []
            for sd in self.session_documents:
                match_session = target_sess_id is None or sd.session_id == target_sess_id
                if match_session and sd.document_id in self.documents:
                    pairs.append((sd, self.documents[sd.document_id]))
            mock_res = MagicMock()
            mock_res.all.return_value = pairs
            if "select documents" in stmt_str.lower() or "from documents" in stmt_str.lower():
                mock_res.scalars.return_value.all.return_value = [d for _, d in pairs]
            else:
                mock_res.scalars.return_value.all.return_value = [sd for sd, _ in pairs]
            mock_res.scalar_one_or_none.return_value = pairs[0] if pairs else None
            return mock_res

        # 4. Select documents
        if "FROM documents" in stmt_str:
            target_doc_id = None
            for v in params.values():
                if isinstance(v, UUID) and v in self.documents:
                    target_doc_id = v
                    break
            doc = self.documents.get(target_doc_id)
            mock_res = MagicMock()
            mock_res.scalar_one_or_none.return_value = doc
            mock_res.scalars.return_value.all.return_value = [doc] if doc else []
            return mock_res

        # 5. Select session_documents standalone
        if "FROM session_documents" in stmt_str:
            target_sess_id = None
            target_doc_id = None
            for v in params.values():
                if isinstance(v, UUID):
                    if v in self.sessions:
                        target_sess_id = v
                    elif v in self.documents:
                        target_doc_id = v

            matches = [
                sd
                for sd in self.session_documents
                if (target_sess_id is None or sd.session_id == target_sess_id)
                and (target_doc_id is None or sd.document_id == target_doc_id)
            ]
            mock_res = MagicMock()
            mock_res.scalar_one_or_none.return_value = matches[0] if matches else None
            mock_res.scalars.return_value.all.return_value = matches
            mock_res.all.return_value = [(sd.session_id, len(matches)) for sd in matches]
            return mock_res

        mock_res = MagicMock()
        mock_res.scalars.return_value.all.return_value = []
        mock_res.scalar_one_or_none.return_value = None
        mock_res.scalar_one.return_value = 0
        mock_res.all.return_value = []
        return mock_res


@pytest.fixture
def lifecycle_db() -> InMemoryAsyncLifecycleStore:
    return InMemoryAsyncLifecycleStore()


@pytest.fixture
def test_idempotency_adapter() -> InMemoryIdempotencyAdapter:
    return InMemoryIdempotencyAdapter()


@pytest.fixture
def client(
    lifecycle_db: InMemoryAsyncLifecycleStore,
    test_idempotency_adapter: InMemoryIdempotencyAdapter,
) -> Generator[AsyncClient, None, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield lifecycle_db  # type: ignore[misc]

    async def override_get_current_user() -> UserModel:
        return UserModel(
            id=DEFAULT_DEV_USER_ID,
            email="researcher@verischolar.org",
            full_name="VeriScholar Researcher",
            hashed_password="hash",
            is_active=True,
        )

    def override_get_idempotency() -> IIdempotencyPort:
        return test_idempotency_adapter

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_idempotency_port] = override_get_idempotency

    transport = ASGITransport(app=app)
    async_client = AsyncClient(transport=transport, base_url="http://testserver")
    yield async_client
    app.dependency_overrides.clear()


def _create_mock_session(
    session_id: UUID,
    user_id: UUID,
    title: str = "Attention Is All You Need Study",
    version: int = 1,
    is_archived: bool = False,
) -> ResearchSessionModel:
    return ResearchSessionModel(
        id=session_id,
        user_id=user_id,
        title=title,
        active_document_id=None,
        viewport_state={"page": 1, "zoom_ratio": 1.0, "scroll_top": 0.0},
        active_tab="chat",
        is_archived=is_archived,
        archived_at=None,
        version=version,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def _create_mock_doc(
    doc_id: UUID,
    user_id: UUID,
    title: str = "Attention Is All You Need",
    status: str = "completed",
) -> DocumentModel:
    return DocumentModel(
        id=doc_id,
        user_id=user_id,
        content_hash=f"hash_{doc_id.hex}",
        filename="paper.pdf",
        file_size_bytes=1024,
        page_count=10,
        title=title,
        status=status,
    )


# ==============================================================================
# 46. GET /api/v1/sessions (Sidebar History)
# ==============================================================================
@pytest.mark.asyncio
async def test_list_sessions_sidebar_history_success(
    client: AsyncClient, lifecycle_db: InMemoryAsyncLifecycleStore
) -> None:
    """Endpoint 46: Returns paginated session list for current user."""
    s1 = _create_mock_session(uuid4(), DEFAULT_DEV_USER_ID, "Session Alpha")
    s2 = _create_mock_session(uuid4(), DEFAULT_DEV_USER_ID, "Session Beta")
    lifecycle_db.add(s1)
    lifecycle_db.add(s2)

    resp = await client.get("/api/v1/sessions?page=1&per_page=10")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]) == 2
    assert body["meta"]["page"] == 1
    assert "links" in body


# ==============================================================================
# 47. GET /api/v1/sessions/{id} (Restore Session Snapshot)
# ==============================================================================
@pytest.mark.asyncio
async def test_get_session_detail_snapshot_success(
    client: AsyncClient, lifecycle_db: InMemoryAsyncLifecycleStore
) -> None:
    """Endpoint 47: Retrieves full session state with ETag matching version."""
    s_id = uuid4()
    doc_id = uuid4()
    sess = _create_mock_session(s_id, DEFAULT_DEV_USER_ID, "Detail Session", version=3)
    doc = _create_mock_doc(doc_id, DEFAULT_DEV_USER_ID, "Paper 1")
    lifecycle_db.add(sess)
    lifecycle_db.add(doc)
    lifecycle_db.add(SessionDocumentModel(session_id=s_id, document_id=doc_id, display_order=0))

    resp = await client.get(f"/api/v1/sessions/{s_id}")
    assert resp.status_code == 200
    assert resp.headers["ETag"] == '"v3"'
    body = resp.json()
    assert body["data"]["id"] == str(s_id)
    assert body["data"]["version"] == 3


@pytest.mark.asyncio
async def test_get_session_detail_not_found(client: AsyncClient) -> None:
    """Endpoint 47: 404 when session does not exist."""
    resp = await client.get(f"/api/v1/sessions/{uuid4()}")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "SESSION_NOT_FOUND"


# ==============================================================================
# 48. PATCH /api/v1/sessions/{id} (OCC Title Update)
# ==============================================================================
@pytest.mark.asyncio
async def test_patch_session_metadata_occ_success(
    client: AsyncClient, lifecycle_db: InMemoryAsyncLifecycleStore
) -> None:
    """Endpoint 48: OCC If-Match matching version updates title and increments version."""
    s_id = uuid4()
    sess = _create_mock_session(s_id, DEFAULT_DEV_USER_ID, "Old Title", version=1)
    lifecycle_db.add(sess)

    resp = await client.patch(
        f"/api/v1/sessions/{s_id}",
        json={"title": "New Awesome Research Title"},
        headers={"If-Match": '"v1"'},
    )
    assert resp.status_code == 200
    assert resp.headers["ETag"] == '"v2"'
    assert sess.title == "New Awesome Research Title"
    assert sess.version == 2


@pytest.mark.asyncio
async def test_patch_session_metadata_occ_concurrency_conflict(
    client: AsyncClient, lifecycle_db: InMemoryAsyncLifecycleStore
) -> None:
    """Endpoint 48: 412 Precondition Failed when If-Match does not match current version."""
    s_id = uuid4()
    sess = _create_mock_session(s_id, DEFAULT_DEV_USER_ID, "Title", version=3)
    lifecycle_db.add(sess)

    resp = await client.patch(
        f"/api/v1/sessions/{s_id}",
        json={"title": "Stale Update"},
        headers={"If-Match": '"v1"'},
    )
    assert resp.status_code == 412
    assert resp.json()["error"]["code"] == "CONCURRENCY_CONFLICT"


@pytest.mark.asyncio
async def test_patch_session_metadata_missing_if_match_header(
    client: AsyncClient, lifecycle_db: InMemoryAsyncLifecycleStore
) -> None:
    """Endpoint 48: 428 Precondition Required when If-Match header is omitted."""
    s_id = uuid4()
    sess = _create_mock_session(s_id, DEFAULT_DEV_USER_ID, "Title", version=1)
    lifecycle_db.add(sess)

    resp = await client.patch(
        f"/api/v1/sessions/{s_id}",
        json={"title": "No Header Title"},
    )
    assert resp.status_code == 428
    assert resp.json()["error"]["code"] == "PRECONDITION_REQUIRED"


# ==============================================================================
# 49. PATCH /api/v1/sessions/{id}/viewport (Save Viewport & Active Tab)
# ==============================================================================
@pytest.mark.asyncio
async def test_patch_session_viewport_occ_success(
    client: AsyncClient, lifecycle_db: InMemoryAsyncLifecycleStore
) -> None:
    """Endpoint 49: Updates PDF scroll, zoom ratio, active tab with OCC."""
    s_id = uuid4()
    sess = _create_mock_session(s_id, DEFAULT_DEV_USER_ID, "Viewport Session", version=2)
    lifecycle_db.add(sess)

    payload = {
        "viewport_state": {"page": 5, "zoom_ratio": 1.5, "scroll_top": 450.0},
        "active_tab": "notes",
        "active_document_id": None,
    }
    resp = await client.patch(
        f"/api/v1/sessions/{s_id}/viewport",
        json=payload,
        headers={"If-Match": '"v2"'},
    )
    assert resp.status_code == 200
    assert resp.headers["ETag"] == '"v3"'
    assert sess.viewport_state["page"] == 5
    assert sess.active_tab == "notes"
    assert sess.version == 3


# ==============================================================================
# 50. DELETE /api/v1/sessions/{id} (Delete Session)
# ==============================================================================
@pytest.mark.asyncio
async def test_delete_session_success(
    client: AsyncClient, lifecycle_db: InMemoryAsyncLifecycleStore
) -> None:
    """Endpoint 50: Deleting session returns 204 No Content."""
    s_id = uuid4()
    sess = _create_mock_session(s_id, DEFAULT_DEV_USER_ID, "To Delete")
    lifecycle_db.add(sess)

    resp = await client.delete(f"/api/v1/sessions/{s_id}")
    assert resp.status_code == 204
    assert s_id not in lifecycle_db.sessions


# ==============================================================================
# 51. POST /api/v1/sessions/{id}/documents (Add Document Pure JSON)
# ==============================================================================
@pytest.mark.asyncio
async def test_add_document_to_session_by_id_success(
    client: AsyncClient, lifecycle_db: InMemoryAsyncLifecycleStore
) -> None:
    """Endpoint 51: Adding an existing library document to session returns 202 Accepted."""
    s_id = uuid4()
    doc_id = uuid4()
    sess = _create_mock_session(s_id, DEFAULT_DEV_USER_ID, "Active Session", version=1)
    doc = _create_mock_doc(doc_id, DEFAULT_DEV_USER_ID, "New Paper")
    lifecycle_db.add(sess)
    lifecycle_db.add(doc)

    payload = {"source_type": "document_id", "document_id": str(doc_id)}
    resp = await client.post(f"/api/v1/sessions/{s_id}/documents", json=payload)
    assert resp.status_code == 202
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["document_id"] == str(doc_id)
    assert body["data"]["status"] == "associated"


@pytest.mark.asyncio
async def test_add_document_to_session_by_url_success(
    client: AsyncClient, lifecycle_db: InMemoryAsyncLifecycleStore
) -> None:
    """Endpoint 51: Adding document via external URL queues background download."""
    s_id = uuid4()
    sess = _create_mock_session(s_id, DEFAULT_DEV_USER_ID, "Active Session", version=1)
    lifecycle_db.add(sess)

    payload = {
        "source_type": "url",
        "url": "https://arxiv.org/pdf/1706.03762.pdf",
        "title": "Attention Is All You Need arXiv",
    }
    resp = await client.post(f"/api/v1/sessions/{s_id}/documents", json=payload)
    assert resp.status_code == 202
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["status"] == "queued"


# ==============================================================================
# 55. POST /api/v1/sessions/{id}:restore-archived (Reactivate Expired TTL Session)
# ==============================================================================
@pytest.mark.asyncio
async def test_restore_archived_session_success(
    client: AsyncClient, lifecycle_db: InMemoryAsyncLifecycleStore
) -> None:
    """Endpoint 55: Re-uploading valid PDF binary restores archived session."""
    s_id = uuid4()
    sess = _create_mock_session(s_id, DEFAULT_DEV_USER_ID, "Archived Session", is_archived=True)
    lifecycle_db.add(sess)

    pdf_bytes = b"%PDF-1.4\n%mock content\n%%EOF"
    files = {"file": ("original_paper.pdf", pdf_bytes, "application/pdf")}

    resp = await client.post(f"/api/v1/sessions/{s_id}:restore-archived", files=files)
    assert resp.status_code == 200
    assert sess.is_archived is False
    assert resp.json()["data"]["is_archived"] is False


@pytest.mark.asyncio
async def test_restore_archived_session_invalid_pdf_header(
    client: AsyncClient, lifecycle_db: InMemoryAsyncLifecycleStore
) -> None:
    """Endpoint 55: Uploading non-PDF file rejects with 400 INVALID_PDF_HEADER."""
    s_id = uuid4()
    sess = _create_mock_session(s_id, DEFAULT_DEV_USER_ID, "Archived Session", is_archived=True)
    lifecycle_db.add(sess)

    txt_bytes = b"This is a plain text file, not a PDF."
    files = {"file": ("not_a_pdf.txt", txt_bytes, "text/plain")}

    resp = await client.post(f"/api/v1/sessions/{s_id}:restore-archived", files=files)
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_PDF_HEADER"
