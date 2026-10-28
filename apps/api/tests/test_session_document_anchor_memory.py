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
