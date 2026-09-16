"""Driven adapter for extracting layout-aware chunks using PyMuPDF (fitz).

Implements IChunkExtractorPort to produce semantically coherent text chunks
with normalized spatial bounding boxes and token counts for visual PDF grounding.
"""

import re
from collections.abc import Sequence
from uuid import UUID, uuid4

import pymupdf
from core.domain.entities.chunk import DocumentChunk
from core.domain.value_objects.bounding_box import BoundingBox
from core.ports.chunk import IChunkExtractorPort

_MIN_CHUNK_CHAR_LENGTH = 15
_TARGET_MAX_CHUNK_TOKENS = 350
_PAGE_MARGIN_RATIO_HEADER = 0.04
_PAGE_MARGIN_RATIO_FOOTER = 0.96

_SENTENCE_TERMINATORS = {".", "!", "?", ":", '"', "”", ")", "]", ";"}

_DISCLAIMER_PATTERNS = [
    re.compile(
        r"permission to reproduce|proper attribution is provided|all rights reserved|"
        r"under review as a conference paper|draft – not for circulation|scholarly works",
        re.IGNORECASE,
    ),
]

_EQUATION_PATTERNS = [
    re.compile(r"^(Attention|MultiHead|FFN|PE)\s*\(", re.IGNORECASE),
    re.compile(r"^.+=\s*(softmax|max|min|sin|cos|Concat)\s*\(", re.IGNORECASE),
]

_MATH_SYMBOLS = ("softmax", "∈", "∑", "√", "dmodel", "dv", "dk")
_CAPTION_PATTERN = re.compile(r"^(Figure|Table|Fig\.)\s+\d+[:\.]", re.IGNORECASE)
_FOOTNOTE_URL_PATTERN = re.compile(r"^\d+\s+https?://", re.IGNORECASE)


class PyMuPDFChunkExtractor(IChunkExtractorPort):
    """Concrete implementation of IChunkExtractorPort using PyMuPDF (fitz)."""

    SENTENCE_SPLIT_REGEX = re.compile(r"(?<=[.!?])\s+")
    DEHYPHEN_REGEX = re.compile(r"(\b[a-zA-Z]{2,})-\n\s*([a-zA-Z]{2,}\b)")

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
            chunk_size: Target token size per chunk (default 500).
            chunk_overlap: Token overlap between consecutive chunks (default 50).

        Returns:
            List of DocumentChunk domain entities with 0-based chunk_index,
            normalized [x0, y0, x1, y1, page] bounding boxes, and word token counts.
        """
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        if len(doc) == 0:
            return []

        all_ordered_blocks: list[tuple[float, float, float, float, str, int, float, float]] = []

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_rect = page.rect
            width = page_rect.width or 1.0
            height = page_rect.height or 1.0
            page_num = page_idx + 1

            # 1. Extract raw blocks: (x0, y0, x1, y1, text, block_no, block_type)
            raw_blocks = page.get_text("blocks")
            filtered_blocks: list[tuple[float, float, float, float, str, int, float, float]] = []

            for b in raw_blocks:
                if len(b) < 7 or b[6] != 0:
                    continue

                bx0, by0, bx1, by1, raw_text, _, _ = b
                text = raw_text.strip()
                if not text:
                    continue

                # Filter vertical margin stamps (e.g. rotated arXiv margin watermarks)
                if (bx1 - bx0) < 40 and (by1 - by0) > 100 and (bx0 / width) < 0.1:
                    continue

                # Filter disclaimer banners on opening pages
                if page_num <= 2 and any(p.search(text) for p in _DISCLAIMER_PATTERNS):
                    continue

                y0_norm = by0 / height
                y1_norm = by1 / height
                words = text.split()

                # Filter running headers with page numbers at the top of pages (y1_norm < 0.14)
                if page_num > 1 and y1_norm < 0.14 and len(words) <= 6:
                    if words[0] == str(page_num) or words[-1] == str(page_num):
                        continue

                # Filter standalone footnote references at bottom of pages
                if y0_norm > 0.75 and _FOOTNOTE_URL_PATTERN.match(text):
                    continue

                # Filter page header/footer standalone numbers or running heads
                is_edge_margin = (
                    y1_norm < _PAGE_MARGIN_RATIO_HEADER or y0_norm > _PAGE_MARGIN_RATIO_FOOTER
                )
                if is_edge_margin and len(words) <= 4:
                    continue

                # Filter isolated single-word diagram scatter (e.g. heatmap diagram labels)
                if len(words) <= 2 and len(text) < 15 and (bx1 - bx0) < 60:
                    continue

                filtered_blocks.append((bx0, by0, bx1, by1, text, page_num, width, height))

            if not filtered_blocks:
                continue

            # 2. Multi-column detection and layout-aware sorting
            ordered_page_blocks = self._order_page_blocks(filtered_blocks, width)
            all_ordered_blocks.extend(ordered_page_blocks)

        # 3. Assemble continuous paragraphs across blocks and pages
        return self._assemble_chunks_across_document(
            all_blocks=all_ordered_blocks,
            document_id=document_id,
            target_max_tokens=min(chunk_size, _TARGET_MAX_CHUNK_TOKENS),
        )

    def _order_page_blocks(
        self,
        blocks: list[tuple[float, float, float, float, str, int, float, float]],
        page_width: float,
    ) -> list[tuple[float, float, float, float, str, int, float, float]]:
        """Order blocks to respect multi-column layout."""
        mid_x = page_width * 0.5
        col_width_max = page_width * 0.55

        # Only consider substantial blocks to judge column layout
        sub_blocks = [b for b in blocks if len(b[4].strip().split()) >= 10]
        left_sub = [b for b in sub_blocks if b[2] <= mid_x + 15 and (b[2] - b[0]) < col_width_max]
        right_sub = [b for b in sub_blocks if b[0] >= mid_x - 15 and (b[2] - b[0]) < col_width_max]

        is_two_column = len(left_sub) >= 1 and len(right_sub) >= 1
        if not is_two_column:
            return sorted(blocks, key=lambda b: (b[1], b[0]))

        col_top = min(min(b[1] for b in left_sub), min(b[1] for b in right_sub))
        col_bottom = max(max(b[3] for b in left_sub), max(b[3] for b in right_sub))

        spans_top = sorted([b for b in blocks if b[3] <= col_top + 5], key=lambda b: b[1])
        left_col = sorted(
            [
                b
                for b in blocks
                if b not in spans_top and b[2] <= mid_x + 15 and b[1] < col_bottom + 5
            ],
            key=lambda b: b[1],
        )
        right_col = sorted(
            [
                b
                for b in blocks
                if b not in spans_top and b[0] >= mid_x - 15 and b[1] < col_bottom + 5
            ],
            key=lambda b: b[1],
        )
        spans_bottom = sorted(
            [
                b
                for b in blocks
                if b[1] >= col_bottom - 5
                and b not in spans_top
                and b not in left_col
                and b not in right_col
            ],
            key=lambda b: b[1],
        )

        handled = set(spans_top + left_col + right_col + spans_bottom)
        others = sorted([b for b in blocks if b not in handled], key=lambda b: b[1])

        return spans_top + left_col + right_col + spans_bottom + others

    def _assemble_chunks_across_document(
        self,
        all_blocks: Sequence[tuple[float, float, float, float, str, int, float, float]],
        document_id: UUID,
        target_max_tokens: int,
    ) -> list[DocumentChunk]:
        """Assemble flowing blocks across pages into semantic chunks."""
        chunks: list[DocumentChunk] = []
        pending_text = ""
        pending_boxes: list[BoundingBox] = []
        pending_page = 1
        pending_is_heading = False
        counter = 0

        # Buffer for holding a paragraph from page P waiting for lowercase continuation on page P+1
        cross_page_buffer: tuple[str, list[BoundingBox], int] | None = None

        def flush_pending() -> None:
            nonlocal pending_text, pending_boxes, pending_page, pending_is_heading, counter
            if not pending_text:
                return
            clean_chunk_text = pending_text.rstrip("-").strip()
            tokens = len(clean_chunk_text.split())
            chunks.append(
                DocumentChunk(
                    id=uuid4(),
                    document_id=document_id,
                    chunk_index=counter,
                    page_number=pending_page,
                    content=clean_chunk_text,
                    bounding_boxes=pending_boxes,
                    token_count=max(1, tokens),
                )
            )
            counter += 1
            pending_text = ""
            pending_boxes = []
            pending_is_heading = False

        def flush_cross_page() -> None:
            nonlocal cross_page_buffer, counter
            if not cross_page_buffer:
                return
            t, boxes, p = cross_page_buffer
            clean_chunk_text = t.rstrip("-").strip()
            tokens = len(clean_chunk_text.split())
            chunks.append(
                DocumentChunk(
                    id=uuid4(),
                    document_id=document_id,
                    chunk_index=counter,
                    page_number=p,
                    content=clean_chunk_text,
                    bounding_boxes=boxes,
                    token_count=max(1, tokens),
                )
            )
            counter += 1
            cross_page_buffer = None

        for bx0, by0, bx1, by1, raw_text, page_num, width, height in all_blocks:
            cleaned = self.DEHYPHEN_REGEX.sub(r"\1\2", raw_text)
            cleaned = re.sub(r"\s+", " ", cleaned).strip()
            if not cleaned:
                continue

            x0_c = max(0.0, min(1.0, round(bx0 / width, 4)))
            y0_c = max(0.0, min(1.0, round(by0 / height, 4)))
            x1_c = max(0.0, min(1.0, round(bx1 / width, 4)))
            y1_c = max(0.0, min(1.0, round(by1 / height, 4)))

            if x1_c <= x0_c or y1_c <= y0_c:
                continue

            bbox = BoundingBox(x0=x0_c, y0=y0_c, x1=x1_c, y1=y1_c, page=page_num)

            is_caption = bool(_CAPTION_PATTERN.match(cleaned))
            is_equation = len(cleaned.split()) <= 35 and (
                any(p.search(cleaned) for p in _EQUATION_PATTERNS)
                or ("=" in cleaned and any(sym in cleaned for sym in _MATH_SYMBOLS))
            )
            is_heading = len(cleaned.split()) <= 7 and (
                cleaned.lower() in ["abstract", "abstract.", "references", "acknowledgements"]
                or cleaned.split()[0].replace(".", "").isdigit()
                or cleaned.isupper()
            )
            is_metadata = bool(
                re.search(r"[\w\.-]+@[\w\.-]+\.\w+", cleaned)
                or "Equal contribution" in cleaned
                or "Work performed while at" in cleaned
            )

            # Move pending text from earlier page to cross_page_buffer if incomplete
            if page_num > pending_page and pending_text:
                if pending_text[-1] not in _SENTENCE_TERMINATORS:
                    cross_page_buffer = (pending_text, pending_boxes, pending_page)
                    pending_text = ""
                    pending_boxes = []
                else:
                    flush_pending()

            # Check if this block continues the cross_page_buffer
            is_cross_cont = (
                cross_page_buffer is not None
                and cleaned[0].islower()
                and not is_caption
                and not is_equation
                and not is_heading
            )
            if is_cross_cont and cross_page_buffer is not None:
                t, boxes, p = cross_page_buffer
                if t.endswith("-"):
                    pending_text = t[:-1] + cleaned
                else:
                    pending_text = t + " " + cleaned
                pending_boxes = boxes + [bbox]
                pending_page = p
                cross_page_buffer = None
                continue

            # 1. Floating Captions and Isolated Equations are self-contained
            if is_caption or is_equation:
                flush_pending()
                chunks.append(
                    DocumentChunk(
                        id=uuid4(),
                        document_id=document_id,
                        chunk_index=counter,
                        page_number=page_num,
                        content=cleaned,
                        bounding_boxes=[bbox],
                        token_count=max(1, len(cleaned.split())),
                    )
                )
                counter += 1
                continue

            # 2. Section Headings: Combine consecutive headings or flush preceding text
            if is_heading:
                if pending_is_heading and page_num == pending_page:
                    pending_text = pending_text + " - " + cleaned
                    pending_boxes.append(bbox)
                    continue
                flush_cross_page()
                flush_pending()
                pending_text = cleaned
                pending_boxes = [bbox]
                pending_page = page_num
                pending_is_heading = True
                continue

            # 3. Regular body prose or metadata grouping within the same page
            can_merge = False
            if pending_text and page_num == pending_page:
                if pending_is_heading:
                    # Heading seamlessly prefixes into the first paragraph of section
                    can_merge = True
                    pending_is_heading = False
                else:
                    prev_ends_hyphen = pending_text.endswith("-")
                    prev_ends_term = pending_text[-1] in _SENTENCE_TERMINATORS
                    prev_is_meta = bool(re.search(r"[\w\.-]+@[\w\.-]+\.\w+", pending_text))

                    if not is_metadata and prev_is_meta:
                        # Never merge body prose into author/email metadata
                        can_merge = False
                    elif is_metadata and prev_is_meta:
                        # Merge consecutive author/affiliation blocks together
                        can_merge = True
                    elif prev_ends_hyphen or not prev_ends_term or cleaned[0].islower():
                        # Seamlessly stitch continuous paragraphs within page
                        tokens_so_far = len(pending_text.split())
                        new_tokens = len(cleaned.split())
                        if tokens_so_far + new_tokens < target_max_tokens:
                            can_merge = True

            if can_merge:
                if pending_text.endswith("-"):
                    pending_text = pending_text[:-1] + cleaned
                else:
                    pending_text = pending_text + " " + cleaned
                pending_boxes.append(bbox)
            else:
                flush_pending()
                pending_text = cleaned
                pending_boxes = [bbox]
                pending_page = page_num

        flush_cross_page()
        flush_pending()
        return chunks
