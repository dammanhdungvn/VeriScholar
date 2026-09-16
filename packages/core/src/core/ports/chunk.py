"""Chunk Extractor Port Protocol.

Defines the port interface for extracting semantically coherent text chunks
with normalized spatial bounding boxes from PDF binaries in compliance with Hexagonal Architecture.
"""

from typing import Protocol
from uuid import UUID

from core.domain.entities.chunk import DocumentChunk


class IChunkExtractorPort(Protocol):
    """Abstract port for extracting layout-aware chunks with bounding boxes from scholarly PDFs."""

    def extract_chunks(
        self,
        pdf_bytes: bytes,
        document_id: UUID,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> list[DocumentChunk]:
        """Extract ordered chunks with spatial bounding boxes and token metrics.

        Args:
            pdf_bytes: Raw binary content of the PDF file.
            document_id: Associated document UUID.
            chunk_size: Target token size per chunk.
            chunk_overlap: Token overlap between consecutive chunks.

        Returns:
            List of DocumentChunk domain entities containing raw text,
            normalized bounding boxes [x0, y0, x1, y1, page], and token counts.
        """
        ...
