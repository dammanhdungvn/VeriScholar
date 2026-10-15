# Master Plan — VeriScholar Module 1 Comprehensive AI Evaluation Benchmark & Infrastructure

## Objective
Triển khai bộ kiểm chuẩn đánh giá chất lượng AI toàn diện cho Module 1 (Scholar Reading & Deep Reader), kết hợp giữa Public Benchmarks (QASPER, SciFact, PubMedQA) và Project Regression Set (25 test cases chuyên sâu bằng corpus PDF thực tế: Attention Is All You Need, LoRA, RAG), bổ sung Playwright E2E Auth Fixture và chuẩn hóa header X-Request-ID cho toàn bộ SSE streaming.

## Phase 0: Survey & Investigation
- [ ] Survey 1: SSE Streaming endpoints, ASGI tracing middleware, `X-Request-ID` propagation in `apps/api`.
- [ ] Survey 2: Module 1 architecture in `packages/core` (parsers, chunkers, hybrid search, grounding, reranking) & existing eval harness.
- [ ] Survey 3: Benchmark dataset formats (QASPER, SciFact, PubMedQA), PDF corpus files, and Playwright E2E auth fixture setup in `apps/web`.
- [ ] Synthesize Survey results into `PROJECT.md` (Feature Inventory, Architecture, Milestones, Code Layout).

## Milestone 1: SSE Streaming & X-Request-ID Header Standardization
- Ensure ASGI middleware extracts or generates `X-Request-ID` (`uuid4`).
- Standardize all SSE streaming responses (`apps/api`) to include `X-Request-ID` header and emit event-level tracing/metadata.
- Ensure clients/tests receive `X-Request-ID` consistently.
- Verification: Unit & API integration tests for SSE endpoints and middleware.

## Milestone 2: Module 1 Public Benchmarks Adapter & Evaluators (QASPER, SciFact, PubMedQA)
- Build evaluation adapters/loaders for:
  - QASPER (Question Answering on Scholarly Pages with Evidence Retrieval)
  - SciFact (Scientific claim verification / citation support)
  - PubMedQA (Biomedical question answering)
- Implement metrics: Retrieval Recall@k, Grounding Precision/F1, Faithfulness / Citation Accuracy, normalized BoundingBox validation.
- In-memory test execution adhering to Ports & Adapters, zero live network during unit eval tests.

## Milestone 3: Project Regression Test Set (25 Test Cases on Real PDF Corpus)
- Corpus: Attention Is All You Need, LoRA, RAG papers.
- Define 25 targeted test cases across retrieval, chunking, math/table extraction, bounding box grounding, and citation verification.
- Implement automated regression runner with scoring and threshold gates.

## Milestone 4: Playwright E2E Auth Fixture & Web Integration
- In `apps/web`: Create reusable Playwright Auth fixture (mocked/stored state or session bypass) for end-to-end tests.
- Add E2E tests verifying Deep Reader UI with SSE streaming receiving `X-Request-ID` and rendering grounding bounding boxes.

## Phase 5: Final Acceptance, Dual-Track E2E Test Suite & Adversarial Hardening
- 100% test pass on backend (`uv run pytest`) and frontend (`pnpm --prefix apps/web exec tsc -b`, `pnpm --prefix apps/web lint`).
- Forensic Audit verification (`teamwork_preview_auditor`).
- Adversarial review & final completion handoff.
