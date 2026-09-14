# Quyết Định Kiến Trúc & Kế Hoạch Triển Khai: Tải Lên Tài Liệu PDF Với CAS Deduplication

* **Tên Branch:** `feat/m1-api-upload-document`
* **API Endpoint:** `POST /api/v1/documents`
* **Mã Phản Hồi:** `201 Created`
* **Loại Endpoint:** Standard REST Collection Endpoint (File Ingestion)
* **Tài Liệu Tham Chiếu:**
  - [`docs/vi/design-api.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-api.md) (Mục 3.1: API Tải lên tài liệu PDF)
  - [`docs/vi/design-database.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-database.md) (Bảng `documents`, `document_storage_blobs`, `session_documents`)
  - [`docs/vi/design-architecture.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-architecture.md) (Mục 2 & 5: Lưu trữ CAS và cô lập đa người dùng)
  - [`docs/vi/PRD.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/PRD.md) (FR-1: Tải lên và khử trùng lặp PDF)
  - [`AGENTS.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/AGENTS.md) (Quy tắc Hexagonal Architecture & Zero-Retention)

---

## 1. Bối Cảnh & Quyết Định Kỹ Thuật (Architecture Decision)

### 1.1 Bài toán
Hệ thống VeriScholar phục vụ việc đọc sâu và đối chiếu trích dẫn tài liệu khoa học. Người dùng tải lên các tệp PDF có dung lượng lớn (lên tới 50MB). Nếu nhiều người dùng hoặc cùng một người dùng tải lên các tệp giống hệt nhau (cùng nội dung), việc lưu trữ lặp lại trên đĩa vật lý sẽ gây lãng phí dung lượng đĩa và tài nguyên I/O nghiêm trọng.

### 1.2 Quyết định kiến trúc (Decisions)
1. **Lưu trữ hướng nội dung (Content-Addressable Storage - CAS):**
   - Sử dụng thuật toán băm SHA-256 trên toàn bộ luồng byte của tệp PDF ngay khi nhận được stream: `content_hash = sha256(file_bytes)`.
   - Bảng `document_storage_blobs` đóng vai trò quản trị thực thể vật lý: `id`, `content_hash`, `storage_path`, `file_size_bytes`, `mime_type`, `ref_count`.
   - Nếu `content_hash` đã tồn tại trong database: Tái sử dụng `blob_id` đã có, tăng nguyên tử `ref_count = ref_count + 1`, và không ghi đè tệp lên ổ đĩa.
   - Nếu `content_hash` chưa tồn tại: Lưu tệp vật lý theo cấu trúc phân cấp bảo vệ inodes (`/storage/blobs/ab/cd/abcdef...pdf`), tạo bản ghi `document_storage_blobs` mới với `ref_count = 1`.
2. **Cô lập Đa Người Dùng (Multi-Tenancy Isolation):**
   - Mỗi bản ghi trong bảng `documents` đại diện cho quyền sở hữu logic của một người dùng: `user_id`, `blob_id`, `filename`, `status = "uploaded"`, `is_persistent = false`.
   - Người dùng A và người dùng B có thể sở hữu cùng một tệp (chung một `blob_id`), nhưng thông tin logic, ghi chú, trạng thái và phiên làm việc là hoàn toàn tách biệt.
3. **Giới Hạn Tải Lên & Xác Thực Nghiêm Ngặt:**
   - Dung lượng tối đa: 50MB (`MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024`). Vượt quá trả về `413 Payload Too Large`.
   - Định dạng tệp: Xác thực Magic Bytes 4 byte đầu tiên phải là `%PDF-` (`0x25 0x50 0x44 0x46 0x2D`). Nếu sai trả về `415 Unsupported Media Type`.
   - Giới hạn phiên làm việc: Một phiên làm việc (`session_id`) chỉ được liên kết tối đa 5 tài liệu (`MAX_SESSION_DOCUMENTS = 5`). Nếu vượt quá trả về `400 SESSION_DOCUMENT_LIMIT_EXCEEDED`.

---

## 2. Kế Hoạch Triển Khai Chi Tiết (Step-by-Step Execution Plan)

### Bước 1: Khởi Tạo Git Branch
* Tạo và chuyển sang branch: `git checkout -b feat/m1-api-upload-document`.

### Bước 2: Thiết Kế Port & Adapter Lưu Trữ Vật Lý (Hexagonal Architecture)
1. **Port Interface (`packages/core/src/core/ports/storage.py`):**
   - `IStoragePort`:
     - `async def save_file(self, content_hash: str, stream: AsyncIterator[bytes]) -> str`
     - `async def delete_file(self, storage_path: str) -> bool`
     - `async def get_file_stream(self, storage_path: str) -> AsyncIterator[bytes]`
2. **Adapter Cụ Thể (`packages/core/src/core/adapters/storage/local.py`):**
   - `LocalStorageAdapter`: Triển khai lưu trữ cục bộ an toàn, tự động tạo cấu trúc thư mục 2 cấp theo prefix của sha256 hash.

### Bước 3: Thiết Kế Pydantic Schemas Cho Request & Response
Trong `apps/api/src/api/schemas/document.py`:
1. `DocumentUploadResponseData`:
   - `id: UUID`: Khóa chính của bản ghi tài liệu.
   - `filename: str`: Tên gốc của tệp tải lên.
   - `file_size_bytes: int`: Kích thước tệp byte.
   - `content_hash: str`: Chuỗi băm SHA-256 kiểm tra toàn vẹn dữ liệu.
   - `status: str`: Trạng thái ban đầu `uploaded`.
   - `created_at: datetime`: Thời điểm tạo.
   - `links: DocumentUploadLinks` (`status_url`, `file_url`, `detail_url`).
2. `DocumentUploadEnvelope`:
   - Kế thừa `SingleResponseEnvelope[DocumentUploadResponseData]` chuẩn toàn hệ thống (`success: bool`, `data`, `meta`).

### Bước 4: Triển Khai Service Layer
Trong `apps/api/src/api/services/document_service.py`:
1. Phương thức `upload_document(file: UploadFile, session_id: UUID | None, user_id: UUID, db: AsyncSession)`:
   - Kiểm tra magic bytes `%PDF-`.
   - Tính toán streaming SHA-256 hash và kiểm đếm kích thước byte trong quá trình đọc stream.
   - Kiểm tra `session_id` nếu có: Đảm bảo session thuộc về `user_id` và số lượng tài liệu hiện tại trong session `< 5`.
   - Khử trùng lặp CAS:
     - `SELECT * FROM document_storage_blobs WHERE content_hash = :hash FOR UPDATE`.
     - Nếu có: Tăng `ref_count += 1`.
     - Nếu chưa có: Lưu tệp vật lý qua `IStoragePort`, insert bản ghi `document_storage_blobs`.
   - Tạo bản ghi `DocumentModel` mới liên kết với `blob_id`.
   - Nếu có `session_id`: Tạo bản ghi liên kết `SessionDocumentModel`.
   - Flush và commit giao dịch nguyên tử.

### Bước 5: Đăng Ký Endpoint FastAPI & Mini-Docs
Trong `apps/api/src/api/v1/endpoints/documents.py`:
1. Đăng ký route:
   - `@router.post("", status_code=status.HTTP_201_CREATED, response_model=DocumentUploadEnvelope)`
2. Mini-Docs 4 phần chuẩn:
   - **Mục đích:** Tải lên tệp PDF, kiểm tra tính hợp lệ và khử trùng lặp qua Content-Addressable Storage (CAS).
   - **Đầu vào:** Multipart Form Data (`file: UploadFile`), Form field tùy chọn (`session_id: UUID`).
   - **Đầu ra:** HTTP `201 Created` kèm thông tin tài liệu và các liên kết HATEOAS.
   - **Lưu ý:** Giới hạn 50MB, kiểm tra magic bytes `%PDF-`, giới hạn 5 tài liệu/phiên.

### Bước 6: Xây Dựng Bộ Kiểm Thử Tự Động
1. **Điều kiện 1 - Bộ Autotest Riêng Biệt Cho Endpoint:**
   - Tệp test: `apps/api/tests/test_documents_upload.py`.
   - Các ca kiểm thử bao phủ:
     - Tải lên tệp PDF hợp lệ thành công trả về `201 Created`.
     - Tải lên kèm `session_id` hợp lệ.
     - Khử trùng lặp CAS: Tải lên cùng 1 tệp lần thứ hai thì `ref_count` tăng lên 2 và không nhân bản tệp đĩa.
     - Từ chối tệp không đúng Magic Bytes `%PDF-` trả về `415 Unsupported Media Type`.
     - Xử lý `session_id` không tồn tại hoặc không thuộc user trả về `404`.
     - Xử lý session đã đầy 5 tài liệu trả về `400 Session Limit Exceeded`.
     - Xử lý tệp vượt quá 50MB trả về `413 Payload Too Large`.
     - Kiểm tra OpenAPI schema chứa endpoint tải lên.
2. **Điều kiện 2 - Master Autotest Runner:**
   - Chạy tích hợp qua `apps/api/tests/run_all_api_tests.py` và `uv run pytest`.

### Bước 7: Quy Trình Hoàn Tất
1. Commit code trước: `feat(api): implement document upload endpoint with CAS and validation`.
2. Bổ sung mục `[POST] /api/v1/documents` vào `docs/vi/swagger.md` và để ở trạng thái uncommitted để user review.
