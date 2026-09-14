# Quyết Định Kiến Trúc & Kế Hoạch Triển Khai: Danh Sách Tài Liệu Phân Trang HATEOAS (Document List)

* **Tên Branch:** `feat/m1-api-list-documents`
* **API Endpoint:** `GET /api/v1/documents`
* **Mã Phản Hồi:** `200 OK`
* **Loại Endpoint:** Standard REST Collection Endpoint (List Resource)
* **Tài Liệu Tham Chiếu:**
  - [`docs/vi/design-api.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-api.md) (Mục 1.2: Chuẩn phản hồi phân trang và Mục 3.4: API Danh sách tài liệu)
  - [`docs/vi/design-database.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/docs/vi/design-database.md) (Bảng `documents`, các chỉ mục phân trang đa người dùng `idx_documents_user_created`)
  - [`AGENTS.md`](file:///home/dammanhdungvn/Downloads/Workspace/VeriScholar/AGENTS.md) (Quy chuẩn HATEOAS và PaginatedResponseEnvelope)

---

## 1. Bối Cảnh & Quyết Định Kỹ Thuật (Architecture Decision)

### 1.1 Bài toán
Người dùng tích lũy hàng chục đến hàng trăm tài liệu nghiên cứu trong thư viện cá nhân. Việc tải toàn bộ danh sách một lần sẽ gây nghẽn băng thông và làm chậm thời gian tải trang của ứng dụng frontend. Đồng thời, client cần các bộ lọc linh hoạt (theo trạng thái `status`, theo thư mục `folder_id`) và các siêu liên kết điều hướng trực tiếp (HATEOAS) để chuyển trang một cách trực quan mà không cần tự tính toán offset.

### 1.2 Quyết định kiến trúc (Decisions)
1. **Chuẩn Phản Hồi Phân Trang HATEOAS Toàn Hệ Thống (`PaginatedResponseEnvelope`):**
   - Định dạng bao bọc (envelope) thống nhất gồm 4 phần:
     - `success: true`
     - `data: list[DocumentListItem]`
     - `pagination`: `total_items`, `total_pages`, `current_page`, `page_size`, và `links` (`first`, `prev`, `next`, `last`).
     - `meta`: `request_id`, `timestamp`.
   - Nếu ở trang đầu tiên: `links.prev = null`. Nếu ở trang cuối cùng: `links.next = null`.
2. **Bộ Lọc Query Parameters Linh Hoạt & Kiểm Soát Giới Hạn:**
   - `page: int = Query(default=1, ge=1)`
   - `page_size: int = Query(default=20, ge=1, le=100)`
   - `folder_id: UUID | None = Query(default=None)`: Lọc tài liệu theo thư mục lưu trữ.
   - `status: str | None = Query(default=None)`: Lọc theo trạng thái (`uploaded`, `processing`, `completed`, `failed`).
3. **Tối Ưu Hóa Truy Vấn Cơ Sở Dữ Liệu:**
   - Bắt buộc lọc theo `user_id = current_user.id` để đảm bảo cô lập dữ liệu hoàn toàn.
   - Sử dụng cặp truy vấn: một truy vấn đếm tổng (`COUNT(*)`) và một truy vấn lấy dữ liệu có `LIMIT :page_size OFFSET :offset`, sắp xếp theo `created_at DESC`.
   - Tận dụng chỉ mục tổng hợp `idx_documents_user_created` trên bảng `documents`.

---

## 2. Kế Hoạch Triển Khai Chi Tiết (Step-by-Step Execution Plan)

### Bước 1: Khởi Tạo Git Branch
* Tạo và chuyển sang branch: `git checkout -b feat/m1-api-list-documents`.

### Bước 2: Thiết Kế Pydantic Schemas
Trong `apps/api/src/api/schemas/document.py`:
1. `DocumentListItem`:
   - `id: UUID`
   - `filename: str`
   - `file_size_bytes: int`
   - `status: str`
   - `is_persistent: bool`
   - `folder_id: UUID | None`
   - `created_at: datetime`
   - `updated_at: datetime`
   - `links: DocumentItemLinks` (`self_url`, `file_url`, `status_url`)
2. `DocumentPaginationLinks`:
   - `first: str`
   - `prev: str | None`
   - `next: str | None`
   - `last: str`
3. `DocumentPaginationMeta`:
   - `total_items: int`
   - `total_pages: int`
   - `current_page: int`
   - `page_size: int`
   - `links: DocumentPaginationLinks`
4. `DocumentListEnvelope`:
   - Kế thừa `PaginatedResponseEnvelope[list[DocumentListItem]]`.

### Bước 3: Triển Khai Service Layer
Trong `apps/api/src/api/services/document_service.py`:
1. Phương thức `list_documents(user_id: UUID, page: int, page_size: int, folder_id: UUID | None, status_filter: str | None, base_url: str, db: AsyncSession)`:
   - Xây dựng câu lệnh `Select` trên model `DocumentModel` với điều kiện cơ sở `user_id == user_id`.
   - Bổ sung điều kiện lọc `folder_id == folder_id` và `status == status_filter` nếu có.
   - Thực thi câu lệnh `func.count()` để lấy `total_items`.
   - Tính toán `total_pages = math.ceil(total_items / page_size)`.
   - Thực thi truy vấn phân trang với `offset((page - 1) * page_size)` và `limit(page_size)`.
   - Xây dựng URL điều hướng HATEOAS (`first`, `prev`, `next`, `last`) bảo toàn các query parameters hiện tại.

### Bước 4: Đăng Ký Endpoint FastAPI & Mini-Docs
Trong `apps/api/src/api/v1/endpoints/documents.py`:
1. Đăng ký route:
   - `@router.get("", response_model=DocumentListEnvelope)`
2. Mini-Docs 4 phần chuẩn:
   - **Mục đích:** Lấy danh sách tài liệu khoa học của người dùng hiện tại có phân trang HATEOAS và hỗ trợ lọc.
   - **Đầu vào:** `page`, `page_size`, `folder_id`, `status`.
   - **Đầu ra:** HTTP `200 OK` chứa danh sách tài liệu, siêu dữ liệu phân trang và liên kết HATEOAS.
   - **Lưu ý:** Chỉ trả về tài liệu thuộc quyền sở hữu của user; `page_size` tối đa là 100.

### Bước 5: Xây Dựng Bộ Kiểm Thử Tự Động
1. **Điều kiện 1 - Bộ Autotest Riêng Biệt:**
   - Tệp test: `apps/api/tests/test_documents_list.py`.
   - Các ca kiểm thử bao phủ:
     - Danh sách rỗng khi người dùng chưa có tài liệu nào (`total_items = 0`, `data = []`).
     - Phân trang trang đầu tiên (`prev = None`, `next` trỏ đến trang 2).
     - Phân trang trang giữa (`prev` trỏ trang trước, `next` trỏ trang sau).
     - Phân trang trang cuối cùng (`prev` hợp lệ, `next = None`).
     - Lọc tài liệu theo `status` (`completed`, `processing`).
     - Cô lập multi-tenant: User A không thấy tài liệu của User B trong danh sách.
     - Kiểm tra xác thực tham số đầu vào (`page < 1`, `page_size > 100`) trả về `422 Unprocessable Entity`.
     - Kiểm tra sự hiện diện của endpoint trong OpenAPI schema.
2. **Điều kiện 2 - Master Autotest Runner:**
   - Chạy tích hợp toàn bộ qua `apps/api/tests/run_all_api_tests.py`.

### Bước 6: Quy Trình Hoàn Tất
1. Commit code: `feat(api): implement document endpoints and synchronize architecture to Zero-GPU stack`.
2. Cập nhật tài liệu offline tại `docs/vi/swagger.md` (uncommitted) để user review.
