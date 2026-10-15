"""Base evaluation metric protocol and abstract class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from core.eval.models import MetricResult


class BaseEvalMetric(ABC):
    """Abstract interface for pluggable evaluation metrics."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the evaluation metric."""
        pass

    @abstractmethod
    def measure(self, prediction: Any, ground_truth: Any = None, **kwargs: Any) -> MetricResult:
        """Execute evaluation measurement on prediction against optional ground truth.

        Args:
            prediction: System prediction (text string, list of boxes, list of chunks, dict, etc.)
            ground_truth: Ground truth reference data from EvalSample.
            **kwargs: Additional parameters (e.g. metadata, sample context).

        Returns:
            MetricResult: Evaluation verdict containing score, threshold, pass/fail status,
                details, and error samples.
        """
        pass
