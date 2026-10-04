"""Automated tests for Research Organizations and Lab collaboration (BỔ SUNG 2)."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.organization import OrganizationMemberModel, OrganizationModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.services.auth_service import AuthService
from httpx import ASGITransport, AsyncClient


class InMemoryOrgStore:
    """In-memory test double for organizations and members."""

    def __init__(self) -> None:
        self.orgs: dict[UUID, OrganizationModel] = {}
        self.members: dict[UUID, OrganizationMemberModel] = {}
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
        elif isinstance(obj, OrganizationModel):
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            if getattr(obj, "updated_at", None) is None:
                obj.updated_at = now
            self.orgs[obj.id] = obj
        elif isinstance(obj, OrganizationMemberModel):
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            self.members[obj.id] = obj

    async def flush(self) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def refresh(self, obj: object) -> None:
        pass

    async def delete(self, obj: object) -> None:
        if isinstance(obj, OrganizationMemberModel) and obj.id in self.members:
            del self.members[obj.id]

    async def execute(self, statement: Any, *args: Any, **kwargs: Any) -> Any:
        stmt_str = str(statement)
        try:
            compiled = statement.compile()
            params = compiled.params or {}
        except Exception:
            params = {}

        mock_result = MagicMock()

        # Handle users query
        if "FROM users" in stmt_str or "users" in stmt_str:
            target_email = None
            target_id = None
            for p_val in params.values():
                if isinstance(p_val, str) and "@" in p_val:
                    target_email = p_val.lower().strip()
                elif isinstance(p_val, UUID):
                    target_id = p_val

            matched_user = None
            if target_id and target_id in self.users:
                matched_user = self.users[target_id]
            elif target_email and target_email in self.users_by_email:
                matched_user = self.users_by_email[target_email]

            mock_result.scalar_one_or_none.return_value = matched_user
            return mock_result

        # Handle slug check query
        if "organizations.slug" in stmt_str:
            target_slug = None
            for p_val in params.values():
                if isinstance(p_val, str) and "@" not in p_val:
                    target_slug = p_val.lower().strip()

            found_slug = None
            if target_slug:
                for org in self.orgs.values():
                    if org.slug == target_slug:
                        found_slug = org
                        break
            mock_result.scalar_one_or_none.return_value = found_slug
            return mock_result

        # Handle member count query
        if "count(organization_members.id)" in stmt_str or "count(" in stmt_str:
            org_id = None
            for p_val in params.values():
                if isinstance(p_val, UUID):
                    org_id = p_val
            c = sum(1 for m in self.members.values() if m.organization_id == org_id)
            mock_result.scalar.return_value = c or 1
            return mock_result

        # Handle organization by id
        if "organizations.id" in stmt_str:
            org_id = None
            for p_val in params.values():
                if isinstance(p_val, UUID):
                    org_id = p_val
            mock_result.scalar_one_or_none.return_value = self.orgs.get(org_id)
            return mock_result

        # Handle members list query
        if "organization_members.organization_id" in stmt_str and "join" in stmt_str.lower():
            org_id = None
            for p_val in params.values():
                if isinstance(p_val, UUID):
                    org_id = p_val

            rows = []
            for m in self.members.values():
                if m.organization_id == org_id:
                    u = self.users.get(m.user_id)
                    email = u.email if u else "unknown@user"
                    full_name = u.full_name if u else "Unknown"
                    rows.append((m, email, full_name))
            mock_result.all.return_value = rows
            return mock_result

        # Handle membership check query
        if "organization_members" in stmt_str:
            target_org = None
            target_u = None
            for p_val in params.values():
                if isinstance(p_val, UUID):
                    if target_org is None:
                        target_org = p_val
                    else:
                        target_u = p_val

            matched_mem = None
            for m in self.members.values():
                if target_org and m.organization_id == target_org:
                    if target_u and m.user_id == target_u:
                        matched_mem = m
                        break
                    elif not target_u:
                        matched_mem = m
                        break
            mock_result.scalar_one_or_none.return_value = matched_mem
            mock_result.all.return_value = (
                [
                    (self.orgs[m.organization_id], m.role)
                    for m in self.members.values()
                    if m.user_id == target_u
                ]
                if target_u
                else []
            )

            return mock_result

        mock_result.scalar_one_or_none.return_value = None
        mock_result.all.return_value = []
        return mock_result


@pytest.fixture
def org_store() -> InMemoryOrgStore:
    return InMemoryOrgStore()


@pytest.fixture
def auth_service() -> AuthService:
    return AuthService()


@pytest.fixture(autouse=True)
def override_db(org_store: InMemoryOrgStore) -> Generator[None, None, None]:
    async def _get_test_db() -> AsyncGenerator[Any, None]:
        yield org_store

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_create_and_list_organizations(
    org_store: InMemoryOrgStore, auth_service: AuthService
) -> None:
    """Create lab, assign owner, and verify in list endpoint."""
    user = UserModel(
        id=uuid4(),
        email="prof_turing@cambridge.edu",
        full_name="Alan Turing",
        hashed_password="pw",
        role="researcher",
        is_active=True,
    )
    org_store.add(user)
    token, _ = auth_service.create_access_token(user.id, user.email)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Create
        response = await client.post(
            "/api/v1/organizations",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Machine Intelligence Lab",
                "slug": "machine-intelligence-lab",
                "description": "Pioneering neural computation and verification.",
            },
        )
        assert response.status_code == 201
        res = response.json()
        assert res["success"] is True
        assert res["data"]["slug"] == "machine-intelligence-lab"
        assert res["data"]["user_role"] == "owner"

        # Duplicate slug check
        dup_resp = await client.post(
            "/api/v1/organizations",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Another Lab",
                "slug": "machine-intelligence-lab",
            },
        )
        assert dup_resp.status_code == 409


@pytest.mark.asyncio
async def test_add_and_remove_member(
    org_store: InMemoryOrgStore, auth_service: AuthService
) -> None:
    """Invite member to lab, update role, and remove."""
    owner = UserModel(
        id=uuid4(),
        email="curie@sorbonne.fr",
        full_name="Marie Curie",
        hashed_password="pw",
        role="researcher",
        is_active=True,
    )
    colleague = UserModel(
        id=uuid4(),
        email="becquerel@sorbonne.fr",
        full_name="Henri Becquerel",
        hashed_password="pw",
        role="researcher",
        is_active=True,
    )
    org_store.add(owner)
    org_store.add(colleague)

    org = OrganizationModel(
        id=uuid4(),
        name="Radioactivity Research Group",
        slug="radioactivity-lab",
        storage_quota_bytes=10737418240,
        token_quota=1000000,
    )
    owner_membership = OrganizationMemberModel(
        id=uuid4(),
        organization_id=org.id,
        user_id=owner.id,
        role="owner",
    )
    org_store.add(org)
    org_store.add(owner_membership)

    token, _ = auth_service.create_access_token(owner.id, owner.email)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Add colleague
        add_resp = await client.post(
            f"/api/v1/organizations/{org.id}/members",
            headers={"Authorization": f"Bearer {token}"},
            json={"email": "becquerel@sorbonne.fr", "role": "member"},
        )
        assert add_resp.status_code == 201
        assert add_resp.json()["email"] == "becquerel@sorbonne.fr"

        # Update role
        upd_resp = await client.patch(
            f"/api/v1/organizations/{org.id}/members/{colleague.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"role": "admin"},
        )
        assert upd_resp.status_code == 200
        assert upd_resp.json()["role"] == "admin"

        # Remove member
        del_resp = await client.delete(
            f"/api/v1/organizations/{org.id}/members/{colleague.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert del_resp.status_code == 204
