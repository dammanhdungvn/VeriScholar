"""PDF Annotator Port Protocol.

Defines the domain port interface for embedding ISO 32000-1 / ISO 32000-2
text markup annotations (highlights with rich popup comments), PDF Bookmarks (Outlines),
and document metadata into PDF byte streams.
"""

from typing import Protocol

from core.domain.value_objects.pdf_annotation import PdfAnnotation


class IPdfAnnotatorPort(Protocol):
    """Abstract port for embedding native highlight annotations into PDF documents."""

    def annotate_pdf(
        self,
        pdf_bytes: bytes,
        annotations: list[PdfAnnotation],
        document_title: str | None = None,
        authors: list[str] | None = None,
        add_bookmarks: bool = True,
    ) -> bytes:
        """Embed visual grounding highlight annotations into a PDF byte stream.

        Args:
            pdf_bytes: Original raw PDF binary stream.
            annotations: List of domain PdfAnnotation value objects.
            document_title: Optional academic paper title to inject into PDF metadata.
            authors: Optional list of authors to inject into PDF metadata.
            add_bookmarks: Whether to inject sidebar bookmarks/outlines tree for rapid navigation.

        Returns:
            New PDF binary stream with embedded ISO 32000 compliant annotations.
        """
        ...
