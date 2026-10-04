"""Automated integration tests for Project Folders (Module 4 Library API)."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.document import DocumentModel
from api.db.models.folder import FolderModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import DEFAULT_DEV_USER_ID, get_current_user
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class InMemoryFolderStore:
    """In-memory store for project folder testing."""

    def __init__(self) -> None:
        self.folders: dict[UUID, FolderModel] = {}
        self.documents: dict[UUID, DocumentModel] = {}

    def add(self, obj: object) -> None:
        now = datetime.now(UTC)
        if isinstance(obj, FolderModel):
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            if getattr(obj, "updated_at", None) is None:
                obj.updated_at = now
            self.folders[obj.id] = obj
        elif isinstance(obj, DocumentModel):
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()
            self.documents[obj.id] = obj

    async def delete(self, obj: object) -> None:
        if isinstance(obj, FolderModel):
            self.folders.pop(obj.id, None)

    async def flush(self) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def refresh(self, obj: object) -> None:
        now = datetime.now(UTC)
        if isinstance(obj, FolderModel):
            if obj.updated_at is None:
                obj.updated_at = now

    async def execute(self, statement: Any, *args: Any, **kwargs: Any) -> Any:
        stmt_str = str(statement)
        try:
            compiled = statement.compile()
            params = compiled.params or {}
        except Exception:
            params = {}

        # 1. Update documents where folder_id in (...)
        if "UPDATE documents" in stmt_str:
            for doc in self.documents.values():
                doc.folder_id = None
            mock_res = MagicMock()
            return mock_res

        # 2. Document count grouped by folder_id
        if "FROM documents" in stmt_str and "GROUP BY documents.folder_id" in stmt_str:
            mock_res = MagicMock()
            counts: dict[UUID, int] = {}
            for doc in self.documents.values():
                if doc.user_id == DEFAULT_DEV_USER_ID and doc.is_persistent and doc.folder_id:
                    counts[doc.folder_id] = counts.get(doc.folder_id, 0) + 1
            mock_res.all.return_value = list(counts.items())
            return mock_res

        # 3. Document count for single folder
        if "count(documents.id)" in stmt_str.lower():
            mock_res = MagicMock()
            target_f_id = None
            for v in params.values():
                if isinstance(v, UUID) and v in self.folders:
                    target_f_id = v
                    break
            count = sum(
                1
                for d in self.documents.values()
                if (
                    d.user_id == DEFAULT_DEV_USER_ID
                    and d.is_persistent
                    and d.folder_id == target_f_id
                )
            )
            mock_res.scalar_one.return_value = count
            return mock_res

        # 4. Select documents
        if "FROM documents" in stmt_str:
            mock_res = MagicMock()
            docs = [d for d in self.documents.values() if d.user_id == DEFAULT_DEV_USER_ID]
            mock_res.scalars.return_value.all.return_value = docs
            return mock_res

        # 5. Duplicate folder check or find by id/name
        if "FROM folders" in stmt_str:
            mock_res = MagicMock()
            # Check by specific ID
            target_id = None
            for k, v in params.items():
                if "id" in k.lower() and isinstance(v, UUID):
                    target_id = v
                    break

            name_param = None
            for k, v in params.items():
                if "name" in k.lower() and isinstance(v, str):
                    name_param = v
                    break

            parent_id_param = None
            for k, v in params.items():
                if "parent_id" in k.lower() and (isinstance(v, UUID) or v is None):
                    parent_id_param = v
                    break

            if target_id and not name_param:
                f = self.folders.get(target_id)
                mock_res.scalar_one_or_none.return_value = f
                mock_res.scalars.return_value.all.return_value = [f] if f else []
                return mock_res

            if name_param:
                # Find matching folder by name & parent_id & user_id
                matched = None
                for f in self.folders.values():
                    if f.user_id == DEFAULT_DEV_USER_ID and f.name == name_param:
                        # Check parent
                        if (
                            "parent_id IS NULL" in stmt_str
                            or "parent_id IS NOT DISTINCT FROM" in stmt_str
                            or "parent_id IS" in stmt_str
                        ):
                            if f.parent_id == parent_id_param:
                                if target_id and f.id == target_id:
                                    continue
                                matched = f
                                break
                        elif f.parent_id == parent_id_param:
                            if target_id and f.id == target_id:
                                continue
                            matched = f
                            break
                mock_res.scalar_one_or_none.return_value = matched
                mock_res.scalars.return_value.all.return_value = [matched] if matched else []
                return mock_res

            # All user folders
            user_folders = [f for f in self.folders.values() if f.user_id == DEFAULT_DEV_USER_ID]
            mock_res.scalars.return_value.all.return_value = user_folders
            mock_res.scalar_one_or_none.return_value = user_folders[0] if user_folders else None
            return mock_res

        # Default fallback
        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = None
        mock_res.scalars.return_value.all.return_value = []
        mock_res.all.return_value = []
        return mock_res


@pytest.fixture
def folder_store() -> InMemoryFolderStore:
    return InMemoryFolderStore()


@pytest.fixture
def mock_db_session(folder_store: InMemoryFolderStore) -> AsyncSession:
    return folder_store  # type: ignore[return-value]


@pytest.fixture
def mock_user() -> UserModel:
    user = UserModel(
        email="researcher@verischolar.org",
        full_name="Dr. Scholar",
        is_active=True,
    )
    user.id = DEFAULT_DEV_USER_ID
    return user


@pytest.fixture
def client(
    mock_db_session: AsyncSession,
    mock_user: UserModel,
) -> Generator[AsyncClient, None, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield mock_db_session

    async def override_get_current_user() -> UserModel:
        return mock_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)
    async_client = AsyncClient(transport=transport, base_url="http://testserver")
    yield async_client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_folders_empty(client: AsyncClient) -> None:
    """Listing folders on a clean account returns an empty list."""
    response = await client.get("/api/v1/folders")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"] == []


@pytest.mark.asyncio
async def test_create_root_folder_success(
    client: AsyncClient,
    folder_store: InMemoryFolderStore,
) -> None:
    """Create a new root folder successfully."""
    payload = {"name": "Machine Learning", "parent_id": None}
    response = await client.post("/api/v1/folders", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["name"] == "Machine Learning"
    assert body["data"]["parent_id"] is None
    assert body["data"]["document_count"] == 0
    assert UUID(body["data"]["id"]) in folder_store.folders


@pytest.mark.asyncio
async def test_create_nested_folder_success(
    client: AsyncClient,
    folder_store: InMemoryFolderStore,
) -> None:
    """Create a nested child folder under an existing root folder."""
    root_folder = FolderModel(
        user_id=DEFAULT_DEV_USER_ID,
        name="Deep Learning",
        parent_id=None,
    )
    folder_store.add(root_folder)

    payload = {"name": "Transformers", "parent_id": str(root_folder.id)}
    response = await client.post("/api/v1/folders", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["name"] == "Transformers"
    assert body["data"]["parent_id"] == str(root_folder.id)


@pytest.mark.asyncio
async def test_create_folder_duplicate_conflict(
    client: AsyncClient,
    folder_store: InMemoryFolderStore,
) -> None:
    """Creating a folder with duplicate name in the same parent returns 409 Conflict."""
    existing = FolderModel(
        user_id=DEFAULT_DEV_USER_ID,
        name="Computer Vision",
        parent_id=None,
    )
    folder_store.add(existing)

    payload = {"name": "Computer Vision", "parent_id": None}
    response = await client.post("/api/v1/folders", json=payload)
    assert response.status_code == 409
    body = response.json()
    assert body["error"]["code"] == "DUPLICATE_FOLDER_NAME"


@pytest.mark.asyncio
async def test_create_folder_invalid_name(client: AsyncClient) -> None:
    """Empty folder name returns 422 Unprocessable Entity."""
    payload = {"name": "   ", "parent_id": None}
    response = await client.post("/api/v1/folders", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_folder_parent_not_found(client: AsyncClient) -> None:
    """Non-existent parent folder ID returns 404 Not Found."""
    fake_parent_id = str(uuid4())
    payload = {"name": "Subtopic", "parent_id": fake_parent_id}
    response = await client.post("/api/v1/folders", json=payload)
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "PARENT_FOLDER_NOT_FOUND"


@pytest.mark.asyncio
async def test_update_folder_rename(
    client: AsyncClient,
    folder_store: InMemoryFolderStore,
) -> None:
    """Rename an existing folder."""
    folder = FolderModel(
        user_id=DEFAULT_DEV_USER_ID,
        name="NLP",
        parent_id=None,
    )
    folder_store.add(folder)

    payload = {"name": "Natural Language Processing"}
    response = await client.patch(f"/api/v1/folders/{folder.id}", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["name"] == "Natural Language Processing"
    assert folder.name == "Natural Language Processing"


@pytest.mark.asyncio
async def test_update_folder_self_parent_error(
    client: AsyncClient,
    folder_store: InMemoryFolderStore,
) -> None:
    """Attempting to set a folder as its own parent returns 400 Bad Request."""
    folder = FolderModel(
        user_id=DEFAULT_DEV_USER_ID,
        name="Robotics",
        parent_id=None,
    )
    folder_store.add(folder)

    payload = {"parent_id": str(folder.id)}
    response = await client.patch(f"/api/v1/folders/{folder.id}", json=payload)
    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "CYCLIC_PARENT_ERROR"


@pytest.mark.asyncio
async def test_delete_folder_uncategorizes_documents(
    client: AsyncClient,
    folder_store: InMemoryFolderStore,
) -> None:
    """Deleting a folder resets document folder_id to None (Zero Data Loss)."""
    folder = FolderModel(
        user_id=DEFAULT_DEV_USER_ID,
        name="Archived Topic",
        parent_id=None,
    )
    folder_store.add(folder)

    doc = DocumentModel(
        user_id=DEFAULT_DEV_USER_ID,
        filename="paper.pdf",
        title="Sample Paper",
        content_hash="abc1234",
        file_size_bytes=1000,
        is_persistent=True,
        folder_id=folder.id,
    )
    folder_store.add(doc)

    response = await client.delete(f"/api/v1/folders/{folder.id}")
    assert response.status_code == 204
    assert folder.id not in folder_store.folders
    # Document remains, folder_id reset to None
    assert doc.folder_id is None
