"""Document Summarizer Port Protocol.

Defines the port interface for generating 3-point grounded summaries
(problem_statement, contributions, limitations) from scholarly document content
in compliance with Hexagonal Architecture.
"""

from typing import Protocol
from uuid import UUID

from core.domain.entities.chunk import DocumentChunk
from core.domain.entities.summary import DocumentSummary


class IDocumentSummarizerPort(Protocol):
    """Abstract port for generating 3-point grounded summaries from academic papers."""

    async def summarize(
        self,
        document_id: UUID,
        title: str | None,
        abstract: str | None,
        chunks: list[DocumentChunk],
        pdf_bytes: bytes | None = None,
    ) -> DocumentSummary:
        """Generate a 3-point grounded summary for a document.

        Args:
            document_id: Associated document UUID.
            title: Paper title if available.
            abstract: Paper abstract if available.
            chunks: Ordered list of document chunks with spatial bounding boxes.
            pdf_bytes: Optional raw PDF bytes for micro-precision text search.

        Returns:
            DocumentSummary domain entity containing problem_statement,
            contributions, limitations with spatial visual grounding citations.
        """
        ...
