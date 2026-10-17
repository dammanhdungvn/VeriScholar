# Project: VeriScholar 100% Completion Across 5 Core Technology Pillars

## Architecture
VeriScholar operates as a monorepo containing:
- `packages/core`: Core domain logic, ports, entities (`ComparisonMatrixRow`, `ComparisonMatrixResult`, `Draft`, `ResearchNote`, `DocumentChunk`, `BoundingBox`), adapters (`RedisIdempotencyAdapter`, `ExaAcademicResolverAdapter`), and evaluation domain. Strict in-memory unit testing invariant with zero external network leaks.
- `apps/api`: FastAPI ASGI backend handling document ingestion, drafts lifecycle, LaTeX/Overleaf export (`POST /api/v1/drafts/{id}:export-overleaf`), proactive associative memory (`POST /api/v1/drafts/{id}/associative-suggestions`), literature comparison matrix (`POST /api/v1/folders/comparison-matrix`) with Redis query caching and multi-field search/pagination, and ARQ worker background jobs.
- `apps/web`: Vite 8 + React 19 web frontend with Writing Workspace (`WritingHeaderBar` with 1-Click Overleaf Launch, `AssociativeMemoryCard` floating recommendation card with 1-click citation insert) and Library Comparison Matrix (`ComparisonMatrixModal` with server-side pagination, multi-attribute filtering, and UTF-8 BOM CSV export).
- `deploy/`: On-premise enterprise deployment bundle (`docker-compose.enterprise.yml`, `Dockerfile.api`, `Dockerfile.web`, `nginx/verischolar.conf`, `pgbouncer/pgbouncer.ini`) orchestrating API, Web, PostgreSQL 16 + pgvector, Redis 7.2, ARQ Worker, and PgBouncer for air-gapped university and lab deployments.
- `scripts/`: Single-command enterprise installer (`bootstrap_enterprise.sh`).

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F1 | 1-Click Overleaf Direct Sync (Pillar 2) | Endpoint `POST /api/v1/drafts/{id}:export-overleaf` packing LaTeX snippet launch URL, and frontend toolbar button `header-overleaf-btn` in `WritingHeaderBar.tsx`. | M1 | Survey 1 |
| F2 | Proactive Scholarly Associative Memory (Pillar 3) | Endpoint `POST /api/v1/drafts/{id}/associative-suggestions` returning historical user notes matching draft content, and frontend floating `AssociativeMemoryCard.tsx` with 1-click citation insertion. | M1 | Survey 1 |
| F3 | Scalable 100+ Paper Comparison Matrix (Pillar 4) | Server-side pagination (`limit`, `offset`, `search`), multi-field filtering across Title, Methodology, Datasets, Metrics, Redis query caching in `LibrarySynthesisService`, frontend pagination alignment in `ComparisonMatrixModal.tsx`, and CSV export. | M1 | Survey 2 |
| F4 | Enterprise On-Premise Docker Compose Stack (Pillar 5) | Production-ready `deploy/docker-compose.enterprise.yml` configuring API, Web, PostgreSQL 16 pgvector with init.sql, Redis 7.2, PgBouncer, and ARQ worker with proper Nginx reverse proxy routing. | M2 | Survey 3 |
| F5 | Automated Enterprise Bootstrap Script (Pillar 5) | Turn-key single-command installer `scripts/bootstrap_enterprise.sh` with prerequisite checking, secrets generation, topology display, and syntax verification. | M2 | Survey 3 |
| F6 | Monorepo Test Baseline Harmonization & Ruff Cleanliness | Patch `exa_resolver.py` environment secret leak, resolve 12 ruff formatting/lint errors in `latex_healer.py` and `latex_linter.py`, ensuring 100% test pass rate across `pytest` and `vitest`. | M2 | Survey 3 |
| F7 | Monorepo Zero-Regression Acceptance & Forensic Audit | Comprehensive verification of 100% backend pytest, 100% frontend vitest, type checking (`tsc -b`), Challenger empirical verification, and Forensic Audit (`teamwork_preview_auditor`). | M3 | Synthesis |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1_WRITING_AND_SYNTHESIS | Pillars 2, 3 & 4: Overleaf 1-click sync, Associative Memory frontend wiring, Matrix Redis caching & 100+ papers pagination alignment. | none | DONE |
| 2 | M2_ENTERPRISE_AND_BASELINE | Pillar 5 & Baseline: Enterprise Docker Compose fixes, Nginx routing, `arq` dependency, `bootstrap_enterprise.sh`, and `exa_resolver` test leak fix + ruff linting. | none | IN_PROGRESS |
| 3 | M3_FINAL_ACCEPTANCE_AUDIT | Full Monorepo Zero-Regression Pass (Backend Pytest 100%, Frontend Vitest 100%, Challenger empirical stress testing, Forensic Integrity Audit CLEAN). | M1, M2 | PLANNED |

## Interface Contracts
### apps/api ↔ Overleaf 1-Click Launch
- **Endpoint**: `POST /api/v1/drafts/{id}:export-overleaf`
- **Response**: `SingleResponseEnvelope[OverleafExportResponse]` containing:
  - `draft_id`: UUID
  - `title`: string
  - `overleaf_url`: string (e.g. `https://www.overleaf.com/docs?snip=...&snip_name=...`)
  - `launch_url`: string (alias for `overleaf_url`)
  - `latex_snip`: string
  - `snip_length`: int

### apps/api ↔ Proactive Associative Suggestions
- **Endpoint**: `POST /api/v1/drafts/{id}/associative-suggestions`
- **Request**: `AssociativeSuggestionsRequest` (`content: str | None`, `text: str | None`, `limit: int`, `min_similarity: float`)
- **Response**: `SingleResponseEnvelope[AssociativeSuggestionsResponse]` containing:
  - `draft_id`: UUID
  - `suggestions`: list of `AssociativeSuggestionItem` (`note_id`, `paper_title`, `similarity_score`, `suggested_citation`, `reason`)

### apps/api ↔ Comparison Matrix (Pillar 4)
- **Endpoints**: `POST /api/v1/folders/comparison-matrix` and `POST /api/v1/folders/{id}/comparison-matrix`
- **Request**: `ComparisonMatrixRequest` (`topic: str`, `folder_id: UUID | None`, `document_ids: list[UUID] | None`, `search: str | None`, `limit: int` [default 50, max 200], `offset: int` [default 0])
- **Response**: `ComparisonMatrixEnvelope` containing:
  - `matrix_id`: UUID
  - `total_count`: int
  - `limit`: int
  - `offset`: int
  - `rows`: list of `ComparisonMatrixRowSchema`
  - `sufficiency`: `SufficiencyGateSchema`
  - `markdown_table`: str

### Enterprise Stack Contract
- **Database**: PostgreSQL 16 with `pgvector` extension initialized via `./infra/postgres/init.sql`.
- **Nginx Reverse Proxy**:
  - Web SPA root: `/usr/share/nginx/html;`
  - API Proxy: `proxy_pass http://api:8000;` (connecting to `verischolar-enterprise-api` container)
  - SSE Streaming routes: `proxy_buffering off;`, `proxy_cache off;`, `proxy_read_timeout 3600s;`.

## Code Layout
- `apps/api/src/api/v1/endpoints/drafts.py`: Drafts endpoints (Overleaf export, associative suggestions).
- `apps/api/src/api/services/draft_service.py`: Draft service with LaTeX export and Overleaf URL construction.
- `apps/api/src/api/services/associative_memory_service.py`: Associative memory matching service.
- `apps/api/src/api/v1/endpoints/folders.py`: Comparison matrix endpoints.
- `apps/api/src/api/services/library_synthesis_service.py`: Comparison matrix extraction, filtering, and Redis caching.
- `apps/api/src/api/core/config.py`: Application settings (`REDIS_URL`).
- `apps/api/src/api/deps.py`: Dependency injection for caching adapters.
- `apps/web/src/features/writing/components/WritingHeaderBar.tsx`: Overleaf 1-click launch button.
- `apps/web/src/features/writing/components/AssociativeMemoryCard.tsx`: Floating associative insight card.
- `apps/web/src/features/writing/components/WritingWorkspace.tsx`: Writing workspace view.
- `apps/web/src/features/writing/api/draftsApi.ts`: Drafts API client.
- `apps/web/src/features/library/components/ComparisonMatrixModal.tsx`: Comparison matrix modal.
- `apps/web/src/features/library/types/index.ts`: Library and matrix TypeScript types.
- `deploy/docker-compose.enterprise.yml`: Enterprise compose specification.
- `deploy/nginx/verischolar.conf`: Enterprise Nginx configuration.
- `scripts/bootstrap_enterprise.sh`: Automated enterprise bootstrap script.
- `packages/core/src/core/services/exa_resolver.py`: Academic resolver with env leak fix.
- `packages/core/src/core/services/latex_healer.py`: LaTeX healer service.
- `packages/core/src/core/services/latex_linter.py`: LaTeX linter service.
