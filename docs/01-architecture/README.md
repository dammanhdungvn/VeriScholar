# Phân Hệ 01: Kiến Trúc & Thiết Kế Hệ Thống (Architecture & System Design)

Phân hệ này tập hợp toàn bộ các tài liệu thiết kế nền tảng, nguyên lý kiến trúc lục giác (Hexagonal Architecture), mô hình dữ liệu quan hệ kết hợp vector, tiêu chuẩn giao tiếp API và hàng rào bảo vệ trí tuệ nhân tạo của nền tảng **VeriScholar**.

---

## 📑 DANH MỤC TÀI LIỆU TRONG PHÂN HỆ

1. **[Kiến Trúc Tổng Thể & 5 Trụ Cột Công Nghệ (architecture-overview.md)](file:///home/VeriScholar/Workspace/VeriScholar/docs/01-architecture/architecture-overview.md):**  
   Nguyên lý Hexagonal Architecture, ranh giới domain bất biến, sơ đồ luồng dữ liệu giữa API, Worker, Sandbox Broker và Web Client.

2. **[Toàn Cảnh Techstack Backend 5 Trụ Cột (backend-techstack.md)](file:///home/VeriScholar/Workspace/VeriScholar/docs/01-architecture/backend-techstack.md):**  
   Hệ sinh thái Python 3.12, công cụ quản lý gói `uv`, FastAPI, SQLAlchemy 2.0 Async, PostgreSQL 16 pgvector, Redis 7, ARQ Worker, PyMuPDF và Langfuse Tracing.

3. **[Thiết Kế Cơ Sở Dữ Liệu (database-design.md)](file:///home/VeriScholar/Workspace/VeriScholar/docs/01-architecture/database-design.md):**  
   Lược đồ CSDL chi tiết cho toàn bộ các thực thể: `users`, `sessions`, `documents`, `chunks`, `notes`, `drafts`, `folders`, `comparisons`. Các trigger OCC (`handle_occ_and_timestamp`), trigger ngắt nguồn (`handle_note_source_detached`) và chỉ mục vector HNSW.

4. **[Đặc Tả Tiêu Chuẩn Giao Tiếp API (api-specification.md)](file:///home/VeriScholar/Workspace/VeriScholar/docs/01-architecture/api-specification.md):**  
   Quy chuẩn RESTful API, Server-Sent Events (SSE) streaming cho trợ lý Socratic Copilot, phân trang server-side (`limit`, `offset`), bộ lọc, định dạng lỗi chuẩn RFC 7807 (Problem Details).

5. **[Hàng Rào An Toàn AI & Kiến Trúc 2-Tier RAG (ai-guardrails-and-rag.md)](file:///home/VeriScholar/Workspace/VeriScholar/docs/01-architecture/ai-guardrails-and-rag.md):**  
   Kiến trúc RAG 2 tầng, trích xuất tọa độ Bounding Box (Page Dimension & Rotation Invariant), thuật toán ghép bảng (Table Stitching), phát hiện tiền đề câu hỏi (Presupposition Validation) và phòng chống ảo giác (Hallucination Mitigation).

6. **[Quản Lý Prompt & Persona Học Thuật (prompt-management.md)](file:///home/VeriScholar/Workspace/VeriScholar/docs/01-architecture/prompt-management.md):**  
   Cấu trúc prompt phân tầng, định danh vai trò Socratic Mentor, kiểm soát ngân sách token linh hoạt (Elastic Table Budgeting).

7. **[Hồ Sơ Học Giả & An Ninh Định Danh (scholar-profile-and-identity.md)](file:///home/VeriScholar/Workspace/VeriScholar/docs/01-architecture/scholar-profile-and-identity.md):**  
   Thiết kế phân hệ 3 Tabs đạt chuẩn Academic Luxury, tích hợp định danh ORCID iD quốc tế, Google Scholar, luồng xác thực Google Identity Services (GIS OAuth 2.0) và giải pháp phòng thủ tuyệt đối trước lỗ hổng OIDC Confused Deputy Attack (CVSS 8.8).

8. **[Cấu Trúc Thư Mục Backend & Hạt Nhân Lục Giác (directory-structure.md)](file:///home/VeriScholar/Workspace/VeriScholar/docs/01-architecture/directory-structure.md):**  
   Tổ chức cây thư mục chuẩn Monorepo `uv workspace`: `apps/api` (Driving Adapters), `packages/core` (Pure Domain Entities & Ports), và các cơ chế cách ly I/O tuyệt đối.

9. **[Đặc Tả Ngoại Tuyến Swagger OpenAPI 3.1.0 (swagger-offline.md)](file:///home/VeriScholar/Workspace/VeriScholar/docs/01-architecture/swagger-offline.md):**  
   Đặc tả chi tiết toàn bộ các schema, payload, request/response headers và mã phản hồi HTTP của toàn hệ thống API phục vụ tích hợp độc lập không phụ thuộc backend runtime.

---
*Thuộc Bộ Tài Liệu Kỹ Thuật VeriScholar Enterprise.*
