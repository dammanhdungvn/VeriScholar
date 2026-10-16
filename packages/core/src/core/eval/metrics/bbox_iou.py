"""Spatial BoundingBox IoU evaluation metric.

Enforces strictly normalized [x0, y0, x1, y1, page] coordinates with Top-Left origin (0, 0),
1-indexed pages (page >= 1), and calculates 2D Intersection-over-Union.
"""

from __future__ import annotations

from typing import Any

from core.domain.value_objects.bounding_box import BoundingBox
from core.eval.metrics.base import BaseEvalMetric
from core.eval.models import MetricResult


def _to_bbox_coords(box: Any) -> list[float] | None:
    """Normalize box representation to [x0, y0, x1, y1, page]."""
    if isinstance(box, BoundingBox):
        return [box.x0, box.y0, box.x1, box.y1, float(box.page)]
    if isinstance(box, (list, tuple)) and len(box) >= 4:
        coords = [float(c) for c in box[:4]]
        page = float(box[4]) if len(box) > 4 else 1.0
        return [*coords, page]
    if isinstance(box, dict):
        raw = box.get("bbox") or box.get("box_2d") or box.get("bounding_box")
        if isinstance(raw, (list, tuple)) and len(raw) >= 4:
            coords = [float(c) for c in raw[:4]]
            page = float(box.get("page") or (raw[4] if len(raw) > 4 else 1))
            return [*coords, page]
    return None


def compute_box_iou(b1: list[float], b2: list[float]) -> float:
    """Computes spatial IoU of two normalized boxes [x0, y0, x1, y1, page].

    Returns 0.0 if pages do not match.
    """
    if len(b1) > 4 and len(b2) > 4:
        if int(b1[4]) != int(b2[4]):
            return 0.0

    x0 = max(b1[0], b2[0])
    y0 = max(b1[1], b2[1])
    x1 = min(b1[2], b2[2])
    y1 = min(b1[3], b2[3])

    if x1 <= x0 or y1 <= y0:
        return 0.0

    inter_area = (x1 - x0) * (y1 - y0)
    area1 = max(0.0, (b1[2] - b1[0]) * (b1[3] - b1[1]))
    area2 = max(0.0, (b2[2] - b2[0]) * (b2[3] - b2[1]))
    union_area = area1 + area2 - inter_area

    return inter_area / union_area if union_area > 0 else 0.0


class BoundingBoxIoUMetric(BaseEvalMetric):
    """Calculates Spatial BoundingBox IoU against ground truth coordinates."""

    def __init__(self, min_iou: float = 0.70) -> None:
        self.min_iou = min_iou

    @property
    def name(self) -> str:
        return "bounding_box_iou"

    def measure(self, prediction: Any, ground_truth: Any = None, **kwargs: Any) -> MetricResult:
        """Measure average BoundingBox IoU.

        prediction: list of predicted bounding boxes [[x0, y0, x1, y1, page], ...],
                    list of BoundingBox objects, or list of dicts with 'bbox'.
        ground_truth: list of ground truth bounding boxes or BoundingBox objects.
        """
        pred_boxes: list[list[float]] = []
        if isinstance(prediction, list):
            for item in prediction:
                coords = _to_bbox_coords(item)
                if coords:
                    pred_boxes.append(coords)
        elif prediction is not None:
            coords = _to_bbox_coords(prediction)
            if coords:
                pred_boxes.append(coords)

        gt_boxes: list[list[float]] = []
        if isinstance(ground_truth, list):
            for item in ground_truth:
                coords = _to_bbox_coords(item)
                if coords:
                    gt_boxes.append(coords)
        elif ground_truth is not None:
            coords = _to_bbox_coords(ground_truth)
            if coords:
                gt_boxes.append(coords)

        # If no spatial bounding boxes required
        if not gt_boxes:
            return MetricResult(
                name=self.name,
                score=1.0,
                threshold=self.min_iou,
                passed=True,
                details={"gt_boxes_count": 0, "pred_boxes_count": len(pred_boxes)},
                reasoning="No spatial bounding boxes required for this test case.",
            )

        if not pred_boxes:
            return MetricResult(
                name=self.name,
                score=0.0,
                threshold=self.min_iou,
                passed=False,
                details={"gt_boxes_count": len(gt_boxes), "pred_boxes_count": 0},
                reasoning=(
                    f"Missing required spatial bounding boxes: expected {len(gt_boxes)}, got 0."
                ),
            )

        iou_scores: list[float] = []
        matched_pairs: list[dict[str, Any]] = []

        for gt in gt_boxes:
            best_iou = 0.0
            best_pred = None

            for pred in pred_boxes:
                iou = compute_box_iou(pred, gt)
                if iou > best_iou:
                    best_iou = iou
                    best_pred = pred

            iou_scores.append(best_iou)
            matched_pairs.append(
                {
                    "gt": gt,
                    "best_pred": best_pred,
                    "iou": round(best_iou, 4),
                }
            )

        mean_iou = sum(iou_scores) / len(iou_scores) if iou_scores else 0.0
        passed = mean_iou >= self.min_iou

        return MetricResult(
            name=self.name,
            score=round(mean_iou, 4),
            threshold=self.min_iou,
            passed=passed,
            details={
                "mean_iou": round(mean_iou, 4),
                "matched_count": len(iou_scores),
                "pairs": matched_pairs,
            },
            reasoning=f"Spatial IoU {mean_iou:.3f} (target threshold: {self.min_iou:.2f}).",
        )
