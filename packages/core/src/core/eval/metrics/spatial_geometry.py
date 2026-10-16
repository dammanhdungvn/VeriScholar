"""Spatial geometry metric auditing bounding box coordinates and architectural invariants."""

from __future__ import annotations

from typing import Any

from core.domain.value_objects.bounding_box import BoundingBox
from core.eval.metrics.base import BaseEvalMetric
from core.eval.metrics.bbox_iou import compute_box_iou
from core.eval.models import MetricResult


class SpatialGeometryMetric(BaseEvalMetric):
    """Audits 2D bounding boxes against geometric invariants:

    x0 < x1, y0 < y1, page >= 1, area < 0.95.
    """

    def __init__(self, min_iou: float = 0.70, max_page_area_ratio: float = 0.95) -> None:
        self.min_iou = min_iou
        self.max_page_area_ratio = max_page_area_ratio

    @property
    def name(self) -> str:
        return "spatial_geometry"

    def measure(self, prediction: Any, ground_truth: Any = None, **kwargs: Any) -> MetricResult:
        """Prediction: chunk/layout dicts containing 'box_2d'/'bbox', boxes, or DocumentChunks."""
        boxes: list[dict[str, Any]] = []

        if isinstance(prediction, list):
            for idx, item in enumerate(prediction):
                if isinstance(item, BoundingBox):
                    boxes.append(
                        {
                            "index": idx,
                            "page": item.page,
                            "bbox": [item.x0, item.y0, item.x1, item.y1, float(item.page)],
                        }
                    )
                elif isinstance(item, dict):
                    bbox = item.get("box_2d") or item.get("bounding_box") or item.get("bbox")
                    if bbox:
                        page = item.get("page") or (bbox[4] if len(bbox) > 4 else 1)
                        boxes.append({"index": item.get("index", idx), "page": page, "bbox": bbox})
                elif isinstance(item, (list, tuple)) and len(item) >= 4:
                    page = item[4] if len(item) > 4 else 1
                    boxes.append({"index": idx, "page": page, "bbox": list(item)})

        if not boxes:
            if ground_truth and isinstance(ground_truth, list) and len(ground_truth) > 0:
                return MetricResult(
                    name=self.name,
                    score=0.0,
                    threshold=self.min_iou,
                    passed=False,
                    details={"total_boxes": 0, "ground_truth_count": len(ground_truth)},
                    reasoning=(
                        "No spatial bounding boxes in payload when ground truth expects boxes."
                    ),
                )
            return MetricResult(
                name=self.name,
                score=1.0,
                threshold=self.min_iou,
                passed=True,
                details={"total_boxes": 0},
                reasoning="No spatial bounding boxes in payload to evaluate.",
            )

        anomalies: list[dict[str, Any]] = []

        for b in boxes:
            idx = b["index"]
            bbox = b["bbox"]

            if not isinstance(bbox, (list, tuple)) or len(bbox) < 4:
                anomalies.append(
                    {
                        "index": idx,
                        "error": "MALFORMED_BBOX",
                        "bbox": bbox,
                        "detail": "Bounding box must be a list/tuple of at least 4 numbers.",
                    }
                )
                continue

            x0, y0, x1, y1 = [float(c) for c in bbox[:4]]

            # 1. Coordinate normalization bounds check [0.0, 1.0]
            if any(coord < 0.0 for coord in (x0, y0, x1, y1)):
                anomalies.append(
                    {
                        "index": idx,
                        "error": "NEGATIVE_COORDINATE",
                        "bbox": [x0, y0, x1, y1],
                        "detail": "Coordinates must be non-negative.",
                    }
                )

            if any(coord > 1.0 for coord in (x0, y0, x1, y1)):
                anomalies.append(
                    {
                        "index": idx,
                        "error": "UNNORMALIZED_COORDINATES",
                        "bbox": [x0, y0, x1, y1],
                        "detail": "Coordinates must be normalized floats in range [0.0, 1.0].",
                    }
                )

            # 2. Strict Ordering check (x1 > x0, y1 > y0)
            if x1 <= x0 or y1 <= y0:
                detail_msg = f"Inverted box: x1({x1}) <= x0({x0}) or y1({y1}) <= y0({y0})."
                anomalies.append(
                    {
                        "index": idx,
                        "error": "INVERTED_COORDINATES",
                        "bbox": [x0, y0, x1, y1],
                        "detail": detail_msg,
                    }
                )

            # 3. 1-indexed page check
            page = int(bbox[4]) if len(bbox) > 4 else int(b.get("page", 1))
            if page < 1:
                anomalies.append(
                    {
                        "index": idx,
                        "error": "INVALID_PAGE_INDEX",
                        "bbox": [x0, y0, x1, y1, page],
                        "detail": f"Page index must be strictly >= 1, got {page}.",
                    }
                )

            # 4. Anti-lazy full-page box detection (box covers > 95% of page area)
            if all(0.0 <= c <= 1.0 for c in (x0, y0, x1, y1)):
                area = (x1 - x0) * (y1 - y0)
                if area > self.max_page_area_ratio:
                    anomalies.append(
                        {
                            "index": idx,
                            "error": "LAZY_FULL_PAGE_BOX",
                            "bbox": [x0, y0, x1, y1],
                            "detail": f"Box covers {area:.1%} of page; suspected lazy fallback.",
                        }
                    )

        # 5. Optional IoU verification against ground truth if provided
        iou_scores: list[float] = []
        if ground_truth and isinstance(ground_truth, list):
            gt_boxes: list[list[float]] = []
            for item in ground_truth:
                if isinstance(item, (list, tuple)) and len(item) >= 4:
                    gt_boxes.append([float(c) for c in item])
                elif isinstance(item, dict):
                    raw = item.get("box_2d") or item.get("bbox")
                    if raw and len(raw) >= 4:
                        gt_boxes.append([float(c) for c in raw])

            for b in boxes:
                pred_b = [float(c) for c in b["bbox"][:4]]
                if len(b["bbox"]) > 4:
                    pred_b.append(float(b["bbox"][4]))

                best_iou = 0.0
                for gt_b in gt_boxes:
                    iou = compute_box_iou(pred_b, gt_b)
                    if iou > best_iou:
                        best_iou = iou

                iou_scores.append(best_iou)

        avg_iou = (sum(iou_scores) / len(iou_scores)) if iou_scores else 1.0
        passed = len(anomalies) == 0 and avg_iou >= self.min_iou

        if iou_scores and len(anomalies) == 0:
            score = avg_iou
        elif not anomalies:
            score = 1.0
        else:
            score = max(0.0, 1.0 - (len(anomalies) * 0.2))

        return MetricResult(
            name=self.name,
            score=round(score, 4),
            threshold=self.min_iou,
            passed=passed,
            details={
                "total_boxes": len(boxes),
                "avg_iou": round(avg_iou, 4) if iou_scores else None,
                "anomalies_count": len(anomalies),
            },
            error_samples=anomalies[:5],
            reasoning=(
                f"Spatial geometry verified ({len(boxes)} boxes, 0 anomalies)."
                if passed
                else f"Detected {len(anomalies)} geometry anomalies."
            ),
        )
