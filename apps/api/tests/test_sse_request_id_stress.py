"""Empirical Stress Test Suite for SSE Streaming & X-Request-ID Header Standardization.

Conducted by Challenger Agent for Milestone 1 (M1_SSE_TRACING).
Tests all 4 challenge dimensions:
1. No X-Request-ID -> server generates valid UUID4 and propagates across endpoints.
2. Custom X-Request-ID -> exact echo in headers and initial SSE payloads.
3. Uppercase X-REQUEST-ID & duplicates -> exactly one canonical lowercase x-request-id.
4. Deep SSE event stream chunk parsing & payload validation (summary_start, start, error).
"""

import json
from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pymupdf
import pytest
from api import app
from api.db.models.chunk import DocumentChunkModel
from api.db.models.document import DocumentModel
from api.db.models.session import (
    ResearchSessionModel,
    SessionDocumentModel,
    SessionTurnModel,
)
from api.db.models.summary import DocumentSummaryModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import (
    DEFAULT_DEV_USER_ID,
    get_current_user,
    get_document_service,
    get_idempotency_port,
)
from api.services.document_service import DocumentService
from core.adapters.cache.idempotency import InMemoryIdempotencyAdapter
from core.ports.storage import IBlobStoragePort
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class InMemoryAsyncStressDb:
    """In-memory database test double for empirical stress testing."""

    def __init__(self) -> None:
        self.documents: dict[UUID, DocumentModel] = {}
        self.chunks: list[DocumentChunkModel] = []
        self.summaries: dict[UUID, DocumentSummaryModel] = {}
        self.sessions: dict[UUID, ResearchSessionModel] = {}
        self.session_documents: list[SessionDocumentModel] = []
        self.session_turns: list[SessionTurnModel] = []

    def add(self, obj: object) -> None:
        now = datetime.now(UTC)
        if isinstance(obj, DocumentModel):
            self.documents[obj.id] = obj
        elif isinstance(obj, DocumentChunkModel):
            self.chunks.append(obj)
        elif isinstance(obj, DocumentSummaryModel):
            self.summaries[obj.document_id] = obj
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

    def add_all(self, objs: list[Any]) -> None:
        for obj in objs:
            self.add(obj)

    async def flush(self) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def refresh(self, obj: object) -> None:
        pass

    async def execute(self, statement: Any, *args: Any, **kwargs: Any) -> Any:
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
                if "user_id" in k:
                    target_user_id = v
                elif "id" in k and isinstance(v, UUID):
                    target_id = v

            doc = None
            if target_id and target_id in self.documents:
                cand = self.documents[target_id]
                if target_user_id is None or cand.user_id == target_user_id:
                    doc = cand
            result_mock.scalar_one_or_none.return_value = doc
            return result_mock

        # 2. DocumentSummaryModel lookup
        if "FROM document_summaries" in statement_str:
            target_doc_id = None
            for k, v in params.items():
                if "document_id" in k and isinstance(v, UUID):
                    target_doc_id = v
            summary = self.summaries.get(target_doc_id) if target_doc_id else None
            result_mock.scalar_one_or_none.return_value = summary
            return result_mock

        # 3. DocumentChunkModel lookup
        if "FROM document_chunks" in statement_str:
            target_doc_id = None
            for k, v in params.items():
                if "document_id" in k and isinstance(v, UUID):
                    target_doc_id = v
            matched_chunks = [c for c in self.chunks if c.document_id == target_doc_id]
            scalars_mock = MagicMock()
            scalars_mock.all.return_value = matched_chunks
            result_mock.scalars.return_value = scalars_mock
            return result_mock

        # 4. ResearchSessionModel lookup
        if "FROM research_sessions" in statement_str:
            target_sess_id = None
            for k, v in params.items():
                if "id" in k and isinstance(v, UUID):
                    target_sess_id = v
                    break
            sess = self.sessions.get(target_sess_id) if target_sess_id else None
            result_mock.scalar_one_or_none.return_value = sess
            return result_mock

        # 5. SessionDocumentModel lookup
        if "FROM session_documents" in statement_str:
            target_sess_id = None
            for k, v in params.items():
                if "session_id" in k and isinstance(v, UUID):
                    target_sess_id = v
                    break
            docs = [
                sd.document_id for sd in self.session_documents if sd.session_id == target_sess_id
            ]
            scalars_mock = MagicMock()
            scalars_mock.all.return_value = docs
            result_mock.scalars.return_value = scalars_mock
            return result_mock

        # 6. SessionTurnModel queries
        if "FROM session_turns" in statement_str:
            scalars_mock = MagicMock()
            scalars_mock.all.return_value = list(self.session_turns)
            result_mock.scalars.return_value = scalars_mock
            return result_mock

        result_mock.scalar_one_or_none.return_value = None
        result_mock.scalars.return_value.all.return_value = []
        return result_mock


class MockBlobStorage(IBlobStoragePort):
    """In-memory mock blob storage for stress test environment."""

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

    async def blob_exists(self, content_hash: str) -> bool:
        return content_hash in self.blobs

    async def delete(self, content_hash: str) -> bool:
        if content_hash in self.blobs:
            del self.blobs[content_hash]
            return True
        return False


def _create_sample_pdf_bytes() -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text(
        (50, 72),
        "Attention Is All You Need\n\n"
        "Dominant sequence models suffer from compute bottlenecks.\n"
        "We propose Transformer.\n"
        "Limitation is quadratic complexity.\n",
    )
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


def _parse_sse_events(raw_body: str) -> list[dict[str, Any]]:
    """Parse raw SSE text into structured list of event records."""
    events: list[dict[str, Any]] = []
    chunks = raw_body.strip().split("\n\n")
    for chunk in chunks:
        if not chunk.strip():
            continue
        event_dict: dict[str, Any] = {"id": None, "event": None, "data": None}
        for line in chunk.splitlines():
            if line.startswith("id: "):
                event_dict["id"] = line.removeprefix("id: ").strip()
            elif line.startswith("event: "):
                event_dict["event"] = line.removeprefix("event: ").strip()
            elif line.startswith("data: "):
                data_str = line.removeprefix("data: ").strip()
                try:
                    event_dict["data"] = json.loads(data_str)
                except Exception:
                    event_dict["data"] = data_str
        events.append(event_dict)
    return events


def _assert_valid_uuid4(val: str) -> None:
    """Empirically assert string is valid RFC 4122 version 4 UUID."""
    assert val is not None, "UUID value must not be None"
    parsed = UUID(val)
    assert parsed.version == 4, f"Expected UUID version 4, got version {parsed.version}"


@pytest.fixture
def stress_db() -> InMemoryAsyncStressDb:
    return InMemoryAsyncStressDb()


@pytest.fixture
def test_user() -> UserModel:
    return UserModel(
        id=DEFAULT_DEV_USER_ID,
        email="developer@verischolar.org",
        full_name="VeriScholar Developer",
        hashed_password="hash",
        is_active=True,
    )


@pytest.fixture
def sample_document(stress_db: InMemoryAsyncStressDb) -> DocumentModel:
    doc_id = uuid4()
    now = datetime.now(UTC)
    doc = DocumentModel(
        id=doc_id,
        user_id=DEFAULT_DEV_USER_ID,
        blob_id=None,
        filename="attention.pdf",
        title="Attention Is All You Need",
        content_hash="stress_summary_hash",
        file_size_bytes=1024,
        status="completed",
        stage="completed",
        progress=100,
        chunk_count=2,
        is_persistent=True,
        created_at=now,
        updated_at=now,
    )
    stress_db.add(doc)

    c1 = DocumentChunkModel(
        id=uuid4(),
        document_id=doc_id,
        chunk_index=0,
        page_number=1,
        content="Dominant sequence models suffer from compute bottlenecks.",
        bounding_boxes=[[0.1, 0.1, 0.9, 0.2, 1]],
        token_count=12,
        created_at=now,
        updated_at=now,
    )
    c2 = DocumentChunkModel(
        id=uuid4(),
        document_id=doc_id,
        chunk_index=1,
        page_number=1,
        content="We propose Transformer.",
        bounding_boxes=[[0.1, 0.3, 0.9, 0.4, 1]],
        token_count=10,
        created_at=now,
        updated_at=now,
    )
    stress_db.add(c1)
    stress_db.add(c2)

    summary = DocumentSummaryModel(
        id=uuid4(),
        document_id=doc_id,
        problem_statement="Sequence models suffer from bottlenecks.",
        problem_citations=[[0.1, 0.1, 0.9, 0.2, 1]],
        contributions="We propose Transformer.",
        contribution_citations=[[0.1, 0.3, 0.9, 0.4, 1]],
        limitations="Quadratic memory complexity remains a drawback.",
        limitation_citations=[[0.1, 0.5, 0.9, 0.6, 1]],
        total_tokens=42,
        latency_ms=5,
        created_at=now,
        updated_at=now,
    )
    stress_db.add(summary)
    return doc


@pytest.fixture
def sample_session(stress_db: InMemoryAsyncStressDb) -> ResearchSessionModel:
    s_id = uuid4()
    now = datetime.now(UTC)
    sess = ResearchSessionModel(
        id=s_id,
        user_id=DEFAULT_DEV_USER_ID,
        title="Stress Test Chat Session",
        active_document_id=None,
        viewport_state={"page": 1, "zoom_ratio": 1.0, "scroll_top": 0.0},
        active_tab="chat",
        is_archived=False,
        archived_at=None,
        version=1,
        created_at=now,
        updated_at=now,
    )
    stress_db.add(sess)
    return sess


@pytest.fixture
def client(
    stress_db: InMemoryAsyncStressDb,
    test_user: UserModel,
) -> Generator[AsyncClient, None, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield stress_db  # type: ignore[misc]

    async def override_get_current_user() -> UserModel:
        return test_user

    mock_storage = MockBlobStorage()
    mock_storage.blobs["stress_summary_hash"] = _create_sample_pdf_bytes()
    idempotency_adapter = InMemoryIdempotencyAdapter()
    service = DocumentService(storage=mock_storage)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_document_service] = lambda: service
    app.dependency_overrides[get_idempotency_port] = lambda: idempotency_adapter

    transport = ASGITransport(app=app)
    async_client = AsyncClient(transport=transport, base_url="http://testserver")

    yield async_client

    app.dependency_overrides.clear()


# ==============================================================================
# DIMENSION 1: NO X-Request-ID Header -> Valid UUID4 Generated and Propagated
# ==============================================================================
@pytest.mark.asyncio
async def test_dim1_events_no_request_id_generates_valid_uuid4(client: AsyncClient) -> None:
    """GET /events with NO X-Request-ID: server returns UUID4 header and in SSE payload."""
    resp = await client.get("/events")
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
    assert "x-request-id" in resp.headers

    req_id = resp.headers["x-request-id"]
    _assert_valid_uuid4(req_id)

    events = _parse_sse_events(resp.text)
    assert len(events) >= 3
    for ev in events:
        assert ev["event"] == "progress"
        assert isinstance(ev["data"], dict)
        assert ev["data"]["request_id"] == req_id


@pytest.mark.asyncio
async def test_dim1_document_summary_no_request_id_generates_valid_uuid4(
    client: AsyncClient, sample_document: DocumentModel
) -> None:
    """POST summary:stream with NO X-Request-ID: returns UUID4 header & in summary_start."""
    resp = await client.post(f"/api/v1/documents/{sample_document.id}/summary:stream")
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
    assert "x-request-id" in resp.headers

    req_id = resp.headers["x-request-id"]
    _assert_valid_uuid4(req_id)

    events = _parse_sse_events(resp.text)
    start_events = [e for e in events if e["event"] == "summary_start"]
    assert len(start_events) == 1
    start_payload = start_events[0]["data"]
    assert start_payload["document_id"] == str(sample_document.id)
    assert start_payload["status"] == "streaming"
    assert start_payload["request_id"] == req_id


@pytest.mark.asyncio
async def test_dim1_session_chat_no_request_id_generates_valid_uuid4(
    client: AsyncClient, sample_session: ResearchSessionModel
) -> None:
    """POST /messages with NO X-Request-ID: returns UUID4 header & in start payload."""
    payload = {
        "question": "What is the core breakthrough of the Transformer?",
        "stream": True,
        "scope": "multi_paper",
    }
    resp = await client.post(f"/api/v1/sessions/{sample_session.id}/messages", json=payload)
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
    assert "x-request-id" in resp.headers

    req_id = resp.headers["x-request-id"]
    _assert_valid_uuid4(req_id)

    events = _parse_sse_events(resp.text)
    start_events = [e for e in events if e["event"] == "start"]
    assert len(start_events) == 1
    start_payload = start_events[0]["data"]
    assert "turn_id" in start_payload
    assert "message_id" in start_payload
    assert "created_at" in start_payload
    assert start_payload["request_id"] == req_id


# ==============================================================================
# DIMENSION 2: Custom X-Request-ID Header -> Exact Echo in Header and Payloads
# ==============================================================================
@pytest.mark.asyncio
async def test_dim2_events_custom_request_id_exact_echo(client: AsyncClient) -> None:
    """GET /events with custom X-Request-ID: echoes exact trace string."""
    custom_id = "my-custom-trace-uuid-12345"
    resp = await client.get("/events", headers={"X-Request-ID": custom_id})
    assert resp.status_code == 200
    assert resp.headers.get("x-request-id") == custom_id

    events = _parse_sse_events(resp.text)
    for ev in events:
        assert ev["data"]["request_id"] == custom_id


@pytest.mark.asyncio
async def test_dim2_document_summary_custom_request_id_exact_echo(
    client: AsyncClient, sample_document: DocumentModel
) -> None:
    """POST summary:stream with custom X-Request-ID: echoes in header & summary_start."""
    custom_id = "my-custom-trace-uuid-12345"
    resp = await client.post(
        f"/api/v1/documents/{sample_document.id}/summary:stream",
        headers={"X-Request-ID": custom_id},
    )
    assert resp.status_code == 200
    assert resp.headers.get("x-request-id") == custom_id

    events = _parse_sse_events(resp.text)
    start_events = [e for e in events if e["event"] == "summary_start"]
    assert len(start_events) == 1
    assert start_events[0]["data"]["request_id"] == custom_id


@pytest.mark.asyncio
async def test_dim2_session_chat_custom_request_id_exact_echo(
    client: AsyncClient, sample_session: ResearchSessionModel
) -> None:
    """POST /sessions/{id}/messages with custom X-Request-ID: echoes in header & start event."""
    custom_id = "my-custom-trace-uuid-12345"
    payload = {
        "question": "Can attention replace recurrent architectures completely?",
        "stream": True,
        "scope": "multi_paper",
    }
    resp = await client.post(
        f"/api/v1/sessions/{sample_session.id}/messages",
        json=payload,
        headers={"X-Request-ID": custom_id},
    )
    assert resp.status_code == 200
    assert resp.headers.get("x-request-id") == custom_id

    events = _parse_sse_events(resp.text)
    start_events = [e for e in events if e["event"] == "start"]
    assert len(start_events) == 1
    assert start_events[0]["data"]["request_id"] == custom_id


# ==============================================================================
# DIMENSION 3: Uppercase X-REQUEST-ID & Duplicate Headers Deduplication
# ==============================================================================
@pytest.mark.asyncio
async def test_dim3_uppercase_header_canonical_single_response(client: AsyncClient) -> None:
    """Client sends uppercase X-REQUEST-ID: server returns exactly 1 lowercase x-request-id."""
    custom_id = "trace-uppercase-stress-77777"
    resp = await client.get("/events", headers={"X-REQUEST-ID": custom_id})
    assert resp.status_code == 200

    # Verify httpx header list has exactly 1 entry
    header_list = resp.headers.get_list("x-request-id")
    assert len(header_list) == 1, f"Expected 1 x-request-id header, got {header_list}"
    assert header_list[0] == custom_id


@pytest.mark.asyncio
async def test_dim3_duplicate_headers_deduplicated_to_single_header(client: AsyncClient) -> None:
    """Client sends duplicate headers: server returns exactly 1 deduplicated x-request-id."""
    raw_headers = [
        ("X-REQUEST-ID", "duplicate-trace-alpha"),
        ("x-request-id", "duplicate-trace-beta"),
        ("X-Request-Id", "duplicate-trace-gamma"),
    ]
    resp = await client.get("/events", headers=raw_headers)
    assert resp.status_code == 200

    header_list = resp.headers.get_list("x-request-id")
    assert len(header_list) == 1, f"Duplicate headers detected: {header_list}"
    assert header_list[0] == "duplicate-trace-alpha"


@pytest.mark.asyncio
async def test_dim3_duplicate_headers_on_document_summary_stream(
    client: AsyncClient, sample_document: DocumentModel
) -> None:
    """StreamingResponse with explicit route header does NOT duplicate x-request-id."""
    raw_headers = [
        ("X-REQUEST-ID", "doc-duplicate-trace-001"),
        ("x-request-id", "doc-duplicate-trace-002"),
    ]
    resp = await client.post(
        f"/api/v1/documents/{sample_document.id}/summary:stream",
        headers=raw_headers,
    )
    assert resp.status_code == 200
    header_list = resp.headers.get_list("x-request-id")
    assert len(header_list) == 1, f"Duplicate x-request-id headers in summary stream: {header_list}"
    assert header_list[0] == "doc-duplicate-trace-001"


@pytest.mark.asyncio
async def test_dim3_empty_request_id_fallback_to_uuid4(client: AsyncClient) -> None:
    """Client sends empty string header X-Request-ID: '': server generates new UUID4."""
    resp = await client.get("/events", headers={"X-Request-ID": ""})
    assert resp.status_code == 200
    header_list = resp.headers.get_list("x-request-id")
    assert len(header_list) == 1
    req_id = header_list[0]
    assert req_id != ""
    _assert_valid_uuid4(req_id)


# ==============================================================================
# DIMENSION 4: Deep SSE Chunk Parsing & Structural Invariant Verification
# ==============================================================================
@pytest.mark.asyncio
async def test_dim4_document_summary_full_chunk_lifecycle(
    client: AsyncClient, sample_document: DocumentModel
) -> None:
    """Verify complete summary SSE stream sequence: summary_start -> chunk -> box -> end."""
    custom_id = "lifecycle-summary-trace-444"
    resp = await client.post(
        f"/api/v1/documents/{sample_document.id}/summary:stream",
        headers={"X-Request-ID": custom_id},
    )
    assert resp.status_code == 200
    events = _parse_sse_events(resp.text)
    assert len(events) >= 4

    # 1. First event must be summary_start with valid contract
    first_ev = events[0]
    assert first_ev["event"] == "summary_start"
    assert first_ev["data"] == {
        "document_id": str(sample_document.id),
        "status": "streaming",
        "request_id": custom_id,
    }

    # 2. Intermediate events must be summary_chunk and summary_box
    event_names = [e["event"] for e in events]
    assert "summary_chunk" in event_names
    assert "summary_box" in event_names

    # Verify summary_box structure
    box_events = [e for e in events if e["event"] == "summary_box"]
    for be in box_events:
        assert "section" in be["data"]
        assert "bounding_boxes" in be["data"]
        assert isinstance(be["data"]["bounding_boxes"], list)

    # 3. Last event must be summary_end
    last_ev = events[-1]
    assert last_ev["event"] == "summary_end"
    assert last_ev["data"]["document_id"] == str(sample_document.id)
    assert last_ev["data"]["finish_reason"] == "completed"


@pytest.mark.asyncio
async def test_dim4_session_chat_full_chunk_lifecycle(
    client: AsyncClient, sample_session: ResearchSessionModel
) -> None:
    """Verify complete chat SSE stream sequence: start -> reasoning/citations/token -> done."""
    custom_id = "lifecycle-chat-trace-555"
    payload = {
        "question": "How does self-attention compute query, key, and value vectors?",
        "stream": True,
        "scope": "multi_paper",
    }
    resp = await client.post(
        f"/api/v1/sessions/{sample_session.id}/messages",
        json=payload,
        headers={"X-Request-ID": custom_id},
    )
    assert resp.status_code == 200
    events = _parse_sse_events(resp.text)
    assert len(events) >= 3

    # 1. First event must be start with valid contract
    start_ev = events[0]
    assert start_ev["event"] == "start"
    data = start_ev["data"]
    assert "turn_id" in data
    assert "message_id" in data
    assert "created_at" in data
    assert data["request_id"] == custom_id

    # 2. Done event must complete the turn
    event_names = [e["event"] for e in events]
    assert "done" in event_names
    done_ev = [e for e in events if e["event"] == "done"][0]
    assert done_ev["data"]["finish_reason"] == "stop"


@pytest.mark.asyncio
async def test_dim4_session_not_found_sse_error_payload_has_request_id(
    client: AsyncClient,
) -> None:
    """Verify in-stream error event on missing session carries request_id."""
    missing_id = uuid4()
    custom_id = "missing-session-trace-888"
    payload = {
        "question": "Non-existent session query",
        "stream": True,
    }
    resp = await client.post(
        f"/api/v1/sessions/{missing_id}/messages",
        json=payload,
        headers={"X-Request-ID": custom_id},
    )
    assert resp.status_code == 200
    assert resp.headers.get("x-request-id") == custom_id

    events = _parse_sse_events(resp.text)
    assert len(events) == 1
    err_ev = events[0]
    assert err_ev["event"] == "error"
    assert err_ev["data"]["code"] == "SESSION_NOT_FOUND"
    assert err_ev["data"]["request_id"] == custom_id


@pytest.mark.asyncio
async def test_dim4_archived_session_sse_error_payload_has_request_id(
    client: AsyncClient, stress_db: InMemoryAsyncStressDb
) -> None:
    """Verify in-stream error event on archived session carries request_id."""
    s_id = uuid4()
    archived_sess = ResearchSessionModel(
        id=s_id,
        user_id=DEFAULT_DEV_USER_ID,
        title="Archived Session",
        active_document_id=None,
        viewport_state={"page": 1, "zoom_ratio": 1.0, "scroll_top": 0.0},
        active_tab="chat",
        is_archived=True,
        archived_at=datetime.now(UTC),
        version=1,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    stress_db.add(archived_sess)

    custom_id = "archived-session-trace-999"
    payload = {
        "question": "Can I query archived session?",
        "stream": True,
    }
    resp = await client.post(
        f"/api/v1/sessions/{s_id}/messages",
        json=payload,
        headers={"X-Request-ID": custom_id},
    )
    assert resp.status_code == 200
    assert resp.headers.get("x-request-id") == custom_id

    events = _parse_sse_events(resp.text)
    assert len(events) == 1
    err_ev = events[0]
    assert err_ev["event"] == "error"
    assert err_ev["data"]["code"] == "SESSION_ARCHIVED"
    assert err_ev["data"]["request_id"] == custom_id


@pytest.mark.asyncio
async def test_dim4_pre_stream_error_envelope_carries_request_id(
    client: AsyncClient,
) -> None:
    """Pre-stream 404 returns structured error envelope and single x-request-id."""
    missing_doc_id = uuid4()
    custom_id = "doc-not-found-trace-111"
    resp = await client.post(
        f"/api/v1/documents/{missing_doc_id}/summary:stream",
        headers={"X-Request-ID": custom_id},
    )
    assert resp.status_code == 404
    header_list = resp.headers.get_list("x-request-id")
    assert len(header_list) == 1
    assert header_list[0] == custom_id

    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "DOCUMENT_NOT_FOUND"
    assert body["meta"]["request_id"] == custom_id
