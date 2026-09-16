"""Base metric protocol and result structures for API Evaluation Harness."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MetricResult:
    """Result of an individual evaluation metric check."""

    name: str
    score: float  # Normalized score between 0.0 and 1.0
    threshold: float  # Required threshold
    passed: bool
    details: dict[str, Any] = field(default_factory=dict)
    error_samples: list[dict[str, Any]] = field(default_factory=list)
    reasoning: str = ""


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

        Returns:
            MetricResult: Evaluation verdict with normalized score and anomaly samples.
        """
        pass
