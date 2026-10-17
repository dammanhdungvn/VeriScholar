# Toàn Cảnh Công Nghệ Backend 5 Trụ Cột (Comprehensive Backend Techstack & Architecture)

Tài liệu này cung cấp cái nhìn tổng thể về hệ sinh thái công nghệ, cấu trúc Monorepo, các thư viện phụ thuộc cốt lõi và các nguyên tắc thiết kế tầng máy chủ (Backend Services) phục vụ trọn vẹn **5 Trụ Cột Công Nghệ** của nền tảng **VeriScholar**.

---

## 0. BẢNG THUẬT NGỮ CÔNG NGHỆ BACKEND (FRESHER GLOSSARY)

| Thuật ngữ | Khái niệm kỹ thuật | Giải thích trực quan cho Fresher |
| :--- | :--- | :--- |
| **Monorepo** | Single Repository Architecture | Toàn bộ mã nguồn backend API, worker ngầm, và thư viện domain lõi nằm chung trong một kho mã nguồn duy nhất, quản lý bằng công cụ siêu tốc `uv`. |
| **Hexagonal Ports** | Abstract Domain Interfaces | Các lớp trừu tượng (Interface/Protocol) định nghĩa những gì tầng nghiệp vụ cần (ví dụ: `VectorStorePort`, `LLMClientPort`) mà không quan tâm bên dưới dùng công nghệ gì. |
| **Pure ASGI Tracing** | Zero-Overhead ASGI Middleware | Tầng trung gian can thiệp trực tiếp vào giao thức ASGI (không qua framework wrapper nặng), chịu trách nhiệm sinh `x-request-id`, đo lường độ trễ mạng và xử lý hủy kết nối sớm HTTP 499. |
| **Idempotent DDL** | Add Column If Not Exists | Lệnh cập nhật bảng dữ liệu an toàn, chạy lặp lại nhiều lần mà không gây lỗi hoặc khóa bảng trong quá trình nâng cấp sản xuất (Zero-Downtime). |
| **Content-Addressable Storage (CAS)** | SHA-256 Blob Storage | Lưu trữ tệp dựa trên mã băm nội dung: Hai người dùng cùng tải lên một tệp PDF giống nhau chỉ lưu đúng 1 bản vật lý trên đĩa cứng kèm bộ đếm tham chiếu (`ref_count`). |

---

## 1. BẢNG MA TRẬN CÔNG NGHỆ 5 TRỤ CỘT (TECHSTACK MATRIX)

| Thành phần | Công nghệ / Thư viện | Phiên bản | Vai trò & Mục đích trong 5 Trụ Cột |
| :--- | :--- | :--- | :--- |
| **Ngôn ngữ cốt lõi** | Python | `>= 3.12` | Hỗ trợ cú pháp gõ tĩnh nâng cao, cú pháp type parameter PEP 695, và hiệu năng asyncio vượt trội. |
| **Quản trị Monorepo** | Astral `uv` | `>= 0.5.0` | Quản lý phụ thuộc cực nhanh (thay thế Poetry/Pipenv), khóa phụ thuộc tất định qua `uv.lock`. |
| **Web API Gateway** | FastAPI + Uvicorn | `0.115+` / `0.34+` | Cung cấp RESTful APIs chuẩn OpenAPI, hỗ trợ SSE streaming không đệm và xử lý bất đồng bộ cao. |
| **CSDL Quan hệ & Vector** | PostgreSQL + `pgvector` | `16+` / `0.7+` | Lưu trữ dữ liệu quan hệ ACID, bảng biểu, metadata và tìm kiếm độ tương đồng cosine dense vectors (HNSW). |
| **ORM & Database Driver** | SQLAlchemy (Async) + `asyncpg` | `2.0+` / `0.30+` | Truy vấn cơ sở dữ liệu phi đồng bộ hoàn toàn, kiểm soát Transactional boundaries an toàn. |
| **Bộ nhớ đệm & Task Queue** | Redis + ARQ | `7+` / `0.26+` | Quản lý phiên làm việc, Rate-limiting, bộ nhớ đệm ma trận 100+ bài báo, và hàng đợi xử lý PDF ngầm. |
| **Trích xuất PDF Học thuật** | PyMuPDF (`fitz` / `pymupdf`) | `1.25+` | Trích xuất văn bản có tọa độ hình học (Bounding Box `[x0, y0, x1, y1]`), nhận diện cột và bảng biểu. |
| **Mô hình Trí tuệ Nhân tạo** | OpenAI / Luna API Client | `1.50+` | Xử lý suy luận sâu, Socratic Mentorship, kiểm chứng sự thật SAFE và tổng hợp bài viết. |
| **Đo lường & Quan sát AI** | Langfuse Tracing SDK | `2.50+` | Truy vết độ trễ suy luận LLM, thống kê chi phí token và giám sát chất lượng phản hồi. |
| **Nhật ký Cấu trúc** | Structlog | `24.4+` | Ghi log chuẩn định dạng JSON, correlation ID theo luồng request, tự động bọc lọc che giấu thông tin nhạy cảm (PII). |
| **Định danh & OAuth 2.0** | Google Identity Services (GIS) | OIDC RFC | Xác thực tài khoản Google học thuật, kiểm tra chặt chẽ `aud == GOOGLE_CLIENT_ID` chống Confused Deputy. |

---

## 2. KIẾN TRÚC MONOREPO & BỐ CỤC THƯ MỤC (MONOREPO TOPOLOGY)

```
VeriScholar/
├── apps/
│   ├── api/                          # Web Gateway Application (FastAPI)
│   │   ├── src/api/
│   │   │   ├── core/                 # Cấu hình môi trường (config.py), security
│   │   │   ├── db/                   # Kết nối cơ sở dữ liệu (session.py, init_db.py)
│   │   │   ├── routers/              # Bộ định tuyến API v1 (auth, sessions, documents, drafts, notes, matrix)
│   │   │   └── services/             # Lớp dịch vụ điều phối (auth_service, document_service, etc.)
│   │   └── tests/                    # Bộ kiểm thử Pytest tích hợp & bảo mật
│   ├── worker/                       # Cụm tiến trình xử lý tác vụ nặng ngầm (ARQ Ingestion Worker)
│   └── sandbox-broker/               # Dịch vụ biên dịch mã LaTeX cô lập (gVisor / Kernel Sandbox)
├── packages/
│   └── core/                         # Nghiệp vụ miền lõi độc lập hoàn toàn (Hexagonal Domain Core)
│       └── src/core/
│           ├── domain/               # Thực thể nghiệp vụ thuần túy (Entities, Value Objects, Domain Events)
│           ├── ports/                # Cổng giao tiếp trừu tượng (VectorStorePort, LLMClientPort)
│           └── usecases/             # Các kịch bản nghiệp vụ (ChunkDocument, SynthesizeDraft, etc.)
```

---

## 3. NGUYÊN TẮC BẢO VỆ RANH GIỚI BẤT BIẾN (HEXAGONAL BOUNDARY INVARIANTS)

1. **Tính Trong Sạch của `packages/core`:**
   - Tuyệt đối không import bất kỳ thư viện I/O hay framework web nào (`fastapi`, `sqlalchemy`, `docker`, `fitz`, `uvicorn`) vào thư mục `packages/core/src/core/domain/`.
   - Vi phạm quy tắc này sẽ bị chặn đứng ngay lập tức tại chốt chặn CI `Hexagonal Boundary Check`.
2. **Chiến Lược Quản Lý Phiên CSDL Ngắt Sớm (Early Connection Release):**
   - Khi truyền luồng chữ thời gian thực (Server-Sent Events) kéo dài hàng chục giây cho Socratic Copilot, kết nối cơ sở dữ liệu bắt buộc phải được đóng/trả lại Connection Pool ngay sau khi đọc xong dữ liệu ban đầu. Không bao giờ giữ kết nối CSDL trong suốt quá trình LLM streaming.
3. **Bảo Mật Xác Thực GIS OAuth 2.0:**
   - Endpoint xác thực Google `POST /api/v1/auth/google` bắt buộc phải đối chiếu trường `aud` từ Google Tokeninfo với `settings.GOOGLE_CLIENT_ID` để triệt tiêu hoàn toàn nguy cơ tấn công OIDC Confused Deputy Attack (CVSS 8.8).

---
*Thuộc Bộ Tài Liệu Kỹ Thuật VeriScholar Enterprise.*
