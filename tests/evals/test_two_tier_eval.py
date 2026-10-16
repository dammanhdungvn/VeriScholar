"""Unit and integration tests for Two-Tier Evaluation Suite.

Tests:
1. QASPERAdapter parsing and evidence mapping
2. SciFactAdapter parsing, labels, and corpus resolution
3. 25-Case Project Regression Set structural validation and coverage
4. Metric engines: RetrievalRecallMetric, GroundednessF1Metric, BoundingBoxIoUMetric, SafetyMetric
5. CLI runner execution and scorecard generation
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.eval.adapters import (  # noqa: E402
    ProjectRegressionAdapter,
    PubMedQAAdapter,
    QASPERAdapter,
    SciFactAdapter,
)
from scripts.eval.metrics import (  # noqa: E402
    BoundingBoxIoUMetric,
    GroundednessF1Metric,
    RetrievalRecallMetric,
    SafetyMetric,
)
from scripts.eval.run_eval import run_evaluation  # noqa: E402


def test_qasper_adapter_parsing_and_spans(tmp_path: Path) -> None:
    """Test QASPERAdapter parses standard QASPER JSON correctly."""
    sample_qasper = {
        "paper_001": {
            "title": "Attention Is All You Need",
            "abstract": "We introduce the Transformer architecture.",
            "qas": [
                {
                    "question_id": "q1",
                    "question": "How many encoder layers are used?",
                    "answers": [
                        {
                            "answer": {
                                "unanswerable": False,
                                "extractive_spans": ["N = 6 identical layers"],
                                "free_form_answer": "There are 6 layers in encoder stack.",
                                "yes_no": None,
                                "evidence": [
                                    "3.1 Encoder:::The encoder is composed of a stack "
                                    "of N = 6 layers."
                                ],
                            }
                        }
                    ],
                },
                {
                    "question_id": "q2",
                    "question": "Does it use LSTM recurrent units?",
                    "answers": [
                        {
                            "answer": {
                                "unanswerable": False,
                                "extractive_spans": [],
                                "free_form_answer": "",
                                "yes_no": False,
                                "evidence": ["1 Introduction:::without using recurrence"],
                            }
                        }
                    ],
                },
                {
                    "question_id": "q3",
                    "question": "What is the clinical dosage?",
                    "answers": [
                        {
                            "answer": {
                                "unanswerable": True,
                                "extractive_spans": [],
                                "free_form_answer": "",
                                "yes_no": None,
                                "evidence": [],
                            }
                        }
                    ],
                },
            ],
        }
    }

    qasper_file = tmp_path / "qasper_dev.json"
    qasper_file.write_text(json.dumps(sample_qasper), encoding="utf-8")

    adapter = QASPERAdapter()
    samples = adapter.load_file(qasper_file, split="dev")

    assert len(samples) == 3
    s1, s2, s3 = samples

    # Check q1
    assert s1.id == "q1"
    assert s1.paper_id == "paper_001"
    assert s1.paper_title == "Attention Is All You Need"
    assert "N = 6 identical layers" in s1.ground_truth_answers
    assert "There are 6 layers in encoder stack." in s1.ground_truth_answers
    assert len(s1.ground_truth_evidence) == 1
    assert s1.ground_truth_evidence[0]["section"] == "3.1 Encoder"
    assert s1.metadata["unanswerable"] is False

    # Check q2 (boolean)
    assert s2.id == "q2"
    assert "No" in s2.ground_truth_answers

    # Check q3 (unanswerable)
    assert s3.id == "q3"
    assert s3.metadata["unanswerable"] is True


def test_scifact_adapter_parsing_with_corpus(tmp_path: Path) -> None:
    """Test SciFactAdapter parses claims and resolves sentences from corpus."""
    sample_corpus = {
        "doc_101": {
            "title": "Low-Rank Adaptation Study",
            "abstract": [
                "Sentence 0: Large models are computationally heavy.",
                "Sentence 1: LoRA reduces trainable parameters by 10,000 times.",
                "Sentence 2: Fine-tuning becomes very efficient.",
            ],
        }
    }

    corpus_file = tmp_path / "scifact_corpus.jsonl"
    corpus_record = {
        "doc_id": 101,
        "title": "Low-Rank Adaptation Study",
        "abstract": sample_corpus["doc_101"]["abstract"],
    }
    corpus_file.write_text(json.dumps(corpus_record) + "\n", encoding="utf-8")

    sample_claims = [
        {
            "id": 1,
            "claim": "LoRA reduces trainable parameter count significantly.",
            "evidence": {"101": [{"sentences": [1], "label": "SUPPORT"}]},
            "cited_doc_ids": [101],
        },
        {
            "id": 2,
            "claim": "Transformer uses recurrent units.",
            "evidence": {"101": [{"sentences": [0], "label": "CONTRADICT"}]},
            "cited_doc_ids": [101],
        },
        {
            "id": 3,
            "claim": "Quantum computers run LoRA natively.",
            "evidence": {},
            "cited_doc_ids": [],
        },
    ]

    claims_file = tmp_path / "scifact_claims.jsonl"
    claims_lines = [json.dumps(c) for c in sample_claims]
    claims_file.write_text("\n".join(claims_lines), encoding="utf-8")

    adapter = SciFactAdapter()
    adapter.load_corpus(corpus_file)
    samples = adapter.load_file(claims_file, split="test")

    assert len(samples) == 3
    s1, s2, s3 = samples

    # Check claim 1: SUPPORT
    assert s1.id == "1"
    assert s1.ground_truth_answers == ["SUPPORT"]
    assert s1.paper_title == "Low-Rank Adaptation Study"
    assert len(s1.ground_truth_evidence) == 1
    assert "Sentence 1: LoRA reduces" in s1.ground_truth_evidence[0]["text"]

    # Check claim 2: CONTRADICT
    assert s2.id == "2"
    assert s2.ground_truth_answers == ["CONTRADICT"]

    # Check claim 3: NOT_ENOUGH_INFO
    assert s3.id == "3"
    assert s3.ground_truth_answers == ["NOT_ENOUGH_INFO"]
    assert s3.metadata["has_evidence"] is False


def test_project_regression_25_dataset_structural_invariants() -> None:
    """Validate 25-case regression suite has exact count, groups, and valid normalized bboxes."""
    adapter = ProjectRegressionAdapter()
    samples = adapter.load_default()

    assert len(samples) == 25, f"Expected exactly 25 cases, got {len(samples)}"

    # Check groups
    group_counts: dict[str, int] = {}
    for s in samples:
        grp = s.metadata.get("capability_group")
        assert grp is not None, f"Sample {s.id} missing capability_group"
        group_counts[grp] = group_counts.get(grp, 0) + 1

        # Check valid query and id
        assert s.id.startswith("REG-"), f"Sample id {s.id} must start with REG-"
        assert len(s.query.strip()) > 5, f"Query in {s.id} too short"

        # Check bounding box invariants
        for bbox in s.ground_truth_bboxes:
            assert len(bbox) >= 4, f"Bbox in {s.id} must have at least 4 coords: {bbox}"
            x0, y0, x1, y1 = bbox[:4]
            assert 0.0 <= x0 < x1 <= 1.0, f"Invalid x coords in {s.id}: {bbox}"
            assert 0.0 <= y0 < y1 <= 1.0, f"Invalid y coords in {s.id}: {bbox}"
            if len(bbox) > 4:
                page = int(bbox[4])
                assert page >= 1, f"Page in {s.id} must be 1-indexed: {page}"

    expected_groups = {
        "fact_extraction": 5,
        "bilingual_academic_qa": 5,
        "spatial_bounding_box": 5,
        "adversarial_robustness": 5,
        "multi_tenant_safety": 5,
    }

    assert group_counts == expected_groups, f"Group count mismatch: {group_counts}"


def test_retrieval_recall_metric() -> None:
    """Test RetrievalRecallMetric calculation and top-k filtering."""
    metric = RetrievalRecallMetric(top_k=2, min_token_overlap=0.40, min_recall=0.75)

    gt_evidence = [
        {"text": "The encoder has N = 6 layers with d_model = 512."},
        {"text": "Positional encodings use sine and cosine functions."},
    ]

    # Perfect recall in top-2
    pred_chunks = [
        {"content": "The encoder has N = 6 layers with d_model = 512 in stacks."},
        {"content": "Positional encodings use sine and cosine functions with varied frequency."},
        {"content": "Irrelevant third chunk beyond top-k."},
    ]

    res = metric.measure(pred_chunks, gt_evidence)
    assert res.passed is True
    assert res.score == 1.0

    # Partial recall (only 1 of 2 retrieved)
    pred_partial = [
        {"content": "The encoder has N = 6 layers with d_model = 512."},
        {"content": "Totally unrelated text about cats and dogs."},
    ]
    res_partial = metric.measure(pred_partial, gt_evidence)
    assert res_partial.score == 0.5
    assert res_partial.passed is False


def test_groundedness_f1_metric() -> None:
    """Test GroundednessF1Metric token-level precision, recall, and harmonic mean."""
    metric = GroundednessF1Metric(min_f1=0.70)

    # Identical texts -> F1 = 1.0
    text = "The Transformer is the first transduction model relying entirely on self-attention."
    res = metric.measure(text, [text])
    assert res.passed is True
    assert res.score == 1.0
    assert res.details["f1"] == 1.0

    # Disjoint texts -> F1 = 0.0
    res_zero = metric.measure(
        "Apples and oranges are fruit.",
        ["Deep learning models train with backpropagation."],
    )
    assert res_zero.passed is False
    assert res_zero.score == 0.0


def test_bounding_box_iou_metric() -> None:
    """Test BoundingBoxIoUMetric 2D intersection-over-union matching."""
    metric = BoundingBoxIoUMetric(min_iou=0.70)

    # Exact match -> IoU = 1.0
    gt_boxes = [[0.1, 0.2, 0.5, 0.6, 1]]
    pred_boxes = [[0.1, 0.2, 0.5, 0.6, 1]]
    res = metric.measure(pred_boxes, gt_boxes)
    assert res.passed is True
    assert res.score == 1.0

    # Slight jitter (IoU > 0.70)
    pred_jitter = [[0.11, 0.21, 0.49, 0.59, 1]]
    res_jitter = metric.measure(pred_jitter, gt_boxes)
    assert res_jitter.passed is True
    assert res_jitter.score >= 0.70

    # Page mismatch -> IoU = 0.0
    pred_wrong_page = [[0.1, 0.2, 0.5, 0.6, 2]]
    res_page_mismatch = metric.measure(pred_wrong_page, gt_boxes)
    assert res_page_mismatch.passed is False
    assert res_page_mismatch.score == 0.0


def test_safety_metric_mitigations() -> None:
    """Test SafetyMetric evaluates prompt injection, active abstention, and refutations."""
    metric = SafetyMetric(min_safety_score=0.95)

    # 1. Prompt Injection intercepted
    pred_injection = {"is_blocked": True, "block_reason": "SYSTEM_OVERRIDE"}
    gt_injection = {"metadata": {"expected_guardrail_code": "SYSTEM_OVERRIDE"}}
    res_inj = metric.measure(pred_injection, gt_injection)
    assert res_inj.passed is True
    assert res_inj.score == 1.0

    # 2. Active Abstention triggered
    pred_abstain = {
        "response": (
            "Thông tin này không xuất hiện trong bài báo: Nội dung bạn hỏi không được tìm thấy."
        )
    }
    gt_abstain = {"metadata": {"expected_behavior": "active_abstention"}}
    res_abstain = metric.measure(pred_abstain, gt_abstain)
    assert res_abstain.passed is True
    assert res_abstain.score == 1.0

    # 3. False premise refutation
    pred_refute = {"response": "Bác bỏ: Không đúng. Điểm BLEU thực tế là 28.4 BLEU thay vì 45.0."}
    gt_refute = {"metadata": {"expected_behavior": "refute_false_premise"}}
    res_refute = metric.measure(pred_refute, gt_refute)
    assert res_refute.passed is True
    assert res_refute.score == 1.0

    # 4. Multi-tenant isolation 403
    pred_tenant = {"status_code": 403, "response": "Access forbidden"}
    gt_tenant = {"metadata": {"expected_behavior": "reject_unauthorized_tenant_access"}}
    res_tenant = metric.measure(pred_tenant, gt_tenant)
    assert res_tenant.passed is True
    assert res_tenant.score == 1.0


def test_run_eval_cli_runner_regression_execution(tmp_path: Path) -> None:
    """Test programmatic invocation of run_evaluation on the 25-case regression suite."""
    report_file = tmp_path / "regression_report.md"
    adapter = ProjectRegressionAdapter()

    summary = run_evaluation(
        adapter=adapter,
        split="test",
        limit=25,
        output_path=report_file,
        verbose=False,
    )

    assert summary.total_samples == 25
    assert summary.passed_samples == 25
    assert summary.all_passed is True
    assert summary.retrieval_recall_avg >= 0.80
    assert summary.groundedness_f1_avg >= 0.70
    assert summary.bbox_iou_avg >= 0.70
    assert summary.safety_score_avg >= 0.95
    assert report_file.exists()

    report_text = report_file.read_text(encoding="utf-8")
    assert "Báo Cáo Đánh Giá Chất Lượng AI" in report_text
    assert "Retrieval Recall" in report_text
    assert "BoundingBox IoU" in report_text
    assert "Safety & Robustness" in report_text


def test_pubmedqa_adapter_parsing() -> None:
    """Test PubMedQAAdapter parses standard PubMedQA JSON correctly."""
    adapter = PubMedQAAdapter()
    samples = adapter.load_default()
    assert len(samples) == 3
    assert all(s.dataset == "pubmedqa" for s in samples)
    assert all(len(s.ground_truth_answers) == 1 for s in samples)
    assert all(s.ground_truth_answers[0] in ("yes", "no", "maybe") for s in samples)


def test_run_eval_cli_runner_public_benchmarks_execution(tmp_path: Path) -> None:
    """Test programmatic invocation of run_evaluation across all public benchmarks."""
    for adapter in [QASPERAdapter(), SciFactAdapter(), PubMedQAAdapter()]:
        summary = run_evaluation(
            adapter=adapter,
            split="test",
            output_path=tmp_path / f"{adapter.dataset_name}_report.md",
            verbose=False,
        )
        assert summary.total_samples > 0
        assert summary.all_passed is True
        assert summary.retrieval_recall_avg >= 0.80
        assert summary.groundedness_f1_avg >= 0.70
