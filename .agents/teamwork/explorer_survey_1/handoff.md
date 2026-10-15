# Investigation & Survey Report: API & SSE Streaming and X-Request-ID Propagation

**Explorer**: `explorer_survey_1`  
**Date**: 2026-10-15  
**Working Directory**: `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/explorer_survey_1`  
**Scope**: `apps/api` FastAPI Application, ASGI Middleware, Logging, SSE Streaming Endpoints, Client Expectations, and Test Suites.

---

## 1. Observation

### 1.1. FastAPI App Initialization & ASGI Middleware Stack
- **File**: `apps/api/src/api/__init__.py:70-86`
  ```python
  app = FastAPI(
      title=settings.PROJECT_NAME,
      version=settings.VERSION,
      description="Academic Research & Writing AI Assistant API",
      lifespan=lifespan,
  )

  # 2. Add Pure ASGI Tracing Middleware and CORS Middleware
  app.add_middleware(PureASGITracingMiddleware)
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
      expose_headers=["ETag", "Location", "X-Request-ID", "Content-Disposition"],
  )
  ```
  - In Starlette/FastAPI, middlewares wrap in reverse order of addition. `CORSMiddleware` wraps `PureASGITracingMiddleware`.
  - `CORSMiddleware` exposes `X-Request-ID` in CORS responses via `expose_headers`.

### 1.2. Logging Configuration & Missing Call
- **File**: `apps/api/src/api/core/logging.py:46-50`
  ```python
  def setup_logging() -> None:
      """Configures structured JSON logging with request tracing context and PII masking.

      Must be called at module load time before FastAPI app or Uvicorn startup.
      """
  ```
  - Search command: `grep_search("setup_logging", SearchPath="apps/api")`
  - Observation: `setup_logging()` is defined in `api/core/logging.py` but is **never imported or called** in `apps/api/src/api/__init__.py`, `lifespan`, or `apps/api/src/api/__main__.py`.
  - Per `docs/vi/guide-logging-system.md:65`, `api/__init__.py` is designated to: *"Kích hoạt hệ thống logging ngay khi nạp module, quản lý sự kiện khởi động/tắt máy (lifespan)..."*.

### 1.3. X-Request-ID Extraction, Contextvars, and State Handling
- **File**: `apps/api/src/api/middleware/tracing.py:26-57`
  ```python
  request_id: str | None = None
  headers = scope.get("headers", [])
  for name, value in headers:
      if name.lower() == b"x-request-id":
          request_id = value.decode("latin1")
          break

  if not request_id:
      request_id = str(uuid.uuid4())

  structlog.contextvars.clear_contextvars()
  structlog.contextvars.bind_contextvars(
      request_id=request_id,
      method=scope.get("method"),
      path=scope.get("path"),
  )
  ...
  async def send_wrapper(message: Message) -> None:
      nonlocal status_code, ttfb_ms
      if message["type"] == "http.response.start":
          status_code = message.get("status", 500)
          ttfb_ms = round((time.perf_counter() - start_time) * 1000, 2)

          res_headers = list(message.get("headers", []))
          res_headers.append((b"x-request-id", request_id.encode("latin1")))
          message = {**message, "headers": res_headers}

      await send(message)
  ```
  - `PureASGITracingMiddleware` reads incoming `X-Request-ID` or generates a UUID4.
  - It binds `request_id` to `structlog.contextvars`.
  - It appends `(b"x-request-id", request_id.encode("latin1"))` on `http.response.start`.
  - **Critical Observation**: It does **NOT** set `scope["state"]["request_id"]`.
  - Starlette `Request.state` reads from `scope["state"]`.
  - In `apps/api/src/api/__init__.py:121, 174, 222, 250`, exception handlers attempt to retrieve:
    `"request_id": getattr(request.state, "request_id", None)`
    Because `scope["state"]["request_id"]` is never populated, `getattr(request.state, "request_id", None)` always returns `None`.
  - **Duplicate Header Risk**: `res_headers.append((b"x-request-id", ...))` does not filter or deduplicate existing headers. If an endpoint sets `headers={"X-Request-ID": ...}`, two `x-request-id` headers are sent.

### 1.4. Catalog of SSE Streaming Endpoints in `apps/api`
1. **Probe SSE Stream**: `GET /events`
   - File: `apps/api/src/api/__init__.py:271-280`
   - Response class: `EventSourceResponse`
   - Stream content: `ServerSentEvent(data={"step": i, "content": f"Streaming chunk {i}"}, event="progress", id=str(i))`
   - X-Request-ID: Propagated via `PureASGITracingMiddleware` in HTTP headers. Not present in event data payload.

2. **Scholar Reading Summary Stream**: `POST /api/v1/documents/{document_id}/summary:stream`
   - Route file: `apps/api/src/api/v1/endpoints/documents.py:1100-1217`
   - Service file: `apps/api/src/api/services/document_service.py:2295-2351`
   - Response class: `StreamingResponse(media_type="text/event-stream")`
   - Headers declared in route (`documents.py:1212`):
     ```python
     headers={
         "Cache-Control": "no-cache",
         "Connection": "keep-alive",
         "X-Accel-Buffering": "no",
     }
     ```
   - Events emitted: `summary_start`, `summary_chunk`, `summary_box`, `summary_end`, `error`.
   - Event payload in `summary_start` (`document_service.py:2306`):
     `start_dict = {"document_id": str(document_id), "status": "streaming"}` (Lacks `request_id`).

3. **Socratic Research Chat Stream**: `POST /api/v1/sessions/{id}/messages`
   - Route file: `apps/api/src/api/v1/endpoints/sessions.py:715-756`
   - Service file: `apps/api/src/api/services/session_chat_service.py:644-1135`
   - Response class: `StreamingResponse(media_type="text/event-stream")`
   - Headers declared in route (`sessions.py:751`):
     ```python
     headers={
         "Cache-Control": "no-cache",
         "Connection": "keep-alive",
         "X-Accel-Buffering": "no",
     }
     ```
   - Events emitted: `start`, `reasoning`, `token`, `citations`, `done`, `error`.
   - Event payload in `start` (`session_chat_service.py:708`):
     `start_payload = {"turn_id": str(turn_id), "message_id": f"msg_{turn_id.hex[:8]}", "created_at": now_iso}` (Lacks `request_id`).

4. *(Non-SSE streaming endpoints for completeness)*:
   - `GET /api/v1/documents/{document_id}/file`: `StreamingResponse(media_type="application/pdf")`
   - `POST /api/v1/sessions/{id}:export-bundle`: `StreamingResponse(media_type="application/zip")`

### 1.5. Web Client Consumers and Contract Expectations
- `apps/web/src/features/documents/api/documentsApi.ts:284-289`:
  Uses `@microsoft/fetch-event-source` to POST to `/documents/${documentId}/summary:stream`. Sends:
  ```typescript
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "text/event-stream",
    "X-Request-ID": finalRequestId,
  };
  ```
- `apps/web/src/features/sessions/api/sessionsApi.ts:168-173`:
  Uses `@microsoft/fetch-event-source` to POST to `/sessions/${sessionId}/messages`. Sends:
  ```typescript
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "text/event-stream",
    "X-Request-ID": finalRequestId,
  };
  ```
- `apps/web/src/features/dashboard/hooks/useStreamingChat.ts:284-289`:
  Sends `"X-Request-ID": finalRequestId`.
- **Browser EventSource Limitation**: While `@microsoft/fetch-event-source` can inspect HTTP response headers during `onopen(response)`, standard browser `EventSource` cannot access HTTP headers. Including `request_id` in the initial metadata event (`summary_start`, `start`) guarantees end-to-end trace correlation across all client runtimes.

### 1.6. Existing Test Verification
- All existing tests run via: `uv run pytest apps/api/tests`
  - Result: **212 passed, 1 warning** in **24.82s**.
- Search for `x-request-id` in tests:
  - Only `apps/api/tests/test_logging.py:24-32` (`test_health_check_returns_200_and_request_id`) tests `x-request-id`.
  - `test_sse_streaming_endpoint()` in `test_logging.py:89-100` tests `/events` chunks but **does NOT assert `x-request-id`**.
  - `test_stream_summary_success()` in `test_documents_summary_generate.py:543-562` tests `summary:stream` but **does NOT assert `x-request-id`**.
  - `test_post_session_message_sse_streaming_success()` in `test_sessions_chat.py:223-247` tests `/messages` but **does NOT assert `x-request-id`**.
  - `test_level_4_golden_paper_summary_streaming()` in `test_golden_papers_matrix.py:480-493` tests `summary:stream` but **does NOT assert `x-request-id`**.

---

## 2. Logic Chain

1. **Premise 1**: The user request and AGENTS.md Section 8 require standardizing the `X-Request-ID` header across all SSE streaming endpoints and adhering to `docs/vi/guide-logging-system.md`.
2. **Observation to Inference on Middleware (1.1, 1.3)**:
   - `PureASGITracingMiddleware` intercepts `http.response.start` and appends `(b"x-request-id", request_id.encode("latin1"))`.
   - Verified through runtime probe: `GET /events` and `POST /documents/{id}/summary:stream` DO return `x-request-id` in HTTP response headers.
   - However, `PureASGITracingMiddleware` fails to set `scope.setdefault("state", {})["request_id"] = request_id`.
   - Consequently, all route handlers, dependencies, and exception handlers (`api/__init__.py:121, 174, 222, 250`) get `getattr(request.state, "request_id", None) == None`. Error envelopes currently emit `"meta": {"request_id": null}`.
   - Furthermore, `res_headers.append((b"x-request-id", ...))` blindly appends without deduplication, risking duplicate headers.
3. **Observation to Inference on SSE Streams (1.4, 1.5)**:
   - The SSE endpoints (`/events`, `summary:stream`, `sessions/{id}/messages`) use `StreamingResponse` with `media_type="text/event-stream"`.
   - Neither `documents.py:1212` nor `sessions.py:751` explicitly declares `"X-Request-ID"` in the `headers` dictionary passed to `StreamingResponse`. While `PureASGITracingMiddleware` currently injects it into ASGI `http.response.start`, explicit declaration on `StreamingResponse` guarantees contract preservation even if middleware is bypassed or mock-tested in isolation.
   - Initial SSE event data payloads (`summary_start` in `document_service.py:2306` and `start` in `session_chat_service.py:708`) omit `request_id`. Providing `request_id` in these payloads guarantees browser clients (including standard EventSource) can correlate stream events with server traces.
4. **Observation to Inference on Logging Configuration (1.2)**:
   - `setup_logging()` in `api/core/logging.py` was created to configure structlog (processors, formatters, and muting `uvicorn.access`), but is never invoked.
   - Calling `setup_logging()` inside `apps/api/src/api/__init__.py` at module load time aligns with `docs/vi/guide-logging-system.md:65` and ensures unified structured logging.
5. **Observation to Inference on Test Coverage (1.6)**:
   - There is a complete lack of automated assertions for `X-Request-ID` on all 3 SSE endpoints (`/events`, `summary:stream`, `/sessions/{id}/messages`).
   - Standardizing `X-Request-ID` requires targeted test assertions in `test_logging.py`, `test_documents_summary_generate.py`, `test_sessions_chat.py`, and `test_golden_papers_matrix.py`.

---

## 3. Caveats

- **No Caveats** regarding the core problem boundary and findings.
- **Scope note**: `apps/web` client components (`documentsApi.ts`, `sessionsApi.ts`, `useStreamingChat.ts`) already send `"X-Request-ID": finalRequestId` in their request headers. No breaking changes are required in `apps/web`, but adding `request_id` into event payloads will be backward-compatible and immediately available to the frontend.

---

## 4. Conclusion & Actionable Blueprint

To comprehensively standardize `X-Request-ID` header and observability for all SSE streaming, the following 6 modules must be modified:

### 4.1. Middleware: `apps/api/src/api/middleware/tracing.py`
1. Set `request_id` on `scope["state"]`:
   ```python
   if "state" not in scope:
       scope["state"] = {}
   scope["state"]["request_id"] = request_id
   ```
2. Deduplicate `x-request-id` in `send_wrapper`:
   ```python
   # Filter out any pre-existing x-request-id to prevent duplicate headers
   res_headers = [(k, v) for k, v in message.get("headers", []) if k.lower() != b"x-request-id"]
   res_headers.append((b"x-request-id", request_id.encode("latin1")))
   message = {**message, "headers": res_headers}
   ```

### 4.2. Application Lifecycle & Logging: `apps/api/src/api/__init__.py`
1. Call `setup_logging()` at module import or inside `lifespan`:
   ```python
   from api.core.logging import setup_logging
   setup_logging()
   ```
2. In demo endpoint `GET /events`: Accept `request: Request` and emit `request_id` in progress data.

### 4.3. Document Summary Streaming: `apps/api/src/api/v1/endpoints/documents.py` & `document_service.py`
1. In `stream_document_summary` (`documents.py:1140-1217`):
   - Retrieve `request_id = getattr(request.state, "request_id", None) or request.headers.get("x-request-id") or str(uuid.uuid4())`.
   - Add `"X-Request-ID": request_id` to `StreamingResponse(headers={...})`.
   - Pass `request_id=request_id` to `service.stream_summary()`.
2. In `DocumentService.stream_summary` (`document_service.py:2295-2351`):
   - Include `"request_id": request_id` in `summary_start` payload.
   - Include `"request_id": request_id` in error payload.

### 4.4. Session Chat Streaming: `apps/api/src/api/v1/endpoints/sessions.py` & `session_chat_service.py`
1. In `post_session_message` (`sessions.py:728-756`):
   - Retrieve `request_id = getattr(request.state, "request_id", None) or request.headers.get("x-request-id") or str(uuid.uuid4())`.
   - Add `"X-Request-ID": request_id` to `StreamingResponse(headers={...})`.
   - Pass `request_id=request_id` to `chat_service.stream_chat()`.
2. In `SessionChatService.stream_chat` (`session_chat_service.py:644-725`):
   - Include `"request_id": request_id` in `start_payload`.
   - Include `"request_id": request_id` in `self.ai_tracing.trace(..., metadata={"request_id": request_id})` to link Langfuse traces with HTTP access logs.
   - Include `"request_id": request_id` in error event payloads.

### 4.5. Test Suite Enhancements:
1. `apps/api/tests/test_logging.py`:
   - Assert `x-request-id` header in `test_sse_streaming_endpoint`.
   - Assert custom `X-Request-ID` propagation in `/events`.
   - Assert `request.state.request_id` is populated in error envelope `meta["request_id"]`.
2. `apps/api/tests/test_documents_summary_generate.py`:
   - Assert `response.headers["x-request-id"]` is present and valid UUID.
   - Assert custom `X-Request-ID` propagation in `summary:stream`.
   - Assert `summary_start` event contains `"request_id"`.
3. `apps/api/tests/test_sessions_chat.py`:
   - Assert `resp.headers["x-request-id"]` is present and valid UUID.
   - Assert custom `X-Request-ID` propagation in `messages`.
   - Assert `start` event contains `"request_id"`.
4. `apps/api/tests/test_golden_papers_matrix.py`:
   - Assert `resp.headers["x-request-id"]` in `test_level_4_golden_paper_summary_streaming`.

---

## 5. Verification Method

To independently verify the observations, conclusions, and subsequent implementation:

1. **Run full API test suite**:
   ```bash
   uv run pytest apps/api/tests
   ```
   *Expected*: All 212 tests pass cleanly without errors.
2. **Run targeted SSE and logging tests**:
   ```bash
   uv run pytest apps/api/tests/test_logging.py -v
   uv run pytest apps/api/tests/test_documents_summary_generate.py -k "stream" -v
   uv run pytest apps/api/tests/test_sessions_chat.py -k "stream" -v
   uv run pytest apps/api/tests/test_golden_papers_matrix.py -k "stream" -v
   ```
3. **Verify Header & Context Invariant with Custom Trace**:
   Send HTTP request with custom `X-Request-ID`:
   ```bash
   uv run python -c "
   import asyncio
   from httpx import ASGITransport, AsyncClient
   from api import app

   async def check():
       transport = ASGITransport(app=app)
       async with AsyncClient(transport=transport, base_url='http://testserver') as client:
           r = await client.get('/events', headers={'X-Request-ID': 'test-trace-verify-001'})
           assert r.headers.get('x-request-id') == 'test-trace-verify-001'
           print('Verified X-Request-ID header on /events successfully.')
   asyncio.run(check())
   "
   ```
4. **Code Quality and Lint**:
   ```bash
   uv run ruff check apps/api
   uv run ruff format --check apps/api
   ```
   *Expected*: Zero errors, zero warnings.
