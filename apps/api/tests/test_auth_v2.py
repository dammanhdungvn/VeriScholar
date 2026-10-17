"""Comprehensive Unit & Integration Tests for Auth 2.0.

Covers:
1. email_validator.py: disposable email rejection, academic & reputable prioritization.
2. Strict whitelist rejection of maxxspace.com and arbitrary unverified domains with HTTP 422.
3. Layer-2 Pydantic schema validation for RegisterRequest & LoginRequest.
4. EmailService: 6-digit OTP generation, verify token, SMTP + logger fallback.
5. Endpoints: POST /api/v1/auth/verify-email and POST /api/v1/auth/resend-verification.
6. Token lifetimes: 30 days (2,592,000s) for remember_me=True, 90 days for refresh token.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

import httpx
import pytest
from api import app
from api.core.config import settings
from api.core.email_validator import (
    EmailCategory,
    classify_email,
    ensure_valid_registration_email,
    extract_domain,
    get_academic_priority_score,
    is_academic_domain,
    is_disposable_domain,
    is_reputable_domain,
    validate_academic_or_trusted_email,
    validate_user_full_name,
)
from api.db.models.base import Base
from api.db.models.user import UserModel
from api.db.session import get_db
from api.schemas.auth import (
    GoogleAuthRequest,
    LoginRequest,
    RegisterRequest,
    UpdateProfileRequest,
    UserProfileResponse,
)
from api.services.auth_service import AuthService
from api.services.email_service import EMAIL_LOG_PATH, EmailService
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@asynccontextmanager
async def auth2_test_context() -> AsyncGenerator[
    tuple[httpx.AsyncClient, async_sessionmaker[AsyncSession]], None
]:
    """Provide isolated in-memory test database and HTTP test client."""
    engine = create_async_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client, session_maker

    app.dependency_overrides.clear()
    await engine.dispose()


# ==============================================================================
# Task 1: email_validator.py Tests & Strict Whitelist Enforcement
# ==============================================================================
def test_email_validator_disposable_blocking() -> None:
    """Verify that known disposable email domains are strictly identified and rejected."""
    disposable_samples = [
        "user@mailinator.com",
        "hacker@10minutemail.com",
        "burner@tempmail.com",
        "temp@temp-mail.org",
        "bot@guerrillamail.com",
        "throwaway@trashmail.com",
        "spam@yopmail.com",
        "anon@sharklasers.com",
        "test@fakeinbox.com",
        "auto@burnermail.io",
        "intruder@maxxspace.com",
    ]
    for email in disposable_samples:
        domain = extract_domain(email)
        assert is_disposable_domain(domain) is True, f"Failed for {email}"
        assert classify_email(email) == EmailCategory.DISPOSABLE

        is_valid, err = validate_academic_or_trusted_email(email)
        assert is_valid is False
        assert err is not None

        with pytest.raises(ValueError):
            ensure_valid_registration_email(email)


def test_maxxspace_and_non_whitelisted_domains_strictly_rejected() -> None:
    """Verify Sprint Auth Refinement: maxxspace.com & non-whitelisted domains are rejected.

    Demonstrates removal of the arbitrary len(domain_parts) >= 2 fallback and strict
    enforcement of whitelist: only academic (.edu, .edu.vn, .ac.*), reputable providers
    (Gmail, Outlook, Proton, iCloud, etc.), and institutional (.gov, .org).
    """
    untrusted_samples = [
        "user@maxxspace.com",
        "temp_user@sub.maxxspace.com",
        "hacker@randomtemp.xyz",
        "badactor@somedotcomdomain.com",
        "spammer@unknowncorp.biz",
        "bot@unverifiedmail.net",
    ]
    for email in untrusted_samples:
        domain = extract_domain(email)
        # Must not be accepted as academic
        assert is_academic_domain(domain) is False, f"Expected non-academic for {domain}"

        # Must fail validate_academic_or_trusted_email
        is_valid, err = validate_academic_or_trusted_email(email)
        assert is_valid is False, f"Expected invalid for {email}"
        assert err is not None

        # Must raise ValueError when passed to ensure_valid_registration_email
        with pytest.raises(ValueError):
            ensure_valid_registration_email(email)

        # Must be rejected by RegisterRequest Pydantic validator
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(
                full_name="Untrusted User",
                email=email,
                password="SecurePassword2026!",
            )
        assert "không thuộc danh sách" in str(exc_info.value) or "tạm thời" in str(exc_info.value)


def test_email_validator_academic_and_reputable_recognition() -> None:
    """Verify academic and reputable domains are properly recognized and prioritized."""
    academic_samples = [
        "prof@stanford.edu",
        "researcher@mit.edu",
        "scholar@ox.ac.uk",
        "giangvien@vnu.edu.vn",
        "hocvien@hust.edu.vn",
        "lab@cam.ac.uk",
        "postdoc@nus.edu.sg",
        "phd@u-tokyo.ac.jp",
    ]
    for email in academic_samples:
        assert is_academic_domain(extract_domain(email)) is True, f"Failed for {email}"
        assert classify_email(email) == EmailCategory.ACADEMIC
        assert get_academic_priority_score(email) == 100
        is_valid, err = validate_academic_or_trusted_email(email)
        assert is_valid is True
        assert err is None
        assert ensure_valid_registration_email(email) == email.lower()

    reputable_samples = [
        "john.doe@gmail.com",
        "mary@outlook.com",
        "dev@proton.me",
        "research@verischolar.org",
        "investigator@yahoo.com",
        "lead@icloud.com",
        "scientist@nih.gov",
    ]
    for email in reputable_samples:
        assert is_reputable_domain(extract_domain(email)) is True, f"Failed for {email}"
        is_valid, err = validate_academic_or_trusted_email(email)
        assert is_valid is True
        assert err is None
        assert get_academic_priority_score(email) >= 60


def test_user_full_name_validation() -> None:
    """Verify full name validation rules (length, characters, no XSS)."""
    valid_names = [
        "Dr. Alice Scholar",
        "Nguyen Van A",
        "Jean-Luc Picard",
        "Alan Turing",
        "Dev User",
    ]
    for name in valid_names:
        is_valid, err = validate_user_full_name(name)
        assert is_valid is True, f"Failed for {name}: {err}"

    invalid_names = [
        "A",  # too short (< 2)
        "Dr. <script>alert(1)</script>",  # XSS
        'Dr. Hacker" OR "1"="1',  # quotes
        "Dr. $evil_var",  # dollar
    ]
    for name in invalid_names:
        is_valid, err = validate_user_full_name(name)
        assert is_valid is False


# ==============================================================================
# Task 2: Pydantic Schema Validation Layer-2 Tests
# ==============================================================================
def test_register_request_schema_validation() -> None:
    """Verify Layer-2 Pydantic schema validation for RegisterRequest."""
    # 1. Valid registration payload
    req = RegisterRequest(
        full_name="Prof. John Doe",
        email="  JOHN.DOE@STANFORD.EDU  ",
        password="SecurePassword2026!",
        confirm_password="SecurePassword2026!",
        institution="Stanford University",
    )
    assert req.email == "john.doe@stanford.edu"
    assert req.full_name == "Prof. John Doe"

    # 2. Reject disposable email
    with pytest.raises(ValidationError) as exc:
        RegisterRequest(
            full_name="Burner User",
            email="spammer@mailinator.com",
            password="SecurePassword2026!",
        )
    assert "tạm thời" in str(exc.value)

    # 3. Reject password mismatch
    with pytest.raises(ValidationError) as exc:
        RegisterRequest(
            full_name="Prof. John Doe",
            email="john@stanford.edu",
            password="SecurePassword2026!",
            confirm_password="DifferentPassword!",
        )
    assert "Mật khẩu xác nhận không khớp" in str(exc.value)

    # 4. Reject empty or trivially short password
    with pytest.raises(ValidationError):
        RegisterRequest(
            full_name="Prof. John Doe",
            email="john@stanford.edu",
            password="   ",
        )


def test_login_request_schema_validation() -> None:
    """Verify Layer-2 Pydantic schema validation for LoginRequest."""
    # 1. Normalization of email
    req = LoginRequest(
        email="  SCHOLAR@HARVARD.EDU ",
        password="ValidPassword123!",
        remember_me=True,
    )
    assert req.email == "scholar@harvard.edu"
    assert req.remember_me is True

    # 2. Reject blank password
    with pytest.raises(ValidationError):
        LoginRequest(
            email="scholar@harvard.edu",
            password="   ",
        )


# ==============================================================================
# Task 3 & 5: EmailService & Token Lifetimes Tests
# ==============================================================================
@pytest.mark.asyncio
async def test_email_service_and_token_lifetimes() -> None:
    """Verify EmailService OTP generation/fallback and token lifetimes (30d / 90d)."""
    email_service = EmailService()
    # Test fallback delivery (writes to audit log without throwing)
    sent = await email_service.send_verification_email(
        email="scholar.test@harvard.edu",
        code="987654",
        token="jwt.mock.token",
    )
    assert sent is True

    # Verify Token Lifetimes in AuthService
    engine = create_async_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_maker() as session:
        auth_service = AuthService(db=session, email_service=email_service)
        mock_user = UserModel(
            id=UUID("00000000-0000-0000-0000-000000000099"),
            email="test.scholar@mit.edu",
            full_name="Dr. Test Scholar",
            hashed_password="hashed_pwd",
            is_active=True,
            role="researcher",
        )

        # 1. remember_me = True -> Access token = 30 days (2,592,000s)
        tokens_30d = auth_service.create_tokens_for_user(mock_user, remember_me=True)
        assert tokens_30d.expires_in == settings.REMEMBER_ME_ACCESS_TOKEN_EXPIRE_SECONDS
        assert tokens_30d.expires_in == 2592000

        claims = auth_service.decode_token(tokens_30d.access_token)
        # exp - iat should be 2,592,000s
        assert claims["exp"] - claims["iat"] == 2592000

        refresh_claims = auth_service.decode_token(tokens_30d.refresh_token)
        # refresh token should be 90 days = 7,776,000s
        assert refresh_claims["exp"] - refresh_claims["iat"] == 7776000

        # 2. remember_me = False -> Standard access token lifetime
        tokens_std = auth_service.create_tokens_for_user(mock_user, remember_me=False)
        assert tokens_std.expires_in == settings.ACCESS_TOKEN_EXPIRE_SECONDS

    await engine.dispose()


# ==============================================================================
# Task 4: Endpoints POST /verify-email & /resend-verification Tests
# ==============================================================================
@pytest.mark.asyncio
async def test_verify_email_and_resend_verification_endpoints() -> None:
    """Test end-to-end email verification with OTP and token via HTTP API."""
    async with auth2_test_context() as (client, session_maker):
        # 1. Register new researcher
        reg_payload = {
            "full_name": "Dr. Marie Curie",
            "email": "marie.curie@sorbonne.edu",
            "password": "RadiumPassword2026!",
            "institution": "Sorbonne University",
            "accept_terms": True,
        }
        res_reg = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res_reg.status_code == 201
        reg_data = res_reg.json()
        assert reg_data["success"] is True
        otp_code = reg_data["data"].get("verification_code_debug")
        assert otp_code is not None
        assert len(otp_code) == 6

        # Check DB user initially unverified
        async with session_maker() as session:
            stmt = select(UserModel).where(UserModel.email == "marie.curie@sorbonne.edu")
            user = (await session.execute(stmt)).scalar_one()
            assert user.is_verified is False

        # 2. Negative test: verify with wrong OTP code (400)
        wrong_res = await client.post(
            "/api/v1/auth/verify-email",
            json={"email": "marie.curie@sorbonne.edu", "code": "000000"},
        )
        assert wrong_res.status_code == 400
        assert wrong_res.json()["success"] is False

        # 3. Positive test: verify with correct 6-digit OTP code (200)
        verify_res = await client.post(
            "/api/v1/auth/verify-email",
            json={"email": "marie.curie@sorbonne.edu", "code": otp_code},
        )
        assert verify_res.status_code == 200
        assert verify_res.json()["success"] is True

        # Check DB user is now verified
        async with session_maker() as session:
            stmt = select(UserModel).where(UserModel.email == "marie.curie@sorbonne.edu")
            user = (await session.execute(stmt)).scalar_one()
            assert user.is_verified is True

        # 4. Test POST /api/v1/auth/resend-verification
        resend_res = await client.post(
            "/api/v1/auth/resend-verification",
            json={"email": "marie.curie@sorbonne.edu"},
        )
        assert resend_res.status_code == 200
        assert resend_res.json()["success"] is True

        # 5. Negative test: resend to nonexistent email (404)
        not_found_res = await client.post(
            "/api/v1/auth/resend-verification",
            json={"email": "ghost@university.edu"},
        )
        assert not_found_res.status_code == 404


# ==============================================================================
# Task 6: Endpoint HTTP 422 Rejection for Maxxspace & Non-Whitelisted Domains
# ==============================================================================
@pytest.mark.asyncio
async def test_register_endpoint_rejects_maxxspace_with_http_422() -> None:
    """End-to-End API Test: Prove that POST /api/v1/auth/register rejects maxxspace.com

    with HTTP 422 Unprocessable Entity and returns actionable error feedback.
    """
    async with auth2_test_context() as (client, _):
        # 1. Attempt registration with maxxspace.com temp mail
        malicious_payload = {
            "full_name": "Temp Mail Spammer",
            "email": "attacker123@maxxspace.com",
            "password": "Password2026!#",
            "accept_terms": True,
        }
        res = await client.post("/api/v1/auth/register", json=malicious_payload)

        # Must strictly return HTTP 422 Unprocessable Content / Entity
        assert res.status_code == 422, f"Expected 422, got {res.status_code}: {res.text}"
        body = res.json()
        error_detail = str(body)
        assert (
            "maxxspace.com" in error_detail
            or "tạm thời" in error_detail
            or "không thuộc danh sách" in error_detail
        )

        # 2. Attempt registration with arbitrary non-whitelisted commercial domain
        arbitrary_payload = {
            "full_name": "Random Corp User",
            "email": "user@randomcommercialdomain.com",
            "password": "Password2026!#",
            "accept_terms": True,
        }
        res_arb = await client.post("/api/v1/auth/register", json=arbitrary_payload)
        assert res_arb.status_code == 422, f"Expected 422 for arbitrary domain: {res_arb.text}"

        # 3. Confirm legitimate academic email (.edu.vn) succeeds (201 Created)
        legit_payload = {
            "full_name": "Prof. Nguyen Van An",
            "email": "an.nguyen@vnu.edu.vn",
            "password": "ValidScholarly2026!",
            "institution": "Vietnam National University",
            "accept_terms": True,
        }
        res_legit = await client.post("/api/v1/auth/register", json=legit_payload)
        assert res_legit.status_code == 201, f"Expected 201, got {res_legit.status_code}"
        legit_data = res_legit.json()
        assert legit_data["success"] is True
        # Verify debug code is provided for UAT/Dev
        assert legit_data["data"]["verification_code_debug"] is not None


# ==============================================================================
# Task 7: Resend API Delivery & Priority Fallback Hierarchy Tests
# ==============================================================================
@pytest.mark.asyncio
async def test_email_service_resend_integration_and_priority_fallback() -> None:
    """Verify EmailService initializes Resend credentials and executes priority dispatch."""
    svc = EmailService()
    assert svc.resend_from_email == "onboarding@resend.dev"

    # 1. Test dispatch to delivered@resend.dev via real or fallback Resend API
    sent = await svc.send_verification_email(
        email="delivered@resend.dev",
        code="654321",
        token="mock.jwt.verify.token",
    )
    assert sent is True

    # 2. Test password reset dispatch via Resend
    reset_sent = await svc.send_password_reset_email(
        email="delivered@resend.dev",
        code="654321",
        token="mock.jwt.reset.token",
    )
    assert reset_sent is True

    # 3. Verify audit log was recorded
    assert EMAIL_LOG_PATH.exists()
    content = EMAIL_LOG_PATH.read_text(encoding="utf-8")
    assert "delivered@resend.dev" in content
    assert "654321" in content


TEST_GOOGLE_CLIENT_ID = "1006802584657-6nope0a7s81th2b8aumt7no6l5nccd48.apps.googleusercontent.com"


# ==============================================================================
# Task 8: Google OAuth 2.0 Authentication & Provisioning Tests
# ==============================================================================
@pytest.mark.asyncio
async def test_google_auth_new_user_provisioning_and_tokens() -> None:
    """Verify Google OAuth provisions a new verified researcher account and returns 30-day tokens."""
    # Test schema validation
    req = GoogleAuthRequest(id_token="valid.google.id.token.xyz")
    assert req.id_token == "valid.google.id.token.xyz"
    with pytest.raises(ValidationError):
        GoogleAuthRequest(id_token="")

    client_id = settings.GOOGLE_CLIENT_ID or TEST_GOOGLE_CLIENT_ID

    async with auth2_test_context() as (client, session_maker):
        google_payload = {
            "iss": "https://accounts.google.com",
            "sub": "google-uid-1001",
            "aud": client_id,
            "email": "dr.alan.turing@cam.ac.uk",
            "email_verified": "true",
            "name": "Dr. Alan Turing",
            "picture": "https://lh3.googleusercontent.com/turing.png",
        }

        mock_resp = httpx.Response(200, json=google_payload)
        with (
            patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get,
            patch.object(settings, "GOOGLE_CLIENT_ID", client_id),
        ):
            mock_get.return_value = mock_resp

            res = await client.post(
                "/api/v1/auth/google",
                json={"id_token": "valid.google.id.token.xyz"},
            )

            assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
            data = res.json()
            assert data["success"] is True
            user_data = data["data"]["user"]
            tokens_data = data["data"]["tokens"]

            assert user_data["email"] == "dr.alan.turing@cam.ac.uk"
            assert user_data["full_name"] == "Dr. Alan Turing"
            assert user_data["avatar_url"] == "https://lh3.googleusercontent.com/turing.png"
            assert user_data["is_verified"] is True
            assert user_data["role"] == "researcher"

            assert tokens_data["access_token"]
            assert tokens_data["refresh_token"]
            assert tokens_data["expires_in"] == settings.REMEMBER_ME_ACCESS_TOKEN_EXPIRE_SECONDS

        # Verify persisted in database
        async with session_maker() as session:
            stmt = select(UserModel).where(UserModel.email == "dr.alan.turing@cam.ac.uk")
            res_db = await session.execute(stmt)
            persisted = res_db.scalar_one_or_none()
            assert persisted is not None
            assert persisted.is_verified is True
            assert persisted.avatar_url == "https://lh3.googleusercontent.com/turing.png"


@pytest.mark.asyncio
async def test_google_auth_existing_user_auto_verify() -> None:
    """Verify Google OAuth links to existing account and marks unverified accounts as verified."""
    client_id = settings.GOOGLE_CLIENT_ID or TEST_GOOGLE_CLIENT_ID

    async with auth2_test_context() as (client, session_maker):
        # Seed unverified user in database
        async with session_maker() as session:
            existing = UserModel(
                id=UUID("550e8400-e29b-41d4-a716-446655440000"),
                email="ada.lovelace@ox.ac.uk",
                full_name="Ada Lovelace",
                hashed_password=AuthService.hash_password("ExistingSecret123!"),
                role="researcher",
                is_active=True,
                is_verified=False,
                avatar_url=None,
            )
            session.add(existing)
            await session.commit()

        google_payload = {
            "iss": "https://accounts.google.com",
            "sub": "google-uid-1002",
            "aud": client_id,
            "email": "ada.lovelace@ox.ac.uk",
            "email_verified": True,
            "name": "Countess Ada Lovelace",
            "picture": "https://lh3.googleusercontent.com/ada.png",
        }

        mock_resp = httpx.Response(200, json=google_payload)
        with (
            patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get,
            patch.object(settings, "GOOGLE_CLIENT_ID", client_id),
        ):
            mock_get.return_value = mock_resp

            res = await client.post(
                "/api/v1/auth/google",
                json={"id_token": "valid.google.id.token.ada"},
            )

            assert res.status_code == 200
            data = res.json()
            assert data["data"]["user"]["is_verified"] is True
            assert data["data"]["user"]["avatar_url"] == "https://lh3.googleusercontent.com/ada.png"

        # Verify database record updated
        async with session_maker() as session:
            stmt = select(UserModel).where(UserModel.email == "ada.lovelace@ox.ac.uk")
            res_db = await session.execute(stmt)
            user_db = res_db.scalar_one_or_none()
            assert user_db is not None
            assert user_db.is_verified is True
            assert user_db.avatar_url == "https://lh3.googleusercontent.com/ada.png"


@pytest.mark.asyncio
async def test_google_auth_invalid_token_rejected_with_401() -> None:
    """Verify invalid or expired Google ID tokens return HTTP 401 Unauthorized."""
    async with auth2_test_context() as (client, _):
        mock_resp = httpx.Response(
            400, json={"error": "invalid_token", "error_description": "Invalid Value"}
        )
        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp

            res = await client.post(
                "/api/v1/auth/google",
                json={"id_token": "expired_or_forged_token"},
            )

            assert res.status_code == 401
            data = res.json()
            assert "Token Google không hợp lệ hoặc đã hết hạn" in str(data)


@pytest.mark.asyncio
async def test_google_auth_unverified_google_email_rejected_with_400() -> None:
    """Verify unverified Google emails return HTTP 400 Bad Request."""
    client_id = settings.GOOGLE_CLIENT_ID or TEST_GOOGLE_CLIENT_ID

    async with auth2_test_context() as (client, _):
        google_payload = {
            "iss": "https://accounts.google.com",
            "sub": "google-uid-1003",
            "aud": client_id,
            "email": "unverified.researcher@gmail.com",
            "email_verified": "false",
            "name": "Unverified User",
        }
        mock_resp = httpx.Response(200, json=google_payload)
        with (
            patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get,
            patch.object(settings, "GOOGLE_CLIENT_ID", client_id),
        ):
            mock_get.return_value = mock_resp

            res = await client.post(
                "/api/v1/auth/google",
                json={"id_token": "token_with_unverified_email"},
            )

            assert res.status_code == 400
            data = res.json()
            assert "Email Google chưa được xác thực" in str(data)


@pytest.mark.asyncio
async def test_google_auth_disposable_domain_rejected_with_422() -> None:
    """Verify strict whitelist blocks disposable/unapproved domains even through Google OAuth."""
    client_id = settings.GOOGLE_CLIENT_ID or TEST_GOOGLE_CLIENT_ID

    async with auth2_test_context() as (client, _):
        google_payload = {
            "iss": "https://accounts.google.com",
            "sub": "google-uid-1004",
            "aud": client_id,
            "email": "attacker@maxxspace.com",
            "email_verified": "true",
            "name": "Attacker via Google",
        }
        mock_resp = httpx.Response(200, json=google_payload)
        with (
            patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get,
            patch.object(settings, "GOOGLE_CLIENT_ID", client_id),
        ):
            mock_get.return_value = mock_resp

            res = await client.post(
                "/api/v1/auth/google",
                json={"id_token": "token_with_maxxspace"},
            )

            assert res.status_code == 422
            data = res.json()
            assert "maxxspace.com" in str(data) or "tạm thời" in str(data)


@pytest.mark.asyncio
async def test_google_auth_audience_mismatch_rejected_with_401() -> None:
    """Verify OIDC Confused Deputy Attack is blocked when token audience doesn't match client id."""
    async with auth2_test_context() as (client, _):
        # Attacker generated token intended for a different rogue application
        google_payload = {
            "iss": "https://accounts.google.com",
            "sub": "google-uid-1005",
            "aud": "attacker-rogue-app.apps.googleusercontent.com",
            "email": "victim.researcher@cam.ac.uk",
            "email_verified": "true",
            "name": "Victim Researcher",
        }
        mock_resp = httpx.Response(200, json=google_payload)
        with (
            patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get,
            patch.object(settings, "GOOGLE_CLIENT_ID", TEST_GOOGLE_CLIENT_ID),
        ):
            mock_get.return_value = mock_resp

            res = await client.post(
                "/api/v1/auth/google",
                json={"id_token": "token_with_attacker_audience"},
            )

            assert res.status_code == 401
            data = res.json()
            assert "Token Google không hợp lệ hoặc audience không khớp với ứng dụng." in str(data)


@pytest.mark.asyncio
async def test_google_auth_unconfigured_client_id_rejected_with_401() -> None:
    """Verify Google auth fails securely when server GOOGLE_CLIENT_ID is unconfigured."""
    async with auth2_test_context() as (client, _):
        google_payload = {
            "iss": "https://accounts.google.com",
            "sub": "google-uid-1006",
            "aud": "some-random-id.apps.googleusercontent.com",
            "email": "user@cam.ac.uk",
            "email_verified": "true",
            "name": "User",
        }
        mock_resp = httpx.Response(200, json=google_payload)
        with (
            patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get,
            patch.object(settings, "GOOGLE_CLIENT_ID", ""),
        ):
            mock_get.return_value = mock_resp

            res = await client.post(
                "/api/v1/auth/google",
                json={"id_token": "token_when_unconfigured"},
            )

            assert res.status_code == 401
            data = res.json()
            assert "Token Google không hợp lệ hoặc audience không khớp với ứng dụng." in str(data)


# ==============================================================================
# Task 9: Scholar Profile & Academic Identity Upgrade Tests
# ==============================================================================
@pytest.mark.asyncio
async def test_update_profile_with_scholarly_metadata() -> None:
    """Verify updating scholar bio, research_interests, google_scholar_url, and department."""
    # 1. Test schema validation
    req = UpdateProfileRequest(
        department="Department of Physics",
        bio="Theoretical physicist studying quantum field theory.",
        research_interests="Quantum Field Theory, General Relativity",
        google_scholar_url="https://scholar.google.com/citations?user=einstein123",
    )
    assert req.department == "Department of Physics"
    assert req.bio == "Theoretical physicist studying quantum field theory."
    assert req.research_interests == "Quantum Field Theory, General Relativity"
    assert req.google_scholar_url == "https://scholar.google.com/citations?user=einstein123"

    # 2. Test HTTP API PATCH /api/v1/auth/me
    async with auth2_test_context() as (client, session_maker):
        # Register new scholar account
        reg_payload = {
            "full_name": "Prof. Albert Einstein",
            "email": "albert.einstein@princeton.edu",
            "password": "Relativity2026!#",
            "institution": "Princeton University",
            "accept_terms": True,
        }
        res_reg = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res_reg.status_code == 201
        tokens = res_reg.json()["data"]["tokens"]
        access_token = tokens["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # Update profile with academic identity metadata
        patch_payload = {
            "department": "Department of Physics & Advanced Study",
            "bio": "Theoretical physicist investigating quantum mechanics and unified field theory.",
            "research_interests": "General Relativity, Quantum Mechanics, Unified Field Theory",
            "google_scholar_url": "https://scholar.google.com/citations?user=einstein123",
            "academic_rank": "Giáo sư Vật lý Lý thuyết",
        }
        res_patch = await client.patch("/api/v1/auth/me", json=patch_payload, headers=headers)
        assert res_patch.status_code == 200, (
            f"Expected 200, got {res_patch.status_code}: {res_patch.text}"
        )
        data = res_patch.json()
        assert data["success"] is True
        profile = data["data"]

        # Validate schema fields
        assert profile["department"] == "Department of Physics & Advanced Study"
        assert (
            profile["bio"]
            == "Theoretical physicist investigating quantum mechanics and unified field theory."
        )
        assert (
            profile["research_interests"]
            == "General Relativity, Quantum Mechanics, Unified Field Theory"
        )
        assert (
            profile["google_scholar_url"] == "https://scholar.google.com/citations?user=einstein123"
        )
        assert profile["academic_rank"] == "Giáo sư Vật lý Lý thuyết"
        assert profile["institution"] == "Princeton University"
        assert profile["email"] == "albert.einstein@princeton.edu"

        # Verify GET /api/v1/auth/me returns updated metadata
        res_get = await client.get("/api/v1/auth/me", headers=headers)
        assert res_get.status_code == 200
        get_profile = res_get.json()["data"]
        assert get_profile["department"] == "Department of Physics & Advanced Study"
        assert get_profile["bio"] == profile["bio"]
        assert get_profile["research_interests"] == profile["research_interests"]
        assert get_profile["google_scholar_url"] == profile["google_scholar_url"]

        # Verify database record persisted correctly
        async with session_maker() as session:
            stmt = select(UserModel).where(UserModel.email == "albert.einstein@princeton.edu")
            res_db = await session.execute(stmt)
            user_db = res_db.scalar_one_or_none()
            assert user_db is not None
            assert user_db.department == "Department of Physics & Advanced Study"
            assert user_db.bio == profile["bio"]
            assert user_db.research_interests == profile["research_interests"]
            assert user_db.google_scholar_url == profile["google_scholar_url"]

            # Validate UserProfileResponse schema
            user_response = UserProfileResponse.model_validate(user_db)
            assert user_response.department == "Department of Physics & Advanced Study"
            assert user_response.bio == profile["bio"]
            assert user_response.research_interests == profile["research_interests"]
            assert user_response.google_scholar_url == profile["google_scholar_url"]


# ==============================================================================
# Task 10: Security Hardening, SQL Injection & Boundary Defenses
# ==============================================================================
@pytest.mark.asyncio
async def test_security_sql_injection_defense_in_scholar_metadata() -> None:
    """Verify SQL injection payloads in profile metadata are safely parameterized and harmless."""
    async with auth2_test_context() as (client, session_maker):
        # Register user
        reg_payload = {
            "full_name": "Dr. SQL Defense Tester",
            "email": "sqldefense@mit.edu",
            "password": "SecurePassword2026!#",
            "accept_terms": True,
        }
        res_reg = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res_reg.status_code == 201
        token = res_reg.json()["data"]["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Malicious SQL injection payloads in metadata fields
        sql_injection_payload = {
            "department": "Computer Science'; DROP TABLE users; --",
            "bio": "' UNION SELECT id, email, hashed_password FROM users WHERE '1'='1",
            "research_interests": "AI Safety'; DELETE FROM users WHERE email LIKE '%'; --",
            "academic_rank": "' OR 1=1 --",
        }
        res_patch = await client.patch(
            "/api/v1/auth/me", json=sql_injection_payload, headers=headers
        )
        assert res_patch.status_code == 200
        patch_data = res_patch.json()["data"]

        # Ensure strings were safely escaped and preserved verbatim without SQL execution
        assert patch_data["department"] == "Computer Science'; DROP TABLE users; --"
        assert (
            patch_data["bio"] == "' UNION SELECT id, email, hashed_password FROM users WHERE '1'='1"
        )
        assert (
            patch_data["research_interests"]
            == "AI Safety'; DELETE FROM users WHERE email LIKE '%'; --"
        )

        # Verify DB users table still exists and data is intact
        async with session_maker() as session:
            stmt = select(UserModel).where(UserModel.email == "sqldefense@mit.edu")
            res_db = await session.execute(stmt)
            user_db = res_db.scalar_one_or_none()
            assert user_db is not None
            assert user_db.department == "Computer Science'; DROP TABLE users; --"
            assert (
                user_db.bio == "' UNION SELECT id, email, hashed_password FROM users WHERE '1'='1"
            )


@pytest.mark.asyncio
async def test_security_xss_and_boundary_defense_in_scholar_metadata() -> None:
    """Verify XSS payloads and length boundary violations are strictly validated."""
    async with auth2_test_context() as (client, session_maker):
        reg_payload = {
            "full_name": "Dr. Boundary Checker",
            "email": "boundary@oxford.ac.uk",
            "password": "SecurePassword2026!#",
            "accept_terms": True,
        }
        res_reg = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res_reg.status_code == 201
        token = res_reg.json()["data"]["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Stored XSS scripts are safely accepted as plain text strings without interpretation
        xss_payload = {
            "bio": "<script>alert('XSS Attack');</script>",
            "research_interests": "<img src=x onerror=alert(1)>",
        }
        res_xss = await client.patch("/api/v1/auth/me", json=xss_payload, headers=headers)
        assert res_xss.status_code == 200
        assert res_xss.json()["data"]["bio"] == "<script>alert('XSS Attack');</script>"
        assert res_xss.json()["data"]["research_interests"] == "<img src=x onerror=alert(1)>"

        # 2. Oversized bio (> 1000 characters) must trigger 422 Unprocessable Entity
        huge_bio = "A" * 1001
        res_huge_bio = await client.patch(
            "/api/v1/auth/me", json={"bio": huge_bio}, headers=headers
        )
        assert res_huge_bio.status_code == 422

        # 3. Oversized department (> 255 characters) must trigger 422
        huge_dept = "D" * 256
        res_huge_dept = await client.patch(
            "/api/v1/auth/me", json={"department": huge_dept}, headers=headers
        )
        assert res_huge_dept.status_code == 422


@pytest.mark.asyncio
async def test_security_role_escalation_defense() -> None:
    """Verify that researchers cannot escalate role to admin or superadmin via profile update."""
    async with auth2_test_context() as (client, session_maker):
        reg_payload = {
            "full_name": "Dr. Regular Researcher",
            "email": "regular@harvard.edu",
            "password": "SecurePassword2026!#",
            "accept_terms": True,
        }
        res_reg = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res_reg.status_code == 201
        token = res_reg.json()["data"]["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Attempt to inject role: admin in profile update
        res_escalate = await client.patch(
            "/api/v1/auth/me",
            json={"department": "Security Lab", "role": "admin", "is_superuser": True},
            headers=headers,
        )
        assert res_escalate.status_code == 200
        profile = res_escalate.json()["data"]
        # Role must remain researcher
        assert profile["role"] == "researcher"

        # Verify in DB
        async with session_maker() as session:
            stmt = select(UserModel).where(UserModel.email == "regular@harvard.edu")
            res_db = await session.execute(stmt)
            user_db = res_db.scalar_one_or_none()
            assert user_db is not None
            assert user_db.role == "researcher"


@pytest.mark.asyncio
async def test_security_expired_and_forged_jwt_tokens() -> None:
    """Verify that expired, forged, or malformed JWT tokens are rejected with HTTP 401."""
    async with auth2_test_context() as (client, session_maker):
        # 1. No Authorization header -> 401
        res_no_auth = await client.get("/api/v1/auth/me")
        assert res_no_auth.status_code == 401

        # 2. Malformed token format -> 401
        res_malformed = await client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-valid-jwt-token"}
        )
        assert res_malformed.status_code == 401

        # 3. Forged signature token -> 401
        valid_token = AuthService.create_token(
            payload={"sub": str(uuid4()), "email": "hacker@evil.org", "role": "admin"},
            expires_delta_seconds=3600,
        )
        forged_token = valid_token[:-4] + "fake"
        res_forged = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {forged_token}"}
        )
        assert res_forged.status_code == 401

        # 4. Expired token (expires_delta_seconds=-3600) -> 401
        expired_token = AuthService.create_token(
            payload={"sub": str(uuid4()), "email": "expired@harvard.edu", "role": "researcher"},
            expires_delta_seconds=-3600,
        )
        res_expired = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert res_expired.status_code == 401
