# BRIEFING — 2026-10-15T02:34:30Z

## Mission
Survey PDF corpus, design 25 regression test cases across 3 seminal papers, and examine apps/web for Playwright E2E Auth Fixtures, SSE streaming, and Deep Reader interactions.

## 🔒 My Identity
- Archetype: explorer
- Roles: PDF corpus analysis, 25 test cases regression set design, Playwright E2E auth fixture design
- Working directory: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/explorer_survey_3
- Original parent: a2173842-299f-4803-8153-e166837e5cde
- Milestone: Survey & Architecture Discovery

## 🔒 Key Constraints
- Read-only investigation — do NOT implement
- Monorepo atomicity & AGENTS.md guidelines
- BoundingBox normalized coordinates invariant [x0, y0, x1, y1, page] top-left [0,1]
- Write only to our own teamwork directory (.agents/teamwork/explorer_survey_3)

## Current Parent
- Conversation ID: a2173842-299f-4803-8153-e166837e5cde
- Updated: 2026-10-15T02:34:30Z

## Investigation State
- **Explored paths**:
  * `data/papers/`, `storage/blobs/`, `storage/verischolar.db`
  * `apps/api/src/api/adapters/chunk_extractor.py`, `pdf_annotator.py`, `pdf_structure_extractor.py`
  * `apps/api/src/api/deps.py`, `auth_service.py`, `middleware/tracing.py`
  * `apps/web/package.json`, `src/features/auth/`, `src/features/dashboard/`, `src/features/reader/`
  * `apps/web/src/lib/api-client.ts`, `bounding-box-scaler.ts`
  * `apps/web/scripts/e2e-playwright-manual-audit.mjs`
- **Key findings**:
  * Attention paper is present in `data/papers/` and CAS storage; LoRA and Lewis et al. RAG need to be acquired into `data/papers/`.
  * Designed 25 deep regression test cases across 5 categories (multi-column tables/figures, formulas, BBoxes, hybrid search, negative queries).
  * Auth uses JWT Bearer tokens + `localStorage` (`verischolar_auth_token` & `verischolar_auth_user`).
  * Designed reusable Playwright E2E Auth fixture with two-tier architecture (`auth.setup.ts` + `authenticatedPage` with `page.addInitScript`).
  * Tracing: `PureASGITracingMiddleware` propagates `X-Request-ID` on `http.response.start` for SSE streams.
  * Deep Reader: `BboxHighlightLayer` dynamically renders normalized BoundingBoxes via CSS percentages.
- **Unexplored areas**: None for Phase 0 survey.

## Key Decisions Made
- Standardized fixture layout: full PDFs in `data/papers/`, unit test synthetic fixtures in `packages/core/tests/fixtures/corpus/`.
- Proposed `playwright.config.ts` and `authenticatedPage` fixture to eliminate manual login UI overhead.

## Artifact Index
- /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/explorer_survey_3/DISPATCH.md
- /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/explorer_survey_3/BRIEFING.md
- /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/explorer_survey_3/progress.md
- /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/explorer_survey_3/handoff.md
