"""Adversarial stress-test suite for Milestone 2 evaluation components."""

import sys
from uuid import uuid4
import pytest
from core.domain.entities.chunk import (
    BGE_M3_EMBEDDING_DIM,
    OPENAI_EMBEDDING_DIM,
    VALID_EMBEDDING_DIMS,
    DocumentChunk,
)
from core.domain.exceptions import InvariantViolationError
from core.eval.models import EvalSample, MetricResult, BenchmarkReport, EvalPrediction
from core.eval.adapters.qasper import QASPERAdapter
from core.eval.adapters.scifact import SciFactAdapter
from core.eval.adapters.pubmedqa import PubMedQAAdapter
from core.eval.adapters.regression import ProjectRegressionAdapter
from core.eval.metrics.token_f1 import TokenF1Metric, compute_token_f1, normalize_answer
from core.eval.metrics.retrieval_recall import RetrievalRecallMetric
from core.eval.metrics.classification import ClassificationMetric, compute_macro_f1, normalize_label
from core.eval.metrics.bbox_iou import BoundingBoxIoUMetric, compute_box_iou
from core.eval.metrics.spatial_geometry import SpatialGeometryMetric
from core.eval.metrics.safety import SafetyMetric
from core.eval.evaluators.benchmark_runner import BenchmarkRunner

def test_adversarial_chunk_embeddings():
    doc_id = uuid4()
    # Boundary tests for embedding dimension
    for invalid_dim in [0, 1, 1023, 1025, 1535, 1537, 2048, 4096]:
        try:
            DocumentChunk(
                document_id=doc_id,
                chunk_index=0,
                page_number=1,
                content="test",
                token_count=1,
                embedding=[0.0] * invalid_dim,
            )
            assert False, f"Failed to reject invalid dimension {invalid_dim}"
        except InvariantViolationError:
            pass

    # Valid dimensions
    c1024 = DocumentChunk(
        document_id=doc_id,
        chunk_index=0,
        page_number=1,
        content="test",
        token_count=1,
        embedding=[0.0] * 1024,
    )
    assert len(c1024.embedding) == 1024

    c1536 = DocumentChunk(
        document_id=doc_id,
        chunk_index=1,
        page_number=1,
        content="test",
        token_count=1,
        embedding=[0.0] * 1536,
    )
    assert len(c1536.embedding) == 1536
    print("[PASS] Adversarial chunk embeddings")

def test_adversarial_token_f1():
    metric = TokenF1Metric(min_f1=0.70)
    
    # 1. Punctuation only and whitespace only
    assert normalize_answer("!@#$%^&*()_+") == ""
    assert normalize_answer("   \t\n  ") == ""
    p, r, f1 = compute_token_f1("!@#$", "   ")
    assert (p, r, f1) == (1.0, 1.0, 1.0)

    # 2. Vietnamese unicode text normalization
    res_vi = metric.measure(
        "Mô hình Transformer gồm 6 lớp encoder và 6 lớp decoder.",
        ["mô hình transformer gồm 6 lớp encoder và 6 lớp decoder"]
    )
    assert res_vi.passed is True
    assert res_vi.score == 1.0

    # 3. None and dict inputs
    res_none = metric.measure(None, ["something"])
    assert res_none.passed is False
    assert res_none.score == 0.0

    res_dict = metric.measure({"predicted_answer": "correct answer"}, ["correct answer"])
    assert res_dict.passed is True
    assert res_dict.score == 1.0
    print("[PASS] Adversarial Token F1")

def test_adversarial_bbox_iou():
    metric = BoundingBoxIoUMetric(min_iou=0.70)

    # 1. Negative or zero area box
    b_zero_width = [0.2, 0.2, 0.2, 0.5, 1.0]
    b_norm = [0.1, 0.1, 0.5, 0.5, 1.0]
    assert compute_box_iou(b_zero_width, b_norm) == 0.0

    # 2. Inverted box (x1 < x0)
    b_inverted = [0.5, 0.2, 0.2, 0.5, 1.0]
    assert compute_box_iou(b_inverted, b_norm) == 0.0

    # 3. Disjoint pages
    b_p1 = [0.1, 0.1, 0.4, 0.4, 1.0]
    b_p2 = [0.1, 0.1, 0.4, 0.4, 2.0]
    assert compute_box_iou(b_p1, b_p2) == 0.0

    # 4. Partial overlap calculation accuracy
    b_a = [0.0, 0.0, 2.0, 2.0, 1.0]
    b_b = [1.0, 1.0, 3.0, 3.0, 1.0]
    # Inter: [1, 1, 2, 2] -> area = 1
    # Area A = 4, Area B = 4, Union = 4 + 4 - 1 = 7
    # IoU = 1/7
    assert round(compute_box_iou(b_a, b_b), 4) == round(1 / 7, 4)
    print("[PASS] Adversarial BBox IoU")

def test_adversarial_spatial_geometry():
    metric = SpatialGeometryMetric(min_iou=0.70, max_page_area_ratio=0.95)

    # 1. Negative coordinates
    res_neg = metric.measure([[-0.1, 0.1, 0.5, 0.5, 1]])
    assert res_neg.passed is False
    assert res_neg.details["anomalies_count"] == 1
    assert res_neg.error_samples[0]["error"] == "NEGATIVE_COORDINATE"

    # 2. Inverted coordinates
    res_inv = metric.measure([[0.5, 0.1, 0.2, 0.5, 1]])
    assert res_inv.passed is False
    assert res_inv.details["anomalies_count"] == 1
    assert res_inv.error_samples[0]["error"] == "INVERTED_COORDINATES"

    # 3. Invalid page (page = 0)
    res_p0 = metric.measure([[0.1, 0.1, 0.5, 0.5, 0]])
    assert res_p0.passed is False
    assert res_p0.details["anomalies_count"] == 1
    assert res_p0.error_samples[0]["error"] == "INVALID_PAGE_INDEX"

    # 4. Lazy full page box (area > 0.95)
    res_lazy = metric.measure([[0.0, 0.0, 0.99, 0.99, 1]])
    assert res_lazy.passed is False
    assert res_lazy.details["anomalies_count"] == 1
    assert res_lazy.error_samples[0]["error"] == "LAZY_FULL_PAGE_BOX"
    print("[PASS] Adversarial Spatial Geometry")

def test_adversarial_safety_metric():
    metric = SafetyMetric(min_safety_score=0.95)

    # 1. Citation hallucination detection
    res_hallucination = metric.measure(
        prediction={"response": "Based on [^cit_valid1] and [^cit_fake99]."},
        valid_citation_ids=["valid1"],
    )
    assert res_hallucination.passed is False
    assert res_hallucination.score == 0.0
    assert "fake99" in str(res_hallucination.details["hallucinated_citations"])

    # 2. Prompt leak detection
    res_leak = metric.measure(
        prediction={"response": "The <untrusted_document_context> shows..."}
    )
    assert res_leak.passed is False
    assert res_leak.score == 0.0

    # 3. Tenant 403 isolation
    res_tenant_ok = metric.measure(
        prediction={"status_code": 403, "response": "Forbidden"},
        metadata={"expected_behavior": "reject_unauthorized_tenant_access"},
    )
    assert res_tenant_ok.passed is True

    res_tenant_fail = metric.measure(
        prediction={"status_code": 200, "response": "Authorized"},
        metadata={"expected_behavior": "reject_unauthorized_tenant_access"},
    )
    assert res_tenant_fail.passed is False
    print("[PASS] Adversarial Safety Metric")

def test_adversarial_adapters():
    # 1. Malformed QASPER
    q_adapter = QASPERAdapter()
    assert q_adapter.parse_data({"invalid": "data"}) == []
    assert q_adapter.parse_data([{"paper_id": "p1", "qas": "not a list"}]) == []

    # 2. SciFact with empty corpus
    s_adapter = SciFactAdapter(corpus={})
    samples = s_adapter.parse_data([{"id": "c1", "claim": "claim 1", "cited_doc_ids": ["999"]}])
    assert len(samples) == 1
    assert samples[0].paper_title == ""

    # 3. PubMedQA missing questions
    p_adapter = PubMedQAAdapter()
    assert p_adapter.parse_data({"pmid1": {"no_question": True}}) == []
    print("[PASS] Adversarial Adapters")

def main():
    test_adversarial_chunk_embeddings()
    test_adversarial_token_f1()
    test_adversarial_bbox_iou()
    test_adversarial_spatial_geometry()
    test_adversarial_safety_metric()
    test_adversarial_adapters()
    print("\nALL ADVERSARIAL STRESS TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
