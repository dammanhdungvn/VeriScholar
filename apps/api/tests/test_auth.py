"""Unit and Integration Test Suite for GitHub OAuth Authentication.

Covers:
1. POST /api/v1/auth/github with access_token payload provisioning new user.
2. POST /api/v1/auth/github with authorization code exchange provisioning new user.
3. POST /api/v1/auth/github with redirect_uri during code exchange.
4. User linking with existing unverified account and avatar synchronization.
5. Email privacy resolution via https://api.github.com/user/emails API.
6. Validation and rejection of unverified GitHub emails (HTTP 400).
7. Validation and rejection of disposable / untrusted email domains (HTTP 422).
8. Validation and rejection of inactive scholar accounts (HTTP 401).
9. Validation and rejection of invalid / expired authorization codes (HTTP 401).
10. Validation and rejection of invalid / expired access tokens (HTTP 401).
11. Handling network errors and upstream timeout gracefully (HTTP 401).
12. Schema validation for missing credentials (code / access_token) (HTTP 422).
13. Unconfigured GitHub client credentials rejection (HTTP 401).
14. Direct AuthService.authenticate_github invocation tests.
"""

from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from unittest.mock import patch
from uuid import UUID

import httpx
import pytest
from api import app
from api.core.config import settings
from api.db.models.base import Base
from api.db.models.user import UserModel
from api.db.session import get_db
from api.schemas.auth import GitHubAuthRequest
from api.services.auth_service import AuthService
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
TEST_GITHUB_CLIENT_ID = "gh_test_client_id_2026"
TEST_GITHUB_CLIENT_SECRET = "gh_test_client_secret_super_secure"

_ORIGINAL_HTTPX_GET = httpx.AsyncClient.get
_ORIGINAL_HTTPX_POST = httpx.AsyncClient.post


@asynccontextmanager
async def github_test_context() -> AsyncGenerator[
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


def patch_github_http(
    get_handler: Callable[[str], httpx.Response] | httpx.Response | None = None,
    post_handler: Callable[[str, dict], httpx.Response] | httpx.Response | None = None,
):
    """Context manager to intercept outbound HTTP calls to github.com while keeping ASGI client intact."""

    async def mocked_get(self: httpx.AsyncClient, url: str, *args, **kwargs):
        if "github.com" in str(url):
            if isinstance(get_handler, Exception):
                raise get_handler
            if callable(get_handler):
                return get_handler(str(url))
            if get_handler is not None:
                return get_handler
        return await _ORIGINAL_HTTPX_GET(self, url, *args, **kwargs)

    async def mocked_post(self: httpx.AsyncClient, url: str, *args, **kwargs):
        if "github.com" in str(url):
            if isinstance(post_handler, Exception):
                raise post_handler
            if callable(post_handler):
                return post_handler(str(url), kwargs.get("json", {}))
            if post_handler is not None:
                return post_handler
        return await _ORIGINAL_HTTPX_POST(self, url, *args, **kwargs)

    return (
        patch.object(httpx.AsyncClient, "get", mocked_get),
        patch.object(httpx.AsyncClient, "post", mocked_post),
    )


# ==============================================================================
# 1. Pydantic Schema Validation Tests
# ==============================================================================
def test_github_auth_request_schema_validation() -> None:
    """Verify GitHubAuthRequest accepts valid payload shapes and rejects empty ones."""
    # Valid with code
    req_code = GitHubAuthRequest(code="gh_code_123")
    assert req_code.code == "gh_code_123"
    assert req_code.redirect_uri is None
    assert req_code.access_token is None

    # Valid with code + redirect_uri
    req_code_redirect = GitHubAuthRequest(
        code="gh_code_123", redirect_uri="https://verischolar.org/oauth/callback"
    )
    assert req_code_redirect.code == "gh_code_123"
    assert req_code_redirect.redirect_uri == "https://verischolar.org/oauth/callback"

    # Valid with access_token
    req_token = GitHubAuthRequest(access_token="gho_test_access_token")
    assert req_token.access_token == "gho_test_access_token"
    assert req_token.code is None

    # Invalid when both code and access_token are missing
    with pytest.raises(ValidationError) as exc_info:
        GitHubAuthRequest()
    assert "code" in str(exc_info.value) or "access_token" in str(exc_info.value)

    # Invalid when empty strings provided
    with pytest.raises(ValidationError):
        GitHubAuthRequest(code="   ", access_token="")


# ==============================================================================
# 2. GitHub Auth via access_token Tests
# ==============================================================================
@pytest.mark.asyncio
async def test_github_auth_with_access_token_provisions_new_user() -> None:
    """Verify POST /api/v1/auth/github provisions a new scholar with valid access_token."""
    github_user_data = {
        "login": "octocat",
        "name": "Octocat Scholar",
        "email": "octocat@mit.edu",
        "avatar_url": "https://avatars.githubusercontent.com/u/583231",
        "email_verified": True,
    }

    async with github_test_context() as (client, session_maker):
        mock_user_resp = httpx.Response(200, json=github_user_data)
        p_get, p_post = patch_github_http(get_handler=mock_user_resp)
        with p_get, p_post:
            res = await client.post(
                "/api/v1/auth/github",
                json={"access_token": "gho_valid_test_token_123"},
            )

            assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
            body = res.json()
            assert "data" in body
            user = body["data"]["user"]
            tokens = body["data"]["tokens"]

            assert user["email"] == "octocat@mit.edu"
            assert user["full_name"] == "Octocat Scholar"
            assert user["avatar_url"] == "https://avatars.githubusercontent.com/u/583231"
            assert user["is_verified"] is True
            assert user["role"] == "researcher"

            assert tokens["access_token"]
            assert tokens["refresh_token"]
            assert tokens["token_type"] == "bearer"

        # Verify database record
        async with session_maker() as session:
            stmt = select(UserModel).where(UserModel.email == "octocat@mit.edu")
            res_db = await session.execute(stmt)
            user_db = res_db.scalar_one_or_none()
            assert user_db is not None
            assert user_db.full_name == "Octocat Scholar"
            assert user_db.is_verified is True
            assert user_db.avatar_url == "https://avatars.githubusercontent.com/u/583231"


# ==============================================================================
# 3. GitHub Auth via Authorization Code Exchange Tests
# ==============================================================================
@pytest.mark.asyncio
async def test_github_auth_with_code_exchange_provisions_new_user() -> None:
    """Verify POST /api/v1/auth/github exchanges code for token and provisions scholar."""
    exchange_response = {
        "access_token": "gho_exchanged_token_999",
        "token_type": "bearer",
        "scope": "read:user,user:email",
    }
    github_user_data = {
        "login": "torvalds",
        "name": "Linus Torvalds",
        "email": "torvalds@helsinki.edu",
        "avatar_url": "https://avatars.githubusercontent.com/u/1024",
    }

    recorded_exchange: dict[str, str] = {}

    def handle_post(url: str, payload: dict) -> httpx.Response:
        recorded_exchange.update(payload)
        return httpx.Response(200, json=exchange_response)

    async with github_test_context() as (client, session_maker):
        p_get, p_post = patch_github_http(
            get_handler=httpx.Response(200, json=github_user_data),
            post_handler=handle_post,
        )
        with (
            patch.object(settings, "GITHUB_CLIENT_ID", TEST_GITHUB_CLIENT_ID),
            patch.object(settings, "GITHUB_CLIENT_SECRET", TEST_GITHUB_CLIENT_SECRET),
            p_get,
            p_post,
        ):
            res = await client.post(
                "/api/v1/auth/github",
                json={
                    "code": "auth_code_from_oauth_callback",
                    "redirect_uri": "https://verischolar.org/oauth/callback",
                },
            )

            assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
            body = res.json()
            user = body["data"]["user"]
            tokens = body["data"]["tokens"]

            assert user["email"] == "torvalds@helsinki.edu"
            assert user["full_name"] == "Linus Torvalds"
            assert user["is_verified"] is True
            assert tokens["access_token"]

            # Verify exchange request payload
            assert recorded_exchange["client_id"] == TEST_GITHUB_CLIENT_ID
            assert recorded_exchange["client_secret"] == TEST_GITHUB_CLIENT_SECRET
            assert recorded_exchange["code"] == "auth_code_from_oauth_callback"
            assert recorded_exchange["redirect_uri"] == "https://verischolar.org/oauth/callback"


# ==============================================================================
# 4. User Linking & Avatar Synchronization Tests
# ==============================================================================
@pytest.mark.asyncio
async def test_github_auth_links_with_existing_unverified_user() -> None:
    """Verify GitHub auth links to existing account, marks verified and adds avatar."""
    async with github_test_context() as (client, session_maker):
        # Pre-seed unverified user in database
        async with session_maker() as session:
            existing = UserModel(
                id=UUID("550e8400-e29b-41d4-a716-446655440001"),
                email="ada.lovelace@ox.ac.uk",
                full_name="Ada Lovelace",
                hashed_password=AuthService.hash_password("ExistingPassword123!"),
                role="researcher",
                is_active=True,
                is_verified=False,
                avatar_url=None,
            )
            session.add(existing)
            await session.commit()

        github_user_data = {
            "login": "ada",
            "name": "Countess Ada Lovelace",
            "email": "ada.lovelace@ox.ac.uk",
            "avatar_url": "https://avatars.githubusercontent.com/u/ada_lovelace",
        }

        p_get, p_post = patch_github_http(get_handler=httpx.Response(200, json=github_user_data))
        with p_get, p_post:
            res = await client.post(
                "/api/v1/auth/github",
                json={"access_token": "gho_valid_ada_token"},
            )

            assert res.status_code == 200
            user = res.json()["data"]["user"]
            assert user["id"] == "550e8400-e29b-41d4-a716-446655440001"
            assert user["is_verified"] is True
            assert user["avatar_url"] == "https://avatars.githubusercontent.com/u/ada_lovelace"

        # Verify database record updated
        async with session_maker() as session:
            stmt = select(UserModel).where(UserModel.email == "ada.lovelace@ox.ac.uk")
            res_db = await session.execute(stmt)
            user_db = res_db.scalar_one_or_none()
            assert user_db is not None
            assert user_db.is_verified is True
            assert user_db.avatar_url == "https://avatars.githubusercontent.com/u/ada_lovelace"


@pytest.mark.asyncio
async def test_github_auth_retains_existing_avatar_if_already_set() -> None:
    """Verify existing scholar avatar is preserved if already set."""
    async with github_test_context() as (client, session_maker):
        async with session_maker() as session:
            existing = UserModel(
                id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                email="scholar@stanford.edu",
                full_name="Stanford Scholar",
                hashed_password=AuthService.hash_password("Pass123!"),
                role="researcher",
                is_active=True,
                is_verified=True,
                avatar_url="https://custom-avatar.stanford.edu/pic.jpg",
            )
            session.add(existing)
            await session.commit()

        github_user_data = {
            "login": "stanfordscholar",
            "name": "Stanford Scholar",
            "email": "scholar@stanford.edu",
            "avatar_url": "https://avatars.githubusercontent.com/u/new_gh_pic",
        }

        p_get, p_post = patch_github_http(get_handler=httpx.Response(200, json=github_user_data))
        with p_get, p_post:
            res = await client.post(
                "/api/v1/auth/github",
                json={"access_token": "gho_valid_token_avatar"},
            )
            assert res.status_code == 200
            user = res.json()["data"]["user"]
            assert user["avatar_url"] == "https://custom-avatar.stanford.edu/pic.jpg"


# ==============================================================================
# 5. Private Email Resolution via /user/emails API Tests
# ==============================================================================
@pytest.mark.asyncio
async def test_github_auth_resolves_private_email_via_user_emails() -> None:
    """Verify private email is queried from /user/emails and primary verified email chosen."""
    github_user_data = {
        "login": "private_user",
        "name": "Private Scholar",
        "email": None,  # Email is private in GitHub user profile
        "avatar_url": "https://avatars.githubusercontent.com/u/999",
    }
    github_emails_data = [
        {"email": "unverified@unverified.org", "primary": False, "verified": False},
        {"email": "primary.scholar@cam.ac.uk", "primary": True, "verified": True},
        {"email": "backup@gmail.com", "primary": False, "verified": True},
    ]

    def handle_get(url: str) -> httpx.Response:
        if "user/emails" in url:
            return httpx.Response(200, json=github_emails_data)
        return httpx.Response(200, json=github_user_data)

    async with github_test_context() as (client, session_maker):
        p_get, p_post = patch_github_http(get_handler=handle_get)
        with p_get, p_post:
            res = await client.post(
                "/api/v1/auth/github",
                json={"access_token": "gho_valid_token_private_email"},
            )

            assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
            user = res.json()["data"]["user"]
            assert user["email"] == "primary.scholar@cam.ac.uk"
            assert user["full_name"] == "Private Scholar"


@pytest.mark.asyncio
async def test_github_auth_unverified_emails_in_list_rejected_with_400() -> None:
    """Verify HTTP 400 when all emails from /user/emails are unverified."""
    github_user_data = {
        "login": "unverified_dev",
        "name": "Unverified Dev",
        "email": None,
    }
    github_emails_data = [
        {"email": "candidate1@cam.ac.uk", "primary": True, "verified": False},
        {"email": "candidate2@ox.ac.uk", "primary": False, "verified": False},
    ]

    def handle_get(url: str) -> httpx.Response:
        if "user/emails" in url:
            return httpx.Response(200, json=github_emails_data)
        return httpx.Response(200, json=github_user_data)

    async with github_test_context() as (client, _):
        p_get, p_post = patch_github_http(get_handler=handle_get)
        with p_get, p_post:
            res = await client.post(
                "/api/v1/auth/github",
                json={"access_token": "gho_unverified_emails_list"},
            )
            assert res.status_code == 400
            assert "chưa được xác thực" in res.text


# ==============================================================================
# 6. Error & Security Hardening Tests
# ==============================================================================
@pytest.mark.asyncio
async def test_github_auth_unverified_email_field_rejected_with_400() -> None:
    """Verify HTTP 400 when GitHub user object explicitly specifies email_verified=False."""
    github_user_data = {
        "login": "bad_actor",
        "email": "bad_actor@cam.ac.uk",
        "email_verified": False,
    }

    async with github_test_context() as (client, _):
        p_get, p_post = patch_github_http(get_handler=httpx.Response(200, json=github_user_data))
        with p_get, p_post:
            res = await client.post(
                "/api/v1/auth/github",
                json={"access_token": "gho_unverified_field_token"},
            )
            assert res.status_code == 400
            assert "chưa được xác thực" in res.text


@pytest.mark.asyncio
async def test_github_auth_disposable_domain_rejected_with_422() -> None:
    """Verify strict whitelist blocks disposable or unapproved email domains (HTTP 422)."""
    disposable_samples = [
        "intruder@maxxspace.com",
        "bot@mailinator.com",
        "hacker@10minutemail.com",
    ]

    async with github_test_context() as (client, _):
        for bad_email in disposable_samples:
            github_user_data = {
                "login": "bad_user",
                "email": bad_email,
                "email_verified": True,
            }
            p_get, p_post = patch_github_http(
                get_handler=httpx.Response(200, json=github_user_data)
            )
            with p_get, p_post:
                res = await client.post(
                    "/api/v1/auth/github",
                    json={"access_token": "gho_bad_email_token"},
                )
                assert res.status_code == 422
                data = res.json()
                assert (
                    "INVALID_EMAIL_DOMAIN" in str(data)
                    or "tạm thời" in str(data)
                    or "không thuộc" in str(data)
                )


@pytest.mark.asyncio
async def test_github_auth_inactive_account_rejected_with_401() -> None:
    """Verify deactivated user accounts cannot authenticate via GitHub (HTTP 401)."""
    async with github_test_context() as (client, session_maker):
        async with session_maker() as session:
            inactive_user = UserModel(
                id=UUID("550e8400-e29b-41d4-a716-446655440003"),
                email="inactive.researcher@harvard.edu",
                full_name="Inactive Researcher",
                hashed_password=AuthService.hash_password("Pass123!"),
                role="researcher",
                is_active=False,
                is_verified=True,
            )
            session.add(inactive_user)
            await session.commit()

        github_user_data = {
            "login": "inactive_researcher",
            "email": "inactive.researcher@harvard.edu",
        }
        p_get, p_post = patch_github_http(get_handler=httpx.Response(200, json=github_user_data))
        with p_get, p_post:
            res = await client.post(
                "/api/v1/auth/github",
                json={"access_token": "gho_inactive_user_token"},
            )
            assert res.status_code == 401
            assert "ACCOUNT_INACTIVE" in str(res.json())


@pytest.mark.asyncio
async def test_github_auth_invalid_code_rejected_with_401() -> None:
    """Verify expired or bad authorization code from GitHub OAuth returns HTTP 401."""
    async with github_test_context() as (client, _):
        error_resp = {
            "error": "bad_verification_code",
            "error_description": "The code passed is incorrect or has expired.",
        }

        p_get, p_post = patch_github_http(post_handler=httpx.Response(200, json=error_resp))
        with (
            patch.object(settings, "GITHUB_CLIENT_ID", TEST_GITHUB_CLIENT_ID),
            patch.object(settings, "GITHUB_CLIENT_SECRET", TEST_GITHUB_CLIENT_SECRET),
            p_get,
            p_post,
        ):
            res = await client.post(
                "/api/v1/auth/github",
                json={"code": "expired_code_123"},
            )
            assert res.status_code == 401
            assert "incorrect or has expired" in str(res.json())


@pytest.mark.asyncio
async def test_github_auth_invalid_access_token_rejected_with_401() -> None:
    """Verify invalid or revoked GitHub access token returns HTTP 401."""
    async with github_test_context() as (client, _):
        p_get, p_post = patch_github_http(
            get_handler=httpx.Response(401, json={"message": "Bad credentials"})
        )
        with p_get, p_post:
            res = await client.post(
                "/api/v1/auth/github",
                json={"access_token": "invalid_access_token"},
            )
            assert res.status_code == 401
            assert "Token GitHub không hợp lệ hoặc đã hết hạn" in str(res.json())


@pytest.mark.asyncio
async def test_github_auth_unconfigured_client_credentials_rejected_with_401() -> None:
    """Verify code exchange fails with 401 when GITHUB_CLIENT_ID or SECRET is unconfigured."""
    async with github_test_context() as (client, _):
        with (
            patch.object(settings, "GITHUB_CLIENT_ID", ""),
            patch.object(settings, "GITHUB_CLIENT_SECRET", ""),
        ):
            res = await client.post(
                "/api/v1/auth/github",
                json={"code": "valid_looking_code"},
            )
            assert res.status_code == 401
            assert "chưa được cấu hình" in str(res.json())


@pytest.mark.asyncio
async def test_github_auth_network_failure_rejected_with_401() -> None:
    """Verify network connection timeout or failure to GitHub API returns HTTP 401."""
    async with github_test_context() as (client, _):
        p_get, p_post = patch_github_http(get_handler=httpx.ConnectTimeout("Connection timed out"))
        with p_get, p_post:
            res = await client.post(
                "/api/v1/auth/github",
                json={"access_token": "gho_network_fail_token"},
            )
            assert res.status_code == 401
            assert "Không thể kết nối" in str(res.json())


@pytest.mark.asyncio
async def test_github_auth_fallback_name_when_name_missing() -> None:
    """Verify username login or email prefix is used when name is missing from GitHub."""
    github_user_data = {
        "login": "researcher_alpha",
        "name": None,
        "email": "alpha@princeton.edu",
    }

    async with github_test_context() as (client, _):
        p_get, p_post = patch_github_http(get_handler=httpx.Response(200, json=github_user_data))
        with p_get, p_post:
            res = await client.post(
                "/api/v1/auth/github",
                json={"access_token": "gho_alpha_token"},
            )
            assert res.status_code == 200
            user = res.json()["data"]["user"]
            assert user["full_name"] == "researcher_alpha"


# ==============================================================================
# 7. Direct AuthService Method Invocation Tests
# ==============================================================================
@pytest.mark.asyncio
async def test_auth_service_authenticate_github_direct_call() -> None:
    """Verify direct invocation of AuthService.authenticate_github returns (UserModel, AuthTokensResponse)."""
    async with github_test_context() as (_, session_maker):
        async with session_maker() as session:
            auth_service = AuthService(db=session)

            github_user_data = {
                "login": "mariecurie",
                "name": "Marie Curie",
                "email": "marie.curie@sorbonne.ac.uk",
                "avatar_url": "https://avatars.githubusercontent.com/u/marie",
            }

            p_get, p_post = patch_github_http(
                get_handler=httpx.Response(200, json=github_user_data)
            )
            with p_get, p_post:
                user, tokens = await auth_service.authenticate_github(
                    access_token="gho_direct_call_token"
                )

                assert isinstance(user, UserModel)
                assert user.email == "marie.curie@sorbonne.ac.uk"
                assert user.full_name == "Marie Curie"
                assert user.is_verified is True
                assert tokens.access_token
                assert tokens.refresh_token
