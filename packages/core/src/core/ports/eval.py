"""Evaluation Port Protocols.

Defines the abstract contracts for benchmark dataset adapters, evaluation metrics,
and benchmark evaluators in compliance with Hexagonal Architecture.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from core.eval.models import BenchmarkReport, EvalSample, MetricResult


@runtime_checkable
class IDatasetAdapter(Protocol):
    """Protocol for benchmark dataset adapters (QASPER, SciFact, PubMedQA, Regression)."""

    @property
    def dataset_name(self) -> str:
        """Dataset name identifier (e.g. 'qasper', 'scifact', 'pubmedqa', 'regression')."""
        ...

    def parse_data(self, raw_data: Any, split: str = "dev") -> list[EvalSample]:
        """Convert raw dict or list structure into list of unified EvalSample items."""
        ...

    def load_file(self, path: str | Path, split: str = "dev") -> list[EvalSample]:
        """Load and parse dataset from file path (JSON or JSONL)."""
        ...


@runtime_checkable
class IEvalMetric(Protocol):
    """Protocol for pluggable evaluation metric evaluators."""

    @property
    def name(self) -> str:
        """Name of the evaluation metric."""
        ...

    def measure(self, prediction: Any, ground_truth: Any = None, **kwargs: Any) -> MetricResult:
        """Execute evaluation measurement on prediction against optional ground truth."""
        ...


@runtime_checkable
class IBenchmarkEvaluator(Protocol):
    """Protocol for benchmark runners and evaluators orchestrating metrics over sample sets."""

    def evaluate(
        self,
        samples: list[EvalSample],
        **kwargs: Any,
    ) -> BenchmarkReport:
        """Run evaluation across a collection of samples and generate a BenchmarkReport."""
        ...
