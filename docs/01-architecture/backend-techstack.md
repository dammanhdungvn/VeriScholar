# Toàn Cảnh Công Nghệ Backend (Comprehensive Backend Techstack & Architecture)

Tài liệu này cung cấp cái nhìn tổng thể về hệ sinh thái công nghệ, cấu trúc Monorepo, các thư viện phụ thuộc cốt lõi và các nguyên tắc thiết kế tầng máy chủ (Backend Services) của nền tảng **VeriScholar**, đồng bộ với **[`docs/PRD/`](../PRD/00-overview-and-cleanup.md)**.

---

## 0. BẢNG THUẬT NGỮ CÔNG NGHỆ BACKEND (FRESHER GLOSSARY)

| Thuật ngữ | Khái niệm kỹ thuật | Giải thích trực quan cho Fresher |
| :--- | :--- | :--- |
| **Monorepo** | Single Repository Architecture | Toàn bộ mã nguồn backend API, worker ngầm, và thư viện domain lõi nằm chung trong một kho mã nguồn duy nhất, quản lý bằng công cụ siêu tốc `uv`. |
| **Hexagonal Ports** | Abstract Domain Interfaces | Các lớp trừu tượng (Interface/Protocol) định nghĩa những gì tầng nghiệp vụ cần (ví dụ: `VectorStorePort`, `LLMClientPort`) mà không quan tâm bên dưới dùng công nghệ gì. |
| **Pure ASGI Tracing** | Zero-Overhead ASGI Middleware | Tầng trung gian can thiệp trực tiếp vào giao thức ASGI, chịu trách nhiệm sinh `x-request-id` (`trace_id`), đo lường độ trễ mạng và xử lý hủy kết nối sớm HTTP 499. |
| **Idempotent DDL** | Add Column If Not Exists | Lệnh cập nhật bảng dữ liệu an toàn, chạy lặp lại nhiều lần mà không gây lỗi hoặc khóa bảng trong quá trình nâng cấp sản xuất (Zero-Downtime). |
| **Content-Addressable Storage (CAS)** | SHA-256 Blob Storage | Lưu trữ tệp dựa trên mã băm nội dung: Hai người dùng cùng tải lên một tệp PDF giống nhau chỉ lưu đúng 1 bản vật lý trên đĩa cứng kèm bộ đếm tham chiếu (`ref_count`). |

---

## 1. BẢNG MA TRẬN CÔNG NGHỆ BACKEND (TECHSTACK MATRIX)

| Thành phần | Công nghệ / Thư viện | Phiên bản | Vai trò & Mục đích trong MVP |
| :--- | :--- | :--- | :--- |
| **Ngôn ngữ cốt lõi** | Python | `>= 3.12` | Hỗ trợ cú pháp gõ tĩnh nâng cao, cú pháp type parameter PEP 695, và hiệu năng asyncio vượt trội. |
| **Quản trị Monorepo** | Astral `uv` | `>= 0.5.0` | Quản lý phụ thuộc cực nhanh, khóa phụ thuộc tất định qua `uv.lock`. |
| **Web API Gateway** | FastAPI + Uvicorn | `0.115+` / `0.34+` | Cung cấp RESTful APIs chuẩn OpenAPI, hỗ trợ SSE streaming không đệm và xử lý bất đồng bộ cao. |
| **CSDL Quan hệ, Vector & Đồ thị** | PostgreSQL + `pgvector` | `16+` / `0.7+` | Lưu trữ dữ liệu quan hệ ACID, tìm kiếm vector HNSW (`document_chunks`), và lưu trữ đồ thị tri thức **GraphRAG** (`graph_nodes`, `graph_edges`, `citation_edges`). |
| **ORM & Database Driver** | SQLAlchemy (Async) + `asyncpg` | `2.0+` / `0.30+` | Truy vấn cơ sở dữ liệu phi đồng bộ hoàn toàn, kiểm soát Transactional boundaries an toàn. |
| **Bộ nhớ đệm & Task Queue** | Redis + ARQ | `7+` / `0.26+` | Quản lý phiên làm việc, Rate-limiting, và hàng đợi xử lý PDF ngầm. |
| **Trích xuất PDF Học thuật** | PyMuPDF (`fitz` / `pymupdf`) | `1.25+` | Trích xuất văn bản có tọa độ hình học (Bounding Box `[x0, y0, x1, y1, page]`), nhận diện cột và bảng biểu. |
| **Mô hình Trí tuệ Nhân tạo** | OpenAI / Cloud LLM Client | `1.50+` | Xử lý suy luận sâu, Socratic Mentorship, trích xuất thực thể GraphRAG và hỗ trợ soạn thảo LaTeX (`assist`). |
| **Đo lường & Quan sát AI** | Langfuse Tracing SDK | `2.50+` | Truy vết độ trễ suy luận LLM, thống kê chi phí token trên 2 project tách biệt (`verischolar-dev` và `verischolar-prod`). |
| **Nhật ký Cấu trúc** | Structlog | `24.4+` | Ghi log chuẩn định dạng JSON, correlation ID (`trace_id`), tự động bọc lọc che giấu thông tin nhạy cảm (PII). |
| **Định danh & OAuth 2.0** | Google Identity Services (GIS) | OIDC RFC | Xác thực tài khoản Google học thuật, kiểm tra chặt chẽ `aud == GOOGLE_CLIENT_ID` chống Confused Deputy. |

---

## 2. KIẾN TRÚC MONOREPO & BỐ CỤC THƯ MỤC (MONOREPO TOPOLOGY)

```
VeriScholar/
├── apps/
│   ├── api/                          # Web Gateway Application (FastAPI)
│   │   ├── src/api/
│   │   │   ├── core/                 # Cấu hình môi trường (config.py), security, logging
│   │   │   ├── db/                   # Kết nối cơ sở dữ liệu (session.py, init_db.py, models/)
│   │   │   ├── v1/endpoints/         # Bộ định tuyến API v1 (auth, sessions, documents, drafts, notes, folders)
│   │   │   └── services/             # Lớp dịch vụ điều phối (auth_service, document_service, draft_service, etc.)
│   │   └── tests/                    # Bộ kiểm thử Pytest tích hợp & bảo mật
│   └── web/                          # Ứng dụng Web Client (React 19 + TypeScript + Vite)
├── packages/
│   └── core/                         # Nghiệp vụ miền lõi độc lập hoàn toàn (Hexagonal Domain Core)
│       └── src/core/
│           ├── domain/               # Thực thể nghiệp vụ thuần túy (Entities, Value Objects)
│           ├── ports/                # Cổng giao tiếp trừu tượng (Retrieval, Latex, Storage, Academic Resolver)
│           └── services/             # Các dịch vụ miền & adapters (Exa/Arxiv/Crossref Resolver, LaTeX Compiler/Healer)
```

---

## 3. NGUYÊN TẮC BẢO VỆ RANH GIỚI BẤT BIẾN (HEXAGONAL BOUNDARY INVARIANTS)

1. **Tính Trong Sạch của `packages/core`:**
   - Tuyệt đối không import bất kỳ thư viện I/O hay framework web nào (`fastapi`, `sqlalchemy`, `docker`, `fitz`, `uvicorn`) vào thư mục `packages/core/src/core/domain/`.
   - Vi phạm quy tắc này sẽ bị chặn đứng ngay lập tức tại chốt chặn CI `Hexagonal Boundary Check`.
2. **Chiến Lược Quản Lý Phiên CSDL Ngắt Sớm (Early Connection Release):**
   - Khi truyền luồng chữ thời gian thực (Server-Sent Events) cho Socratic Copilot, kết nối cơ sở dữ liệu bắt buộc phải được đóng/trả lại Connection Pool ngay sau khi đọc xong dữ liệu ban đầu. Không bao giờ giữ kết nối CSDL trong suốt quá trình LLM streaming.
3. **Bảo Mật Xác Thực GIS OAuth 2.0:**
   - Endpoint xác thực Google `POST /api/v1/auth/google` bắt buộc phải đối chiếu trường `aud` từ Google Tokeninfo với `settings.GOOGLE_CLIENT_ID` để triệt tiêu hoàn toàn nguy cơ tấn công OIDC Confused Deputy Attack.

---
*Thuộc Bộ Tài Liệu Kỹ Thuật VeriScholar MVP.*
