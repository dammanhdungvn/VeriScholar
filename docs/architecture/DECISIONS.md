# Nhật Ký Quyết Định Kiến Trúc (Architectural Decision Records - ADRs)

Tài liệu này ghi lại toàn bộ các quyết định kiến trúc quan trọng (**Architectural Decision Records**), phân tích đánh đổi kỹ thuật (**Trade-off Analysis**), lý do lựa chọn công nghệ, các phương án thay thế, và cam kết vận hành an toàn cho hệ thống **VeriScholar**.

Tuân thủ **Quy luật thứ nhất của Kiến trúc Phần mềm**: *"Mọi thứ trong kiến trúc phần mềm đều là một sự đánh đổi (Everything is a trade-off)"*.

---

## MỤC LỤC CÁC QUYẾT ĐỊNH (ADR INDEX)

- [ADR-001: Kiến Trúc Phân Tách Hexagonal Architecture & Quy Chuẩn Ranh Giới Monorepo](#adr-001-kiến-trúc-phân-tách-hexagonal-architecture--quy-chuẩn-ranh-giới-monorepo)
- [ADR-002: Khử Trùng Lặp Tệp Vật Lý Bằng Content-Addressable Storage (CAS) & Cam Kết Zero-Retention](#adr-002-khử-trùng-lặp-tệp-vật-lý-bằng-content-addressable-storage-cas--cam-kết-zero-retention)
- [ADR-003: Cơ Sở Dữ Liệu Hợp Nhất PostgreSQL 18 + pgvector Thay Vì Dedicated Vector DB](#adr-003-cơ-sở-dữ-liệu-hợp-nhất-postgresql-18--pgvector-thay-vì-dedicated-vector-db)
- [ADR-004: Tìm Kiếm Hỗn Hợp Dense-Sparse Bằng Thuật Toán Reciprocal Rank Fusion (RRF)](#adr-004-tìm-kiếm-hỗn-hợp-dense-sparse-bằng-thuật-toán-reciprocal-rank-fusion-rrf)
- [ADR-005: Kiểm Soát Sửa Đổi Đồng Thời Bằng Khóa Lạc Quan Cấp Giao Thức (RFC 9110 / RFC 7232 OCC)](#adr-005-kiểm-soát-sửa-đổi-đồng-thời-bằng-khóa-lạc-quan-cấp-giao-thức-rfc-9110--rfc-7232-occ)
- [ADR-006: Phòng Vệ Đa Tầng 3-Tier AI Guardrails & XML Context Sandboxing](#adr-006-phòng-vệ-đa-tầng-3-tier-ai-guardrails--xml-context-sandboxing)
- [ADR-007: Kiến Trúc Biên Dịch Sandbox Cô Lập Qua Microservice Riêng Biệt (gVisor runsc)](#adr-007-kiến-trúc-biên-dịch-sandbox-cô-lập-qua-microservice-riêng-biệt-gvisor-runsc)
- [ADR-008: Hàng Đợi Tác Vụ Bền Vững Bằng Redis Streams Thay Vì In-Memory BackgroundTasks](#adr-008-hàng-đợi-tác-vụ-bền-vững-bằng-redis-streams-thay-vì-in-memory-backgroundtasks)
- [ADR-009: Giám Sát Phân Tán Pure ASGI Tracing Middleware & TTFB Real-time](#adr-009-giám-sát-phân-tán-pure-asgi-tracing-middleware--ttfb-real-time)
- [ADR-010: Chiến Lược Chuyển Đổi Định Danh Người Dùng Thật (True Production Auth & RBAC)](#adr-010-chiến-lược-chuyển-đổi-định-danh-người-dùng-thật-true-production-auth--rbac)
- [ADR-011: Chia Sẻ Công Khai Zero-Auth & Cơ Chế Thu Hồi Tức Thì (HTTP 410 Gone Instant Revocation)](#adr-011-chia-sẻ-công-khai-zero-auth--cơ-chế-thu-hồi-tức-thì-http-410-gone-instant-revocation)
- [ADR-012: Không Gian Soạn Thảo Bản Thảo Học Thuật, Khóa Lạc Quan OCC & SAFE Fact-Checking](#adr-012-không-gian-soạn-thảo-bản-thảo-học-thuật-khóa-lạc-quan-occ--safe-fact-checking)

---


## ADR-001: Kiến Trúc Phân Tách Hexagonal Architecture & Quy Chuẩn Ranh Giới Monorepo

- **Trạng thái:** `Đã phê duyệt & Đang áp dụng (Accepted)`
- **Ngày quyết định:** 2026-09-01
- **Phạm vi tác động:** Toàn bộ backend (`packages/core`, `apps/api`, `apps/worker`)

### 1. Bối cảnh & Vấn đề kỹ thuật
Hệ thống VeriScholar đòi hỏi khả năng hoán đổi linh hoạt giữa các nhà cung cấp mô hình AI (OpenAI, Gemini, Local Docker Model Runner), công cụ bóc tách PDF (PyMuPDF, Docling, Azure Document Intelligence), và các bộ lưu trữ (Local Disk CAS, S3/MinIO). Nếu nhúng trực tiếp code FastAPI hoặc SQLAlchemy vào logic RAG, hệ thống sẽ gặp hiện tượng "Architecture Sinkhole" và vi phạm nghiêm trọng nguyên lý đơn nhiệm (SRP).

### 2. Quyết định
Áp dụng **Hexagonal Architecture (Ports & Adapters)** kết hợp cấu trúc `uv workspace`:
1. `packages/core`: Hạt nhân nghiệp vụ thuần túy chứa Domain Entities, Value Objects, Use Cases (Inbound Ports), và Interfaces (Outbound Ports). Tuyệt đối không import FastAPI, SQLAlchemy, Uvicorn, hay Docker.
2. `apps/api`: Driving Adapter tiếp nhận HTTP/SSE, chuyển đổi DTO sang Domain Models và gọi Use Cases.
3. Chiều phụ thuộc duy nhất: Phụ thuộc luôn hướng tâm từ ngoài vào trong (`apps/api` -> `packages/core`).

### 3. Các phương án đã xem xét (Alternatives)
- *Phương án A: Layered Architecture truyền thống (Controller -> Service -> Repository).* Nhược điểm: Service phụ thuộc chặt chẽ vào ORM models, khó viết unit test in-memory không cần DB.
- *Phương án B: Clean Architecture / Hexagonal (Được chọn).* Ưu điểm: Domain testable 100% in-memory, dễ thay đổi adapter.

### 4. Đánh đổi kỹ thuật (Trade-offs)
- **Độ phức tạp (Complexity):** Tăng thêm tầng abstraction (Ports, DTO mapping), đòi hỏi đội ngũ tuân thủ quy tắc ranh giới nghiêm ngặt.
- **Khả năng bảo trì & Kiểm thử (Maintainability & Testability):** Tuyệt đối vượt trội; unit tests chạy hoàn toàn độc lập với tốc độ < 10ms.

---

## ADR-002: Khử Trùng Lặp Tệp Vật Lý Bằng Content-Addressable Storage (CAS) & Cam Kết Zero-Retention

- **Trạng thái:** `Đã phê duyệt & Đang áp dụng (Accepted)`
- **Ngày quyết định:** 2026-09-02
- **Phạm vi tác động:** `packages/core/domain/entities/blob.py`, `apps/api/src/api/db/models/blob.py`, `LocalStorageAdapter`

### 1. Bối cảnh & Vấn đề kỹ thuật
Nhiều người dùng thường xuyên nạp các bài báo kinh điển giống nhau. Nếu lưu trữ nhiều bản sao vật lý sẽ gây lãng phí dung lượng đĩa và tốn chi phí gọi mô hình embedding lặp lại. Tuy nhiên, nếu dùng chung bản ghi tài liệu sẽ vi phạm tính riêng tư của người dùng (Multi-tenancy) và không thể đáp ứng cam kết bảo mật **Zero Data Retention** khi người dùng yêu cầu xóa tài liệu.

### 2. Quyết định
Tách biệt giữa **Khối dữ liệu nhị phân vật lý (Storage Blob)** và **Thực thể tài liệu người dùng (Document Entity)**:
1. Lưu file vật lý tại `storage/blobs/{content_hash}.pdf` theo mã băm SHA-256 nội dung.
2. Bảng `document_storage_blobs` theo dõi `ref_count` (số người đang tham chiếu).
3. Mỗi người dùng luôn sở hữu một bản ghi `documents` riêng biệt.
4. Khi xóa bài báo: Xóa cascade bản ghi `documents` của người dùng đó. `ref_count` giảm 1. File vật lý chỉ bị xóa khi `ref_count == 0`.

### 3. Đánh đổi kỹ thuật (Trade-offs)
- **Đánh đổi:** Cần quản lý giao dịch ACID cẩn thận khi tăng/giảm `ref_count` để tránh race condition dẫn đến dangling files hoặc xóa sớm.
- **Lợi ích:** Tiết kiệm tới 80% dung lượng đĩa cho các bài báo phổ biến; tốc độ phản hồi upload cho file trùng hash giảm từ 15 giây xuống < 500ms.

---

## ADR-003: Cơ Sở Dữ Liệu Hợp Nhất PostgreSQL 18 + pgvector Thay Vì Dedicated Vector DB

- **Trạng thái:** `Đã phê duyệt & Đang áp dụng (Accepted)`
- **Ngày quyết định:** 2026-09-03
- **Phạm vi tác động:** `infra/postgres`, `apps/api/src/api/db`

### 1. Bối cảnh & Vấn đề kỹ thuật
Cần lựa chọn hệ thống lưu trữ vector cho các chunks văn bản (1536 chiều từ `text-embedding-3-small` hoặc 1024 chiều từ `BGE-M3`) phục vụ truy vấn Hybrid RAG.

### 2. Quyết định
Sử dụng **PostgreSQL 18** tích hợp extension **`pgvector`** (chỉ mục `HNSW` với `vector_cosine_ops`, `m=16`, `ef_construction=64`).

### 3. Các phương án đã xem xét (Alternatives)
- *Phương án A: Sử dụng Dedicated Vector Database (Milvus, Qdrant, Pinecone).*
  - *Nhược điểm:* Phải quản lý Dual-Write giữa Relational DB (metadata, users, notes) và Vector DB, phát sinh rủi ro mất đồng bộ dữ liệu (Distributed Dual-Write Inconsistency), tăng chi phí vận hành và số container cần duy trì.
- *Phương án B: PostgreSQL 18 + pgvector (Được chọn).*
  - *Ưu điểm:* Toàn bộ dữ liệu quan hệ, chunks, vectors, JSONB và Full-text search nằm trong một giao dịch ACID duy nhất. Khi xóa tài liệu, `ON DELETE CASCADE` xóa sạch vector ngay lập tức, không để lại dữ liệu rác.

### 4. Đánh đổi kỹ thuật (Trade-offs)
- **Thông lượng (Throughput):** Dedicated Vector DB có thể xử lý hàng chục triệu vectors nhanh hơn, nhưng quy mô tài liệu học thuật của từng viện/nhóm nghiên cứu (hàng chục ngàn đến vài triệu vectors) hoàn toàn nằm trong vùng tối ưu của PostgreSQL HNSW (< 10ms truy vấn).
- **Vận hành (Operational Overhead):** Đơn giản, chỉ cần duy trì 1 container DB duy nhất, dễ dàng backup và khôi phục toàn vẹn.

---

## ADR-004: Tìm Kiếm Hỗn Hợp Dense-Sparse Bằng Thuật Toán Reciprocal Rank Fusion (RRF)

- **Trạng thái:** `Đã phê duyệt & Đang áp dụng (Accepted)`
- **Ngày quyết định:** 2026-09-04
- **Phạm vi tác động:** `packages/core/src/core/services/search.py`, `apps/api/src/api/services/document_service.py`

### 1. Bối cảnh & Vấn đề kỹ thuật
Tìm kiếm ngữ nghĩa thuần túy (Dense Vector Search) thường bỏ sót các từ khóa học thuật chính xác, tên riêng tác giả, ký hiệu hóa học hoặc công thức toán. Ngược lại, tìm kiếm từ khóa thuần túy (Lexical Search) không hiểu được từ đồng nghĩa hoặc ngữ nghĩa ngữ cảnh.

### 2. Quyết định
Kết hợp Dense Vector Search (`<=>` Cosine Distance) và Sparse Lexical Search (`to_tsvector('simple', content)`) trực tiếp trong PostgreSQL bằng công thức **Reciprocal Rank Fusion (RRF)**:
$$\text{RRF\_Score} = \frac{1.0}{60 + \text{Dense\_Rank}} + \frac{1.0}{60 + \text{Lexical\_Rank}}$$
Sau đó, các chunk ứng viên được xếp hạng lại qua tầng **Cross-Encoder Reranker** (`Cohere Rerank v3.5` hoặc `bge-reranker-large`) với ngưỡng cắt độ liên quan: $\text{score} \ge 0.35$.

### 3. Đánh đổi kỹ thuật (Trade-offs)
- **Độ trễ (Latency):** Tăng thêm ~80-150ms cho bước Rerank, nhưng toàn bộ pipeline vẫn hoàn tất dưới 2 giây, thỏa mãn nghiêm ngặt SLA < 5s của PRD.
- **Chất lượng (Accuracy):** Triệt tiêu 95% hiện tượng nhầm lẫn ngữ cảnh và lọc sạch các đoạn văn gây nhiễu (Distractor Mitigation).

---

## ADR-005: Kiểm Soát Sửa Đổi Đồng Thời Bằng Khóa Lạc Quan Cấp Giao Thức (RFC 9110 / RFC 7232 OCC)

- **Trạng thái:** `Đã phê duyệt & Đang áp dụng (Accepted)`
- **Ngày quyết định:** 2026-09-05
- **Phạm vi tác động:** `research_notes`, `drafts`, `research_sessions`

### 1. Bối cảnh & Vấn đề kỹ thuật
Khi người dùng mở ứng dụng trên nhiều tab trình duyệt hoặc thao tác sửa ghi chú / bản thảo liên tục, rủi ro ghi đè mất dữ liệu (Lost Update Problem) là rất cao nếu không có cơ chế khóa đồng thời.

### 2. Quyết định
Triển khai cơ chế **Optimistic Concurrency Control (OCC)** chuẩn giao thức HTTP RFC 9110 / RFC 7232:
1. Mọi bản ghi có sửa đổi đều có cột `version INT NOT NULL DEFAULT 1`.
2. Database Trigger `handle_occ_and_timestamp()` tự động tăng `NEW.version = OLD.version + 1` khi UPDATE.
3. Server trả về header `ETag: "v{version}"`.
4. Client bắt buộc gửi `If-Match: "v{version}"` trong request `PUT`/`PATCH`.
5. Nếu phiên bản không khớp, server từ chối ngay lập tức bằng mã **`HTTP 412 Precondition Failed`** thay vì âm thầm ghi đè.

### 3. Đánh đổi kỹ thuật (Trade-offs)
- **Đánh đổi:** Client phải xử lý mã lỗi 412 và hiển thị giao diện đối chiếu (Diff/Merge View) để người dùng chọn bản lưu.
- **Lợi ích:** Đảm bảo toàn vẹn dữ liệu 100%, không cần giữ các kết nối khóa bi quan (Pessimistic Locks) tốn tài nguyên DB.

---

## ADR-006: Phòng Vệ Đa Tầng 3-Tier AI Guardrails & XML Context Sandboxing

- **Trạng thái:** `Đã phê duyệt & Đang áp dụng (Accepted)`
- **Ngày quyết định:** 2026-09-06
- **Phạm vi tác động:** `packages/core/src/core/services/guardrails.py`, `apps/api/src/api/services/session_chat_service.py`

### 1. Bối cảnh & Vấn đề kỹ thuật
Các tệp PDF học thuật do người dùng tải lên có thể chứa tấn công can thiệp gián tiếp (Indirect Prompt Injection). Người dùng cũng có thể gửi các prompt cố tình bẻ khóa hệ thống (Jailbreak, System Override) nhằm làm lãng phí chi phí token API hoặc gây ảo giác trích dẫn.

### 2. Quyết định
Thiết lập hệ thống phòng thủ 3 tầng:
1. **Tier 1 (Input Guardrail):** Quét chữ ký Injection và Delimiter Breakout trước khi cấp phát tài nguyên DB/LLM. Chặn ngay tại bước 0.
2. **Tier 2 (Context Sandboxing):** Đóng gói toàn bộ trích dẫn PDF vào thẻ `<untrusted_document_context>` và bọc bằng `<![CDATA[ ... ]]>`, tự động trung hòa chuỗi `]]>` thành `]] >`.
3. **Tier 3 (Output Grounding Guardrail):** Kiểm tra đối soát thẻ trích dẫn `[^cit_N]` với danh sách chunks hợp lệ, tự động loại bỏ trích dẫn ảo giác khỏi database.

### 3. Đánh đổi kỹ thuật (Trade-offs)
- **Chi phí (Cost):** Tiết kiệm 100% chi phí gọi LLM cho các prompt độc hại.
- **Độ trễ:** Quét regex và AST chỉ tốn < 2ms trên luồng async.

---

## ADR-007: Kiến Trúc Biên Dịch Sandbox Cô Lập Qua Microservice Riêng Biệt (gVisor runsc)

- **Trạng thái:** `Đã phê duyệt & Đang áp dụng (Accepted)`
- **Ngày quyết định:** 2026-09-07
- **Phạm vi tác động:** Module 2 (LaTeX Compilation), `apps/sandbox-broker`

### 1. Bối cảnh & Vấn đề kỹ thuật
Biên dịch mã nguồn LaTeX không rõ nguồn gốc là mối nguy hiểm an ninh nghiêm trọng (mã TeX là Turing-complete, có thể đọc trộm file hệ thống, thực thi shell hoặc chiếm dụng 100% CPU). Tuyệt đối không được mount `/var/run/docker.sock` vào API server.

### 2. Quyết định
Xây dựng microservice **Sandbox Broker (`apps/sandbox-broker`)** riêng biệt:
1. Giao tiếp qua gRPC nội bộ có xác thực mTLS.
2. Container biên dịch chạy trên nền tảng ảo hóa Kernel bằng **gVisor (`runsc`)**.
3. Cấm triệt để shell escape: `--no-shell-escape`.
4. Tài nguyên cgroups: 1 vCPU, 512MB RAM, mạng ngắt hoàn toàn (`--network none`), timeout cứng 15 giây.

### 3. Đánh đổi kỹ thuật (Trade-offs)
- **Độ trễ:** gVisor có độ trễ khởi động container thêm ~150-300ms so với container thường, nhưng đảm bảo an toàn cấp kernel tuyệt đối.

---

## ADR-008: Hàng Đợi Tác Vụ Bền Vững Bằng Redis Streams Thay Vì In-Memory BackgroundTasks

- **Trạng thái:** `Đã phê duyệt & Đang áp dụng (Accepted)`
- **Ngày quyết định:** 2026-09-08
- **Phạm vi tác động:** `apps/worker`, `apps/api/src/api/services/document_service.py`

### 1. Bối cảnh & Vấn đề kỹ thuật
Bóc tách bài báo PDF lớn (15 - 50MB, 50 - 100 trang) tốn nhiều tài nguyên CPU và RAM. Nếu dùng `FastAPI.BackgroundTasks` in-memory:
- Khi server khởi động lại (restart/deploy), các tác vụ đang chạy bị bốc hơi (Task Evaporation).
- Khi xử lý file nặng, tiến trình API dễ bị OOM-Killed làm gián đoạn toàn bộ các request khác.

### 2. Quyết định
Sử dụng **Redis Streams** với cơ chế Consumer Groups:
1. API ghi nhận tác vụ vào Redis Stream trong một giao dịch nguyên tử.
2. Worker Pool chuyên dụng (`apps/worker`) kéo tác vụ, xử lý bóc tách và xác nhận tường minh (`XACK`).
3. Tích hợp Dead-Letter Queue (DLQ) sau 3 lần retry thất bại.

### 3. Đánh đổi kỹ thuật (Trade-offs)
- **Hạ tầng:** Cần duy trì Redis 7 trong Docker Compose, nhưng nâng cao độ tin cậy và khả năng mở rộng ngang (horizontal scaling) của hệ thống lên mức công nghiệp.

---

## ADR-009: Giám Sát Phân Tán Pure ASGI Tracing Middleware & TTFB Real-time

- **Trạng thái:** `Đã phê duyệt & Đang áp dụng (Accepted)`
- **Ngày quyết định:** 2026-09-09
- **Phạm vi tác động:** `apps/api/src/api/middleware/tracing.py`, `apps/api/src/api/core/logging.py`

### 1. Bối cảnh & Vấn đề kỹ thuật
Cần đo lường chính xác chỉ số Time-To-First-Byte (TTFB) cho các luồng Server-Sent Events (SSE) kéo dài 20 - 30 giây mà không làm tràn bộ nhớ RAM (Memory Leak) hoặc chặn dòng dữ liệu thời gian thực.

### 2. Quyết định
Xây dựng **`PureASGITracingMiddleware`** hoạt động tại tầng ASGI thuần túy (không kế thừa `BaseHTTPMiddleware` của Starlette):
1. Bắt trực tiếp sự kiện `http.response.start` để ghi nhận thời điểm mili-giây phát sinh byte đầu tiên (TTFB).
2. Tự động sinh hoặc kế thừa `X-Request-ID` và đưa vào `structlog.contextvars`.
3. Bắt sự kiện ngắt kết nối mạng của máy trạm (**HTTP 499 Client Closed Request**) để hủy ngay coroutine đang chạy, bảo vệ ngân sách token API.
4. Tự động mặt nạ hóa các dữ liệu nhạy cảm (PII & Secret Redaction).

### 3. Đánh đổi kỹ thuật (Trade-offs)
- **Đánh đổi:** Lập trình ở mức ASGI thuần túy phức tạp hơn BaseHTTPMiddleware nhưng giải quyết triệt để vấn đề memory leak và bảo đảm độ trễ TTFB thấp nhất.

---

## ADR-010: Chiến Lược Chuyển Đổi Định Danh Người Dùng Thật (True Production Auth & RBAC)

- **Trạng thái:** `Đã phê duyệt & Đã hoàn thành (Accepted & Implemented)`
- **Ngày quyết định:** 2026-10-04
- **Phạm vi tác động:** `apps/api/src/api/deps.py`, `apps/api/src/api/v1/endpoints/auth.py`, `UserModel`, `AuthService`

### 1. Bối cảnh & Vấn đề kỹ thuật
Codebase hiện tại trước đây sử dụng Mock User / Developer fallback (`DEFAULT_DEV_USER_ID = UUID("00000000-0000-0000-0000-000000000001")`). Để đạt chuẩn Production-Ready, hệ thống bắt buộc phải thay thế bằng cơ chế xác thực thật, an toàn và bảo mật cao mà không phá vỡ backward compatibility cho các test hiện có.

### 2. Quyết định
Triển khai hệ thống xác thực chuẩn công nghiệp theo nguyên tắc chuyển đổi không gián đoạn (N-1 Backward Compatibility):
1. **Password Hashing:** Sử dụng thuật toán Argon2id qua `pwdlib[argon2]`, chuẩn đoạt giải Password Hashing Competition và được OWASP khuyến nghị hàng đầu hiện nay.
2. **Token Strategy:**
   - **Access Token:** JWT ngắn hạn (TTL = 15 phút), ký bằng HMAC-SHA256 (`HS256`).
   - **Refresh Token:** JWT dài hạn (TTL = 7 ngày).
3. **Chế độ tương thích ngược N-1 (Dev / Test Graceful Fallback):**
   - Trong môi trường `development` hoặc `test`, nếu không có Bearer Token, middleware cho phép fallback về `DEFAULT_DEV_USER_ID` chỉ khi có cờ `ENABLE_DEV_AUTH_BYPASS=true`.
   - Trong môi trường `production`, cờ này bị vô hiệu hóa cưỡng bức; mọi request không có Bearer Token hợp lệ đều bị từ chối với **`HTTP 401 Unauthorized`**.
4. **Phân quyền (RBAC):** Bổ sung trường `role: VARCHAR(20) DEFAULT 'researcher'` vào bảng `users`.

### 3. Đánh đổi kỹ thuật (Trade-offs)
- **Đánh đổi:** Cần quản lý vòng đời refresh token và bảo vệ khóa bí mật `JWT_SECRET_KEY` an toàn qua biến môi trường.
- **Lợi ích:** Đạt tiêu chuẩn an ninh thông tin production, bảo vệ 100% dữ liệu nghiên cứu cá nhân của người dùng.

---

## ADR-011: Chia Sẻ Công Khai Zero-Auth & Cơ Chế Thu Hồi Tức Thì (HTTP 410 Gone Instant Revocation)

- **Trạng thái:** `Đã phê duyệt & Đã hoàn thành (Accepted & Implemented)`
- **Ngày quyết định:** 2026-10-04
- **Phạm vi tác động:** `apps/api/src/api/db/models/share.py`, `apps/api/src/api/services/share_service.py`, `apps/api/src/api/v1/endpoints/shares.py`

### 1. Bối cảnh & Vấn đề kỹ thuật
Cần cho phép nhà nghiên cứu tạo đường link chia sẻ công khai cho các ghi chú, bài báo hoặc bộ sưu tập mà khách truy cập không cần tài khoản (Zero-Auth read-only). Khi chủ tài sản hủy liên kết, link phải lập tức bị vô hiệu hóa, không được lưu cache trên client.

### 2. Quyết định
1. Sử dụng bảng `shares` lưu `share_token` (ngẫu nhiên 32 ký tự URL-safe), `is_revoked: bool`, `expires_at: datetime`.
2. Khi liên kết bị thu hồi (`is_revoked = True`) hoặc hết hạn, server trả về **`HTTP 410 Gone`** kèm header thông báo rõ ràng cho client.
3. Hỗ trợ stream PDF nhị phân cho khách qua `GET /shares/{token}/file` hỗ trợ đầy đủ **HTTP 206 Partial Content (RFC 7233)** để trình đọc PDF trên web tải nhanh từng trang.

### 3. Đánh đổi kỹ thuật (Trade-offs)
- **Đánh đổi:** Cần kiểm tra trạng thái share trên từng request đọc công khai, nhưng độ trễ được tối ưu với DB Index `(token)`.
- **Lợi ích:** An toàn dữ liệu tuyệt đối, tuân thủ quyền kiểm soát tức thời của nhà nghiên cứu.

---

## ADR-012: Không Gian Soạn Thảo Bản Thảo Học Thuật, Khóa Lạc Quan OCC & SAFE Fact-Checking

- **Trạng thái:** `Đã phê duyệt & Đã hoàn thành (Accepted & Implemented)`
- **Ngày quyết định:** 2026-10-04
- **Phạm vi tác động:** `apps/api/src/api/db/models/draft.py`, `apps/api/src/api/services/draft_service.py`, `apps/api/src/api/v1/endpoints/drafts.py`

### 1. Bối cảnh & Vấn đề kỹ thuật
Soạn thảo tài liệu học thuật (LaTeX/Markdown) đòi hỏi giải quyết ba bài toán cốt lõi:
1. Tránh ghi đè ngầm (lost updates) khi nhiều tab hoặc cộng tác viên cùng chỉnh sửa.
2. Biên dịch mã nguồn nặng mà không gây timeout HTTP.
3. Kiểm chứng các mệnh đề khẳng định trong bài báo với tài liệu tham khảo để ngăn chặn ảo giác (Hallucination).

### 2. Quyết định
1. **Khóa lạc quan OCC:** Sử dụng trường `version: int` trên `drafts`, kiểm tra bắt buộc qua header **`If-Match`** (RFC 9110 / RFC 7232). Bất kỳ xung đột nào đều trả về **`HTTP 412 Precondition Failed`** (`CONCURRENCY_CONFLICT`).
2. **Biên dịch Sandbox qua SSE Stream:** Endpoint `POST /drafts/{id}:compile` truyền sự kiện Server-Sent Events (SSE) theo các giai đoạn: AST Linter -> Sandbox Started -> Agentic Healing -> Compile Success.
3. **Quy trình SAFE Fact-Checking 4 bước:** Phân rã văn bản thành các mệnh đề nguyên tử, truy hồi bằng chứng trong `DocumentChunkModel`, chấm điểm NLI (Supported/Contradicted/Not Enough Info), và bảo tồn tọa độ Bounding Box Top-Left chuẩn hóa `[x0, y0, x1, y1, page]`.
4. **Hệ thống phản biện nhóm (Reviewer Mode):** Cho phép đặt nhận xét gắn vào số dòng cụ thể (`DraftCommentModel`).

### 3. Đánh đổi kỹ thuật (Trade-offs)
- **Đánh đổi:** Tăng độ chặt chẽ trong luồng client (phải đọc ETag và gửi If-Match), nhưng ngăn chặn 100% mất dữ liệu người dùng.
- **Lợi ích:** Trải nghiệm viết bài chuẩn xác, có thể kiểm chứng học thuật và an toàn môi trường biên dịch.

