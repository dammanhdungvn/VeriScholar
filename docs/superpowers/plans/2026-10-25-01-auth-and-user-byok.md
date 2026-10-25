# Scholar Authentication, User Profile & Secure BYOK Key Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hiện thực hóa phân hệ Xác thực Học giả toàn diện, duy trì phiên làm việc bảo mật (JWT + Redis 7), xác thực email/khôi phục mật khẩu OTP, quản lý hồ sơ học thuật (ORCID, đơn vị công tác) và mã hóa cấp quân đội **AES-256-GCM** cho khóa riêng tư AI cá nhân (BYOK).

**Architecture:** Áp dụng Kiến trúc Lục giác (Hexagonal Architecture): Thực thể người dùng thuần túy, bộ kiểm tra chuẩn email học thuật/ORCID và enum theme nằm trong `packages/core`; dịch vụ `AuthService` và engine mã hóa AES-256-GCM đặt trong `apps/api`; tầng cơ sở dữ liệu sử dụng bảng `users` PostgreSQL kết hợp Redis 7 lưu trữ OTP (300s TTL) và danh sách đen thu hồi token; giao diện `apps/web` quản lý trạng thái bằng Zustand v5 (`useAuthStore`), tự động làm mới phiên ngầm qua Axios interceptor và hiển thị `UserProfileModal` 3 tabs.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0 Async, PostgreSQL 16+, Redis 7, Cryptography (AES-256-GCM), React 19, TypeScript, Tailwind CSS, Zustand v5, Axios.

**Spec:** [`docs/specs/01-auth-and-user-spec.md`](../../specs/01-auth-and-user-spec.md) & [`docs/PRD/01-auth-and-user.md`](../../PRD/01-auth-and-user.md).

---

## Global Constraints

- 100% mã nguồn trong `packages/core/` chỉ dùng Python Standard Library và `pydantic`, cấm tuyệt đối import `fastapi`, `sqlalchemy`, `redis`, `cryptography`.
- Mọi truy vấn trên bảng `users` hoặc dữ liệu hồ sơ cá nhân phải kiểm tra quyền sở hữu hoặc cách ly định danh nghiêm ngặt (`user_id == current_user.id`).
- Khóa cá nhân BYOK gửi lên từ client bắt buộc mã hóa ngay bằng thuật toán **AES-256-GCM** với khóa chủ bí mật `BYOK_ENCRYPTION_KEY` (32 bytes hex); cấm tuyệt đối lưu trữ khóa thô hoặc ghi khóa thô vào log/trace.
- Khi người dùng truy vấn hồ sơ (`GET /api/v1/auth/me`), không bao giờ trả về khóa thô, chỉ trả về `has_byok: true` và `byok_masked: "sk-proj-...4f8A"`.
- Bảng mã lỗi phản hồi bắt buộc tuân thủ 100% Ma Trận Mã Lỗi Chuẩn Hóa trong Mục 4.C của [`docs/specs/01-auth-and-user-spec.md`](../../specs/01-auth-and-user-spec.md).
- Toàn bộ liên kết trong tài liệu Markdown dùng đường dẫn tương đối (`./...`, `../...`, `../../...`), tuyệt đối không dùng link tuyệt đối máy chủ.
- Bốn Cổng Xác Minh Bắt Buộc (`uv run ruff check .`, `uv run pytest`, `npm --prefix apps/web run test`, `npm --prefix apps/web run build`) phải đạt exit code 0 sau mỗi task.

---

## Review Focus

1. **Master Encryption Key Absence or Corruption:** Khi biến môi trường `BYOK_ENCRYPTION_KEY` chưa được thiết lập hoặc có độ dài không đủ 32 bytes (64 hex chars), hệ thống phải từ chối lưu khóa với mã lỗi `500 BYOK_ENCRYPTION_FAILED`, ghi nhận cảnh báo hệ thống an toàn và tuyệt đối không lưu khóa dưới dạng văn bản thô (plaintext).
2. **Anti-Enumeration Neutrality in Auth Endpoints:** Endpoints `POST /api/v1/auth/forgot-password` và `POST /api/v1/auth/login` phải trả về phản hồi trung tính và bảo toàn thời gian xử lý (timing-safe), không để lộ email đó đã tồn tại hay chưa tồn tại trong cơ sở dữ liệu để ngăn chặn hành vi dò quét danh tính học giả.
3. **Redis OTP Attempt Exhaustion & Replay Cutoff:** Khi người dùng nhập sai mã OTP lần thứ 6 liên tiếp, mã OTP trong Redis phải bị xóa tiêu hủy tức thì và chặn yêu cầu gửi mới trong 15 phút với mã `429 OTP_MAX_ATTEMPTS_EXCEEDED`, đảm bảo mã cũ không thể bị tấn công vét cạn (brute-force).
4. **Token Refresh Race Condition & Queue Handling:** Khi nhiều request bất đồng bộ trên giao diện đồng thời nhận mã lỗi `401 Unauthorized`, interceptor của Axios phải tạm dừng hàng đợi và chỉ thực hiện duy nhất 1 request `POST /api/v1/auth/refresh`, sau đó phân phối token mới cho toàn bộ các request đang chờ, tránh tình trạng gọi refresh dồn dập làm thu hồi chéo refresh token.
5. **BYOK Plaintext Leakage Guardrail in Response & Logs:** Khóa OpenAI API cá nhân (`byok_api_key`) chỉ được xuất hiện trên RAM trong thời khắc thực hiện gọi mô hình LLM; tuyệt đối không xuất hiện trong payload trả về của `GET /api/v1/auth/me`, trong bảng ghi log `structlog`, trong Pydantic dump hay trong spans giám sát Langfuse.

---

## Implementation Tasks

### Task 1: Core Domain User Entity, Value Objects & Academic Profile Validators (`packages/core`)

**Files:**
- Create: `packages/core/src/core/domain/entities/user.py`
- Modify: `packages/core/src/core/domain/value_objects/enums.py`
- Modify: `packages/core/src/core/services/email_validator.py`
- Test: `packages/core/tests/test_auth_user_core.py`

**Interfaces:**
- Consumes: Python Standard Library (`re`, `uuid.UUID`, `dataclasses`, `datetime`), `pydantic.BaseModel`.
- Produces:
  - `ThemePreference` enum (`LIGHT = "light"`, `DARK = "dark"`, `SYSTEM = "system"`).
  - `AcademicRank` enum (`STUDENT`, `MASTER`, `PHD`, `ASSOC_PROF`, `PROFESSOR`, `RESEARCHER`).
  - `validate_orcid_id(orcid: str | None) -> bool` (kiểm tra regex `^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$`).
  - `mask_api_key(raw_key: str) -> str` (chuyển đổi `sk-proj-abc123456xyz` thành `sk-proj-...6xyz`).
  - `UserEntity` thuần Python không phụ thuộc ORM.

- [ ] **Step 1: Write the failing test**

Tạo `packages/core/tests/test_auth_user_core.py`:
```python
import pytest
from uuid import uuid4
from core.domain.value_objects.enums import ThemePreference
from core.services.email_validator import (
    validate_academic_or_trusted_email,
    validate_orcid_id,
    mask_api_key,
)
from core.domain.entities.user import UserEntity


def test_orcid_validation_regex():
    assert validate_orcid_id("0000-0002-1825-0097") is True
    assert validate_orcid_id("0000-0001-5109-370X") is True
    assert validate_orcid_id("invalid-orcid-1234") is False
    assert validate_orcid_id("0000-0002-1825") is False
    assert validate_orcid_id(None) is True  # Optional field


def test_mask_api_key_formats_correctly():
    assert mask_api_key("sk-proj-abcdef123456") == "sk-proj-...3456"
    assert mask_api_key("sk-short12") == "sk-...rt12"
    assert mask_api_key("") == ""


def test_user_entity_creation_and_theme_invariant():
    user = UserEntity(
        id=uuid4(),
        email="scholar@vnu.edu.vn",
        full_name="TS. Nguyễn Văn A",
        theme_preference=ThemePreference.DARK,
        orcid_id="0000-0002-1825-0097",
    )
    assert user.theme_preference == ThemePreference.DARK
    assert user.email == "scholar@vnu.edu.vn"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest packages/core/tests/test_auth_user_core.py -v`  
Expected: FAIL with `ImportError: cannot import name 'validate_orcid_id'` or `No module named 'core.domain.entities.user'`.

- [ ] **Step 3: Implement UserEntity, ThemePreference and validators in `packages/core`**

Cài đặt `validate_orcid_id` và `mask_api_key` trong `email_validator.py`, bổ sung `ThemePreference` vào `enums.py`, và tạo thực thể `UserEntity` trong `packages/core/src/core/domain/entities/user.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest packages/core/tests/test_auth_user_core.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add packages/core/src/core/domain/entities/user.py packages/core/src/core/domain/value_objects/enums.py packages/core/src/core/services/email_validator.py packages/core/tests/test_auth_user_core.py
git commit -m "feat(core): add UserEntity, ThemePreference, ORCID validator and API key masking"
```

---

### Task 2: BYOK AES-256-GCM Cryptographic Engine & Pydantic Schema Security (`apps/api`)

**Files:**
- Create: `apps/api/src/api/core/crypto.py`
- Modify: `apps/api/src/api/db/models/user.py`
- Modify: `apps/api/src/api/schemas/auth.py`
- Test: `apps/api/tests/test_byok_crypto.py`

**Interfaces:**
- Consumes: `cryptography.hazmat.primitives.ciphers.aead.AESGCM`, `api.core.config.settings.BYOK_ENCRYPTION_KEY`.
- Produces:
  - `encrypt_byok_key(raw_key: str, master_key_hex: str) -> str` (sinh nonce 12 bytes ngẫu nhiên, mã hóa chuỗi và trả về `base64(nonce + ciphertext + tag)`).
  - `decrypt_byok_key(encrypted_base64: str, master_key_hex: str) -> str` (giải mã chuỗi base64 khôi phục khóa thô trên bộ nhớ RAM).
  - Cột mới trong `UserModel`: `theme_preference` (VARCHAR, default `'system'`) và `byok_api_key_encrypted` (TEXT, nullable).
  - Cập nhật Pydantic schemas: `UserProfileResponse` có `has_byok: bool`, `byok_masked: str | None`, `theme_preference: str`; `UpdateProfileRequest` nhận `byok_api_key: str | None`.

- [ ] **Step 1: Write the failing test**

Tạo `apps/api/tests/test_byok_crypto.py`:
```python
import os
import pytest
from api.core.crypto import encrypt_byok_key, decrypt_byok_key, CryptoError

TEST_MASTER_KEY = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"


def test_byok_aes_256_gcm_roundtrip():
    raw_key = "sk-proj-test1234567890abcdefghijklmnopqrstuvwxyz"
    encrypted = encrypt_byok_key(raw_key, TEST_MASTER_KEY)
    
    assert encrypted != raw_key
    assert "sk-proj" not in encrypted
    
    decrypted = decrypt_byok_key(encrypted, TEST_MASTER_KEY)
    assert decrypted == raw_key


def test_byok_encryption_rejects_invalid_master_key():
    with pytest.raises(CryptoError) as exc_info:
        encrypt_byok_key("sk-test", "short-invalid-key")
    assert "32 bytes" in str(exc_info.value)


def test_byok_decryption_detects_ciphertext_tampering():
    raw_key = "sk-proj-secret-key"
    encrypted = encrypt_byok_key(raw_key, TEST_MASTER_KEY)
    
    # Tamper with base64 payload
    tampered = encrypted[:-2] + ("AA" if not encrypted.endswith("AA") else "BB")
    with pytest.raises(CryptoError):
        decrypt_byok_key(tampered, TEST_MASTER_KEY)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_byok_crypto.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'api.core.crypto'`.

- [ ] **Step 3: Implement AES-256-GCM crypto service and update UserModel & Pydantic schemas**

Cài đặt `apps/api/src/api/core/crypto.py` sử dụng thư viện `cryptography`, cập nhật `UserModel` trong `apps/api/src/api/db/models/user.py` bổ sung 2 cột và cập nhật schema `auth.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_byok_crypto.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/api/core/crypto.py apps/api/src/api/db/models/user.py apps/api/src/api/schemas/auth.py apps/api/tests/test_byok_crypto.py
git commit -m "feat(api): add AES-256-GCM BYOK crypto engine, UserModel fields, and secure profile schemas"
```

---

### Task 3: Redis 7 OTP Security, Anti-Enumeration & Deterministic Auth REST Endpoints (`apps/api`)

**Files:**
- Modify: `apps/api/src/api/services/auth_service.py`
- Modify: `apps/api/src/api/v1/endpoints/auth.py`
- Test: `apps/api/tests/test_auth_endpoints_and_otp.py`

**Interfaces:**
- Consumes: `encrypt_byok_key`, `decrypt_byok_key`, `mask_api_key`, `validate_orcid_id`, `UserModel`, `ErrorResponse` chuẩn hóa theo Ma Trận Mã Lỗi của `SPEC-01`.
- Produces:
  - Redis key `verischolar:otp:{email}` lưu `{ "code": "...", "user_id": "...", "attempts": int }` với TTL 300s.
  - Redis rate limit `verischolar:rate_limit:otp:{email}` (tối đa 3 lần gửi / 15 phút).
  - 13 endpoints đầy đủ xử lý lỗi tất định với các mã: `INVALID_CREDENTIALS`, `EMAIL_ALREADY_EXISTS`, `OTP_MAX_ATTEMPTS_EXCEEDED`, `OTP_RATE_LIMITED`, `WEAK_PASSWORD`, `INVALID_ORCID_FORMAT`, `RESOURCE_NOT_FOUND`.

- [ ] **Step 1: Write the failing test**

Tạo `apps/api/tests/test_auth_endpoints_and_otp.py`:
```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_duplicate_email_conflict(async_client: AsyncClient):
    payload = {
        "email": "scholar.test@univ.edu.vn",
        "password": "Password123!",
        "full_name": "TS. Test Scholar"
    }
    # Register 1: 201 Created
    res1 = await async_client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201
    assert res1.json()["data"]["user"]["email"] == "scholar.test@univ.edu.vn"

    # Register 2 (Duplicate): 409 Conflict with deterministic error_code
    res2 = await async_client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 409
    err = res2.json()["error"]
    assert err["code"] == "EMAIL_ALREADY_EXISTS"
    assert "đã được sử dụng" in err["message"]


@pytest.mark.asyncio
async def test_login_invalid_password_neutral_message(async_client: AsyncClient):
    res = await async_client.post("/api/v1/auth/login", json={
        "email": "scholar.test@univ.edu.vn",
        "password": "WrongPassword999!"
    })
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "INVALID_CREDENTIALS"
    assert res.json()["error"]["message"] == "Email hoặc mật khẩu không chính xác."


@pytest.mark.asyncio
async def test_update_profile_orcid_and_byok(async_client: AsyncClient, auth_headers: dict):
    # Invalid ORCID rejected
    res_bad = await async_client.patch("/api/v1/auth/me", headers=auth_headers, json={
        "orcid_id": "invalid-orcid"
    })
    assert res_bad.status_code == 400
    assert res_bad.json()["error"]["code"] == "INVALID_ORCID_FORMAT"

    # Valid profile & BYOK
    res_ok = await async_client.patch("/api/v1/auth/me", headers=auth_headers, json={
        "full_name": "PGS. TS. Nguyễn Văn B",
        "orcid_id": "0000-0002-1825-0097",
        "theme_preference": "dark",
        "byok_api_key": "sk-proj-test1234567890abcdef"
    })
    assert res_ok.status_code == 200
    data = res_ok.json()["data"]
    assert data["has_byok"] is True
    assert data["byok_masked"] == "sk-proj-...cdef"
    assert data["theme_preference"] == "dark"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest apps/api/tests/test_auth_endpoints_and_otp.py -v`  
Expected: FAIL (mã lỗi trả về chưa đồng nhất hoặc thiếu trường xử lý BYOK/ORCID).

- [ ] **Step 3: Implement Redis OTP rate limiting, BYOK encryption integration, and error envelopes**

Cập nhật `AuthService` trong `apps/api/src/api/services/auth_service.py` và `apps/api/src/api/v1/endpoints/auth.py`. Đảm bảo mọi lỗi đều ném `HTTPException` với cấu trúc `detail={"code": "...", "message": "...", "field": "...", "action": "..."}` đồng nhất.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest apps/api/tests/test_auth_endpoints_and_otp.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/api/services/auth_service.py apps/api/src/api/v1/endpoints/auth.py apps/api/tests/test_auth_endpoints_and_otp.py
git commit -m "feat(api): implement Redis OTP verification, BYOK endpoint logic, and deterministic error handling"
```

---

### Task 4: Frontend Zustand Auth Store, Axios Token Queue Interceptor & UserProfileModal 3 Tabs (`apps/web`)

**Files:**
- Modify: `apps/web/src/features/auth/stores/useAuthStore.ts`
- Modify: `apps/web/src/lib/apiClient.ts`
- Create/Modify: `apps/web/src/components/profile/UserProfileModal.tsx`
- Test: `apps/web/src/features/auth/__tests__/UserProfileModal.test.tsx`

**Interfaces:**
- Consumes: Endpoints `GET /api/v1/auth/me`, `PATCH /api/v1/auth/me`, `POST /api/v1/auth/refresh`.
- Produces:
  - Zustand store đồng bộ `theme` với thẻ `<html>` (`dark` class) và lưu trữ an toàn `user`, `accessToken`.
  - Axios response interceptor tự động gom hàng đợi (request queue) khi gặp 401 để chỉ gọi refresh token 1 lần duy nhất.
  - Giao diện `UserProfileModal` chuẩn mực 3 Tabs:
    - Tab 1: Hồ sơ Học giả (Họ tên, Đơn vị công tác, Khoa/Bộ môn, Mã ORCID iD có validation).
    - Tab 2: Bảo mật & Khóa BYOK (Form đổi mật khẩu, ô cấu hình `sk-proj-...` kèm nút "Lưu & Xác thực khóa", hiển thị trạng thái `has_byok` và badge `byok_masked`).
    - Tab 3: Giao diện Sáng / Tối (3 nút chọn: `☀️ Sáng`, `🌙 Tối`, `💻 Theo hệ điều hành`).

- [ ] **Step 1: Write the failing test**

Tạo `apps/web/src/features/auth/__tests__/UserProfileModal.test.tsx`:
```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { UserProfileModal } from '@/components/profile/UserProfileModal';

describe('UserProfileModal 3 Tabs Component', () => {
  it('renders 3 tabs and displays masked BYOK key when available', () => {
    const mockUser = {
      id: 'usr-123',
      email: 'scholar@univ.edu.vn',
      full_name: 'TS. Nguyễn Văn A',
      has_byok: true,
      byok_masked: 'sk-proj-...4f8A',
      theme_preference: 'dark' as const,
      orcid_id: '0000-0002-1825-0097'
    };

    render(<UserProfileModal isOpen={true} onClose={() => {}} user={mockUser} />);

    expect(screen.getByText(/Hồ sơ Học thuật/i)).toBeInTheDocument();
    expect(screen.getByText(/Bảo mật & Khóa BYOK/i)).toBeInTheDocument();
    expect(screen.getByText(/Giao diện/i)).toBeInTheDocument();

    // Click Tab 2
    fireEvent.click(screen.getByText(/Bảo mật & Khóa BYOK/i));
    expect(screen.getByText(/sk-proj-...4f8A/i)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test -- UserProfileModal`  
Expected: FAIL with component missing or tab elements not found.

- [ ] **Step 3: Implement `UserProfileModal.tsx` and Axios Interceptors in `apps/web`**

Xây dựng modal hoàn chỉnh với 3 tabs, gắn kết gọi API qua `apiClient`, đồng bộ trạng thái đổi theme vào `useAuthStore` và kiểm tra định dạng ORCID phía client trước khi gửi PATCH request.

- [ ] **Step 4: Run test and build to verify all 4 verification gates pass**

Run: `uv run ruff check . && uv run pytest && npm --prefix apps/web run test && npm --prefix apps/web run build`  
Expected: 100% PASS (exit code 0)

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/features/auth/ apps/web/src/components/profile/ apps/web/src/lib/apiClient.ts
git commit -m "feat(web): implement UserProfileModal 3 tabs, theme synchronization, and token refresh queuing"
```
