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
