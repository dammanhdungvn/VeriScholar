# Hướng Dẫn Hệ Thống Logging & Observability (Structlog + Pure ASGI)

Tài liệu này cung cấp đặc tả kiến trúc và hướng dẫn vận hành hệ thống **Logging & Distributed Tracing** cho backend `apps/api` của **VeriScholar** theo chuẩn mực production và mã nguồn mở.

---

## 1. TỔNG QUAN KIẾN TRÚC LOGGING

Hệ thống Logging của VeriScholar được xây dựng trên 4 trụ cột cốt lõi:
1. **Zero Memory Leak & Non-Buffering Streaming:** Sử dụng `PureASGITracingMiddleware` hoạt động tại tầng ASGI thuần túy (outermost middleware), không kế thừa `BaseHTTPMiddleware` nhằm tránh lỗi tiêu hao RAM và nghẽn luồng Server-Sent Events (SSE).
2. **Chính xác TTFB (Time-To-First-Byte):** Bắt trực tiếp event `http.response.start` để đo lường chính xác mili-giây đầu tiên khi server phản hồi chunk cho client.
3. **Bảo vệ Dữ liệu Nhạy cảm (PII & Secret Sanitization):** Tự động bóc tách và che giấu (`***REDACTED***`) các token bí mật (Bearer JWT, OpenAI `sk-proj`, Google Gemini `AIzaSy`, GitHub `ghp`, mật khẩu người dùng).
4. **Chuẩn hóa Error Envelope:** Mọi ngoại lệ (`HTTPException`, `RequestValidationError`, `Exception`) đều được định dạng về schema JSON nhất quán `ErrorResponse`.

```text
HTTP Request (Client)
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ PureASGITracingMiddleware (Outermost ASGI Layer)      │
│  - Sinh hoặc kế thừa X-Request-ID                      │
│  - Bind request_id vào structlog.contextvars          │
│  - Ghi nhận start_time                                 │
└────────────────────────────────────────────────────────┘
      │
      ├─► FastAPI Router / Business Logic (apps/api)
      │      └─► structlog.get_logger(...) [Structured Log]
      │
      ├─► http.response.start ──► Tính ttfb_ms & Gắn X-Request-ID Header
      ├─► http.response.body  ──► Stream SSE hoặc JSON Payload
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ finally: log_type="access"                             │
│  - status_code, ttfb_ms, total_duration_ms            │
│  - client_aborted=True (HTTP 499 khi ngắt kết nối)    │
└────────────────────────────────────────────────────────┘
```

---

## 2. CẤU TRÚC MÃ NGUỒN

| File | Đường dẫn | Trách nhiệm chính |
| :--- | :--- | :--- |
| **Settings** | `apps/api/src/api/core/config.py` | Quản trị biến môi trường (`ENVIRONMENT`, `LOG_LEVEL`, `LOG_FORMAT`, `RELOAD_DIRS`) |
| **Core Logger** | `apps/api/src/api/core/logging.py` | Cấu hình structlog, ProcessorFormatter, bộ lọc PII masking, vô hiệu hóa `uvicorn.access` |
| **Tracing** | `apps/api/src/api/middleware/tracing.py` | Middleware đo TTFB, Total Duration, bẫy HTTP 499, contextvars |
| **Error Schema** | `apps/api/src/api/schemas/error.py` | Pydantic model cho `ErrorDetail` và `ErrorResponse` |
| **Lifecycle & App** | `apps/api/src/api/__init__.py` | Setup logging tại module load time, lifespan context manager, exception handlers |
| **Test Suite** | `apps/api/tests/test_logging.py` | 8 bài test tự động bao phủ 100% kịch bản |

---

## 3. CÁC ĐỊNH DẠNG LOG & CHUYỂN ĐỔI MÔI TRƯỜNG

### 3.1. Chế độ Local Development (`LOG_FORMAT=console`)
- Hiển thị trực quan qua thư viện `rich` với màu sắc phân biệt từng log level:
  - `[info]`: Xanh dương / Cyan
  - `[warning]`: Vàng
  - `[error]`: Đỏ kèm Traceback chi tiết

### 3.2. Chế độ Production (`LOG_FORMAT=json` hoặc `ENVIRONMENT=production`)
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

| `log_type` | Phạm vi sử dụng | Nơi phát sinh |
| :--- | :--- | :--- |
| `lifecycle` | Sự kiện khởi động (`application_startup`), tắt máy (`application_shutdown`), nạp module | `api.lifecycle` |
| `access` | Nhật ký truy cập HTTP hoàn tất của từng request (chứa `ttfb_ms`, `total_duration_ms`) | `api.access` (Middleware) |
| `application` | Log xử lý nghiệp vụ thông thường (Business Logic, Ingestion, Retrieval) | `api.*` |
| `audit` | Log kiểm tra bảo mật, đăng nhập, phân quyền, thanh toán | `audit` |

---

## 5. HƯỚNG DẪN KIỂM THỬ TỪNG BƯỚC

### Bước 1: Chạy Test Suite Tự Động
```bash
uv run pytest -s -v apps/api/tests/test_logging.py
```
*Kỳ vọng:* 8/8 test passed trong < 1 giây.

### Bước 2: Khởi chạy API Server
```bash
uv run --package api api
```

### Bước 3: Gửi Request Kiểm thử Trực tiếp
```bash
# 1. Health check & Tự sinh X-Request-ID
curl -i http://127.0.0.1:8000/health

# 2. Truyền nối X-Request-ID từ Client
curl -i -H "X-Request-ID: test-custom-trace-001" http://127.0.0.1:8000/health

# 3. Stream SSE & Đo lường TTFB
curl -N http://127.0.0.1:8000/events

# 4. Kiểm thử Bẫy Lỗi 404
curl -i http://127.0.0.1:8000/non-existent-route
```
