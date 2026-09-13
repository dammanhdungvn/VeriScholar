"""Automated integration tests for DELETE /api/v1/documents/{id} endpoint."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.blob import DocumentStorageBlobModel
from api.db.models.document import DocumentModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import DEFAULT_DEV_USER_ID, get_current_user, get_document_service
from api.services.document_service import DocumentService
from core.ports.storage import IBlobStoragePort
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class InMemoryAsyncDeleteSession:
    """Deterministic in-memory session test double for document deletion and blob cleanup."""

    def __init__(self) -> None:
        self.documents: dict[UUID, DocumentModel] = {}
        self.blobs: dict[UUID, DocumentStorageBlobModel] = {}
        self._deleted: list[object] = []

    def add(self, obj: object) -> None:
        if isinstance(obj, DocumentModel):
            self.documents[obj.id] = obj
        elif isinstance(obj, DocumentStorageBlobModel):
            self.blobs[obj.id] = obj

    async def delete(self, obj: object) -> None:
        self._deleted.append(obj)
        if isinstance(obj, DocumentModel) and obj.id in self.documents:
            del self.documents[obj.id]
        elif isinstance(obj, DocumentStorageBlobModel) and obj.id in self.blobs:
            del self.blobs[obj.id]

    async def flush(self) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def execute(self, statement: object) -> MagicMock:
        result_mock = MagicMock()
        stmt_str = str(statement)

        try:
            compiled = statement.compile()  # type: ignore[union-attr]
            params = compiled.params or {}
        except Exception:
            params = {}

        target_id = params.get("id_1") or params.get("id")
        target_user_id = params.get("user_id_1") or params.get("user_id")
        target_hash = params.get("content_hash_1") or params.get("content_hash")

        if "FROM document_storage_blobs" in stmt_str:
            matched_blob: DocumentStorageBlobModel | None = None
            for b in self.blobs.values():
                id_matches = target_id is None or b.id == target_id
                hash_matches = target_hash is None or b.content_hash == target_hash
                if id_matches and hash_matches:
                    matched_blob = b
                    break
            result_mock.scalar_one_or_none.return_value = matched_blob
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
def mock_db() -> InMemoryAsyncDeleteSession:
    return InMemoryAsyncDeleteSession()


@pytest.fixture
def mock_storage() -> MagicMock:
    storage = MagicMock(spec=IBlobStoragePort)
    storage.delete_blob = AsyncMock(return_value=True)
    storage.blob_exists = AsyncMock(return_value=True)
    return storage


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
    mock_db: InMemoryAsyncDeleteSession,
    mock_storage: MagicMock,
    test_user: UserModel,
) -> Generator[AsyncClient, None, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield mock_db  # type: ignore[misc]

    async def override_get_current_user() -> UserModel:
        return test_user

    def override_get_document_service() -> DocumentService:
        return DocumentService(storage=mock_storage)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_document_service] = override_get_document_service

    transport = ASGITransport(app=app)
    yield AsyncClient(transport=transport, base_url="http://test")

    app.dependency_overrides.clear()


def _create_sample_doc(
    doc_id: UUID,
    blob_id: UUID,
    content_hash: str,
    user_id: UUID = DEFAULT_DEV_USER_ID,
) -> DocumentModel:
    return DocumentModel(
        id=doc_id,
        user_id=user_id,
        blob_id=blob_id,
        folder_id=None,
        filename="test_paper.pdf",
        title="Test Paper Title",
        authors=["Author One"],
        publication_year=2024,
        doi="10.1000/182",
        content_hash=content_hash,
        file_size_bytes=10240,
        page_count=10,
        chunk_count=5,
        pages_metadata=[],
        parsed_metadata=None,
        status="completed",
        stage="embedding",
        progress=100,
        error_message=None,
        is_persistent=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def _create_sample_blob(
    blob_id: UUID,
    content_hash: str,
    ref_count: int = 1,
) -> DocumentStorageBlobModel:
    return DocumentStorageBlobModel(
        id=blob_id,
        content_hash=content_hash,
        storage_path=f"storage/{content_hash[:2]}/{content_hash}",
        file_size_bytes=10240,
        ref_count=ref_count,
        status="completed",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


# ==============================================================================
# TEST SUITE: DELETE /api/v1/documents/{document_id}
# ==============================================================================


@pytest.mark.asyncio
async def test_delete_document_success_single_owner_purges_blob_and_file(
    client: AsyncClient,
    mock_db: InMemoryAsyncDeleteSession,
    mock_storage: MagicMock,
) -> None:
    """Test deleting document with ref_count=1 purges database row and physical storage."""
    doc_id = uuid4()
    blob_id = uuid4()
    content_hash = "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"

    blob = _create_sample_blob(blob_id, content_hash, ref_count=1)
    doc = _create_sample_doc(doc_id, blob_id, content_hash)
    mock_db.add(blob)
    mock_db.add(doc)

    response = await client.delete(f"/api/v1/documents/{doc_id}")

    assert response.status_code == 204
    assert response.text == ""

    # Document must be removed from DB
    assert doc_id not in mock_db.documents
    # Blob must be removed from DB since ref_count became 0
    assert blob_id not in mock_db.blobs
    # Physical file purge must be invoked with content_hash
    mock_storage.delete_blob.assert_awaited_once_with(content_hash)


@pytest.mark.asyncio
async def test_delete_document_success_shared_blob_decrements_ref_count(
    client: AsyncClient,
    mock_db: InMemoryAsyncDeleteSession,
    mock_storage: MagicMock,
) -> None:
    """Test deleting shared-blob document decrements ref_count without file purge."""
    blob_id = uuid4()
    content_hash = "sharedhash0123456789abcdef0123456789abcdef0123456789abcdef012345"

    blob = _create_sample_blob(blob_id, content_hash, ref_count=2)
    doc1 = _create_sample_doc(uuid4(), blob_id, content_hash)
    doc2 = _create_sample_doc(uuid4(), blob_id, content_hash)

    mock_db.add(blob)
    mock_db.add(doc1)
    mock_db.add(doc2)

    response = await client.delete(f"/api/v1/documents/{doc1.id}")

    assert response.status_code == 204

    # doc1 is removed, doc2 is preserved
    assert doc1.id not in mock_db.documents
    assert doc2.id in mock_db.documents

    # Blob is preserved and ref_count is decremented to 1
    assert blob_id in mock_db.blobs
    assert mock_db.blobs[blob_id].ref_count == 1

    # Physical file must NOT be deleted while other users still reference it
    mock_storage.delete_blob.assert_not_called()


@pytest.mark.asyncio
async def test_delete_document_not_found(client: AsyncClient) -> None:
    """Test deleting a non-existent document ID returns 404 DOCUMENT_NOT_FOUND."""
    non_existent_id = uuid4()
    response = await client.delete(f"/api/v1/documents/{non_existent_id}")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "DOCUMENT_NOT_FOUND"
    assert str(non_existent_id) in body["error"]["message"]
    assert "meta" in body


@pytest.mark.asyncio
async def test_delete_document_multi_tenant_isolation(
    client: AsyncClient,
    mock_db: InMemoryAsyncDeleteSession,
    mock_storage: MagicMock,
) -> None:
    """Test user cannot delete a document owned by another user (returns 404 for privacy)."""
    other_user_id = uuid4()
    doc_id = uuid4()
    blob_id = uuid4()
    content_hash = "otheruserhash0123456789abcdef0123456789abcdef0123456789abcdef01"

    blob = _create_sample_blob(blob_id, content_hash, ref_count=1)
    doc = _create_sample_doc(doc_id, blob_id, content_hash, user_id=other_user_id)
    mock_db.add(blob)
    mock_db.add(doc)

    response = await client.delete(f"/api/v1/documents/{doc_id}")

    # Must return 404 to avoid information leakage about documents owned by others
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "DOCUMENT_NOT_FOUND"

    # Document must remain intact for other user
    assert doc_id in mock_db.documents
    assert blob_id in mock_db.blobs
    mock_storage.delete_blob.assert_not_called()


@pytest.mark.asyncio
async def test_delete_document_invalid_uuid(client: AsyncClient) -> None:
    """Test non-UUID identifier returns 422 Unprocessable Entity."""
    response = await client.delete("/api/v1/documents/invalid-uuid-string")
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_delete_document_idempotency_second_call_returns_404(
    client: AsyncClient,
    mock_db: InMemoryAsyncDeleteSession,
) -> None:
    """Test calling delete twice returns 204 on first attempt and 404 on subsequent attempt."""
    doc_id = uuid4()
    blob_id = uuid4()
    content_hash = "idempotencyhash0123456789abcdef0123456789abcdef0123456789abcdef"

    blob = _create_sample_blob(blob_id, content_hash, ref_count=1)
    doc = _create_sample_doc(doc_id, blob_id, content_hash)
    mock_db.add(blob)
    mock_db.add(doc)

    # First call: successfully deleted
    first_res = await client.delete(f"/api/v1/documents/{doc_id}")
    assert first_res.status_code == 204

    # Second call: already purged, returns 404
    second_res = await client.delete(f"/api/v1/documents/{doc_id}")
    assert second_res.status_code == 404
    assert second_res.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_openapi_schema_contains_delete_endpoint(client: AsyncClient) -> None:
    """Verify OpenAPI schema documents DELETE /api/v1/documents/{document_id} with 204 status."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    path_item = schema["paths"].get("/api/v1/documents/{document_id}")
    assert path_item is not None, "Endpoint path not registered in OpenAPI"
    assert "delete" in path_item, "DELETE operation not defined on path"

    delete_op = path_item["delete"]
    assert "204" in delete_op["responses"], "204 No Content response not defined"
    assert "Zero-Retention" in delete_op["summary"] or "Zero-Retention" in delete_op["description"]


@pytest.mark.asyncio
async def test_delete_document_with_content_hash_when_blob_id_is_none(
    client: AsyncClient,
    mock_db: InMemoryAsyncDeleteSession,
    mock_storage: MagicMock,
) -> None:
    """Test fallback to content_hash lookup when document blob_id is None."""
    doc_id = uuid4()
    blob_id = uuid4()
    content_hash = "fallbackhash0123456789abcdef0123456789abcdef0123456789abcdef01"

    blob = _create_sample_blob(blob_id, content_hash, ref_count=1)
    doc = _create_sample_doc(doc_id, None, content_hash)  # type: ignore[arg-type]
    doc.blob_id = None
    mock_db.add(blob)
    mock_db.add(doc)

    response = await client.delete(f"/api/v1/documents/{doc_id}")

    assert response.status_code == 204
    assert doc_id not in mock_db.documents
    assert blob_id not in mock_db.blobs
    mock_storage.delete_blob.assert_awaited_once_with(content_hash)


@pytest.mark.asyncio
async def test_delete_document_when_physical_blob_already_missing_on_disk(
    client: AsyncClient,
    mock_db: InMemoryAsyncDeleteSession,
    mock_storage: MagicMock,
) -> None:
    """Test graceful handling when physical blob was already purged or missing from storage."""
    doc_id = uuid4()
    blob_id = uuid4()
    content_hash = "missingdiskfile0123456789abcdef0123456789abcdef0123456789abcdef"

    blob = _create_sample_blob(blob_id, content_hash, ref_count=1)
    doc = _create_sample_doc(doc_id, blob_id, content_hash)
    mock_db.add(blob)
    mock_db.add(doc)

    # Physical storage reports file did not exist
    mock_storage.delete_blob.return_value = False

    response = await client.delete(f"/api/v1/documents/{doc_id}")

    assert response.status_code == 204
    assert doc_id not in mock_db.documents
    assert blob_id not in mock_db.blobs
    mock_storage.delete_blob.assert_awaited_once_with(content_hash)
