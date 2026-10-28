import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

# Ensure repo root is in sys.path if invoked from different directories
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from apps.api.src.api.services.session_chat_service import SessionChatService
except ModuleNotFoundError:
    from api.services.session_chat_service import SessionChatService


@pytest.mark.asyncio
async def test_detect_full_section_intent():
    assert (
        SessionChatService._is_full_section_query(
            "Dịch toàn bộ phần 1 Introduction sang tiếng việt"
        )
        is True
    )
    assert SessionChatService._is_full_section_query("Tóm tắt tất cả mục 2") is True
    assert SessionChatService._is_full_section_query("Công thức A(H) là gì?") is False


@pytest.mark.asyncio
async def test_contiguous_section_expansion_stops_at_next_section():
    # Chunks: 6 (Intro), 7 (Intro p2), 8 (Intro p3), 9 (Intro p4), 10 (2 Background)
    service = SessionChatService(db=AsyncMock())
    doc_id = uuid4()

    mock_chunks = [
        MagicMock(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=6,
            page_number=2,
            content="1 Introduction\nRecurrent neural networks...",
        ),
        MagicMock(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=7,
            page_number=2,
            content="Recurrent models typically factor computation...",
        ),
        MagicMock(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=8,
            page_number=2,
            content="Attention mechanisms have become an integral part...",
        ),
        MagicMock(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=9,
            page_number=2,
            content="In this work we propose the Transformer...",
        ),
        MagicMock(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=10,
            page_number=2,
            content="2 Background\nThe goal of reducing sequential computation...",
        ),
    ]

    expanded = service._filter_contiguous_section_chunks(mock_chunks, start_chunk_index=6)
    assert len(expanded) == 4
    assert [c.chunk_index for c in expanded] == [6, 7, 8, 9]
    assert 10 not in [c.chunk_index for c in expanded]


@pytest.mark.asyncio
async def test_contiguous_section_expansion_max_chunks_limit():
    service = SessionChatService(db=AsyncMock())
    doc_id = uuid4()

    mock_chunks = [
        MagicMock(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=i,
            page_number=2,
            content=f"Body paragraph of section {i} without next header...",
        )
        for i in range(1, 10)
    ]

    expanded = service._filter_contiguous_section_chunks(
        mock_chunks, start_chunk_index=1, max_chunks=4
    )
    assert len(expanded) == 4
    assert [c.chunk_index for c in expanded] == [1, 2, 3, 4]


@pytest.mark.asyncio
async def test_contiguous_section_expansion_gap_detection():
    service = SessionChatService(db=AsyncMock())
    doc_id = uuid4()

    # Chunks with index 1, 2, gap at 3, then 4, 5
    mock_chunks = [
        MagicMock(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=1,
            page_number=1,
            content="1 Introduction\nText...",
        ),
        MagicMock(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=2,
            page_number=1,
            content="Continuation...",
        ),
        MagicMock(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=4,
            page_number=2,
            content="After gap...",
        ),
    ]

    expanded = service._filter_contiguous_section_chunks(mock_chunks, start_chunk_index=1)
    assert len(expanded) == 2
    assert [c.chunk_index for c in expanded] == [1, 2]


@pytest.mark.asyncio
async def test_expand_contiguous_section_chunks_queries_db():
    mock_db = AsyncMock()
    service = SessionChatService(db=mock_db)
    doc_id = uuid4()

    mock_chunks = [
        MagicMock(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=6,
            page_number=2,
            content="1 Introduction\nRecurrent neural networks...",
        ),
        MagicMock(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=7,
            page_number=2,
            content="Recurrent models typically factor computation...",
        ),
        MagicMock(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=8,
            page_number=2,
            content="2 Background\nThe goal...",
        ),
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_chunks
    mock_db.execute.return_value = mock_result

    expanded = await service._expand_contiguous_section_chunks(
        document_id=doc_id, start_chunk_index=6, max_chunks=6
    )
    assert len(expanded) == 2
    assert [c.chunk_index for c in expanded] == [6, 7]


@pytest.mark.asyncio
async def test_contiguous_section_expansion_ignores_body_numbered_lists():
    """Verify that chunks containing body numbered lists (e.g. '1. We propose...')
    are NOT prematurely truncated by _filter_contiguous_section_chunks.
    """
    service = SessionChatService(db=AsyncMock())
    doc_id = uuid4()

    mock_chunks = [
        MagicMock(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=6,
            page_number=2,
            content="1 Introduction\nIn recent years, deep learning has advanced rapidly.",
            token_count=100,
        ),
        MagicMock(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=7,
            page_number=2,
            content=(
                "Our primary contributions are twofold:\n"
                "1. We propose an attention-only architecture that dispenses with recurrence.\n"
                "2. We demonstrate state-of-the-art BLEU scores on translation tasks."
            ),
            token_count=120,
        ),
        MagicMock(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=8,
            page_number=3,
            content="The remainder of this paper is structured as follows.",
            token_count=80,
        ),
        MagicMock(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=9,
            page_number=3,
            content=(
                "2 Background\nRecurrent models typically factor computation along "
                "the symbol positions."
            ),
            token_count=110,
        ),
    ]

    expanded = service._filter_contiguous_section_chunks(mock_chunks, start_chunk_index=6)
    # Chunks 6, 7, and 8 should all be included. Chunk 9 (Section 2 Background) halts expansion.
    assert len(expanded) == 3
    assert [c.chunk_index for c in expanded] == [6, 7, 8]
    assert 9 not in [c.chunk_index for c in expanded]


@pytest.mark.asyncio
async def test_contiguous_section_expansion_enforces_token_ceiling():
    """Verify expansion halts when token count exceeds max_tokens (default 4000)."""
    service = SessionChatService(db=AsyncMock())
    doc_id = uuid4()

    mock_chunks = [
        MagicMock(
            id=uuid4(),
            document_id=doc_id,
            chunk_index=i,
            page_number=1,
            content=f"Chunk {i} body text...",
            token_count=1500,
        )
        for i in range(1, 5)
    ]

    # chunk 1: 1500 tokens
    # chunk 2: 1500 tokens -> total 3000 <= 4000
    # chunk 3: 1500 tokens -> total 4500 > 4000 -> halted
    expanded = service._filter_contiguous_section_chunks(
        mock_chunks, start_chunk_index=1, max_tokens=4000
    )
    assert len(expanded) == 2
    assert [c.chunk_index for c in expanded] == [1, 2]

    # Custom max_tokens=2500 -> chunk 1: 1500 <= 2500, chunk 2: 1500 + 1500 = 3000 > 2500 -> halted
    expanded_custom = service._filter_contiguous_section_chunks(
        mock_chunks, start_chunk_index=1, max_tokens=2500
    )
    assert len(expanded_custom) == 1
    assert [c.chunk_index for c in expanded_custom] == [1]


def test_is_next_section_header_heuristics():
    """Unit test precise heading detection vs body enumerations."""
    # Valid next section headings
    assert SessionChatService._is_next_section_header("2 Background", start_section_num=1) is True
    assert SessionChatService._is_next_section_header("2. Background", start_section_num=1) is True
    assert SessionChatService._is_next_section_header("3 Methodology", start_section_num=1) is True
    assert (
        SessionChatService._is_next_section_header("## 2 Background", start_section_num=1) is True
    )
    assert (
        SessionChatService._is_next_section_header("## Related Work", start_section_num=1) is True
    )
    assert SessionChatService._is_next_section_header("Related Work", start_section_num=1) is True

    # Body sentences and numbered list items (MUST NOT MATCH)
    assert (
        SessionChatService._is_next_section_header(
            "1. We introduce the Transformer model", start_section_num=1
        )
        is False
    )
    assert (
        SessionChatService._is_next_section_header("1. We propose our method.", start_section_num=1)
        is False
    )
    assert (
        SessionChatService._is_next_section_header(
            "2. We also evaluate the model on WMT.", start_section_num=1
        )
        is False
    )
    assert (
        SessionChatService._is_next_section_header(
            "In this section, we discuss Background in detail.", start_section_num=1
        )
        is False
    )
    assert (
        SessionChatService._is_next_section_header("1 Introduction", start_section_num=1) is False
    )


@pytest.mark.asyncio
async def test_retrieve_evidence_full_section_retains_6_chunks():
    """Verify that full section queries retain up to 6 chunks instead of being capped to 5."""
    mock_db = AsyncMock()
    service = SessionChatService(db=mock_db)
    doc_id = uuid4()
    user_id = uuid4()
    session_id = uuid4()

    candidate_chunks = [
        {
            "chunk_id": f"chk_{i}",
            "id": f"chk_{i}",
            "document_id": str(doc_id),
            "chunk_index": i,
            "page_number": 1,
            "content": f"Section content part {i}",
            "text_content": f"Section content part {i}",
            "bounding_boxes": [[0.1, 0.1, 0.9, 0.2, 1]],
            "token_count": 100,
            "document_title": "Paper Title",
            "filename": "paper.pdf",
            "max_cosine_sim": 0.9,
            "rrf_score": 2.0,
        }
        for i in range(1, 7)  # 6 chunks
    ]

    service.transform_query = AsyncMock(
        return_value=("Dịch toàn bộ phần 1 Introduction", [0.1] * 1536)
    )
    service.retrieve_hybrid_chunks = AsyncMock(return_value=candidate_chunks)
    service.evaluate_crag_and_expand = AsyncMock(return_value=("CORRECT", candidate_chunks, False))

    # Question with full section intent
    chunks, citations, abstain = await service.retrieve_and_prepare_context(
        session_id=session_id,
        user_id=user_id,
        question="Dịch toàn bộ phần 1 Introduction",
        target_doc_ids=[doc_id],
        limit=10,
    )

    assert abstain is False
    assert len(chunks) == 6
    assert len(citations) == 6
