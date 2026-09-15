"""Cascading F1 metric for reference and entity extraction."""

from typing import Any

from scripts.eval.matchers import is_reference_match
from scripts.eval.metrics.base import BaseEvalMetric, MetricResult


class CascadingF1Metric(BaseEvalMetric):
    """Evaluates reference extraction via Cascading Matcher (DOI/arXiv -> Token Jaccard)."""

    def __init__(self, min_recall: float = 0.90, min_precision: float = 0.95):
        self.min_recall = min_recall
        self.min_precision = min_precision

    @property
    def name(self) -> str:
        return "cascading_f1"

    def measure(self, prediction: Any, ground_truth: Any = None, **kwargs: Any) -> MetricResult:
        """Prediction: list of extracted reference dicts.

        ground_truth: golden ground truth dict with 'expected_reference_count',
        'expected_dois', 'expected_arxiv_ids', 'sample_references'.
        """
        if not isinstance(prediction, list):
            prediction = []

        if not ground_truth or not isinstance(ground_truth, dict):
            return MetricResult(
                name=self.name,
                score=1.0,
                threshold=self.min_precision,
                passed=len(prediction) > 0,
                details={"extracted_count": len(prediction)},
                reasoning="No ground truth provided for strict F1 calculation.",
            )

        expected_count = ground_truth.get("expected_reference_count", len(prediction))
        expected_dois = ground_truth.get("expected_dois", [])
        expected_arxiv_ids = ground_truth.get("expected_arxiv_ids", [])
        sample_expected_refs = ground_truth.get("sample_references", [])

        matched_count = 0
        match_breakdown = {"doi": 0, "arxiv": 0, "jaccard": 0, "unmatched": 0}

        for ext in prediction:
            parsed = ext.get("parsed", {}) if isinstance(ext, dict) else {}
            is_match = False

            if parsed.get("doi") and parsed.get("doi") in expected_dois:
                is_match = True
                match_breakdown["doi"] += 1
            elif parsed.get("arxiv_id") and parsed.get("arxiv_id") in expected_arxiv_ids:
                is_match = True
                match_breakdown["arxiv"] += 1
            else:
                for exp in sample_expected_refs:
                    matched, match_type = is_reference_match(parsed, exp)
                    if matched:
                        is_match = True
                        if "doi" in match_type:
                            match_breakdown["doi"] += 1
                        elif "arxiv" in match_type:
                            match_breakdown["arxiv"] += 1
                        else:
                            match_breakdown["jaccard"] += 1
                        break

            if is_match:
                matched_count += 1
            else:
                match_breakdown["unmatched"] += 1

        total_extracted = len(prediction)
        recall = (total_extracted / expected_count) if expected_count > 0 else 1.0
        recall = min(1.0, recall)
        precision = (matched_count / total_extracted) if total_extracted > 0 else 0.0

        if recall + precision > 0:
            f1 = 2 * (recall * precision) / (recall + precision)
        else:
            f1 = 0.0

        passed = recall >= self.min_recall and precision >= self.min_precision

        return MetricResult(
            name=self.name,
            score=round(f1, 4),
            threshold=round((self.min_recall + self.min_precision) / 2, 4),
            passed=passed,
            details={
                "recall": round(recall, 4),
                "precision": round(precision, 4),
                "f1": round(f1, 4),
                "total_extracted": total_extracted,
                "expected_count": expected_count,
                "matched_count": matched_count,
                "match_breakdown": match_breakdown,
            },
            reasoning=(
                f"Cascading F1: {f1:.1%} (Recall: {recall:.1%}, Precision: {precision:.1%})"
            ),
        )
