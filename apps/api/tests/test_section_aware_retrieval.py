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
