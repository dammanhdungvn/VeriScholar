# Hướng Dẫn Hệ Thống Logging & Observability (Structlog + Pure ASGI)

Tài liệu này cung cấp đặc tả kiến trúc và hướng dẫn vận hành hệ thống **Logging & Distributed Tracing** (Ghi nhật ký và Truy vết phân tán) cho backend `apps/api` của **VeriScholar** theo chuẩn mực production và mã nguồn mở.

---

## 0. BẢNG THUẬT NGỮ GIÁM SÁT VẬN HÀNH CHO KỸ SƯ MỚI (FRESHER GLOSSARY)

| Thuật ngữ | Tên tiếng Anh đầy đủ | Giải thích trực quan cho Fresher |
| :--- | :--- | :--- |
| **Observability** | System Observability | Khả năng quan sát và đo lường trạng thái bên trong của hệ thống phần mềm thông qua các dữ liệu đầu ra như Logs (nhật ký), Metrics (chỉ số đo lường) và Traces (dấu vết cuộc gọi). |
| **ASGI** | Asynchronous Server Gateway Interface | Chuẩn giao tiếp bất đồng bộ giữa máy chủ web Python (như Uvicorn) và ứng dụng web (FastAPI), cho phép xử lý hàng nghìn kết nối đồng thời mà không bị nghẽn. |
| **Pure ASGI Middleware** | Pure ASGI Middleware (Outermost Layer) | Lớp phần mềm trung gian bọc ngoài cùng ứng dụng ở mức độ giao thức thuần túy; không dùng bộ đệm giữ dữ liệu trong RAM giúp ngăn ngừa tràn bộ nhớ (Memory Leak) khi truyền luồng dữ liệu dài. |
| **TTFB** | Time-To-First-Byte | Thời gian phản hồi byte đầu tiên: Khoảng thời gian từ lúc client gửi request cho đến khoảnh khắc mili-giây đầu tiên máy chủ bắt đầu gửi mẩu dữ liệu đầu tiên về. |
| **PII Redaction** | Personally Identifiable Information Sanitization | Cơ chế tự động phát hiện và che giấu thông tin nhạy cảm (mật khẩu, mã khóa bí mật API keys, JWT Token) thành chuỗi `***REDACTED***` để bảo mật an toàn thông tin, không cho lộ ra file log. |
| **Client Disconnect (HTTP 499)** | Client Closed Request (HTTP 499 Status) | Mã trạng thái ghi nhận khi người dùng chủ động đóng trình duyệt hoặc hủy thao tác giữa chừng trong lúc server đang tính toán xử lý; server sẽ lập tức dừng công việc để tiết kiệm tài nguyên. |
| **Error Envelope** | Standardized Error Envelope | Bao thư lỗi chuẩn hóa: Mọi thông báo lỗi trả về cho người dùng đều có chung một cấu trúc JSON nhất quán (`success: false`, `error: { code, message, details }`), giúp lập trình viên frontend dễ dàng xử lý giao diện hiển thị. |
| **Contextvars** | Python Context Variables | Biến ngữ cảnh an toàn trong xử lý bất đồng bộ (asyncio); giúp mang mã định danh `X-Request-ID` xuyên suốt qua tất cả các hàm mà không cần phải truyền thủ công qua tham số. |

---

## 1. TỔNG QUAN KIẾN TRÚC LOGGING

Hệ thống Logging của VeriScholar được xây dựng trên 4 trụ cột cốt lõi:
1. **Zero Memory Leak & Non-Buffering Streaming (Chống tràn RAM & không giữ đệm dòng chảy):** Sử dụng `PureASGITracingMiddleware` hoạt động tại tầng ASGI thuần túy (outermost middleware - lớp bọc ngoài cùng), không kế thừa `BaseHTTPMiddleware` nhằm tránh lỗi tiêu hao RAM và nghẽn luồng Server-Sent Events (SSE - dòng dữ liệu một chiều thời gian thực).
2. **Chính xác TTFB (Time-To-First-Byte - Thời gian phản hồi byte đầu tiên):** Bắt trực tiếp sự kiện `http.response.start` để đo lường chính xác mili-giây đầu tiên khi server phản hồi chunk dữ liệu cho client.
3. **Bảo vệ Dữ liệu Nhạy cảm (PII & Secret Sanitization):** Tự động bóc tách và che giấu (`***REDACTED***`) các token bí mật (Bearer JWT, OpenAI `sk-proj`, Google Gemini `AIzaSy`, GitHub `ghp`, mật khẩu người dùng).
4. **Chuẩn hóa Error Envelope (Bao thư thông điệp lỗi nhất quán):** Mọi ngoại lệ (`HTTPException`, `RequestValidationError`, `Exception`) đều được định dạng về schema JSON nhất quán `ErrorResponse`.

```text
HTTP Request (Client gửi yêu cầu)
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ PureASGITracingMiddleware (Lớp bọc ASGI ngoài cùng)   │
│  - Sinh hoặc kế thừa X-Request-ID                      │
│  - Bind request_id vào structlog.contextvars          │
│  - Ghi nhận mốc thời gian bắt đầu (start_time)         │
└────────────────────────────────────────────────────────┘
      │
      ├─► FastAPI Router / Business Logic (Xử lý nghiệp vụ tại apps/api)
      │      └─► structlog.get_logger(...) [Nhật ký có cấu trúc JSON]
      │
      ├─► http.response.start ──► Tính ttfb_ms & Gắn tiêu đề X-Request-ID Header
      ├─► http.response.body  ──► Stream SSE từng mẩu hoặc JSON Payload
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ finally: log_type="access" (Nhật ký truy cập hoàn tất) │
│  - status_code, ttfb_ms, total_duration_ms            │
│  - client_aborted=True (HTTP 499 khi client ngắt mạng)│
└────────────────────────────────────────────────────────┘
```

---

## 2. CẤU TRÚC MÃ NGUỒN

| Thành phần | Đường dẫn | Trách nhiệm chính trong hệ thống |
| :--- | :--- | :--- |
| **Settings** *(Cấu hình)* | `apps/api/src/api/core/config.py` | Quản trị biến môi trường qua Pydantic Settings (`ENVIRONMENT`, `LOG_LEVEL`, `LOG_FORMAT`, `RELOAD_DIRS`) |
| **Core Logger** *(Bộ ghi nhật ký cốt lõi)* | `apps/api/src/api/core/logging.py` | Cấu hình structlog, bộ xử lý ProcessorFormatter, bộ lọc che giấu PII masking, vô hiệu hóa log mặc định `uvicorn.access` |
| **Tracing** *(Bộ truy vết luồng)* | `apps/api/src/api/middleware/tracing.py` | Middleware đo lường TTFB, tổng thời gian xử lý (Total Duration), bẫy ngắt kết nối HTTP 499, quản trị contextvars |
| **Error Schema** *(Lược đồ thông điệp lỗi)* | `apps/api/src/api/schemas/error.py` | Lớp dữ liệu Pydantic model định nghĩa cấu trúc chuẩn cho `ErrorDetail` và `ErrorResponse` |
| **Lifecycle & App** *(Vòng đời ứng dụng)* | `apps/api/src/api/__init__.py` | Kích hoạt hệ thống logging ngay khi nạp module, quản lý sự kiện khởi động/tắt máy (lifespan), bộ bẫy ngoại lệ toàn cục |
| **Test Suite** *(Bộ kiểm thử tự động)* | `apps/api/tests/test_logging.py` | 8 bài kiểm thử tự động bao phủ 100% các kịch bản kiểm tra an toàn |

---

## 3. CÁC ĐỊNH DẠNG LOG & CHUYỂN ĐỔI MÔI TRƯỜNG

### 3.1. Chế độ Phát triển Cục bộ (`LOG_FORMAT=console`)
- Hiển thị trực quan qua thư viện `rich` với màu sắc phân biệt từng mức độ nghiêm trọng (Log Level):
  - `[info]`: Màu xanh dương / Cyan (Thông tin hoạt động bình thường)
  - `[warning]`: Màu vàng (Cảnh báo cần lưu ý)
  - `[error]`: Màu đỏ kèm dấu vết mã nguồn (Traceback chi tiết)

### 3.2. Chế độ Môi trường Sản xuất (`LOG_FORMAT=json` hoặc `ENVIRONMENT=production`)
- Xuất log theo định dạng **JSON 1 dòng (Single-line Structured JSON)**, tương thích hoàn toàn với Datadog, Grafana Loki, AWS CloudWatch, Google Cloud Logging:
```json
{
  "log_type": "access",
  "status_code": 200,
  "ttfb_ms": 1.25,
  "total_duration_ms": 1.48,
  "client_aborted": false,
  "request_id": "9c1fa8fe-1a24-41d6-b76d-68b2cf47aaaf",
  "method": "GET",
  "path": "/health",
  "event": "http_request_finished",
  "level": "info",
  "logger": "api.access",
  "timestamp": "2026-09-09T07:28:38.475677Z"
}
```

---

## 4. QUY TẮC PHÂN LOẠI LOG TYPE

Để dễ dàng lọc log trên các hệ thống giám sát tập trung, hệ thống phân định rõ 4 trường `log_type`:

| `log_type` | Phạm vi sử dụng | Nơi phát sinh trong hệ thống |
| :--- | :--- | :--- |
| `lifecycle` | Sự kiện vòng đời khởi động (`application_startup`), tắt máy (`application_shutdown`), nạp module | `api.lifecycle` |
| `access` | Nhật ký truy cập HTTP hoàn tất của từng request (chứa thời gian phản hồi `ttfb_ms`, `total_duration_ms`) | `api.access` (Middleware) |
| `application` | Log xử lý nghiệp vụ thông thường (Logic kinh doanh, Bóc tách Ingestion, Truy xuất Retrieval) | `api.*` |
| `audit` | Log kiểm tra bảo mật, sự kiện đăng nhập, cấp phát phân quyền, giao dịch nhạy cảm | `audit` |

---

## 5. HƯỚNG DẪN KIỂM THỬ TỪNG BƯỚC

### Bước 1: Chạy Bộ Kiểm Thử Tự Động
```bash
uv run pytest -s -v apps/api/tests/test_logging.py
```
*Kỳ vọng:* 8/8 bài test đều đạt (passed) trong thời gian dưới 1 giây (< 1 giây).

### Bước 2: Khởi chạy Máy Chủ API
```bash
uv run --package api api
```

### Bước 3: Gửi Request Kiểm Thử Trực Tiếp
```bash
# 1. Kiểm tra sức khỏe hệ thống (Health check) & Tự sinh mã vết X-Request-ID
curl -i http://127.0.0.1:8000/health

# 2. Truyền nối mã vết X-Request-ID từ Client gửi sang
curl -i -H "X-Request-ID: test-custom-trace-001" http://127.0.0.1:8000/health

# 3. Stream Server-Sent Events (SSE) & Đo lường chỉ số TTFB
curl -N http://127.0.0.1:8000/events

# 4. Kiểm thử Bẫy Lỗi Đường dẫn không tồn tại (HTTP 404)
curl -i http://127.0.0.1:8000/non-existent-route
```
