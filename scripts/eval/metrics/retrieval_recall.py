"""Retrieval Recall metric for evaluation harness."""

from __future__ import annotations

import re
from typing import Any

from scripts.eval.metrics.base import BaseEvalMetric, MetricResult


def _tokenize(text: str) -> set[str]:
    """Tokenize text into lowercase alphanumeric word tokens."""
    return set(re.findall(r"\w+", text.lower()))


class RetrievalRecallMetric(BaseEvalMetric):
    """Calculates top-k retrieval recall against ground truth evidence items."""

    def __init__(self, top_k: int = 5, min_token_overlap: float = 0.50, min_recall: float = 0.80):
        self.top_k = top_k
        self.min_token_overlap = min_token_overlap
        self.min_recall = min_recall

    @property
    def name(self) -> str:
        return "retrieval_recall"

    def measure(self, prediction: Any, ground_truth: Any = None, **kwargs: Any) -> MetricResult:
        """Measure retrieval recall.

        prediction: list of retrieved chunk dicts or strings.
        ground_truth: list of ground truth evidence dicts or strings.
        """
        # Parse retrieved items
        retrieved_texts: list[str] = []
        if isinstance(prediction, list):
            for item in prediction[: self.top_k]:
                if isinstance(item, dict):
                    retrieved_texts.append(str(item.get("content") or item.get("text", "")))
                elif isinstance(item, str):
                    retrieved_texts.append(item)
        elif isinstance(prediction, str):
            retrieved_texts = [prediction]

        # Parse ground truth evidence
        gt_evidence: list[str] = []
        if isinstance(ground_truth, list):
            for ev in ground_truth:
                if isinstance(ev, dict):
                    gt_evidence.append(str(ev.get("text") or ev.get("raw") or ""))
                elif isinstance(ev, str):
                    gt_evidence.append(ev)
        elif isinstance(ground_truth, str):
            gt_evidence = [ground_truth]

        # If no ground truth evidence was required (e.g. pure safety or absent info)
        if not gt_evidence:
            return MetricResult(
                name=self.name,
                score=1.0,
                threshold=self.min_recall,
                passed=True,
                details={"gt_count": 0, "retrieved_count": len(retrieved_texts)},
                reasoning="No ground truth evidence required for this sample.",
            )

        matched_gt_count = 0
        error_samples: list[dict[str, Any]] = []

        retrieved_token_sets = [_tokenize(t) for t in retrieved_texts if t.strip()]

        for idx, gt_text in enumerate(gt_evidence):
            gt_tokens = _tokenize(gt_text)
            if not gt_tokens:
                matched_gt_count += 1
                continue

            found = False
            best_overlap = 0.0

            for r_tokens in retrieved_token_sets:
                if not r_tokens:
                    continue
                intersection = len(gt_tokens & r_tokens)
                overlap = intersection / len(gt_tokens)
                if overlap > best_overlap:
                    best_overlap = overlap
                if overlap >= self.min_token_overlap:
                    found = True
                    break

            if found:
                matched_gt_count += 1
            else:
                error_samples.append(
                    {
                        "gt_index": idx,
                        "best_overlap": round(best_overlap, 3),
                        "snippet": gt_text[:100],
                    }
                )

        recall = matched_gt_count / len(gt_evidence)
        passed = recall >= self.min_recall

        return MetricResult(
            name=self.name,
            score=round(recall, 3),
            threshold=self.min_recall,
            passed=passed,
            details={
                "matched_gt_count": matched_gt_count,
                "total_gt_count": len(gt_evidence),
                "top_k": self.top_k,
            },
            error_samples=error_samples,
            reasoning=f"Retrieved {matched_gt_count}/{len(gt_evidence)} ground truth evidence items.",
        )
