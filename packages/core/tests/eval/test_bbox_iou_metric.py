"""Unit tests for BoundingBoxIoUMetric in core evaluation domain."""

from __future__ import annotations

from core.domain.value_objects.bounding_box import BoundingBox
from core.eval.metrics.bbox_iou import BoundingBoxIoUMetric, compute_box_iou


def test_compute_box_iou_exact_and_disjoint() -> None:
    # Identical box on same page
    b1 = [0.1, 0.2, 0.5, 0.6, 1.0]
    b2 = [0.1, 0.2, 0.5, 0.6, 1.0]
    assert compute_box_iou(b1, b2) == 1.0

    # Non-overlapping boxes on same page
    b_disjoint = [0.7, 0.7, 0.9, 0.9, 1.0]
    assert compute_box_iou(b1, b_disjoint) == 0.0

    # Identical coordinates but different pages -> IoU = 0.0
    b_diff_page = [0.1, 0.2, 0.5, 0.6, 2.0]
    assert compute_box_iou(b1, b_diff_page) == 0.0


def test_bounding_box_iou_metric_exact_match() -> None:
    metric = BoundingBoxIoUMetric(min_iou=0.70)
    gt_boxes = [[0.1, 0.2, 0.5, 0.6, 1]]
    pred_boxes = [[0.1, 0.2, 0.5, 0.6, 1]]

    res = metric.measure(pred_boxes, gt_boxes)
    assert res.passed is True
    assert res.score == 1.0


def test_bounding_box_iou_metric_with_bounding_box_domain_objects() -> None:
    metric = BoundingBoxIoUMetric(min_iou=0.70)
    gt_box = BoundingBox(x0=0.1, y0=0.2, x1=0.5, y1=0.6, page=1)
    pred_box = BoundingBox(x0=0.11, y0=0.21, x1=0.49, y1=0.59, page=1)

    res = metric.measure([pred_box], [gt_box])
    assert res.passed is True
    assert res.score >= 0.70


def test_bounding_box_iou_metric_page_mismatch_failure() -> None:
    metric = BoundingBoxIoUMetric(min_iou=0.70)
    gt_boxes = [[0.1, 0.2, 0.5, 0.6, 1]]
    pred_boxes = [[0.1, 0.2, 0.5, 0.6, 3]]  # Page 3 vs Page 1

    res = metric.measure(pred_boxes, gt_boxes)
    assert res.passed is False
    assert res.score == 0.0


def test_bounding_box_iou_metric_missing_boxes() -> None:
    metric = BoundingBoxIoUMetric(min_iou=0.70)
    gt_boxes = [[0.1, 0.2, 0.5, 0.6, 1]]

    res = metric.measure([], gt_boxes)
    assert res.passed is False
    assert res.score == 0.0


def test_bounding_box_iou_metric_no_ground_truth_required() -> None:
    metric = BoundingBoxIoUMetric(min_iou=0.70)
    res = metric.measure([[0.1, 0.2, 0.3, 0.4, 1]], [])
    assert res.passed is True
    assert res.score == 1.0
