"""Unit tests for SpatialGeometryMetric in core evaluation domain."""

from __future__ import annotations

from core.domain.value_objects.bounding_box import BoundingBox
from core.eval.metrics.spatial_geometry import SpatialGeometryMetric


def test_spatial_geometry_metric_valid_boxes() -> None:
    metric = SpatialGeometryMetric()
    valid_boxes = [
        {"bbox": [0.1, 0.1, 0.5, 0.4, 1]},
        {"bbox": [0.2, 0.5, 0.8, 0.9, 2]},
    ]
    res = metric.measure(valid_boxes)
    assert res.passed is True
    assert res.score == 1.0
    assert res.details["anomalies_count"] == 0


def test_spatial_geometry_metric_with_domain_objects() -> None:
    metric = SpatialGeometryMetric()
    boxes = [
        BoundingBox(x0=0.08, y0=0.25, x1=0.48, y1=0.55, page=3),
    ]
    res = metric.measure(boxes)
    assert res.passed is True
    assert res.score == 1.0


def test_spatial_geometry_metric_inverted_coordinates() -> None:
    metric = SpatialGeometryMetric()
    inverted = [{"bbox": [0.6, 0.5, 0.2, 0.4, 1]}]  # x0 > x1 and y0 > y1

    res = metric.measure(inverted)
    assert res.passed is False
    assert any(err["error"] == "INVERTED_COORDINATES" for err in res.error_samples)


def test_spatial_geometry_metric_negative_coordinates() -> None:
    metric = SpatialGeometryMetric()
    neg = [{"bbox": [-0.1, 0.1, 0.5, 0.5, 1]}]

    res = metric.measure(neg)
    assert res.passed is False
    assert any(err["error"] == "NEGATIVE_COORDINATE" for err in res.error_samples)


def test_spatial_geometry_metric_invalid_page() -> None:
    metric = SpatialGeometryMetric()
    bad_page = [{"bbox": [0.1, 0.1, 0.5, 0.5, 0]}]  # page 0 is invalid

    res = metric.measure(bad_page)
    assert res.passed is False
    assert any(err["error"] == "INVALID_PAGE_INDEX" for err in res.error_samples)


def test_spatial_geometry_metric_lazy_full_page_detection() -> None:
    metric = SpatialGeometryMetric(max_page_area_ratio=0.95)
    lazy_box = [{"bbox": [0.01, 0.01, 0.99, 0.99, 1]}]  # area ~ 0.96 > 0.95

    res = metric.measure(lazy_box)
    assert res.passed is False
    assert any(err["error"] == "LAZY_FULL_PAGE_BOX" for err in res.error_samples)


def test_spatial_geometry_metric_empty_payload() -> None:
    metric = SpatialGeometryMetric()
    res = metric.measure([])
    assert res.passed is True
    assert res.score == 1.0


def test_spatial_geometry_metric_unnormalized_pixel_coordinates_rejected() -> None:
    metric = SpatialGeometryMetric()
    unnormalized = [{"bbox": [50.0, 100.0, 400.0, 700.0, 1]}]
    res = metric.measure(unnormalized)

    assert res.passed is False
    assert res.score < 1.0
    assert any(err["error"] == "UNNORMALIZED_COORDINATES" for err in res.error_samples)


def test_spatial_geometry_metric_missing_boxes_with_ground_truth_fails() -> None:
    metric = SpatialGeometryMetric()
    gt_boxes = [[0.1, 0.2, 0.5, 0.6, 1]]
    res = metric.measure(prediction=[], ground_truth=gt_boxes)

    assert res.passed is False
    assert res.score == 0.0
    assert "expects boxes" in res.reasoning
