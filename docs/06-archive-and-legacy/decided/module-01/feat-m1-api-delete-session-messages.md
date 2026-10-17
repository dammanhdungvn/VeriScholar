# Kế Hoạch Thiết Kế Kỹ Thuật: DELETE /api/v1/sessions/{id}/messages

> **Mã tính năng**: `FEAT-M1-API-DELETE-SESSION-MESSAGES`  
> **Endpoint**: `DELETE /api/v1/sessions/{id}/messages`  
> **STT API PRD**: `#54. Xóa lịch sử hội thoại của phiên (Idempotent 204)`  
> **Trạng thái**: Decided / In-Progress  
> **Tiêu chuẩn áp dụng**: RFC 9110 (HTTP Semantics - DELETE & 204 No Content), Idempotency Contract, Parent Session Isolation (Zero Side-Effects), Multi-Tenancy Shielding.

---

## 1. Bối Cảnh & Mục Tiêu Nghiệp Vụ

Trong quá trình nghiên cứu tài liệu trên VeriScholar, người dùng có thể muốn làm mới ngữ cảnh đối thoại (Clear Chat History) để bắt đầu một chuỗi câu hỏi mới về một đề tài hoặc khía cạnh khác của bài báo, mà vẫn muốn giữ nguyên phiên làm việc (`ResearchSession`), bao gồm:
- Toàn bộ danh sách bài báo đã nạp (`document_ids`).
- Bài báo đang mở (`active_document_id`).
- Trạng thái cuộn trang và tỷ lệ thu phóng (`viewport_state`).
- Thẻ đang kích hoạt (`active_tab`).

Endpoint `DELETE /api/v1/sessions/{id}/messages` đảm nhận nhiệm vụ:
1. **Xóa Toàn Bộ Lượt Hỏi Đáp Của Phiên (Atomic Message Purge)**: Xóa sạch toàn bộ các bản ghi `SessionTurnModel` liên kết với phiên nghiên cứu mục tiêu.
2. **Tuân Thủ Tuyệt Đối Tính Bất Biến Lũy Đẳng (Idempotency Invariant)**: Theo chuẩn RFC 9110, phương thức DELETE có tính lũy đẳng (Idempotent). Khi người dùng gọi lại lệnh xóa nhiều lần, hệ thống luôn phản hồi `HTTP 204 No Content` chứ không sinh lỗi 404 hay 400 do danh sách đã rỗng.
3. **Bảo Tồn Toàn Vẹn Thực Thể Cha (Zero Side-Effects on Parent Session)**: Hành động xóa tin nhắn chỉ tác động lên bảng con `session_turns`, tuyệt đối không làm suy giảm, thay đổi cấu trúc hoặc xóa nhầm phiên cha `research_sessions`.
4. **Bảo Mật Đa Thuê Tuyệt Đối (Multi-Tenant Shielding)**: Kiểm tra nghiêm ngặt quyền sở hữu `user_id`. Mọi yêu cầu xóa từ một tenant khác đều bị chặn với mã `HTTP 404 Not Found` (`SESSION_NOT_FOUND`).

---

## 2. 5 Bất Biến Nghiệp Vụ Cốt Lõi (Core Invariants)

1. **RFC 9110 Idempotent 204 Invariant**:
   - Mọi cuộc gọi hợp lệ đến `DELETE /api/v1/sessions/{id}/messages` phải trả về `HTTP 204 No Content` với thân phản hồi hoàn toàn rỗng.
   - Việc gọi liên tiếp $N$ lần lệnh DELETE vào cùng một phiên phải trả về kết quả nhất quán `HTTP 204 No Content`.
2. **State Transition & Emptiness Invariant**:
   - Ngay sau khi lệnh DELETE hoàn tất, cuộc gọi `GET /api/v1/sessions/{id}/messages` kế tiếp phải phản hồi `data: []` và `meta.total == 0`.
3. **Parent Session Preservation Invariant**:
   - Phiên nghiên cứu cha `research_sessions` phải giữ nguyên vẹn 100% thuộc tính (`title`, `active_document_id`, `viewport_state`, `active_tab`, `version`).
4. **Multi-Tenant Isolation Invariant**:
   - Người dùng lạ (Alien Tenant) cố tình gửi lệnh xóa tin nhắn của phiên thuộc người khác sẽ nhận `HTTP 404 Not Found` (`SESSION_NOT_FOUND`), bảo đảm nguyên tắc Zero Data Tampering.
5. **Format Validation Guard Invariant**:
   - Định danh `id` không đúng chuẩn UUIDv4 bị chặn tại tầng schema validation với mã `HTTP 422 Unprocessable Content`.

---

## 3. Đặc Tả Giao Diện API

### 3.1. Endpoint Signature
- **Method**: `DELETE`
- **Route**: `/api/v1/sessions/{id}/messages`
- **Path Parameter**:
  - `id`: UUID (Mã định danh phiên nghiên cứu)
- **Headers**:
  - `Authorization`: `Bearer <token>` (hoặc session cookie)
- **Status Code Thành Công**: `HTTP 204 No Content` (Empty Body)

### 3.2. Response Schema
- **Success (`204 No Content`)**: Thân phản hồi rỗng (`content-length: 0`).
- **Error (`404 Not Found`)**:
  ```json
  {
    "detail": {
      "code": "SESSION_NOT_FOUND",
      "message": "Phiên nghiên cứu không tồn tại hoặc bạn không có quyền truy cập.",
      "action": "Verify session ID."
    }
  }
  ```

---

## 4. Ma Trận Kịch Bản Kiểm Thử Runner (`delete_session_messages.py`)

| STT | Kịch Bản Kiểm Thử | Hành Động & Tham Số | HTTP Kỳ Vọng | Tiêu Chí Đánh Giá Thành Công |
|:---:|:---|:---|:---:|:---|
| **01** | **Active History Purge & State Transition** | Gửi DELETE trên phiên có 3 tin nhắn | `204 No Content` | HTTP 204, gọi GET kiểm tra `data: []`, `total: 0` |
| **02** | **Idempotency Verification (Consecutive Call)** | Gửi DELETE lần 2 trên phiên đã rỗng | `204 No Content` | Tiếp tục trả về 204 No Content, không lỗi |
| **03** | **Parent Session Preservation Guard** | Gọi `GET /api/v1/sessions/{id}` sau khi xóa | `200 OK` | Phiên cha nguyên vẹn (`title`, `active_tab`, `viewport`) |
| **04** | **Multi-Tenant Isolation Guard** | Tenant lạ gửi DELETE với `X-User-Id` khác | `404 Not Found` | `SESSION_NOT_FOUND`, tin nhắn người dùng gốc không bị xóa |
| **05** | **Non-Existent Session Guard** | Gửi DELETE với random UUID | `404 Not Found` | `SESSION_NOT_FOUND` |
| **06** | **UUID Format Validation Guard** | Gửi DELETE với `id="invalid-uuid-format"` | `422 Unprocessable` | `VALIDATION_ERROR` từ chối trước khi truy cập DB |

---

## 5. Dọn Dẹp Khép Kín (Hermetic Teardown)
Mọi phiên nghiên cứu và tài liệu thử nghiệm được dọn dẹp sạch sẽ qua các endpoint REST tiêu chuẩn (`DELETE /api/v1/sessions/{id}` và `DELETE /api/v1/documents/{id}`) theo nguyên tắc Zero Retention.
