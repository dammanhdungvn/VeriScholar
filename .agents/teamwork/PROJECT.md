# Project: VeriScholar Module 1 Comprehensive AI Evaluation Benchmark & Infrastructure

## Architecture
VeriScholar operates as a monorepo containing:
- `packages/core`: Core domain logic, ports, entities (`DocumentChunk`, `BoundingBox`), guardrails, and the new in-memory Evaluation Domain (`core/eval/`). Strict zero-external-network / zero-DB unit testing invariant.
- `apps/api`: FastAPI ASGI backend handling document ingestion, hybrid search, Cohere/local cross-encoder reranking, session chat, and SSE streaming. Includes `PureASGITracingMiddleware` for distributed tracing (`X-Request-ID`).
- `apps/web`: Vite 8 + React 19 web frontend with PDF.js Deep Reader canvas, dynamic percentage-scaled `BboxHighlightLayer`, Zustand auth storage (`verischolar_auth_token`), and Playwright E2E testing suite.

Data Flow & Evaluation Architecture:
```
[Public Benchmarks: QASPER, SciFact, PubMedQA] ──┐
                                                 ├──> [core/eval/adapters] ──> [EvalSample]
[Project Regression: 25 Cases (Attention,LoRA,RAG)] ┘                                 │
                                                                                      ▼
[Module 1 Engine: Retrieval + Rerank + Grounding + Generation] <─── [BenchmarkRunner]
                               │
                               ▼
[Evaluation Metrics: TokenF1, Recall@k, ClassificationF1, BBoxIoU, Geometry, Safety]
                               │
                               ▼
                    [BenchmarkReport Scorecard]
```

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F1 | ASGI Tracing Middleware & Request ID State | Set `scope["state"]["request_id"]`, deduplicate headers, and call `setup_logging()` in `api/__init__.py`. | M1 | Survey 1 |
| F2 | SSE Streaming X-Request-ID Standardization | Explicit `X-Request-ID` header on `GET /events`, `POST /summary:stream`, `POST /messages`, and embed `request_id` in initial event payloads. | M1 | Survey 1 |
| F3 | Hexagonal Evaluation Domain Architecture | Standardized in-memory models (`EvalSample`, `MetricResult`, `BenchmarkReport`), base adapter port, and decoupled metrics in `packages/core/src/core/eval/`. | M2 | Survey 2 |
| F4 | Public Benchmark Adapters (QASPER, SciFact, PubMedQA) | Dataset adapters for QASPER, SciFact, and PubMedQA with in-memory offline subset fixtures for unit tests. | M2 | Survey 2 |
| F5 | Project Regression Set (25 Test Cases) | 5x5 deep test matrix across Attention, LoRA, and RAG covering layout, equations, bounding boxes, hybrid search, and negative queries. | M3 | Survey 3 |
| F6 | Playwright E2E Auth Fixture | Two-tier Playwright fixture (`auth.fixture.ts` with `authenticatedPage` using `page.addInitScript`) in `apps/web`. | M4 | Survey 3 |
| F7 | Web E2E Verification Tests | Playwright E2E specs for Deep Reader BoundingBox overlays and SSE streaming with `X-Request-ID`. | M4 | Survey 3 |
| F8 | Final E2E Suite, Dual-Track Runner & Adversarial Audit | Integrated benchmark runner (`scripts/eval/run_eval.py`), 100% test pass across monorepo, challenger verification, and forensic audit. | M5 | Synthesis |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1_SSE_TRACING | SSE Streaming & X-Request-ID Header Standardization in `apps/api` | none | DONE |
| 2 | M2_PUBLIC_BENCHMARKS | Core Evaluation Domain & Public Benchmark Suite (QASPER, SciFact, PubMedQA) in `packages/core` | none | IN_PROGRESS |
| 3 | M3_REGRESSION_CORPUS | Project Regression Set (25 Test Cases across Attention, LoRA, RAG Corpus) & decoupled metrics runner | M2 | PLANNED |
| 4 | M4_PLAYWRIGHT_AUTH | Playwright E2E Auth Fixture & Web E2E Verification in `apps/web` | M1 | PLANNED |
| 5 | M5_FINAL_ACCEPTANCE | Dual-Track Acceptance, E2E CLI Runner, Full Suite Pass & Forensic Audit | M1, M2, M3, M4 | PLANNED |

## Interface Contracts
### apps/api ↔ Client / SSE Streaming
- **Headers**:
  - `X-Request-ID`: Client-provided UUID4 string or server-generated UUID4 string. Must be present on all HTTP responses, including SSE `text/event-stream` responses.
  - `Content-Type`: `text/event-stream`
  - `Cache-Control`: `no-cache`
- **Initial Event Payload**:
  - `summary:stream` -> event `summary_start`: `{"document_id": str, "status": "streaming", "request_id": str}`
  - `/messages` -> event `start`: `{"turn_id": str, "message_id": str, "created_at": str, "request_id": str}`

### packages/core Evaluation Domain ↔ Benchmark Adapters
- **Domain Value Objects**:
  - `BoundingBox`: `[x0, y0, x1, y1, page]`, `x0 < x1`, `y0 < y1`, `page >= 1`, normalized floats `[0.0, 1.0]`, Top-Left origin.
- **Evaluation Sample Contract (`core.eval.models.EvalSample`)**:
  - `id`: `str`
  - `dataset`: `"qasper" | "scifact" | "pubmedqa" | "project_regression"`
  - `split`: `str` ("dev" | "test" | "train")
  - `paper_id`: `str`
  - `paper_title`: `str`
  - `query`: `str`
  - `ground_truth_answers`: `list[str]`
  - `ground_truth_evidence`: `list[dict[str, Any]]`
  - `ground_truth_bboxes`: `list[list[float]]` (normalized `[x0, y0, x1, y1, page]`)
  - `metadata`: `dict[str, Any]`

### apps/web ↔ Playwright Auth Contract
- `localStorage` Keys:
  - `verischolar_auth_token`: JWT string with claims `{"sub": UUID, "email": str, "role": str, "exp": int}`
  - `verischolar_auth_user`: Serialized JSON string conforming to `UserProfile` (`id`, `email`, `full_name`, `role`, etc.)

## Code Layout
- `apps/api/src/api/middleware/tracing.py`: Pure ASGI tracing middleware (`scope["state"]["request_id"]`, header deduplication).
- `apps/api/src/api/__init__.py`: App lifespan, `setup_logging()` invocation, `/events` endpoint.
- `apps/api/src/api/v1/endpoints/documents.py`: `stream_document_summary` endpoint.
- `apps/api/src/api/services/document_service.py`: `DocumentService.stream_summary` with `request_id`.
- `apps/api/src/api/v1/endpoints/sessions.py`: `post_session_message` endpoint.
- `apps/api/src/api/services/session_chat_service.py`: `SessionChatService.stream_chat` with `request_id`.
- `packages/core/src/core/eval/`: Core evaluation domain (models, adapters, metrics, runner).
- `packages/core/tests/eval/`: In-memory evaluation unit test suite & offline subset fixtures.
- `scripts/eval/`: CLI benchmark evaluation runner and full benchmark dataset downloaders.
- `data/papers/`: Full PDF benchmark corpus (Attention, LoRA, RAG).
- `apps/web/playwright.config.ts`: Playwright test runner configuration.
- `apps/web/tests/fixtures/auth.fixture.ts`: Two-tier Playwright E2E auth fixture.
- `apps/web/tests/e2e/`: End-to-end test specifications.
