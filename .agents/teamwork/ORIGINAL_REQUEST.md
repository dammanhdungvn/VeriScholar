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


## 2026-10-17T03:52:20Z

Nâng cấp và hoàn thiện toàn diện hệ thống CI/CD của VeriScholar đạt chuẩn Production Enterprise (100/100): Khắc phục triệt để lỗ hổng thiếu kiểm thử Vitest trong CI, tự động hóa kiểm tra tính toàn vẹn Docker Container Images, và thiết lập quy trình Continuous Deployment (CD) tự động với Zero-Downtime Database Migration và cơ chế Auto-Rollback khi gặp sự cố.

Working directory: /home/VeriScholar/Workspace/VeriScholar
Integrity mode: development

## Requirements

### R1. Tích hợp Đầy đủ Bộ Kiểm thử Frontend (Vitest) vào CI Quality Gates
Bổ sung bước thực thi tự động toàn bộ test suite Frontend (`pnpm test:run`) vào job `frontend-checks` trong `.github/workflows/ci.yml`. Cấu hình xuất kết quả JUnit XML và đảm bảo CI từ chối dứt khoát mọi Pull Request nếu có bất kỳ bài test client nào bị fail.

### R2. Tự động hóa Kiểm thử Container & Hạ tầng Docker (Docker Gate)
Bổ sung job `docker-validation` trong CI workflow nhằm kiểm tra cú pháp cấu hình `deploy/docker-compose.enterprise.yml` và xác thực khả năng build thành công của cả hai container images (`deploy/Dockerfile.api` và `deploy/Dockerfile.web`) với Docker Buildx cache để tối ưu hóa thời gian chạy.

### R3. Xây dựng Pipeline Continuous Deployment (CD) Tự động với Zero-Downtime & Auto-Rollback
Thiết lập quy trình CD tự động (`.github/workflows/cd.yml` hoặc kịch bản tự động hóa triển khai production):
- Tự động kích hoạt khi có commit merge vào nhánh `main`.
- Đồng bộ mã nguồn mới nhất, thực thi migration CSDL an toàn (`init_db.py` với `ADD COLUMN IF NOT EXISTS`).
- Triển khai static bundle lên Web Server Nginx và khởi động lại API Backend không gián đoạn dịch vụ.
- Tự động kiểm tra sức khỏe endpoint `https://verischolar.duckdns.org/health` sau khi triển khai; nếu không phản hồi HTTP 200 trong vòng 30 giây, hệ thống tự động Rollback về commit ổn định trước đó.

### R4. Thẩm định Kiến trúc & Cấp Chứng chỉ Quality Gate
Lead Quality Gatekeeper tiến hành kiểm toán độc lập toàn bộ cú pháp YAML, kiểm thử mô phỏng các kịch bản lỗi, đo lường tổng thời gian chạy CI/CD (đảm bảo hoàn tất dưới 5 phút), và chính thức cấp chứng chỉ Quality Gate Pass.

## Verification Resources
- GitHub Actions workflow: `.github/workflows/ci.yml`
- Docker compose configuration: `deploy/docker-compose.enterprise.yml`
- Dockerfiles: `deploy/Dockerfile.api`, `deploy/Dockerfile.web`
- Deployment scripts: `scripts/deploy_web.sh`
- Health check endpoint: `https://verischolar.duckdns.org/health`

## Acceptance Criteria

### Continuous Integration (CI Quality Gates)
- [ ] File `.github/workflows/ci.yml` có bước chạy `pnpm test:run` cho frontend, đảm bảo 83/83 tests được thực thi tự động.
- [ ] Bất kỳ bài test nào fail ở cả Backend (Pytest) hoặc Frontend (Vitest) đều khiến CI báo đỏ và chặn merge PR.
- [ ] Cú pháp `docker-compose.enterprise.yml` và các Dockerfile được kiểm tra tính hợp lệ tự động trong CI.
- [ ] Thời gian thực thi toàn bộ pipeline CI trên GitHub Actions duy trì dưới 5 phút nhờ cơ chế cache (`uv cache`, `pnpm cache`, `docker cache`).

### Continuous Deployment (CD Quality Gates)
- [ ] Có kịch bản CD tự động triển khai mã nguồn mới khi merge vào nhánh `main`.
- [ ] Quy trình migration CSDL bảo đảm Zero-Downtime (idempotent DDL).
- [ ] Cơ chế tự động kiểm tra sức khỏe endpoint `/health` và kích hoạt Rollback tự động nếu dịch vụ không khởi động thành công.
- [ ] Môi trường Production Live tại `https://verischolar.duckdns.org` hoạt động ổn định và nhận được chứng chỉ nghiệm thu Quality Gate Pass.
