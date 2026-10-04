"""Automated unit and integration tests for Authentication and Identity system."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from api import app
from api.core.config import settings
from api.db.models.user import UserModel
from api.db.session import get_db
from api.services.auth_service import AuthService
from httpx import ASGITransport, AsyncClient


class InMemoryUserStore:
    """In-memory database test double for user authentication testing."""

    def __init__(self) -> None:
        self.users: dict[UUID, UserModel] = {}
        self.users_by_email: dict[str, UserModel] = {}

    def add(self, obj: object) -> None:
        now = datetime.now(UTC)
        if isinstance(obj, UserModel):
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            if getattr(obj, "updated_at", None) is None:
                obj.updated_at = now
            self.users[obj.id] = obj
            self.users_by_email[obj.email.lower().strip()] = obj

    async def flush(self) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def refresh(self, obj: object) -> None:
        now = datetime.now(UTC)
        if isinstance(obj, UserModel):
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            if getattr(obj, "updated_at", None) is None:
                obj.updated_at = now

    async def execute(self, statement: Any, *args: Any, **kwargs: Any) -> Any:
        stmt_str = str(statement)
        try:
            compiled = statement.compile()
            params = compiled.params or {}
        except Exception:
            params = {}

        mock_result = MagicMock()

        if "FROM users" in stmt_str or "users" in stmt_str:
            target_email = None
            target_id = None
            for p_val in params.values():
                if isinstance(p_val, str) and "@" in p_val:
                    target_email = p_val.lower().strip()
                elif isinstance(p_val, UUID):
                    target_id = p_val

            found_user = None
            if target_email and target_email in self.users_by_email:
                found_user = self.users_by_email[target_email]
            elif target_id and target_id in self.users:
                found_user = self.users[target_id]
            else:
                for email, u in self.users_by_email.items():
                    if email in stmt_str:
                        found_user = u
                        break
                if not found_user:
                    for uid, u in self.users.items():
                        if str(uid) in stmt_str:
                            found_user = u
                            break

            mock_result.scalar_one_or_none.return_value = found_user
            return mock_result

        mock_result.scalar_one_or_none.return_value = None
        return mock_result


@pytest.fixture
def user_store() -> InMemoryUserStore:
    return InMemoryUserStore()


@pytest.fixture
def auth_service() -> AuthService:
    return AuthService()


@pytest.fixture
def client(user_store: InMemoryUserStore) -> Generator[AsyncClient, None, None]:
    async def override_get_db() -> AsyncGenerator[Any, None]:
        yield user_store

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async_client = AsyncClient(transport=transport, base_url="http://testserver")
    yield async_client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_auth_service_argon2_hashing(auth_service: AuthService) -> None:
    """Verify password hashing with Argon2id and verification logic."""
    raw_pass = "SecurePass123!#"
    hashed = auth_service.hash_password(raw_pass)
    assert hashed != raw_pass
    assert "$argon2" in hashed
    assert auth_service.verify_password(raw_pass, hashed) is True
    assert auth_service.verify_password("WrongPassword!", hashed) is False


@pytest.mark.asyncio
async def test_auth_service_jwt_lifecycle(auth_service: AuthService) -> None:
    """Verify JWT token creation, encoding, decoding, and type validation."""
    user_id = uuid4()
    email = "scientist@verischolar.org"

    access_token, expires_in = auth_service.create_access_token(user_id, email)
    assert isinstance(access_token, str)
    assert expires_in == 60 * 60

    payload = auth_service.decode_token(access_token, expected_type="access")
    assert payload["sub"] == str(user_id)
    assert payload["email"] == email
    assert payload["type"] == "access"

    refresh_token = auth_service.create_refresh_token(user_id, email)
    ref_payload = auth_service.decode_token(refresh_token, expected_type="refresh")
    assert ref_payload["sub"] == str(user_id)
    assert ref_payload["type"] == "refresh"


@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient, user_store: InMemoryUserStore) -> None:
    """POST /api/v1/auth/register should create a new user and return UserResponse."""
    payload = {
        "email": "dr_curie@lab.edu",
        "password": "Radioactivity1898!",
        "full_name": "Marie Curie",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["email"] == "dr_curie@lab.edu"
    assert data["data"]["full_name"] == "Marie Curie"
    assert data["data"]["is_active"] is True
    assert "password" not in data["data"]
    assert "hashed_password" not in data["data"]

    # Verify user stored in in-memory DB has Argon2 hash
    user = user_store.users_by_email["dr_curie@lab.edu"]
    assert user.hashed_password.startswith("$argon2")


@pytest.mark.asyncio
async def test_register_duplicate_email(
    client: AsyncClient, auth_service: AuthService, user_store: InMemoryUserStore
) -> None:
    """POST /api/v1/auth/register with duplicate email should return HTTP 409 Conflict."""
    existing_user = UserModel(
        id=uuid4(),
        email="existing@lab.edu",
        full_name="Existing Scholar",
        hashed_password=auth_service.hash_password("password123"),
        is_active=True,
    )
    user_store.add(existing_user)

    payload = {
        "email": "existing@lab.edu",
        "password": "newpassword123",
        "full_name": "Another Person",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 409
    data = resp.json()
    assert data["success"] is False
    assert data["error"]["code"] == "EMAIL_ALREADY_REGISTERED"


@pytest.mark.asyncio
async def test_login_success(
    client: AsyncClient, auth_service: AuthService, user_store: InMemoryUserStore
) -> None:
    """POST /api/v1/auth/login with valid credentials returns access and refresh tokens."""
    raw_pass = "MySecretPass2026!"
    user = UserModel(
        id=uuid4(),
        email="turing@princeton.edu",
        full_name="Alan Turing",
        hashed_password=auth_service.hash_password(raw_pass),
        is_active=True,
    )
    user_store.add(user)

    login_payload = {
        "email": "turing@princeton.edu",
        "password": raw_pass,
    }
    resp = await client.post("/api/v1/auth/login", json=login_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    token_data = data["data"]
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["expires_in"] > 0


@pytest.mark.asyncio
async def test_login_invalid_password(
    client: AsyncClient, auth_service: AuthService, user_store: InMemoryUserStore
) -> None:
    """POST /api/v1/auth/login with wrong password returns HTTP 401."""
    user = UserModel(
        id=uuid4(),
        email="newton@cambridge.ac.uk",
        full_name="Isaac Newton",
        hashed_password=auth_service.hash_password("Principia1687!"),
        is_active=True,
    )
    user_store.add(user)

    login_payload = {
        "email": "newton@cambridge.ac.uk",
        "password": "WrongPassword123!",
    }
    resp = await client.post("/api/v1/auth/login", json=login_payload)
    assert resp.status_code == 401
    data = resp.json()
    assert data["success"] is False
    assert data["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_refresh_token_endpoint(
    client: AsyncClient, auth_service: AuthService, user_store: InMemoryUserStore
) -> None:
    """POST /api/v1/auth/refresh issues a new token pair using a valid refresh token."""
    user = UserModel(
        id=uuid4(),
        email="einstein@ias.edu",
        full_name="Albert Einstein",
        hashed_password=auth_service.hash_password("Relativity1915!"),
        is_active=True,
    )
    user_store.add(user)

    refresh_token = auth_service.create_refresh_token(user.id, user.email)
    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]


@pytest.mark.asyncio
async def test_get_me_with_bearer_token(
    client: AsyncClient, auth_service: AuthService, user_store: InMemoryUserStore
) -> None:
    """GET /api/v1/auth/me returns current user profile when valid Bearer token provided."""
    user = UserModel(
        id=uuid4(),
        email="feynman@caltech.edu",
        full_name="Richard Feynman",
        hashed_password=auth_service.hash_password("QED1948!"),
        is_active=True,
    )
    user_store.add(user)

    access_token, _ = auth_service.create_access_token(user.id, user.email)
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = await client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["email"] == "feynman@caltech.edu"
    assert data["data"]["full_name"] == "Richard Feynman"


@pytest.mark.asyncio
async def test_unauthorized_when_auth_required(client: AsyncClient) -> None:
    """When allow_dev_auth_bypass is disabled, request without Bearer token must return HTTP 401."""
    original_bypass = settings.ENABLE_DEV_AUTH_BYPASS
    try:
        settings.ENABLE_DEV_AUTH_BYPASS = False
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401
        data = resp.json()
        assert data["success"] is False
        assert data["error"]["code"] == "AUTHENTICATION_REQUIRED"
    finally:
        settings.ENABLE_DEV_AUTH_BYPASS = original_bypass
