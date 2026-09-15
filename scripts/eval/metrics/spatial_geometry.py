"""Spatial geometry and bounding box coordinate metric."""

from typing import Any

from scripts.eval.metrics.base import BaseEvalMetric, MetricResult


class SpatialGeometryMetric(BaseEvalMetric):
    """Audits 2D bounding boxes against geometric invariants and calculates IoU."""

    def __init__(self, min_iou: float = 0.70, max_page_area_ratio: float = 0.95):
        self.min_iou = min_iou
        self.max_page_area_ratio = max_page_area_ratio

    @property
    def name(self) -> str:
        return "spatial_geometry"

    def measure(self, prediction: Any, ground_truth: Any = None, **kwargs: Any) -> MetricResult:
        """Prediction: list of chunk/layout dicts containing 'page' and 'box_2d'.

        kwargs: page_dimensions (optional list of dicts with width, height).
        """
        boxes: list[dict[str, Any]] = []
        if isinstance(prediction, list):
            for item in prediction:
                if isinstance(item, dict):
                    bbox = item.get("box_2d") or item.get("bounding_box") or item.get("bbox")
                    if bbox:
                        boxes.append(
                            {
                                "index": item.get("index", 0),
                                "page": item.get("page", 1),
                                "bbox": bbox,
                            }
                        )

        if not boxes:
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

            x0, y0, x1, y1 = bbox[:4]

            # 1. Non-negativity check
            if any(coord < 0.0 for coord in (x0, y0, x1, y1)):
                anomalies.append(
                    {
                        "index": idx,
                        "error": "NEGATIVE_COORDINATE",
                        "bbox": [x0, y0, x1, y1],
                        "detail": "Coordinates must be non-negative.",
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

            # 3. Full-page lazy fallback detection (normalized box covers > 95% of page)
            if all(0.0 <= c <= 1.05 for c in (x0, y0, x1, y1)):
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

        # 4. Calculate spatial IoU against ground truth if provided
        iou_scores: list[float] = []
        if ground_truth and isinstance(ground_truth, list):
            gt_map = {}
            for index, item in enumerate(ground_truth):
                if isinstance(item, dict):
                    gt_box = item.get("box_2d") or item.get("bbox")
                    if gt_box:
                        gt_map[index] = gt_box

            for b in boxes:
                idx = b["index"]
                if idx in gt_map:
                    px0, py0, px1, py1 = b["bbox"][:4]
                    gx0, gy0, gx1, gy1 = gt_map[idx][:4]

                    ix0 = max(px0, gx0)
                    iy0 = max(py0, gy0)
                    ix1 = min(px1, gx1)
                    iy1 = min(py1, gy1)

                    if ix1 > ix0 and iy1 > iy0:
                        inter_area = (ix1 - ix0) * (iy1 - iy0)
                        p_area = (px1 - px0) * (py1 - py0)
                        g_area = (gx1 - gx0) * (gy1 - gy0)
                        union_area = p_area + g_area - inter_area
                        iou = inter_area / union_area if union_area > 0 else 0.0
                    else:
                        iou = 0.0

                    iou_scores.append(iou)
                    if iou < self.min_iou:
                        anomalies.append(
                            {
                                "index": idx,
                                "error": "LOW_SPATIAL_IOU",
                                "iou": round(iou, 3),
                                "detail": f"IoU {iou:.2f} < threshold {self.min_iou}.",
                            }
                        )

        avg_iou = (sum(iou_scores) / len(iou_scores)) if iou_scores else 1.0
        passed = len(anomalies) == 0 and avg_iou >= self.min_iou

        if iou_scores:
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
