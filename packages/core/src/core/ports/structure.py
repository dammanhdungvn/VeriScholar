"""Structure Extractor Port Protocol.

Defines the port interface for extracting document outline (TOC), headings,
abstract, and visual bounding boxes from PDF streams in compliance with Hexagonal Architecture.
"""

from typing import Protocol
from uuid import UUID

from core.domain.entities.structure import DocumentStructure


class IStructureExtractorPort(Protocol):
    """Abstract port for extracting hierarchical structure from scholarly PDFs."""

    def extract_structure(
        self,
        pdf_bytes: bytes,
        document_id: UUID | None = None,
    ) -> DocumentStructure:
        """Extract table of contents, headings, abstract, and bounding boxes.

        Args:
            pdf_bytes: Raw binary content of the PDF file.
            document_id: Optional associated document UUID.

        Returns:
            DocumentStructure domain entity containing title, abstract,
            and ordered sections with normalized bounding boxes.
        """
        ...
