# Design Specification: Open-Reading PDF Ingestion & Abstract-Only Handling

- **Date:** 2026-10-26
- **Status:** Proposed
- **Module:** `apps/api/src/api/v1/endpoints/discovery.py`, `apps/api/src/api/services/document_service.py`, `apps/web/src/features/dashboard/components/DashboardWorkspace.tsx`

---

## 1. Bối cảnh & Vấn đề (Context & Problem Statement)

Khi người dùng nhấn nút **"Mở Đọc Sâu"** (`[📖 Mở Đọc Sâu]`) từ kết quả tìm kiếm bài báo khoa học:
1. `POST /api/v1/discovery/open-reading` tạo bản ghi `DocumentModel` với mã băm giả lập SHA-256 (`initial_hash = hashlib.sha256(...)`), kích thước `0 byte`, và không tải tệp PDF thật từ `pdf_url` (arXiv/Unpaywall) vào kho CAS (`storage/blobs/`).
2. Trình duyệt chuyển hướng ngay sang `/dashboard/{sessionId}`. `DashboardWorkspace.tsx` thấy có `activeDocumentId` nên khởi chạy `PdfCanvasViewer`.
3. PDF.js gọi `GET /api/v1/documents/{document_id}/file`. Backend kiểm tra `storage.blob_exists(content_hash)` thấy không có file trên ổ cứng nên trả về lỗi `404 FILE_NOT_FOUND`.
4. PDF.js hiển thị lỗi:
   > *"Không thể kết xuất tài liệu PDF - Unexpected server response (404) while retrieving PDF '.../file'"*.
5. Đối với các bài báo chỉ có tóm tắt (`access_status == "abstract_only"`), giao diện cũng cố gắng tải file PDF và gặp lỗi 404 tương tự thay vì hiển thị trình đọc tóm tắt học thuật.

---

## 2. Mục tiêu (Goals & Anti-Goals)

### Goals:
- **Tải và lưu trữ tệp PDF tự động (Automated CAS Ingestion):** Khi người dùng mở một bài báo Open Access có `pdf_url`, backend tải tệp PDF về, xác thực Magic Bytes `%PDF-`, tính SHA-256 thực tế, lưu vào CAS `storage/blobs/`, và cập nhật thông số tài liệu trong DB.
- **Khả năng tự phục hồi (Graceful Fallback):** Nếu liên kết PDF bị hỏng hoặc timeout, hệ thống tự động chuyển trạng thái tài liệu về `abstract_only` thay vì sập lỗi 404/500.
- **Trải nghiệm đọc tóm tắt chuẩn mực (Abstract-Only Reader View):** Khi tài liệu là `abstract_only` (hoặc trong lúc PDF đang tải), giao diện hiển thị bảng thông tin học thuật (Metadata, Abstract, Authors, DOI link) kèm khu vực kéo thả để người dùng có thể đính kèm file PDF đầy đủ (`attach-pdf`).
- **Tuân thủ Kiến trúc Lục giác & TDD:** Viết test backend/frontend đầy đủ trước khi hoàn thiện mã nguồn; không vi phạm ranh giới kiến trúc.

### Anti-Goals:
- Không tạo hàng đợi phân tán phức tạp (như Celery/RabbitMQ) ngoài quy mô MVP Monorepo.
- Không cho phép tải tệp vượt quá giới hạn an toàn 50MB hoặc tệp không phải PDF.

---

## 3. Các hướng tiếp cận (Approaches Considered)

### Tiếp cận 1 (Đề xuất): Tải trực tiếp trong API `open-reading` với Fallback Abstract tức thì
- **Cơ chế:** Khi nhận yêu cầu `POST /api/v1/discovery/open-reading`:
  - Nếu có `pdf_url`: Backend dùng `httpx.AsyncClient(timeout=10.0)` tải luồng PDF (tối đa 50MB).
  - Nếu tải thành công và tệp hợp lệ (`%PDF-`): Tính SHA-256 thực tế, lưu vào CAS `storage.save_blob`, gán `status: "parsing"`, `access_status: "open_access_pdf"`, `file_size_bytes = len(content)`.
  - Nếu tải thất bại (timeout, 404 arXiv, hoặc mạng chậm): Ghi log cảnh báo, tự động hạ cấp tài liệu xuống `status: "abstract_only"`, `access_status: "abstract_only"`, và vẫn trả về phiên đọc thành công cho người dùng.
- **Ưu điểm:**
  - Khắc phục triệt để lỗi 404: Khi người dùng vào Dashboard, tệp PDF đã chắc chắn nằm trong CAS hoặc giao diện đã biết rõ đây là `abstract_only`.
  - Không phát sinh race condition giữa frontend và background task.
  - Phù hợp với nút bấm hiện tại trên frontend vốn đã có trạng thái loading `"Đang mở..."`.
- **Nhược điểm:** Endpoint `open-reading` mất khoảng 500ms - 1.5s để hoàn thành tải PDF (arXiv tải khoảng 2-3MB rất nhanh trên VPS băng thông cao).

### Tiếp cận 2: Tải ngầm (Background Task) kết hợp Polling trạng thái
- **Cơ chế:** `open-reading` trả về ngay trong 100ms với `status: "downloading"`. Một background task tải PDF từ từ. Frontend polling liên tục `/status` cho đến khi `ready` mới hiển thị PDF.
- **Ưu điểm:** Phản hồi API ban đầu cực nhanh.
- **Nhược điểm:** Phức tạp hóa trạng thái phía Frontend, người dùng vẫn phải đợi spinner tại Dashboard, dễ xảy ra lỗi race condition nếu người dùng chuyển tab hoặc mạng gián đoạn.

### Tiếp cận 3: Lazy-Load Caching tại endpoint `/file`
- **Cơ chế:** Khi gọi `/file`, nếu tệp chưa có trong CAS nhưng có `pdf_url`, backend mới bắt đầu stream từ arXiv về người dùng và ghi cache ngầm.
- **Nhược điểm:** Rất khó hỗ trợ các tính năng phân đoạn Range Request (HTTP 206) của PDF.js khi tệp chưa được tải trọn vẹn về đĩa cứng.

$\rightarrow$ **Quyết định:** Chọn **Tiếp cận 1**. Đơn giản, an toàn, ổn định tuyệt đối và có cơ chế fallback tự động.

---

## 4. Đặc tả kỹ thuật chi tiết (Technical Specification)

### 4.1 Backend (`apps/api`)
1. **Helper nạp tệp học thuật ngoại vi:**
   Bổ sung phương thức `download_and_ingest_pdf(pdf_url: str, ...)` trong `DocumentService` hoặc `discovery.py`:
   - Dùng `httpx.AsyncClient` tải luồng với `timeout=12.0s`.
   - Kiểm tra `Content-Length <= 50MB` và Magic Bytes `%PDF-`.
   - Lưu tệp qua `storage.save_blob(chunks, content_hash)`.
   - Trả về `(content_hash, file_size_bytes)`.
2. **Cập nhật `open_reading_session` (`apps/api/src/api/v1/endpoints/discovery.py`):**
   - Nếu `payload.pdf_url` có giá trị: Gọi nạp tệp PDF. Nếu thành công, gán hash thật; nếu thất bại (timeout/error), chuyển thành `access_status = "abstract_only"`.
3. **Endpoint `/file` an toàn:**
   - Nếu tài liệu là `abstract_only`, trả về `404` có cấu trúc rõ ràng (`DOCUMENT_ABSTRACT_ONLY`) hoặc từ chối hợp lệ.

### 4.2 Frontend (`apps/web`)
1. **`DashboardWorkspace.tsx`:**
   - Kiểm tra `documentDetail?.access_status`:
     - Nếu `access_status === "abstract_only"`: Không render `PdfCanvasViewer`. Thay vào đó, render component `AbstractOnlyViewer` hiển thị tóm tắt khoa học, tác giả, năm xuất bản, DOI link và nút kéo thả đính kèm tệp PDF đầy đủ (`attach-pdf`).
     - Nếu `access_status === "open_access_pdf"`: Render `PdfCanvasViewer` như bình thường.
2. **`ScholarlyResultCard.tsx`:**
   - Đảm bảo hiển thị đúng trạng thái loading khi người dùng bấm "Mở Đọc Sâu".
