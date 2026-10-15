"""Base dataset adapter and evaluation sample definitions for Two-Tier Evaluation Suite."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class EvalSample:
    """Unified evaluation sample representation across standard and regression benchmarks."""

    id: str
    dataset: str  # "qasper", "scifact", "project_regression"
    split: str  # "dev", "test", "train"
    paper_id: str
    paper_title: str
    query: str
    ground_truth_answers: list[str] = field(default_factory=list)
    ground_truth_evidence: list[dict[str, Any]] = field(default_factory=list)
    ground_truth_bboxes: list[list[float]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert sample to dictionary."""
        return {
            "id": self.id,
            "dataset": self.dataset,
            "split": self.split,
            "paper_id": self.paper_id,
            "paper_title": self.paper_title,
            "query": self.query,
            "ground_truth_answers": self.ground_truth_answers,
            "ground_truth_evidence": self.ground_truth_evidence,
            "ground_truth_bboxes": self.ground_truth_bboxes,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvalSample:
        """Create sample from dictionary."""
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


class BaseDatasetAdapter(ABC):
    """Abstract interface for benchmark dataset adapters."""

    @property
    @abstractmethod
    def dataset_name(self) -> str:
        """Name of the dataset (e.g. 'qasper', 'scifact')."""
        pass

    @abstractmethod
    def parse_data(self, raw_data: Any, split: str = "dev") -> list[EvalSample]:
        """Parse raw dataset structure into list of unified EvalSample items."""
        pass

    def load_file(self, path: str | Path, split: str = "dev") -> list[EvalSample]:
        """Load and parse dataset from file path (JSON or JSONL)."""
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {file_path}")

        content = file_path.read_text(encoding="utf-8").strip()
        if not content:
            return []

        # Support JSON Lines
        if file_path.suffix.lower() == ".jsonl" or "\n" in content and content.startswith("{"):
            try:
                # Try single JSON first
                raw_data = json.loads(content)
            except json.JSONDecodeError:
                lines = [line.strip() for line in content.splitlines() if line.strip()]
                raw_data = [json.loads(line) for line in lines]
        else:
            raw_data = json.loads(content)

        return self.parse_data(raw_data, split=split)
