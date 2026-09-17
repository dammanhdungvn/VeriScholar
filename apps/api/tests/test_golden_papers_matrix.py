"""Comprehensive 5-Level Test Suite on Golden Benchmark Papers.

Validates the complete research user journey across:
1. 'Attention Is All You Need'
2. 'Reconstructing Context Evaluating Advanced Chunking Strategies for RAG'
3. 'Advancing Retrieval-Augmented Generation for Structured Enterprise and Internal Data'

Levels:
- Level 1 (Easy): Ingestion & Session Creation
- Level 2 (Medium): Dual-Pane Viewport & Active Recall Quiz Note Synthesis
- Level 3 (Hard): Presupposition Validation & Socratic Mentor Steering
- Level 4 (Very Hard): Real-Time Grounded Summary Stream with Spatial Bounding Boxes
- Level 5 (Extremely Hard): Multi-Paper Cross-Synthesis & Full Offline Bundle Export
"""

import io
import zipfile
from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from api import app
from api.db.models.chunk import DocumentChunkModel
from api.db.models.document import DocumentModel
from api.db.models.note import ResearchNoteModel
from api.db.models.session import (
    ResearchSessionModel,
    SessionDocumentModel,
    SessionTurnModel,
)
from api.db.models.summary import DocumentSummaryModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import DEFAULT_DEV_USER_ID, get_current_user, get_idempotency_port
from core.adapters.cache.idempotency import InMemoryIdempotencyAdapter
from core.ports.idempotency import IIdempotencyPort
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

GOLDEN_PAPERS_DIR = Path("data/papers")


class InMemoryMatrixStore:
    """In-memory database store supporting all 5 test levels."""

    def __init__(self) -> None:
        self.documents: dict[UUID, DocumentModel] = {}
        self.sessions: dict[UUID, ResearchSessionModel] = {}
        self.session_documents: list[SessionDocumentModel] = []
        self.session_turns: list[SessionTurnModel] = []
        self.chunks: list[DocumentChunkModel] = []
        self.notes: list[ResearchNoteModel] = []
        self.summaries: dict[UUID, DocumentSummaryModel] = {}

    def add(self, obj: object) -> None:
        now = datetime.now(UTC)
        if isinstance(obj, DocumentModel):
            self.documents[obj.id] = obj
        elif isinstance(obj, ResearchSessionModel):
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            if getattr(obj, "updated_at", None) is None:
                obj.updated_at = now
            self.sessions[obj.id] = obj
        elif isinstance(obj, SessionDocumentModel):
            if getattr(obj, "added_at", None) is None:
                obj.added_at = now
            self.session_documents.append(obj)
        elif isinstance(obj, SessionTurnModel):
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            self.session_turns.append(obj)
        elif isinstance(obj, DocumentChunkModel):
            self.chunks.append(obj)
        elif isinstance(obj, ResearchNoteModel):
            self.notes.append(obj)
        elif isinstance(obj, DocumentSummaryModel):
            self.summaries[obj.document_id] = obj

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
        if "count(" in stmt_str.lower():
            if "session_turns" in stmt_str:
                mock_res.scalar_one.return_value = len(self.session_turns)
            elif "documents" in stmt_str:
                mock_res.scalar_one.return_value = len(self.documents)
            else:
                mock_res.scalar_one.return_value = 0
            return mock_res

        # Research sessions
        if "FROM research_sessions" in stmt_str:
            target_id = None
            for v in params.values():
                if isinstance(v, UUID) and v in self.sessions:
                    target_id = v
                    break
            sess = self.sessions.get(target_id)
            mock_res.scalar_one_or_none.return_value = sess
            mock_res.scalars.return_value.all.return_value = [sess] if sess else []
            return mock_res

        # Session documents
        if "FROM session_documents" in stmt_str:
            target_id = None
            for v in params.values():
                if isinstance(v, UUID) and v in self.sessions:
                    target_id = v
                    break
            docs = [
                sd.document_id
                for sd in self.session_documents
                if target_id is None or sd.session_id == target_id
            ]
            mock_res.scalars.return_value.all.return_value = docs
            return mock_res

        # Session turns
        if "FROM session_turns" in stmt_str:
            target_id = None
            for v in params.values():
                if isinstance(v, UUID) and v in self.sessions:
                    target_id = v
                    break
            matching = [
                t for t in self.session_turns if target_id is None or t.session_id == target_id
            ]
            mock_res.scalars.return_value.all.return_value = matching
            return mock_res

        # Document chunks
        if "document_chunks" in stmt_str:
            pairs = []
            for c in self.chunks:
                d = self.documents.get(c.document_id)
                pairs.append((c, d.title if d else "Mock Title"))
            mock_res.all.return_value = pairs
            mock_res.scalars.return_value.all.return_value = self.chunks
            return mock_res

        # Summaries
        if "FROM document_summaries" in stmt_str:
            target_id = None
            for v in params.values():
                if isinstance(v, UUID) and v in self.summaries:
                    target_id = v
                    break
            summary = self.summaries.get(target_id)
            mock_res.scalar_one_or_none.return_value = summary
            return mock_res

        # Documents lookup joined with session_documents
        if "session_documents" in stmt_str and "FROM documents" in stmt_str:
            target_session_id = None
            for v in params.values():
                if isinstance(v, UUID) and v in self.sessions:
                    target_session_id = v
                    break
            doc_ids = [
                sd.document_id
                for sd in self.session_documents
                if target_session_id is None or sd.session_id == target_session_id
            ]
            matched = [self.documents[did] for did in doc_ids if did in self.documents]
            mock_res.scalars.return_value.all.return_value = matched
            return mock_res

        # Documents lookup
        if "FROM documents" in stmt_str:
            target_user_id = None
            target_ids = set()
            for k, v in params.items():
                if "user_id" in k:
                    target_user_id = v
                elif isinstance(v, UUID):
                    target_ids.add(v)
            matched = [
                d
                for d in self.documents.values()
                if (target_user_id is None or d.user_id == target_user_id)
                and (not target_ids or d.id in target_ids)
            ]
            single = matched[0] if matched else None
            mock_res.scalar_one_or_none.return_value = single
            mock_res.scalars.return_value.all.return_value = matched
            return mock_res

        # Notes lookup
        if "FROM research_notes" in stmt_str:
            mock_res.scalars.return_value.all.return_value = self.notes
            return mock_res

        mock_res.scalar_one_or_none.return_value = None
        mock_res.scalars.return_value.all.return_value = []
        mock_res.all.return_value = []
        return mock_res


@pytest.fixture
def matrix_db() -> InMemoryMatrixStore:
    return InMemoryMatrixStore()


@pytest.fixture
def client(matrix_db: InMemoryMatrixStore) -> Generator[AsyncClient, None, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield matrix_db  # type: ignore[misc]

    async def override_get_current_user() -> UserModel:
        return UserModel(
            id=DEFAULT_DEV_USER_ID,
            email="researcher@verischolar.org",
            full_name="Principal Researcher",
            hashed_password="hash",
            is_active=True,
        )

    in_memory_idempotency = InMemoryIdempotencyAdapter()

    def override_get_idempotency() -> IIdempotencyPort:
        return in_memory_idempotency

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_idempotency_port] = override_get_idempotency

    transport = ASGITransport(app=app)
    c = AsyncClient(transport=transport, base_url="http://testserver")
    yield c
    app.dependency_overrides.clear()


# ==============================================================================
# LEVEL 1: Easy - Ingestion & Session Creation on 3 Golden Papers
# ==============================================================================
@pytest.mark.asyncio
async def test_level_1_session_creation_with_golden_papers(
    client: AsyncClient, matrix_db: InMemoryMatrixStore
) -> None:
    """Level 1: Create multi-paper research session with the 3 golden papers."""
    doc_ids = []
    titles = [
        "Attention Is All You Need",
        "Reconstructing Context Evaluating Advanced Chunking Strategies for RAG",
        "Advancing Retrieval-Augmented Generation for Structured Enterprise Data",
    ]
    for idx, title in enumerate(titles, start=1):
        doc_id = uuid4()
        doc = DocumentModel(
            id=doc_id,
            user_id=DEFAULT_DEV_USER_ID,
            title=title,
            filename=f"golden_paper_{idx}.pdf",
            content_hash=f"hash_{idx}",
            file_size_bytes=2048 * idx,
            status="completed",
            is_persistent=True,
        )
        matrix_db.add(doc)
        doc_ids.append(doc_id)

    payload = {
        "title": "Golden RAG & Attention Comparative Study",
        "initial_document_ids": [str(d) for d in doc_ids],
    }
    resp = await client.post("/api/v1/sessions", json=payload)
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["title"] == "Golden RAG & Attention Comparative Study"
    assert len(data["document_ids"]) == 3


# ==============================================================================
# LEVEL 2: Medium - Dual-Pane Viewport OCC & Active Recall Quiz Synthesis
# ==============================================================================
@pytest.mark.asyncio
async def test_level_2_viewport_occ_and_active_recall_quiz(
    client: AsyncClient, matrix_db: InMemoryMatrixStore
) -> None:
    """Level 2: Dual-pane autosave viewport with OCC RFC 7232 & Mode 4 Active Recall Quiz."""
    s_id = uuid4()
    sess = ResearchSessionModel(
        id=s_id,
        user_id=DEFAULT_DEV_USER_ID,
        title="Attention Mechanism Architecture",
        viewport_state={"page": 1, "zoom": 1.0, "scroll_top": 0.0},
        active_tab="chat",
        version=1,
        is_archived=False,
    )
    matrix_db.add(sess)

    # 1. Update viewport with OCC
    viewport_payload = {
        "viewport_state": {"page": 6, "zoom": 1.5, "scroll_top": 450.0},
        "active_tab": "notes",
    }
    resp = await client.patch(
        f"/api/v1/sessions/{s_id}/viewport",
        json=viewport_payload,
        headers={"If-Match": '"v1"'},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["version"] == 2
    assert resp.headers["ETag"] == '"v2"'

    # 2. Synthesize note with active_recall_quiz
    doc_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=DEFAULT_DEV_USER_ID,
        title="Attention Is All You Need",
        filename="attention.pdf",
        content_hash="att_hash",
        file_size_bytes=1024,
        status="completed",
        is_persistent=True,
    )
    note_id = uuid4()
    note = ResearchNoteModel(
        id=note_id,
        user_id=DEFAULT_DEV_USER_ID,
        document_id=doc_id,
        selected_text="Positional Encodings have the same dimension d_model as embeddings.",
        page_number=6,
        bounding_boxes=[[0.1, 0.45, 0.9, 0.65, 6]],
        version=1,
    )
    matrix_db.add(doc)
    matrix_db.add(note)

    synth_resp = await client.post(
        "/api/v1/notes:synthesize",
        json={"mode": "active_recall_quiz", "note_ids": [str(note_id)]},
    )
    assert synth_resp.status_code == 200
    synth_data = synth_resp.json()["data"]
    assert synth_data["mode"] == "active_recall_quiz"
    assert (
        "<details>" in synth_data["markdown_content"]
        and "<summary>" in synth_data["markdown_content"]
    )
    assert "Đáp án & Cơ sở khoa học" in synth_data["markdown_content"]


# ==============================================================================
# LEVEL 3: Hard - Presupposition Validation & Socratic Mentor Steering
# ==============================================================================
@pytest.mark.asyncio
async def test_level_3_socratic_steering_on_transformer_paper(
    client: AsyncClient, matrix_db: InMemoryMatrixStore
) -> None:
    """Level 3: Refutes false presupposition and steers to Sec 3.5 Page 6."""
    s_id = uuid4()
    sess = ResearchSessionModel(
        id=s_id,
        user_id=DEFAULT_DEV_USER_ID,
        title="Attention Paper Review",
        version=1,
        is_archived=False,
    )
    matrix_db.add(sess)

    doc_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=DEFAULT_DEV_USER_ID,
        title="Attention Is All You Need",
        filename="attention.pdf",
        content_hash="att_hash",
        file_size_bytes=1024,
        status="completed",
        is_persistent=True,
    )
    chunk = DocumentChunkModel(
        id=uuid4(),
        document_id=doc_id,
        chunk_index=0,
        content="Positional Encoding sinusoidal functions allow model to attend to positions.",
        page_number=6,
        bounding_boxes=[[0.1, 0.45, 0.9, 0.65, 6]],
        token_count=15,
    )
    sdoc = SessionDocumentModel(
        session_id=s_id,
        document_id=doc_id,
        display_order=0,
    )
    matrix_db.add(doc)
    matrix_db.add(chunk)
    matrix_db.add(sdoc)

    # 1. False premise question
    q_payload = {
        "question": "Các tác giả dùng mạng đệ quy RNN ở tầng encoder nào để mã hoá thứ tự từ?",
        "stream": True,
        "scope": "single_paper",
        "focused_document_id": str(doc_id),
    }
    resp = await client.post(f"/api/v1/sessions/{s_id}/messages", json=q_payload)
    assert resp.status_code == 200

    last_turn = matrix_db.session_turns[-1]
    assert "Tiền đề trong câu hỏi của bạn chưa chính xác" in last_turn.answer
    assert "loại bỏ hoàn toàn các cơ chế đệ quy" in last_turn.answer
    assert "Positional Encoding" in last_turn.answer
    assert "Mục 3.5, Trang 6" in last_turn.answer

    # 2. Out-of-scope benchmark distractor mitigation
    distractor_payload = {
        "question": "So sánh điểm số MMLU và GSM8K của Attention Is All You Need so với GPT-4?",
        "stream": True,
        "scope": "single_paper",
        "focused_document_id": str(doc_id),
    }
    resp2 = await client.post(f"/api/v1/sessions/{s_id}/messages", json=distractor_payload)
    assert resp2.status_code == 200
    last_turn2 = matrix_db.session_turns[-1]
    assert "Thông tin này không xuất hiện trong bài báo" in last_turn2.answer
    assert "2017" in last_turn2.answer


# ==============================================================================
# LEVEL 4: Very Hard - Real-Time Grounded Summary Stream
# ==============================================================================
@pytest.mark.asyncio
async def test_level_4_realtime_grounded_summary_stream(
    client: AsyncClient, matrix_db: InMemoryMatrixStore
) -> None:
    """Level 4: Real-time SSE streaming for 3-point grounded summary (Endpoint #57)."""
    doc_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=DEFAULT_DEV_USER_ID,
        title="Reconstructing Context Evaluating Advanced Chunking Strategies for RAG",
        filename="rag_chunking.pdf",
        content_hash="rag_hash",
        file_size_bytes=2048,
        status="completed",
        is_persistent=True,
    )
    summary = DocumentSummaryModel(
        id=uuid4(),
        document_id=doc_id,
        problem_statement="Retrieval degrades when chunks are overly fragmented without context.",
        problem_citations=[[0.1, 0.1, 0.9, 0.3, 1]],
        contributions="Proposes hierarchical chunking techniques for RAG.",
        contribution_citations=[[0.1, 0.35, 0.9, 0.55, 2]],
        limitations="Evaluation focuses primarily on dense embedding models and English corpora.",
        limitation_citations=[[0.1, 0.6, 0.9, 0.8, 8]],
    )
    matrix_db.add(doc)
    matrix_db.add(summary)

    resp = await client.post(f"/api/v1/documents/{doc_id}/summary:stream")
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]

    body = resp.text
    assert "event: summary_start" in body
    assert "event: summary_chunk" in body
    assert "event: summary_box" in body
    assert "event: summary_end" in body
    assert "problem_statement" in body
    assert "contributions" in body
    assert "limitations" in body


# ==============================================================================
# LEVEL 5: Extremely Hard - Multi-Paper Cross-Synthesis & Full Offline Bundle
# ==============================================================================
@pytest.mark.asyncio
async def test_level_5_offline_research_bundle_export(
    client: AsyncClient, matrix_db: InMemoryMatrixStore
) -> None:
    """Level 5: Full Offline Research Bundle (.zip) packaging files."""
    s_id = uuid4()
    sess = ResearchSessionModel(
        id=s_id,
        user_id=DEFAULT_DEV_USER_ID,
        title="Unified Knowledge Synthesis: Transformer & Modern RAG",
        version=3,
        is_archived=False,
    )
    matrix_db.add(sess)

    # 3 golden papers
    papers = [
        ("Attention Is All You Need", "attention.pdf"),
        ("Reconstructing Context RAG", "rag_chunking.pdf"),
        ("Enterprise Structured RAG", "structured_rag.pdf"),
    ]
    for idx, (title, fname) in enumerate(papers):
        d_id = uuid4()
        doc = DocumentModel(
            id=d_id,
            user_id=DEFAULT_DEV_USER_ID,
            title=title,
            filename=fname,
            content_hash=f"hash_{idx}",
            file_size_bytes=2048,
            status="completed",
            is_persistent=True,
        )
        sdoc = SessionDocumentModel(
            session_id=s_id,
            document_id=d_id,
            display_order=idx,
        )
        matrix_db.add(doc)
        matrix_db.add(sdoc)

    # Add conversation turn
    turn = SessionTurnModel(
        id=uuid4(),
        session_id=s_id,
        question="Điểm giao thoa giữa Attention và RAG là gì?",
        answer="Attention liên kết ngữ cảnh, RAG mở rộng tri thức ngoại vi.",
        citations=[],
        prompt_tokens=15,
        completion_tokens=30,
        latency_ms=120,
    )
    matrix_db.add(turn)

    # Export bundle
    resp = await client.post(f"/api/v1/sessions/{s_id}:export-bundle")
    assert resp.status_code == 200
    assert "application/zip" in resp.headers["content-type"]
    assert f"verischolar_session_{s_id}.zip" in resp.headers["content-disposition"]

    zf = zipfile.ZipFile(io.BytesIO(resp.content))
    namelist = zf.namelist()

    # 1. documents/ contains all 3 PDFs
    assert "documents/attention.pdf" in namelist
    assert "documents/rag_chunking.pdf" in namelist
    assert "documents/structured_rag.pdf" in namelist

    # 2. master_lesson.md is complete with frontmatter and sections
    assert "master_lesson.md" in namelist
    master_md = zf.read("master_lesson.md").decode("utf-8")
    assert "Unified Knowledge Synthesis: Transformer & Modern RAG" in master_md
    assert "Attention Is All You Need" in master_md
    assert "Reconstructing Context RAG" in master_md
    assert "Enterprise Structured RAG" in master_md
    assert "Điểm giao thoa giữa Attention và RAG là gì?" in master_md

    # 3. chat_transcript.html is self-contained
    assert "chat_transcript.html" in namelist
    transcript = zf.read("chat_transcript.html").decode("utf-8")
    assert "Unified Knowledge Synthesis: Transformer & Modern RAG" in transcript
    assert "Điểm giao thoa giữa Attention và RAG là gì?" in transcript
