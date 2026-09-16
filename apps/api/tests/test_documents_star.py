"""Automated integration tests for POST /api/v1/documents/{id}:star endpoint."""

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


class InMemoryAsyncStarSession:
    """Fast, deterministic in-memory session test double for document star and folder queries."""

    def __init__(self) -> None:
        self.documents: dict[UUID, DocumentModel] = {}
        self.folders: dict[UUID, FolderModel] = {}
        self._added: list[object] = []

    def add(self, obj: object) -> None:
        self._added.append(obj)
        if isinstance(obj, DocumentModel):
            self.documents[obj.id] = obj
        elif isinstance(obj, FolderModel):
            self.folders[obj.id] = obj

    async def flush(self) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def execute(self, statement: Any) -> MagicMock:
        result_mock = MagicMock()
        stmt_str = str(statement)

        try:
            compiled = statement.compile()  # type: ignore[union-attr]
            params = compiled.params or {}
        except Exception:
            params = {}

        target_id = params.get("id_1") or params.get("id")
        target_user_id = params.get("user_id_1") or params.get("user_id")

        if "FROM folders" in stmt_str:
            matched_folder: FolderModel | None = None
            for f in self.folders.values():
                id_matches = target_id is None or f.id == target_id
                user_matches = target_user_id is None or f.user_id == target_user_id
                if id_matches and user_matches:
                    matched_folder = f
                    break
            result_mock.scalar_one_or_none.return_value = matched_folder
            return result_mock

        if "FROM documents" in stmt_str:
            matched_doc: DocumentModel | None = None
            for d in self.documents.values():
                id_matches = target_id is None or d.id == target_id
                user_matches = target_user_id is None or d.user_id == target_user_id
                if id_matches and user_matches:
                    matched_doc = d
                    break
            result_mock.scalar_one_or_none.return_value = matched_doc
            return result_mock

        return result_mock


@pytest.fixture
def mock_db() -> InMemoryAsyncStarSession:
    return InMemoryAsyncStarSession()


@pytest.fixture
def test_user() -> UserModel:
    return UserModel(
        id=DEFAULT_DEV_USER_ID,
        email="dev@verischolar.local",
        full_name="Developer User",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def client(
    mock_db: InMemoryAsyncStarSession, test_user: UserModel
) -> Generator[AsyncClient, None, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield mock_db  # type: ignore[misc]

    async def override_get_current_user() -> UserModel:
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)
    yield AsyncClient(transport=transport, base_url="http://test")

    app.dependency_overrides.clear()


def _create_sample_doc(
    doc_id: UUID,
    user_id: UUID = DEFAULT_DEV_USER_ID,
    is_persistent: bool = False,
    folder_id: UUID | None = None,
) -> DocumentModel:
    now = datetime.now(UTC)
    return DocumentModel(
        id=doc_id,
        user_id=user_id,
        filename="attention_paper.pdf",
        title="Attention Is All You Need",
        content_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        file_size_bytes=1024 * 500,
        status="completed",
        stage="completed",
        progress=100,
        is_persistent=is_persistent,
        folder_id=folder_id,
        created_at=now,
        updated_at=now,
    )


def _create_sample_folder(
    folder_id: UUID,
    user_id: UUID = DEFAULT_DEV_USER_ID,
    name: str = "Deep Learning Literature",
) -> FolderModel:
    now = datetime.now(UTC)
    return FolderModel(
        id=folder_id,
        user_id=user_id,
        name=name,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_star_document_success_without_folder(
    client: AsyncClient,
    mock_db: InMemoryAsyncStarSession,
) -> None:
    """Starring a temporary document without folder promotes it to persistent library."""
    doc_id = uuid4()
    doc = _create_sample_doc(doc_id=doc_id, is_persistent=False, folder_id=None)
    mock_db.add(doc)

    response = await client.post(f"/api/v1/documents/{doc_id}:star", json={})

    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    assert res_json["data"]["id"] == str(doc_id)
    assert res_json["data"]["is_persistent"] is True
    assert res_json["data"]["folder_id"] is None
    assert res_json["data"]["filename"] == "attention_paper.pdf"
    assert "updated_at" in res_json["data"]

    # Verify state mutated on document
    assert doc.is_persistent is True
    assert doc.folder_id is None


@pytest.mark.asyncio
async def test_star_document_success_with_valid_folder(
    client: AsyncClient,
    mock_db: InMemoryAsyncStarSession,
) -> None:
    """Starring a document with an existing owned folder assigns folder_id atomically."""
    doc_id = uuid4()
    folder_id = uuid4()
    doc = _create_sample_doc(doc_id=doc_id, is_persistent=False)
    folder = _create_sample_folder(folder_id=folder_id)
    mock_db.add(doc)
    mock_db.add(folder)

    response = await client.post(
        f"/api/v1/documents/{doc_id}:star",
        json={"folder_id": str(folder_id)},
    )

    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    assert res_json["data"]["is_persistent"] is True
    assert res_json["data"]["folder_id"] == str(folder_id)

    # Verify state in DB model
    assert doc.is_persistent is True
    assert doc.folder_id == folder_id


@pytest.mark.asyncio
async def test_star_document_idempotent_re_star_with_new_folder(
    client: AsyncClient,
    mock_db: InMemoryAsyncStarSession,
) -> None:
    """Re-starring an already persistent document updates folder_id idempotently."""
    doc_id = uuid4()
    folder1_id = uuid4()
    folder2_id = uuid4()
    doc = _create_sample_doc(doc_id=doc_id, is_persistent=True, folder_id=folder1_id)
    folder1 = _create_sample_folder(folder_id=folder1_id, name="Folder 1")
    folder2 = _create_sample_folder(folder_id=folder2_id, name="Folder 2")
    mock_db.add(doc)
    mock_db.add(folder1)
    mock_db.add(folder2)

    response = await client.post(
        f"/api/v1/documents/{doc_id}:star",
        json={"folder_id": str(folder2_id)},
    )

    assert response.status_code == 200
    res_json = response.json()
    assert res_json["data"]["is_persistent"] is True
    assert res_json["data"]["folder_id"] == str(folder2_id)
    assert doc.folder_id == folder2_id


@pytest.mark.asyncio
async def test_star_document_folder_not_found(
    client: AsyncClient,
    mock_db: InMemoryAsyncStarSession,
) -> None:
    """Providing a non-existent folder_id returns HTTP 404 with FOLDER_NOT_FOUND."""
    doc_id = uuid4()
    non_existent_folder = uuid4()
    doc = _create_sample_doc(doc_id=doc_id)
    mock_db.add(doc)

    response = await client.post(
        f"/api/v1/documents/{doc_id}:star",
        json={"folder_id": str(non_existent_folder)},
    )

    assert response.status_code == 404
    res_json = response.json()
    assert res_json["success"] is False
    assert res_json["error"]["code"] == "FOLDER_NOT_FOUND"
    assert res_json["error"]["field"] == "folder_id"
    # Ensure document was not mutated
    assert doc.is_persistent is False


@pytest.mark.asyncio
async def test_star_document_folder_other_user_isolation(
    client: AsyncClient,
    mock_db: InMemoryAsyncStarSession,
) -> None:
    """Attempting to assign to another user's folder returns HTTP 404 for tenant isolation."""
    doc_id = uuid4()
    folder_id = uuid4()
    other_user_id = uuid4()
    doc = _create_sample_doc(doc_id=doc_id)
    other_user_folder = _create_sample_folder(folder_id=folder_id, user_id=other_user_id)
    mock_db.add(doc)
    mock_db.add(other_user_folder)

    response = await client.post(
        f"/api/v1/documents/{doc_id}:star",
        json={"folder_id": str(folder_id)},
    )

    assert response.status_code == 404
    res_json = response.json()
    assert res_json["error"]["code"] == "FOLDER_NOT_FOUND"


@pytest.mark.asyncio
async def test_star_document_not_found(
    client: AsyncClient,
    mock_db: InMemoryAsyncStarSession,
) -> None:
    """Attempting to star a non-existent document returns HTTP 404 with DOCUMENT_NOT_FOUND."""
    non_existent_doc = uuid4()

    response = await client.post(
        f"/api/v1/documents/{non_existent_doc}:star",
        json={},
    )

    assert response.status_code == 404
    res_json = response.json()
    assert res_json["success"] is False
    assert res_json["error"]["code"] == "DOCUMENT_NOT_FOUND"
    assert res_json["error"]["field"] == "id"


@pytest.mark.asyncio
async def test_star_document_other_user_isolation(
    client: AsyncClient,
    mock_db: InMemoryAsyncStarSession,
) -> None:
    """Attempting to star another user's document returns HTTP 404 without data leakage."""
    doc_id = uuid4()
    other_user_id = uuid4()
    other_doc = _create_sample_doc(doc_id=doc_id, user_id=other_user_id)
    mock_db.add(other_doc)

    response = await client.post(
        f"/api/v1/documents/{doc_id}:star",
        json={},
    )

    assert response.status_code == 404
    res_json = response.json()
    assert res_json["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_star_document_invalid_uuid(client: AsyncClient) -> None:
    """Passing an invalid UUID path string returns HTTP 422 Unprocessable Entity."""
    response = await client.post("/api/v1/documents/invalid-uuid-format:star", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_star_document_openapi_spec(client: AsyncClient) -> None:
    """Verify endpoint is registered with summary, description, and responses in OpenAPI."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    path_spec = schema["paths"].get("/api/v1/documents/{document_id}:star")
    assert path_spec is not None, (
        "Endpoint '/api/v1/documents/{document_id}:star' missing from OpenAPI"
    )

    post_op = path_spec.get("post")
    assert post_op is not None
    assert "Lưu bài báo vào thư viện cá nhân (Star/Promotion)" in post_op["summary"]
    assert "Module 1: Documents" in post_op["tags"]
    assert "200" in post_op["responses"]
    assert "404" in post_op["responses"]
    assert "422" in post_op["responses"]
