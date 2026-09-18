# Kế Hoạch Kỹ Thuật: Khôi Phục Nguyên Vẹn Phiên Nghiên Cứu (GET /api/v1/sessions/{id})

> **Mã tài liệu:** `FEAT-M1-API-47`  
> **Trạng thái:** `APPROVED / SẴN SÀNG TRIỂN KHAI EVALUATION HARNESS`  
> **Tác giả:** Antigravity Agent & VeriScholar Engineering Team  
> **Ngày lập:** 17/09/2026  
> **Nhánh Git đề xuất:** `feat/m1-api-get-session-detail`  
> **API Canonical:** `GET /api/v1/sessions/{id}` (#47 trong danh mục API VeriScholar)  
> **Chuẩn thiết kế:** RFC 9110 (HTTP Semantics), RFC 7232 (Conditional Requests & ETag), RFC 7807 (Problem Details), Optimistic Concurrency Control (OCC), Hexagonal Clean Architecture.

---

## 1. Bối Cảnh Nghiệp Vụ & Khảo Sát Thế Giới (Context & SOTA Survey)

### 1.1. Bối Cảnh Người Dùng & Trải Nghiệm Khôi Phục Không Gian Làm Việc
Trong ứng dụng VeriScholar, giao diện làm việc chia đôi (Dual-Pane Workspace) gồm:
- **Khung bên trái (Left Pane):** Trình xem tài liệu PDF khoa học (PDF Canvas Viewer), hiển thị trang hiện tại (`page`), tỷ lệ phóng to (`zoom_ratio`), và vị trí cuộn (`scroll_top`).
- **Khung bên phải (Right Pane):** Khung công cụ đa năng với các tab nghiệp vụ (`active_tab`: `chat`, `notes`, `summary`, `graph`, `draft`).

Khi người dùng thao tác:
1. Bấm vào một phiên nghiên cứu trên thanh Sidebar bên trái.
2. Tải lại trang (F5 / Browser Reload) hoặc mở liên kết phiên nghiên cứu được chia sẻ/lưu bookmark.
3. Chuyển đổi qua lại giữa các phiên làm việc song song.

Hệ thống phải lập tức khôi phục **nguyên vẹn 100% trạng thái** không gian làm việc mà không làm gián đoạn dòng tư duy khoa học của người dùng.

### 1.2. Khảo Sát Kiến Trúc Quốc Tế (State of the Art)
- **Google NotebookLM:** Khi người dùng mở một Notebook, backend lập tức tải toàn bộ danh mục nguồn tài liệu (Sources list), trạng thái tóm tắt, và lịch sử câu hỏi gợi ý, đồng thời duy trì con trỏ phiên bản để đồng bộ dữ liệu.
- **Claude Artifacts & Projects:** Lưu trữ snapshot không gian làm việc và đồng bộ trạng thái cửa sổ hiển thị, đảm bảo khi reload trình duyệt, artifact đang xem dở không bị đóng lại.
- **VeriScholar Innovation:**
  - **Khôi phục toàn vẹn Viewport Canvas (`viewport_state`):** Lưu chính xác vị trí cuộn pixel (`scroll_top`), số trang (`page`), và tỷ lệ thu phóng (`zoom_ratio`) của tài liệu PDF đang mở (`active_document_id`).
  - **Gắn Khóa OCC Phiên Bản (`ETag: "v{version}"`):** Mỗi phản hồi `200 OK` đi kèm header `ETag` mang số phiên bản hiện tại (`v1`, `v2`, ...). Giá trị này là điều kiện tiên quyết bắt buộc để máy khách gửi header `If-Match` trong các thao tác biến đổi tiếp theo (như cập nhật tiêu đề `#48`, lưu tọa độ viewport `#49`, thêm tài liệu `#50`), ngăn chặn triệt để xung đột ghi đè đồng thời (Lost Updates).
  - **Phân lập Đa người thuê (Multi-Tenancy Security):** Người dùng chỉ được khôi phục phiên nghiên cứu thuộc sở hữu của chính mình. Nếu truy vấn ID của người dùng khác, hệ thống trả về `404 Not Found` (thay vì `403 Forbidden`) để ngăn chặn tấn công dò quét sự tồn tại của phiên (Resource Enumeration Attack).

---

## 2. Đặc Tả API Kỹ Thuật (API Technical Specification)

### 2.1. Request Thông Tin
- **Method:** `GET`
- **Path:** `/api/v1/sessions/{id}`
- **Path Parameter:**
  | Tên tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
  | :--- | :---: | :---: | :--- |
  | `id` | `UUIDv4` | **Bắt buộc** | Định danh UUID duy nhất của phiên nghiên cứu cần khôi phục. |
- **Headers:**
  - `Authorization: Bearer <token>` hoặc Cookie xác thực người dùng.
  - `x-user-id: <UUID>` (trong môi trường kiểm thử nội bộ hoặc ASGI transport).

### 2.2. Response Thông Tin
- **Mã HTTP:** `200 OK`
- **Headers phản hồi:**
  - `Content-Type: application/json; charset=utf-8`
  - `ETag: "v{version}"` (Ví dụ: `"v1"`, `"v14"`) - Khóa phiên bản phục vụ kiểm soát đồng thời.
- **Cấu trúc dữ liệu:** `SessionSingleEnvelope` (kế thừa `SingleResponseEnvelope[SessionResponseData]`)
```json
{
  "success": true,
  "data": {
    "id": "497894b2-a211-417b-82d0-2ff5001c7a5d",
    "title": "Nghiên cứu Kiến trúc Transformer và Attention Mechanism",
    "document_ids": [
      "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c"
    ],
    "active_document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
    "viewport_state": {
      "page": 1,
      "zoom_ratio": 1.0,
      "scroll_top": 0.0
    },
    "active_tab": "chat",
    "is_archived": false,
    "version": 1,
    "message_count": 0,
    "documents": [
      {
        "id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
        "title": "Attention Is All You Need",
        "filename": "1706.03762v7.pdf",
        "status": "completed",
        "file_size_bytes": 2215244,
        "added_at": "2026-09-17T15:02:09.978540Z",
        "display_order": 0
      }
    ],
    "warnings": [],
    "created_at": "2026-09-17T15:02:09.978540Z",
    "updated_at": "2026-09-17T15:02:09.978543Z"
  },
  "meta": {
    "request_id": "req_839a9c21b45f",
    "timestamp": "2026-09-17T15:20:00.000000Z"
  }
}
```

### 2.3. Mã Lỗi & Xử Lý Ngoại Lệ
| Mã HTTP | Mã Lỗi (`code`) | Tình Huống Kích Hoạt | Hành Động Khắc Phục Cho AI/Client |
| :---: | :--- | :--- | :--- |
| `404` | `SESSION_NOT_FOUND` | Phiên nghiên cứu không tồn tại trên hệ thống hoặc thuộc quyền sở hữu của người dùng khác. | Kiểm tra lại UUID phiên hoặc điều hướng người dùng tạo phiên mới. |
| `422` | `VALIDATION_ERROR` | Giá trị path parameter `id` không phải định dạng UUIDv4 hợp lệ. | Cung cấp đúng chuỗi định dạng UUID (36 ký tự hex kèm dấu gạch nối). |

---

## 3. Các Bất Biến Của Hệ Thống Đánh Giá (Core System Invariants)

Để đảm bảo việc khôi phục phiên nghiên cứu đạt độ tin cậy tuyệt đối, hệ thống đánh giá tự động áp dụng 5 bất biến:

1. **Bất biến Khóa Phiên Bản ETag (OCC ETag Invariant):**
   Header `ETag` phải xuất hiện trong phản hồi `200 OK`, có định dạng chuẩn RFC 9110/RFC 7232 `"{version}"` (có dấu ngoặc kép kép bọc ngoài) và giá trị số phiên bản bên trong phải khớp chính xác với trường `data.version` trong JSON payload.
2. **Bất biến Khôi Phục Toàn Vẹn Không Gian Làm Việc (Complete State Invariant):**
   Trạng thái trả về phải khôi phục đầy đủ:
   - `viewport_state`: Gồm 3 trường số thực/nguyên: `page >= 1`, `zoom_ratio > 0`, `scroll_top >= 0`.
   - `active_tab`: Phải thuộc tập hợp cho phép `["chat", "notes", "summary", "graph", "draft"]`.
   - `documents`: Danh sách bài báo liên kết kèm thứ tự hiển thị `display_order` và trạng thái xử lý `status`.
3. **Bất biến Phân Lập Đa Người Thuê (Multi-Tenant Shielding Invariant):**
   Khi một người dùng độc lập (Alien Tenant với UUID khác) cố gắng gọi `GET /api/v1/sessions/{id}` của người dùng hiện tại, hệ thống bắt buộc phải trả về `HTTP 404 Not Found` với mã lỗi `SESSION_NOT_FOUND`. Tuyệt đối không rò rỉ bất kỳ thông tin nào về sự tồn tại của phiên.
4. **Bất biến Rào Chắn Định Dạng Đường Dẫn (Path UUID Validation Guard):**
   Khi gửi một chuỗi định danh không hợp lệ (ví dụ: `not-a-valid-uuid`), hệ sinh thái FastAPI / Pydantic phải chặn ngay ở tầng routing và trả về `HTTP 422 Unprocessable Entity` với định dạng lỗi RFC 7807 chuẩn hóa.
5. **Bất biến Dọn Dẹp Khép Kín (Hermetic Teardown Invariant):**
   Mọi tài liệu PDF và phiên nghiên cứu tạo ra phục vụ bài test khôi phục chi tiết đều được đăng ký với `EvaluationContext` và tự động dọn dẹp sạch sẽ qua các endpoint REST `DELETE /api/v1/sessions/{id}` và `DELETE /api/v1/documents/{id}` ngay sau khi runner kết thúc.

---

## 4. Kế Hoạch 6 Kịch Bản Kiểm Thử Runner (`get_session_detail.py`)

| STT | Tên Kịch Bản | Yêu Cầu Gửi Đi | Kèm Header | Kỳ Vọng HTTP | Tiêu Chí Đánh Giá Thành Công |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **01** | Khôi phục phiên nghiên cứu đầy đủ (Full Session Restoration) | `GET /api/v1/sessions/{seeded_id}` | `x-user-id: {test_user}` | `200 OK` | `success=True`, `id` khớp, `document_ids` chứa doc đã nạp, `viewport_state` hợp lệ, `active_tab="chat"`. |
| **02** | Kiểm toán Header ETag chuẩn OCC (ETag Header Conformance) | `GET /api/v1/sessions/{seeded_id}` | `x-user-id: {test_user}` | `200 OK` | Header `ETag` có dạng `"v{version}"`, khớp chính xác với `data.version`. |
| **03** | Khôi phục phiên nghiên cứu rỗng (Empty Session Restoration) | `GET /api/v1/sessions/{empty_id}` | `x-user-id: {test_user}` | `200 OK` | `document_ids=[]`, `active_document_id=None`, `documents=[]`, `message_count=0`. |
| **04** | Rào chắn phân lập dữ liệu đa người thuê (Multi-tenant Guard) | `GET /api/v1/sessions/{seeded_id}` | `x-user-id: {alien_user}` | `404 Not Found` | Bị từ chối với mã lỗi `SESSION_NOT_FOUND`. Zero data leakage. |
| **05** | Truy vấn UUID ngẫu nhiên không tồn tại (Non-existent UUID Guard) | `GET /api/v1/sessions/{random_uuid}` | `x-user-id: {test_user}` | `404 Not Found` | Trả về `404 Not Found` với mã lỗi `SESSION_NOT_FOUND`. |
| **06** | Chặn định danh không đúng chuẩn UUID (Malformed UUID Path Guard) | `GET /api/v1/sessions/malformed-uuid-123` | `x-user-id: {test_user}` | `422 Unprocessable` | FastAPI chặn trước controller, trả về lỗi validation schema. |

---

## 5. Danh Mục Tệp Triển Khai

1. **Tài liệu kỹ thuật:**
   - `docs/vi/decided/module-01/feat-m1-api-get-session-detail.md` (Tạo mới).
   - `docs/vi/design-api-eval-snapshots.md` (Cập nhật ma trận Section 6 và Section 7.4).
2. **Script Runner kiểm thử tự động:**
   - `scripts/eval/runners/get_session_detail.py` (Tạo mới `GetSessionDetailAPIRunner`).
   - `scripts/eval/runners/__init__.py` (Đăng ký runner và các alias: `get_session_detail`, `get_session`, `session_detail`).
3. **Báo cáo kết quả kiểm thử:**
   - `temp/output/test/get_session_detail.md` (Sinh tự động sau khi chạy runner).
