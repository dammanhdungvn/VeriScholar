"""Driven adapter for embedding native ISO 32000-1 / ISO 32000-2 PDF annotations using PyMuPDF."""

import logging
from typing import Any

import pymupdf
from core.domain.value_objects.pdf_annotation import PdfAnnotation
from core.ports.pdf_annotator import IPdfAnnotatorPort

logger = logging.getLogger(__name__)

CATEGORY_BOOKMARK_LABELS: dict[str, str] = {
    "problem_statement": "🟧 Problem Statement",
    "contributions": "🟩 Contributions",
    "limitations": "🟪 Limitations",
    "user_note": "📝 User Note",
}


class PyMuPdfAnnotator(IPdfAnnotatorPort):
    """Concrete implementation of IPdfAnnotatorPort using PyMuPDF (fitz)."""

    def annotate_pdf(
        self,
        pdf_bytes: bytes,
        annotations: list[PdfAnnotation],
        document_title: str | None = None,
        authors: list[str] | None = None,
        add_bookmarks: bool = True,
    ) -> bytes:
        """Embed visual grounding highlight annotations, bookmarks, and metadata into a PDF stream.

        Args:
            pdf_bytes: Original raw PDF binary stream.
            annotations: List of domain PdfAnnotation value objects.
            document_title: Optional academic paper title for PDF metadata.
            authors: Optional author names list for PDF metadata.
            add_bookmarks: Whether to inject sidebar bookmarks/outlines tree.

        Returns:
            New PDF binary stream with embedded ISO 32000 compliant annotations.
        """
        if not pdf_bytes:
            return b""

        # If no annotations and no metadata updates requested, return original bytes directly
        if not annotations and not document_title and not authors:
            return pdf_bytes

        doc: Any = None
        try:
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            total_pages = len(doc)
            embedded_count = 0

            # 1. Embed Native ISO 32000 Highlight Annotations
            for annot in annotations:
                page_idx = annot.page_number - 1
                if not (0 <= page_idx < total_pages):
                    logger.warning(
                        "Skipping annotation out of page bounds: page %s (total: %s)",
                        annot.page_number,
                        total_pages,
                    )
                    continue

                page = doc[page_idx]
                pw = page.rect.width
                ph = page.rect.height

                # Convert normalized [0.0, 1.0] bounding box coordinates to absolute PDF points
                x0 = max(0.0, min(annot.bounding_box.x0, 1.0)) * pw
                y0 = max(0.0, min(annot.bounding_box.y0, 1.0)) * ph
                x1 = max(0.0, min(annot.bounding_box.x1, 1.0)) * pw
                y1 = max(0.0, min(annot.bounding_box.y1, 1.0)) * ph

                if x0 >= x1 or y0 >= y1:
                    logger.warning(
                        "Skipping degenerate bounding box: x0=%s, y0=%s, x1=%s, y1=%s",
                        x0,
                        y0,
                        x1,
                        y1,
                    )
                    continue

                rect = pymupdf.Rect(x0, y0, x1, y1)

                try:
                    ha = page.add_highlight_annot(rect)
                    ha.set_colors(stroke=annot.color_rgb)
                    ha.set_opacity(annot.opacity)
                    ha.set_info(
                        title=annot.title,
                        content=annot.content,
                        subject=annot.category.value,
                    )
                    ha.update()
                    embedded_count += 1
                except Exception as ex:
                    logger.warning(
                        "Failed to add highlight annotation on page %s: %s",
                        annot.page_number,
                        ex,
                    )

            logger.info("Successfully embedded %s annotations into PDF", embedded_count)

            # 2. Inject Sidebar Bookmarks / Outlines Navigation Tree
            if add_bookmarks and annotations:
                try:
                    min_page = min(a.page_number for a in annotations)
                    new_entries: list[list[Any]] = [
                        [1, "📑 VeriScholar AI Grounded Summary", min_page]
                    ]
                    seen_categories: set[str] = set()
                    for annot in sorted(
                        annotations, key=lambda a: (a.page_number, a.category.value)
                    ):
                        cat_val = annot.category.value
                        if cat_val not in seen_categories:
                            seen_categories.add(cat_val)
                            label = CATEGORY_BOOKMARK_LABELS.get(cat_val, annot.title)
                            new_entries.append([2, label, annot.page_number])

                    existing_toc = doc.get_toc(simple=True)
                    combined_toc = new_entries + existing_toc
                    doc.set_toc(combined_toc)
                    logger.info("Injected %s bookmark entries into PDF", len(new_entries))
                except Exception as ex:
                    logger.warning("Failed to set PDF bookmarks: %s", ex)

            # 3. Inject Standardized Academic PDF Metadata (Zotero/Mendeley support)
            try:
                meta = dict(doc.metadata or {})
                if document_title:
                    meta["title"] = document_title
                if authors:
                    meta["author"] = ", ".join(authors)
                meta["subject"] = "VeriScholar AI Grounded Summary (ISO 32000)"
                meta["keywords"] = "VeriScholar, AI Summary, Visual Grounding, ISO 32000"
                meta["producer"] = "VeriScholar AI Research Assistant (verischolar.org)"
                meta["creator"] = "VeriScholar PDF Engine"
                doc.set_metadata(meta)
            except Exception as ex:
                logger.warning("Failed to set PDF metadata: %s", ex)

            output_bytes = doc.tobytes(garbage=3, deflate=True)
            return output_bytes
        finally:
            if doc is not None:
                try:
                    doc.close()
                except Exception:
                    pass
