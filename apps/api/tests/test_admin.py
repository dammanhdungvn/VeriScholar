"""Automated tests for Admin Console dashboard, user quotas, and health probes (BỔ SUNG 2)."""

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


class InMemoryAdminStore:
    """In-memory test double for admin testing."""

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

    async def commit(self) -> None:
        pass

    async def refresh(self, obj: object) -> None:
        pass

    async def execute(self, statement: Any, *args: Any, **kwargs: Any) -> Any:
        stmt_str = str(statement)
        try:
            compiled = statement.compile()
            params = compiled.params or {}
        except Exception:
            params = {}

        mock_result = MagicMock()

        # Handle user lookup by id or email
        if "FROM users" in stmt_str or "users.id =" in stmt_str:
            target_id = None
            target_email = None
            for p_val in params.values():
                if isinstance(p_val, UUID):
                    target_id = p_val
                elif isinstance(p_val, str) and "@" in p_val:
                    target_email = p_val.lower().strip()

            matched = None
            if target_id and target_id in self.users:
                matched = self.users[target_id]
            elif target_email and target_email in self.users_by_email:
                matched = self.users_by_email[target_email]

            mock_result.scalar_one_or_none.return_value = matched
            mock_result.scalars.return_value.all.return_value = list(self.users.values())
            return mock_result

        # Handle aggregate count queries
        if "count(" in stmt_str:
            mock_result.scalar.return_value = len(self.users)
            return mock_result

        # Handle sum queries
        if "sum(" in stmt_str:
            mock_result.scalar.return_value = 50000
            return mock_result

        # Handle raw health check query
        if "SELECT 1" in stmt_str:
            mock_result.scalar.return_value = 1
            return mock_result

        mock_result.scalar_one_or_none.return_value = None
        mock_result.scalars.return_value.all.return_value = []
        mock_result.all.return_value = []
        return mock_result


@pytest.fixture
def admin_store() -> InMemoryAdminStore:
    return InMemoryAdminStore()


@pytest.fixture
def auth_service() -> AuthService:
    return AuthService()


@pytest.fixture(autouse=True)
def override_db(admin_store: InMemoryAdminStore) -> Generator[None, None, None]:
    async def _get_test_db() -> AsyncGenerator[Any, None]:
        yield admin_store

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_admin_dashboard_metrics(
    admin_store: InMemoryAdminStore, auth_service: AuthService
) -> None:
    """Admin can view global system dashboard metrics."""
    admin_user = UserModel(
        id=uuid4(),
        email="admin@verischolar.org",
        full_name="System Admin",
        hashed_password="pw",
        role="admin",
        is_active=True,
    )
    admin_store.add(admin_user)
    token, _ = auth_service.create_access_token(admin_user.id, admin_user.email, role="admin")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get(
            "/api/v1/admin/dashboard",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        data = res["data"]
        assert "total_users" in data
        assert "total_storage_bytes" in data
        assert "total_tokens_consumed" in data
        assert data["system_status"] == "healthy"


@pytest.mark.asyncio
async def test_admin_update_user_quota(
    admin_store: InMemoryAdminStore, auth_service: AuthService
) -> None:
    """Admin can modify user token quota and privileges."""
    admin_user = UserModel(
        id=uuid4(),
        email="admin@verischolar.org",
        full_name="System Admin",
        hashed_password="pw",
        role="admin",
        is_active=True,
    )
    regular_user = UserModel(
        id=uuid4(),
        email="student@university.edu",
        full_name="PhD Student",
        hashed_password="pw",
        role="researcher",
        is_active=True,
        token_quota=100000,
        tokens_used=5000,
    )
    admin_store.add(admin_user)
    admin_store.add(regular_user)

    token, _ = auth_service.create_access_token(admin_user.id, admin_user.email, role="admin")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.patch(
            f"/api/v1/admin/users/{regular_user.id}/quota",
            headers={"Authorization": f"Bearer {token}"},
            json={"token_quota": 500000, "role": "admin"},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["token_quota"] == 500000
        assert data["role"] == "admin"


@pytest.mark.asyncio
async def test_regular_user_forbidden_from_admin(
    admin_store: InMemoryAdminStore, auth_service: AuthService
) -> None:
    """Non-admin researcher receives 403 Forbidden on admin endpoints."""
    regular_user = UserModel(
        id=uuid4(),
        email="student@university.edu",
        full_name="PhD Student",
        hashed_password="pw",
        role="researcher",
        is_active=True,
    )
    admin_store.add(regular_user)
    token, _ = auth_service.create_access_token(
        regular_user.id, regular_user.email, role="researcher"
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get(
            "/api/v1/admin/dashboard",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
        res = response.json()
        assert res["success"] is False
        assert res["error"]["code"] == "INSUFFICIENT_PRIVILEGES"
