# Kế Hoạch Kỹ Thuật: Tự Động Lưu Vị Trí Cuộn Trang PDF & Tab Đang Mở Với Khóa OCC (PATCH /api/v1/sessions/{id}/viewport)

> **Mã tài liệu:** `FEAT-M1-API-49`  
> **Trạng thái:** `APPROVED / SẴN SÀNG TRIỂN KHAI EVALUATION HARNESS`  
> **Tác giả:** Antigravity Agent & VeriScholar Engineering Team  
> **Ngày lập:** 18/09/2026  
> **Nhánh Git đề xuất:** `feat/m1-api-patch-session-viewport`  
> **API Canonical:** `PATCH /api/v1/sessions/{id}/viewport` (#49 trong danh mục API VeriScholar)  
> **Chuẩn thiết kế:** RFC 9110 / RFC 7232 (Conditional Requests & OCC), RFC 7807 (Problem Details), Dual-Pane Synchronization, Hexagonal Clean Architecture.

---

## 1. Bối Cảnh Nghiệp Vụ & Khảo Sát Thế Giới (Context & SOTA Survey)

### 1.1. Bối Cảnh Nghiệp Vụ & Trải Nghiệm Dual-Pane
Trong VeriScholar, không gian làm việc của nhà nghiên cứu được tổ chức dưới dạng giao diện song song hai cột (**Dual-Pane Workspace**):
- **Cột trái (Left Pane):** PDF Canvas Viewer hỗ trợ cuộn mượt (virtualized scroll), hiển thị tài liệu theo từng trang (`page`), tỷ lệ thu phóng (`zoom_ratio`), và vị trí cuộn trang dọc (`scroll_top`).
- **Cột phải (Right Pane):** Hộp công cụ nghiên cứu đa năng (`active_tab`), cho phép chuyển đổi tức thì giữa: Trò chuyện AI (`chat`), Ghi chú khoa học (`notes`), Trích xuất tóm tắt (`summary`), Bản đồ tri thức (`graph`), và Bản thảo học thuật (`draft`).
- Khi người dùng đang đọc tài liệu tại trang 5, phóng to 125% và chuyển sang tab `notes`, hệ thống cần định kỳ hoặc tức thời tự động lưu trạng thái này lên máy chủ (**Auto-Save Viewport State**).
- Nhờ đó, khi người dùng tải lại trang (F5), chuyển thiết bị hoặc đóng trình duyệt và mở lại sau đó, toàn bộ không gian làm việc được khôi phục nguyên vẹn tại đúng tọa độ cuộn mà không bị giật trang hay sai lệch ngữ cảnh.

### 1.2. Khóa Kiểm Soát Cạnh Tranh Lạc Quan (Optimistic Concurrency Control - OCC)
Trong môi trường người dùng mở đồng thời nhiều tab trình duyệt hoặc AI Agent cùng lúc điều hướng tài liệu để minh họa dẫn chứng, nguy cơ ghi đè mất mát dữ liệu (**Lost Updates**) là rất lớn nếu sử dụng cập nhật tự do không kiểm soát.
- VeriScholar áp dụng cơ chế **Optimistic Concurrency Control (OCC)** tuân thủ chuẩn HTTP quốc tế RFC 7232 / RFC 9110:
  1. Client bắt buộc phải gửi kèm header `If-Match: "v{version}"` tương ứng với phiên bản ETag hiện tại đang nắm giữ.
  2. Nếu thiếu header `If-Match`, API từ chối với `HTTP 428 Precondition Required`.
  3. Nếu header `If-Match` mang phiên bản cũ (ví dụ gửi `"v1"` khi phiên bản trên server đã được cập nhật lên `2`), API ném `HTTP 412 Precondition Failed` với mã lỗi `CONCURRENCY_CONFLICT`. Client được thông báo để tải lại trạng thái mới nhất thay vì vô tình ghi đè.
  4. Sau khi cập nhật thành công, trường `version` trong cơ sở dữ liệu được tăng lên 1, và API phản hồi kèm header `ETag: "v{version+1}"`.

### 1.3. Ràng Buộc Toàn Vẹn Liên Kết Tài Liệu
- Tham số `active_document_id` (nếu được cung cấp) bắt buộc phải là UUID của một tài liệu **đang thực sự được gắn vào phiên làm việc đó** (có bản ghi trong bảng `session_documents`).
- Nếu client truyền một UUID của tài liệu không thuộc phiên làm việc, API lập tức từ chối với `HTTP 400 Bad Request` và mã lỗi `INVALID_ACTIVE_DOCUMENT`, loại bỏ nguy cơ trỏ sai ngữ cảnh.

---

## 2. Đặc Tả API Kỹ Thuật (API Technical Specification)

### 2.1. Request Thông Tin
- **Method:** `PATCH`
- **Path:** `/api/v1/sessions/{id}/viewport`
- **Headers:**
  - `If-Match: "v{version}"` (**Bắt buộc**): Chuỗi ETag phiên bản hiện tại (ví dụ: `"v1"`).
  - `Content-Type: application/json`
  - `x-user-id: <UUID>`: Định danh người dùng thực hiện.
- **Path Parameter:**
  | Tên tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
  | :--- | :---: | :---: | :--- |
  | `id` | `UUIDv4` | **Bắt buộc** | Định danh duy nhất của phiên nghiên cứu. |
- **Request Body (`SessionUpdateViewportRequest`):**
  ```json
  {
    "viewport_state": {
      "page": 3,
      "zoom_ratio": 1.25,
      "scroll_top": 450.0
    },
    "active_tab": "notes",
    "active_document_id": "2f4de426-02dc-4434-b268-e18de78773ae"
  }
  ```
  - `viewport_state` (Object, Bắt buộc):
    - `page` (Integer, `>= 1`): Số trang PDF đang hiển thị.
    - `zoom_ratio` (Float, `> 0.0`): Hệ số phóng to hiển thị.
    - `scroll_top` (Float, `>= 0.0`): Tọa độ cuộn dọc tính bằng pixel.
  - `active_tab` (String, Mặc định: `"chat"`): Phải thuộc tập `["chat", "notes", "summary", "graph", "draft"]`.
  - `active_document_id` (UUIDv4, Tùy chọn): Định danh bài báo đang mở trên Canvas.

### 2.2. Response Thông Tin
- **Mã HTTP:** `200 OK`
- **Headers Phản Hồi:**
  - `ETag: "v{version}"` (Ví dụ: `"v2"`, tăng 1 so với phiên bản trước).
  - `x-request-id: <UUID>`
- **Thân Phản Hồi (`SessionSingleEnvelope`):**
  ```json
  {
    "success": true,
    "data": {
      "id": "8b8db74b-3f0f-493e-8a39-827484b2ad29",
      "title": "Nghiên cứu Kiến trúc Transformer",
      "document_ids": ["2f4de426-02dc-4434-b268-e18de78773ae"],
      "active_document_id": "2f4de426-02dc-4434-b268-e18de78773ae",
      "viewport_state": {
        "page": 3,
        "zoom_ratio": 1.25,
        "scroll_top": 450.0
      },
      "active_tab": "notes",
      "is_archived": false,
      "version": 2,
      "message_count": 0,
      "documents": [...],
      "warnings": [],
      "created_at": "2026-09-18T15:20:00.000000Z",
      "updated_at": "2026-09-18T15:25:30.000000Z"
    },
    "meta": {
      "request_id": "req_8492048ab",
      "timestamp": "2026-09-18T15:25:30.123456Z"
    }
  }
  ```

### 2.3. Mã Lỗi & Xử Lý Ngoại Lệ
| Mã HTTP | Mã Lỗi (`code`) | Tình Huống Kích Hoạt | Hành Động Cho AI/Client |
| :---: | :--- | :--- | :--- |
| `428` | `PRECONDITION_REQUIRED` | Thiếu header `If-Match` trong yêu cầu PATCH. | Đính kèm header `If-Match: "v{version}"` từ phản hồi GET/POST trước đó. |
| `412` | `CONCURRENCY_CONFLICT` | Phiên bản gửi lên không khớp với `version` hiện tại của phiên trên server. | Gọi `GET /api/v1/sessions/{id}` lấy phiên bản mới nhất rồi áp dụng lại thay đổi. |
| `400` | `INVALID_ACTIVE_DOCUMENT` | `active_document_id` không nằm trong danh sách tài liệu của phiên nghiên cứu. | Kiểm tra lại danh mục `document_ids` thuộc phiên trước khi đặt làm active. |
| `400` | `INVALID_IF_MATCH_HEADER` | Giá trị header `If-Match` sai cú pháp hoặc không thể phân giải thành số nguyên dương. | Cung cấp đúng định dạng ví dụ `"v1"`. |
| `403` | `SESSION_ARCHIVED` | Phiên nghiên cứu đã được lưu trữ (archived), không được phép cập nhật viewport. | Khôi phục phiên nghiên cứu về trạng thái hoạt động trước khi điều hướng. |
| `404` | `SESSION_NOT_FOUND` | Phiên không tồn tại hoặc thuộc quyền sở hữu của người dùng khác. | Kiểm tra lại session UUID. |
| `422` | `VALIDATION_ERROR` | Tham số đường dẫn `id` không phải UUID hợp lệ, hoặc payload body vi phạm ràng buộc schema. | Điều chỉnh tham số cho khớp schema. |

---

## 3. Các Bất Biến Của Hệ Thống Đánh Giá (Core System Invariants)

1. **Bất biến Khóa Phiên Bản Đồng Thời (OCC Version Increment Invariant):**
   Khi yêu cầu có `If-Match` hợp lệ, hệ thống phải cập nhật `version = version + 1`, trả về phản hồi `HTTP 200 OK` và header `ETag: "v{version_moi}"` đồng nhất hoàn toàn với trường `data.version`.
2. **Bất biến Chống Ghi Đè Lạc Hậu (Stale Write / Conflict Guard Invariant):**
   Gửi lại yêu cầu với `If-Match` cũ sau khi version đã tăng phải kích hoạt `HTTP 412 Precondition Failed` với mã lỗi `CONCURRENCY_CONFLICT`.
3. **Bất biến Bắt Buộc Điều Kiện (Precondition Enforcement Invariant):**
   Mọi yêu cầu thiếu header `If-Match` phải bị từ chối với `HTTP 428 Precondition Required`.
4. **Bất biến Toàn Vẹn Liên Kết Tài Liệu (Document Boundary Invariant):**
   Chỉ cho phép chọn `active_document_id` thuộc danh mục tài liệu của chính phiên đó; truyền tài liệu lạ phải trả về `HTTP 400 Bad Request` với mã `INVALID_ACTIVE_DOCUMENT`.
5. **Bất biến Phân Lập Đa Người Thuê (Multi-Tenant Shielding Invariant):**
   Người dùng khác (Alien Tenant) cố gắng cập nhật viewport của phiên sẽ nhận về `HTTP 404 SESSION_NOT_FOUND` (Zero Cross-Tenant Data Leakage).

---

## 4. Kế Hoạch 6 Kịch Bản Kiểm Thử Runner (`patch_session_viewport.py`)

| STT | Kịch Bản Kiểm Thử | Yêu Cầu Gửi Đi | Kèm Header | Kỳ Vọng HTTP | Tiêu Chí Đánh Giá Thành Công |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **01** | Cập nhật viewport thành công (Valid OCC Update) | `PATCH /api/v1/sessions/{id}/viewport` | `If-Match: "v1"` | `200 OK` | `data.version == 2`, `ETag: "\"v2\""`, `page == 3`, `active_tab == "notes"`. |
| **02** | Chặn xung đột phiên bản cũ (Concurrency Conflict Guard) | `PATCH /api/v1/sessions/{id}/viewport` | `If-Match: "v1"` | `412 Precondition Failed` | Trả về mã lỗi `CONCURRENCY_CONFLICT` khi server đã ở phiên bản 2. |
| **03** | Chặn yêu cầu thiếu If-Match (Precondition Required Guard) | `PATCH /api/v1/sessions/{id}/viewport` | *Không gửi If-Match* | `428 Precondition Required` | Trả về mã lỗi `PRECONDITION_REQUIRED`. |
| **04** | Chặn tài liệu không thuộc phiên (Invalid Active Document Guard) | `PATCH /api/v1/sessions/{id}/viewport` | `If-Match: "v2"`, `active_document_id: {unlinked_id}` | `400 Bad Request` | Trả về mã lỗi `INVALID_ACTIVE_DOCUMENT`. |
| **05** | Rào chắn bảo vệ đa người thuê (Multi-tenant Isolation Guard) | `PATCH /api/v1/sessions/{id}/viewport` | `x-user-id: {alien_user}`, `If-Match: "v2"` | `404 Not Found` | Bị từ chối với `SESSION_NOT_FOUND`. |
| **06** | Rào chắn định danh đường dẫn (Malformed UUID Path Guard) | `PATCH /api/v1/sessions/malformed-uuid/viewport` | `If-Match: "v2"` | `422 Unprocessable` | FastAPI chặn trước controller, trả về `VALIDATION_ERROR`. |

---

## 5. Danh Mục Tệp Triển Khai

1. **Tài liệu thiết kế kỹ thuật:**
   - `docs/vi/decided/module-01/feat-m1-api-patch-session-viewport.md` (Tạo mới).
   - `docs/vi/design-api-eval-snapshots.md` (Cập nhật ma trận Section 6 và Section 7.6).
2. **Script Runner kiểm thử tự động:**
   - `scripts/eval/runners/patch_session_viewport.py` (Tạo mới `PatchSessionViewportAPIRunner`).
   - `scripts/eval/runners/__init__.py` (Đăng ký runner và các alias).
3. **Báo cáo kết quả kiểm thử:**
   - `temp/output/test/patch_session_viewport.md` (Sinh tự động sau khi chạy runner).
