# Quyết Định Kiến Trúc & Kế Hoạch Triển Khai: Lưu Bài Báo Vào Thư Viện Cá Nhân (Star Document Custom Method)

* **Tên Branch:** `feat/m1-api-star-document`
* **API Endpoint:** `POST /api/v1/documents/{id}:star`
* **Mã Phản Hồi:** `200 OK`
* **Loại Endpoint:** Custom Action Method Endpoint (Promotion Resource)
* **Tài Liệu Tham Chiếu:**
  - [`docs/vi/design-api.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-api.md) (Mục 3.6: API Lưu bài báo vào thư viện cá nhân)
  - [`docs/vi/design-database.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-database.md) (Bảng `documents`, các trường `is_persistent`, `folder_id`)
  - [`docs/vi/design-architecture.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-architecture.md) (Quy tắc chuyển đổi từ Ephemeral sang Persistent Resource)
  - Google Cloud API Design Guide (Custom Methods with `:` syntax)

---

## 1. Bối Cảnh & Quyết Định Kỹ Thuật (Architecture Decision)

### 1.1 Bài toán
Theo cam kết bảo mật Zero-Retention của VeriScholar, các tài liệu tải lên trong một phiên hỏi đáp thông thường chỉ là tài liệu tạm thời (`is_persistent = false`). Khi phiên làm việc kết thúc hoặc người dùng chủ động dọn dẹp, tài liệu tạm sẽ bị loại bỏ. Tuy nhiên, nếu người dùng nhận thấy bài báo có giá trị nghiên cứu lâu dài, họ cần lưu trữ bài báo vào thư viện cá nhân vĩnh viễn (`star`) và tùy chọn phân loại vào các thư mục chuyên đề (`folders`).

### 1.2 Quyết định kiến trúc (Decisions)
1. **Sử Dụng Custom Method Cú Pháp Google API Design (`:star`):**
   - Thay vì tạo thêm endpoint con dạng REST CRUD phức tạp hoặc dùng PATCH dễ gây nhầm lẫn ngữ nghĩa, hệ thống áp dụng cú pháp Custom Method chuẩn: `POST /api/v1/documents/{document_id}:star`.
   - Hành động này thể hiện rõ chuyển đổi trạng thái nguyên tử (Atomic State Transition): Thúc đẩy tài liệu từ tệp tạm thành tệp bền vững (`is_persistent = true`).
2. **Cấu Trúc Request Body Rõ Ràng (`folder_id: null` mặc định):**
   - Client có thể gửi `{"folder_id": null}` để lưu bài báo vào thư viện gốc (Root Library) mà không gắn vào thư mục nào.
   - Nếu client truyền `{"folder_id": "<UUID>"}`, hệ thống sẽ xác thực sự tồn tại của thư mục và kiểm tra quyền sở hữu của người dùng.
   - Cấu hình hiển thị OpenAPI/Swagger UI được tinh chỉnh để mẫu request body hiển thị rõ ràng `{"folder_id": null}` thay vì `{}` để tăng tính thân thiện và dễ hiểu cho nhà phát triển.
3. **Tính Lũy Thừa Tuyệt Đối (Idempotency):**
   - Nếu bài báo đã được star trước đó:
     - Gửi lại cùng `folder_id`: Hệ thống trả về `200 OK` thành công ngay lập tức mà không gây lỗi xung đột.
     - Gửi `folder_id` mới: Hệ thống cập nhật tài liệu sang thư mục mới và cập nhật `updated_at`.
4. **Kiểm Soát Toàn Vẹn Khóa Ngoại & Cô Lập Đa Người Dùng:**
   - Nếu `folder_id` được truyền nhưng không tồn tại trong database hoặc thuộc về người dùng khác, hệ thống từ chối ngay với mã `404 FOLDER_NOT_FOUND`.
   - Không cho phép người dùng star bài báo của người khác; trả về `404 DOCUMENT_NOT_FOUND`.

---

## 2. Kế Hoạch Triển Khai Chi Tiết (Step-by-Step Execution Plan)

### Bước 1: Khởi Tạo Git Branch
* Tạo và chuyển sang branch: `git checkout -b feat/m1-api-star-document`.

### Bước 2: Thiết Kế Pydantic Schemas
Trong `apps/api/src/api/schemas/document.py`:
1. `DocumentStarRequest`:
   - `folder_id: UUID | None = Field(default=None, description="UUID của thư mục đích. Để null nếu muốn lưu vào thư viện gốc.")`
2. `DocumentStarResponseData`:
   - `id: UUID`
   - `title: str | None`
   - `status: str`
   - `is_persistent: bool`
   - `folder_id: UUID | None`
   - `updated_at: datetime`
3. `DocumentStarEnvelope`:
   - Kế thừa `SingleResponseEnvelope[DocumentStarResponseData]`.

### Bước 3: Triển Khai Service Layer
Trong `apps/api/src/api/services/document_service.py`:
1. Phương thức `star_document(document_id: UUID, user_id: UUID, folder_id: UUID | None, db: AsyncSession) -> DocumentStarResponseData`:
   - Truy vấn `DocumentModel` theo `id` và `user_id`.
   - Nếu không tìm thấy: Raise `HTTPException(404, detail={"code": "DOCUMENT_NOT_FOUND", ...})`.
   - Nếu có `folder_id`:
     - Truy vấn bảng `folders` theo `id == folder_id AND user_id == user_id`.
     - Nếu không tìm thấy: Raise `HTTPException(404, detail={"code": "FOLDER_NOT_FOUND", ...})`.
   - Cập nhật bản ghi:
     - `doc.is_persistent = True`
     - `doc.folder_id = folder_id`
     - `doc.updated_at = datetime.now(UTC)`
   - Flush và commit giao dịch.
   - Trả về `DocumentStarResponseData`.

### Bước 4: Đăng Ký Endpoint FastAPI & Tùy Biến OpenAPI
Trong `apps/api/src/api/v1/endpoints/documents.py` và `apps/api/src/api/__init__.py`:
1. Đăng ký route:
   - `@router.post("/{document_id}:star", response_model=DocumentStarEnvelope)`
2. Tùy biến OpenAPI Schema Generator:
   - Đảm bảo trường `folder_id` trong request body của endpoint `:star` hiển thị schema có `default: null` và ví dụ `{"folder_id": null}` trực quan trên Swagger UI.
3. Mini-Docs 4 phần chuẩn:
   - **Mục đích:** Đánh dấu lưu trữ bài báo vào thư viện cá nhân vĩnh viễn (chuyển `is_persistent: true`) và tùy chọn gán thư mục.
   - **Đầu vào:** `document_id: UUID` (Path), `folder_id: UUID | null` (Body).
   - **Đầu ra:** HTTP `200 OK` chứa thông tin tài liệu sau khi được thăng cấp trạng thái.
   - **Lưu ý:** Thao tác mang tính lũy thừa (Idempotent); kiểm tra quyền sở hữu folder và document.

### Bước 5: Xây Dựng Bộ Kiểm Thử Tự Động
1. **Điều kiện 1 - Bộ Autotest Riêng Biệt:**
   - Tệp test: `apps/api/tests/test_documents_star.py`.
   - Các ca kiểm thử bao phủ:
     - Star tài liệu thành công không kèm thư mục (`folder_id: null`).
     - Star tài liệu thành công kèm thư mục hợp lệ của chính user.
     - Lũy thừa: Star lại tài liệu đã star trước đó để đổi sang thư mục mới.
     - Xử lý `folder_id` không tồn tại trả về `404 FOLDER_NOT_FOUND`.
     - Cô lập thư mục: Cố tình truyền `folder_id` của user khác bị từ chối `404 FOLDER_NOT_FOUND`.
     - Xử lý `document_id` không tồn tại trả về `404 DOCUMENT_NOT_FOUND`.
     - Cô lập tài liệu: Cố tình star tài liệu của user khác bị từ chối `404 DOCUMENT_NOT_FOUND`.
     - Kiểm tra UUID không hợp lệ nhận mã `422 Unprocessable Entity`.
     - Kiểm tra schema OpenAPI và Swagger example `{"folder_id": null}`.
2. **Điều kiện 2 - Master Autotest Runner:**
   - Chạy tích hợp toàn bộ qua `apps/api/tests/run_all_api_tests.py`.

### Bước 6: Quy Trình Hoàn Tất
1. Commit code: `feat(api): implement POST /api/v1/documents/{id}:star atomic promotion transition`.
2. Bổ sung mục `[POST] /api/v1/documents/{document_id}:star` vào `docs/vi/swagger.md` (uncommitted) để user review.
