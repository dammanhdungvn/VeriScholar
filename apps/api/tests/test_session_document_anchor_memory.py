from uuid import uuid4

import pytest
from api.db.models.document import DocumentModel
from api.services.session_chat_service import SessionChatService


@pytest.mark.asyncio
async def test_build_document_anchor_context_with_abstract_and_sections(db_session):
    service = SessionChatService(db_session)

    doc_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=uuid4(),
        title="Graph Neural Networks for Financial Fraud Detection: A Review",
        filename="gnn_review.pdf",
        authors=["Dawei Cheng", "Yao Zou", "Changjun Jiang"],
        publication_year=2024,
        doi="10.1007/s11704-024-0000",
        status="completed",
        content_hash="hash_gnn_001",
        file_size_bytes=2048,
        parsed_metadata={
            "abstract": "The landscape of financial transactions has grown increasingly complex due to global integration. This review explores the role of GNNs in financial fraud detection.",
            "structure": {
                "sections": [
                    {"title": "1 Introduction", "page_number": 1},
                    {"title": "2 Preliminaries", "page_number": 3},
                    {"title": "8 Conclusion", "page_number": 12},
                ]
            },
        },
    )

    anchor_context = await service._build_document_anchor_context([doc])

    assert "TÀI LIỆU NGHIÊN CỨU HIỆN TẠI (DOCUMENT ANCHOR MEMORY)" in anchor_context
    assert "Graph Neural Networks for Financial Fraud Detection: A Review" in anchor_context
    assert "Dawei Cheng" in anchor_context
    assert "BẢN TÓM TẮT CHÍNH THỨC (OFFICIAL ABSTRACT)" in anchor_context
    assert (
        "The landscape of financial transactions has grown increasingly complex" in anchor_context
    )
    assert "1 Introduction (Trang 1)" in anchor_context or "1 Introduction" in anchor_context
    assert "8 Conclusion" in anchor_context


@pytest.mark.asyncio
async def test_build_document_anchor_context_empty_documents(db_session):
    service = SessionChatService(db_session)
    anchor_context = await service._build_document_anchor_context([])
    assert anchor_context == ""


@pytest.mark.asyncio
async def test_build_document_anchor_context_falls_back_to_chunk_when_metadata_abstract_missing(
    db_session,
):
    from api.db.models.chunk import DocumentChunkModel
    from api.db.models.user import UserModel

    user = UserModel(
        id=uuid4(),
        email=f"scholar.{uuid4().hex[:8]}@vnu.edu.vn",
        hashed_password="fake_hashed_pw",
        full_name="TS. Anchor Fallback Tester",
        role="scholar",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    doc_id = uuid4()
    doc = DocumentModel(
        id=doc_id,
        user_id=user.id,
        title="Paper Without Abstract in Metadata",
        filename="no_meta_abstract.pdf",
        authors=["Alice", "Bob"],
        publication_year=2025,
        status="completed",
        content_hash="hash_no_meta_001",
        file_size_bytes=1024,
        parsed_metadata={},  # No abstract in parsed_metadata
    )
    db_session.add(doc)
    await db_session.flush()

    # Create chunk 1 with Abstract keyword
    chunk = DocumentChunkModel(
        id=uuid4(),
        document_id=doc_id,
        user_id=user.id,
        chunk_index=1,
        page_number=1,
        content="Abstract: This paper explores novel graph representations for molecular biology.",
        bounding_boxes=[[0.1, 0.2, 0.9, 0.4, 1]],
        token_count=60,
    )
    db_session.add(chunk)
    await db_session.commit()

    service = SessionChatService(db_session)
    anchor_context = await service._build_document_anchor_context([doc])

    assert "Paper Without Abstract in Metadata" in anchor_context
    assert "BẢN TÓM TẮT CHÍNH THỨC (OFFICIAL ABSTRACT)" in anchor_context
    assert "Abstract: This paper explores novel graph representations" in anchor_context
