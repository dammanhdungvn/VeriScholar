# Trung Tâm Tài Liệu Kỹ Thuật VeriScholar (Master Technical Documentation)

Chào mừng bạn đến với kho lưu trữ tài liệu kỹ thuật chính thức của nền tảng **VeriScholar** — Hệ thống Phân tích & Trợ lý Nghiên cứu Khoa học Đẳng cấp Quốc tế dành cho Học giả và Viện Nghiên cứu.

Tất cả các tài liệu được xây dựng theo chuẩn mực kỹ thuật phân tán hiện đại, bảo đảm tính toàn vẹn thông tin, tính khả thi vận hành và quy chuẩn an toàn bảo mật nghiêm ngặt.

---

## 📚 MỤC LỤC TÀI LIỆU TOÀN DIỆN (DOCUMENTATION INDEX)

### 1. Kiến Trúc & Thiết Kế Hệ Thống (Architecture & System Design)
- **[Thiết Kế Kiến Trúc Tổng Thể (System Architecture)](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/design-architecture.md):** Tổng quan kiến trúc đa thành phần Monorepo, Hexagonal Architecture, ranh giới các domain và luồng dữ liệu.
- **[Thiết Kế Cơ Sở Dữ Liệu (Database Design)](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/design-database.md):** Lược đồ CSDL PostgreSQL 16, pgvector, triggers OCC (`handle_occ_and_timestamp`), chiến lược chỉ mục và mô hình dữ liệu.
- **[Hồ Sơ Học Giả & Nhận Diện Học Thuật (Scholar Profile Architecture)](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/guide-academic-profile.md):** Ngôn ngữ Academic Luxury, cấu trúc 3 Tabs, ORCID iD, Google Scholar, Google GIS OAuth 2.0 và cơ chế phòng thủ OIDC Confused Deputy Attack (CVSS 8.8).
- **[Thiết Kế API Chuẩn Mực (API Design)](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/design-api.md):** Quy chuẩn RESTful API, Server-Sent Events (SSE) streaming, phân trang server-side và xử lý mã lỗi HTTP.
- **[Đặc Tả Yêu Cầu Sản Phẩm (PRD)](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/PRD.md):** Yêu cầu sản phẩm, hành trình người dùng và tiêu chí chấp nhận 5 trụ cột công nghệ.

### 2. Đường Ống CI/CD & Vận Hành Sản Xuất (CI/CD & Production Operations)
- **[Hướng Dẫn Đường Ống Tích Hợp Liên Tục CI (CI Quality Gates Guide)](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/guide-ci.md):** 9 chốt chặn chất lượng trong `.github/workflows/ci.yml`: Ruff lint/format, Pytest coverage, Hexagonal boundary, Secret scanning (Gitleaks), Oxlint, TypeScript compiler, Vitest Frontend Suite, và Docker Container Validation.
- **[Hướng Dẫn Triển Khai Liên Tục CD & Vận Hành (CD & Production Operations)](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/guide-cd-and-deployment.md):** Kịch bản triển khai tự động `scripts/deploy_production.sh`, Zero-Downtime Migration (`init_db.py`), Nginx Reverse Proxy & SSL, Systemd daemon management (`verischolar-api.service`), automated health check và cơ chế Auto-Rollback khi gặp sự cố.
- **[Hướng Dẫn Triển Khai Docker & On-Premise Enterprise (Docker Guide)](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/guide-docker.md):** Khởi chạy cụm dịch vụ On-Premise (`deploy/docker-compose.enterprise.yml`), PgBouncer, pgvector, Redis và ARQ Worker bằng script `scripts/bootstrap_enterprise.sh`.

### 3. Giao Diện Người Dùng & Frontend Web (Frontend Engineering)
- **[Kiến Trúc Frontend & Design System](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/frontend/techstack-frontend.md):** React 19, TypeScript, Vite, Tailwind CSS, Zustand store, và Lucide React icons.
- **[Cấu Trúc Thư Mục Frontend](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/frontend/directory-structure.md):** Bố cục tính năng theo chuẩn Feature-Driven Development (`features/auth`, `features/reader`, `features/writing`, `features/library`, `features/dashboard`).
- **[Tiêu Chuẩn Mã Nguồn Frontend](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/frontend/coding-standards.md):** Quy tắc viết mã, quản lý Hooks, định kiểu dữ liệu nghiêm ngặt và tối ưu hóa kết xuất DOM.

### 4. Trí Tuệ Nhân Tạo & Khả Năng Quan Sát (AI & Observability)
- **[Hàng Rào Bảo Vệ An Toàn AI (AI Guardrails)](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/design-ai-guardrails.md):** Phòng chống Hallucination, phát hiện thiên kiến và xác thực ngữ nghĩa trích dẫn học thuật.
- **[Khả Năng Quan Sát & Đo Lường AI (AI Observability)](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/guide-ai-observability.md):** Giám sát độ trễ LLM, đo lường chi phí token và truy vết luồng suy luận qua Langfuse.
- **[Hệ Thống Nhật Ký Có Cấu Trúc (Structured Logging System)](file:///home/VeriScholar/Workspace/VeriScholar/docs/vi/guide-logging-system.md):** Chuẩn mực Structlog JSON, PureASGITracingMiddleware, correlation ID (`x-request-id`), và bộ lọc thông tin nhạy cảm PII redaction.

### 5. Hồ Sơ Bàn Giao & Kiểm Toán Chất Lượng (Handoff & Audit Records)
- **[Hồ Sơ Bàn Giao & Kiểm Toán Toàn Diện](file:///home/VeriScholar/Workspace/VeriScholar/docs/handoff/README.md):** Nhật ký kiểm định UAT, chứng chỉ nghiệm thu Quality Gates, và báo cáo thử nghiệm Beta Cohort.

---

## 🚀 HƯỚNG DẪN KHỞI ĐỘNG NHANH CHO LẬP TRÌNH VIÊN (QUICK START)

```bash
# 1. Sao chép kho mã nguồn
git clone https://github.com/verischolar/verischolar.git
cd verischolar

# 2. Cài đặt phụ thuộc Backend (Python 3.12 + uv)
uv sync --all-packages

# 3. Cài đặt phụ thuộc Frontend (Node.js 20 + pnpm)
pnpm --dir apps/web install

# 4. Chạy kiểm thử chất lượng toàn diện
uv run pytest
pnpm --dir apps/web test:run

# 5. Khởi động môi trường phát triển
# Terminal 1: Backend API
uv run uvicorn api:app --reload --host 127.0.0.1 --port 8000
# Terminal 2: Frontend Web UI
pnpm --dir apps/web dev
```

---
*Bản quyền © 2026 VeriScholar. Mọi quyền được bảo lưu.*
