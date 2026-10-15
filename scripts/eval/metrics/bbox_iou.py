"""Bounding Box IoU metric for evaluation harness."""

from __future__ import annotations

from typing import Any

from scripts.eval.metrics.base import BaseEvalMetric, MetricResult


def _compute_single_iou(b1: list[float], b2: list[float]) -> float:
    """Computes IoU of two normalized 2D boxes [x0, y0, x1, y1]."""
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
    """Calculates Spatial BoundingBox Intersection-over-Union (IoU) against ground truth coordinates."""

    def __init__(self, min_iou: float = 0.70):
        self.min_iou = min_iou

    @property
    def name(self) -> str:
        return "bounding_box_iou"

    def measure(self, prediction: Any, ground_truth: Any = None, **kwargs: Any) -> MetricResult:
        """Measure average BoundingBox IoU.

        prediction: list of predicted bounding boxes [[x0, y0, x1, y1, page], ...] or dicts with 'bbox'.
        ground_truth: list of ground truth bounding boxes [[x0, y0, x1, y1, page], ...] or dicts with 'bbox'.
        """
        pred_boxes: list[list[float]] = []
        if isinstance(prediction, list):
            for item in prediction:
                if isinstance(item, (list, tuple)) and len(item) >= 4:
                    pred_boxes.append([float(c) for c in item])
                elif isinstance(item, dict):
                    raw = item.get("bbox") or item.get("box_2d") or item.get("bounding_box")
                    if isinstance(raw, (list, tuple)) and len(raw) >= 4:
                        pred_boxes.append([float(c) for c in raw])

        gt_boxes: list[list[float]] = []
        if isinstance(ground_truth, list):
            for item in ground_truth:
                if isinstance(item, (list, tuple)) and len(item) >= 4:
                    gt_boxes.append([float(c) for c in item])
                elif isinstance(item, dict):
                    raw = item.get("bbox") or item.get("box_2d") or item.get("bounding_box")
                    if isinstance(raw, (list, tuple)) and len(raw) >= 4:
                        gt_boxes.append([float(c) for c in raw])

        # If no spatial bounding boxes are required
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
                reasoning=f"Missing required spatial bounding boxes: expected {len(gt_boxes)}, got 0.",
            )

        iou_scores: list[float] = []
        matched_pairs: list[dict[str, Any]] = []

        # Match each ground truth box to the best overlapping predicted box (respecting page if available)
        for gt in gt_boxes:
            gt_page = int(gt[4]) if len(gt) > 4 else None
            best_iou = 0.0
            best_pred = None

            for pred in pred_boxes:
                pred_page = int(pred[4]) if len(pred) > 4 else None
                if gt_page is not None and pred_page is not None and gt_page != pred_page:
                    continue  # Page mismatch

                iou = _compute_single_iou(pred[:4], gt[:4])
                if iou > best_iou:
                    best_iou = iou
                    best_pred = pred

            iou_scores.append(best_iou)
            matched_pairs.append(
                {
                    "gt": gt,
                    "best_pred": best_pred,
                    "iou": round(best_iou, 3),
                }
            )

        mean_iou = sum(iou_scores) / len(iou_scores) if iou_scores else 0.0
        passed = mean_iou >= self.min_iou

        return MetricResult(
            name=self.name,
            score=round(mean_iou, 3),
            threshold=self.min_iou,
            passed=passed,
            details={
                "mean_iou": round(mean_iou, 3),
                "matched_count": len(iou_scores),
                "pairs": matched_pairs,
            },
            reasoning=f"Spatial IoU {mean_iou:.3f} (target threshold: {self.min_iou:.2f}).",
        )
