"""Core Evaluation Domain models and data structures.

Standardized representations for benchmark samples, evaluation metric outcomes,
and consolidated benchmark reports across QASPER, SciFact, PubMedQA, and Project Regression.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class EvalSample:
    """Standardized benchmark sample across QASPER, SciFact, PubMedQA, and Regression.

    Maintains normalized bounding box coordinates [x0, y0, x1, y1, page] where
    page >= 1, 0.0 <= x0 < x1 <= 1.0, 0.0 <= y0 < y1 <= 1.0, with Top-Left origin.
    """

    id: str
    dataset: Literal["qasper", "scifact", "pubmedqa", "project_regression"] | str
    split: str  # "train", "dev", "test"
    paper_id: str
    paper_title: str
    query: str
    ground_truth_answers: list[str] = field(default_factory=list)
    ground_truth_evidence: list[dict[str, Any]] = field(default_factory=list)
    ground_truth_bboxes: list[list[float]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize evaluation sample to dictionary."""
        return {
            "id": self.id,
            "dataset": self.dataset,
            "split": self.split,
            "paper_id": self.paper_id,
            "paper_title": self.paper_title,
            "query": self.query,
            "ground_truth_answers": list(self.ground_truth_answers),
            "ground_truth_evidence": list(self.ground_truth_evidence),
            "ground_truth_bboxes": [list(b) for b in self.ground_truth_bboxes],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvalSample:
        """Construct evaluation sample from dictionary."""
        return cls(
            id=str(data.get("id", "")),
            dataset=str(data.get("dataset", "unknown")),
            split=str(data.get("split", "dev")),
            paper_id=str(data.get("paper_id", "")),
            paper_title=str(data.get("paper_title", "")),
            query=str(data.get("query", "")),
            ground_truth_answers=list(data.get("ground_truth_answers", [])),
            ground_truth_evidence=list(data.get("ground_truth_evidence", [])),
            ground_truth_bboxes=list(data.get("ground_truth_bboxes", [])),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass(frozen=True)
class MetricResult:
    """Outcome of an individual evaluation metric check."""

    name: str
    score: float  # Normalized score between 0.0 and 1.0
    threshold: float  # SLA pass/fail cutoff
    passed: bool
    details: dict[str, Any] = field(default_factory=dict)
    error_samples: list[dict[str, Any]] = field(default_factory=list)
    reasoning: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize metric result to dictionary."""
        return {
            "name": self.name,
            "score": self.score,
            "threshold": self.threshold,
            "passed": self.passed,
            "details": dict(self.details),
            "error_samples": list(self.error_samples),
            "reasoning": self.reasoning,
        }


@dataclass
class EvalPrediction:
    """Prediction outcome generated for a given evaluation sample."""

    sample_id: str
    predicted_answer: str = ""
    retrieved_chunks: list[dict[str, Any]] = field(default_factory=list)
    predicted_bboxes: list[list[float]] = field(default_factory=list)
    predicted_label: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize prediction to dictionary."""
        return {
            "sample_id": self.sample_id,
            "predicted_answer": self.predicted_answer,
            "retrieved_chunks": list(self.retrieved_chunks),
            "predicted_bboxes": [list(b) for b in self.predicted_bboxes],
            "predicted_label": self.predicted_label,
            "metadata": dict(self.metadata),
        }


@dataclass
class BenchmarkReport:
    """Consolidated scorecard across an evaluation benchmark run."""

    benchmark_name: str
    total_samples: int
    passed_samples: int
    pass_rate: float
    metric_averages: dict[str, float] = field(default_factory=dict)
    group_breakdown: dict[str, dict[str, Any]] = field(default_factory=dict)
    all_passed: bool = False
    details: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize benchmark report to dictionary."""
        return {
            "benchmark_name": self.benchmark_name,
            "total_samples": self.total_samples,
            "passed_samples": self.passed_samples,
            "pass_rate": self.pass_rate,
            "metric_averages": dict(self.metric_averages),
            "group_breakdown": dict(self.group_breakdown),
            "all_passed": self.all_passed,
            "details": list(self.details),
        }
