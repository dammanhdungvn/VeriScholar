# Master Plan — VeriScholar 100% Completion Across 5 Core Technology Pillars

## Objective
Elevate VeriScholar to 100% completion across all 5 core technology pillars:
1. Pillar 2 (LaTeX Writing): 1-Click Overleaf Integration (`POST /api/v1/drafts/{id}:export-overleaf` & UI Launch Button)
2. Pillar 3 (Knowledge Capital & 2-Tier RAG): Proactive Scholarly Associative Memory (`POST /api/v1/drafts/{id}/associative-suggestions` & UI Insight Card)
3. Pillar 4 (Multi-Paper Synthesis): Scalable 100+ Paper Comparison Matrix with Server-Side Pagination, Filtering & CSV Export
4. Pillar 5 (Enterprise Scalability): Full On-Premise Enterprise Docker Compose stack & automated single-command bootstrap script

## Phase 0: Survey & Codebase Exploration
- [ ] Explorer 1: Pillars 2 & 3 (LaTeX draft endpoints, Overleaf form/payload specs, UI writing workspace, notes/annotations storage, semantic associative memory logic).
- [ ] Explorer 2: Pillar 4 (Comparison Matrix endpoints, database query/pagination, Redis caching, frontend matrix virtualized grid, search, column filters, CSV export).
- [ ] Explorer 3: Pillar 5 & Baseline Testing (Docker compose configs, Postgres pgvector, Redis, PgBouncer, ARQ worker, bootstrap scripts, and full baseline pytest/vitest pass).
- [ ] Synthesize Survey results into updated `PROJECT.md` (Feature Inventory, Architecture, Milestones, Code Layout).

## Milestone 1: Pillar 2 — 1-Click Overleaf Integration
- Backend: Endpoint `POST /api/v1/drafts/{id}:export-overleaf` generates valid Overleaf launch URL / snippet form data with LaTeX source, bibtex, and authentication payload.
- Frontend: Writing workspace provides "Đồng bộ Overleaf (1-Click)" button that opens draft directly in Overleaf.
- Verification: Pytest endpoint tests + Vitest UI component tests.

## Milestone 2: Pillar 3 — Proactive Scholarly Associative Memory
- Backend: Endpoint `POST /api/v1/drafts/{id}/associative-suggestions` returns relevant historical user research notes matching draft content using semantic embedding / trigram similarity.
- Frontend: Writing UI displays floating "Spark of Insight" recommendation card with one-click citation insertion.
- Verification: Unit tests for associative memory matching + API tests + Vitest UI tests.

## Milestone 3: Pillar 4 — Scalable 100+ Paper Comparison Matrix
- Backend: Matrix API supporting server-side pagination (`limit`, `offset`, `search`), column filtering across Methodology, Datasets, Metrics, and Redis query caching for heavy extractions. CSV export endpoint/utility.
- Frontend: Comparison matrix virtualized rendering for large collections (100+ papers) with smooth search and filtering.
- Verification: Matrix performance & pagination pytest tests + Vitest virtualized table tests.

## Milestone 4: Pillar 5 — Enterprise On-Premise Deployment Package
- Architecture: `deploy/docker-compose.enterprise.yml` and `scripts/bootstrap_enterprise.sh`.
- Services: API, Web, PostgreSQL 16 pgvector, Redis 7, ARQ Worker, PgBouncer for air-gapped university and lab deployments.
- Verification: Docker compose config validation, shell script syntax/execution check (`bash -n`), configuration tests.

## Milestone 5: Final Acceptance, Dual-Track E2E Test Suite & Adversarial Hardening
- 100% tests pass on backend (`uv run pytest`) and frontend (`pnpm --prefix apps/web exec tsc -b`, `pnpm --prefix apps/web test`).
- Zero regressions across existing benchmarks and modules.
- Forensic Integrity Audit (`teamwork_preview_auditor`).
