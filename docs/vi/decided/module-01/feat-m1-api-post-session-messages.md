# Kế Hoạch Thiết Kế Kỹ Thuật: POST /api/v1/sessions/{id}/messages

> **Mã tính năng**: `FEAT-M1-API-POST-SESSION-MESSAGES`  
> **Endpoint**: `POST /api/v1/sessions/{id}/messages`  
> **STT API PRD**: `#52. Gửi câu hỏi & Stream SSE (Cross-Document Namespacing)`  
> **Trạng thái**: Decided / In-Progress  
> **Tiêu chuẩn áp dụng**: RFC 8895 (Server-Sent Events), Google AIP-136 / AIP-158, Socratic Presupposition Refutation, Cross-Document Namespacing, Multi-Tenancy & Zero Data Leakage.

---

## 1. Bối Cảnh & Mục Tiêu Nghiệp Vụ

Trong kiến trúc VeriScholar, endpoint `POST /api/v1/sessions/{id}/messages` đóng vai trò là "trái tim đối thoại học thuật" của Module 1. Endpoint cho phép người dùng đặt câu hỏi so sánh, tổng hợp hoặc đào sâu trên tập hợp 1 đến 5 bài báo khoa học đã được nạp vào phiên nghiên cứu (`ResearchSession`).

Khác với các chatbot thông thường, VeriScholar giải quyết bài toán chống ảo giác học thuật (Anti-Hallucination) và bẫy tiền đề sai (False Presupposition) thông qua 4 cơ chế cốt lõi:
1. **Server-Sent Events (SSE) Streaming**: Truyền phát dòng token, khối suy luận (Reasoning / AT-CoT), trích dẫn bằng chứng (Citations kèm bounding boxes) theo thời gian thực với độ trễ phản hồi ban đầu (TTFT) cực thấp.
2. **Cross-Document Context Namespacing**: Đóng gói tường minh các đoạn ngữ cảnh bằng thẻ XML `<document id="...">` và cắt tỉa bảng biểu thông minh (**Elastic Table Budgeting**) để bảo toàn context window.
3. **AT-CoT Ambiguity Clarification**: Khi câu hỏi người dùng có độ mơ hồ cao (ví dụ: *"Tôi không có kiến thức gì, hãy lên lộ trình học từ con số 0"*), hệ thống tự động phát hiện và phát sự kiện `interactive_options` (chứa 3 Personas và 3 câu hỏi Diagnostic Quiz) thay vì sinh câu trả lời chung chung.
4. **Socratic Presupposition Refutation & Metric Guards**: Bác bỏ thẳng thắn các giả định sai (ví dụ gán ghép RNN vào Transformer) và đính chính các chỉ số hiệu năng bị bóp méo (ví dụ BLEU 45.0 vs thực tế 28.4).

---

## 2. 5 Bất Biến Nghiệp Vụ Cốt Lõi (Core Invariants)

1. **RFC 8895 Server-Sent Events (SSE) Contract**:
   - Giao thức truyền thông bắt buộc `Content-Type: text/event-stream`.
   - Chuỗi sự kiện có cấu trúc chuẩn hóa:
     - `event: start` -> Khởi tạo phiên giao dịch turn với `turn_id`, `message_id`, `created_at`.
     - `event: reasoning` -> Truyền phát dòng suy luận nội tâm (Thinking/CoT) khi `enable_thinking=true`.
     - `event: citations` -> Danh sách trích dẫn bài báo khoa học kèm số trang và tọa độ Bounding Box `[ymin, xmin, ymax, xmax, page]`.
     - `event: token` -> Từng token văn bản câu trả lời trả về thời gian thực cho UI rendering.
     - `event: interactive_options` -> Danh sách lựa chọn phân tầng đối tượng học và câu hỏi trắc nghiệm khi phát hiện truy vấn mơ hồ.
     - `event: done` -> Kết thúc luồng kèm thống kê `total_tokens` và `finish_reason` (`stop`, `abstention`).
     - `event: error` -> Báo lỗi khi phiên bị khóa hoặc lỗi nội bộ.
2. **Cross-Document Namespacing & Elastic Table Budgeting**:
   - Khi `scope="multi_paper"`, ngữ cảnh được định danh nguồn rõ ràng qua cấu trúc XML; khi `scope="single_paper"`, hệ thống chỉ truy xuất trong phạm vi `focused_document_id`.
   - Cắt tỉa các bảng biểu phức tạp trong context prompt để đảm bảo TTFT < 1s.
3. **Socratic False Presupposition Refutation**:
   - Khi người dùng đưa ra câu hỏi gài bẫy tiền đề sai (Adversarial False Presupposition), hệ thống phải phản biện học thuật, chỉ ra sai lầm của tiền đề và điều hướng tới bằng chứng xác thực trong tài liệu (ví dụ: mục 3.5 Positional Encoding thay vì RNN).
4. **Anti-Hallucination Scope & Experimental Metric Trap Mitigation**:
   - Tự từ chối lịch sự (`finish_reason="abstention"`) khi câu hỏi vượt quá miền tri thức của bài báo (Out-of-Domain), tránh ngụy tạo số liệu trên các benchmark hiện đại (GSM8K, GPT-4).
   - Đính chính chuẩn xác các số liệu thực nghiệm thực tế tại bảng kết quả (Table 2 BLEU score).
5. **Stream Resumption (RFC 8895 Last-Event-ID) & Disconnect Guard**:
   - Hỗ trợ khôi phục luồng stream bị đứt quãng thông qua header `Last-Event-ID`, bỏ qua các sự kiện đã gửi.
   - Khi người dùng ngắt kết nối giữa chừng, server dừng ngay coroutine và ghi log mã `HTTP 499 (Client Closed Request)`.

---

## 3. Đặc Tả Giao Diện API

### 3.1. Endpoint Signature
- **Method**: `POST`
- **Route**: `/api/v1/sessions/{id}/messages`
- **Headers**:
  - `Content-Type: application/json`
  - `Accept: text/event-stream`
  - `Last-Event-ID: <string>` *(Tùy chọn, dùng khi nối lại stream)*
  - `X-User-ID: <user_id>` *(hoặc JWT Bearer)*
- **Status Code Thành Công**: `HTTP 200 OK` (`text/event-stream`)

### 3.2. Request Payload Schema
```json
{
  "question": "So sánh hàm kích hoạt giữa Paper gốc và Paper Vaswani et al.?",
  "stream": true,
  "scope": "multi_paper",
  "focused_document_id": null,
  "enable_thinking": false,
  "interactive_response": null
}
```

### 3.3. Dòng Sự Kiện SSE Mẫu
```text
event: start
data: {"turn_id": "9f1a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c", "message_id": "msg_9f1a2b3c", "created_at": "2026-09-18T15:40:00.000Z"}

event: citations
data: {"citations": [{"citation_id": "cit_1", "document_id": "c7a2e8c5-9231-419b-a0eb-4a1796d8e05c", "document_title": "Attention Is All You Need", "page_number": 5, "bounding_boxes": [[0.1, 0.2, 0.8, 0.28, 5]]}]}

event: token
data: {"token": "Trong bài báo của Vaswani et al., hàm kích hoạt được sử dụng là ReLU..."}

event: done
data: {"turn_id": "9f1a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c", "message_id": "msg_9f1a2b3c", "total_tokens": 128, "finish_reason": "stop"}
```

---

## 4. Ma Trận Kịch Bản Kiểm Thử Runner (`post_sessions_chat.py` / `post_session_messages.py`)

| STT | Kịch Bản Kiểm Thử | Đầu Vào Thử Nghiệm | Sự Kiện SSE Kỳ Vọng | Tiêu Chí Đánh Giá Thành Công |
|:---:|:---|:---|:---:|:---|
| **01** | **Ambiguous Query Clarification** | *"Lên roadmap học paper từ con số 0"* | `event: interactive_options` | 3 Personas & 3 Diagnostic Micro-Quiz questions |
| **02** | **Tailored Roadmap Path** | Chọn Nhóm B (đã biết ML, chưa rõ Attention) | `event: token`, `event: done` | 5 giai đoạn chi tiết neo vào Figure 1 và Table 1 |
| **03** | **Mathematical Complexity Grounding** | So sánh độ phức tạp Table 1 khi $n < d$ | `event: citations`, `event: token` | Công thức $\mathcal{O}(n^2 \cdot d)$ vs $\mathcal{O}(n \cdot d^2)$ neo Trang 6 |
| **04** | **Socratic Presupposition Refutation** | Bẫy: tác giả đặt RNN ở tầng encoder nào? | `event: token` | Bác bỏ tiền đề sai, điều hướng sang Positional Encoding Mục 3.5 Trang 6 |
| **05** | **Out-of-Domain Distractor Mitigation** | Hỏi điểm GSM8K so với GPT-4 | `event: token`, `finish_reason` | Từ chối ảo giác, viện dẫn mốc thời gian công bố 2017 |
| **06** | **Experimental Metric Trap Mitigation** | Bẫy điểm BLEU 45.0 trên EN-DE | `event: token`, `event: citations` | Bác bỏ 45.0, xác nhận 28.4 BLEU tại Table 2 Trang 8 |
| **07** | **Chat History Verification (#53)** | `GET /api/v1/sessions/{id}/messages` | `200 OK` Paginated | Trả về tối thiểu 6 lượt trao đổi đầy đủ Q&A contract |
| **08** | **Stream Resumption (RFC 8895)** | Header `Last-Event-ID: 2` | `event: token`, `done` | Bỏ qua các sự kiện <= 2 (start, reasoning) |
| **09** | **Idempotent Clear History (#54)** | `DELETE /api/v1/sessions/{id}/messages` | `204 No Content` | Làm sạch toàn bộ tin nhắn, kiểm tra GET trả về 0 |
| **10** | **Archived Session Guard** | Gửi tin nhắn vào phiên đã Archive | `event: error` | Nhận mã lỗi `SESSION_ARCHIVED` |

---

## 5. Dọn Dẹp Khép Kín (Hermetic Teardown)
Toàn bộ tài liệu PDF mẫu và phiên nghiên cứu phục vụ autotest đều được thu hồi và xóa sạch qua `DELETE /api/v1/sessions/{id}` và `DELETE /api/v1/documents/{id}`, bảo đảm nguyên tắc Zero Retention.
