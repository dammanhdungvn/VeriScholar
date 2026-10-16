"""Unit tests for ProjectRegressionAdapter in core evaluation domain."""

from __future__ import annotations

from pathlib import Path

import pytest
from core.eval.adapters.regression import ProjectRegressionAdapter

FIXTURES_DIR = Path(__file__).parent / "fixtures"
REGRESSION_FIXTURE = FIXTURES_DIR / "regression_subset.json"


def test_regression_adapter_name() -> None:
    adapter = ProjectRegressionAdapter()
    assert adapter.dataset_name == "project_regression"


def test_regression_adapter_load_file() -> None:
    adapter = ProjectRegressionAdapter()
    samples = adapter.load_file(REGRESSION_FIXTURE, split="test")

    assert len(samples) == 5

    # Check structural integrity and coordinate invariants
    for s in samples:
        assert s.id.startswith("REG-")
        assert s.dataset == "project_regression"
        assert s.split == "test"
        assert len(s.query) > 5

        for bbox in s.ground_truth_bboxes:
            assert len(bbox) >= 4
            x0, y0, x1, y1 = bbox[:4]
            assert 0.0 <= x0 < x1 <= 1.0
            assert 0.0 <= y0 < y1 <= 1.0
            if len(bbox) > 4:
                page = int(bbox[4])
                assert page >= 1

    # Check sample 1 (fact extraction)
    s1 = samples[0]
    assert s1.id == "REG-01"
    assert s1.metadata["capability_group"] == "fact_extraction"
    assert "Encoder gồm N = 6 layers giống hệt nhau." in s1.ground_truth_answers

    # Check sample 5 (safety prompt injection)
    s5 = samples[4]
    assert s5.id == "REG-21"
    assert s5.metadata["capability_group"] == "multi_tenant_safety"
    assert s5.metadata["expected_guardrail_code"] == "SYSTEM_OVERRIDE"


def test_regression_adapter_load_default() -> None:
    adapter = ProjectRegressionAdapter(data_path=REGRESSION_FIXTURE)
    samples = adapter.load_default()
    assert len(samples) == 5


def test_regression_adapter_load_default_without_path_raises() -> None:
    adapter = ProjectRegressionAdapter()
    with pytest.raises(ValueError, match="No data_path provided"):
        adapter.load_default()


def test_regression_adapter_empty_inputs(tmp_path: Path) -> None:
    adapter = ProjectRegressionAdapter()

    # Non-existent file
    with pytest.raises(FileNotFoundError):
        adapter.load_file(tmp_path / "missing.json")

    # Empty data
    assert adapter.parse_data([]) == []
    assert adapter.parse_data(None) == []
