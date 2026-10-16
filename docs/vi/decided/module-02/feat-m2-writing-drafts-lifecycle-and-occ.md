# Module 2: Quản lý Vòng đời Bản thảo Nghiên cứu & Kiểm soát Đồng thời Lạc quan (OCC)

## 1. Giới thiệu & Bối cảnh Nghiệp vụ
Module 2 (Academic Writing & SAFE Fact-Checking) cung cấp môi trường soạn thảo học thuật tích hợp kiểm chứng sự thật và biên dịch trực tiếp. Để đảm bảo an toàn dữ liệu khi người dùng mở nhiều tab hoặc nhiều tiến trình chỉnh sửa bản thảo cùng lúc, hệ thống áp dụng cơ chế **Optimistic Concurrency Control (OCC)** chuẩn RFC 9110 / RFC 7232.

---

## 2. Kiến trúc Thực thể & Invariants (Hexagonal Domain)

### Aggregate Root: `Draft`
- Vị trí: `packages/core/src/core/domain/entities/draft.py`
- Định dạng hỗ trợ: `latex` (mặc định) và `markdown`.
- Bất biến OCC: Mỗi lần cập nhật nội dung hoặc đổi tiêu đề, trường `version` tăng đơn điệu `version = current_version + 1`. Nếu phiên bản yêu cầu không khớp `expected_version`, hệ thống ném ngoại lệ `ConcurrencyConflictError`.

```python
class Draft(BaseModel):
    id: UUID
    user_id: UUID
    title: str = "Untitled Draft"
    content: str = ""
    format: str = "latex"
    version: int = 1
    created_at: datetime
    updated_at: datetime
```

### Mô hình Lưu trữ: `DraftModel`
- Vị trí: `apps/api/src/api/db/models/draft.py`
- Bảng: `drafts`
- Khóa ngoại: `user_id -> users.id` với `ondelete="CASCADE"`.
- Chỉ mục: `ix_drafts_user_id` và `ix_drafts_user_id_updated_at` phục vụ truy vấn phân trang danh sách tốc độ cao.
- Kiểm tra tính hợp lệ: `CheckConstraint("format IN ('latex', 'markdown')")` và `CheckConstraint("version >= 1")`.

---

## 3. Danh mục API REST Contracts

### 3.1. Tạo bản thảo mới
- **Method & Route:** `POST /api/v1/drafts`
- **Request Body:**
  ```json
  {
    "title": "Quantum Transformer Survey",
    "content": "\\documentclass{article}...",
    "format": "latex"
  }
  ```
- **Response Headers:** `Location: /api/v1/drafts/{id}`, `ETag: "v1"`
- **Response Code:** `HTTP 201 Created`

### 3.2. Liệt kê bản thảo phân trang
- **Method & Route:** `GET /api/v1/drafts?page=1&per_page=20`
- **Response Envelope:** `PaginatedResponseEnvelope[DraftResponse]`

### 3.3. Xem chi tiết bản thảo
- **Method & Route:** `GET /api/v1/drafts/{id}`
- **Response Headers:** `ETag: "v{version}"`
- **Response Code:** `HTTP 200 OK`

### 3.4. Chỉnh sửa bản thảo với OCC
- **Method & Route:** `PUT /api/v1/drafts/{id}`
- **Request Headers:** `If-Match: "v{version}"` (hoặc truyền `version` trong body)
- **Request Body:**
  ```json
  {
    "title": "Updated Title",
    "content": "\\documentclass{article}...",
    "format": "latex",
    "version": 1
  }
  ```
- **Xử lý xung đột (OCC Conflict):**
  - Nếu phiên bản gửi lên khác với phiên bản hiện tại trong cơ sở dữ liệu, server lập tức ngắt giao dịch và trả về `HTTP 412 Precondition Failed`:
  ```json
  {
    "error": {
      "code": "CONCURRENCY_CONFLICT",
      "message": "Xung đột phiên bản: bản thảo hiện tại ở phiên bản 2, yêu cầu gửi phiên bản 1.",
      "action": "Re-fetch draft GET /api/v1/drafts/{id} to get the latest version before retrying."
    }
  }
  ```
  - Nếu thiếu cả `If-Match` và `version`, server trả về `HTTP 428 Precondition Required`.

### 3.5. Xóa bản thảo
- **Method & Route:** `DELETE /api/v1/drafts/{id}`
- **Response Code:** `HTTP 204 No Content`

---

## 4. Kiểm thử Tích hợp
Toàn bộ quy trình CRUD và xử lý xung đột đồng thời OCC được kiểm thử tự động tại `apps/api/tests/test_drafts_lifecycle.py`:
- `test_draft_crud_lifecycle`: Kiểm tra luồng tạo, đọc, sửa, xóa với ETag header.
- `test_draft_occ_conflict_detection`: Mô phỏng 2 phiên client cập nhật đồng thời, client chậm nhận mã HTTP 412.
- `test_draft_multi_tenant_isolation`: Xác nhận người dùng A không thể truy cập hoặc sửa bản thảo của người dùng B.
