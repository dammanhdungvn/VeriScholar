"""Domain evaluation metrics and algorithms for chunking quality audit.

Calculates Linguistic Boundary Integrity (LBI), Dehyphenation Error Rate,
Multi-Column Reading Flow Integrity, Spatial Bounding Box Validity,
and Token Size Distribution metrics without external ML dependencies.
"""

import math
import re
from dataclasses import dataclass
from typing import Any

from core.domain.entities.chunk import DocumentChunk

_VALID_TERMINATORS = {".", "!", "?", ":", '"', "”", ")", "]", ";"}
_TRAILING_HYPHEN_REGEX = re.compile(r"[a-zA-Z]{2,}-$")


@dataclass(frozen=True)
class ChunkAnomaly:
    """Represents a flagged chunk-level defect or anomaly."""

    chunk_index: int
    page_number: int
    issue_type: str  # 'PUNCTUATION_CUT', 'DEHYPHENATION_ERROR', 'MICRO_CHUNK', 'BLOATED_CHUNK', 'INVALID_COORDINATES'
    severity: str  # 'LOW', 'MEDIUM', 'HIGH'
    description: str
    content_snippet: str
    token_count: int


@dataclass(frozen=True)
class PaperChunkMetrics:
    """Comprehensive evaluation metrics for a single document's chunks."""

    paper_name: str
    total_pages: int
    total_chunks: int
    total_tokens: int

    # Token Distribution
    min_tokens: int
    max_tokens: int
    mean_tokens: float
    median_tokens: float
    p90_tokens: float
    p99_tokens: float
    std_dev_tokens: float

    # SLA Rates (Percentages 0.0 -> 100.0)
    boundary_integrity_ratio: float  # Target >= 95.0%
    dehyphenation_error_rate: float  # Target == 0.0%
    micro_chunk_rate: float  # Target <= 5.0% (<25 tokens)
    bloated_chunk_rate: float  # Target <= 2.0% (>800 tokens)
    spatial_validity_ratio: float  # Target == 100.0%
    column_flow_integrity: float  # Target >= 95.0%

    # Performance
    elapsed_time_ms: float
    ms_per_page: float

    # Composite Score (0.0 -> 100.0)
    composite_score: float
    anomalies: list[ChunkAnomaly]

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to serializable dictionary."""
        return {
            "paper_name": self.paper_name,
            "total_pages": self.total_pages,
            "total_chunks": self.total_chunks,
            "total_tokens": self.total_tokens,
            "token_distribution": {
                "min": self.min_tokens,
                "max": self.max_tokens,
                "mean": round(self.mean_tokens, 2),
                "median": round(self.median_tokens, 2),
                "p90": round(self.p90_tokens, 2),
                "p99": round(self.p99_tokens, 2),
                "std_dev": round(self.std_dev_tokens, 2),
            },
            "sla_rates": {
                "boundary_integrity_ratio": round(self.boundary_integrity_ratio, 2),
                "dehyphenation_error_rate": round(self.dehyphenation_error_rate, 2),
                "micro_chunk_rate": round(self.micro_chunk_rate, 2),
                "bloated_chunk_rate": round(self.bloated_chunk_rate, 2),
                "spatial_validity_ratio": round(self.spatial_validity_ratio, 2),
                "column_flow_integrity": round(self.column_flow_integrity, 2),
            },
            "performance": {
                "elapsed_time_ms": round(self.elapsed_time_ms, 2),
                "ms_per_page": round(self.ms_per_page, 2),
            },
            "composite_score": round(self.composite_score, 1),
            "anomalies_count": len(self.anomalies),
        }


def calculate_token_statistics(
    chunks: list[DocumentChunk],
) -> tuple[int, int, float, float, float, float, float]:
    """Calculate min, max, mean, median, p90, p99, and standard deviation of token counts."""
    if not chunks:
        return 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0

    counts = sorted(c.token_count for c in chunks)
    n = len(counts)
    min_c = counts[0]
    max_c = counts[-1]
    mean_c = sum(counts) / n

    if n % 2 == 1:
        median_c = float(counts[n // 2])
    else:
        median_c = (counts[n // 2 - 1] + counts[n // 2]) / 2.0

    p90_idx = min(n - 1, math.ceil(0.90 * n) - 1)
    p99_idx = min(n - 1, math.ceil(0.99 * n) - 1)
    p90_c = float(counts[p90_idx])
    p99_c = float(counts[p99_idx])

    variance = sum((x - mean_c) ** 2 for x in counts) / n
    std_dev = math.sqrt(variance)

    return min_c, max_c, mean_c, median_c, p90_c, p99_c, std_dev


def evaluate_chunks(
    paper_name: str,
    chunks: list[DocumentChunk],
    total_pages: int,
    elapsed_time_ms: float,
) -> PaperChunkMetrics:
    """Evaluate a list of extracted chunks and return comprehensive PaperChunkMetrics."""
    total_chunks = len(chunks)
    if total_chunks == 0:
        return PaperChunkMetrics(
            paper_name=paper_name,
            total_pages=total_pages,
            total_chunks=0,
            total_tokens=0,
            min_tokens=0,
            max_tokens=0,
            mean_tokens=0.0,
            median_tokens=0.0,
            p90_tokens=0.0,
            p99_tokens=0.0,
            std_dev_tokens=0.0,
            boundary_integrity_ratio=0.0,
            dehyphenation_error_rate=0.0,
            micro_chunk_rate=0.0,
            bloated_chunk_rate=0.0,
            spatial_validity_ratio=0.0,
            column_flow_integrity=0.0,
            elapsed_time_ms=elapsed_time_ms,
            ms_per_page=0.0,
            composite_score=0.0,
            anomalies=[],
        )

    anomalies: list[ChunkAnomaly] = []
    valid_boundary_count = 0
    dehyphenation_error_count = 0
    micro_chunk_count = 0
    bloated_chunk_count = 0
    valid_spatial_count = 0
    total_bboxes = 0

    for chunk in chunks:
        text = chunk.content.strip()
        tokens = chunk.token_count

        # 1. Linguistic Boundary Integrity
        if text and text[-1] in _VALID_TERMINATORS:
            valid_boundary_count += 1
        else:
            # Check if it is a heading, formula, or table row
            words = text.split()
            is_heading = len(words) <= 8 and (
                text[0].isdigit()
                or text.isupper()
                or text.istitle()
                or "Table" in text
                or "Figure" in text
            )
            is_formula = "=" in text or "+" in text or "/" in text or "^" in text
            if is_heading or is_formula:
                valid_boundary_count += 1
            else:
                anomalies.append(
                    ChunkAnomaly(
                        chunk_index=chunk.chunk_index,
                        page_number=chunk.page_number,
                        issue_type="PUNCTUATION_CUT",
                        severity="MEDIUM",
                        description=f"Chunk does not end with sentence terminator (ends with '{text[-1] if text else ''}')",
                        content_snippet=text[-60:] if len(text) > 60 else text,
                        token_count=tokens,
                    )
                )

        # 2. Dehyphenation Check
        if _TRAILING_HYPHEN_REGEX.search(text):
            dehyphenation_error_count += 1
            anomalies.append(
                ChunkAnomaly(
                    chunk_index=chunk.chunk_index,
                    page_number=chunk.page_number,
                    issue_type="DEHYPHENATION_ERROR",
                    severity="HIGH",
                    description="Chunk ends with broken hyphenated word",
                    content_snippet=text[-40:] if len(text) > 40 else text,
                    token_count=tokens,
                )
            )

        # 3. Micro and Bloated Chunks
        if tokens < 25:
            if len(text.split()) < 6:
                micro_chunk_count += 1
                anomalies.append(
                    ChunkAnomaly(
                        chunk_index=chunk.chunk_index,
                        page_number=chunk.page_number,
                        issue_type="MICRO_CHUNK",
                        severity="LOW",
                        description=f"Micro-chunk with only {tokens} tokens",
                        content_snippet=text[:50],
                        token_count=tokens,
                    )
                )
        elif tokens > 800:
            bloated_chunk_count += 1
            anomalies.append(
                ChunkAnomaly(
                    chunk_index=chunk.chunk_index,
                    page_number=chunk.page_number,
                    issue_type="BLOATED_CHUNK",
                    severity="MEDIUM",
                    description=f"Bloated chunk with {tokens} tokens",
                    content_snippet=text[:50] + "...",
                    token_count=tokens,
                )
            )

        # 4. Spatial Coordinate Validity
        for bbox in chunk.bounding_boxes:
            total_bboxes += 1
            if (
                0.0 <= bbox.x0 < bbox.x1 <= 1.0
                and 0.0 <= bbox.y0 < bbox.y1 <= 1.0
                and bbox.page >= 1
            ):
                valid_spatial_count += 1
            else:
                anomalies.append(
                    ChunkAnomaly(
                        chunk_index=chunk.chunk_index,
                        page_number=chunk.page_number,
                        issue_type="INVALID_COORDINATES",
                        severity="HIGH",
                        description=f"Coordinates out of bounds: [{bbox.x0}, {bbox.y0}, {bbox.x1}, {bbox.y1}]",
                        content_snippet=text[:40],
                        token_count=tokens,
                    )
                )

    # 5. Multi-Column Reading Flow Integrity (evaluated only on multi-column pages)
    column_transitions_valid = 0
    total_transitions = 0
    page_chunks_map: dict[int, list[DocumentChunk]] = {}
    for c in chunks:
        page_chunks_map.setdefault(c.page_number, []).append(c)

    for _, p_chunks in page_chunks_map.items():
        if len(p_chunks) < 2:
            continue

        # Check if page is genuinely multi-column (has substantial content in both columns)
        left_sub_count = sum(
            1
            for c in p_chunks
            if c.token_count >= 15
            and c.bounding_boxes
            and (c.bounding_boxes[0].x1 - c.bounding_boxes[0].x0) <= 0.48
            and c.bounding_boxes[0].x1 <= 0.52
        )
        right_sub_count = sum(
            1
            for c in p_chunks
            if c.token_count >= 15
            and c.bounding_boxes
            and (c.bounding_boxes[0].x1 - c.bounding_boxes[0].x0) <= 0.48
            and c.bounding_boxes[0].x0 >= 0.48
        )

        if left_sub_count < 1 or right_sub_count < 1:
            # Single-column page layout
            continue

        last_col: str | None = None
        for c in p_chunks:
            if not c.bounding_boxes or c.token_count < 8:
                continue
            bx0 = c.bounding_boxes[0].x0
            bx1 = c.bounding_boxes[0].x1
            b_width = bx1 - bx0

            # Only classify as column if block is narrow (less than 50% width)
            if b_width <= 0.48:
                if bx1 <= 0.52:
                    cur_col = "LEFT"
                elif bx0 >= 0.48:
                    cur_col = "RIGHT"
                else:
                    cur_col = "SPAN"
            else:
                cur_col = "SPAN"

            if last_col and last_col != "SPAN" and cur_col != "SPAN":
                total_transitions += 1
                if last_col == "RIGHT" and cur_col == "LEFT":
                    # Zig-zag detected
                    pass
                else:
                    column_transitions_valid += 1
            last_col = cur_col

    if total_transitions > 0:
        column_flow_ratio = (column_transitions_valid / total_transitions) * 100.0
    else:
        column_flow_ratio = 100.0

    # Rates
    boundary_integrity_ratio = (valid_boundary_count / total_chunks) * 100.0
    dehyphenation_error_rate = (dehyphenation_error_count / total_chunks) * 100.0
    micro_chunk_rate = (micro_chunk_count / total_chunks) * 100.0
    bloated_chunk_rate = (bloated_chunk_count / total_chunks) * 100.0
    spatial_validity_ratio = (
        (valid_spatial_count / total_bboxes * 100.0) if total_bboxes > 0 else 100.0
    )

    # Statistics
    min_t, max_t, mean_t, med_t, p90_t, p99_t, std_t = calculate_token_statistics(chunks)
    ms_per_p = elapsed_time_ms / total_pages if total_pages > 0 else 0.0

    # Composite Quality Score (0 to 100)
    score = (
        0.35 * boundary_integrity_ratio
        + 0.20 * (100.0 - dehyphenation_error_rate)
        + 0.20 * column_flow_ratio
        + 0.15 * spatial_validity_ratio
        + 0.10 * (100.0 - micro_chunk_rate)
    )

    return PaperChunkMetrics(
        paper_name=paper_name,
        total_pages=total_pages,
        total_chunks=total_chunks,
        total_tokens=sum(c.token_count for c in chunks),
        min_tokens=min_t,
        max_tokens=max_t,
        mean_tokens=mean_t,
        median_tokens=med_t,
        p90_tokens=p90_t,
        p99_tokens=p99_t,
        std_dev_tokens=std_t,
        boundary_integrity_ratio=boundary_integrity_ratio,
        dehyphenation_error_rate=dehyphenation_error_rate,
        micro_chunk_rate=micro_chunk_rate,
        bloated_chunk_rate=bloated_chunk_rate,
        spatial_validity_ratio=spatial_validity_ratio,
        column_flow_integrity=column_flow_ratio,
        elapsed_time_ms=elapsed_time_ms,
        ms_per_page=ms_per_p,
        composite_score=score,
        anomalies=anomalies,
    )
