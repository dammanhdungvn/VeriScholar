"""Unit tests for CRAG (Corrective RAG) Evaluation & Multiline Window Expansion."""

import json
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from api.db.models.chunk import DocumentChunkModel
from api.db.models.document import DocumentModel
from api.db.models.session import ResearchSessionModel, SessionDocumentModel
from api.db.models.user import UserModel
from api.schemas.session import SessionChatMessageRequest
from api.services.session_chat_service import SessionChatService


@pytest.mark.asyncio
async def test_crag_expands_adjacent_chunks_when_ambiguous(db_session):
    """When retrieval confidence is ambiguous (0.20 <= tau < 0.35), adjacent chunks are expanded."""
    service = SessionChatService(db=db_session)
    doc_id = uuid4()
    candidate_chunks = [
        {
            "chunk_id": uuid4(),
            "document_id": doc_id,
            "chunk_index": 19,
            "page_number": 3,
            "cosine_sim": 0.28,
            "content": "AR = (1/n) * sum(",
        }
    ]
    with patch.object(service, "_fetch_adjacent_chunks", new_callable=AsyncMock) as mock_adj:
        mock_adj.return_value = [
            {
                "chunk_id": uuid4(),
                "document_id": doc_id,
                "chunk_index": 20,
                "page_number": 3,
                "content": "cos(q, q_i)) where q is query",
            }
        ]
        verdict, final_chunks, abstain = await service.evaluate_crag_and_expand(candidate_chunks)
        assert verdict == "AMBIGUOUS_EXPANDED"
        assert len(final_chunks) == 2
        assert not abstain
        mock_adj.assert_called_once()


@pytest.mark.asyncio
async def test_crag_confident_retrieval_keeps_candidates_without_expansion(db_session):
    """When retrieval confidence is high (tau >= 0.35), keep candidates without expansion."""
    service = SessionChatService(db=db_session)
    doc_id = uuid4()
    candidate_chunks = [
        {
            "chunk_id": uuid4(),
            "document_id": doc_id,
            "chunk_index": 5,
            "page_number": 2,
            "cosine_sim": 0.52,
            "content": "Self-attention layer computes attention weights using scaled dot-product.",
        }
    ]
    with patch.object(service, "_fetch_adjacent_chunks", new_callable=AsyncMock) as mock_adj:
        verdict, final_chunks, abstain = await service.evaluate_crag_and_expand(candidate_chunks)
        assert verdict == "CORRECT"
        assert len(final_chunks) == 1
        assert not abstain
        mock_adj.assert_not_called()


@pytest.mark.asyncio
async def test_crag_triggers_active_abstention_when_low_confidence(db_session):
    """When retrieval confidence is low (tau < 0.20), trigger active abstention to avoid hallucination."""
    service = SessionChatService(db=db_session)
    candidate_chunks = [
        {
            "chunk_id": uuid4(),
            "document_id": uuid4(),
            "chunk_index": 12,
            "page_number": 4,
            "cosine_sim": 0.14,
            "content": "Vague unrelated passage.",
        }
    ]
    verdict, final_chunks, abstain = await service.evaluate_crag_and_expand(candidate_chunks)
    assert verdict == "ACTIVE_ABSTENTION"
    assert abstain is True


@pytest.mark.asyncio
async def test_crag_triggers_active_abstention_when_empty_candidates(db_session):
    """When no candidates retrieved, CRAG evaluates tau = 0.0 and abstains."""
    service = SessionChatService(db=db_session)
    verdict, final_chunks, abstain = await service.evaluate_crag_and_expand([])
    assert verdict == "ACTIVE_ABSTENTION"
    assert abstain is True
    assert final_chunks == []


@pytest.mark.asyncio
async def test_crag_deduplicates_chunks_by_chunk_id(db_session):
    """Candidate chunks and adjacent chunks are deduplicated by chunk_id."""
    service = SessionChatService(db=db_session)
    doc_id = uuid4()
    shared_id = uuid4()
    other_id = uuid4()
    candidate_chunks = [
        {
            "chunk_id": shared_id,
            "document_id": doc_id,
            "chunk_index": 10,
            "page_number": 2,
            "cosine_sim": 0.26,
            "content": "Shared chunk content",
        }
    ]
    with patch.object(service, "_fetch_adjacent_chunks", new_callable=AsyncMock) as mock_adj:
        mock_adj.return_value = [
            {
                "chunk_id": shared_id,
                "document_id": doc_id,
                "chunk_index": 10,
                "page_number": 2,
                "content": "Shared chunk duplicate",
            },
            {
                "chunk_id": other_id,
                "document_id": doc_id,
                "chunk_index": 11,
                "page_number": 2,
                "content": "Adjacent next chunk",
            },
        ]
        verdict, final_chunks, abstain = await service.evaluate_crag_and_expand(candidate_chunks)
        assert verdict == "AMBIGUOUS_EXPANDED"
        assert len(final_chunks) == 2
        assert not abstain
        chunk_ids = [str(c["chunk_id"]) for c in final_chunks]
        assert str(shared_id) in chunk_ids
        assert str(other_id) in chunk_ids


@pytest.mark.asyncio
async def test_crag_context_budget_capping_at_max_evidence_tokens(db_session):
    """Context expansion must not exceed MAX_EVIDENCE_TOKENS = 3500."""
    service = SessionChatService(db=db_session)
    doc_id = uuid4()
    candidate_chunks = [
        {
            "chunk_id": uuid4(),
            "document_id": doc_id,
            "chunk_index": 15,
            "page_number": 3,
            "cosine_sim": 0.27,
            "token_count": 1000,
            "content": "Initial ambiguous chunk with 1000 tokens",
        }
    ]
    with patch.object(service, "_fetch_adjacent_chunks", new_callable=AsyncMock) as mock_adj:
        mock_adj.return_value = [
            {
                "chunk_id": uuid4(),
                "document_id": doc_id,
                "chunk_index": 14,
                "page_number": 3,
                "token_count": 1000,
                "content": "Preceding chunk with 1000 tokens",
            },
            {
                "chunk_id": uuid4(),
                "document_id": doc_id,
                "chunk_index": 16,
                "page_number": 3,
                "token_count": 1000,
                "content": "Following chunk 1 with 1000 tokens",
            },
            {
                "chunk_id": uuid4(),
                "document_id": doc_id,
                "chunk_index": 17,
                "page_number": 3,
                "token_count": 1000,
                "content": "Following chunk 2 with 1000 tokens exceeding budget",
            },
        ]
        verdict, final_chunks, abstain = await service.evaluate_crag_and_expand(candidate_chunks)
        assert verdict == "AMBIGUOUS_EXPANDED"
        # 1000 + 1000 + 1000 = 3000 <= 3500. 4th chunk (4000) exceeds 3500 and is excluded.
        assert len(final_chunks) == 3
        total_tokens = sum(c.get("token_count", 0) for c in final_chunks)
        assert total_tokens <= 3500
        assert not abstain


@pytest.mark.asyncio
async def test_fetch_adjacent_chunks_queries_database(db_session):
    """_fetch_adjacent_chunks fetches chunks [i-1, i+1] from database for given document."""
    service = SessionChatService(db=db_session)

    # 1. Create user and document
    user = UserModel(
        email=f"crag_test_{uuid4().hex[:8]}@example.com",
        full_name="Dr. Scholar",
        hashed_password="mock_hash",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    doc = DocumentModel(
        user_id=user.id,
        filename="ragas_eval.pdf",
        title="RAGAS: Automated Evaluation of Retrieval Augmented Generation",
        content_hash=uuid4().hex,
        status="completed",
        access_status="completed",
        page_count=5,
        chunk_count=3,
        file_size_bytes=1000,
    )
    db_session.add(doc)
    await db_session.flush()

    # 2. Insert chunks 18, 19, 20
    chunk18 = DocumentChunkModel(
        user_id=user.id,
        document_id=doc.id,
        chunk_index=18,
        page_number=3,
        content="Context preceding formula.",
        bounding_boxes=[[0.1, 0.1, 0.9, 0.2, 3]],
        token_count=10,
    )
    chunk19 = DocumentChunkModel(
        user_id=user.id,
        document_id=doc.id,
        chunk_index=19,
        page_number=3,
        content="AR = (1/n) * sum(",
        bounding_boxes=[[0.1, 0.2, 0.9, 0.4, 3]],
        token_count=10,
    )
    chunk20 = DocumentChunkModel(
        user_id=user.id,
        document_id=doc.id,
        chunk_index=20,
        page_number=3,
        content="cos(q, q_i)) where q is query.",
        bounding_boxes=[[0.1, 0.4, 0.9, 0.6, 3]],
        token_count=10,
    )
    db_session.add_all([chunk18, chunk19, chunk20])
    await db_session.commit()

    # 3. Call _fetch_adjacent_chunks for candidate chunk 19
    candidate = [
        {
            "chunk_id": chunk19.id,
            "document_id": doc.id,
            "chunk_index": 19,
            "page_number": 3,
            "cosine_sim": 0.25,
            "content": chunk19.content,
        }
    ]
    adj_chunks = await service._fetch_adjacent_chunks(candidate)
    indices = {c["chunk_index"] for c in adj_chunks}
    assert 18 in indices
    assert 20 in indices
    assert 19 not in indices
    assert len(adj_chunks) == 2


@pytest.mark.asyncio
async def test_stream_chat_emits_crag_abstention_on_low_confidence(db_session):
    """When candidate chunks have low confidence (tau < 0.20), stream_chat triggers CRAG abstention."""
    service = SessionChatService(db=db_session)
    user = UserModel(
        email=f"crag_stream_abs_{uuid4().hex[:8]}@example.com",
        full_name="Dr. Scholar",
        hashed_password="mock",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    session = ResearchSessionModel(
        user_id=user.id,
        title="CRAG Stream Abstention Session",
    )
    db_session.add(session)
    await db_session.flush()

    doc = DocumentModel(
        user_id=user.id,
        filename="ragas_eval.pdf",
        title="RAGAS Paper",
        content_hash=uuid4().hex,
        status="completed",
        access_status="completed",
        page_count=5,
        chunk_count=1,
        file_size_bytes=1000,
    )
    db_session.add(doc)
    await db_session.flush()

    link = SessionDocumentModel(session_id=session.id, document_id=doc.id)
    db_session.add(link)
    await db_session.commit()

    request = SessionChatMessageRequest(
        question="What is the answer relevance formula in Ragas?",
        scope="single_paper",
        focused_document_id=doc.id,
    )

    async def mock_is_disconnected():
        return False

    with patch.object(service, "retrieve_hybrid_chunks", new_callable=AsyncMock) as mock_ret:
        # Low confidence tau = 0.10 < 0.20
        mock_ret.return_value = [
            {
                "chunk_id": uuid4(),
                "document_id": doc.id,
                "chunk_index": 0,
                "page_number": 1,
                "cosine_sim": 0.10,
                "rrf_score": 0.01,
                "content": "Unrelated intro",
            }
        ]
        events = []
        async for chunk in service.stream_chat(
            session_id=session.id,
            user_id=user.id,
            request=request,
            is_disconnected=mock_is_disconnected,
        ):
            events.append(chunk)

        full_stream = "".join(events)
        assert "CRAG Active Abstention" in full_stream or "tau < 0.20" in full_stream
        tokens = [
            json.loads(line[6:])["token"]
            for line in full_stream.splitlines()
            if line.startswith('data: {"token":')
        ]
        answer_text = "".join(tokens)
        assert "Thông tin này không xuất hiện trong bài báo" in answer_text


@pytest.mark.asyncio
async def test_stream_chat_expands_windows_on_ambiguous_confidence(db_session):
    """When candidate chunks have ambiguous confidence, stream_chat expands adjacent chunks."""
    service = SessionChatService(db=db_session)
    user = UserModel(
        email=f"crag_stream_exp_{uuid4().hex[:8]}@example.com",
        full_name="Dr. Scholar",
        hashed_password="mock",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    session = ResearchSessionModel(
        user_id=user.id,
        title="CRAG Stream Expansion Session",
    )
    db_session.add(session)
    await db_session.flush()

    doc = DocumentModel(
        user_id=user.id,
        filename="ragas_eval.pdf",
        title="RAGAS Paper",
        content_hash=uuid4().hex,
        status="completed",
        access_status="completed",
        page_count=5,
        chunk_count=2,
        file_size_bytes=1000,
    )
    db_session.add(doc)
    await db_session.flush()

    link = SessionDocumentModel(session_id=session.id, document_id=doc.id)
    db_session.add(link)
    await db_session.commit()

    request = SessionChatMessageRequest(
        question="What is the answer relevance formula?",
        scope="single_paper",
        focused_document_id=doc.id,
    )

    async def mock_is_disconnected():
        return False

    cand_id = uuid4()
    adj_id = uuid4()
    with (
        patch.object(service, "retrieve_hybrid_chunks", new_callable=AsyncMock) as mock_ret,
        patch.object(service, "_fetch_adjacent_chunks", new_callable=AsyncMock) as mock_adj,
    ):
        mock_ret.return_value = [
            {
                "chunk_id": cand_id,
                "document_id": doc.id,
                "chunk_index": 19,
                "page_number": 3,
                "cosine_sim": 0.28,
                "rrf_score": 0.05,
                "content": "AR = (1/n) * sum(",
            }
        ]
        mock_adj.return_value = [
            {
                "chunk_id": adj_id,
                "document_id": doc.id,
                "chunk_index": 20,
                "page_number": 3,
                "cosine_sim": 0.0,
                "rrf_score": 0.0,
                "content": "cos(q, q_i))",
            }
        ]
        events = []
        async for chunk in service.stream_chat(
            session_id=session.id,
            user_id=user.id,
            request=request,
            is_disconnected=mock_is_disconnected,
        ):
            events.append(chunk)

        full_stream = "".join(events)
        assert "event: citations" in full_stream
        cit_lines = [
            json.loads(line[6:])["citations"]
            for line in full_stream.splitlines()
            if line.startswith('data: {"citations":')
        ]
        assert len(cit_lines) == 1
        # Citations expanded to include both original candidate and adjacent chunk
        assert len(cit_lines[0]) == 2
