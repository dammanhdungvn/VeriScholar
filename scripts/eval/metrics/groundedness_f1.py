"""Groundedness F1 metric for evaluation harness."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from scripts.eval.metrics.base import BaseEvalMetric, MetricResult


def _get_tokens(text: str) -> list[str]:
    """Tokenize string into lowercase alphanumeric words."""
    return re.findall(r"\w+", text.lower())


class GroundednessF1Metric(BaseEvalMetric):
    """Calculates token-level precision, recall, and F1 between generated response and ground truth evidence."""

    def __init__(self, min_f1: float = 0.70):
        self.min_f1 = min_f1

    @property
    def name(self) -> str:
        return "groundedness_f1"

    def measure(self, prediction: Any, ground_truth: Any = None, **kwargs: Any) -> MetricResult:
        """Measure token-level groundedness F1.

        prediction: string response from model or dict with 'text'/'response'.
        ground_truth: list of ground truth evidence/answer strings or dicts.
        """
        pred_text = ""
        if isinstance(prediction, dict):
            pred_text = str(
                prediction.get("response")
                or prediction.get("text")
                or prediction.get("content", "")
            )
        elif isinstance(prediction, str):
            pred_text = prediction

        gt_texts: list[str] = []
        if isinstance(ground_truth, list):
            for item in ground_truth:
                if isinstance(item, dict):
                    gt_texts.append(str(item.get("text") or item.get("raw") or ""))
                elif isinstance(item, str):
                    gt_texts.append(item)
        elif isinstance(ground_truth, str):
            gt_texts = [ground_truth]

        gt_combined = " ".join(gt_texts).strip()

        if not gt_combined:
            # If no ground truth text is required (e.g. prompt injection block)
            return MetricResult(
                name=self.name,
                score=1.0,
                threshold=self.min_f1,
                passed=True,
                details={"gt_tokens": 0},
                reasoning="No ground truth text required for groundedness.",
            )

        pred_tokens = _get_tokens(pred_text)
        gt_tokens = _get_tokens(gt_combined)

        if not pred_tokens or not gt_tokens:
            return MetricResult(
                name=self.name,
                score=0.0,
                threshold=self.min_f1,
                passed=False,
                details={"pred_tokens": len(pred_tokens), "gt_tokens": len(gt_tokens)},
                reasoning="Prediction or ground truth has zero tokens.",
            )

        pred_counter = Counter(pred_tokens)
        gt_counter = Counter(gt_tokens)

        common_tokens = pred_counter & gt_counter
        intersection = sum(common_tokens.values())

        if intersection == 0:
            return MetricResult(
                name=self.name,
                score=0.0,
                threshold=self.min_f1,
                passed=False,
                details={"precision": 0.0, "recall": 0.0, "f1": 0.0},
                reasoning="Zero common tokens between prediction and ground truth.",
            )

        precision = intersection / len(pred_tokens)
        recall = intersection / len(gt_tokens)
        f1 = (2 * precision * recall) / (precision + recall)

        passed = f1 >= self.min_f1

        return MetricResult(
            name=self.name,
            score=round(f1, 3),
            threshold=self.min_f1,
            passed=passed,
            details={
                "precision": round(precision, 3),
                "recall": round(recall, 3),
                "f1": round(f1, 3),
                "pred_tokens_count": len(pred_tokens),
                "gt_tokens_count": len(gt_tokens),
            },
            reasoning=f"Groundedness F1 score: {f1:.3f} (P={precision:.3f}, R={recall:.3f}).",
        )
