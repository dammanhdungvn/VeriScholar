"""Automated integration tests for Module 2: Drafting Workspace, Compile Broker & SAFE."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.chunk import DocumentChunkModel
from api.db.models.draft import (
    DraftCommentModel,
    DraftModel,
    DraftVerificationModel,
)
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import DEFAULT_DEV_USER_ID, get_current_user, get_storage
from core.ports.storage import IBlobStoragePort
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class InMemoryDraftStore:
    """In-memory database double for drafts, comments, chunks, and SAFE verifications."""

    def __init__(self) -> None:
        self.drafts: dict[UUID, DraftModel] = {}
        self.comments: dict[UUID, DraftCommentModel] = {}
        self.verifications: dict[UUID, DraftVerificationModel] = {}
        self.chunks: dict[UUID, DocumentChunkModel] = {}

    def add(self, obj: object) -> None:
        now = datetime.now(UTC)
        if isinstance(obj, DraftModel):
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            if getattr(obj, "updated_at", None) is None:
                obj.updated_at = now
            if getattr(obj, "version", None) is None:
                obj.version = 1
            if getattr(obj, "format", None) is None:
                obj.format = "latex"
            if getattr(obj, "template", None) is None:
                obj.template = "ieee_conference"
            self.drafts[obj.id] = obj

        elif isinstance(obj, DraftCommentModel):
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            if getattr(obj, "updated_at", None) is None:
                obj.updated_at = now
            self.comments[obj.id] = obj
        elif isinstance(obj, DraftVerificationModel):
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            self.verifications[obj.id] = obj
        elif isinstance(obj, DocumentChunkModel):
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()
            self.chunks[obj.id] = obj

    async def delete(self, obj: object) -> None:
        if isinstance(obj, DraftModel) and obj.id in self.drafts:
            del self.drafts[obj.id]

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

        # Count queries
        if "count(drafts.id)" in stmt_str.lower():
            matching_drafts = [d for d in self.drafts.values() if d.user_id == DEFAULT_DEV_USER_ID]
            mock_res.scalar_one.return_value = len(matching_drafts)
            return mock_res

        if "count(draft_comments.id)" in stmt_str.lower():
            target_draft_id = None
            for v in params.values():
                if isinstance(v, UUID) and v in self.drafts:
                    target_draft_id = v
                    break
            matching_comments = [
                c
                for c in self.comments.values()
                if target_draft_id is None or c.draft_id == target_draft_id
            ]
            mock_res.scalar_one.return_value = len(matching_comments)
            return mock_res

        # Select drafts
        if "FROM drafts" in stmt_str:
            target_id = None
            target_user = None
            for v in params.values():
                if isinstance(v, UUID):
                    if v in self.drafts:
                        target_id = v
                    elif v == DEFAULT_DEV_USER_ID:
                        target_user = v

            matching = list(self.drafts.values())
            if target_id:
                matching = [d for d in matching if d.id == target_id]
            if target_user:
                matching = [d for d in matching if d.user_id == target_user]

            int_params = [
                v for v in params.values() if isinstance(v, int) and not isinstance(v, bool)
            ]

            if len(int_params) >= 2:
                limit_val, offset_val = int_params[0], int_params[1]
                sliced_matching = matching[offset_val : offset_val + limit_val]
            elif len(int_params) == 1:
                sliced_matching = matching[: int_params[0]]
            else:
                sliced_matching = matching

            mock_res.scalar_one_or_none.return_value = matching[0] if matching else None
            mock_res.scalars.return_value.all.return_value = sliced_matching
            return mock_res

        # Select comments
        if "FROM draft_comments" in stmt_str:
            target_draft_id = None
            for v in params.values():
                if isinstance(v, UUID) and v in self.drafts:
                    target_draft_id = v
                    break

            matching = list(self.comments.values())
            if target_draft_id:
                matching = [c for c in matching if c.draft_id == target_draft_id]

            mock_res.scalars.return_value.all.return_value = matching
            return mock_res

        # Select chunks for SAFE Fact-Checking
        if "FROM document_chunks" in stmt_str:
            chunks = list(self.chunks.values())
            mock_res.scalars.return_value.all.return_value = chunks
            return mock_res

        mock_res.scalar_one_or_none.return_value = None
        mock_res.scalars.return_value.all.return_value = []
        return mock_res


@pytest.fixture
def draft_store() -> InMemoryDraftStore:
    return InMemoryDraftStore()


@pytest.fixture
def mock_db_session(draft_store: InMemoryDraftStore) -> AsyncSession:
    return draft_store  # type: ignore[return-value]


@pytest.fixture
def mock_user() -> UserModel:
    user = UserModel(
        email="author@verischolar.org",
        full_name="Academic Author",
        is_active=True,
    )
    user.id = DEFAULT_DEV_USER_ID
    return user


@pytest.fixture
def mock_storage() -> MagicMock:
    return MagicMock(spec=IBlobStoragePort)


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
async def test_create_and_get_draft(
    client: AsyncClient,
    draft_store: InMemoryDraftStore,
) -> None:
    """Create a draft, checking Location and ETag headers, and retrieve it."""
    resp = await client.post(
        "/api/v1/drafts",
        json={
            "title": "A Survey on Self-Attention",
            "format": "latex",
            "template": "ieee_conference",
            "initial_content": (
                "\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}"
            ),
        },
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    draft_id = data["id"]
    assert data["title"] == "A Survey on Self-Attention"
    assert data["version"] == 1
    assert resp.headers["etag"] == '"v1"'
    assert f"/api/v1/drafts/{draft_id}" in resp.headers["location"]

    # Retrieve draft
    get_resp = await client.get(f"/api/v1/drafts/{draft_id}")
    assert get_resp.status_code == 200
    assert get_resp.headers["etag"] == '"v1"'
    assert get_resp.json()["data"]["content"] == data["content"]


@pytest.mark.asyncio
async def test_list_drafts_pagination(
    client: AsyncClient,
    draft_store: InMemoryDraftStore,
    mock_user: UserModel,
) -> None:
    """List drafts with RFC 8288 style pagination envelope."""
    for i in range(3):
        draft_store.add(
            DraftModel(
                id=uuid4(),
                user_id=mock_user.id,
                title=f"Paper Draft {i + 1}",
                content=f"Content {i + 1}",
                version=1,
            )
        )

    resp = await client.get("/api/v1/drafts?page=1&per_page=2")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]) == 2
    assert body["meta"]["total"] == 3
    assert body["meta"]["page"] == 1
    assert body["meta"]["per_page"] == 2
    assert body["meta"]["total_pages"] == 2


@pytest.mark.asyncio
async def test_update_draft_occ_success_and_conflict(
    client: AsyncClient,
    draft_store: InMemoryDraftStore,
    mock_user: UserModel,
) -> None:
    """Enforce RFC 9110 / RFC 7232 OCC with If-Match header."""
    draft = DraftModel(
        id=uuid4(),
        user_id=mock_user.id,
        title="Attention Mechanism Draft",
        content="Initial code",
        version=1,
    )
    draft_store.add(draft)

    # 1. Missing If-Match -> 412 PRECONDITION_FAILED
    missing_resp = await client.put(
        f"/api/v1/drafts/{draft.id}",
        json={"content": "New updated content"},
    )
    assert missing_resp.status_code == 412
    assert missing_resp.json()["error"]["code"] == "PRECONDITION_REQUIRED"

    # 2. Conflicting/Stale If-Match -> 412 PRECONDITION_FAILED
    stale_resp = await client.put(
        f"/api/v1/drafts/{draft.id}",
        headers={"If-Match": '"v99"'},
        json={"content": "New updated content"},
    )
    assert stale_resp.status_code == 412
    assert stale_resp.json()["error"]["code"] == "CONCURRENCY_CONFLICT"

    # 3. Correct If-Match -> 200 OK, version incremented
    ok_resp = await client.put(
        f"/api/v1/drafts/{draft.id}",
        headers={"If-Match": '"v1"'},
        json={"content": "New updated content"},
    )
    assert ok_resp.status_code == 200
    assert ok_resp.headers["etag"] == '"v2"'
    data = ok_resp.json()["data"]
    assert data["version"] == 2
    assert data["content"] == "New updated content"


@pytest.mark.asyncio
async def test_patch_draft_metadata(
    client: AsyncClient,
    draft_store: InMemoryDraftStore,
    mock_user: UserModel,
) -> None:
    """Patch draft metadata with OCC If-Match header."""
    draft = DraftModel(
        id=uuid4(),
        user_id=mock_user.id,
        title="Old Title",
        template="ieee_conference",
        content="...",
        version=2,
    )
    draft_store.add(draft)

    resp = await client.patch(
        f"/api/v1/drafts/{draft.id}",
        headers={"If-Match": '"v2"'},
        json={"title": "Updated Title via Patch"},
    )
    assert resp.status_code == 200
    assert resp.headers["etag"] == '"v3"'
    assert resp.json()["data"]["title"] == "Updated Title via Patch"
    assert resp.json()["data"]["version"] == 3


@pytest.mark.asyncio
async def test_delete_draft(
    client: AsyncClient,
    draft_store: InMemoryDraftStore,
    mock_user: UserModel,
) -> None:
    """Delete draft permanently."""
    draft = DraftModel(
        id=uuid4(),
        user_id=mock_user.id,
        title="To Delete",
        content="...",
        version=1,
    )
    draft_store.add(draft)

    resp = await client.delete(f"/api/v1/drafts/{draft.id}")
    assert resp.status_code == 204

    # Subsequent GET returns 404
    get_resp = await client.get(f"/api/v1/drafts/{draft.id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_draft_comments(
    client: AsyncClient,
    draft_store: InMemoryDraftStore,
    mock_user: UserModel,
) -> None:
    """Add and list line-level peer review comments on draft."""
    draft = DraftModel(
        id=uuid4(),
        user_id=mock_user.id,
        title="Reviewable Draft",
        content="Line 1\nLine 2\nLine 3",
        version=1,
    )
    draft_store.add(draft)

    # 1. Add comment
    add_resp = await client.post(
        f"/api/v1/drafts/{draft.id}/comments",
        json={
            "line_number": 2,
            "selected_text": "Line 2",
            "comment": "Consider citing Vaswani et al. here.",
        },
    )
    assert add_resp.status_code == 201
    c_data = add_resp.json()["data"]
    assert c_data["line_number"] == 2
    assert c_data["selected_text"] == "Line 2"
    assert c_data["comment"] == "Consider citing Vaswani et al. here."

    # 2. List comments
    list_resp = await client.get(f"/api/v1/drafts/{draft.id}/comments")
    assert list_resp.status_code == 200
    list_body = list_resp.json()
    assert list_body["success"] is True
    assert len(list_body["data"]) == 1
    assert list_body["data"][0]["line_number"] == 2


@pytest.mark.asyncio
async def test_compile_draft_sse_stream(
    client: AsyncClient,
    draft_store: InMemoryDraftStore,
    mock_user: UserModel,
) -> None:
    """Compile LaTeX draft, receiving SSE stream with linter and compile events."""
    draft = DraftModel(
        id=uuid4(),
        user_id=mock_user.id,
        title="Compilable Draft",
        content="\\documentclass{article}\n\\begin{document}\nHello Science\n\\end{document}",
        version=1,
    )
    draft_store.add(draft)

    resp = await client.post(f"/api/v1/drafts/{draft.id}:compile")
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
    text = resp.text
    assert "event: linter_status" in text
    assert "event: sandbox_started" in text
    assert "event: compile_success" in text


@pytest.mark.asyncio
async def test_safe_fact_checking(
    client: AsyncClient,
    draft_store: InMemoryDraftStore,
    mock_user: UserModel,
) -> None:
    """Run 4-stage SAFE Fact-Checking on draft text with NLI grounding and Bounding Boxes."""
    doc_id = uuid4()
    chunk = DocumentChunkModel(
        id=uuid4(),
        document_id=doc_id,
        chunk_index=0,
        page_number=1,
        content=(
            "The Transformer model establishes a new state of the art "
            "achieving 28.4 BLEU score on WMT 2014 English-to-German."
        ),
        bounding_boxes=[[0.1, 0.2, 0.9, 0.35, 1]],
        token_count=22,
        embedding=[0.0] * 1536,
    )
    draft_store.add(chunk)

    draft = DraftModel(
        id=uuid4(),
        user_id=mock_user.id,
        title="Fact Checked Paper",
        content="Some draft text",
        version=1,
    )
    draft_store.add(draft)

    resp = await client.post(
        f"/api/v1/drafts/{draft.id}:verify-claims",
        json={
            "selected_text": (
                "The Transformer model establishes state of the art "
                "achieving 28.4 BLEU on English-to-German."
            ),
        },
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["total_claims"] >= 1
    assert data["supported_count"] >= 1

    first_claim = data["claims"][0]
    assert first_claim["verdict"] == "supported"
    assert first_claim["confidence"] >= 0.6
    assert first_claim["citation"] is not None
    assert first_claim["citation"]["page_number"] == 1
    # Preserves normalized BoundingBox coordinates [x0, y0, x1, y1, page]
    bb = first_claim["citation"]["bounding_boxes"][0]
    assert len(bb) == 5
    assert bb[4] == 1  # 1-indexed page


@pytest.mark.asyncio
async def test_export_draft_bundle_zip(
    client: AsyncClient,
    draft_store: InMemoryDraftStore,
    mock_user: UserModel,
) -> None:
    """Test camera-ready bundle export as ZIP archive containing TeX, bib, README, and PDF."""
    import io
    import zipfile

    draft = DraftModel(
        id=uuid4(),
        user_id=mock_user.id,
        title="Attention Is All You Need",
        content="\\documentclass{article}\n\\begin{document}\nHello World\n\\end{document}",
        format="latex",
        template="ieee_conference",
        version=1,
    )
    draft_store.add(draft)

    resp = await client.get(f"/api/v1/drafts/{draft.id}/bundle?format=zip")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"
    assert "camera_ready_bundle.zip" in resp.headers["content-disposition"]

    # Verify zip content
    zip_bytes = resp.content
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        file_list = zf.namelist()
        assert "main.tex" in file_list
        assert "references.bib" in file_list
        assert "README.txt" in file_list
        assert "camera_ready.pdf" in file_list

        main_tex = zf.read("main.tex").decode()
        assert "Hello World" in main_tex


@pytest.mark.asyncio
async def test_export_draft_bundle_pdf(
    client: AsyncClient,
    draft_store: InMemoryDraftStore,
    mock_user: UserModel,
) -> None:
    """Test camera-ready bundle export directly as compiled PDF."""
    draft = DraftModel(
        id=uuid4(),
        user_id=mock_user.id,
        title="Direct PDF Paper",
        content="\\documentclass{article}",
        version=1,
    )
    draft_store.add(draft)

    resp = await client.get(f"/api/v1/drafts/{draft.id}/bundle?format=pdf")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert "attachment; filename=" in resp.headers["content-disposition"]
    assert resp.content.startswith(b"%PDF-1.7")
