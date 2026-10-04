"""Automated integration tests for Public Resource Sharing & Instant Revocation."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.document import DocumentModel
from api.db.models.note import ResearchNoteModel
from api.db.models.share import ShareModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import DEFAULT_DEV_USER_ID, get_current_user, get_storage
from core.ports.storage import IBlobStoragePort
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class InMemoryShareStore:
    """In-memory store for public sharing and revocation tests."""

    def __init__(self) -> None:
        self.shares: dict[UUID, ShareModel] = {}
        self.documents: dict[UUID, DocumentModel] = {}
        self.notes: dict[UUID, ResearchNoteModel] = {}

    def add(self, obj: object) -> None:
        now = datetime.now(UTC)
        if isinstance(obj, ShareModel):
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            self.shares[obj.id] = obj
        elif isinstance(obj, DocumentModel):
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            self.documents[obj.id] = obj
        elif isinstance(obj, ResearchNoteModel):
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            self.notes[obj.id] = obj

    async def flush(self) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
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

        mock_res = MagicMock()

        # 1. Query shares
        if "FROM shares" in stmt_str:
            token_val = None
            for k, v in params.items():
                if "token" in k.lower():
                    token_val = str(v)
                    break
            matching = [
                s for s in self.shares.values() if token_val is None or s.token == token_val
            ]

            mock_res.scalar_one_or_none.return_value = matching[0] if matching else None
            mock_res.scalars.return_value.all.return_value = matching
            return mock_res

        # 2. Query notes
        if "FROM research_notes" in stmt_str:
            target_id = None
            user_id = None
            for k, v in params.items():
                if isinstance(v, UUID) and v in self.notes:
                    target_id = v
                elif "user_id" in k.lower() and isinstance(v, UUID):
                    user_id = v

            matching_notes = list(self.notes.values())
            if target_id:
                matching_notes = [n for n in matching_notes if n.id == target_id]
            if user_id:
                matching_notes = [n for n in matching_notes if n.user_id == user_id]

            mock_res.scalar_one_or_none.return_value = matching_notes[0] if matching_notes else None
            mock_res.scalars.return_value.all.return_value = matching_notes
            return mock_res

        # 3. Query documents
        if "FROM documents" in stmt_str:
            target_id = None
            user_id = None
            for k, v in params.items():
                if isinstance(v, UUID) and v in self.documents:
                    target_id = v
                elif "user_id" in k.lower() and isinstance(v, UUID):
                    user_id = v

            matching_docs = list(self.documents.values())
            if target_id:
                matching_docs = [d for d in matching_docs if d.id == target_id]
            if user_id:
                matching_docs = [d for d in matching_docs if d.user_id == user_id]

            mock_res.scalar_one_or_none.return_value = matching_docs[0] if matching_docs else None
            mock_res.scalars.return_value.all.return_value = matching_docs
            return mock_res

        mock_res.scalar_one_or_none.return_value = None
        mock_res.scalars.return_value.all.return_value = []
        return mock_res


@pytest.fixture
def share_store() -> InMemoryShareStore:
    return InMemoryShareStore()


@pytest.fixture
def mock_db_session(share_store: InMemoryShareStore) -> AsyncSession:
    return share_store  # type: ignore[return-value]


@pytest.fixture
def mock_user() -> UserModel:
    user = UserModel(
        email="owner@verischolar.org",
        full_name="Resource Owner",
        is_active=True,
    )
    user.id = DEFAULT_DEV_USER_ID
    return user


@pytest.fixture
def mock_storage() -> MagicMock:
    storage = MagicMock(spec=IBlobStoragePort)

    async def dummy_stream(
        content_hash: str,
        start_byte: int = 0,
        end_byte: int | None = None,
        chunk_size: int = 64 * 1024,
    ) -> AsyncGenerator[bytes, None]:
        data = b"%PDF-1.7 sample pdf content for public sharing stream test"
        if end_byte is not None:
            yield data[start_byte : end_byte + 1]
        else:
            yield data[start_byte:]

    storage.stream_blob_range.side_effect = dummy_stream
    return storage


@pytest.fixture
def client(
    mock_db_session: AsyncSession,
    mock_user: UserModel,
    mock_storage: MagicMock,
) -> Generator[AsyncClient, None, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield mock_db_session

    async def override_get_current_user() -> UserModel:
        return mock_user

    def override_get_storage() -> IBlobStoragePort:
        return mock_storage

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_storage] = override_get_storage

    transport = ASGITransport(app=app)
    async_client = AsyncClient(transport=transport, base_url="http://testserver")
    yield async_client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_share_note_success(
    client: AsyncClient,
    share_store: InMemoryShareStore,
    mock_user: UserModel,
) -> None:
    """Test generating a public shareable link for an owned note."""
    note = ResearchNoteModel(
        id=uuid4(),
        user_id=mock_user.id,
        selected_text="Key Findings on Attention Mechanisms",
        page_number=1,
        user_note="Self-attention allows parallelization.",
    )
    share_store.add(note)

    resp = await client.post(
        "/api/v1/shares",
        json={"resource_type": "note", "resource_id": str(note.id)},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["resource_type"] == "note"
    assert data["resource_id"] == str(note.id)
    assert "share_token" in data
    assert f"/share/{data['share_token']}" in data["share_url"]


@pytest.mark.asyncio
async def test_create_share_unauthorized_resource(
    client: AsyncClient,
    share_store: InMemoryShareStore,
) -> None:
    """Attempting to share another user's note returns 404 NOT_FOUND."""
    stranger_id = uuid4()
    note = ResearchNoteModel(
        id=uuid4(),
        user_id=stranger_id,
        selected_text="Stranger Private Note",
        page_number=1,
        user_note="Secret draft.",
    )
    share_store.add(note)

    resp = await client.post(
        "/api/v1/shares",
        json={"resource_type": "note", "resource_id": str(note.id)},
    )
    assert resp.status_code == 404
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "RESOURCE_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_public_share_zero_auth(
    client: AsyncClient,
    share_store: InMemoryShareStore,
    mock_user: UserModel,
) -> None:
    """Guests can access shared resource snapshot without any authorization credentials."""
    note = ResearchNoteModel(
        id=uuid4(),
        user_id=mock_user.id,
        selected_text="Publicly Shared Note Content",
        page_number=2,
        user_note="Open science commentary.",
    )
    share_store.add(note)

    share = ShareModel(
        id=uuid4(),
        token="tok_pub_abc123",
        resource_type="note",
        resource_id=note.id,
        user_id=mock_user.id,
        permission="read_only",
        is_revoked=False,
    )
    share_store.add(share)

    # Note: Request has NO Authorization header
    resp = await client.get(f"/api/v1/shares/{share.token}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["share_token"] == "tok_pub_abc123"
    assert data["resource_type"] == "note"
    assert data["resource_data"]["selected_text"] == "Publicly Shared Note Content"
    assert data["resource_data"]["user_note"] == "Open science commentary."


@pytest.mark.asyncio
async def test_get_public_share_non_existent(client: AsyncClient) -> None:
    """Querying a non-existent share token returns 404 NOT_FOUND."""
    resp = await client.get("/api/v1/shares/non_existent_token_12345")
    assert resp.status_code == 404
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "SHARE_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_shared_file_streaming_and_range(
    client: AsyncClient,
    share_store: InMemoryShareStore,
    mock_user: UserModel,
) -> None:
    """Stream PDF for a shared document with zero auth and HTTP 206 Partial Content."""

    doc = DocumentModel(
        id=uuid4(),
        user_id=mock_user.id,
        filename="paper.pdf",
        content_hash="hash_pdf_sample",
        file_size_bytes=58,
        status="completed",
        is_persistent=True,
    )
    share_store.add(doc)

    share = ShareModel(
        id=uuid4(),
        token="tok_doc_share_789",
        resource_type="document",
        resource_id=doc.id,
        user_id=mock_user.id,
        permission="read_only",
        is_revoked=False,
    )
    share_store.add(share)

    # 1. Full stream request
    resp = await client.get(f"/api/v1/shares/{share.token}/file")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert b"%PDF-1.7 sample pdf content" in resp.content

    # 2. Byte Range request (RFC 7233)
    range_resp = await client.get(
        f"/api/v1/shares/{share.token}/file",
        headers={"Range": "bytes=0-9"},
    )
    assert range_resp.status_code == 206
    assert range_resp.headers["accept-ranges"] == "bytes"
    assert "bytes 0-9/58" in range_resp.headers["content-range"]
    assert len(range_resp.content) == 10


@pytest.mark.asyncio
async def test_revoke_share_instant_revocation_410(
    client: AsyncClient,
    share_store: InMemoryShareStore,
    mock_user: UserModel,
) -> None:
    """Owner revokes share link, immediately causing 410 Gone for subsequent public reads."""
    note = ResearchNoteModel(
        id=uuid4(),
        user_id=mock_user.id,
        selected_text="Revocable Note",
        page_number=1,
        user_note="Will be private soon.",
    )
    share_store.add(note)

    share = ShareModel(
        id=uuid4(),
        token="tok_to_revoke_xyz",
        resource_type="note",
        resource_id=note.id,
        user_id=mock_user.id,
        permission="read_only",
        is_revoked=False,
    )
    share_store.add(share)

    # 1. Owner revokes the link
    del_resp = await client.delete(f"/api/v1/shares/{share.token}")
    assert del_resp.status_code == 204

    # 2. Subsequent public read immediately returns HTTP 410 Gone
    read_resp = await client.get(f"/api/v1/shares/{share.token}")
    assert read_resp.status_code == 410
    body = read_resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "SHARE_REVOKED"

    # 3. File access also returns HTTP 410 Gone
    file_resp = await client.get(f"/api/v1/shares/{share.token}/file")
    assert file_resp.status_code == 410


@pytest.mark.asyncio
async def test_revoke_share_unauthorized_user(
    client: AsyncClient,
    share_store: InMemoryShareStore,
    mock_user: UserModel,
) -> None:
    """Non-owner cannot revoke another user's share link, returning 403 Forbidden."""
    other_user_id = uuid4()
    share = ShareModel(
        id=uuid4(),
        token="tok_other_user",
        resource_type="document",
        resource_id=uuid4(),
        user_id=other_user_id,
        permission="read_only",
        is_revoked=False,
    )
    share_store.add(share)

    resp = await client.delete(f"/api/v1/shares/{share.token}")
    assert resp.status_code == 403
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "REVOCATION_FORBIDDEN"
