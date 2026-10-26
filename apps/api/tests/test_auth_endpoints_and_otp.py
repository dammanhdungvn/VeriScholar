from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_duplicate_email_conflict(async_client: AsyncClient):
    unique_email = f"scholar.{uuid4().hex[:8]}@univ.edu.vn"
    payload = {
        "email": unique_email,
        "password": "Password123!",
        "full_name": "TS. Test Scholar",
    }
    # Register 1: 201 Created
    res1 = await async_client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201
    body1 = res1.json()
    data1 = body1.get("data", body1)
    assert data1["user"]["email"] == unique_email

    # Register 2 (Duplicate): 409 Conflict with deterministic error_code
    res2 = await async_client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 409
    err = res2.json()["error"]
    assert err["code"] == "EMAIL_ALREADY_EXISTS"
    assert "đã được sử dụng" in err["message"]


@pytest.mark.asyncio
async def test_login_invalid_password_neutral_message(async_client: AsyncClient):
    res = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "scholar.nonexistent@univ.edu.vn",
            "password": "WrongPassword999!",
        },
    )
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "INVALID_CREDENTIALS"
    assert res.json()["error"]["message"] == "Email hoặc mật khẩu không chính xác."


@pytest.mark.asyncio
async def test_update_profile_orcid_and_byok(async_client: AsyncClient, auth_headers: dict):
    # Invalid ORCID rejected
    res_bad = await async_client.patch(
        "/api/v1/auth/me",
        headers=auth_headers,
        json={"orcid_id": "invalid-orcid"},
    )
    assert res_bad.status_code == 400
    assert res_bad.json()["error"]["code"] == "INVALID_ORCID_FORMAT"

    # Valid profile & BYOK
    res_ok = await async_client.patch(
        "/api/v1/auth/me",
        headers=auth_headers,
        json={
            "full_name": "PGS. TS. Nguyễn Văn B",
            "orcid_id": "0000-0002-1825-0097",
            "theme_preference": "dark",
            "byok_api_key": "sk-proj-test1234567890abcdef",
        },
    )
    assert res_ok.status_code == 200
    body_ok = res_ok.json()
    data = body_ok.get("data", body_ok)
    assert data["has_byok"] is True
    assert data["byok_masked"] == "sk-proj-...cdef"
    assert data["theme_preference"] == "dark"


@pytest.mark.asyncio
async def test_forgot_password_and_reset_with_otp_flow(async_client: AsyncClient):
    email = f"reset.scholar.{uuid4().hex[:8]}@univ.edu.vn"
    initial_password = "InitialPass123@"
    new_password = "UpdatedPass456@"

    # 1. Register account
    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": initial_password,
            "full_name": "TS. Đàm Mạnh Dũng",
        },
    )
    assert reg_res.status_code == 201

    # 2. Request forgot password OTP
    forgot_res = await async_client.post(
        "/api/v1/auth/forgot-password",
        json={"email": email},
    )
    assert forgot_res.status_code == 200
    forgot_data = forgot_res.json()["data"]
    otp_code = forgot_data.get("otp_code")
    assert otp_code is not None
    assert len(otp_code) == 6 and otp_code.isdigit()

    # 3. Attempt reset with 6-digit OTP but WITHOUT email -> 400 EMAIL_REQUIRED_FOR_OTP
    no_email_res = await async_client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": otp_code,
            "new_password": new_password,
        },
    )
    assert no_email_res.status_code == 400
    assert no_email_res.json()["error"]["code"] == "EMAIL_REQUIRED_FOR_OTP"

    # 4. Attempt reset with wrong OTP code -> 400 INVALID_RESET_CODE
    wrong_otp_res = await async_client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": "000000",
            "new_password": new_password,
            "email": email,
        },
    )
    assert wrong_otp_res.status_code == 400
    assert wrong_otp_res.json()["error"]["code"] == "INVALID_RESET_CODE"

    # 5. Reset with valid OTP code and email -> 200 OK
    reset_res = await async_client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": otp_code,
            "new_password": new_password,
            "email": email,
        },
    )
    assert reset_res.status_code == 200

    # 6. Replay attack: re-using the same OTP should now fail because cache is evicted
    replay_res = await async_client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": otp_code,
            "new_password": new_password,
            "email": email,
        },
    )
    assert replay_res.status_code == 400
    assert replay_res.json()["error"]["code"] == "INVALID_RESET_CODE"

    # 7. Old password no longer works
    old_login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": initial_password},
    )
    assert old_login_res.status_code == 401

    # 8. New password succeeds
    new_login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": new_password},
    )
    assert new_login_res.status_code == 200
    assert new_login_res.json()["data"]["user"]["email"] == email
