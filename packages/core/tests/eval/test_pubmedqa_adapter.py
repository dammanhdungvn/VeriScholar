"""Unit tests for PubMedQAAdapter in core evaluation domain."""

from __future__ import annotations

from pathlib import Path

import pytest
from core.eval.adapters.pubmedqa import PubMedQAAdapter

FIXTURES_DIR = Path(__file__).parent / "fixtures"
PUBMEDQA_FIXTURE = FIXTURES_DIR / "pubmedqa_subset.json"


def test_pubmedqa_adapter_name() -> None:
    adapter = PubMedQAAdapter()
    assert adapter.dataset_name == "pubmedqa"


def test_pubmedqa_adapter_load_file() -> None:
    adapter = PubMedQAAdapter()
    samples = adapter.load_file(PUBMEDQA_FIXTURE, split="dev")

    assert len(samples) == 3

    # Sample 1: "yes" decision
    s1 = samples[0]
    assert s1.id == "21645374"
    assert s1.dataset == "pubmedqa"
    assert s1.split == "dev"
    assert s1.paper_id == "21645374"
    assert "Do statins reduce all-cause mortality" in s1.query
    assert s1.ground_truth_answers == ["yes"]
    assert len(s1.ground_truth_evidence) == 3
    assert s1.ground_truth_evidence[0]["section"] == "BACKGROUND"
    assert s1.ground_truth_evidence[1]["section"] == "METHODS"
    assert s1.ground_truth_evidence[2]["section"] == "RESULTS"
    assert s1.metadata["final_decision"] == "yes"
    assert "significantly reduces" in s1.metadata["long_answer"]
    assert "Mortality" in s1.metadata["meshes"]
    assert s1.metadata["year"] == "2011"
    assert s1.ground_truth_bboxes == [[0.1, 0.1, 0.9, 0.35, 1.0]]

    # Sample 2: "no" decision
    s2 = samples[1]
    assert s2.id == "22341908"
    assert s2.ground_truth_answers == ["no"]
    assert s2.metadata["final_decision"] == "no"
    assert s2.metadata["year"] == "2012"
    assert s2.ground_truth_bboxes == [[0.1, 0.4, 0.9, 0.65, 2.0]]

    # Sample 3: "maybe" decision
    s3 = samples[2]
    assert s3.id == "23456789"
    assert s3.ground_truth_answers == ["maybe"]
    assert s3.metadata["final_decision"] == "maybe"
    assert s3.ground_truth_bboxes == [[0.1, 0.65, 0.9, 0.9, 1.0]]


def test_pubmedqa_adapter_list_format() -> None:
    raw_list = [
        {
            "pubid": "pmid_999",
            "question": "Is exercise beneficial for heart health?",
            "final_decision": "yes",
            "long_answer": "Yes, exercise clearly improves cardiovascular outcomes.",
            "contexts": ["Context text"],
            "labels": ["BACKGROUND"],
        }
    ]

    adapter = PubMedQAAdapter()
    samples = adapter.parse_data(raw_list, split="train")
    assert len(samples) == 1
    assert samples[0].id == "pmid_999"
    assert samples[0].split == "train"
    assert samples[0].ground_truth_answers == ["yes"]
    assert samples[0].metadata["final_decision"] == "yes"
    expected_long = "Yes, exercise clearly improves cardiovascular outcomes."
    assert samples[0].metadata["long_answer"] == expected_long


def test_pubmedqa_adapter_empty_and_error_handling(tmp_path: Path) -> None:
    adapter = PubMedQAAdapter()

    # Missing file
    with pytest.raises(FileNotFoundError):
        adapter.load_file(tmp_path / "missing_pubmedqa.json")

    # Empty data
    assert adapter.parse_data({}) == []
    assert adapter.parse_data([]) == []
    assert adapter.parse_data("bad input") == []


def test_pubmedqa_opposite_decision_mismatch_with_long_answer_in_text() -> None:
    long_ans = "There was no difference observed between the treated and untreated cohorts."
    raw = {
        "pmid_test": {
            "QUESTION": "Is drug X effective?",
            "final_decision": "yes",
            "LONG_ANSWER": long_ans,
        }
    }
    adapter = PubMedQAAdapter()
    sample = adapter.parse_data(raw)[0]

    assert sample.ground_truth_answers == ["yes"]
    assert sample.metadata["long_answer"] == long_ans

    from core.eval.metrics.classification import ClassificationMetric

    metric = ClassificationMetric()
    res = metric.measure(prediction="no", ground_truth=sample.ground_truth_answers)
    assert res.passed is False
    assert res.score == 0.0
