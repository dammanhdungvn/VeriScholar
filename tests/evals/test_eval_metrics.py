"""Unit tests for pluggable deep evaluation metrics, formatters, and surgical inspect CLI."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.eval.formatters import fold_heavy_payload  # noqa: E402
from scripts.eval.metrics import (  # noqa: E402
    CascadingF1Metric,
    EntitySanityMetric,
    SpatialGeometryMetric,
    TextIntegrityMetric,
)


def test_text_integrity_metric_clean():
    metric = TextIntegrityMetric()
    clean_text = "This is a clean academic paper text without corruption."
    result = metric.measure(clean_text)
    assert result.passed is True
    assert result.score == 1.0
    assert result.details["mojibake_count"] == 0


def test_text_integrity_metric_mojibake():
    metric = TextIntegrityMetric()
    corrupted_text = "Corrupted academic text with \ufffd\ufffd mojibake characters."
    result = metric.measure(corrupted_text)
    assert result.passed is False
    assert result.details["mojibake_count"] == 2
    assert any(err["error"] == "UNICODE_MOJIBAKE" for err in result.error_samples)


def test_text_integrity_metric_word_gluing():
    metric = TextIntegrityMetric(max_word_length=15)
    glued_text = "Supercalifragilisticexpialidociouswithoutanyspacesinbetween"
    result = metric.measure(glued_text)
    assert any(err["error"] == "WORD_GLUING" for err in result.error_samples)


def test_entity_sanity_metric_valid():
    metric = EntitySanityMetric(current_year=2026)
    valid_refs = [
        {
            "parsed": {
                "authors": ["Vaswani, Ashish"],
                "year": 2017,
                "title": "Attention Is All You Need",
            }
        }
    ]
    result = metric.measure(valid_refs)
    assert result.passed is True
    assert result.score == 1.0


def test_entity_sanity_metric_anomalies():
    metric = EntitySanityMetric(current_year=2026)
    anomalous_refs = [
        {
            "parsed": {
                "authors": ["Department of Computer Science", "john@university.edu"],
                "year": 1750,
                "title": "AB",
            }
        }
    ]
    result = metric.measure(anomalous_refs)
    assert result.passed is False
    errors = [err["error"] for err in result.error_samples]
    assert "ORGANIZATION_AS_AUTHOR" in errors
    assert "EMAIL_AS_AUTHOR" in errors
    assert "INVALID_PUBLICATION_YEAR" in errors
    assert "TITLE_TOO_SHORT" in errors


def test_spatial_geometry_metric_valid():
    metric = SpatialGeometryMetric()
    boxes = [
        {"index": 0, "page": 1, "box_2d": [0.1, 0.1, 0.5, 0.5]},
        {"index": 1, "page": 1, "box_2d": [0.2, 0.2, 0.8, 0.8]},
    ]
    result = metric.measure(boxes)
    assert result.passed is True
    assert result.score == 1.0


def test_spatial_geometry_metric_anomalies():
    metric = SpatialGeometryMetric(max_page_area_ratio=0.95)
    invalid_boxes = [
        {"index": 0, "page": 1, "box_2d": [0.8, 0.8, 0.2, 0.2]},  # Inverted
        {"index": 1, "page": 1, "box_2d": [0.0, 0.0, 1.0, 1.0]},  # Lazy full-page
    ]
    result = metric.measure(invalid_boxes)
    assert result.passed is False
    errors = [err["error"] for err in result.error_samples]
    assert "INVERTED_COORDINATES" in errors
    assert "LAZY_FULL_PAGE_BOX" in errors


def test_cascading_f1_metric():
    metric = CascadingF1Metric(min_recall=0.5, min_precision=0.5)
    prediction = [
        {"parsed": {"doi": "10.1145/12345", "title": "Paper One"}},
        {"parsed": {"arxiv_id": "1706.03762", "title": "Paper Two"}},
    ]
    gt = {
        "expected_reference_count": 2,
        "expected_dois": ["10.1145/12345"],
        "expected_arxiv_ids": ["1706.03762"],
    }
    result = metric.measure(prediction, ground_truth=gt)
    assert result.passed is True
    assert result.details["recall"] == 1.0
    assert result.details["precision"] == 1.0
    assert result.details["f1"] == 1.0


def test_fold_heavy_payload():
    raw_payload = {
        "embeddings": [0.1] * 1536,
        "thumbnail_base64": "A" * 500,
        "chunks": [{"id": i} for i in range(20)],
        "normal_field": "Normal value",
    }
    folded = fold_heavy_payload(raw_payload, max_list_items=2)
    assert folded["embeddings"] == "[float x 1536 dimensions]"
    assert folded["thumbnail_base64"] == "[base64 string (500 bytes)]"
    assert len(folded["chunks"]) == 3
    assert "items folded" in folded["chunks"][1]
    assert folded["chunks"][0] == {"id": 0}
    assert folded["chunks"][2] == {"id": 19}
    assert folded["normal_field"] == "Normal value"
