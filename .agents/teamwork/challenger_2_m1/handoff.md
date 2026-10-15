# Handoff Report: Empirical Challenge for Milestone 1 (Error Handling & Concurrency)

**Agent**: `challenger_2_m1`  
**Role**: `critic`, `specialist` (Empirical Challenger)  
**Milestone**: `M1_SSE_TRACING`  
**Verdict**: **CONFIRM**  
**Date**: 2026-10-15  

---

## 1. Observation

1. **Concurrency and structlog Contextvars Isolation**:
   - `apps/api/src/api/middleware/tracing.py:40-45`:
     ```python
     structlog.contextvars.clear_contextvars()
     structlog.contextvars.bind_contextvars(
         request_id=request_id,
         method=scope.get("method"),
         path=scope.get("path"),
     )
     ```
   - In `apps/api/tests/test_concurrency_error_sse_challenge.py::test_concurrent_requests_structlog_contextvars_isolation`, 50 concurrent requests with unique client UUIDs (`stress-concurrency-{idx}-{uuid4()}`) were launched against `/events`. Every response header `x-request-id` matched the client's custom UUID, and all 3 SSE data chunks per stream (`{"step": i, "content": ..., "request_id": ...}`) echoed that exact request ID. Zero cross-request bleeding was observed across all 150 streamed event chunks.
   - In `apps/api/tests/test_concurrency_error_sse_challenge.py::test_interleaved_async_execution_contextvars_integrity`, an asynchronous interleaving stress test was run where Task A (slow, 50ms sleep) started first, Task B (fast, 5ms sleep) started 10ms later and finished first. `structlog.contextvars.get_contextvars()["request_id"]` was measured before sleep, during interleaving, and after sleep:
     - Task A: `ctx_before == id_slow`, `ctx_after == id_slow`.
     - Task B: `ctx_before == id_fast`, `ctx_after == id_fast`.
     Zero contextvar mutation or premature clearing occurred during task yielding.

2. **Error Envelope and Header Emittance across 400, 401, 404, 422, and 500**:
   - `apps/api/src/api/__init__.py:94-273`: Global exception handlers implement RFC 7807 structured JSON envelopes (`ErrorResponse`) and propagate `headers={"X-Request-ID": req_id}` and `meta["request_id"]`.
   - In `apps/api/tests/test_concurrency_error_sse_challenge.py`:
     - **400 Bad Request** (`test_error_400_bad_request_envelope_and_header`): Both explicit `HTTPException(400)` and `DomainError` returned HTTP 400 with `success: False`, matching `x-request-id` header and matching `meta["request_id"]` (tested with custom ID and server-generated UUID4).
     - **401 Unauthorized** (`test_error_401_unauthorized_envelope_and_header`): Protected route `/api/v1/sessions` without credentials or with invalid Bearer token returned HTTP 401 with `x-request-id` header, matching `meta["request_id"]`, and `WWW-Authenticate: Bearer` header.
     - **404 Not Found** (`test_error_404_not_found_envelope_and_header`): Unmatched route `/api/v1/non_existent_path` returned HTTP 404 with `x-request-id` header, `error.code == "HTTP_404"`, and matching `meta["request_id"]`.
     - **422 Validation Error** (`test_error_422_validation_error_envelope_and_header`): Invalid payload (`POST /api/v1/sessions` with malformed UUID) and invalid path parameter (`GET /api/v1/documents/not-a-valid-uuid`) returned HTTP 422 with `x-request-id` header, matching `meta["request_id"]`, and detailed field-level error list in `meta["errors"]`.
     - **500 Internal Server Error** (`test_error_500_unhandled_internal_error_envelope_and_header`): Route raising unhandled `ZeroDivisionError` was trapped by `unhandled_exception_handler` and `ServerErrorMiddleware`, returning HTTP 500 with `error.code == "INTERNAL_SERVER_ERROR"`, `x-request-id` header, and matching `meta["request_id"]`.

3. **Aborted SSE Streams, Disconnect Handling, and Memory Leaks**:
   - `apps/api/src/api/services/document_service.py:2351-2352`:
     ```python
     if is_disconnected and await is_disconnected():
         return
     ```
     Tested in `test_sse_client_abort_disconnect_guard_in_summary_stream`: upon disconnect signal after 3 events, generator immediately terminated without continuing to produce the remaining ~150 tokens.
   - `apps/api/src/api/services/session_chat_service.py:1044-1049, 1082-1085`:
     ```python
     if await is_disconnected():
         logger.warning("sse_client_disconnected", session_id=str(session_id))
         finish_reason = "interrupted"
         break
     ```
     Tested in `test_sse_client_abort_disconnect_guard_in_chat_stream`: upon disconnect signal, generator stopped token emission, persisted `SessionTurnModel` with `finish_reason = "interrupted"`, exited Langfuse trace span cleanly, and committed session state.
   - In `test_high_concurrency_sse_aborts_memory_and_task_leak`: 50 concurrent SSE streams were initiated and aborted immediately on first body chunk:
     - `PureASGITracingMiddleware` caught the cancellation, logged `http_request_finished` with `client_aborted=True, status_code=499`.
     - Active asyncio tasks count was verified before and after abort storm: no orphaned background tasks remained.
     - Contextvars were cleared: `request_id` did not leak into global/task scope.
     - Heap memory allocations tracked via `tracemalloc`: total memory difference was `< 500 KB` across 50 aborts, with zero uncollected generator frames or connection leak.

4. **Suite Test Results**:
   - Dedicated empirical challenge suite:
     `uv run pytest apps/api/tests/test_concurrency_error_sse_challenge.py`: 10 passed in 1.71s.
   - Full API suite:
     `uv run pytest apps/api/tests/`: 239 passed in 28.75s.
   - Core domain suite:
     `uv run pytest packages/core/tests`: 76 passed in 0.32s.
   - Code formatting and linting:
     `uv run ruff check apps/api` and `uv run ruff format --check apps/api`: 0 errors, 0 warnings.

---

## 2. Logic Chain

1. **Concurrency Isolation Proof (Observation 1)**:
   - Python 3.12 `contextvars` uses task-local storage. Each asyncio Task receives a copy of the parent context at creation. In `PureASGITracingMiddleware`, `structlog.contextvars.bind_contextvars()` sets values for the specific task context.
   - Empirical test with 50 concurrent requests and interleaved async sleeps confirmed that task switching does not mutate or overwrite other coroutines' `structlog` context or `scope["state"]["request_id"]`.
   - Therefore, concurrent requests cannot bleed or cross-contaminate request IDs.

2. **Error Envelope Uniformity (Observation 2)**:
   - `PureASGITracingMiddleware` sits as the outer ASGI wrapper inside `CORSMiddleware`, wrapping `ExceptionMiddleware`. It intercepts all `http.response.start` messages, ensuring `x-request-id` is appended to headers.
   - Global exception handlers in `api/__init__.py` read `req_id = getattr(request.state, "request_id", None) or request.headers.get("x-request-id")` and explicitly inject it into `meta["request_id"]`.
   - Empirical tests for status codes 400, 401, 404, 422, and 500 confirmed that in all cases (both with client-provided custom headers and with server-generated UUID4s), the `x-request-id` header is emitted and strictly matches `meta["request_id"]`.

3. **Resource Leak & SSE Abort Resilience (Observation 3)**:
   - Streaming endpoints (`/events`, `summary:stream`, `post_session_message`) integrate `is_disconnected` guards and rely on Starlette's `StreamingResponse` task cancellation.
   - When a client aborts mid-stream, generator execution breaks immediately without generating wasteful tokens, turns are recorded with `finish_reason = "interrupted"`, and Langfuse trace spans exit properly.
   - A 50-client concurrent abort storm confirmed that all coroutines terminate, `asyncio.all_tasks()` returns to baseline, and heap memory usage remains bounded with zero generator accumulation.

---

## 3. Caveats

- **Starlette `ClientDisconnect` Type**: In `PureASGITracingMiddleware`, the exception catch is `except (asyncio.CancelledError, ConnectionResetError): status_code = 499`. Starlette's `ClientDisconnect` inherits from `Exception` rather than `CancelledError`. In ASGI 2.3 under Uvicorn, task cancellation raises `asyncio.CancelledError`, which is correctly caught and mapped to 499. If an alternative ASGI server raises `ClientDisconnect` directly without cancelling the task, it would enter `except Exception:` and log 500. This is a minor non-blocking observability caveat that does not affect request processing or resource cleanup.

---

## 4. Conclusion

**Verdict: CONFIRM**

Milestone 1 (`M1_SSE_TRACING`) satisfies all requirements:
1. Concurrency isolation is verified: no structlog contextvars bleeding across concurrent or interleaved requests.
2. Error response uniformity is verified: 400, 401, 404, 422, and unhandled 500 errors consistently emit canonical `x-request-id` headers and matching `meta["request_id"]`.
3. Client abort handling is verified: mid-stream SSE client disconnects cleanly terminate generator execution, record partial turns, close trace spans, release memory, and leave no orphaned asyncio tasks.

---

## 5. Verification Method

To independently verify all challenge findings:

1. **Run the Challenger 2 Empirical Test Suite**:
   ```bash
   uv run pytest apps/api/tests/test_concurrency_error_sse_challenge.py -v
   ```
   *Expected*: 10 passed in ~2s.

2. **Run Full Backend API Test Suite**:
   ```bash
   uv run pytest apps/api/tests/
   ```
   *Expected*: 239 passed in ~29s.

3. **Verify Linter and Formatter**:
   ```bash
   uv run ruff check apps/api
   uv run ruff format --check apps/api
   ```
   *Expected*: Clean with 0 errors and 0 warnings.
