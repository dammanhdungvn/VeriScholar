# Quyết Định Kiến Trúc & Kế Hoạch Triển Khai: Stream Tệp PDF Nhị Phân Với Chuẩn HTTP 206 Range Requests

* **Tên Branch:** `feat/m1-api-stream-document-file`
* **API Endpoint:** `GET /api/v1/documents/{id}/file`
* **Mã Phản Hồi:** `200 OK` (Toàn bộ tệp) hoặc `206 Partial Content` (Một phần tệp)
* **Loại Endpoint:** Binary Streaming Endpoint (Media Resource)
* **Tài Liệu Tham Chiếu:**
  - [`docs/vi/design-api.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-api.md) (Mục 3.3: API Stream tệp PDF gốc)
  - [`docs/vi/design-database.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-database.md) (Bảng `documents`, `document_storage_blobs`)
  - [`docs/vi/design-architecture.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-architecture.md) (Phần 2: Hệ thống lưu trữ và tối ưu hóa bộ nhớ cho file streaming)
  - RFC 9110 HTTP Semantics (Phần 14: Range Requests)

---

## 1. Bối Cảnh & Quyết Định Kỹ Thuật (Architecture Decision)

### 1.1 Bài toán
Client frontend hiển thị tài liệu khoa học thông qua trình đọc PDF Canvas Viewer. Một bài báo PDF thường có kích thước từ vài MB đến vài chục MB. Nếu người dùng chỉ muốn xem trang đầu tiên hoặc nhảy đến một trang bất kỳ, việc bắt client phải tải toàn bộ tệp 50MB về bộ nhớ sẽ gây nghẽn mạng nghiêm trọng và giảm trải nghiệm người dùng (UX latency).

### 1.2 Quyết định kiến trúc (Decisions)
1. **Hỗ Trợ Chuẩn RFC 9110 HTTP Range Requests (Mã 206 Partial Content):**
   - Server đọc header `Range: bytes=start-end` từ client request.
   - Hỗ trợ đầy đủ các định dạng:
     - `bytes=0-1023`: Đọc 1024 byte đầu tiên.
     - `bytes=1024-`: Đọc từ byte 1024 đến hết tệp.
   - Trả về mã phản hồi `206 Partial Content` kèm các headers chuẩn:
     - `Content-Range: bytes <start>-<end>/<total_size>`
     - `Content-Length: <chunk_length>`
     - `Accept-Ranges: bytes`
     - `Content-Type: application/pdf`
2. **Xử Lý Yêu Cầu Tải Toàn Bộ (Mã 200 OK):**
   - Nếu client không gửi header `Range`, server trả về mã `200 OK` kèm header `Accept-Ranges: bytes` để báo cho client biết server có hỗ trợ tải từng phần trong các yêu cầu tiếp theo.
3. **Xử Lý Lỗi Khoảng Byte Không Hợp Lệ (Mã 416 Range Not Satisfiable):**
   - Nếu `start >= total_size` hoặc `start > end`, server trả về ngay mã `416 Range Not Satisfiable` kèm header `Content-Range: bytes */<total_size>`.
4. **Bảo Mật & Quản Trị Khóa CAS:**
   - Người dùng chỉ được stream tệp nếu họ là chủ sở hữu của bản ghi logic trong bảng `documents` (`user_id == current_user.id`).
   - Đường dẫn tệp vật lý được phân giải an toàn từ bảng `document_storage_blobs` qua `blob_id`. Tuyệt đối không để lộ đường dẫn đĩa vật lý ra ngoài.

---

## 2. Kế Hoạch Triển Khai Chi Tiết (Step-by-Step Execution Plan)

### Bước 1: Khởi Tạo Git Branch
* Tạo và chuyển sang branch: `git checkout -b feat/m1-api-stream-document-file`.

### Bước 2: Triển Khai Core File Streaming Service
Trong `apps/api/src/api/services/document_service.py`:
1. Phương thức `stream_document_file(document_id: UUID, user_id: UUID, range_header: str | None, db: AsyncSession)`:
   - Truy vấn kết hợp `DocumentModel` và `DocumentStorageBlobModel` theo `id` và `user_id`.
   - Nếu không tìm thấy: Raise `HTTPException(404, detail={"code": "DOCUMENT_NOT_FOUND", ...})`.
   - Kiểm tra sự tồn tại của tệp vật lý trên đĩa. Nếu tệp vật lý bị mất: Raise `HTTPException(404, detail={"code": "BLOB_NOT_FOUND", ...})`.
   - Phân tích cú pháp header `Range`:
     - Phân tách `start` và `end`.
     - Kiểm tra tính hợp lệ: nếu sai phạm, raise `HTTPException(status_code=416, headers={"Content-Range": f"bytes */{file_size}"})`.
   - Xây dựng async generator để stream từng khối nhỏ (ví dụ 64KB - 1MB chunk) qua `StreamingResponse` nhằm tối ưu hóa bộ nhớ RAM của server, ngăn chặn tràn bộ nhớ khi có nhiều kết nối đồng thời.

### Bước 3: Đăng Ký Endpoint FastAPI & Mini-Docs
Trong `apps/api/src/api/v1/endpoints/documents.py`:
1. Đăng ký route:
   - `@router.get("/{document_id}/file")`
2. Tham số:
   - `document_id: UUID` (Path)
   - `range: str | None = Header(default=None)`
3. Mini-Docs 4 phần chuẩn:
   - **Mục đích:** Tải luồng nhị phân của tệp PDF gốc để hiển thị trên trình đọc PDF, hỗ trợ Range Requests.
   - **Đầu vào:** `document_id: UUID` (Path), `Range: str` (Header tùy chọn).
   - **Đầu ra:** HTTP `200 OK` (Toàn bộ tệp) hoặc `206 Partial Content` (Tải từng phần byte).
   - **Lưu ý:** Header `Accept-Ranges: bytes` luôn được bật; trả về 416 nếu khoảng byte vượt giới hạn.

### Bước 4: Xây Dựng Bộ Kiểm Thử Tự Động
1. **Điều kiện 1 - Bộ Autotest Riêng Biệt:**
   - Tệp test: `apps/api/tests/test_documents_file_stream.py`.
   - Các ca kiểm thử bao phủ:
     - Tải toàn bộ tệp thành công trả về `200 OK` kèm nội dung đầy đủ và header `Accept-Ranges: bytes`.
     - Tải từng phần với header `Range: bytes=0-99` trả về `206 Partial Content` và chính xác 100 byte.
     - Tải từng phần dạng mở `Range: bytes=100-` trả về `206 Partial Content` từ byte 100 đến hết tệp.
     - Yêu cầu khoảng byte vượt quá độ dài tệp trả về `416 Range Not Satisfiable`.
     - Truy vấn tài liệu không tồn tại trả về `404 DOCUMENT_NOT_FOUND`.
     - Cô lập multi-tenant: User khác không thể stream tệp của chủ sở hữu (nhận mã `404`).
     - Xử lý khi tệp vật lý bị thiếu trên đĩa trả về `404 BLOB_NOT_FOUND`.
     - Kiểm tra endpoint xuất hiện trong OpenAPI schema.
2. **Điều kiện 2 - Master Autotest Runner:**
   - Chạy kiểm thử toàn hệ thống thông qua `apps/api/tests/run_all_api_tests.py`.

### Bước 5: Quy Trình Hoàn Tất
1. Commit code: `[api] feat: implement GET /api/v1/documents/{id}/file binary streaming with HTTP 206 partial content support`.
2. Bổ sung mục `[GET] /api/v1/documents/{document_id}/file` vào `docs/vi/swagger.md` (uncommitted) để user review.
