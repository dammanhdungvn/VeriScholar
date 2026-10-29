from api.services.session_chat_service import SessionChatService


def test_chunk_context_assembly_preserves_full_content_without_1000_char_cutoff():
    # Long academic abstract or section chunk of 1,500 characters
    long_content = (
        "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. "
        * 15
    )
    assert len(long_content) > 1400

    citations = [
        {
            "citation_id": "cit_1",
            "document_id": "doc-123",
            "document_title": "Attention Is All You Need",
            "page_number": 1,
            "bounding_boxes": [[0.2, 0.5, 0.8, 0.7, 1]],
        }
    ]

    selected_chunks = [
        (
            {
                "document_id": "doc-123",
                "page_number": 1,
                "content": long_content,
            },
            1.0,
        )
    ]

    evidence_blocks = SessionChatService._build_evidence_blocks(citations, selected_chunks)

    assert len(evidence_blocks) == 1
    assert evidence_blocks[0]["citation_id"] == "cit_1"
    # Content must NOT be truncated to 1,000 characters
    assert len(evidence_blocks[0]["content"]) == len(long_content)
    assert evidence_blocks[0]["content"] == long_content
