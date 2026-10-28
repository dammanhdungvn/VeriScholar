from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from api.db.models.chunk import DocumentChunkModel
from api.db.models.document import DocumentModel
from api.db.models.session import ResearchSessionModel, SessionDocumentModel
from api.db.models.user import UserModel
from api.services.session_chat_service import (
    SessionChatService,
    _detect_formula_query,
    _extract_formula_symbols,
)


def test_detect_target_section_handles_typo_and_numbered_sections():
    assert SessionChatService._detect_target_section("1. Instruction") == "introduction"
    assert (
        SessionChatService._detect_target_section("Dịch mục 1. Instruction sang tiếng việt")
        == "introduction"
    )
    assert SessionChatService._detect_target_section("Tóm tắt Mục 1") == "introduction"
    assert SessionChatService._detect_target_section("Phần 1 bài báo nói gì") == "introduction"
    assert SessionChatService._detect_target_section("Mục 2 nói về gì") == "section_2"


def test_detect_formula_query_and_symbol_extraction():
    res = _detect_formula_query("Công thức A(H) trong paper có ý nghĩa gì")
    assert res is not None
    assert "A(H)" in res["symbols"] or any("A" in s for s in res["symbols"])

    res_typo = _detect_formula_query("Lấy công thức Attendsion ra cho tôi")
    assert res_typo is not None
    assert "attention" in [n.lower() for n in res_typo.get("normalized_names", [])]

    res_eq = _detect_formula_query("Giải thích công thức (3) trong bài")
    assert res_eq is not None
    assert "(3)" in res_eq["equation_numbers"] or "3" in res_eq["equation_numbers"]


def test_extract_formula_symbols():
    symbols = _extract_formula_symbols("Tìm công thức Attention(Q, K, V) và softmax(x)")
    assert any("attention" in s.lower() for s in symbols)
    assert any("softmax" in s.lower() for s in symbols)

    # Common words in Vietnamese queries like "ma" from "ma trận" should NOT be treated as symbols
    vietnamese_query_symbols = _extract_formula_symbols("Công thức tính toán ma trận Attention")
    assert "ma" not in [s.lower() for s in vietnamese_query_symbols]
    assert "trận" not in [s.lower() for s in vietnamese_query_symbols]
    assert any("attention" in s.lower() for s in vietnamese_query_symbols)

    # Subscripted variables like W_Q, h_n, e_{ij} are correctly identified
    subscript_symbols = _extract_formula_symbols("Giải thích các biến W_Q, W_K, h_n và e_{ij}")
    assert "W_Q" in subscript_symbols
    assert "W_K" in subscript_symbols
    assert "h_n" in subscript_symbols
    assert "e_{ij}" in subscript_symbols


@pytest.mark.asyncio
async def test_formula_aware_retrieval_prioritizes_exact_equation_chunk(db_session, monkeypatch):
    monkeypatch.setattr(
        "api.services.embedding_service.EmbeddingService.get_embedding",
        AsyncMock(return_value=[0.01] * 1536),
    )

    user = UserModel(
        id=uuid4(),
        email=f"scholar.{uuid4().hex[:8]}@vnu.edu.vn",
        hashed_password="fake_hashed_pw",
        full_name="TS. Formula Tester",
        role="scholar",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    doc_id = uuid4()
    session_id = uuid4()

    doc = DocumentModel(
        id=doc_id,
        user_id=user.id,
        title="Stack Attention Paper",
        filename="stack_attention.pdf",
        status="completed",
        content_hash="hash_stack_001",
        file_size_bytes=4096,
        parsed_metadata={},
    )
    sess = ResearchSessionModel(
        id=session_id,
        user_id=user.id,
        title="Session Formula Test",
    )
    sess_doc = SessionDocumentModel(
        session_id=session_id,
        document_id=doc_id,
        display_order=0,
    )
    db_session.add_all([doc, sess, sess_doc])
    await db_session.flush()

    # Chunk 10: General text about query, key, value on page 2
    general_chunk = DocumentChunkModel(
        id=uuid4(),
        document_id=doc_id,
        user_id=user.id,
        chunk_index=10,
        page_number=2,
        content="Queries, Keys, and Values. In the version of the attention mechanism introduced by Vaswani...",
        bounding_boxes=[[0.2, 0.4, 0.8, 0.5, 2]],
        token_count=100,
    )
    # Chunk 12: Equation (3) defining A(H) on page 2
    equation_chunk = DocumentChunkModel(
        id=uuid4(),
        document_id=doc_id,
        user_id=user.id,
        chunk_index=12,
        page_number=2,
        content="A(H)_{:, i} = sum_{n=1}^i alpha_i(n) h_n (3) where A(H) denotes the attention head.",
        bounding_boxes=[[0.1, 0.6, 0.5, 0.7, 2]],
        token_count=40,
    )
    db_session.add_all([general_chunk, equation_chunk])
    await db_session.commit()

    service = SessionChatService(db_session)
    selected_chunks, citations, abstain = await service.retrieve_and_prepare_context(
        session_id=session_id,
        user_id=user.id,
        question="Công thức A(H) trong paper có ý nghĩa gì",
        target_doc_ids=[doc_id],
        limit=5,
    )

    assert not abstain
    assert len(citations) >= 1
    # Priority rank 1 must be the equation chunk defining A(H)
    assert citations[0]["chunk_index"] == 12
    assert "A(H)" in selected_chunks[0]["content"]


@pytest.mark.asyncio
async def test_section_aware_retrieval_handles_instruction_typo(db_session, monkeypatch):
    monkeypatch.setattr(
        "api.services.embedding_service.EmbeddingService.get_embedding",
        AsyncMock(return_value=[0.01] * 1536),
    )

    user = UserModel(
        id=uuid4(),
        email=f"scholar.{uuid4().hex[:8]}@vnu.edu.vn",
        hashed_password="fake_hashed_pw",
        full_name="TS. Typo Tester",
        role="scholar",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    doc_id = uuid4()
    session_id = uuid4()

    doc = DocumentModel(
        id=doc_id,
        user_id=user.id,
        title="Stack Attention Paper",
        filename="stack_attention.pdf",
        status="completed",
        content_hash="hash_stack_002",
        file_size_bytes=4096,
        parsed_metadata={},
    )
    sess = ResearchSessionModel(
        id=session_id,
        user_id=user.id,
        title="Session Typo Test",
    )
    sess_doc = SessionDocumentModel(
        session_id=session_id,
        document_id=doc_id,
        display_order=0,
    )
    db_session.add_all([doc, sess, sess_doc])
    await db_session.flush()

    # Chunk 1: 1. Introduction on page 1
    intro_chunk = DocumentChunkModel(
        id=uuid4(),
        document_id=doc_id,
        user_id=user.id,
        chunk_index=1,
        page_number=1,
        content="1. Introduction Language models (LMs) based on the transformer architecture have shown great empirical success...",
        bounding_boxes=[[0.1, 0.3, 0.9, 0.6, 1]],
        token_count=150,
    )
    # Chunk 5: Later body on page 3
    body_chunk = DocumentChunkModel(
        id=uuid4(),
        document_id=doc_id,
        user_id=user.id,
        chunk_index=5,
        page_number=3,
        content="We evaluate our stack-augmented transformer through comparison with standard transformers...",
        bounding_boxes=[[0.1, 0.1, 0.9, 0.4, 3]],
        token_count=120,
    )
    db_session.add_all([intro_chunk, body_chunk])
    await db_session.commit()

    service = SessionChatService(db_session)
    selected_chunks, citations, abstain = await service.retrieve_and_prepare_context(
        session_id=session_id,
        user_id=user.id,
        question="Dịch mục 1. Instruction sang tiếng việt",
        target_doc_ids=[doc_id],
        limit=5,
    )

    assert not abstain
    assert len(citations) >= 1
    # Priority rank 1 must be the 1. Introduction chunk
    assert citations[0]["chunk_index"] == 1
    assert "1. Introduction" in selected_chunks[0]["content"]


@pytest.mark.asyncio
async def test_evidence_and_citations_capped_at_five(db_session, monkeypatch):
    monkeypatch.setattr(
        "api.services.embedding_service.EmbeddingService.get_embedding",
        AsyncMock(return_value=[0.01] * 1536),
    )

    user = UserModel(
        id=uuid4(),
        email=f"scholar.{uuid4().hex[:8]}@vnu.edu.vn",
        hashed_password="fake_hashed_pw",
        full_name="TS. Cap Tester",
        role="scholar",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    doc_id = uuid4()
    session_id = uuid4()

    doc = DocumentModel(
        id=doc_id,
        user_id=user.id,
        title="Cap Test Paper",
        filename="cap_paper.pdf",
        status="completed",
        content_hash="hash_cap_001",
        file_size_bytes=4096,
        parsed_metadata={},
    )
    sess = ResearchSessionModel(
        id=session_id,
        user_id=user.id,
        title="Session Cap Test",
    )
    sess_doc = SessionDocumentModel(
        session_id=session_id,
        document_id=doc_id,
        display_order=0,
    )
    db_session.add_all([doc, sess, sess_doc])
    await db_session.flush()

    # Create 10 chunks with content matching Attention
    chunks = []
    for i in range(10):
        chunks.append(
            DocumentChunkModel(
                id=uuid4(),
                document_id=doc_id,
                user_id=user.id,
                chunk_index=i,
                page_number=1 + i // 2,
                content=f"Attention mechanisms allow models to focus on relevant tokens {i}...",
                bounding_boxes=[[0.1, 0.08 * i, 0.9, 0.08 * i + 0.06, 1 + i // 2]],
                token_count=50,
            )
        )
    db_session.add_all(chunks)
    await db_session.commit()

    service = SessionChatService(db_session)
    selected_chunks, citations, abstain = await service.retrieve_and_prepare_context(
        session_id=session_id,
        user_id=user.id,
        question="Giải thích cơ chế Attention",
        target_doc_ids=[doc_id],
        limit=5,
    )

    assert not abstain
    assert len(citations) <= 5
    assert len(selected_chunks) <= 5


def test_socratic_prompt_contains_equation_katex_rule():
    prompt = SessionChatService._build_socratic_system_prompt()
    assert "$$" in prompt
    assert "công thức" in prompt.lower()
