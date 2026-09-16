"""Driven adapter for extracting scholarly document structure using PyMuPDF (fitz)."""

import re
from uuid import UUID

import pymupdf
from core.domain.entities.structure import DocumentSection, DocumentStructure
from core.domain.value_objects.bounding_box import BoundingBox
from core.ports.structure import IStructureExtractorPort

_TITLE_MAX_PAGE_HEIGHT_RATIO: float = 0.45
_MAX_HEADING_TEXT_LENGTH: int = 80
_MAX_HEADING_PREFIX_LENGTH_DIFF: int = 15


class PyMuPDFStructureExtractor(IStructureExtractorPort):
    """Concrete implementation of IStructureExtractorPort using PyMuPDF (fitz)."""

    HEADING_NUMBER_REGEX = re.compile(
        r"^(?:([1-9]\d*(?:\.\d+)*)\s+)?([A-Z][a-zA-Z0-9\s\:\?\–—]+)$"
    )
    KNOWN_SECTION_KEYWORDS = {
        "abstract",
        "introduction",
        "background",
        "related work",
        "preliminaries",
        "methodology",
        "method",
        "proposed method",
        "model architecture",
        "system architecture",
        "experimental setup",
        "experiments",
        "results",
        "results and analysis",
        "discussion",
        "conclusion",
        "conclusions",
        "future work",
        "acknowledgements",
        "references",
        "bibliography",
        "appendix",
    }

    def extract_structure(
        self,
        pdf_bytes: bytes,
        document_id: UUID | None = None,
    ) -> DocumentStructure:
        """Extract table of contents, headings, abstract, and bounding boxes from PDF binary."""
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        if len(doc) == 0:
            return DocumentStructure(document_id=document_id, sections=[])

        title = self._extract_title(doc)
        abstract_text, abstract_boxes = self._extract_abstract(doc)
        sections = self._extract_sections(doc)

        return DocumentStructure(
            document_id=document_id,
            title=title,
            abstract=abstract_text,
            abstract_bounding_boxes=abstract_boxes,
            sections=sections,
        )

    def _extract_title(self, doc: pymupdf.Document) -> str | None:
        """Extract the academic paper title from PDF metadata or page 1 prominent header block."""
        first_page = doc[0]
        blocks = first_page.get_text("blocks")
        candidate_blocks: list[tuple[float, str]] = []

        # Filter out common license notices and small footers
        for b in blocks:
            text = " ".join(b[4].strip().split())
            if not text or len(text) < 4:
                continue
            lower_text = text.lower()
            if (
                "google hereby grants" in lower_text
                or "arxiv:" in lower_text
                or "all rights reserved" in lower_text
                or "conference" in lower_text
                or "proceedings" in lower_text
            ):
                continue
            # Y-coordinate check: title is usually in the top half of page 1
            y1 = b[3]
            page_height = first_page.rect.height
            if y1 <= page_height * _TITLE_MAX_PAGE_HEIGHT_RATIO:
                # Estimate font size by height / number of lines
                num_lines = max(1, len(b[4].strip().splitlines()))
                line_height = (b[3] - b[1]) / num_lines
                candidate_blocks.append((line_height, text))

        if candidate_blocks:
            # Pick the block with highest average line height
            candidate_blocks.sort(key=lambda x: x[0], reverse=True)
            candidate_title = candidate_blocks[0][1]
            # Avoid picking author affiliations as title
            if "@" not in candidate_title and "department" not in candidate_title.lower():
                return candidate_title

        # Fallback to document metadata title if valid
        meta_title = doc.metadata.get("title")
        if meta_title and len(meta_title.strip()) > 3:
            cleaned_meta = " ".join(meta_title.strip().split())
            if not cleaned_meta.lower().startswith("untitled"):
                return cleaned_meta

        return None

    def _extract_abstract(
        self, doc: pymupdf.Document
    ) -> tuple[str | None, list[BoundingBox]]:
        """Locate Abstract heading and paragraph on page 1 (or 2) with normalized bounding box."""
        for page_idx in range(min(2, len(doc))):
            page = doc[page_idx]
            width = page.rect.width
            height = page.rect.height
            blocks = page.get_text("blocks")

            for i, b in enumerate(blocks):
                cleaned_block = " ".join(b[4].strip().split())
                if cleaned_block.lower() == "abstract" or cleaned_block.lower().startswith(
                    "abstract:"
                ):
                    # The following block is typically the abstract body
                    if i + 1 < len(blocks):
                        body_block = blocks[i + 1]
                        abstract_text = " ".join(body_block[4].strip().split())
                        # Check bounding box
                        x0 = max(0.0, min(1.0, body_block[0] / width))
                        y0 = max(0.0, min(1.0, body_block[1] / height))
                        x1 = max(0.0, min(1.0, body_block[2] / width))
                        y1 = max(0.0, min(1.0, body_block[3] / height))

                        if x0 < x1 and y0 < y1:
                            box = BoundingBox(
                                x0=round(x0, 4),
                                y0=round(y0, 4),
                                x1=round(x1, 4),
                                y1=round(y1, 4),
                                page=page_idx + 1,
                            )
                            return abstract_text, [box]

                # Or the block itself contains "Abstract\n..."
                if b[4].strip().lower().startswith("abstract"):
                    lines = b[4].strip().splitlines()
                    body_lines = [line.strip() for line in lines[1:] if line.strip()]
                    if body_lines:
                        abstract_text = " ".join(body_lines)
                        x0 = max(0.0, min(1.0, b[0] / width))
                        y0 = max(0.0, min(1.0, b[1] / height))
                        x1 = max(0.0, min(1.0, b[2] / width))
                        y1 = max(0.0, min(1.0, b[3] / height))
                        if x0 < x1 and y0 < y1:
                            box = BoundingBox(
                                x0=round(x0, 4),
                                y0=round(y0, 4),
                                x1=round(x1, 4),
                                y1=round(y1, 4),
                                page=page_idx + 1,
                            )
                            return abstract_text, [box]

        return None, []

    def _extract_sections(self, doc: pymupdf.Document) -> list[DocumentSection]:
        """Extract hierarchical or sequential sections using PDF TOC or Heuristic scanning."""
        # Tier 1: Try PDF Outline / Bookmarks (get_toc)
        toc = doc.get_toc()
        if len(toc) >= 2:
            return self._build_sections_from_toc(doc, toc)

        # Tier 2: Heuristic Text Block Scanning
        return self._build_sections_from_heuristic(doc)

    def _build_sections_from_toc(
        self, doc: pymupdf.Document, toc: list[list]
    ) -> list[DocumentSection]:
        """Build sections list from PyMuPDF TOC outline entries."""
        sections: list[DocumentSection] = []
        for item in toc:
            _, raw_title, page_num = item[0], item[1].strip(), item[2]
            if not raw_title or page_num < 1 or page_num > len(doc):
                continue

            page = doc[page_num - 1]
            width = page.rect.width
            height = page.rect.height

            # Try to match a block on page that has heading number e.g. "1 Introduction"
            resolved_title = raw_title
            resolved_bbox: tuple[float, float, float, float] | None = None

            blocks = page.get_text("blocks")
            for b in blocks:
                cleaned_text = " ".join(b[4].strip().split())
                if cleaned_text.lower().endswith(
                    raw_title.lower()
                ) and len(cleaned_text) < len(raw_title) + _MAX_HEADING_PREFIX_LENGTH_DIFF:
                    resolved_title = cleaned_text
                    resolved_bbox = (b[0], b[1], b[2], b[3])
                    break

            boxes: list[BoundingBox] = []
            if resolved_bbox:
                x0 = max(0.0, min(1.0, resolved_bbox[0] / width))
                y0 = max(0.0, min(1.0, resolved_bbox[1] / height))
                x1 = max(0.0, min(1.0, resolved_bbox[2] / width))
                y1 = max(0.0, min(1.0, resolved_bbox[3] / height))
                if x0 < x1 and y0 < y1:
                    boxes.append(
                        BoundingBox(
                            x0=round(x0, 4),
                            y0=round(y0, 4),
                            x1=round(x1, 4),
                            y1=round(y1, 4),
                            page=page_num,
                        )
                    )

            sections.append(
                DocumentSection(
                    title=resolved_title,
                    page_number=page_num,
                    bounding_boxes=boxes,
                )
            )

        return sections

    def _build_sections_from_heuristic(
        self, doc: pymupdf.Document
    ) -> list[DocumentSection]:
        """Heuristically detect section headings from page text blocks."""
        sections: list[DocumentSection] = []
        seen_titles: set[str] = set()

        for page_idx in range(len(doc)):
            page: pymupdf.Page = doc[page_idx]
            page_num = page_idx + 1
            width = page.rect.width
            height = page.rect.height
            blocks = page.get_text("blocks")

            for b in blocks:
                cleaned = " ".join(b[4].strip().split())
                if not cleaned or len(cleaned) > _MAX_HEADING_TEXT_LENGTH:
                    continue

                # Check if matches numbered heading (e.g. "1 Introduction", "3.1 Encoder")
                # or known section keywords
                is_heading = False
                lower_cleaned = cleaned.lower()

                match = self.HEADING_NUMBER_REGEX.match(cleaned)
                if match:
                    sec_num, sec_title = match.group(1), match.group(2).strip()
                    if sec_num or any(k in sec_title.lower() for k in self.KNOWN_SECTION_KEYWORDS):
                        if not sec_title.endswith((".", ";", ",")):
                            is_heading = True
                elif lower_cleaned in self.KNOWN_SECTION_KEYWORDS:
                    is_heading = True

                if is_heading and cleaned not in seen_titles:
                    seen_titles.add(cleaned)
                    x0 = max(0.0, min(1.0, b[0] / width))
                    y0 = max(0.0, min(1.0, b[1] / height))
                    x1 = max(0.0, min(1.0, b[2] / width))
                    y1 = max(0.0, min(1.0, b[3] / height))
                    if x0 < x1 and y0 < y1:
                        box = BoundingBox(
                            x0=round(x0, 4),
                            y0=round(y0, 4),
                            x1=round(x1, 4),
                            y1=round(y1, 4),
                            page=page_num,
                        )
                        sections.append(
                            DocumentSection(
                                title=cleaned,
                                page_number=page_num,
                                bounding_boxes=[box],
                            )
                        )

        return sections
