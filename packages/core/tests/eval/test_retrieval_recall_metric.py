"""Unit tests for RetrievalRecallMetric in core evaluation domain."""

from __future__ import annotations

from uuid import uuid4

from core.domain.entities.chunk import DocumentChunk
from core.eval.metrics.retrieval_recall import RetrievalRecallMetric


def test_retrieval_recall_metric_perfect_recall() -> None:
    metric = RetrievalRecallMetric(top_k=3, min_token_overlap=0.40, min_recall=0.80)

    gt_evidence = [
        {"text": "The encoder has N = 6 layers with d_model = 512."},
        {"text": "Positional encodings use sine and cosine functions."},
    ]

    pred_chunks = [
        {"content": "The encoder has N = 6 layers with d_model = 512 in stacks."},
        {"content": "Positional encodings use sine and cosine functions with varied frequency."},
    ]

    res = metric.measure(pred_chunks, gt_evidence)
    assert res.passed is True
    assert res.score == 1.0
    assert res.details["matched_gt_count"] == 2
    assert res.details["total_gt_count"] == 2


def test_retrieval_recall_metric_with_document_chunk_entities() -> None:
    metric = RetrievalRecallMetric(top_k=2, min_token_overlap=0.40, min_recall=0.50)

    chunk = DocumentChunk(
        document_id=uuid4(),
        chunk_index=0,
        page_number=1,
        content="Transformer architecture eschewing recurrence entirely.",
        token_count=6,
    )

    gt_evidence = [{"text": "The Transformer eschewing recurrence entirely."}]

    res = metric.measure([chunk], gt_evidence)
    assert res.passed is True
    assert res.score == 1.0


def test_retrieval_recall_metric_partial_and_top_k_cutoff() -> None:
    metric = RetrievalRecallMetric(top_k=1, min_token_overlap=0.50, min_recall=0.80)

    gt_evidence = [
        {"text": "Transformer architecture uses multi-head attention."},
        {"text": "Surgical resection improves five-year oncology survival rates."},
    ]

    # Oncology text is placed at index 1, which exceeds top_k=1
    pred_chunks = [
        {"content": "Transformer architecture uses multi-head attention."},
        {"content": "Surgical resection improves five-year oncology survival rates."},
    ]

    res = metric.measure(pred_chunks, gt_evidence)
    assert res.passed is False
    assert res.score == 0.5  # Only 1 of 2 retrieved within top-1


def test_retrieval_recall_metric_no_ground_truth_required() -> None:
    metric = RetrievalRecallMetric()
    res = metric.measure([{"content": "Any retrieved content"}], [])
    assert res.passed is True
    assert res.score == 1.0
