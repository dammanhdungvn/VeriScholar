"""Automated tests for Google OAuth login and Token Quota endpoints."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.user import UserModel
from api.db.session import get_db
from api.services.auth_service import AuthService
from httpx import ASGITransport, AsyncClient


class InMemoryGoogleUserStore:
    """In-memory user store test double for Google OAuth testing."""

    def __init__(self) -> None:
        self.users: dict[UUID, UserModel] = {}
        self.users_by_email: dict[str, UserModel] = {}
        self.users_by_google_id: dict[str, UserModel] = {}

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
            if obj.google_id:
                self.users_by_google_id[obj.google_id] = obj

    async def commit(self) -> None:
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
        if "users" in stmt_str:
            target_email = None
            target_gid = None
            target_id = None
            for p_val in params.values():
                if isinstance(p_val, str) and "@" in p_val:
                    target_email = p_val.lower().strip()
                elif isinstance(p_val, str) and "google_sub_" in p_val:
                    target_gid = p_val
                elif isinstance(p_val, UUID):
                    target_id = p_val

            matched = None
            if target_id and target_id in self.users:
                matched = self.users[target_id]
            elif target_gid and target_gid in self.users_by_google_id:
                matched = self.users_by_google_id[target_gid]
            elif target_email and target_email in self.users_by_email:
                matched = self.users_by_email[target_email]

            mock_result.scalar_one_or_none.return_value = matched
            mock_result.scalars.return_value.all.return_value = (
                [matched] if matched else list(self.users.values())
            )
            return mock_result

        mock_result.scalar_one_or_none.return_value = None
        mock_result.scalars.return_value.all.return_value = []
        return mock_result


@pytest.fixture
def in_memory_store() -> InMemoryGoogleUserStore:
    return InMemoryGoogleUserStore()


@pytest.fixture
def auth_service() -> AuthService:
    return AuthService()


@pytest.fixture(autouse=True)
def override_db(in_memory_store: InMemoryGoogleUserStore) -> Generator[None, None, None]:
    async def _get_test_db() -> AsyncGenerator[Any, None]:
        yield in_memory_store

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_google_login_new_user_success(auth_service: AuthService) -> None:
    """Register and login new user via Google credential."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/auth/google",
            json={"credential": "mock_google:professor_albus@hogwarts.edu:Albus Dumbledore"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]

        # Validate token payload contains researcher role
        payload = auth_service.decode_token(data["data"]["access_token"])
        assert payload["email"] == "professor_albus@hogwarts.edu"
        assert payload["role"] == "researcher"


@pytest.mark.asyncio
async def test_google_login_existing_user(in_memory_store: InMemoryGoogleUserStore) -> None:
    """Login existing user via Google credential links properly."""
    existing_user = UserModel(
        id=uuid4(),
        email="existing_researcher@stanford.edu",
        full_name="Existing Scholar",
        hashed_password="some_hashed_password",
        role="researcher",
        is_active=True,
        token_quota=200000,
        tokens_used=1500,
    )
    in_memory_store.add(existing_user)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/auth/google",
            json={"credential": "mock_google:existing_researcher@stanford.edu:Existing Scholar"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_google_login_invalid_credential() -> None:
    """Reject invalid credential with 400 Bad Request."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/auth/google",
            json={"credential": "invalid_token_without_email"},
        )
        assert response.status_code == 400
        err = response.json()
        assert err["success"] is False
        assert err["error"]["code"] == "INVALID_GOOGLE_CREDENTIAL"


@pytest.mark.asyncio
async def test_get_quota_status_endpoint(
    in_memory_store: InMemoryGoogleUserStore, auth_service: AuthService
) -> None:
    """Retrieve real-time token quota and balance."""
    user = UserModel(
        id=uuid4(),
        email="quota_user@mit.edu",
        full_name="Quota Tester",
        hashed_password="hashed_pwd",
        role="researcher",
        is_active=True,
        token_quota=100000,
        tokens_used=25000,
        storage_quota_bytes=1000000,
        storage_used_bytes=200000,
    )
    in_memory_store.add(user)

    access_token, _ = auth_service.create_access_token(user.id, user.email, role=user.role)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get(
            "/api/v1/auth/quota",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        data = res["data"]
        assert data["token_quota"] == 100000
        assert data["tokens_used"] == 25000
        assert data["tokens_remaining"] == 75000
        assert data["percent_tokens_used"] == 25.0
        assert data["is_quota_exceeded"] is False
