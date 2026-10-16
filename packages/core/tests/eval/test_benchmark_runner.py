"""Unit tests for BenchmarkRunner in core evaluation domain."""

from __future__ import annotations

from pathlib import Path

import pytest
from core.eval.adapters.pubmedqa import PubMedQAAdapter
from core.eval.adapters.qasper import QASPERAdapter
from core.eval.adapters.regression import ProjectRegressionAdapter
from core.eval.adapters.scifact import SciFactAdapter
from core.eval.evaluators.benchmark_runner import BenchmarkRunner
from core.eval.models import EvalPrediction, EvalSample
from core.ports.eval import IBenchmarkEvaluator

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_benchmark_runner_protocol_compliance() -> None:
    runner = BenchmarkRunner()
    assert isinstance(runner, IBenchmarkEvaluator)
    assert "token_f1" in runner.metrics
    assert "retrieval_recall" in runner.metrics
    assert "classification" in runner.metrics
    assert "bounding_box_iou" in runner.metrics
    assert "spatial_geometry" in runner.metrics
    assert "safety" in runner.metrics


def test_benchmark_runner_regression_samples_execution() -> None:
    adapter = ProjectRegressionAdapter()
    samples = adapter.load_file(FIXTURES_DIR / "regression_subset.json", split="test")
    assert len(samples) == 5

    predictions = {
        "REG-01": EvalPrediction(
            sample_id="REG-01",
            predicted_answer="Encoder gồm N = 6 layers giống hệt nhau.",
            retrieved_chunks=samples[0].ground_truth_evidence,
            predicted_bboxes=samples[0].ground_truth_bboxes,
        ),
        "REG-06": EvalPrediction(
            sample_id="REG-06",
            predicted_answer=samples[1].ground_truth_answers[0],
            retrieved_chunks=samples[1].ground_truth_evidence,
            predicted_bboxes=samples[1].ground_truth_bboxes,
        ),
        "REG-11": EvalPrediction(
            sample_id="REG-11",
            predicted_answer="Figure 1: The Transformer - model architecture.",
            retrieved_chunks=samples[2].ground_truth_evidence,
            predicted_bboxes=samples[2].ground_truth_bboxes,
        ),
        "REG-16": EvalPrediction(
            sample_id="REG-16",
            predicted_answer=samples[3].ground_truth_answers[0],
            retrieved_chunks=samples[3].ground_truth_evidence,
            predicted_bboxes=samples[3].ground_truth_bboxes,
            metadata={
                "response": samples[3].ground_truth_answers[0],
            },
        ),
        "REG-21": EvalPrediction(
            sample_id="REG-21",
            predicted_answer="BLOCKED_BY_GUARDRAIL",
            retrieved_chunks=[],
            predicted_bboxes=[],
            metadata={
                "is_blocked": True,
                "block_reason": "SYSTEM_OVERRIDE",
                "response": "BLOCKED_BY_GUARDRAIL",
            },
        ),
    }

    runner = BenchmarkRunner(name="Regression Subset Test")
    report = runner.evaluate(samples, predictions=predictions)

    assert report.total_samples == 5
    assert report.passed_samples == 5
    assert report.pass_rate == 1.0
    assert report.all_passed is True

    # Check metric averages
    assert "token_f1" in report.metric_averages
    assert "retrieval_recall" in report.metric_averages
    assert "bounding_box_iou" in report.metric_averages
    assert "safety" in report.metric_averages
    assert report.metric_averages["retrieval_recall"] >= 0.80

    # Check group breakdown
    assert "fact_extraction" in report.group_breakdown
    assert "adversarial_robustness" in report.group_breakdown
    assert "multi_tenant_safety" in report.group_breakdown
    assert report.group_breakdown["multi_tenant_safety"]["pass_rate"] == 1.0

    # Serialization
    report_dict = report.to_dict()
    assert report_dict["benchmark_name"] == "Regression Subset Test"
    assert report_dict["total_samples"] == 5
    assert report_dict["all_passed"] is True


def test_benchmark_runner_public_benchmarks_execution() -> None:
    # 1. QASPER
    q_adapter = QASPERAdapter()
    q_samples = q_adapter.load_file(FIXTURES_DIR / "qasper_subset.json")

    # 2. SciFact
    s_adapter = SciFactAdapter(
        corpus={
            "12345": {
                "title": "LoRA Paper",
                "abstract": [
                    "Sentence 0: Recurrent models are slow.",
                    "Sentence 1: LoRA reduces parameters.",
                    "Sentence 2: Parameter reduction is great.",
                ],
            }
        }
    )
    s_samples = s_adapter.load_file(FIXTURES_DIR / "scifact_subset.json")

    # 3. PubMedQA
    p_adapter = PubMedQAAdapter()
    p_samples = p_adapter.load_file(FIXTURES_DIR / "pubmedqa_subset.json")

    combined_samples: list[EvalSample] = [*q_samples, *s_samples, *p_samples]
    assert len(combined_samples) == 4 + 3 + 3  # 10 total

    def generate_prediction(sample: EvalSample) -> EvalPrediction:
        answer = sample.ground_truth_answers[0] if sample.ground_truth_answers else ""
        return EvalPrediction(
            sample_id=sample.id,
            predicted_answer=answer,
            retrieved_chunks=sample.ground_truth_evidence,
            predicted_bboxes=sample.ground_truth_bboxes,
            predicted_label=answer,
            metadata={"response": answer},
        )

    runner = BenchmarkRunner(name="Multi-Benchmark Public Suite")
    report = runner.evaluate(combined_samples, predictions=generate_prediction)

    assert report.total_samples == 10
    assert report.passed_samples == 10
    assert report.pass_rate == 1.0
    assert report.all_passed is True
    assert "classification" in report.metric_averages


def test_benchmark_runner_custom_predictions_with_failures() -> None:
    sample = EvalSample(
        id="sample_fail",
        dataset="qasper",
        split="dev",
        paper_id="p1",
        paper_title="Title",
        query="What is the answer?",
        ground_truth_answers=["Exact golden answer."],
        ground_truth_evidence=[{"text": "Golden evidence text."}],
        ground_truth_bboxes=[[0.1, 0.1, 0.5, 0.5, 1]],
    )

    runner = BenchmarkRunner()

    # Intentionally failing predictions
    failing_predictions = {
        "sample_fail": EvalPrediction(
            sample_id="sample_fail",
            predicted_answer="Completely unrelated reply.",
            retrieved_chunks=[{"content": "Irrelevant chunk."}],
            predicted_bboxes=[[0.1, 0.1, 0.5, 0.5, 99]],  # Wrong page -> IoU = 0.0
        )
    }

    report = runner.evaluate([sample], predictions=failing_predictions)

    assert report.total_samples == 1
    assert report.passed_samples == 0
    assert report.pass_rate == 0.0
    assert report.all_passed is False
    assert report.metric_averages["token_f1"] < 0.70
    assert report.metric_averages["bounding_box_iou"] == 0.0


def test_benchmark_runner_omitted_predictions_raises_value_error() -> None:
    sample = EvalSample(
        id="s1",
        dataset="qasper",
        split="dev",
        paper_id="p1",
        paper_title="Title",
        query="What is the answer?",
        ground_truth_answers=["Answer"],
    )
    runner = BenchmarkRunner()
    with pytest.raises(
        ValueError,
        match=r"Predictions must be provided to evaluate\(\)",
    ):
        runner.evaluate([sample])


def test_benchmark_runner_empty_bboxes_does_not_fallback_to_ground_truth() -> None:
    sample = EvalSample(
        id="t1",
        dataset="qasper",
        split="dev",
        paper_id="p1",
        paper_title="T",
        query="Q?",
        ground_truth_bboxes=[[0.1, 0.2, 0.5, 0.6, 1]],
    )
    runner = BenchmarkRunner()
    res = runner.evaluate_sample(sample, {"predicted_bboxes": []})
    assert "spatial_geometry" in res
    assert res["spatial_geometry"].passed is False
    assert res["spatial_geometry"].score == 0.0
