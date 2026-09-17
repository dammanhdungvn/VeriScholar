"""Automated integration tests for POST /api/v1/sessions endpoint (#45)."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.document import DocumentModel
from api.db.models.session import ResearchSessionModel, SessionDocumentModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import DEFAULT_DEV_USER_ID, get_current_user, get_idempotency_port
from core.adapters.cache.idempotency import InMemoryIdempotencyAdapter
from core.ports.idempotency import IIdempotencyPort
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

OTHER_USER_ID = UUID("99999999-9999-9999-9999-999999999999")


class InMemoryAsyncSessionStore:
    """Fast, deterministic in-memory session test double for research sessions."""

    def __init__(self) -> None:
        self.documents: dict[UUID, DocumentModel] = {}
        self.sessions: dict[UUID, ResearchSessionModel] = {}
        self.session_documents: list[SessionDocumentModel] = []
        self._added: list[object] = []

    def add(self, obj: object) -> None:
        self._added.append(obj)
        if isinstance(obj, DocumentModel):
            self.documents[obj.id] = obj
        elif isinstance(obj, ResearchSessionModel):
            self.sessions[obj.id] = obj
        elif isinstance(obj, SessionDocumentModel):
            self.session_documents.append(obj)

    async def flush(self) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def refresh(self, obj: object) -> None:
        now = datetime.now(UTC)
        if isinstance(obj, ResearchSessionModel):
            if obj.created_at is None:
                obj.created_at = now
            if obj.updated_at is None:
                obj.updated_at = now

    async def execute(self, statement: Any, *args: Any, **kwargs: Any) -> Any:
        """Mock SQL select execution for documents and sessions."""
        stmt_str = str(statement)
        try:
            compiled = statement.compile()  # type: ignore[union-attr]
            params = compiled.params or {}
        except Exception:
            params = {}

        if "FROM documents" in stmt_str:
            # SELECT documents.* FROM documents WHERE documents.id IN (...) AND user_id = :id
            target_user_id = None
            for k, v in params.items():
                if "user_id" in k and isinstance(v, UUID):
                    target_user_id = v
                    break

            candidate_ids: list[UUID] = []
            for k, v in params.items():
                if "id" in k and isinstance(v, (list, tuple, set)):
                    candidate_ids.extend([x for x in v if isinstance(x, UUID)])

            matching = [
                doc
                for doc in self.documents.values()
                if doc.id in candidate_ids and doc.user_id == target_user_id
            ]
            mock_res = MagicMock()
            mock_res.scalars.return_value.all.return_value = matching
            return mock_res

        mock_res = MagicMock()
        mock_res.scalars.return_value.all.return_value = []
        return mock_res


@pytest.fixture
def memory_db() -> InMemoryAsyncSessionStore:
    """Fixture providing a fresh in-memory session store."""
    return InMemoryAsyncSessionStore()


@pytest.fixture
def test_idempotency_adapter() -> InMemoryIdempotencyAdapter:
    """Fixture providing clean in-memory idempotency adapter."""
    return InMemoryIdempotencyAdapter()


@pytest.fixture
def client(
    memory_db: InMemoryAsyncSessionStore,
    test_idempotency_adapter: InMemoryIdempotencyAdapter,
) -> Generator[AsyncClient, None, None]:
    """Test client configured with in-memory double and clean dependencies."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield memory_db  # type: ignore[misc]

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
        filename=f"{doc_id.hex[:8]}.pdf",
        file_size_bytes=102400,
        page_count=10,
        title=title,
        status=status,
    )


@pytest.mark.asyncio
async def test_create_empty_session_success(
    client: AsyncClient, memory_db: InMemoryAsyncSessionStore
) -> None:
    """Case 1: Creating an empty session returns 201 Created with Location & ETag headers."""
    payload = {
        "title": "Phiên đọc tài liệu AI",
        "initial_document_ids": [],
    }
    resp = await client.post("/api/v1/sessions", json=payload)

    assert resp.status_code == 201
    assert "Location" in resp.headers
    assert resp.headers["ETag"] == '"v1"'

    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["title"] == "Phiên đọc tài liệu AI"
    assert data["document_ids"] == []
    assert data["active_document_id"] is None
    assert data["version"] == 1
    assert data["active_tab"] == "chat"
    assert data["viewport_state"]["page"] == 1
    assert data["viewport_state"]["zoom_ratio"] == 1.0


@pytest.mark.asyncio
async def test_create_session_with_valid_documents_success(
    client: AsyncClient, memory_db: InMemoryAsyncSessionStore
) -> None:
    """Case 2: Creating a session with valid documents assigns active_document_id to first doc."""
    doc1_id = uuid4()
    doc2_id = uuid4()
    doc3_id = uuid4()

    memory_db.add(_create_mock_doc(doc1_id, DEFAULT_DEV_USER_ID, "Doc 1"))
    memory_db.add(_create_mock_doc(doc2_id, DEFAULT_DEV_USER_ID, "Doc 2"))
    memory_db.add(_create_mock_doc(doc3_id, DEFAULT_DEV_USER_ID, "Doc 3"))

    payload = {
        "title": "Nghiên cứu Transformer & Attention",
        "initial_document_ids": [str(doc1_id), str(doc2_id), str(doc3_id)],
    }
    resp = await client.post("/api/v1/sessions", json=payload)

    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["title"] == "Nghiên cứu Transformer & Attention"
    assert len(data["document_ids"]) == 3
    assert data["active_document_id"] == str(doc1_id)
    assert len(memory_db.session_documents) == 3
    assert memory_db.session_documents[0].display_order == 0
    assert memory_db.session_documents[1].display_order == 1
    assert memory_db.session_documents[2].display_order == 2


@pytest.mark.asyncio
async def test_create_session_exceeds_capacity_failure(
    client: AsyncClient, memory_db: InMemoryAsyncSessionStore
) -> None:
    """Case 3: Exceeding 5 documents returns 400 Bad Request with SESSION_CAPACITY_EXCEEDED."""
    doc_ids = [uuid4() for _ in range(6)]
    for d in doc_ids:
        memory_db.add(_create_mock_doc(d, DEFAULT_DEV_USER_ID))

    payload = {
        "title": "Over Capacity Session",
        "initial_document_ids": [str(d) for d in doc_ids],
    }
    resp = await client.post("/api/v1/sessions", json=payload)

    assert resp.status_code == 400
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "SESSION_CAPACITY_EXCEEDED"
    assert "tối đa chỉ chứa 5 bài báo" in body["error"]["message"]


@pytest.mark.asyncio
async def test_create_session_with_duplicate_documents(
    client: AsyncClient, memory_db: InMemoryAsyncSessionStore
) -> None:
    """Case 4: Duplicate document IDs are deduplicated preserving initial order."""
    doc1_id = uuid4()
    doc2_id = uuid4()
    memory_db.add(_create_mock_doc(doc1_id, DEFAULT_DEV_USER_ID))
    memory_db.add(_create_mock_doc(doc2_id, DEFAULT_DEV_USER_ID))

    payload = {
        "title": "Duplicate Document Deduplication Test",
        "initial_document_ids": [str(doc1_id), str(doc1_id), str(doc2_id)],
    }
    resp = await client.post("/api/v1/sessions", json=payload)

    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["document_ids"] == [str(doc1_id), str(doc2_id)]
    assert data["active_document_id"] == str(doc1_id)


@pytest.mark.asyncio
async def test_create_session_with_nonexistent_document(
    client: AsyncClient, memory_db: InMemoryAsyncSessionStore
) -> None:
    """Case 5: Submitting a non-existent document ID returns 404 DOCUMENT_NOT_FOUND."""
    non_existent = uuid4()
    payload = {
        "title": "Non-existent Document Test",
        "initial_document_ids": [str(non_existent)],
    }
    resp = await client.post("/api/v1/sessions", json=payload)

    assert resp.status_code == 404
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_create_session_multi_tenant_isolation(
    client: AsyncClient, memory_db: InMemoryAsyncSessionStore
) -> None:
    """Case 6: Trying to associate a document belonging to another user returns 404."""
    other_doc_id = uuid4()
    memory_db.add(_create_mock_doc(other_doc_id, OTHER_USER_ID, "Secret Paper"))

    payload = {
        "title": "Tenant Breach Attempt",
        "initial_document_ids": [str(other_doc_id)],
    }
    resp = await client.post("/api/v1/sessions", json=payload)

    assert resp.status_code == 404
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_create_session_invalid_title(client: AsyncClient) -> None:
    """Case 7: Whitespace-only title returns 422 Unprocessable Entity."""
    payload = {"title": "   "}
    resp = await client.post("/api/v1/sessions", json=payload)
    assert resp.status_code == 422

    payload_empty = {"title": ""}
    resp_empty = await client.post("/api/v1/sessions", json=payload_empty)
    assert resp_empty.status_code == 422


@pytest.mark.asyncio
async def test_create_session_title_too_long(client: AsyncClient) -> None:
    """Case 8: Title exceeding 255 characters returns 422 Unprocessable Entity."""
    payload = {"title": "X" * 256}
    resp = await client.post("/api/v1/sessions", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_session_auto_naming_fallback_with_documents(
    client: AsyncClient, memory_db: InMemoryAsyncSessionStore
) -> None:
    """Case 9: Omitting title auto-generates title from first paper."""
    doc_id = uuid4()
    memory_db.add(_create_mock_doc(doc_id, DEFAULT_DEV_USER_ID, "Attention Is All You Need"))

    payload = {
        "initial_document_ids": [str(doc_id)],
    }
    resp = await client.post("/api/v1/sessions", json=payload)

    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["title"] == "Nghiên cứu: Attention Is All You Need"


@pytest.mark.asyncio
async def test_create_session_auto_naming_fallback_empty_session(
    client: AsyncClient,
) -> None:
    """Case 10: Omitting title on empty session auto-generates title with timestamp."""
    resp = await client.post("/api/v1/sessions", json={})

    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["title"].startswith("Phiên nghiên cứu ")


@pytest.mark.asyncio
async def test_create_session_idempotency_cache_hit(
    client: AsyncClient, memory_db: InMemoryAsyncSessionStore
) -> None:
    """Case 11: Idempotency-Key returns cached session on replay with X-Cache header."""
    idempotency_key = str(uuid4())
    headers = {"Idempotency-Key": idempotency_key}
    payload = {"title": "Idempotency Protected Session"}

    # First call
    resp1 = await client.post("/api/v1/sessions", json=payload, headers=headers)
    assert resp1.status_code == 201
    data1 = resp1.json()["data"]

    # Second call with same key
    resp2 = await client.post("/api/v1/sessions", json=payload, headers=headers)
    assert resp2.status_code == 200
    assert resp2.headers.get("X-Cache") == "Idempotent-Hit"
    data2 = resp2.json()["data"]
    assert data1["id"] == data2["id"]
    assert data1["title"] == data2["title"]


@pytest.mark.asyncio
async def test_create_session_include_documents_metadata(
    client: AsyncClient, memory_db: InMemoryAsyncSessionStore
) -> None:
    """Case 12: include_documents=true embeds document metadata."""
    doc_id = uuid4()
    memory_db.add(_create_mock_doc(doc_id, DEFAULT_DEV_USER_ID, "BERT Paper", status="completed"))

    payload = {
        "title": "BERT Study",
        "initial_document_ids": [str(doc_id)],
    }
    resp = await client.post("/api/v1/sessions?include_documents=true", json=payload)

    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["documents"] is not None
    assert len(data["documents"]) == 1
    doc_item = data["documents"][0]
    assert doc_item["id"] == str(doc_id)
    assert doc_item["title"] == "BERT Paper"
    assert doc_item["status"] == "completed"
    assert doc_item["display_order"] == 0


@pytest.mark.asyncio
async def test_create_session_warnings_for_uncompleted_documents(
    client: AsyncClient, memory_db: InMemoryAsyncSessionStore
) -> None:
    """Case 13: Documents in processing or failed status generate advisory warnings."""
    doc_id = uuid4()
    memory_db.add(
        _create_mock_doc(doc_id, DEFAULT_DEV_USER_ID, "Processing Paper", status="processing")
    )

    payload = {
        "title": "Warning Session",
        "initial_document_ids": [str(doc_id)],
    }
    resp = await client.post("/api/v1/sessions", json=payload)

    assert resp.status_code == 201
    data = resp.json()["data"]
    assert len(data["warnings"]) == 1
    assert "đang ở trạng thái 'processing'" in data["warnings"][0]
