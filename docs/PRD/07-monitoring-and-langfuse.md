# MODULE 07: QUẢN LÝ MÔI TRƯỜNG (.ENV), LANGFUSE TRACING & HỆ THỐNG MONITORING 3 TẦNG
# (FILE 07: ENVIRONMENTS, LANGFUSE OBSERVABILITY, ERROR ALERTING & SYSTEM MONITORING)

---

## 1. Mục Tiêu Module
Thiết lập hệ thống quản lý môi trường và giám sát vận hành (Monitoring & Error Tracking) gọn nhẹ, thực chiến cho dự án cá nhân trên cả 2 môi trường **`development`** và **`production`**:
* Bất kỳ câu query hay thao tác nào bị lỗi đều có **1 mã `trace_id` duy nhất** hiển thị ngay trên màn hình để tra cứu trong 3 giây.
* Theo dõi chi tiết từng bước thực thi AI trên **Langfuse** (`verischolar-dev` & `verischolar-prod`).
* Tự động bắt lỗi toàn cục và bắn cảnh báo tức thì qua **Sentry + Webhook Telegram/Discord** khi chạy bản `production`.
* Giám sát trực tiếp sức khỏe Database, ổ cứng PDF, kết nối AI/E2B và hiệu năng API qua `/health/ready` và `/api/v1/system/status`.

---

## 2. Chuẩn Hóa File Môi Trường (`.env` — Chỉ Giữ `development` và `production`)

* **Xóa bỏ hoàn toàn** các môi trường dư thừa không dùng tới: `uat`, `staging`, `sit`, `enterprise` (xóa `apps/api/.env.uat`, `deploy/.env.enterprise.example` và rút gọn kiểu `ENVIRONMENT` trong `apps/api/src/api/core/config.py`).
* **Chỉ sử dụng đúng 2 môi trường:**

| Thuộc tính cấu hình | Môi trường `development` (`.env.development`) | Môi trường `production` (`.env.production`) |
| :--- | :--- | :--- |
| **`ENVIRONMENT`** | `development` | `production` |
| **`LANGFUSE_ENVIRONMENT`** | `verischolar-dev` | `verischolar-prod` |
| **`LOG_LEVEL` / `LOG_FORMAT`** | `DEBUG` / `console` (Màu sắc trực quan + ghi file JSON) | `INFO` / `json` (Ghi đầy đủ access & error dạng JSON 1 dòng) |
| **`LANGFUSE_MASK_INPUT_OUTPUT`** | `false` (Xem toàn bộ nội dung Input/Output từng Node) | `false` cho nội dung học thuật để debug lỗi (chỉ che mật khẩu, JWT Token, API Keys qua `scrub_sensitive_text`) |
| **Cảnh báo lỗi tức thì (Sentry / Webhook)** | Tắt (hoặc chỉ ghi console/log) | **Bật** (Tự động bắn cảnh báo khi có lỗi 500 hoặc sập dịch vụ) |

---

## 3. Mã Truy Vết Đồng Nhất (`trace_id` = `request_id`) Xuyên Suốt Toàn Hệ Thống

Mỗi khi người dùng gửi một câu hỏi (Query) hoặc thực hiện một thao tác API:
1. **Sinh mã duy nhất tại Middleware (`PureASGITracingMiddleware`):**
   * Tạo một mã định danh duy nhất `trace_id` (đồng nhất với header `X-Request-ID`).
   * Gắn `trace_id` này vào cả 3 nơi:
     * **Log hệ thống (`structlog`)**: Mọi dòng log trong `api-audit.log` và `api-error.log` đều mang trường `"trace_id"` và `"request_id"`.
     * **Langfuse Trace**: Gắn làm ID truy vết của câu query đó, đồng thời gắn kèm **`session_id`** (nếu ở phiên đọc) hoặc **`draft_id`** (nếu ở phiên viết bài).
     * **HTTP Response & Bao thư lỗi (`ErrorResponse`)**: Trả về cho Frontend trong `meta.trace_id` và header `X-Request-ID`.
2. **Hiển thị trực tiếp trên Giao diện Web khi có lỗi:**
   * Khi bất kỳ yêu cầu nào gặp lỗi (hoặc khi giao diện bị crash vào React Error Boundary), thông báo lỗi trên màn hình luôn hiển thị kèm:
     > *"⚠️ Đã xảy ra lỗi khi xử lý yêu cầu — Mã tra cứu: `tr_9c1fa8fe` [📋 Sao chép]"*
   * Người phát triển chỉ cần copy mã này dán vào ô tìm kiếm của **Langfuse**, **Sentry** hoặc tìm trong `api-error.log` là thấy ngay lập tức câu query gây lỗi và dòng code bị gãy.

---

## 4. Hệ Thống Monitoring 3 Tầng Thực Chiến

### Tầng 1: Giám sát Luồng AI & Chấm điểm Chất lượng trên Langfuse (`ai_tracing_service.py`)
1. **Tracing từng bước thực thi (Nodes/Spans):**
   * Ghi nhận 5 loại Observation chuẩn trên Langfuse:
     * `trace`: Toàn bộ 1 lượt hỏi đáp RAG, 1 lượt nạp Exa, hoặc 1 lượt chạy LangGraph Agent.
     * `retriever`: Bước tìm kiếm `pgvector` và xếp hạng lại qua Cohere Reranker (lưu danh sách `chunk_ids` và điểm số).
     * `tool`: Bước gọi Exa AI, truy vấn `query_library_graph_rag`, sửa file `edit_file`, hoặc biên dịch trên `compile_latex_e2b`.
     * `guardrail`: Bước kiểm tra trạng thái tải PDF Tầng 2 hoặc lọc an toàn.
     * `generation`: Bước gọi LLM (ghi rõ tên model, `prompt_tokens`, `completion_tokens`, chi phí USD và thời gian phản hồi).
2. **Quản lý theo Phiên (`session_id`):**
   * Gom toàn bộ các câu query thuộc cùng một phiên học hoặc một bản thảo vào tab **Sessions** trên Langfuse để xem trọn vẹn mạch hội thoại và tổng chi phí của phiên đó.
3. **Chấm điểm Chất lượng (`Scores` — 3 chỉ số cốt lõi):**
   * `bbox_grounded` (`1` hoặc `0`): Câu trả lời RAG có trích xuất được tọa độ Bounding Box hợp lệ hay không.
   * `e2b_compile_attempts` (`1`, `2`, `3` hoặc `0` nếu thất bại): Số vòng lặp Agent cần để biên dịch LaTeX thành công trên E2B Sandbox.
   * `user_feedback` (`1` = 👍, `0` = 👎): Dưới mỗi câu trả lời của AI trên giao diện web có 2 nút đánh giá nhanh 👍 / 👎; khi người dùng bấm vào sẽ gọi API `POST /api/v1/sessions/{session_id}/messages/{message_id}/feedback` để gửi điểm số trực tiếp về đúng `trace_id` đó trên Langfuse.

---

### Tầng 2: Quản lý Lỗi Toàn cục & Cảnh báo Tức thì (Sentry + Webhook Telegram/Discord + File Log)
1. **Ghi file Log xoay vòng trên đĩa (`storage/logs/api-error.log`):**
   * Mọi lỗi từ mức `WARNING` và `ERROR` trở lên (bao gồm cả lỗi ngoài luồng AI như lỗi Database, lỗi Upload PDF, lỗi Auth, lỗi 500) đều được ghi tự động vào `storage/logs/api-error.log` kèm đầy đủ Stack Trace, `trace_id`, `user_id`, `method`, `path`.
2. **Tích hợp Sentry SDK (`SENTRY_DSN`):**
   * Tự động bắt mọi ngoại lệ chưa xử lý (`Unhandled Exception`) ở cả Backend FastAPI và Frontend React, gom nhóm theo loại lỗi và gắn thẻ `environment` (`verischolar-dev` / `verischolar-prod`) cùng `trace_id`.
3. **Cảnh báo tức thì qua Webhook Telegram / Discord (`ALERT_WEBHOOK_URL`):**
   * Khi chạy bản `production`, nếu xảy ra lỗi `500 Internal Server Error` hoặc lỗi sập kết nối tới Database / OpenAI / E2B Sandbox, hệ thống bắn ngay một tin nhắn cảnh báo ngắn gọn về kênh Telegram/Discord cá nhân:
     * Nội dung cảnh báo gồm: `Môi trường`, `Mã trace_id`, `Đường dẫn API`, `Loại lỗi & Thông điệp lỗi`, và `Thời gian xảy ra`.

---

### Tầng 3: Giám sát Sức khỏe Hệ thống & Hiệu năng API Tích hợp sẵn (`/health/ready` & `/api/v1/system/status`)
Không cần cài đặt thêm cụm Docker Prometheus/Grafana nặng nề, hệ thống cung cấp trực tiếp 2 điểm kiểm tra giám sát:
1. **Kiểm tra Sức khỏe Sâu (`GET /health/ready`):**
   * Kiểm tra và trả về trạng thái sống/chết + độ trễ (`latency_ms`) của:
     * **Database** (PostgreSQL / SQLite fallback).
     * **Ổ cứng lưu trữ (`storage/blobs`)**: Kiểm tra quyền đọc/ghi và dung lượng MB đang sử dụng.
     * **Trạng thái cấu hình các dịch vụ ngoài**: OpenAI API, Exa AI, E2B Sandbox, Langfuse, Sentry.
   * Dùng để gắn vào **UptimeRobot / Uptime Kuma** ping tự động mỗi 1 phút (báo động ngay nếu sập server).
2. **Bảng Thống kê Hiệu năng & Lỗi gần nhất (`GET /api/v1/system/status`):**
   * Tổng hợp trực tiếp từ `PureASGITracingMiddleware`:
     * Thời gian máy chủ đã hoạt động (`uptime_seconds`).
     * Tổng số request, tỷ lệ thành công (`2xx`) và tỷ lệ lỗi (`4xx`, `5xx`).
     * Thời gian phản hồi trung bình (`avg_duration_ms` và `avg_ttfb_ms`).
     * Danh sách **20 lỗi gần nhất** (kèm `timestamp`, `trace_id`, `path`, `status_code`, `error_message`) để người quản trị mở lên là nắm bắt được ngay sức khỏe toàn hệ thống.
