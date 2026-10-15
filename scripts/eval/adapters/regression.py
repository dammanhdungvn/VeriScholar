"""Adapter for Project Regression Set (25 golden evaluation test cases)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.eval.adapters.base import BaseDatasetAdapter, EvalSample

DEFAULT_REGRESSION_FILE = (
    Path(__file__).resolve().parent.parent / "data" / "project_regression_25.json"
)


class ProjectRegressionAdapter(BaseDatasetAdapter):
    """Adapter for the 25-case Project Regression Benchmark."""

    def __init__(self, data_path: Path | str | None = None) -> None:
        self.data_path = Path(data_path) if data_path else DEFAULT_REGRESSION_FILE

    @property
    def dataset_name(self) -> str:
        return "project_regression"

    def load_default(self, split: str = "test") -> list[EvalSample]:
        """Load the standard 25 regression cases."""
        return self.load_file(self.data_path, split=split)

    def parse_data(self, raw_data: Any, split: str = "test") -> list[EvalSample]:
        """Parse list of regression test case dictionaries."""
        if not isinstance(raw_data, list):
            return []

        samples: list[EvalSample] = []
        for item in raw_data:
            if not isinstance(item, dict):
                continue
            sample = EvalSample.from_dict(item)
            sample.split = split
            samples.append(sample)
        return samples
