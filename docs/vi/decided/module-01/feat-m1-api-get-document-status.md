# Quyết Định Kiến Trúc & Kế Hoạch Triển Khai: Polling Trạng Thái Xử Lý Tài Liệu (Document Status)

* **Tên Branch:** `feat/m1-api-get-document-status`
* **API Endpoint:** `GET /api/v1/documents/{id}/status`
* **Mã Phản Hồi:** `200 OK`
* **Loại Endpoint:** Standard REST Entity Endpoint (Polling Resource)
* **Tài Liệu Tham Chiếu:**
  - [`docs/vi/design-api.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-api.md) (Mục 3.2: API Kiểm tra tiến độ xử lý bài báo)
  - [`docs/vi/design-database.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-database.md) (Bảng `documents`, các trường `status`, `stage`, `progress`, `parsed_metadata`)
  - [`docs/vi/techstack-backend-module-01.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/techstack-backend-module-01.md) (Quy trình Pipeline bóc tách đa tầng)
  - [`AGENTS.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/AGENTS.md) (Quy tắc Zero-Retention & Envelope Response chuẩn)

---

## 1. Bối Cảnh & Quyết Định Kỹ Thuật (Architecture Decision)

### 1.1 Bài toán
Quá trình bóc tách (parsing), trích xuất bố cục bảng biểu (table layout detection), nhận dạng quang học (OCR) và sinh vector nhúng (vector embedding) cho bài báo khoa học là các tác vụ nặng (long-running asynchronous tasks) mất từ vài giây đến hàng chục giây. Client frontend cần một endpoint nhẹ, phản hồi cực nhanh để thực hiện Polling (thăm dò tiến độ) mà không phải kéo toàn bộ dữ liệu văn bản nặng của bài báo.

### 1.2 Quyết định kiến trúc (Decisions)
1. **Thiết Kế Resource Độc Lập Cho Polling (`/documents/{id}/status`):**
   - Chỉ trả về các trường trạng thái tối thiểu: `id`, `status` (`uploaded`, `processing`, `completed`, `failed`), `stage` (`validation`, `layout_detection`, `ocr`, `chunking`, `embedding`), `progress` (0 - 100), `error_message`, và `stages_detail`.
   - Giúp giảm thiểu tối đa băng thông mạng khi client thực hiện polling theo chu kỳ 1s - 2s.
2. **Chi Tiết Các Phân Đoạn Xử Lý (`stages_detail`):**
   - Định nghĩa trạng thái chi tiết của từng bước trong pipeline dưới dạng cấu trúc JSON rõ ràng:
     - `stage_name`: Tên giai đoạn (`validation`, `layout_detection`, `ocr`, `chunking`, `embedding`).
     - `status`: `pending`, `running`, `completed`, `failed`.
     - `duration_ms`: Thời gian xử lý của giai đoạn tính bằng mili-giây.
   - Dữ liệu này được lưu trữ linh hoạt trong cột JSONB `parsed_metadata["stages_detail"]` của bảng `documents`. Nếu chưa có dữ liệu tùy chỉnh, hệ thống tự động suy diễn trạng thái logic dựa trên tiến độ `progress` hiện tại.
3. **Bảo Mật & Cô Lập Đa Người Dùng (Multi-Tenancy Isolation):**
   - Luôn lọc theo cặp khóa `(id, user_id)`: Không cho phép người dùng này thăm dò tiến độ bài báo của người dùng khác.
   - Nếu không tìm thấy hoặc sai chủ sở hữu, trả về thống nhất `404 DOCUMENT_NOT_FOUND` để ngăn chặn rò rỉ thông tin (Information Leakage).

---

## 2. Kế Hoạch Triển Khai Chi Tiết (Step-by-Step Execution Plan)

### Bước 1: Khởi Tạo Git Branch
* Tạo và chuyển sang branch: `git checkout -b feat/m1-api-get-document-status`.

### Bước 2: Thiết Kế Pydantic Schemas
Trong `apps/api/src/api/schemas/document.py`:
1. `StageDetail`:
   - `stage_name: str`
   - `status: str` (`pending`, `running`, `completed`, `failed`)
   - `duration_ms: int | None`
2. `DocumentStatusResponseData`:
   - `id: UUID`
   - `status: str`
   - `stage: str`
   - `progress: int = Field(ge=0, le=100)`
   - `error_message: str | None = None`
   - `stages_detail: list[StageDetail]`
   - `links: DocumentStatusLinks` (`detail_url`, `file_url`, `self_url`)
3. `DocumentStatusEnvelope`:
   - Kế thừa `SingleResponseEnvelope[DocumentStatusResponseData]`.

### Bước 3: Triển Khai Service Layer
Trong `apps/api/src/api/services/document_service.py`:
1. Phương thức `get_document_status(document_id: UUID, user_id: UUID, db: AsyncSession) -> DocumentStatusResponseData`:
   - Truy vấn bản ghi `DocumentModel` theo `id` và `user_id`.
   - Nếu không có: Raise `HTTPException(404, detail={"code": "DOCUMENT_NOT_FOUND", ...})`.
   - Trích xuất `stages_detail` từ `parsed_metadata["stages_detail"]`. Nếu chưa có, xây dựng danh sách giai đoạn mặc định tương ứng với trạng thái hiện tại:
     - Giai đoạn đã qua: `status = "completed"`.
     - Giai đoạn đang chạy: `status = "running"`.
     - Giai đoạn sắp tới: `status = "pending"`.
   - Trả về đối tượng `DocumentStatusResponseData`.

### Bước 4: Đăng Ký Endpoint FastAPI & Mini-Docs
Trong `apps/api/src/api/v1/endpoints/documents.py`:
1. Đăng ký route:
   - `@router.get("/{document_id}/status", response_model=DocumentStatusEnvelope)`
2. Mini-Docs 4 phần chuẩn:
   - **Mục đích:** Thăm dò tiến độ xử lý của bài báo khoa học.
   - **Đầu vào:** `document_id: UUID` (Path parameter).
   - **Đầu ra:** HTTP `200 OK` chứa tiến độ phần trăm, giai đoạn hiện tại và chi tiết từng phân đoạn.
   - **Lưu ý:** Chỉ trả về trạng thái nhẹ, không kèm nội dung chunk; trả về 404 nếu không tìm thấy bài báo.

### Bước 5: Xây Dựng Bộ Kiểm Thử Tự Động
1. **Điều kiện 1 - Bộ Autotest Riêng Biệt Cho Endpoint:**
   - Tệp test: `apps/api/tests/test_documents_status.py`.
   - Các ca kiểm thử bao phủ:
     - Tài liệu đang xử lý: `status: processing`, `stage: ocr`, `progress: 45`.
     - Tài liệu mới tải lên: `status: uploaded`, `stage: queued`, `progress: 0`.
     - Tài liệu hoàn tất: `status: completed`, `stage: embedding`, `progress: 100`.
     - Tài liệu gặp lỗi: `status: failed`, `error_message` chứa lý do lỗi.
     - Tài liệu có `stages_detail` lưu sẵn trong JSONB `parsed_metadata`.
     - Trả về `404 DOCUMENT_NOT_FOUND` khi `document_id` không tồn tại.
     - Cô lập multi-tenant: User B truy vấn tài liệu của User A nhận mã `404`.
     - Xác thực UUID không hợp lệ nhận mã `422 Unprocessable Entity`.
     - Kiểm tra sự hiện diện của endpoint trong OpenAPI schema.
2. **Điều kiện 2 - Master Autotest Runner:**
   - Đảm bảo tương thích hoàn toàn khi chạy thông qua `apps/api/tests/run_all_api_tests.py`.

### Bước 6: Quy Trình Hoàn Tất
1. Commit code: `feat(api): implement GET /api/v1/documents/{id}/status polling endpoint`.
2. Cập nhật tài liệu offline tại `docs/vi/swagger.md` (uncommitted) để user review.
