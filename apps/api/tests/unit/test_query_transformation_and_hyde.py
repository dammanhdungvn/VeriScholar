"""Unit tests for Query Improvement Engine (Condense Type II & HyDE Cross-Lingual Generator)."""

from unittest.mock import AsyncMock, patch

import pytest
from api.services.session_chat_service import SessionChatService


@pytest.mark.asyncio
async def test_transform_query_generates_condensed_and_hyde_vector(db_session):
    """Test transform_query produces condensed query resolving coreferences and 1536-d vector."""
    service = SessionChatService(db=db_session)
    with (
        patch.object(service, "_generate_hyde_doc", new_callable=AsyncMock) as mock_hyde,
        patch(
            "api.services.embedding_service.EmbeddingService.get_embedding",
            new_callable=AsyncMock,
        ) as mock_embed,
    ):
        mock_hyde.return_value = (
            "Answer Relevance (AR) formula in Ragas evaluates cosine similarity..."
        )
        mock_embed.return_value = [0.05] * 1536

        condensed_q, hyde_vec = await service.transform_query(
            raw_query="Công thức AR của nó là gì?",
            chat_history=[{"role": "user", "content": "Tôi đang đọc bài báo Ragas"}],
        )
        assert "Ragas" in condensed_q or "AR" in condensed_q
        assert len(hyde_vec) == 1536
        assert isinstance(hyde_vec[0], float)
        mock_hyde.assert_called_once()
        mock_embed.assert_called_once()


@pytest.mark.asyncio
async def test_transform_query_empty_history_returns_raw_query(db_session):
    """When chat history is empty, condensed query should match raw_query.strip()."""
    service = SessionChatService(db=db_session)
    with (
        patch.object(service, "_generate_hyde_doc", new_callable=AsyncMock) as mock_hyde,
        patch(
            "api.services.embedding_service.EmbeddingService.get_embedding",
            new_callable=AsyncMock,
        ) as mock_embed,
    ):
        mock_hyde.return_value = (
            "Self-attention mechanisms calculate attention scores using query-key dot products."
        )
        mock_embed.return_value = [0.01] * 1536

        condensed_q, hyde_vec = await service.transform_query(
            raw_query="  What is the attention equation?  ",
            chat_history=[],
        )
        assert condensed_q == "What is the attention equation?"
        assert len(hyde_vec) == 1536


@pytest.mark.asyncio
async def test_transform_query_populated_history_resolves_anaphora(db_session):
    """Test resolution of Vietnamese and English coreferences over multi-turn history."""
    service = SessionChatService(db=db_session)
    history = [
        {"role": "user", "content": "Bài báo giới thiệu kiến trúc Mamba-2."},
        {"role": "assistant", "content": "Mamba-2 cải tiến State Space Model với cơ chế SSD."},
    ]

    with (
        patch.object(service, "_generate_hyde_doc", new_callable=AsyncMock) as mock_hyde,
        patch(
            "api.services.embedding_service.EmbeddingService.get_embedding",
            new_callable=AsyncMock,
        ) as mock_embed,
    ):
        mock_hyde.return_value = "The SSD algorithm in Mamba-2 optimizes matrix multiplications..."
        mock_embed.return_value = [0.02] * 1536

        condensed_q, _ = await service.transform_query(
            raw_query="Độ phức tạp tính toán của mô hình này là bao nhiêu?",
            chat_history=history,
        )
        assert "Mamba-2" in condensed_q or "Mamba" in condensed_q


@pytest.mark.asyncio
async def test_generate_hyde_doc_academic_content(db_session):
    """Directly test _generate_hyde_doc generates academic passage for English and Vietnamese queries."""
    service = SessionChatService(db=db_session)

    # 1. Vietnamese query -> English academic passage
    hyde_vi = await service._generate_hyde_doc("Công thức Answer Relevance trong Ragas")
    assert isinstance(hyde_vi, str)
    assert len(hyde_vi.split()) >= 15
    assert (
        "formula" in hyde_vi.lower()
        or "relevance" in hyde_vi.lower()
        or "ragas" in hyde_vi.lower()
        or "academic" in hyde_vi.lower()
    )

    # 2. English query -> English academic passage
    hyde_en = await service._generate_hyde_doc("FlashAttention memory complexity analysis")
    assert isinstance(hyde_en, str)
    assert len(hyde_en.split()) >= 15
    assert (
        "flashattention" in hyde_en.lower()
        or "complexity" in hyde_en.lower()
        or "memory" in hyde_en.lower()
    )


@pytest.mark.asyncio
async def test_transform_query_embedding_failure_fallback_zeroes(db_session):
    """When embedding generation fails, transform_query must not crash and return zero vector."""
    service = SessionChatService(db=db_session)
    with (
        patch.object(service, "_generate_hyde_doc", new_callable=AsyncMock) as mock_hyde,
        patch(
            "api.services.embedding_service.EmbeddingService.get_embedding",
            new_callable=AsyncMock,
        ) as mock_embed,
    ):
        mock_hyde.return_value = "Hypothetical academic passage"
        mock_embed.side_effect = RuntimeError("OpenAI API unreachable or rate limited")

        condensed_q, hyde_vec = await service.transform_query(
            raw_query="Phương pháp huấn luyện là gì?",
            chat_history=[],
        )
        assert condensed_q == "Phương pháp huấn luyện là gì?"
        assert len(hyde_vec) == 1536
        assert all(v == 0.0 for v in hyde_vec)
