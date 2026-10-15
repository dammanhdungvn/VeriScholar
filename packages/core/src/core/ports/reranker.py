"""Cross-Encoder Reranker Port Protocol.

Defines the abstract interface for cross-encoder reranking models (e.g. Cohere rerank-v3.5,
BAAI/bge-reranker-v2-m3) and relevance thresholding (>= 0.35) in compliance with
Hexagonal Architecture.
"""

from typing import Protocol, runtime_checkable

from core.domain.entities.chunk import DocumentChunk

DEFAULT_RELEVANCE_THRESHOLD: float = 0.35


@runtime_checkable
class ICrossEncoderRerankerPort(Protocol):
    """Port for cross-encoder reranking and relevance threshold cutoff (>= 0.35)."""

    async def rerank(
        self,
        query: str,
        chunks: list[DocumentChunk],
        top_n: int = 5,
        relevance_threshold: float = DEFAULT_RELEVANCE_THRESHOLD,
    ) -> list[tuple[DocumentChunk, float]]:
        """Rerank candidate chunks for a query and filter by relevance cutoff threshold.

        Args:
            query: Query or question string against which chunks are reranked.
            chunks: Candidate DocumentChunk instances to be scored.
            top_n: Maximum number of reranked chunks to return.
            relevance_threshold: Minimum cross-encoder score cutoff (default 0.35). Chunks below
                this score are discarded. If all chunks fall below threshold, returns empty list
                to trigger active abstention.

        Returns:
            List of (chunk, relevance_score) tuples ordered descending by score.
        """
        ...
