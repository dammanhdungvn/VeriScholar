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
