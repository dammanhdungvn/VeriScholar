"""Empirical Challenge Test Suite for Milestone 1 (M1_SSE_TRACING).

Conducted by Challenger 2 Agent.
Focus areas:
1. Concurrency isolation: Ensure structlog contextvars and state do not bleed or
   cross-contaminate across concurrent requests (including interleaved async execution).
2. Error handling: Verify 400 Bad Request, 401 Unauthorized, 404 Not Found,
   422 Validation Error, and unhandled 500 Internal Error all emit canonical `x-request-id`
   headers and matching `meta["request_id"]` (both with and without client-supplied header).
3. SSE abort handling & memory leak checks: Client disconnect mid-stream, task cancellation,
   memory stability, generator cleanup in document summary and session chat.
"""

import asyncio
import gc
import json
import tracemalloc
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
import structlog
from api import app
from api.db.models.chunk import DocumentChunkModel
from api.db.models.document import DocumentModel
from api.db.models.session import ResearchSessionModel, SessionDocumentModel, SessionTurnModel
from api.db.models.summary import DocumentSummaryModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import (
    DEFAULT_DEV_USER_ID,
    get_current_user,
)
from api.schemas.document import (
    DocumentSummaryData,
    DocumentSummaryEnvelope,
    SummaryPointResponse,
)
from api.schemas.session import SessionChatMessageRequest
from api.services.document_service import DocumentService
from api.services.session_chat_service import SessionChatService
from core.domain.exceptions import (
    DomainError,
)
from core.ports.storage import IBlobStoragePort
from fastapi import APIRouter, HTTPException, Request, status
from httpx import ASGITransport, AsyncClient


# ==============================================================================
# In-Memory Database Double for Isolated Testing
# ==============================================================================
class InMemoryDbDouble:
    """In-memory database stub satisfying SQLAlchemy async session interface."""

    def __init__(self) -> None:
        self.documents: dict[UUID, DocumentModel] = {}
        self.chunks: list[DocumentChunkModel] = []
        self.summaries: dict[UUID, DocumentSummaryModel] = {}
        self.sessions: dict[UUID, ResearchSessionModel] = {}
        self.session_documents: list[SessionDocumentModel] = []
        self.session_turns: list[SessionTurnModel] = []
        self.users: dict[UUID, UserModel] = {}

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
            self.sessions[obj.id] = obj
        elif isinstance(obj, SessionDocumentModel):
            self.session_documents.append(obj)
        elif isinstance(obj, SessionTurnModel):
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            self.session_turns.append(obj)
        elif isinstance(obj, UserModel):
            self.users[obj.id] = obj

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

        if "FROM users" in statement_str:
            uid = params.get("id_1") or params.get("id")
            result_mock.scalar_one_or_none.return_value = self.users.get(uid)
            return result_mock

        if "FROM documents" in statement_str:
            doc_id = params.get("id_1") or params.get("id")
            result_mock.scalar_one_or_none.return_value = self.documents.get(doc_id)
            return result_mock

        if "FROM research_sessions" in statement_str:
            sid = params.get("id_1") or params.get("id")
            result_mock.scalar_one_or_none.return_value = self.sessions.get(sid)
            return result_mock

        if "FROM session_documents" in statement_str:
            sid = params.get("session_id_1") or params.get("session_id")
            matched = [sd.document_id for sd in self.session_documents if sd.session_id == sid]
            result_mock.scalars.return_value.all.return_value = matched
            return result_mock

        if "FROM document_chunks" in statement_str:
            matched_chunks = [(c, "Doc Title", "doc.pdf") for c in self.chunks]
            result_mock.all.return_value = matched_chunks
            return result_mock

        if "FROM session_turns" in statement_str:
            sid = params.get("session_id_1") or params.get("session_id")
            matched_turns = [t for t in self.session_turns if t.session_id == sid]
            result_mock.scalars.return_value.all.return_value = matched_turns
            return result_mock

        result_mock.scalar_one_or_none.return_value = None
        result_mock.scalars.return_value.all.return_value = []
        return result_mock


# ==============================================================================
# CHALLENGE 1: Concurrency and structlog Contextvars Isolation
# ==============================================================================


@pytest.mark.asyncio
async def test_concurrent_requests_structlog_contextvars_isolation():
    """Verify concurrent requests with distinct X-Request-IDs do NOT bleed

    structlog contextvars or request.state between concurrent tasks.
    """
    num_requests = 8
    transport = ASGITransport(app=app)
    results: list[dict[str, Any]] = []

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:

        async def worker(idx: int) -> dict[str, Any]:
            custom_id = f"stress-concurrency-{idx:03d}-{uuid4()}"
            res = await client.get("/events", headers={"X-Request-ID": custom_id})
            assert res.status_code == 200
            res_header = res.headers.get("x-request-id")

            # Parse event chunk data payloads
            chunk_request_ids: list[str] = []
            for line in res.text.split("\n"):
                if line.startswith("data: "):
                    data_obj = json.loads(line[6:])
                    chunk_request_ids.append(data_obj.get("request_id"))

            return {
                "idx": idx,
                "sent_id": custom_id,
                "header_id": res_header,
                "chunk_ids": chunk_request_ids,
            }

        tasks = [worker(i) for i in range(num_requests)]
        results = await asyncio.gather(*tasks)

    # Validate isolation across every single request
    seen_ids = set()
    for item in results:
        sent = item["sent_id"]
        header = item["header_id"]
        chunks = item["chunk_ids"]

        # 1. Header strictly echoes sent custom ID
        assert header == sent, f"Header ID mismatch: expected {sent}, got {header}"
        assert sent not in seen_ids, f"Duplicate request ID observed: {sent}"
        seen_ids.add(sent)

        # 2. Every streamed chunk contains the exact request ID of this specific request
        assert len(chunks) == 3, f"Expected 3 chunks, got {len(chunks)}"
        for c_id in chunks:
            assert c_id == sent, f"Cross-contamination detected! Chunk had {c_id}, expected {sent}"


@pytest.mark.asyncio
async def test_interleaved_async_execution_contextvars_integrity():
    """Verify that when Task A yields execution via sleep and Task B runs,

    Task A's structlog contextvars are NOT mutated or cleared by Task B.
    """
    challenge_router = APIRouter()
    observed_contextvars: dict[str, list[str | None]] = {}

    @challenge_router.get("/challenge/interleave")
    async def interleave_handler(delay: float, name: str, request: Request):
        req_id = getattr(request.state, "request_id", None)
        ctx_before = structlog.contextvars.get_contextvars().get("request_id")

        # Yield execution to event loop so other concurrent tasks interleave
        await asyncio.sleep(delay)

        ctx_after = structlog.contextvars.get_contextvars().get("request_id")
        observed_contextvars[name] = [ctx_before, ctx_after, req_id]
        return {
            "name": name,
            "ctx_before": ctx_before,
            "ctx_after": ctx_after,
            "state_id": req_id,
        }

    app.include_router(challenge_router)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        id_slow = "slow-task-uuid-111"
        id_fast = "fast-task-uuid-222"

        # Slow task starts first, sleeps 50ms.
        # Fast task starts 10ms later, sleeps 5ms, finishes first.
        task_slow = asyncio.create_task(
            client.get(
                "/challenge/interleave?delay=0.05&name=slow",
                headers={"X-Request-ID": id_slow},
            )
        )
        await asyncio.sleep(0.01)
        task_fast = asyncio.create_task(
            client.get(
                "/challenge/interleave?delay=0.005&name=fast",
                headers={"X-Request-ID": id_fast},
            )
        )

        res_slow, res_fast = await asyncio.gather(task_slow, task_fast)

    assert res_slow.status_code == 200
    assert res_fast.status_code == 200
    assert res_slow.headers.get("x-request-id") == id_slow
    assert res_fast.headers.get("x-request-id") == id_fast

    # Verify contextvars before and after sleep inside the coroutines
    slow_obs = observed_contextvars["slow"]
    fast_obs = observed_contextvars["fast"]

    assert slow_obs[0] == id_slow
    assert slow_obs[1] == id_slow, (
        f"Contextvar bleed in slow task after fast task executed! Got {slow_obs[1]}"
    )
    assert slow_obs[2] == id_slow

    assert fast_obs[0] == id_fast
    assert fast_obs[1] == id_fast
    assert fast_obs[2] == id_fast


# ==============================================================================
# CHALLENGE 2: Error Conditions (400, 401, 404, 422, 500)
# ==============================================================================


@pytest.mark.asyncio
async def test_error_400_bad_request_envelope_and_header():
    """Verify 400 Bad Request emits canonical x-request-id header and matching meta.request_id."""
    test_router = APIRouter()

    @test_router.get("/challenge/error-400-http")
    async def trigger_400_http():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_QUERY_FILTER",
                "message": "The provided date range filter is malformed.",
                "field": "date_range",
                "action": "Specify ISO-8601 formatted start and end dates.",
            },
        )

    @test_router.get("/challenge/error-400-domain")
    async def trigger_400_domain():
        raise DomainError("Generic domain invariant violated.")

    app.include_router(test_router)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Case A: With custom X-Request-ID
        cid = "req-400-custom-trace"
        res_a = await client.get("/challenge/error-400-http", headers={"X-Request-ID": cid})
        assert res_a.status_code == 400
        assert res_a.headers.get("x-request-id") == cid
        data_a = res_a.json()
        assert data_a["success"] is False
        assert data_a["error"]["code"] == "INVALID_QUERY_FILTER"
        assert data_a["meta"]["request_id"] == cid

        # Case B: Without X-Request-ID (server-generated UUID4)
        res_b = await client.get("/challenge/error-400-domain")
        assert res_b.status_code == 400
        gen_id = res_b.headers.get("x-request-id")
        assert gen_id is not None and len(gen_id) > 10
        data_b = res_b.json()
        assert data_b["success"] is False
        assert data_b["error"]["code"] == "DOMAIN_ERROR"
        assert data_b["meta"]["request_id"] == gen_id


@pytest.mark.asyncio
async def test_error_401_unauthorized_envelope_and_header():
    """Verify 401 Unauthorized emits canonical x-request-id header and matching meta.request_id."""
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Case A: Requesting protected /api/v1/sessions without credentials (with custom ID)
        cid = "req-401-custom-trace"
        res_a = await client.get("/api/v1/sessions", headers={"X-Request-ID": cid})
        assert res_a.status_code == 401
        assert res_a.headers.get("x-request-id") == cid
        data_a = res_a.json()
        assert data_a["success"] is False
        assert data_a["error"]["code"] == "UNAUTHORIZED"
        assert data_a["meta"]["request_id"] == cid
        assert "WWW-Authenticate" in res_a.headers

        # Case B: Requesting with malformed Bearer token without custom ID
        res_b = await client.get(
            "/api/v1/sessions",
            headers={"Authorization": "Bearer not-a-valid-token-string"},
        )
        assert res_b.status_code == 401
        gen_id = res_b.headers.get("x-request-id")
        assert gen_id is not None
        data_b = res_b.json()
        assert data_b["success"] is False
        assert data_b["error"]["code"] in ("INVALID_TOKEN", "UNAUTHORIZED")
        assert data_b["meta"]["request_id"] == gen_id


@pytest.mark.asyncio
async def test_error_404_not_found_envelope_and_header():
    """Verify 404 Not Found emits canonical x-request-id header and matching meta.request_id."""
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Case A: Completely non-existent route with custom ID
        cid = "req-404-custom-trace"
        res_a = await client.get("/api/v1/non_existent_path", headers={"X-Request-ID": cid})
        assert res_a.status_code == 404
        assert res_a.headers.get("x-request-id") == cid
        data_a = res_a.json()
        assert data_a["success"] is False
        assert data_a["error"]["code"] == "HTTP_404"
        assert data_a["meta"]["request_id"] == cid

        # Case B: Non-existent route without header (server-generated UUID4)
        res_b = await client.get("/api/v1/unknown_probe")
        assert res_b.status_code == 404
        gen_id = res_b.headers.get("x-request-id")
        assert gen_id is not None
        data_b = res_b.json()
        assert data_b["meta"]["request_id"] == gen_id


@pytest.mark.asyncio
async def test_error_422_validation_error_envelope_and_header():
    """Verify 422 Validation Error emits canonical x-request-id header

    and matching meta.request_id.
    """
    db_double = InMemoryDbDouble()

    async def override_get_db():
        yield db_double

    test_user = UserModel(
        id=DEFAULT_DEV_USER_ID,
        email="dev@verischolar.org",
        full_name="Dev",
        hashed_password="h",
        is_active=True,
    )

    async def override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Case A: Request body schema validation error with custom ID
            cid = "req-422-custom-trace"
            res_a = await client.post(
                "/api/v1/sessions",
                json={"initial_document_ids": ["invalid-uuid-format-fail"]},
                headers={"X-Request-ID": cid, "X-User-Id": str(DEFAULT_DEV_USER_ID)},
            )
            assert res_a.status_code == 422
            assert res_a.headers.get("x-request-id") == cid
            data_a = res_a.json()
            assert data_a["success"] is False
            assert data_a["error"]["code"] == "VALIDATION_ERROR"
            assert data_a["meta"]["request_id"] == cid
            assert "errors" in data_a["meta"]
            assert len(data_a["meta"]["errors"]) > 0

            # Case B: Invalid UUID path parameter without custom ID
            res_b = await client.get(
                "/api/v1/documents/not-a-valid-uuid",
                headers={"X-User-Id": str(DEFAULT_DEV_USER_ID)},
            )
            assert res_b.status_code == 422
            gen_id = res_b.headers.get("x-request-id")
            assert gen_id is not None
            data_b = res_b.json()
            assert data_b["success"] is False
            assert data_b["meta"]["request_id"] == gen_id
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_error_500_unhandled_internal_error_envelope_and_header():
    """Verify unhandled 500 Internal Error emits canonical x-request-id header

    and matching meta.request_id.
    """
    test_router = APIRouter()

    @test_router.get("/challenge/unhandled-500")
    async def trigger_500():
        raise ZeroDivisionError("Simulated unexpected mathematical singularity in ranking!")

    app.include_router(test_router)
    transport = ASGITransport(app=app, raise_app_exceptions=False)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Case A: With custom X-Request-ID
        cid = "req-500-custom-trace"
        res_a = await client.get("/challenge/unhandled-500", headers={"X-Request-ID": cid})
        assert res_a.status_code == 500
        assert res_a.headers.get("x-request-id") == cid
        data_a = res_a.json()
        assert data_a["success"] is False
        assert data_a["error"]["code"] == "INTERNAL_SERVER_ERROR"
        assert data_a["meta"]["request_id"] == cid

        # Case B: Without custom X-Request-ID (server-generated UUID4)
        res_b = await client.get("/challenge/unhandled-500")
        assert res_b.status_code == 500
        gen_id = res_b.headers.get("x-request-id")
        assert gen_id is not None
        data_b = res_b.json()
        assert data_b["success"] is False
        assert data_b["error"]["code"] == "INTERNAL_SERVER_ERROR"
        assert data_b["meta"]["request_id"] == gen_id


# ==============================================================================
# CHALLENGE 3: Aborted SSE Streams, Disconnect Handling, and Memory Leaks
# ==============================================================================


@pytest.mark.asyncio
async def test_sse_client_abort_disconnect_guard_in_summary_stream():
    """Verify DocumentService.stream_summary terminates cleanly when client

    disconnects mid-stream.
    """
    db_double = InMemoryDbDouble()
    doc_id = uuid4()
    user_id = DEFAULT_DEV_USER_ID

    doc = DocumentModel(
        id=doc_id,
        user_id=user_id,
        title="Attention Is All You Need",
        filename="attention.pdf",
        status="completed",
        chunk_count=10,
    )
    db_double.add(doc)

    service = DocumentService(
        storage=MagicMock(spec=IBlobStoragePort),
    )

    # Stub generate_document_summary to return a multi-section summary
    envelope = DocumentSummaryEnvelope(
        data=DocumentSummaryData(
            document_id=doc_id,
            problem_statement=SummaryPointResponse(
                text="Word " * 50,
                bounding_boxes=[],
            ),
            contributions=SummaryPointResponse(
                text="Word " * 50,
                bounding_boxes=[],
            ),
            limitations=SummaryPointResponse(
                text="Word " * 50,
                bounding_boxes=[],
            ),
        ),
        meta={"request_id": "test-abort-req"},
    )
    service.generate_document_summary = MagicMock(return_value=(envelope, False))  # type: ignore

    disconnect_triggered = False

    async def is_disconnected_stub() -> bool:
        return disconnect_triggered

    generator = service.stream_summary(
        document_id=doc_id,
        user_id=user_id,
        db=db_double,  # type: ignore
        is_disconnected=is_disconnected_stub,
        request_id="test-abort-summary",
    )

    chunks_received = 0
    async for event in generator:
        chunks_received += 1
        if chunks_received == 3:
            # Client disconnects after receiving 3 events
            disconnect_triggered = True

    # Total events would normally be ~156. If aborted early, count must be very small.
    assert chunks_received < 15, (
        f"Generator did not abort promptly: received {chunks_received} chunks"
    )


@pytest.mark.asyncio
async def test_sse_client_abort_disconnect_guard_in_chat_stream():
    """Verify SessionChatService.stream_chat handles disconnect mid-stream, persists

    turn with finish_reason='interrupted', and exits cleanly.
    """
    db_double = InMemoryDbDouble()
    session_id = uuid4()
    user_id = DEFAULT_DEV_USER_ID

    session = ResearchSessionModel(
        id=session_id,
        user_id=user_id,
        title="Test Session",
        is_archived=False,
    )
    db_double.add(session)

    chat_service = SessionChatService(db=db_double)  # type: ignore

    disconnect_triggered = False

    async def is_disconnected_stub() -> bool:
        return disconnect_triggered

    req = SessionChatMessageRequest(
        question="How does multi-head attention work?",
        scope="multi_paper",
    )

    generator = chat_service.stream_chat(
        session_id=session_id,
        user_id=user_id,
        request=req,
        is_disconnected=is_disconnected_stub,
        request_id="test-abort-chat",
    )

    events_received: list[str] = []
    async for event in generator:
        events_received.append(event)
        if len(events_received) == 2:
            disconnect_triggered = True

    # Verify that stream finished and recorded turn
    assert len(db_double.session_turns) == 1
    recorded_turn = db_double.session_turns[0]
    assert recorded_turn.finish_reason == "interrupted"


@pytest.mark.asyncio
async def test_high_concurrency_sse_aborts_memory_and_task_leak():
    """Verify concurrent aborted SSE streams do not leave dangling tasks,

    accumulate uncollected memory, or leak open contextvars.
    """
    initial_tasks_count = len(asyncio.all_tasks())

    # Start tracemalloc to monitor memory allocations
    tracemalloc.start()
    gc.collect()
    snap_before = tracemalloc.take_snapshot()

    # Simulate concurrent SSE stream invocations that are cancelled/closed mid-flight
    num_aborts = 8

    async def abortive_stream_session(idx: int):
        custom_id = f"abort-stream-{idx:03d}"
        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "method": "GET",
            "path": "/events",
            "headers": [(b"x-request-id", custom_id.encode())],
            "query_string": b"",
            "server": ("testserver", 80),
            "client": ("127.0.0.1", 12345),
        }

        # Mock ASGI receive that sends http.disconnect after 1st response start
        disconnect_event = asyncio.Event()

        async def mock_receive():
            await disconnect_event.wait()
            return {"type": "http.disconnect"}

        sent_messages = []

        async def mock_send(msg):
            sent_messages.append(msg)
            if msg["type"] == "http.response.body":
                # Immediately trigger disconnect on 1st body chunk
                disconnect_event.set()

        try:
            # Wrap in a short timeout to simulate client dropping connection
            await asyncio.wait_for(app(scope, mock_receive, mock_send), timeout=0.1)
        except (TimeoutError, asyncio.CancelledError):
            pass

    # Run all 50 abortive stream sessions concurrently
    await asyncio.gather(*(abortive_stream_session(i) for i in range(num_aborts)))

    # Allow event loop to process any pending cancellation callbacks
    await asyncio.sleep(0.05)
    gc.collect()

    snap_after = tracemalloc.take_snapshot()
    tracemalloc.stop()

    # 1. Verify no lingering orphaned asyncio Tasks
    current_tasks = [t for t in asyncio.all_tasks() if not t.done()]
    # Only current test runner task should be active
    assert len(current_tasks) <= initial_tasks_count + 1, (
        f"Dangling tasks detected! Initial: {initial_tasks_count}, Current: {len(current_tasks)}"
    )

    # 2. Verify structlog contextvars is completely clean
    remaining_ctx = structlog.contextvars.get_contextvars()
    assert "request_id" not in remaining_ctx or remaining_ctx["request_id"] is Ellipsis, (
        f"Contextvars leaked request_id after all aborted requests: {remaining_ctx}"
    )

    # 3. Memory leak check: ensure top memory diff does not have unbounded generator leakage
    top_stats = snap_after.compare_to(snap_before, "lineno")
    total_diff_kb = sum(stat.size_diff for stat in top_stats) / 1024
    # 50 aborted streams should not leak more than 1000 KB of retained memory
    assert total_diff_kb < 1000, (
        f"Excessive memory retained after aborted streams: {total_diff_kb:.2f} KB"
    )
