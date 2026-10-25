# Phân Hệ 01: Kiến Trúc & Thiết Kế Hệ Thống (Architecture & System Design)

Phân hệ này tập hợp toàn bộ các tài liệu thiết kế nền tảng, nguyên lý kiến trúc lục giác (Hexagonal Architecture), mô hình dữ liệu quan hệ kết hợp vector và đồ thị tri thức (**PostgreSQL + `pgvector`**), tiêu chuẩn giao tiếp API và hàng rào bảo vệ trí tuệ nhân tạo của nền tảng **VeriScholar**, đồng bộ tuyệt đối với **[`docs/PRD/`](../PRD/00-overview-and-cleanup.md)**.

---

## 📑 DANH MỤC TÀI LIỆU TRONG PHÂN HỆ

1. **[Kiến Trúc Tổng Thể Hệ Thống (architecture-overview.md)](architecture-overview.md):**  
   Nguyên lý Hexagonal Architecture, ranh giới domain bất biến, sơ đồ luồng dữ liệu giữa API, Worker, Sandbox Broker và Web Client.

2. **[Toàn Cảnh Techstack Backend (backend-techstack.md)](backend-techstack.md):**  
   Hệ sinh thái Python 3.12, công cụ quản lý gói `uv`, FastAPI, SQLAlchemy 2.0 Async, **PostgreSQL + `pgvector`** (Relational + Vector + GraphRAG), Redis 7, ARQ Worker, PyMuPDF và Langfuse Tracing.

3. **[Thiết Kế Cơ Sở Dữ Liệu (database-design.md)](database-design.md):**  
   Lược đồ CSDL chi tiết trên PostgreSQL + `pgvector`: `users`, `folders`, `document_storage_blobs`, `documents`, `document_chunks`, `document_summaries`, `graph_nodes`, `graph_edges`, `reference_items`, `global_academic_cache`, `research_sessions`, `session_documents`, `session_turns`, `research_notes`, `drafts`.

4. **[Đặc Tả Tiêu Chuẩn Giao Tiếp API (api-specification.md)](api-specification.md):**  
   Quy chuẩn RESTful API, Server-Sent Events (SSE) streaming cho trợ lý Socratic Copilot, phân trang server-side (`limit`, `offset`), bộ lọc, định dạng lỗi chuẩn.

5. **[Hàng Rào An Toàn AI & Kiến Trúc RAG (ai-guardrails-and-rag.md)](ai-guardrails-and-rag.md):**  
   Kiến trúc Hybrid RAG + GraphRAG, trích xuất tọa độ Bounding Box, đóng băng ngữ cảnh XML CDATA và phòng chống ảo giác (Hallucination Mitigation).

6. **[Quản Lý Prompt & Persona Học Thuật (prompt-management.md)](prompt-management.md):**  
   Cấu trúc prompt phân tầng, định danh vai trò Socratic Mentor, kiểm soát ngân sách token linh hoạt.

7. **[Hồ Sơ Học Giả & An Ninh Định Danh (scholar-profile-and-identity.md)](scholar-profile-and-identity.md):**  
   Thiết kế phân hệ 3 Tabs đạt chuẩn Academic Luxury, tích hợp định danh ORCID iD quốc tế, Google Scholar, luồng xác thực Google Identity Services (GIS OAuth 2.0) và phòng thủ OIDC Confused Deputy Attack.

8. **[Cấu Trúc Thư Mục Backend & Hạt Nhân Lục Giác (directory-structure.md)](directory-structure.md):**  
   Tổ chức cây thư mục chuẩn Monorepo `uv workspace`: `apps/api` (Driving Adapters), `packages/core` (Pure Domain Entities & Ports), và các cơ chế cách ly I/O tuyệt đối.

9. **[Đặc Tả Ngoại Tuyến Swagger OpenAPI 3.1.0 (swagger-offline.md)](swagger-offline.md):**  
   Đặc tả chi tiết toàn bộ các schema, payload, request/response headers và mã phản hồi HTTP của hệ thống API.

---
*Thuộc Bộ Tài Liệu Kỹ Thuật VeriScholar MVP.*
