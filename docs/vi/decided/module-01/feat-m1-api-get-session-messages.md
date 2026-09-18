# Kế Hoạch Thiết Kế Kỹ Thuật: GET /api/v1/sessions/{id}/messages

> **Mã tính năng**: `FEAT-M1-API-GET-SESSION-MESSAGES`  
> **Endpoint**: `GET /api/v1/sessions/{id}/messages`  
> **STT API PRD**: `#53. Lấy lịch sử hội thoại của phiên (phân trang)`  
> **Trạng thái**: Decided / In-Progress  
> **Tiêu chuẩn áp dụng**: RFC 8288 (Web Linking), RFC 9110 (HTTP Semantics), Google AIP-158 (Pagination), Chronological Sorting (`created_at ASC`), Multi-Tenancy & Zero Data Leakage.

---

## 1. Bối Cảnh & Mục Tiêu Nghiệp Vụ

Trong ứng dụng nghiên cứu học thuật VeriScholar, mỗi phiên nghiên cứu (`ResearchSession`) lưu trữ lịch sử các câu hỏi của nhà nghiên cứu và câu trả lời kèm trích dẫn không gian của mô hình AI. Khi người dùng tải lại trang trình duyệt hoặc chuyển đổi giữa các phiên nghiên cứu trên Sidebar, giao diện cần khôi phục lại toàn bộ dòng hội thoại (Chat History) theo đúng trật tự thời gian diễn ra.

Endpoint `GET /api/v1/sessions/{id}/messages` đảm nhận nhiệm vụ:
1. **Phục Hồi Dòng Thời Gian Trò Chuyện (Chronological Stream Restoration)**: Trả về danh sách các lượt hỏi đáp (`SessionTurnModel`) được sắp xếp tăng dần theo thời gian tạo (`created_at ASC`), đảm bảo trải nghiệm đọc liền mạch từ câu hỏi đầu tiên đến câu hỏi mới nhất.
2. **Tuân Thủ RFC 8288 & AIP-158 Collection Envelope**: Đóng gói danh sách với đầy đủ siêu dữ liệu phân trang (`meta`: `total`, `page`, `per_page`, `total_pages`) và tập hợp các liên kết điều hướng chuẩn (`links`: `first`, `prev`, `self`, `next`, `last`).
3. **Bảo Toàn Hợp Đồng Trích Dẫn Không Gian (Spatial Citation Contract)**: Mỗi lượt trao đổi lưu trữ nguyên vẹn thông tin trích dẫn bài báo (`citations`), bao gồm `citation_id`, `document_id`, `document_title`, `page_number` và mảng tọa độ `bounding_boxes` tỷ lệ chuẩn hóa `[ymin, xmin, ymax, xmax, page]`.
4. **Bảo Mật Đa Thuê Tuyệt Đối (Multi-Tenant Shielding)**: Kiểm tra quyền sở hữu phiên nghiên cứu qua `user_id`. Mọi truy vấn từ người dùng khác vào phiên riêng tư đều bị từ chối với `HTTP 404 Not Found` (`SESSION_NOT_FOUND`).

---

## 2. 5 Bất Biến Nghiệp Vụ Cốt Lõi (Core Invariants)

1. **Chronological Sorting Invariant**:
   - Dòng lịch sử hội thoại phải luôn được sắp xếp theo `created_at ASC`. Khác với danh sách phiên (`GET /api/v1/sessions` sắp xếp `updated_at DESC`), danh sách tin nhắn bắt buộc phải theo trình tự thời gian tăng dần để người dùng đọc hiểu đúng ngữ cảnh nhiều lượt (Multi-turn Context).
2. **RFC 8288 Web Linking & Pagination Invariant**:
   - Trường `links` phải sinh ra đầy đủ các liên kết `first`, `prev`, `self`, `next`, `last` tương ứng với vị trí trang hiện tại và `total_pages`. Khi ở trang 1, `prev` phải là `null`; khi ở trang cuối, `next` phải là `null`.
3. **Turn Schema & Citation Integrity Invariant**:
   - Mỗi bản ghi `SessionTurnItem` phải có cấu trúc hợp đồng đầy đủ: `id`, `session_id`, `question`, `answer`, `citations`, `total_tokens`, `finish_reason`, `created_at`.
   - Nếu lượt trao đổi có trích dẫn, mảng `bounding_boxes` phải tuân thủ chuẩn không gian VeriScholar.
4. **Empty History Graceful Degradation**:
   - Đối với phiên nghiên cứu vừa khởi tạo chưa có lượt trao đổi nào, endpoint trả về `HTTP 200 OK` với mảng rỗng `data: []`, `meta.total: 0`, `meta.total_pages: 0`. Tuyệt đối không trả về 404 hoặc lỗi máy chủ 500.
5. **Tenant Isolation & Parameter Validation Guards**:
   - Người dùng khác (Alien Tenant) cố truy xuất tin nhắn của phiên không thuộc quyền sở hữu của mình sẽ nhận mã `HTTP 404 Not Found` (`SESSION_NOT_FOUND`).
   - Tham số phân trang ngoài biên hợp lệ (`page < 1` hoặc `per_page > 100`) bị chặn tại tầng Pydantic Schema Validation với mã `HTTP 422 Unprocessable Content`.

---

## 3. Đặc Tả Giao Diện API

### 3.1. Endpoint Signature
- **Method**: `GET`
- **Route**: `/api/v1/sessions/{id}/messages`
- **Query Parameters**:
  - `page`: int (mặc định: `1`, tối thiểu: `1`)
  - `per_page`: int (mặc định: `50`, tối thiểu: `1`, tối đa: `100`)
- **Headers**:
  - `Authorization`: `Bearer <token>` (hoặc Cookie session)
- **Status Code Thành Công**: `HTTP 200 OK`

### 3.2. Response Schema (`200 OK` - Paginated Collection Envelope)
```json
{
  "success": true,
  "data": [
    {
      "id": "9f1a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
      "session_id": "8b5a1f2e-4a6c-4c7b-9e1d-8f3b2a5c6d7e",
      "question": "So sánh hàm kích hoạt giữa Paper gốc và Paper Vaswani et al.?",
      "answer": "Trong bài báo của Vaswani et al., hàm kích hoạt được sử dụng là ReLU...",
      "citations": [
        {
          "citation_id": "cit_1",
          "document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c",
          "document_title": "Attention Is All You Need",
          "page_number": 5,
          "bounding_boxes": [[0.1, 0.2, 0.8, 0.28, 5]]
        }
      ],
      "total_tokens": 128,
      "finish_reason": "stop",
      "created_at": "2026-09-18T15:40:00.000000Z"
    }
  ],
  "meta": {
    "total": 1,
    "page": 1,
    "per_page": 50,
    "total_pages": 1,
    "request_id": "req_55b5aa93_3a91",
    "timestamp": "2026-09-18T15:40:05.000000Z"
  },
  "links": {
    "first": "/api/v1/sessions/8b5a1f2e-4a6c-4c7b-9e1d-8f3b2a5c6d7e/messages?page=1&per_page=50",
    "prev": null,
    "self": "/api/v1/sessions/8b5a1f2e-4a6c-4c7b-9e1d-8f3b2a5c6d7e/messages?page=1&per_page=50",
    "next": null,
    "last": "/api/v1/sessions/8b5a1f2e-4a6c-4c7b-9e1d-8f3b2a5c6d7e/messages?page=1&per_page=50"
  }
}
```

---

## 4. Ma Trận Kịch Bản Kiểm Thử Runner (`get_session_messages.py`)

| STT | Kịch Bản Kiểm Thử | Tham Số Thử Nghiệm | Mã HTTP Kỳ Vọng | Tiêu Chí Đánh Giá Thành Công |
|:---:|:---|:---|:---:|:---|
| **01** | **Default Paginated Chronological List** | `page=1`, `per_page=50` | `200 OK` | Sắp xếp `created_at ASC`, trả về đủ meta và links chuẩn |
| **02** | **Strict Page Slicing & Boundary Links** | `per_page=2`, `page=1..2` | `200 OK` | Phân trang chính xác độ dài 2, tập ID không giao nhau, liên kết `next`/`prev` chuẩn |
| **03** | **Turn Schema & Citation Integrity** | Kiểm tra chi tiết 1 turn | `200 OK` | Đầy đủ `question`, `answer`, `citations` (kèm `bounding_boxes` và `page_number`) |
| **04** | **Empty Conversation History Guard** | Phiên mới tạo chưa có tin nhắn | `200 OK` | `data: []`, `total: 0`, `total_pages: 0` |
| **05** | **Multi-Tenant Isolation Guard** | User lạ truy xuất tin nhắn người khác | `404 Not Found` | `SESSION_NOT_FOUND`, không rò rỉ dữ liệu phiên |
| **06** | **Query Parameter Validation Guard** | `page=0`, `per_page=101`, sai UUID | `422 Unprocessable` | `VALIDATION_ERROR` từ chối tham số vi phạm biên |

---

## 5. Dọn Dẹp Khép Kín (Hermetic Teardown)
Mọi phiên nghiên cứu và tài liệu thử nghiệm phục vụ runner đều được dọn sạch hoàn toàn qua `DELETE /api/v1/sessions/{id}` và `DELETE /api/v1/documents/{id}`, bảo đảm nguyên tắc Zero Retention.
