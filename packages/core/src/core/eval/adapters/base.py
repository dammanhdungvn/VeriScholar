"""Abstract base dataset adapter for evaluation benchmarks."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from core.eval.models import EvalSample


class BaseDatasetAdapter(ABC):
    """Abstract base class for benchmark dataset adapters."""

    @property
    @abstractmethod
    def dataset_name(self) -> str:
        """Name of the dataset (e.g. 'qasper', 'scifact', 'pubmedqa', 'project_regression')."""
        pass

    @abstractmethod
    def parse_data(self, raw_data: Any, split: str = "dev") -> list[EvalSample]:
        """Parse raw dataset structure into list of unified EvalSample items."""
        pass

    def load_file(self, path: str | Path, split: str = "dev") -> list[EvalSample]:
        """Load and parse dataset from file path (JSON or JSONL).

        Supports JSON dicts, JSON arrays, and line-delimited JSONL formats.
        """
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {file_path}")

        content = file_path.read_text(encoding="utf-8").strip()
        if not content:
            return []

        # If file extension is .jsonl or multi-line with multiple JSON objects
        if file_path.suffix.lower() == ".jsonl":
            lines = [line.strip() for line in content.splitlines() if line.strip()]
            raw_data = [json.loads(line) for line in lines]
        else:
            try:
                raw_data = json.loads(content)
            except json.JSONDecodeError:
                lines = [line.strip() for line in content.splitlines() if line.strip()]
                raw_data = [json.loads(line) for line in lines]

        return self.parse_data(raw_data, split=split)
