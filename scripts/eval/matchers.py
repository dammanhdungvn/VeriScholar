"""Evaluation matchers and metrics: Token Jaccard, Spatial IoU, Cascading Matcher."""

import re
from typing import Any


def token_jaccard_similarity(title_a: str, title_b: str) -> float:
    """Calculate Token-based Jaccard similarity between two titles.

    Applies whitespace and alphanumeric extraction, lowercasing, and set intersection/union.
    """
    tokens_a = set(re.findall(r"\w+", title_a.lower()))
    tokens_b = set(re.findall(r"\w+", title_b.lower()))
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a.intersection(tokens_b)) / len(tokens_a.union(tokens_b))


def calculate_bbox_iou(bbox_pred: list[float], bbox_gt: list[float]) -> float:
    """Calculate Intersection over Union (IoU) between two bounding boxes.

    Coordinates format: [x0, y0, x1, y1] normalized in [0.0, 1.0].
    """
    if len(bbox_pred) < 4 or len(bbox_gt) < 4:
        return 0.0

    x0 = max(bbox_pred[0], bbox_gt[0])
    y0 = max(bbox_pred[1], bbox_gt[1])
    x1 = min(bbox_pred[2], bbox_gt[2])
    y1 = min(bbox_pred[3], bbox_gt[3])

    intersection = max(0.0, x1 - x0) * max(0.0, y1 - y0)
    area_pred = max(0.0, bbox_pred[2] - bbox_pred[0]) * max(0.0, bbox_pred[3] - bbox_pred[1])
    area_gt = max(0.0, bbox_gt[2] - bbox_gt[0]) * max(0.0, bbox_gt[3] - bbox_gt[1])
    union = area_pred + area_gt - intersection

    return intersection / union if union > 0 else 0.0


def is_reference_match(extracted: dict[str, Any], expected: dict[str, Any]) -> tuple[bool, str]:
    """Cascading Matcher:

    1. Tầng 1: Khớp định danh duy nhất (DOI / arXiv ID).
    2. Tầng 2: Khớp tiêu đề mờ theo Token Jaccard (>= 0.85) + Năm xuất bản.

    Returns:
        (is_matched, match_type)
    """
    # 1. Khớp DOI
    ext_doi = extracted.get("doi")
    exp_doi = expected.get("doi")
    if ext_doi and exp_doi:
        if ext_doi.strip().lower() == exp_doi.strip().lower():
            return True, "doi_exact"

    # 2. Khớp arXiv ID
    ext_arxiv = extracted.get("arxiv_id")
    exp_arxiv = expected.get("arxiv_id")
    if ext_arxiv and exp_arxiv:
        if ext_arxiv.strip().lower() == exp_arxiv.strip().lower():
            return True, "arxiv_exact"

    # 3. Khớp Token Jaccard tiêu đề
    title_ext = extracted.get("title", "")
    title_exp = expected.get("title", "")
    sim = token_jaccard_similarity(title_ext, title_exp)

    if sim >= 0.85:
        # Kiểm tra nhãn phiên bản nếu có
        for tag in ["part 1", "part 2", "part i", "part ii", "v1", "v2"]:
            if (tag in title_ext.lower()) != (tag in title_exp.lower()):
                return False, "version_mismatch"

        # Nếu cả 2 đều có năm xuất bản, kiểm tra trùng năm
        ext_year = extracted.get("year")
        exp_year = expected.get("year")
        if ext_year and exp_year:
            if ext_year == exp_year:
                return True, f"title_jaccard_{sim:.2f}_year_exact"
            return False, "year_mismatch"

        return True, f"title_jaccard_{sim:.2f}"

    return False, "unmatched"
