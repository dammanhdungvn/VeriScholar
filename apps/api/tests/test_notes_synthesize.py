"""Automated integration tests for POST /api/v1/notes:synthesize (#21)."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.note import NoteSynthesisModel, ResearchNoteModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import DEFAULT_DEV_USER_ID, get_current_user, get_idempotency_port
from core.adapters.cache.idempotency import InMemoryIdempotencyAdapter
from core.ports.idempotency import IIdempotencyPort
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class InMemorySynthesisStore:
    """In-memory store for note synthesis tests."""

    def __init__(self) -> None:
        self.notes: dict[UUID, ResearchNoteModel] = {}
        self.syntheses: dict[UUID, NoteSynthesisModel] = {}

    def add(self, obj: object) -> None:
        now = datetime.now(UTC)
        if isinstance(obj, ResearchNoteModel):
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            if getattr(obj, "updated_at", None) is None:
                obj.updated_at = now
            self.notes[obj.id] = obj
        elif isinstance(obj, NoteSynthesisModel):
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            if getattr(obj, "updated_at", None) is None:
                obj.updated_at = now
            self.syntheses[obj.id] = obj

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
        if "FROM research_notes" in stmt_str:
            mock_res = MagicMock()
            notes_list = [n for n in self.notes.values() if n.user_id == DEFAULT_DEV_USER_ID]
            mock_res.scalars.return_value.all.return_value = notes_list
            return mock_res

        mock_res = MagicMock()
        mock_res.scalars.return_value.all.return_value = []
        return mock_res


@pytest.fixture
def synthesis_store() -> InMemorySynthesisStore:
    return InMemorySynthesisStore()


@pytest.fixture
def test_idempotency_adapter() -> InMemoryIdempotencyAdapter:
    return InMemoryIdempotencyAdapter()


@pytest.fixture
def default_user() -> UserModel:
    return UserModel(
        id=DEFAULT_DEV_USER_ID,
        email="developer@verischolar.org",
        full_name="VeriScholar Developer",
        hashed_password="dummy",
        is_active=True,
    )


@pytest.fixture
def client(
    synthesis_store: InMemorySynthesisStore,
    test_idempotency_adapter: InMemoryIdempotencyAdapter,
    default_user: UserModel,
) -> Generator[AsyncClient, None, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield synthesis_store  # type: ignore[misc]

    async def override_get_current_user() -> UserModel:
        return default_user

    def override_idempotency_port() -> IIdempotencyPort:
        return test_idempotency_adapter

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_idempotency_port] = override_idempotency_port

    transport = ASGITransport(app=app)
    async_client = AsyncClient(transport=transport, base_url="http://testserver")
    yield async_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_notes(synthesis_store: InMemorySynthesisStore) -> list[ResearchNoteModel]:
    n1 = ResearchNoteModel(
        id=uuid4(),
        user_id=DEFAULT_DEV_USER_ID,
        document_id=uuid4(),
        selected_text="Attention(Q, K, V) = softmax(QK^T / sqrt(d_k))V",
        bounding_boxes=[[0.2, 0.3, 0.4, 0.8, 4]],
        page_number=4,
        user_note="Công thức tính Scaled Dot-Product Attention.",
        tags=["formula", "attention"],
        frozen_snapshot={
            "document_title": "Attention Is All You Need",
            "authors": ["Ashish Vaswani", "Noam Shazeer"],
            "year": 2017,
        },
        is_source_detached=False,
        version=1,
    )
    n2 = ResearchNoteModel(
        id=uuid4(),
        user_id=DEFAULT_DEV_USER_ID,
        document_id=uuid4(),
        selected_text=(
            "Multi-head attention allows the model to jointly attend to "
            "information from different representation subspaces."
        ),
        bounding_boxes=[[0.5, 0.2, 0.7, 0.8, 5]],
        page_number=5,
        user_note="Ý nghĩa của nhiều đầu chú ý.",
        tags=["concept", "subspaces"],
        frozen_snapshot={
            "document_title": "Attention Is All You Need",
            "authors": ["Ashish Vaswani", "Noam Shazeer"],
            "year": 2017,
        },
        is_source_detached=False,
        version=1,
    )
    synthesis_store.add(n1)
    synthesis_store.add(n2)
    return [n1, n2]


@pytest.mark.asyncio
async def test_synthesize_notes_concept_lesson_success(
    client: AsyncClient, sample_notes: list[ResearchNoteModel]
) -> None:
    """POST /api/v1/notes:synthesize creates concept lesson with interactive citation badges."""
    payload = {
        "note_ids": [str(n.id) for n in sample_notes],
        "mode": "concept_lesson",
        "language": "vi",
        "target_title": "Bài Học Khái Niệm Cơ Chế Chú Ý (Attention)",
    }
    resp = await client.post("/api/v1/notes:synthesize", json=payload)
    assert resp.status_code == 200

    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["title"] == payload["target_title"]
    assert data["mode"] == "concept_lesson"
    assert "## 1. Trực Giác Cốt Lõi" in data["markdown_content"]
    assert "[^badge_1]" in data["markdown_content"]
    assert "[^badge_2]" in data["markdown_content"]

    # Verify interactive badges
    badges = data["interactive_badges"]
    assert len(badges) == 2
    assert badges[0]["badge_id"] == "badge_1"
    assert "Vaswani et al., 2017 • Tr. 4" in badges[0]["citation_label"]
    assert badges[0]["page_number"] == 4
    assert len(badges[0]["bounding_boxes"]) == 1


@pytest.mark.asyncio
async def test_synthesize_notes_literature_review_mode(
    client: AsyncClient, sample_notes: list[ResearchNoteModel]
) -> None:
    """POST /api/v1/notes:synthesize generates literature review synthesis."""
    payload = {
        "note_ids": [str(n.id) for n in sample_notes],
        "mode": "literature_review",
        "language": "vi",
    }
    resp = await client.post("/api/v1/notes:synthesize", json=payload)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["mode"] == "literature_review"
    assert "Bối Cảnh Nghiên Cứu & Trường Phái Học Thuật" in data["markdown_content"]


@pytest.mark.asyncio
async def test_synthesize_notes_research_gap_mode(
    client: AsyncClient, sample_notes: list[ResearchNoteModel]
) -> None:
    """POST /api/v1/notes:synthesize generates research gap analysis."""
    payload = {
        "note_ids": [str(n.id) for n in sample_notes],
        "mode": "research_gap",
        "language": "vi",
    }
    resp = await client.post("/api/v1/notes:synthesize", json=payload)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["mode"] == "research_gap"
    assert "Những Giả Định Chưa Được Chứng Minh Trọn Vẹn" in data["markdown_content"]


@pytest.mark.asyncio
async def test_synthesize_notes_idempotency_cache(
    client: AsyncClient, sample_notes: list[ResearchNoteModel]
) -> None:
    """POST /api/v1/notes:synthesize returns cached result on duplicate Idempotency-Key."""
    key = f"idem-key-{uuid4().hex[:8]}"
    payload = {
        "note_ids": [str(n.id) for n in sample_notes],
        "mode": "concept_lesson",
        "target_title": "First Run Title",
    }

    resp1 = await client.post(
        "/api/v1/notes:synthesize",
        json=payload,
        headers={"Idempotency-Key": key},
    )
    assert resp1.status_code == 200
    res1_data = resp1.json()["data"]

    # Replay with same Idempotency-Key
    resp2 = await client.post(
        "/api/v1/notes:synthesize",
        json=payload,
        headers={"Idempotency-Key": key},
    )
    assert resp2.status_code == 200
    res2_data = resp2.json()["data"]

    assert res1_data["id"] == res2_data["id"]
    assert res1_data["title"] == res2_data["title"]


@pytest.mark.asyncio
async def test_synthesize_notes_empty_notes_fails(client: AsyncClient) -> None:
    """POST /api/v1/notes:synthesize returns 422 when note_ids is empty."""
    resp = await client.post(
        "/api/v1/notes:synthesize",
        json={"note_ids": []},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_synthesize_notes_active_recall_quiz_mode(
    client: AsyncClient, sample_notes: list[ResearchNoteModel]
) -> None:
    """POST /api/v1/notes:synthesize creates an Active Recall Quiz with collapsible answers."""
    payload = {
        "note_ids": [str(n.id) for n in sample_notes],
        "mode": "active_recall_quiz",
        "language": "vi",
    }
    resp = await client.post("/api/v1/notes:synthesize", json=payload)
    assert resp.status_code == 200

    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["mode"] == "active_recall_quiz"
    assert "Active Recall Flashcards" in data["markdown_content"]
    assert "<details>" in data["markdown_content"]
    assert "<summary>👉 Bấm để xem đáp án" in data["markdown_content"]
    assert "[^badge_1]" in data["markdown_content"]
    assert len(data["interactive_badges"]) == 2
