from uuid import uuid4

import pytest
from api.db.models.chunk import DocumentChunkModel
from api.db.models.document import DocumentModel
from api.db.models.session import ResearchSessionModel, SessionDocumentModel
from api.db.models.user import UserModel
from api.services.session_chat_service import SessionChatService


def test_detect_target_section():
    assert (
        SessionChatService._detect_target_section("Dịch nội dung abstract sang tiếng việt.")
        == "abstract"
    )
    assert SessionChatService._detect_target_section("Tóm tắt bài báo này cho tôi") == "abstract"
    assert (
        SessionChatService._detect_target_section("Phần mở đầu nói về vấn đề gì?") == "introduction"
    )
    assert (
        SessionChatService._detect_target_section("Kết luận của nghiên cứu là gì?") == "conclusion"
    )
    assert (
        SessionChatService._detect_target_section("Graph Neural Networks hoạt động thế nào?")
        is None
    )


@pytest.mark.asyncio
async def test_section_aware_retrieval_prioritizes_abstract_chunk(db_session, monkeypatch):
    from unittest.mock import AsyncMock

    monkeypatch.setattr(
        "api.services.embedding_service.EmbeddingService.get_embedding",
        AsyncMock(return_value=[0.01] * 1536),
    )

    user = UserModel(
        id=uuid4(),
        email=f"scholar.{uuid4().hex[:8]}@vnu.edu.vn",
        hashed_password="fake_hashed_pw",
        full_name="TS. Section Tester",
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
        title="GNN Financial Fraud Review",
        filename="gnn_review.pdf",
        status="completed",
        content_hash="hash_section_001",
        file_size_bytes=4096,
        parsed_metadata={
            "abstract": "Abstract The landscape of financial transactions has grown increasingly complex...",
            "structure": {
                "abstract_bounding_boxes": [[0.081, 0.4196, 0.4881, 0.9258, 1]],
            },
        },
    )
    sess = ResearchSessionModel(
        id=session_id,
        user_id=user.id,
        title="Session Section Aware",
    )
    sess_doc = SessionDocumentModel(
        session_id=session_id,
        document_id=doc_id,
        display_order=0,
    )
    db_session.add_all([doc, sess, sess_doc])
    await db_session.flush()

    # Create Chunk 4 (Abstract) on Page 1
    abstract_chunk = DocumentChunkModel(
        id=uuid4(),
        document_id=doc_id,
        user_id=user.id,
        chunk_index=4,
        page_number=1,
        content="Abstract The landscape of financial transactions has grown increasingly complex due to global integration...",
        bounding_boxes=[[0.081, 0.4196, 0.4881, 0.9258, 1]],
        token_count=120,
    )
    # Create Chunk 101 (Conclusion) on Page 12
    conclusion_chunk = DocumentChunkModel(
        id=uuid4(),
        document_id=doc_id,
        user_id=user.id,
        chunk_index=101,
        page_number=12,
        content="8 Conclusion This review provided an in-depth analysis of GNN for financial fraud detection...",
        bounding_boxes=[[0.081, 0.6253, 0.2071, 0.6405, 12]],
        token_count=150,
    )
    db_session.add_all([abstract_chunk, conclusion_chunk])
    await db_session.commit()

    service = SessionChatService(db_session)
    selected_chunks, citations, abstain = await service.retrieve_and_prepare_context(
        session_id=session_id,
        user_id=user.id,
        question="Dịch nội dung abstract sang tiếng việt.",
        target_doc_ids=[doc_id],
        limit=5,
    )

    assert not abstain
    assert len(citations) >= 1
    # First citation must be the Abstract on Page 1
    assert citations[0]["page_number"] == 1
    assert citations[0]["bounding_boxes"] == [[0.081, 0.4196, 0.4881, 0.9258, 1]]


@pytest.mark.asyncio
async def test_section_aware_retrieval_prefers_chunk_with_abstract_over_chunk_0_header(
    db_session, monkeypatch
):
    from unittest.mock import AsyncMock

    monkeypatch.setattr(
        "api.services.embedding_service.EmbeddingService.get_embedding",
        AsyncMock(return_value=[0.01] * 1536),
    )

    user = UserModel(
        id=uuid4(),
        email=f"scholar.{uuid4().hex[:8]}@vnu.edu.vn",
        hashed_password="fake_hashed_pw",
        full_name="TS. Header Tester",
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
        title="Header Paper",
        filename="header_paper.pdf",
        status="completed",
        content_hash="hash_header_001",
        file_size_bytes=2048,
    )
    sess = ResearchSessionModel(
        id=session_id,
        user_id=user.id,
        title="Session Header Aware",
    )
    sess_doc = SessionDocumentModel(
        session_id=session_id,
        document_id=doc_id,
        display_order=0,
    )
    db_session.add_all([doc, sess, sess_doc])
    await db_session.flush()

    # Chunk 0: Header with affiliations only, no "abstract" word
    header_chunk = DocumentChunkModel(
        id=uuid4(),
        document_id=doc_id,
        user_id=user.id,
        chunk_index=0,
        page_number=1,
        content="Department of Computer Science, University. Email: author@univ.edu. Received 2024.",
        bounding_boxes=[[0.1, 0.1, 0.9, 0.2, 1]],
        token_count=80,
    )
    # Chunk 2: Real Abstract with "Abstract" keyword
    real_abstract_chunk = DocumentChunkModel(
        id=uuid4(),
        document_id=doc_id,
        user_id=user.id,
        chunk_index=2,
        page_number=1,
        content="Abstract: In this paper we propose a novel deep learning framework for anomaly detection.",
        bounding_boxes=[[0.1, 0.25, 0.9, 0.45, 1]],
        token_count=100,
    )
    db_session.add_all([header_chunk, real_abstract_chunk])
    await db_session.commit()

    service = SessionChatService(db_session)
    selected_chunks, citations, abstain = await service.retrieve_and_prepare_context(
        session_id=session_id,
        user_id=user.id,
        question="Tóm tắt nội dung abstract của bài báo",
        target_doc_ids=[doc_id],
        limit=5,
    )

    assert not abstain
    assert len(citations) >= 1
    # Must prioritize Chunk 2 which contains the real Abstract
    assert citations[0]["bounding_boxes"] == [[0.1, 0.25, 0.9, 0.45, 1]]


@pytest.mark.asyncio
async def test_section_aware_retrieval_matches_abstract_by_prefix_and_bypasses_affiliation_header(
    db_session, monkeypatch
):
    from unittest.mock import AsyncMock

    monkeypatch.setattr(
        "api.services.embedding_service.EmbeddingService.get_embedding",
        AsyncMock(return_value=[0.01] * 1536),
    )

    user = UserModel(
        id=uuid4(),
        email=f"scholar.{uuid4().hex[:8]}@vnu.edu.vn",
        hashed_password="fake_hashed_pw",
        full_name="TS. Prefix Tester",
        role="scholar",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    doc_id = uuid4()
    session_id = uuid4()

    abstract_text = (
        "Natural languages are believed to be mildly context-sensitive. "
        "Despite underpinning remarkably capable large language models, "
        "transformers are unable to model many context-free language tasks. "
        "In an attempt to address this limitation, we propose augmenting them "
        "with a differentiable stack-based attention mechanism."
    )

    doc = DocumentModel(
        id=doc_id,
        user_id=user.id,
        title="A Transformer with Stack Attention",
        filename="stack_attention.pdf",
        status="completed",
        content_hash="hash_stack_001",
        file_size_bytes=3072,
        parsed_metadata={
            "abstract": abstract_text,
        },
    )
    sess = ResearchSessionModel(
        id=session_id,
        user_id=user.id,
        title="Session Stack Attention",
    )
    sess_doc = SessionDocumentModel(
        session_id=session_id,
        document_id=doc_id,
        display_order=0,
    )
    db_session.add_all([doc, sess, sess_doc])
    await db_session.flush()

    # Chunk 0: Title, Authors, and Emails - strictly no "abstract" keyword
    chunk_0_authors = DocumentChunkModel(
        id=uuid4(),
        document_id=doc_id,
        user_id=user.id,
        chunk_index=0,
        page_number=1,
        content=(
            "A Transformer with Stack Attention\n"
            "Jiaoda Li, Jennifer C. White, Mrinmaya Sachan, Ryan Cotterell\n"
            "ETH Zurich, University of Cambridge\n"
            "{jiaoda.li, mrinmaya.sachan}@inf.ethz.ch jw2088@cam.ac.uk"
        ),
        bounding_boxes=[[0.1, 0.05, 0.9, 0.2, 1]],
        token_count=65,
    )

    # Chunk 1: Body Abstract text - strictly no "abstract" keyword (header was stripped)
    chunk_1_abstract = DocumentChunkModel(
        id=uuid4(),
        document_id=doc_id,
        user_id=user.id,
        chunk_index=1,
        page_number=1,
        content=abstract_text,
        bounding_boxes=[
            [0.1, 0.22, 0.45, 0.35, 1],
            [0.1, 0.36, 0.45, 0.55, 1],
        ],
        token_count=130,
    )

    db_session.add_all([chunk_0_authors, chunk_1_abstract])
    await db_session.commit()

    service = SessionChatService(db_session)
    selected_chunks, citations, abstain = await service.retrieve_and_prepare_context(
        session_id=session_id,
        user_id=user.id,
        question="Hãy tóm tắt ngắn gọn nội dung abstract bài báo này",
        target_doc_ids=[doc_id],
        limit=5,
    )

    assert not abstain
    assert len(citations) >= 1
    # Citations[0] MUST be Chunk 1 (the actual abstract body), NOT Chunk 0 (authors/affiliations)
    assert citations[0]["chunk_index"] == 1
    assert citations[0]["bounding_boxes"] == [
        [0.1, 0.22, 0.45, 0.35, 1],
        [0.1, 0.36, 0.45, 0.55, 1],
    ]


@pytest.mark.asyncio
async def test_full_section_window_expansion_in_retrieval(db_session, monkeypatch):
    from unittest.mock import AsyncMock

    monkeypatch.setattr(
        "api.services.embedding_service.EmbeddingService.get_embedding",
        AsyncMock(return_value=[0.01] * 1536),
    )

    user = UserModel(
        id=uuid4(),
        email=f"scholar.{uuid4().hex[:8]}@vnu.edu.vn",
        hashed_password="fake_hashed_pw",
        full_name="TS. Section Expansion Tester",
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
        title="Attention Is All You Need",
        filename="transformer.pdf",
        status="completed",
        content_hash="hash_transformer_001",
        file_size_bytes=5000,
    )
    sess = ResearchSessionModel(
        id=session_id,
        user_id=user.id,
        title="Session Transformer",
    )
    sess_doc = SessionDocumentModel(
        session_id=session_id,
        document_id=doc_id,
        display_order=0,
    )
    db_session.add_all([doc, sess, sess_doc])
    await db_session.flush()

    # Chunks 6 to 9: Section 1 Introduction
    # Chunk 10: Section 2 Background
    chunks = [
        DocumentChunkModel(
            id=uuid4(),
            document_id=doc_id,
            user_id=user.id,
            chunk_index=6,
            page_number=2,
            content="1 Introduction\nRecurrent neural networks, long short-term memory...",
            token_count=120,
        ),
        DocumentChunkModel(
            id=uuid4(),
            document_id=doc_id,
            user_id=user.id,
            chunk_index=7,
            page_number=2,
            content="Recurrent models typically factor computation along the symbol positions...",
            token_count=130,
        ),
        DocumentChunkModel(
            id=uuid4(),
            document_id=doc_id,
            user_id=user.id,
            chunk_index=8,
            page_number=2,
            content="Attention mechanisms have become an integral part of compelling sequence modeling...",
            token_count=140,
        ),
        DocumentChunkModel(
            id=uuid4(),
            document_id=doc_id,
            user_id=user.id,
            chunk_index=9,
            page_number=2,
            content="In this work we propose the Transformer, a model architecture eschewing recurrence...",
            token_count=150,
        ),
        DocumentChunkModel(
            id=uuid4(),
            document_id=doc_id,
            user_id=user.id,
            chunk_index=10,
            page_number=2,
            content="2 Background\nThe goal of reducing sequential computation also forms the foundation...",
            token_count=160,
        ),
    ]
    db_session.add_all(chunks)
    await db_session.commit()

    service = SessionChatService(db_session)
    selected_chunks, citations, abstain = await service.retrieve_and_prepare_context(
        session_id=session_id,
        user_id=user.id,
        question="Dịch toàn bộ phần 1 Introduction sang tiếng việt",
        target_doc_ids=[doc_id],
        limit=5,
    )

    assert not abstain
    # All 4 contiguous chunks of Section 1 should be retrieved
    retrieved_indices = [c["chunk_index"] for c in citations]
    assert 6 in retrieved_indices
    assert 7 in retrieved_indices
    assert 8 in retrieved_indices
    assert 9 in retrieved_indices
    # Chunk 10 (Section 2) must NOT be included in the expansion
    assert 10 not in retrieved_indices
