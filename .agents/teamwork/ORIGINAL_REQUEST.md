# Original User Request

## 2026-10-15T02:24:31Z

Triển khai bộ kiểm chuẩn đánh giá chất lượng AI toàn diện cho Module 1 (Scholar Reading & Deep Reader), kết hợp giữa Public Benchmarks uy tín (QASPER, SciFact, PubMedQA) và Project Regression Set (25 test cases chuyên sâu bằng corpus PDF thực tế: Attention Is All You Need, LoRA, RAG), bổ sung Playwright E2E Auth Fixture và chuẩn hóa header X-Request-ID cho toàn bộ SSE streaming.
## 2026-10-16T12:03:58Z

Elevate VeriScholar to 100% completion across all 5 core technology pillars:
1. Pillar 2 (LaTeX Writing): 1-Click Overleaf Integration (`POST /api/v1/drafts/{id}:export-overleaf` & UI Launch Button)
2. Pillar 3 (Knowledge Capital & 2-Tier RAG): Proactive Scholarly Associative Memory (`POST /api/v1/drafts/{id}/associative-suggestions` & UI Insight Card)
3. Pillar 4 (Multi-Paper Synthesis): Scalable 100+ Paper Comparison Matrix with Server-Side Pagination, Filtering & CSV Export
4. Pillar 5 (Enterprise Scalability): Full On-Premise Enterprise Docker Compose stack & automated single-command bootstrap script

Working directory: /home/VeriScholar/Workspace/VeriScholar
Integrity mode: production-deployed

## Requirements

### R1. Overleaf 1-Click Sync Integration (Pillar 2 -> 100%)
Implement a seamless one-click Overleaf launch workflow allowing researchers to instantly open their drafts directly in Overleaf without manual ZIP download/upload. The backend provides an Overleaf launch endpoint packing LaTeX source and bibtex into an authenticated ephemeral payload; the frontend provides an intuitive "Đồng bộ Overleaf (1-Click)" button.

### R2. Proactive Scholarly Associative Memory (Pillar 3 -> 100%)
Build a proactive "Second Brain" association engine that continuously cross-references active writing drafts against historical user research notes using semantic embedding / trigram similarity. When a researcher drafts a section similar to past annotations, the UI proactively displays a floating "Spark of Insight" recommendation card with one-click citation insertion.

### R3. Scalable 100+ Paper Comparison Matrix (Pillar 4 -> 100%)
Upgrade the Literature Comparison Matrix to handle large-scale libraries (100+ papers) with server-side pagination (`limit`, `offset`, `search`), Redis query caching, client-side virtualized rendering, and real-time column filtering across Methodology, Datasets, and Metrics.

### R4. Enterprise On-Premise Deployment Package (Pillar 5 -> 100%)
Create a turn-key enterprise deployment bundle (`deploy/docker-compose.enterprise.yml` and `scripts/bootstrap_enterprise.sh`) orchestrating API, Web, PostgreSQL 16 pgvector, Redis 7, ARQ Worker, and PgBouncer for air-gapped university and lab deployments.

## Acceptance Criteria

### Functional Quality Criteria
- [x] `POST /api/v1/drafts/{id}:export-overleaf` generates valid Overleaf launch URL / snippet form data
- [x] Frontend Writing Workspace provides "Đồng bộ Overleaf" button opening draft directly in Overleaf
- [x] `POST /api/v1/drafts/{id}/associative-suggestions` returns relevant historical notes matching draft content
- [x] Writing UI renders associative insight card with one-click citation insert
- [x] Matrix API supports pagination (`limit`, `offset`, `search`) and caches heavy extractions in Redis
- [x] Comparison Matrix UI renders smoothly for large collections with search and filtering
- [x] `deploy/docker-compose.enterprise.yml` and `scripts/bootstrap_enterprise.sh` pass syntax and configuration validation
- [x] Backend Pytest and Frontend Vitest suites pass 100% with zero regressions
