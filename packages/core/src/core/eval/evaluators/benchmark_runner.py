"""In-memory benchmark evaluation runner.

Orchestrates dataset adapters, evaluation metrics, and sample scoring
to produce structured BenchmarkReport scorecards with 100% in-memory isolation.
"""

from __future__ import annotations

from typing import Any, Callable

from core.eval.metrics.base import BaseEvalMetric
from core.eval.metrics.bbox_iou import BoundingBoxIoUMetric
from core.eval.metrics.classification import ClassificationMetric
from core.eval.metrics.retrieval_recall import RetrievalRecallMetric
from core.eval.metrics.safety import SafetyMetric
from core.eval.metrics.spatial_geometry import SpatialGeometryMetric
from core.eval.metrics.token_f1 import TokenF1Metric
from core.eval.models import BenchmarkReport, EvalPrediction, EvalSample, MetricResult
from core.ports.eval import IBenchmarkEvaluator


class BenchmarkRunner(IBenchmarkEvaluator):
    """In-memory benchmark evaluation runner orchestrating adapters and decoupled metrics."""

    def __init__(
        self,
        metrics: list[BaseEvalMetric] | None = None,
        name: str = "VeriScholar In-Memory Benchmark",
    ) -> None:
        self.name = name
        self.metrics: dict[str, BaseEvalMetric] = {}
        if metrics is not None:
            for m in metrics:
                self.metrics[m.name] = m
        else:
            # Default suite of 6 core metrics
            self.metrics = {
                "token_f1": TokenF1Metric(),
                "retrieval_recall": RetrievalRecallMetric(),
                "classification": ClassificationMetric(),
                "bounding_box_iou": BoundingBoxIoUMetric(),
                "spatial_geometry": SpatialGeometryMetric(),
                "safety": SafetyMetric(),
            }

    def evaluate_sample(
        self,
        sample: EvalSample,
        prediction: EvalPrediction | dict[str, Any] | Any,
    ) -> dict[str, MetricResult]:
        """Evaluate an individual sample against active metrics.

        Returns a dictionary mapping metric name to MetricResult.
        """
        results: dict[str, MetricResult] = {}
        if hasattr(prediction, "to_dict"):
            pred_dict = prediction.to_dict()
            if "metadata" in pred_dict and isinstance(pred_dict["metadata"], dict):
                for k, v in pred_dict["metadata"].items():
                    if k not in pred_dict or pred_dict[k] is None or pred_dict[k] == "":
                        pred_dict[k] = v
        elif isinstance(prediction, dict):
            pred_dict = dict(prediction)
            if "metadata" in pred_dict and isinstance(pred_dict["metadata"], dict):
                for k, v in pred_dict["metadata"].items():
                    if k not in pred_dict or pred_dict[k] is None or pred_dict[k] == "":
                        pred_dict[k] = v
        else:
            pred_dict = {"response": str(prediction)}

        if not pred_dict.get("response") and pred_dict.get("predicted_answer"):
            pred_dict["response"] = pred_dict["predicted_answer"]
        if not pred_dict.get("predicted_answer") and pred_dict.get("response"):
            pred_dict["predicted_answer"] = pred_dict["response"]

        # 1. Safety metric
        if "safety" in self.metrics:
            is_safety_case = (
                bool(sample.metadata.get("expected_guardrail_code"))
                or bool(sample.metadata.get("expected_behavior"))
                or sample.metadata.get("capability_group")
                in ("adversarial_robustness", "multi_tenant_safety")
            )
            if is_safety_case or pred_dict.get("is_blocked"):
                results["safety"] = self.metrics["safety"].measure(
                    prediction=pred_dict,
                    ground_truth={"metadata": sample.metadata},
                    metadata=sample.metadata,
                )

        # 2. Retrieval Recall metric
        if "retrieval_recall" in self.metrics:
            if sample.ground_truth_evidence:
                retrieved = pred_dict.get("retrieved_chunks", [])
                results["retrieval_recall"] = self.metrics["retrieval_recall"].measure(
                    prediction=retrieved,
                    ground_truth=sample.ground_truth_evidence,
                )

        # 3. Categorical Classification metric
        if "classification" in self.metrics:
            is_classification = (
                sample.dataset in ("scifact", "pubmedqa")
                or bool(sample.metadata.get("final_decision"))
                or bool(sample.metadata.get("label"))
                or (
                    bool(sample.ground_truth_answers)
                    and sample.ground_truth_answers[0]
                    in {
                        "SUPPORT",
                        "CONTRADICT",
                        "NOT_ENOUGH_INFO",
                        "yes",
                        "no",
                        "maybe",
                    }
                )
            )
            if is_classification:
                results["classification"] = self.metrics["classification"].measure(
                    prediction=pred_dict,
                    ground_truth=sample.ground_truth_answers,
                    metadata=sample.metadata,
                )

        # 4. Token F1 metric (Answer vs Answer)
        if "token_f1" in self.metrics:
            # Skip token F1 if it was purely a guardrail attack block or classification
            is_guardrail_block = bool(sample.metadata.get("expected_guardrail_code"))
            if not is_guardrail_block and sample.ground_truth_answers:
                pred_text = str(
                    pred_dict.get("predicted_answer")
                    or pred_dict.get("response")
                    or pred_dict.get("answer")
                    or ""
                )
                results["token_f1"] = self.metrics["token_f1"].measure(
                    prediction=pred_text,
                    ground_truth=sample.ground_truth_answers,
                    unanswerable=sample.metadata.get("unanswerable", False),
                )

        # 5. BoundingBox IoU metric
        if "bounding_box_iou" in self.metrics:
            if sample.ground_truth_bboxes:
                pred_bboxes = pred_dict.get("predicted_bboxes") or pred_dict.get(
                    "bounding_boxes", []
                )
                results["bounding_box_iou"] = self.metrics["bounding_box_iou"].measure(
                    prediction=pred_bboxes,
                    ground_truth=sample.ground_truth_bboxes,
                )

        # 6. Spatial Geometry metric
        if "spatial_geometry" in self.metrics:
            if hasattr(prediction, "predicted_bboxes") and prediction.predicted_bboxes is not None:
                pred_bboxes = prediction.predicted_bboxes
            elif (
                isinstance(pred_dict, dict)
                and "predicted_bboxes" in pred_dict
                and pred_dict["predicted_bboxes"] is not None
            ):
                pred_bboxes = pred_dict["predicted_bboxes"]
            elif (
                isinstance(pred_dict, dict)
                and "bounding_boxes" in pred_dict
                and pred_dict["bounding_boxes"] is not None
            ):
                pred_bboxes = pred_dict["bounding_boxes"]
            else:
                pred_bboxes = []

            if pred_bboxes or sample.ground_truth_bboxes:
                results["spatial_geometry"] = self.metrics["spatial_geometry"].measure(
                    prediction=pred_bboxes,
                    ground_truth=sample.ground_truth_bboxes,
                )

        return results

    def evaluate(
        self,
        samples: list[EvalSample],
        predictions: dict[str, Any] | Callable[[EvalSample], Any] | None = None,
        **kwargs: Any,
    ) -> BenchmarkReport:
        """Run evaluation across all samples and return consolidated BenchmarkReport.

        Args:
            samples: List of benchmark EvalSample instances.
            predictions: Either a dictionary mapping sample_id -> prediction, or a callable
                `prediction_fn(sample) -> prediction`.

        Raises:
            ValueError: If predictions is None or omitted.
        """
        if predictions is None:
            raise ValueError(
                "Predictions must be provided to evaluate(). "
                "BenchmarkRunner does not fabricate synthetic predictions."
            )

        sample_results: list[dict[str, Any]] = []
        metric_score_sums: dict[str, float] = {}
        metric_counts: dict[str, int] = {}
        group_stats: dict[str, dict[str, Any]] = {}
        passed_samples_count = 0

        for sample in samples:
            # Resolve prediction
            if callable(predictions):
                pred = predictions(sample)
            elif isinstance(predictions, dict):
                pred = predictions.get(sample.id, {})
            else:
                pred = {}

            metric_verdicts = self.evaluate_sample(sample, pred)
            sample_all_passed = (
                all(res.passed for res in metric_verdicts.values()) if metric_verdicts else True
            )
            if sample_all_passed:
                passed_samples_count += 1

            for m_name, res in metric_verdicts.items():
                metric_score_sums[m_name] = metric_score_sums.get(m_name, 0.0) + res.score
                metric_counts[m_name] = metric_counts.get(m_name, 0) + 1

            # Group statistics (by capability_group or dataset)
            group_key = str(sample.metadata.get("capability_group") or sample.dataset)
            if group_key not in group_stats:
                group_stats[group_key] = {"total": 0, "passed": 0}
            group_stats[group_key]["total"] += 1
            if sample_all_passed:
                group_stats[group_key]["passed"] += 1

            sample_results.append(
                {
                    "sample_id": sample.id,
                    "dataset": sample.dataset,
                    "group": group_key,
                    "passed": sample_all_passed,
                    "metrics": {m: res.to_dict() for m, res in metric_verdicts.items()},
                }
            )

        total_samples = len(samples)
        pass_rate = (passed_samples_count / total_samples) if total_samples > 0 else 1.0
        metric_averages = {
            m: round(metric_score_sums[m] / metric_counts[m], 4)
            for m in metric_score_sums
            if metric_counts.get(m, 0) > 0
        }

        # Calculate pass rates per group
        for grp, stats in group_stats.items():
            tot = stats["total"]
            ps = stats["passed"]
            stats["pass_rate"] = round(ps / tot, 4) if tot > 0 else 1.0

        all_passed = (passed_samples_count == total_samples) if total_samples > 0 else True

        return BenchmarkReport(
            benchmark_name=self.name,
            total_samples=total_samples,
            passed_samples=passed_samples_count,
            pass_rate=round(pass_rate, 4),
            metric_averages=metric_averages,
            group_breakdown=group_stats,
            all_passed=all_passed,
            details=sample_results,
        )
