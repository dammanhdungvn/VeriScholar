# Quyết Định Kiến Trúc & Kế Hoạch Triển Khai: Kích Hoạt / Bóc Tách Lại Với Idempotency (Document Parse Custom Method)

* **Tên Branch:** `feat/m1-api-parse-document`
* **API Endpoint:** `POST /api/v1/documents/{id}:parse`
* **Mã Phản Hồi:** `202 Accepted`
* **Loại Endpoint:** Custom Action Method Endpoint (Asynchronous Pipeline Trigger)
* **Tài Liệu Tham Chiếu:**
  - [`docs/vi/design-api.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-api.md) (Mục 1.4: Quy chuẩn Idempotency 24h & Mục 3.8: Custom Method Bóc tách tài liệu)
  - [`docs/vi/design-database.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-database.md) (Bảng `documents`, các trường `status`, `stage`, `progress`, `parsed_metadata`)
  - [`docs/vi/design-architecture.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-architecture.md) (Mục 2: Hexagonal Ports & Adapters và Máy trạng thái xử lý Pipeline)
  - [`AGENTS.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/AGENTS.md) (Quy tắc không dùng toán học dollar trong docs & Envelope chuẩn)

---

## 1. Bối Cảnh & Quyết Định Kỹ Thuật (Architecture Decision)

### 1.1 Bài toán
Tiến trình bóc tách bài báo khoa học (trích xuất văn bản, nhận diện cấu trúc hai cột, bảng biểu và sinh embedding) là một quy trình tính toán tốn kém tài nguyên máy chủ. Khi người dùng click nút "Bóc tách" trên giao diện hoặc mạng gặp gián đoạn tạm thời, client có thể gửi lại request nhiều lần. Nếu không có cơ chế chống trùng lặp (Deduplication) và kiểm soát máy trạng thái (State Machine), hệ thống sẽ bị quá tải bởi việc bóc tách trùng lặp cho cùng một bài báo. Ngoài ra, người dùng cần có khả năng thay đổi kích thước chunk (`chunk_size`, `chunk_overlap`) và yêu cầu bóc tách lại từ đầu khi cần (`force_reparse`).

### 1.2 Quyết định kiến trúc (Decisions)
1. **Kiến Trúc Khử Trùng Lặp Idempotency Cửa Sổ 24 Giờ (Hexagonal Idempotency Port & Adapter):**
   - Định nghĩa Port `IIdempotencyPort` trừu tượng tại `packages/core/src/core/ports/idempotency.py`.
   - Triển khai hai Adapter tại `packages/core/src/core/adapters/cache/idempotency.py`:
     - `InMemoryIdempotencyAdapter`: Bộ đệm trong bộ nhớ thread-safe có dọn dẹp TTL phục vụ test và môi trường dev.
     - `RedisIdempotencyAdapter`: Bộ đệm phân tán Redis cho môi trường production với thời gian sống khóa 86.400 giây (24 giờ), tự động fallback an toàn.
   - Khi client gửi header `Idempotency-Key: <UUID>`:
     - Tạo cache key: `idempotency:parse:{user_id}:{document_id}:{idempotency_key}`.
     - **Cache Hit:** Trả về nguyên trạng body đã lưu trước đó kèm header `X-Cache: Idempotent-Hit` mà không kích hoạt lại pipeline.
     - **Cache Miss:** Tiếp nhận xử lý, lưu cache và trả về kèm header `X-Cache: Miss`.
2. **Kiểm Soát Chuyển Đổi Máy Trạng Thái (State Machine Transitions):**
   - **Trường hợp 1 (Đang xử lý & `not force_reparse`):** Tài liệu đang ở trạng thái `status == "processing"`. Hệ thống từ chối yêu cầu mới với mã `409 Conflict` (`DOCUMENT_PROCESSING`) nhằm bảo vệ worker.
   - **Trường hợp 2 (Đang xử lý & `force_reparse == true`):** Cho phép khởi động lại pipeline từ đầu (`stage: validation`, `progress: 0`).
   - **Trường hợp 3 (Đã hoàn tất & `not force_reparse`):** Tài liệu đã ở trạng thái `completed`. Hệ thống trả về trạng thái hiện tại kèm hướng dẫn người dùng bật `force_reparse=true` nếu thực sự muốn bóc tách lại.
   - **Trường hợp 4 (Đã hoàn tất & `force_reparse == true`):** Chuyển trạng thái sang `processing/validation` để tái xử lý.
3. **Chiến Lược Phân Đoạn Bóc Tách Phân Cấp (Hierarchical & Structure-Aware Chunking):**
   - Tránh tuyệt đối phương pháp cắt cứng ngây thơ (Naive Chunking) gây vỡ công thức toán, xé nát bảng biểu hoặc đứt gãy câu.
   - `chunk_size` (100 - 2048 token, mặc định: 512) đóng vai trò là **Ngưỡng trần mềm (Soft Upper Limit)**.
   - `chunk_overlap` (0 - 200 token, mặc định: 50) là vùng đệm liên kết ngữ cảnh giữa các đoạn liền kề.
   - Quy trình bóc tách ngầm tuân thủ 4 tầng ngữ nghĩa nghiêm ngặt:
     ```
                       [ Bài báo khoa học PDF ]
                                  │
                                  ▼
       Tầng 1: Tách theo Mục lớn (Section-Aware Splitting)
               ├── Section 1: Introduction
               ├── Section 2: Related Work
               └── Section 3: Methodology (Không bao giờ gộp chéo Section)
                                  │
                                  ▼
       Tầng 2: Tách theo Khối ngữ nghĩa (Block-Level / Table / Equation)
               ├── Khối công thức toán: Giữ nguyên 1 khối trọn vẹn
               ├── Khối bảng biểu (Table): Giữ nguyên trọn bảng
               └── Khối đoạn văn bản (Paragraphs)
                                  │
                                  ▼
       Tầng 3: Ngắt câu thông minh (Sentence-Boundary Splitting)
               └── Nếu một đoạn văn dài vượt quá `chunk_size` (512 token):
                   Hệ thống dùng thuật toán ngắt câu hoàn chỉnh (tại dấu chấm '.', '?')
                   chứ TUYỆT ĐỐI không bao giờ chặt ngang xương một câu!
                                  │
                                  ▼
       Tầng 4: Đính kèm Ngữ cảnh cha (Contextual Enrichment Header)
               └── Mỗi chunk trước khi mang đi embedding sẽ được tự động gắn thêm:
                   [Document: Attention Is All You Need > Section: Multi-Head Attention]
                   -> Đảm bảo khi tìm kiếm, vector luôn hiểu đầy đủ ngữ cảnh gốc.
     ```
   - Ràng buộc logic kiểm tra tại API Request: Bắt buộc `chunk_overlap < chunk_size`. Nếu vi phạm, trả về `422 Unprocessable Entity`.
   - **Chiến lược Đánh giá Chất lượng Phân đoạn (Eval-Driven Development - EDD):**
     Hệ thống sử dụng bộ công cụ mã nguồn mở **Ragas** kết hợp test harness nội bộ để đánh giá chất lượng parse & chunking định lượng:
     + Bounding Box IoU (>= 0.85): Đảm bảo khung viền vàng highlight vẽ đúng tọa độ trên Canvas PDF.
     + Table Structural Preservation (Mục tiêu: 100%): Khâu nối bảng vắt trang trọn vẹn, không xé lẻ ma trận cột.
     + Boundary Integrity Ratio (Mục tiêu: 100%): Đảm bảo không có chunk nào bị ngắt ngang câu giữa chừng.
     + Section Leakage Rate (Mục tiêu: 0%): Tuyệt đối không để câu của phần này lọt vào phần khác.
     + Ragas Context Recall & Precision (>= 0.90): Kiểm chứng bằng tập dữ liệu chuẩn Golden Dataset trên CI/CD mà không gửi dữ liệu ra nền tảng ngoài (Zero-Retention).
4. **Cô Lập Đa Người Dùng (Multi-Tenancy Isolation):**
   - Chỉ chủ sở hữu bài báo mới được phép kích hoạt tiến trình bóc tách (`user_id == current_user.id`). Người dùng khác truy cập nhận mã `404 DOCUMENT_NOT_FOUND`.

---

## 2. Kế Hoạch Triển Khai Chi Tiết (Step-by-Step Execution Plan)

### Bước 0: Quản Lý Biến Môi Trường (.env.example & .env)
- Kiểm tra các biến môi trường thực tế phục vụ AI / Embedding / Reranking qua thư viện `python-dotenv`:
  + `OPENAI_API_KEY`: Dùng cho Embedding (`text-embedding-3-small`, 1536-dim) và LLM (`5.6-luna`).
  + `COHERE_API_KEY`: Dùng cho Reranker (`rerank-v3.5`).
  + `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` & `AZURE_DOCUMENT_INTELLIGENCE_KEY`: Dự phòng cho PDF quét (Scanned PDF).
- Bổ sung các biến mẫu vào `.env.example` (tuyệt đối không đọc trực tiếp file `.env`). Thông báo người dùng khi cần bổ sung khóa API thật.

### Bước 1: Khởi Tạo Git Branch
* Tạo và chuyển sang branch: `git checkout -b feat/m1-api-parse-document` (Hiện tại đã ở đúng branch này).

### Bước 2: Thiết Kế Idempotency Port & Adapter (Hexagonal Architecture)
1. **Port Interface (`packages/core/src/core/ports/idempotency.py`):**
   - `IIdempotencyPort`:
     - `async def get_response(self, key: str) -> dict[str, Any] | None`
     - `async def store_response(self, key: str, response_data: dict[str, Any], status_code: int = 202, ttl_seconds: int = 86400) -> None`
2. **Adapters (`packages/core/src/core/adapters/cache/idempotency.py`):**
   - `InMemoryIdempotencyAdapter` và `RedisIdempotencyAdapter`.
3. **Unit Test Cho Adapters:**
   - `packages/core/tests/adapters/test_idempotency.py` kiểm chứng TTL 24h và tính phân lập giữa các khóa.

### Bước 3: Thiết Kế Pydantic Schemas Cho Request & Response
Trong `apps/api/src/api/schemas/document.py`:
1. `DocumentParseRequest`:
   - `chunk_size: int = Field(default=512, ge=100, le=2048)`
   - `chunk_overlap: int = Field(default=50, ge=0, le=200)`
   - `extract_tables: bool = Field(default=True)`
   - `force_reparse: bool = Field(default=False)`
   - `@model_validator`: Kiểm tra `chunk_overlap < chunk_size`.
2. `DocumentParseLinks`:
   - `status_url: str`
   - `detail_url: str`
3. `DocumentParseResponseData`:
   - `id: UUID`
   - `status: str`
   - `stage: str`
   - `progress: int`
   - `message: str`
   - `links: DocumentParseLinks`
4. `DocumentParseEnvelope`:
   - Kế thừa `SingleResponseEnvelope[DocumentParseResponseData]`.

### Bước 4: Triển Khai Service Layer
Trong `apps/api/src/api/services/document_service.py`:
1. Phương thức `trigger_parse_document(document_id: UUID, user_id: UUID, parse_req: DocumentParseRequest, db: AsyncSession) -> DocumentParseResponseData`:
   - Kiểm tra tồn tại và quyền sở hữu theo `id == document_id AND user_id == user_id`.
   - Kiểm tra máy trạng thái:
     - Nếu đang `processing` và không `force_reparse`: Ném lỗi `HTTPException(409, detail={"code": "DOCUMENT_PROCESSING", ...})`.
     - Nếu đã `completed` và không `force_reparse`: Trả về thông điệp hướng dẫn không cần parse lại.
     - Cập nhật trạng thái `status = "processing"`, `stage = "validation"`, `progress = 0`.
     - Lưu cấu hình bóc tách vào `doc.parsed_metadata["parse_options"]`.
   - Flush và commit giao dịch.
   - Trả về `DocumentParseResponseData`.

### Bước 5: Đăng Ký Endpoint FastAPI & Xử Lý Idempotency-Key Header
Trong `apps/api/src/api/v1/endpoints/documents.py`:
1. Đăng ký route:
   - `@router.post("/{document_id}:parse", status_code=status.HTTP_202_ACCEPTED, response_model=DocumentParseEnvelope)`
2. Xử lý header `Idempotency-Key`:
   - Nếu có header: Truy vấn `idempotency_port`.
   - Nếu hit: Gán header `X-Cache: Idempotent-Hit` và trả về body đã lưu.
   - Nếu miss: Thực thi pipeline, lưu cache với TTL 24h, gán header `X-Cache: Miss`.
3. Mini-Docs 4 phần chuẩn:
   - **Mục đích:** Kích hoạt hoặc tái kích hoạt tiến trình bóc tách bài báo với cơ chế Idempotency chống trùng lặp.
   - **Đầu vào:** `document_id: UUID` (Path), `Idempotency-Key` (Header), Body tùy chọn các thông số chunking.
   - **Đầu ra:** HTTP `202 Accepted` kèm trạng thái tiếp nhận và header `X-Cache`.
   - **Lưu ý:** Chặn 409 khi đang bóc tách dở dang trừ khi có `force_reparse=true`.

### Bước 6: Xây Dựng Bộ Kiểm Thử Tự Động
1. **Điều kiện 1 - Bộ Autotest Riêng Biệt:**
   - Tệp test: `apps/api/tests/test_documents_parse.py`.
   - Các ca kiểm thử bao phủ:
     - Kích hoạt bóc tách thành công trả về `202 Accepted`.
     - Tùy chỉnh thông số chunking (`chunk_size=1024`, `chunk_overlap=100`).
     - Idempotency Cache Hit: Gọi lần 2 với cùng khóa trả về header `X-Cache: Idempotent-Hit`.
     - Tài liệu đang xử lý thì bị từ chối với mã `409 DOCUMENT_PROCESSING`.
     - Tài liệu đang xử lý nhưng có `force_reparse=true` thì được phép tái kích hoạt.
     - Tài liệu đã hoàn tất mà không có `force_reparse` thì trả về hướng dẫn.
     - Tài liệu đã hoàn tất nhưng có `force_reparse=true` thì kích hoạt lại.
     - Trả về `404 DOCUMENT_NOT_FOUND` khi không tìm thấy tài liệu.
     - Cô lập multi-tenant: User B không thể kích hoạt parse tài liệu của User A.
     - Xác thực vi phạm `chunk_overlap >= chunk_size` trả về `422 Unprocessable Entity`.
     - Xác thực UUID không hợp lệ trả về mã `422`.
     - Kiểm tra endpoint xuất hiện trong OpenAPI schema.
2. **Điều kiện 2 - Master Autotest Runner:**
   - Chạy tích hợp toàn bộ qua `apps/api/tests/run_all_api_tests.py` (Toàn bộ 78 tests passed).
3. **Điều kiện 3 - Bộ Autotest Đo Lường Chất Lượng Định Lượng (Eval Harness):**
   - Tệp test eval: `tests/evals/test_parse_chunking_eval.py`.
   - Nạp dữ liệu từ `data/papers/golden_eval_dataset.json` và 3 bài báo PDF chuẩn.
   - Kiểm chứng 5 chỉ số EDD:
     + Boundary Integrity Ratio = 100% (không ngắt đôi câu).
     + Section Leakage Rate = 0% (không trộn lẫn mục).
     + Tọa độ Bounding Box nằm chuẩn trong `[0.0, 1.0]`.
     + Đính kèm ngữ cảnh cha Context Enrichment `[Doc > Section]` cho 100% chunk.
     + Đo lường Ragas Context Recall & Precision >= 0.85.

### Bước 7: Quy Trình Hoàn Tất
1. Commit code: `feat(api): implement POST /api/v1/documents/{id}:parse with idempotency`.
2. Bổ sung mục `[POST] /api/v1/documents/{document_id}:parse` vào `docs/vi/swagger.md` (uncommitted) để user review.
