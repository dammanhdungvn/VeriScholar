"""Retrieval Search Port Protocol.

Defines the abstract interface for hybrid candidate chunk retrieval (dense vector + sparse lexical)
across documents in a session, complying with Hexagonal Architecture.
"""

from typing import Protocol, runtime_checkable
from uuid import UUID

from core.domain.entities.chunk import DocumentChunk


@runtime_checkable
class IRetrievalSearchPort(Protocol):
    """Port for candidate chunk retrieval (dense + sparse) across documents in a session."""

    async def search_candidates(
        self,
        session_id: UUID,
        query: str,
        dense_top_k: int = 25,
        sparse_top_k: int = 25,
        rrf_k: int = 60,
    ) -> list[DocumentChunk]:
        """Retrieve top candidate chunks for a query using hybrid dense and sparse search.

        Args:
            session_id: Active session identifier to scope search across session documents.
            query: User search query or question text.
            dense_top_k: Number of nearest neighbors to retrieve via dense embedding search.
            sparse_top_k: Number of chunks to retrieve via sparse full-text / BM25 search.
            rrf_k: Constant denominator for Reciprocal Rank Fusion blending.

        Returns:
            List of candidate DocumentChunk entities ordered by reciprocal rank score.
        """
        ...
