"""Classification evaluation metric for categorical decision benchmarks.

Computes decision accuracy and Macro F1 for SciFact and PubMedQA.
"""

from __future__ import annotations

from typing import Any

from core.eval.metrics.base import BaseEvalMetric
from core.eval.models import MetricResult


def normalize_label(label: str) -> str:
    """Normalize categorical label string."""
    return label.strip(" .\t\n\r!?;:,").lower().replace("-", "_").replace(" ", "_")


def compute_macro_f1(
    predictions: list[str],
    ground_truths: list[str],
    classes: list[str] | None = None,
) -> tuple[float, float, dict[str, float]]:
    """Compute overall accuracy, macro F1, and per-class F1 scores.

    Args:
        predictions: List of predicted class label strings.
        ground_truths: List of golden ground truth class label strings.
        classes: Explicit class list. If None, inferred from unique ground truth labels.

    Returns:
        tuple of (accuracy, macro_f1, per_class_f1_dict)
    """
    if not ground_truths:
        return 1.0, 1.0, {}

    norm_preds = [normalize_label(p) for p in predictions]
    norm_gts = [normalize_label(g) for g in ground_truths]

    if classes is None:
        target_classes = sorted(list(set(norm_gts) | set(norm_preds)))
    else:
        target_classes = [normalize_label(c) for c in classes]

    correct = sum(1 for p, g in zip(norm_preds, norm_gts) if p == g)
    accuracy = correct / len(ground_truths) if ground_truths else 0.0

    class_f1s: dict[str, float] = {}
    for cls in target_classes:
        tp = sum(1 for p, g in zip(norm_preds, norm_gts) if p == cls and g == cls)
        fp = sum(1 for p, g in zip(norm_preds, norm_gts) if p == cls and g != cls)
        fn = sum(1 for p, g in zip(norm_preds, norm_gts) if p != cls and g == cls)

        if tp + fp == 0 and tp + fn == 0:
            # Class not present in predictions or ground truths
            class_f1s[cls] = 1.0
            continue

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        class_f1s[cls] = f1

    macro_f1 = sum(class_f1s.values()) / len(class_f1s) if class_f1s else 0.0
    return accuracy, macro_f1, class_f1s


class ClassificationMetric(BaseEvalMetric):
    """Measures classification accuracy and decision correctness for categorical tasks."""

    def __init__(self, min_accuracy: float = 0.85, valid_classes: list[str] | None = None) -> None:
        self.min_accuracy = min_accuracy
        self.valid_classes = [normalize_label(c) for c in valid_classes] if valid_classes else None

    @property
    def name(self) -> str:
        return "classification"

    def measure(self, prediction: Any, ground_truth: Any = None, **kwargs: Any) -> MetricResult:
        """Measure categorical decision accuracy for an individual sample or batch.

        prediction: string label or dict with 'predicted_label' / 'decision'.
        ground_truth: string label or list of acceptable labels.
        """
        if isinstance(prediction, dict):
            pred_label = str(
                prediction.get("predicted_label")
                or prediction.get("decision")
                or prediction.get("label")
                or prediction.get("response")
                or ""
            )
        else:
            pred_label = str(prediction or "")

        norm_pred = normalize_label(pred_label)

        # Ground truth resolution
        acceptable_gts: list[str] = []
        if isinstance(ground_truth, list):
            acceptable_gts = [normalize_label(str(g)) for g in ground_truth if g]
        elif ground_truth is not None:
            acceptable_gts = [normalize_label(str(ground_truth))]

        # If metadata has final_decision or label
        meta = kwargs.get("metadata", {})
        if not acceptable_gts and isinstance(meta, dict):
            if meta.get("final_decision"):
                acceptable_gts.append(normalize_label(str(meta["final_decision"])))
            elif meta.get("label"):
                acceptable_gts.append(normalize_label(str(meta["label"])))

        if not acceptable_gts:
            return MetricResult(
                name=self.name,
                score=1.0,
                threshold=self.min_accuracy,
                passed=True,
                details={"pred_label": norm_pred},
                reasoning="No categorical ground truth label required.",
            )

        # Reject empty or None predictions
        if not norm_pred:
            return MetricResult(
                name=self.name,
                score=0.0,
                threshold=self.min_accuracy,
                passed=False,
                details={
                    "predicted_label": norm_pred,
                    "expected_labels": acceptable_gts,
                    "matched": False,
                },
                reasoning="Empty or missing prediction rejected.",
            )

        # Check match against acceptable ground truths using exact matching or token set equality
        def _match_label(p: str, g: str) -> bool:
            if not p or not g:
                return False
            if p == g:
                return True
            p_tokens = set(w for w in p.split("_") if w)
            g_tokens = set(w for w in g.split("_") if w)
            return bool(p_tokens and p_tokens == g_tokens)

        matched = any(_match_label(norm_pred, gt) for gt in acceptable_gts)
        score = 1.0 if matched else 0.0
        passed = score >= self.min_accuracy

        return MetricResult(
            name=self.name,
            score=score,
            threshold=self.min_accuracy,
            passed=passed,
            details={
                "predicted_label": norm_pred,
                "expected_labels": acceptable_gts,
                "matched": matched,
            },
            reasoning=(
                f"Classification match: '{norm_pred}' in {acceptable_gts}."
                if matched
                else (
                    f"Classification mismatch: expected one of {acceptable_gts}, got '{norm_pred}'."
                )
            ),
        )
