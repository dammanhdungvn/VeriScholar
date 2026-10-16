"""Token F1 evaluation metric following SQuAD normalization standards."""

from __future__ import annotations

import re
import string
from collections import Counter
from typing import Any

from core.eval.metrics.base import BaseEvalMetric
from core.eval.models import MetricResult


def normalize_answer(s: str) -> str:
    """Normalize text by lowercasing, removing punctuation, articles, and extra whitespace."""

    def remove_articles(text: str) -> str:
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text: str) -> str:
        return " ".join(text.split())

    def remove_punc(text: str) -> str:
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text: str) -> str:
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def compute_token_f1(prediction: str, ground_truth: str) -> tuple[float, float, float]:
    """Calculate token-level precision, recall, and harmonic F1 between two text strings."""
    pred_tokens = normalize_answer(prediction).split()
    gt_tokens = normalize_answer(ground_truth).split()

    if not pred_tokens and not gt_tokens:
        return 1.0, 1.0, 1.0
    if not pred_tokens or not gt_tokens:
        return 0.0, 0.0, 0.0

    common = Counter(pred_tokens) & Counter(gt_tokens)
    num_same = sum(common.values())

    if num_same == 0:
        return 0.0, 0.0, 0.0

    precision = num_same / len(pred_tokens)
    recall = num_same / len(gt_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    return precision, recall, f1


class TokenF1Metric(BaseEvalMetric):
    """Calculates SQuAD-style answer token F1 with lowercase, punctuation, and article stripping."""

    def __init__(self, min_f1: float = 0.70) -> None:
        self.min_f1 = min_f1

    @property
    def name(self) -> str:
        return "token_f1"

    def measure(self, prediction: Any, ground_truth: Any = None, **kwargs: Any) -> MetricResult:
        """Measure token F1 of prediction against ground truth answers.

        prediction: Predicted answer string or dict with 'predicted_answer' / 'response'.
        ground_truth: List of ground truth answer strings, or single string.
        """
        # Extract predicted string
        if isinstance(prediction, dict):
            pred_text = str(
                prediction.get("predicted_answer")
                or prediction.get("response")
                or prediction.get("answer")
                or ""
            )
        else:
            pred_text = str(prediction or "")

        # Extract ground truth strings
        if ground_truth is None:
            gt_answers: list[str] = []
        elif isinstance(ground_truth, list):
            gt_answers = [str(a) for a in ground_truth if a]
        else:
            gt_answers = [str(ground_truth)]

        if not gt_answers:
            # If no ground truth answer required (e.g. unanswerable or absent)
            is_unanswerable = kwargs.get("unanswerable", False)
            if is_unanswerable and (not pred_text.strip() or "unanswerable" in pred_text.lower()):
                return MetricResult(
                    name=self.name,
                    score=1.0,
                    threshold=self.min_f1,
                    passed=True,
                    details={"f1": 1.0, "reason": "unanswerable_matched"},
                    reasoning="Unanswerable question correctly handled.",
                )
            return MetricResult(
                name=self.name,
                score=1.0,
                threshold=self.min_f1,
                passed=True,
                details={"gt_answers_count": 0},
                reasoning="No ground truth answers provided.",
            )

        best_f1 = 0.0
        best_p = 0.0
        best_r = 0.0
        best_gt = ""

        for gt in gt_answers:
            p, r, f1 = compute_token_f1(pred_text, gt)
            if f1 > best_f1:
                best_f1 = f1
                best_p = p
                best_r = r
                best_gt = gt

        passed = best_f1 >= self.min_f1

        return MetricResult(
            name=self.name,
            score=round(best_f1, 4),
            threshold=self.min_f1,
            passed=passed,
            details={
                "f1": round(best_f1, 4),
                "precision": round(best_p, 4),
                "recall": round(best_r, 4),
                "best_ground_truth": best_gt,
                "candidate_count": len(gt_answers),
            },
            reasoning=f"Token F1 {best_f1:.3f} (target threshold: {self.min_f1:.2f}).",
        )
