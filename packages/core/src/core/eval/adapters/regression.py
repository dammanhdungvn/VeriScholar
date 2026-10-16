"""Adapter for Project Regression Set (25 golden evaluation test cases)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.eval.adapters.base import BaseDatasetAdapter
from core.eval.models import EvalSample


class ProjectRegressionAdapter(BaseDatasetAdapter):
    """Adapter for the 25-case Project Regression Benchmark."""

    def __init__(self, data_path: Path | str | None = None) -> None:
        self.data_path = Path(data_path) if data_path else None

    @property
    def dataset_name(self) -> str:
        return "project_regression"

    def load_default(self) -> list[EvalSample]:
        """Load the standard regression dataset from configured data path."""
        if not self.data_path:
            raise ValueError("No data_path provided for ProjectRegressionAdapter.")
        return self.load_file(self.data_path, split="test")

    def parse_data(self, raw_data: Any, split: str = "test") -> list[EvalSample]:
        """Parse list of regression test case dictionaries into EvalSample instances."""
        if not isinstance(raw_data, list):
            return []

        samples: list[EvalSample] = []
        for item in raw_data:
            if not isinstance(item, dict):
                continue
            sample = EvalSample.from_dict(item)
            if split:
                sample.split = split
            samples.append(sample)
        return samples
