# System Monitoring, Langfuse Academic Telemetry, Alert Webhook & Deep Health Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hiện thực hóa kiến trúc Giám Sát & Đo Lường Học Thuật 3 Tầng: đồng bộ mã định danh `trace_id` (`X-Request-ID`) xuyên suốt, ghi nhận 3 chỉ số chất lượng học thuật lên Langfuse (`bbox_grounded`, `e2b_compile_attempts`, `user_feedback`), cảnh báo lỗi 500 chạy ngầm có chống bão cảnh báo (Cooldown 60s), và bộ đôi endpoint kiểm tra sức khỏe sâu (`/health/ready`, `/api/v1/system/status`).

**Architecture:** Tầng Middleware `PureASGITracingMiddleware` sinh/đọc `X-Request-ID`, đếm metrics trực tiếp trong RAM và lưu bộ đệm vòng `deque(maxlen=20)` cho 20 lỗi gần nhất; tầng dịch vụ `ai_tracing_service.py` làm sạch khóa bí mật (`scrub_sensitive_text`), ẩn danh `user_id` bằng HMAC-SHA256 và gửi điểm đánh giá lên Langfuse ở chế độ không chặn (Graceful No-Op fallback); tầng `alert_service.py` gửi cảnh báo Telegram/Discord bất đồng bộ qua `asyncio.create_task` kèm bộ lọc chống trùng lặp 60 giây.

**Tech Stack:** Python 3.12, FastAPI, `structlog`, Langfuse SDK, Sentry SDK, `httpx`, React 19 (`ErrorBoundary`, `FeedbackThumbs`).

**Spec:** [`docs/specs/07-monitoring-and-langfuse-spec.md`](../../specs/07-monitoring-and-langfuse-spec.md) & [`docs/PRD/07-monitoring-and-langfuse.md`](../../PRD/07-monitoring-and-langfuse.md).

---

## Global Constraints

- Chuẩn hóa duy nhất 2 môi trường cấu hình (`development` với `verischolar-dev` và `production` với `verischolar-prod`, cùng chế độ `test` cho `pytest`).
- Mọi dữ liệu log và telemetry bắt buộc đi qua bộ lọc `scrub_sensitive_text()` để che sạch khóa API BYOK (`sk-...`, `Bearer ...`, mật khẩu) thành `[REDACTED]`.
- Mọi tác vụ gửi telemetry Langfuse hoặc bắn cảnh báo Webhook Telegram/Discord bắt buộc chạy ngầm không chặn (`Non-Blocking`), cam kết không làm tăng độ trễ HTTP của học giả và không làm văng ứng dụng nếu dịch vụ giám sát bên ngoài mất kết nối.
- Giao diện người dùng tuyệt đối không hiển thị stack trace kỹ thuật thô; chỉ hiển thị thông điệp Tiếng Việt lịch sự kèm mã tham chiếu 4 ký tự cuối (`#9c1f`) và nút `[🔄 Thử lại]`.
- Toàn bộ liên kết trong tài liệu Markdown dùng đường dẫn tương đối.
- Bốn Cổng Xác Minh Bắt Buộc (`ruff`, `pytest`, `npm test`, `npm build`) phải đạt exit code 0 sau mỗi task.

---

## Review Focus

1. **BYOK Secret Redaction in Error Payloads & Logs:** Khi một request gửi kèm khóa API cá nhân bị lỗi xác thực hoặc lỗi mạng, chuỗi khóa `sk-...` tuyệt đối không được xuất hiện trong `recent_errors` của `/api/v1/system/status`, file log hay tin nhắn cảnh báo Telegram.
2. **Alert Storm Cooldown Deduplication (60s Window):** Khi cơ sở dữ liệu hoặc dịch vụ phụ trợ gặp sự cố khiến 50 request liên tiếp bị lỗi 500 trong 5 giây, `AlertService` chỉ bắn duy nhất **1 tin nhắn cảnh báo** cho mỗi cặp `(endpoint_path, error_type)` trong chu kỳ 60 giây.
3. **Bounded Ring Buffer Memory Safety:** Bộ đệm lưu lỗi gần nhất trong `PureASGITracingMiddleware` bắt buộc sử dụng `collections.deque(maxlen=20)` để đảm bảo dung lượng RAM cố định bất kể máy chủ chạy liên tục bao nhiêu ngày.
4. **Idempotent User Feedback Toggle:** Khi học giả bấm 👍 (`score = 1.0`) rồi đổi ý bấm 👎 (`score = 0.0`) trên cùng một câu trả lời AI, điểm đánh giá được cập nhật mượt mà theo lần bấm mới nhất; nếu gửi điểm ngoài tập `{0.0, 1.0}`, trả về `422 INVALID_FEEDBACK_SCORE`.
5. **Deep Readiness Probe Partial Outage Detection:** Khi PostgreSQL hoặc thư mục lưu trữ CAS `storage/blobs/` không thể ghi/đọc, `GET /health/ready` phải trả về `HTTP 503 Service Unavailable` với mã `DEPENDENCY_UNREADY` và chỉ rõ thành phần nào bị lỗi.

---

## Implementation Tasks

### Task 1: Secret Scrubber, User HMAC Pseudonymization & Langfuse Academic Scores (`apps/api`)

**Files:**
- Modify: `apps/api/src/api/core/logging.py`
- Modify: `apps/api/src/api/services/ai_tracing_service.py`
- Test: `apps/api/tests/test_telemetry_privacy_and_scrubber.py`

**Interfaces:**
- Consumes: `hmac`, `hashlib`, `re`, `structlog`.
- Produces:
  - `scrub_sensitive_text(raw: str) -> str`
  - `pseudonymize_user_id(user_id: str, secret_salt: str) -> str`
  - `AITracingService.record_academic_score(trace_id: str, name: Literal["bbox_grounded", "e2b_compile_attempts", "user_feedback"], value: float, comment: str | None = None) -> None`.

- [ ] **Step 1: Write the failing test**

Tạo `apps/api/tests/test_telemetry_privacy_and_scrubber.py`:
```python
from api.core.logging import scrub_sensitive_text
from api.services.ai_tracing_service import pseudonymize_user_id, AITracingService


def test_secret_scrubber_redacts_openai_and_bearer_tokens():
    dirty = "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9 and key sk-proj-1234567890abcdefghij"
    cleaned = scrub_sensitive_text(dirty)
    assert "eyJhbGci" not in cleaned
    assert "sk-proj-" not in cleaned
    assert "[REDACTED]" in cleaned


def test_pseudonymize_user_id_is_deterministic_64_hex():
    uid = "550e8400-e29b-41d4-a716-446655440000"
    hashed = pseudonymize_user_id(uid, "test-salt")
    assert len(hashed) == 64
    assert uid not in hashed
    assert hashed == pseudonymize_user_id(uid, "test-salt")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_telemetry_privacy_and_scrubber.py -v`
Expected: FAIL nếu chưa export hàm chuẩn hoặc thiếu `record_academic_score`.

- [ ] **Step 3: Implement `scrub_sensitive_text`, `pseudonymize_user_id`, and `record_academic_score`**

Cập nhật `logging.py` và `ai_tracing_service.py` đảm bảo chế độ No-Op an toàn khi không cấu hình khóa Langfuse.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_telemetry_privacy_and_scrubber.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/api/core/logging.py apps/api/src/api/services/ai_tracing_service.py apps/api/tests/test_telemetry_privacy_and_scrubber.py
git commit -m "feat(api): add BYOK secret scrubber, HMAC user pseudonymization, and Langfuse score recorder"
```

---

### Task 2: PureASGI Tracing Middleware Metrics, 20-Error Ring Buffer & Cooldown Alert Service (`apps/api`)

**Files:**
- Modify: `apps/api/src/api/middleware/tracing.py`
- Create: `apps/api/src/api/services/alert_service.py`
- Test: `apps/api/tests/test_tracing_and_alert_cooldown.py`

**Interfaces:**
- Consumes: `collections.deque(maxlen=20)`, `asyncio.create_task`, `scrub_sensitive_text`.
- Produces:
  - `PureASGITracingMiddleware` gắn `X-Request-ID`, đếm `total_requests`, `status_2xx`, `status_4xx`, `status_5xx`, `avg_duration_ms`, và lưu tối đa 20 lỗi gần nhất đã được scrub bí mật.
  - `AlertService.send_webhook_alert_if_needed(trace_id: str, path: str, error_type: str, message: str)` với thời gian hồi (cooldown) **60 giây** trên mỗi cặp `(path, error_type)`.

- [ ] **Step 1: Write the failing test**

Tạo `apps/api/tests/test_tracing_and_alert_cooldown.py` kiểm tra:
1. Kích hoạt 25 lỗi 500 liên tiếp $\rightarrow$ `recent_errors` chỉ giữ đúng 20 lỗi mới nhất.
2. Gọi `send_webhook_alert_if_needed` 5 lần liên tiếp cho cùng `(path, error_type)` trong 10 giây $\rightarrow$ chỉ thực hiện đúng 1 lần gọi HTTP tới Webhook và không chặn luồng chính.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_tracing_and_alert_cooldown.py -v`
Expected: FAIL

- [ ] **Step 3: Implement `alert_service.py` and upgrade `PureASGITracingMiddleware` in `tracing.py`**

Cài đặt bộ đếm metrics trong RAM, `deque(maxlen=20)` và `AlertService` có cooldown 60 giây chạy ngầm qua `asyncio.create_task` với timeout 3 giây.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_tracing_and_alert_cooldown.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/api/middleware/tracing.py apps/api/src/api/services/alert_service.py apps/api/tests/test_tracing_and_alert_cooldown.py
git commit -m "feat(api): add 20-error ring buffer metrics and non-blocking alert webhook with 60s cooldown"
```

---

### Task 3: Deep Readiness Probe (`/health/ready`), System Status (`/api/v1/system/status`) & Feedback API (`apps/api`)

**Files:**
- Create: `apps/api/src/api/v1/endpoints/health.py`
- Create: `apps/api/src/api/v1/endpoints/feedback.py`
- Modify: `apps/api/src/api/v1/api.py`
- Test: `apps/api/tests/test_health_and_feedback_endpoints.py`

**Interfaces:**
- Consumes: `PureASGITracingMiddleware` metrics state, `AITracingService.record_academic_score`, `SessionTurnModel`.
- Produces:
  - `GET /health/ready` (`200 OK` khi DB + Redis + CAS writable sẵn sàng; `503 DEPENDENCY_UNREADY` khi một thành phần lỗi).
  - `GET /api/v1/system/status` (báo cáo `uptime_seconds`, `metrics`, `recent_errors`).
  - `POST /api/v1/sessions/{session_id}/messages/{message_id}/feedback` (chỉ nhận `score` trong `{0.0, 1.0}`, trả về `422 INVALID_FEEDBACK_SCORE` hoặc `404 FEEDBACK_MESSAGE_NOT_FOUND`).

- [ ] **Step 1: Write the failing test**

Tạo `apps/api/tests/test_health_and_feedback_endpoints.py` kiểm tra cả 3 endpoints và các mã lỗi xác định trong Ma trận Mã lỗi của `SPEC-07`.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_health_and_feedback_endpoints.py -v`
Expected: FAIL

- [ ] **Step 3: Implement `health.py`, `feedback.py`, and register routers in `api.py`**

Cài đặt kiểm tra sâu PostgreSQL (`SELECT 1`), Redis (`PING`), CAS probe file và endpoint gửi đánh giá `user_feedback`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_health_and_feedback_endpoints.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/api/v1/endpoints/health.py apps/api/src/api/v1/endpoints/feedback.py apps/api/src/api/v1/api.py apps/api/tests/test_health_and_feedback_endpoints.py
git commit -m "feat(api): add deep readiness probe, system status dashboard API, and AI feedback endpoint"
```

---

### Task 4: Compassionate Frontend Error Boundary (`#xxxx` Reference Code) & AI Feedback Thumbs (`apps/web`)

**Files:**
- Create: `apps/web/src/components/common/CompassionateErrorBoundary.tsx`
- Create: `apps/web/src/features/reader/components/MessageFeedbackThumbs.tsx`
- Test: `apps/web/src/components/common/__tests__/MonitoringUX.test.tsx`

**Interfaces:**
- Consumes: Header `X-Request-ID` / `error.trace_id`, `POST /api/v1/sessions/{sessionId}/messages/{messageId}/feedback`.
- Produces:
  - `CompassionateErrorBoundary` hiển thị thông báo Tiếng Việt lịch sự, nút `[🔄 Thử lại]` và mã tham chiếu `#9c1f` (4 ký tự cuối của `trace_id`) kèm nút sao chép 1 chạm.
  - `MessageFeedbackThumbs` hiển thị nút 👍 / 👎 dưới mỗi câu trả lời của AI, sáng lên tức thì khi nhấp và hỗ trợ đổi đánh giá mượt mà.

- [ ] **Step 1: Write the failing test**

Tạo `apps/web/src/components/common/__tests__/MonitoringUX.test.tsx` kiểm tra:
1. Không lộ stack trace kỹ thuật khi component con ném lỗi; hiển thị đúng mã tham chiếu `#9c1f` và nút `[🔄 Thử lại]`.
2. Nhấp 👍 hoặc 👎 gọi API feedback với `score = 1.0` hoặc `0.0` mà không tải lại trang.

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- MonitoringUX`
Expected: FAIL

- [ ] **Step 3: Implement `CompassionateErrorBoundary.tsx` and `MessageFeedbackThumbs.tsx`**

Cài đặt giao diện bắt lỗi thân thiện và nút đánh giá phản hồi AI theo đúng đặc tả tại Mục 6 của `SPEC-07`.

- [ ] **Step 4: Run all 4 verification gates to confirm 100% pass**

Run: `uv run ruff check . && uv run pytest && npm --prefix apps/web run test && npm --prefix apps/web run build`
Expected: 100% PASS (exit code 0)

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/components/common/ apps/web/src/features/reader/components/MessageFeedbackThumbs.tsx
git commit -m "feat(web): add CompassionateErrorBoundary with short reference code and AI feedback thumbs"
```
