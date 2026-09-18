# Kế Hoạch Kỹ Thuật: Xóa Phiên Nghiên Cứu (DELETE /api/v1/sessions/{id})

> **Mã tài liệu:** `FEAT-M1-API-50`  
> **Trạng thái:** `APPROVED / SẴN SÀNG TRIỂN KHAI EVALUATION HARNESS`  
> **Tác giả:** Antigravity Agent & VeriScholar Engineering Team  
> **Ngày lập:** 18/09/2026  
> **Nhánh Git đề xuất:** `feat/m1-api-delete-session`  
> **API Canonical:** `DELETE /api/v1/sessions/{id}` (#50 trong danh mục API VeriScholar)  
> **Chuẩn thiết kế:** RFC 9110 (HTTP Semantics), RFC 7807 (Problem Details), Cascade Deletion Invariants, Hexagonal Clean Architecture.

---

## 1. Bối Cảnh Nghiệp Vụ & Khảo Sát Thế Giới (Context & SOTA Survey)

### 1.1. Bối Cảnh Người Dùng & Quản Lý Vòng Đời Phiên Nghiên Cứu
Trong quá trình làm việc trên VeriScholar, người dùng có thể tạo hàng chục phiên nghiên cứu khác nhau nhằm khám phá các chủ đề khoa học hoặc so sánh các bộ tài liệu.
- Khi một phiên nghiên cứu hoàn thành hoặc không còn giá trị tham khảo, người dùng có nhu cầu dọn dẹp danh mục hiển thị trên Sidebar bằng cách xóa phiên.
- Thao tác xóa phiên nghiên cứu là **thao tác vĩnh viễn và không thể hoàn tác**.
- Khi một phiên nghiên cứu bị xóa:
  1. Toàn bộ thông tin trạng thái phiên (`research_sessions`), liên kết tài liệu trong phiên (`session_documents`), và lịch sử hội thoại câu hỏi-đáp án kèm trích dẫn (`session_turns`) phải được dọn sạch xếp chồng (**Cascade Cleanup**).
  2. **Bảo vệ toàn vẹn tài liệu gốc:** Việc xóa phiên nghiên cứu tuyệt đối **KHÔNG ĐƯỢC XÓA** các tệp PDF và dữ liệu bài báo gốc (`documents`, `document_chunks`, CAS file storage) trong thư viện chung của người dùng. Tài liệu gốc vẫn phải tồn tại độc lập để có thể sử dụng cho các phiên nghiên cứu khác.
  3. **Phân lập đa người thuê (Multi-Tenancy Security):** Người dùng chỉ được phép xóa phiên thuộc quyền sở hữu của chính mình. Nếu một người dùng lạ cố gắng xóa phiên của người khác, hệ thống phải phản hồi `404 Not Found` (thay vì `403 Forbidden`) để ngăn chặn việc tấn công dò quét sự tồn tại của phiên nghiên cứu.

### 1.2. Khảo Sát Kiến Trúc Quốc Tế (State of the Art)
- **Google NotebookLM:** Cho phép người dùng xóa một Notebook; toàn bộ các note ghi chú tổng hợp và chat history trong Notebook đó sẽ bị xóa, nhưng các file Drive/PDF nguồn nếu đã nằm trên Google Drive cá nhân của người dùng thì không bị ảnh hưởng.
- **ChatGPT / Claude Projects:** Thao tác xóa chat thread hoặc project sẽ dọn sạch toàn bộ các turn trò chuyện thuộc thread đó, trả về mã trạng thái `200 OK` hoặc `204 No Content`.
- **VeriScholar Customization:**
  - Áp dụng mã trạng thái tiêu chuẩn `HTTP 204 No Content` với thân phản hồi rỗng (Empty Body) theo đúng ngữ nghĩa RESTful RFC 9110 cho thao tác xóa thành công.
  - Sử dụng cơ chế khóa ngoại Foreign Key `ON DELETE CASCADE` ở tầng cơ sở dữ liệu PostgreSQL cho bảng trung gian `session_documents` và `session_turns`, loại bỏ hoàn toàn nguy cơ dữ liệu mồ côi (Orphaned Records) mà không cần can thiệp transaction thủ công phức tạp.
  - Kiểm tra tính bất biến bảo tồn tài liệu gốc: Sau khi phiên bị xóa, gọi `GET /api/v1/documents/{doc_id}` vẫn phải trả về đầy đủ tài liệu ở trạng thái toàn vẹn.

---

## 2. Đặc Tả API Kỹ Thuật (API Technical Specification)

### 2.1. Request Thông Tin
- **Method:** `DELETE`
- **Path:** `/api/v1/sessions/{id}`
- **Path Parameter:**
  | Tên tham số | Kiểu dữ liệu | Bắt buộc | Mô tả |
  | :--- | :---: | :---: | :--- |
  | `id` | `UUIDv4` | **Bắt buộc** | Định danh UUID duy nhất của phiên nghiên cứu cần xóa vĩnh viễn. |
- **Headers:**
  - `Authorization: Bearer <token>` hoặc cookie phiên làm việc.
  - `x-user-id: <UUID>` (trong môi trường kiểm thử nội bộ hoặc ASGI transport).

### 2.2. Response Thông Tin
- **Mã HTTP:** `204 No Content`
- **Thân phản hồi (Response Body):** Rỗng (Empty / Zero-byte payload).
- **Headers phản hồi:**
  - `x-request-id: <UUID>` - Mã truy vết yêu cầu.

### 2.3. Mã Lỗi & Xử Lý Ngoại Lệ
| Mã HTTP | Mã Lỗi (`code`) | Tình Huống Kích Hoạt | Hành Động Khắc Phục Cho AI/Client |
| :---: | :--- | :--- | :--- |
| `404` | `SESSION_NOT_FOUND` | Phiên nghiên cứu không tồn tại trên hệ thống, đã bị xóa trước đó, hoặc thuộc quyền sở hữu của người dùng khác. | Bỏ qua hoặc cập nhật lại danh sách phiên trên giao diện Sidebar. |
| `422` | `VALIDATION_ERROR` | Giá trị path parameter `id` không phải định dạng UUIDv4 hợp lệ. | Cung cấp đúng chuỗi định dạng UUID (36 ký tự hex kèm dấu gạch nối). |

---

## 3. Các Bất Biến Của Hệ Thống Đánh Giá (Core System Invariants)

Hệ thống kiểm định tự động áp dụng 5 bất biến cốt lõi cho endpoint xóa phiên nghiên cứu:

1. **Bất biến HTTP 204 No Content (Clean HTTP 204 Invariant):**
   Khi xóa thành công, API phải trả về chính xác mã `HTTP 204 No Content` và thân phản hồi rỗng. Tuyệt đối không trả về payload JSON thừa hoặc mã `200 OK` sai ngữ nghĩa REST.
2. **Bất biến Bảo Toàn Tài Liệu Gốc (Underlying Document Preservation Invariant):**
   Việc xóa phiên nghiên cứu tuyệt đối không xóa tài liệu PDF hoặc dữ liệu bóc tách gốc trong kho thư viện. Truy vấn `GET /api/v1/documents/{document_id}` ngay sau khi xóa phiên phải luôn trả về `HTTP 200 OK` với dữ liệu nguyên vẹn.
3. **Bất biến Xóa Xếp Chồng Triệt Để (Cascade Associations Removal Invariant):**
   Sau khi nhận phản hồi `204 No Content`, thực hiện truy vấn `GET /api/v1/sessions/{id}` đối với chính phiên vừa xóa phải lập tức trả về `HTTP 404 Not Found` với mã lỗi `SESSION_NOT_FOUND`. Các bản ghi liên kết trong `session_documents` và `session_turns` bị xóa đồng thời.
4. **Bất biến Phân Lập Đa Người Thuê (Multi-Tenant Shielding Invariant):**
   Khi một người dùng độc lập (Alien Tenant với UUID khác) cố gắng gọi `DELETE /api/v1/sessions/{id}` của người dùng hiện tại, hệ thống bắt buộc phải từ chối với `HTTP 404 Not Found` (`SESSION_NOT_FOUND`). Tuyệt đối không cho phép xóa chéo và không rò rỉ thông tin sở hữu phiên.
5. **Bất biến Rào Chắn Lặp Thao Tác (Idempotent Repeat Delete Guard):**
   Gọi `DELETE /api/v1/sessions/{id}` lần thứ hai trên cùng một phiên đã bị xóa trước đó phải trả về `HTTP 404 Not Found` (`SESSION_NOT_FOUND`), phản ánh trung thực trạng thái tài nguyên không còn tồn tại trên server.

---

## 4. Kế Hoạch 6 Kịch Bản Kiểm Thử Runner (`delete_session.py`)

| STT | Tên Kịch Bản | Yêu Cầu Gửi Đi | Kèm Header | Kỳ Vọng HTTP | Tiêu Chí Đánh Giá Thành Công |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **01** | Xóa phiên nghiên cứu thành công (Clean Session Deletion) | `DELETE /api/v1/sessions/{seeded_id}` | `x-user-id: {test_user}` | `204 No Content` | HTTP 204, thân phản hồi rỗng. |
| **02** | Bảo tồn tài liệu gốc trong thư viện (Document Preservation) | `GET /api/v1/documents/{seeded_doc_id}` | `x-user-id: {test_user}` | `200 OK` | Tài liệu vẫn tồn tại nguyên vẹn trong thư viện, không bị xóa theo phiên. |
| **03** | Xác thực xóa xếp chồng triệt để (Cascade Verification) | `GET /api/v1/sessions/{seeded_id}` | `x-user-id: {test_user}` | `404 Not Found` | Phiên không còn tồn tại (`SESSION_NOT_FOUND`), liên kết bị dọn sạch. |
| **04** | Rào chắn phân lập dữ liệu đa người thuê (Multi-tenant Guard) | `DELETE /api/v1/sessions/{alien_session_id}` | `x-user-id: {test_user}` | `404 Not Found` | Bị từ chối với `SESSION_NOT_FOUND`, không thể xóa phiên của người khác. |
| **05** | Chặn xóa lặp lại phiên đã xóa (Repeat Delete Guard) | `DELETE /api/v1/sessions/{seeded_id}` | `x-user-id: {test_user}` | `404 Not Found` | Lần gọi thứ 2 trả về `404 Not Found` với mã `SESSION_NOT_FOUND`. |
| **06** | Chặn định danh không đúng chuẩn UUID (Malformed UUID Path Guard) | `DELETE /api/v1/sessions/malformed-uuid-xyz` | `x-user-id: {test_user}` | `422 Unprocessable` | FastAPI chặn trước controller, trả về lỗi validation schema. |

---

## 5. Danh Mục Tệp Triển Khai

1. **Tài liệu kỹ thuật:**
   - `docs/vi/decided/module-01/feat-m1-api-delete-session.md` (Tạo mới).
   - `docs/vi/design-api-eval-snapshots.md` (Cập nhật ma trận Section 6 và Section 7.5).
2. **Script Runner kiểm thử tự động:**
   - `scripts/eval/runners/delete_session.py` (Tạo mới `DeleteSessionAPIRunner`).
   - `scripts/eval/runners/__init__.py` (Đăng ký runner và các alias: `delete_session`, `delete-session`, `delete_sessions`).
3. **Báo cáo kết quả kiểm thử:**
   - `temp/output/test/delete_session.md` (Sinh tự động sau khi chạy runner).
