## 2026-10-15T02:36:18Z

You are worker_m1.
Your working directory is: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/worker_m1
Read the original user request at: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md
Read the project specifications at: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/PROJECT.md
Read the detailed survey report from explorer_survey_1 at: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/explorer_survey_1/handoff.md
Read the engineering guidelines in /home/dammanhdungvn/Downloads/Workspace/VeriScholar/AGENTS.md.
Also read skills:
/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/skills/fastapi/SKILL.md
/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/skills/verischolar-agent-protocol/SKILL.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

EXCLUSIVE WRITE OWNERSHIP:
You own these files exclusively. Concurrent workers will not touch them:
- apps/api/src/api/middleware/tracing.py
- apps/api/src/api/__init__.py
- apps/api/src/api/v1/endpoints/documents.py
- apps/api/src/api/services/document_service.py
- apps/api/src/api/v1/endpoints/sessions.py
- apps/api/src/api/services/session_chat_service.py
- apps/api/tests/test_logging.py
- apps/api/tests/test_documents_summary_generate.py
- apps/api/tests/test_sessions_chat.py
- apps/api/tests/test_golden_papers_matrix.py

TASK OBJECTIVES (Milestone 1: SSE Streaming & X-Request-ID Header Standardization):
1. In `apps/api/src/api/middleware/tracing.py`:
   - Set `scope.setdefault("state", {})["request_id"] = request_id` so that `request.state.request_id` is properly populated for all requests.
   - In `send_wrapper`, deduplicate `x-request-id` headers: filter out any pre-existing `b"x-request-id"` before appending canonical `(b"x-request-id", request_id.encode("latin1"))`.
2. In `apps/api/src/api/__init__.py`:
   - Import and invoke `setup_logging()` at module load / startup per `docs/vi/guide-logging-system.md:65`.
   - Update demo SSE endpoint `GET /events` to accept `request: Request` and emit `request_id` in its payload.
3. In `apps/api/src/api/v1/endpoints/documents.py` & `apps/api/src/api/services/document_service.py`:
   - In `stream_document_summary`: explicitly add `"X-Request-ID": request_id` to `StreamingResponse(headers=...)`. Retrieve `request_id` from `request.state.request_id` or headers. Pass `request_id` into `service.stream_summary()`.
   - In `DocumentService.stream_summary`: include `"request_id": request_id` in the `summary_start` event payload and error event payload.
4. In `apps/api/src/api/v1/endpoints/sessions.py` & `apps/api/src/api/services/session_chat_service.py`:
   - In `post_session_message`: explicitly add `"X-Request-ID": request_id` to `StreamingResponse(headers=...)`. Retrieve `request_id` from `request.state.request_id` or headers. Pass `request_id` into `chat_service.stream_chat()`.
   - In `SessionChatService.stream_chat`: include `"request_id": request_id` in `start` event payload, attach `request_id` to Langfuse trace metadata, and include in error event payload.
5. In API Test Suites:
   - In `apps/api/tests/test_logging.py`: Add tests asserting `x-request-id` header in `GET /events`, custom `X-Request-ID` propagation, and `request.state.request_id` presence in error envelope metadata.
   - In `apps/api/tests/test_documents_summary_generate.py`: Add assertions for `x-request-id` header and `"request_id"` in `summary_start`.
   - In `apps/api/tests/test_sessions_chat.py`: Add assertions for `x-request-id` header and `"request_id"` in `start`.
   - In `apps/api/tests/test_golden_papers_matrix.py`: Assert `x-request-id` header in streaming tests.
6. Verification & Quality Gates:
   - Run tests: `uv run pytest apps/api/tests/test_logging.py apps/api/tests/test_documents_summary_generate.py apps/api/tests/test_sessions_chat.py apps/api/tests/test_golden_papers_matrix.py`
   - Run full API test suite: `uv run pytest apps/api/tests`
   - Run linter & formatter: `uv run ruff check apps/api` and `uv run ruff format --check apps/api`
   - Verify all pass with 0 errors and 0 warnings.

Write your complete handoff report to:
/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/worker_m1/handoff.md
When done, notify parent (conversation ID: a2173842-299f-4803-8153-e166837e5cde) via send_message.
