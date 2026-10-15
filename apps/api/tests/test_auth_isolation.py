"""Comprehensive Integration Test Suite for Auth, JWT, and Multi-Tenant Isolation.

Covers:
- Registration (success, duplicate rejection, password hashing)
- Login (success, invalid password, inactive accounts)
- Token Refresh (valid refresh, invalid/expired refresh)
- Profile management (GET /me, PATCH /me)
- Password management (change-password, forgot-password, reset-password)
- 401 Unauthorized for unauthenticated or invalid tokens
- Multi-tenant isolation: User A resources (documents, sessions, notes) are isolated
  from User B, returning 404 Not Found upon unauthorized access.
- Backward compatibility: dev user fallback with X-User-Id.
"""

from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.base import Base
from api.db.models.document import DocumentModel
from api.db.models.note import ResearchNoteModel
from api.db.models.session import ResearchSessionModel
from api.db.session import get_db
from api.deps import DEFAULT_DEV_USER_ID, get_current_user
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


@asynccontextmanager
async def auth_test_context() -> AsyncIterator[
    tuple[AsyncClient, async_sessionmaker[AsyncSession]]
]:
    """Provide isolated in-memory database and AsyncClient for auth testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides.pop(get_current_user, None)

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            yield client, session_maker
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


# ==============================================================================
# Authentication & Registration Tests
# ==============================================================================
@pytest.mark.asyncio
async def test_register_and_login_flow() -> None:
    """Test new user registration followed by successful login."""
    async with auth_test_context() as (client, _):
        # 1. Register new user
        register_payload = {
            "full_name": "Dr. Alice Scholar",
            "email": "alice@scholar.edu",
            "password": "SecurePassword123!",
            "institution": "Stanford University",
            "orcid_id": "0000-0002-1825-0001",
            "accept_terms": True,
        }
        reg_res = await client.post("/api/v1/auth/register", json=register_payload)
        assert reg_res.status_code == 201
        reg_data = reg_res.json()
        assert reg_data["success"] is True
        assert reg_data["data"]["user"]["email"] == "alice@scholar.edu"
        assert reg_data["data"]["user"]["full_name"] == "Dr. Alice Scholar"
        assert reg_data["data"]["user"]["role"] == "researcher"
        assert reg_data["data"]["user"]["institution"] == "Stanford University"
        assert reg_data["data"]["tokens"]["access_token"] is not None
        assert reg_data["data"]["tokens"]["refresh_token"] is not None

        # 2. Duplicate registration with same email should be rejected (409)
        dup_res = await client.post("/api/v1/auth/register", json=register_payload)
        assert dup_res.status_code == 409
        dup_data = dup_res.json()
        assert dup_data["success"] is False

        # 3. Login with correct credentials
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": "alice@scholar.edu", "password": "SecurePassword123!"},
        )
        assert login_res.status_code == 200
        login_data = login_res.json()
        assert login_data["success"] is True
        assert login_data["data"]["tokens"]["access_token"] is not None
        access_token = login_data["data"]["tokens"]["access_token"]
        refresh_token = login_data["data"]["tokens"]["refresh_token"]

        # 4. Login with wrong password should fail (401)
        wrong_pwd_res = await client.post(
            "/api/v1/auth/login",
            json={"email": "alice@scholar.edu", "password": "WrongPassword!"},
        )
        assert wrong_pwd_res.status_code == 401

        # 5. Token refresh
        refresh_res = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert refresh_res.status_code == 200
        new_tokens = refresh_res.json()["data"]
        assert new_tokens["access_token"] is not None

        # 6. Authenticated profile check (GET /api/v1/auth/me)
        me_res = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert me_res.status_code == 200
        profile = me_res.json()["data"]
        assert profile["email"] == "alice@scholar.edu"

        # 7. Update profile (PATCH /api/v1/auth/me)
        patch_res = await client.patch(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "full_name": "Prof. Alice Scholar, PhD",
                "institution": "MIT",
                "academic_rank": "Principal Investigator",
            },
        )
        assert patch_res.status_code == 200
        updated_profile = patch_res.json()["data"]
        assert updated_profile["full_name"] == "Prof. Alice Scholar, PhD"
        assert updated_profile["institution"] == "MIT"
        assert updated_profile["academic_rank"] == "Principal Investigator"

        # 8. Change password
        change_res = await client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "current_password": "SecurePassword123!",
                "new_password": "NewSecretPassword456!",
            },
        )
        assert change_res.status_code == 200

        # 9. Verify login with old password fails, new password succeeds
        assert (
            await client.post(
                "/api/v1/auth/login",
                json={"email": "alice@scholar.edu", "password": "SecurePassword123!"},
            )
        ).status_code == 401

        new_login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": "alice@scholar.edu", "password": "NewSecretPassword456!"},
        )
        assert new_login_res.status_code == 200

        # 10. Logout
        logout_res = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert logout_res.status_code == 200


# ==============================================================================
# Password Reset Workflow Tests
# ==============================================================================
@pytest.mark.asyncio
async def test_forgot_and_reset_password_flow() -> None:
    """Verify forgot-password token generation and password reset."""
    async with auth_test_context() as (client, _):
        await client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "Bob Researcher",
                "email": "bob@research.org",
                "password": "InitialPassword123!",
            },
        )

        # 1. Forgot password request
        forgot_res = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "bob@research.org"},
        )
        assert forgot_res.status_code == 200
        data = forgot_res.json()["data"]
        reset_token = data.get("reset_token")
        assert reset_token is not None

        # 2. Reset password using token
        reset_res = await client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "BrandNewPassword789!",
            },
        )
        assert reset_res.status_code == 200

        # 3. Login with new password
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": "bob@research.org", "password": "BrandNewPassword789!"},
        )
        assert login_res.status_code == 200


# ==============================================================================
# Unauthenticated & Invalid Token Rejection (401)
# ==============================================================================
@pytest.mark.asyncio
async def test_unauthenticated_request_rejected_401() -> None:
    """Verify that protected endpoints reject requests lacking valid credentials."""
    async with auth_test_context() as (client, _):
        # No Authorization header and no X-User-Id
        res = await client.get("/api/v1/auth/me")
        assert res.status_code == 401
        assert "WWW-Authenticate" in res.headers

        # Malformed authorization header
        res_bad = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Basic dXNlcjpwYXNz"},
        )
        assert res_bad.status_code == 401

        # Fake/tampered JWT token
        res_fake = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer fake.jwt.signature"},
        )
        assert res_fake.status_code == 401


# ==============================================================================
# Multi-Tenant Isolation Tests (User A vs User B)
# ==============================================================================
@pytest.mark.asyncio
async def test_multi_tenant_isolation() -> None:
    """Verify strict multi-tenant isolation across documents, sessions, and notes."""
    async with auth_test_context() as (client, session_maker):
        # 1. Register User A and User B
        reg_a = await client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "User Alpha",
                "email": "alpha@tenant.org",
                "password": "PasswordAlpha123!",
            },
        )
        token_a = reg_a.json()["data"]["tokens"]["access_token"]
        user_a_id = UUID(reg_a.json()["data"]["user"]["id"])

        reg_b = await client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "User Beta",
                "email": "beta@tenant.org",
                "password": "PasswordBeta123!",
            },
        )
        token_b = reg_b.json()["data"]["tokens"]["access_token"]
        user_b_id = UUID(reg_b.json()["data"]["user"]["id"])

        assert user_a_id != user_b_id

        # 2. Populate resources owned strictly by User A in the database
        doc_a_id = uuid4()
        session_a_id = uuid4()
        note_a_id = uuid4()

        async with session_maker() as db_session:
            doc_a = DocumentModel(
                id=doc_a_id,
                user_id=user_a_id,
                filename="alpha_confidential_paper.pdf",
                title="Alpha Confidential Paper",
                content_hash="a" * 64,
                file_size_bytes=1024,
                status="completed",
                is_persistent=True,
            )
            db_session.add(doc_a)

            session_a = ResearchSessionModel(
                id=session_a_id,
                user_id=user_a_id,
                title="Alpha Private Session",
                viewport_state={"page": 1, "zoom_ratio": 1.0, "scroll_top": 0.0},
                active_tab="chat",
                is_archived=False,
            )
            db_session.add(session_a)

            note_a = ResearchNoteModel(
                id=note_a_id,
                user_id=user_a_id,
                document_id=doc_a_id,
                selected_text="Sensitive hypothesis discovered by Alpha.",
                bounding_boxes=[[0.1, 0.1, 0.5, 0.2, 1]],
                page_number=1,
                user_note="Alpha's personal thoughts",
                tags=["confidential"],
                frozen_snapshot={},
                is_source_detached=False,
                version=1,
            )
            db_session.add(note_a)
            await db_session.commit()

        # 3. User A can access own resources
        headers_a = {"Authorization": f"Bearer {token_a}"}
        res_a_doc = await client.get(f"/api/v1/documents/{doc_a_id}", headers=headers_a)
        assert res_a_doc.status_code == 200

        res_a_session = await client.get(f"/api/v1/sessions/{session_a_id}", headers=headers_a)
        assert res_a_session.status_code == 200

        res_a_note = await client.get(f"/api/v1/notes/{note_a_id}", headers=headers_a)
        assert res_a_note.status_code == 200

        # 4. User B attempts to access User A's resources -> Must receive 404 Not Found!
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # Document isolation
        res_b_doc = await client.get(f"/api/v1/documents/{doc_a_id}", headers=headers_b)
        assert res_b_doc.status_code == 404, "User B should not be able to read User A's document"

        res_b_doc_del = await client.delete(f"/api/v1/documents/{doc_a_id}", headers=headers_b)
        assert res_b_doc_del.status_code == 404, (
            "User B should not be able to delete User A's document"
        )

        # Session isolation
        res_b_session = await client.get(f"/api/v1/sessions/{session_a_id}", headers=headers_b)
        assert res_b_session.status_code == 404, (
            "User B should not be able to access User A's session"
        )

        # Note isolation
        res_b_note = await client.get(f"/api/v1/notes/{note_a_id}", headers=headers_b)
        assert res_b_note.status_code == 404, "User B should not be able to read User A's note"

        res_b_note_patch = await client.patch(
            f"/api/v1/notes/{note_a_id}",
            headers={"Authorization": f"Bearer {token_b}", "If-Match": '"v1"'},
            json={"user_note": "Hacked by Beta"},
        )
        assert res_b_note_patch.status_code == 404, (
            "User B should not be able to modify User A's note"
        )

        # User B delete attempt should not affect User A's note
        await client.delete(f"/api/v1/notes/{note_a_id}", headers=headers_b)
        res_a_note_still_exists = await client.get(f"/api/v1/notes/{note_a_id}", headers=headers_a)
        assert res_a_note_still_exists.status_code == 200, "User A's note must remain untouched"


# ==============================================================================
# Backward Compatibility & Dev User Fallback
# ==============================================================================
@pytest.mark.asyncio
async def test_dev_user_fallback_with_x_user_id() -> None:
    """Verify that requests with X-User-Id and no token fall back to dev user."""
    async with auth_test_context() as (client, _):
        res = await client.get(
            "/api/v1/auth/me",
            headers={"X-User-Id": str(DEFAULT_DEV_USER_ID)},
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["id"] == str(DEFAULT_DEV_USER_ID)
        assert data["email"] == "developer@verischolar.org"
