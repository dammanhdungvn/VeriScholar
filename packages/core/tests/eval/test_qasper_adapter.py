"""Unit tests for QASPERAdapter in core evaluation domain."""

from __future__ import annotations

from pathlib import Path

import pytest
from core.eval.adapters.qasper import QASPERAdapter

FIXTURES_DIR = Path(__file__).parent / "fixtures"
QASPER_FIXTURE = FIXTURES_DIR / "qasper_subset.json"


def test_qasper_adapter_name() -> None:
    adapter = QASPERAdapter()
    assert adapter.dataset_name == "qasper"


def test_qasper_adapter_load_file() -> None:
    adapter = QASPERAdapter()
    samples = adapter.load_file(QASPER_FIXTURE, split="dev")

    assert len(samples) == 4

    # 1. Extractive sample
    s1 = samples[0]
    assert s1.id == "qasper_01_extractive"
    assert s1.dataset == "qasper"
    assert s1.split == "dev"
    assert s1.paper_id == "1706.03762"
    assert s1.paper_title == "Attention Is All You Need"
    assert "N = 6 identical layers" in s1.ground_truth_answers
    assert len(s1.ground_truth_evidence) == 1
    assert s1.ground_truth_evidence[0]["section"] == "3.1 Encoder and Decoder Stacks"
    assert "N = 6 identical layers" in s1.ground_truth_evidence[0]["text"]
    assert len(s1.ground_truth_bboxes) == 1
    assert s1.ground_truth_bboxes[0] == [0.08, 0.25, 0.48, 0.55, 3]
    assert s1.metadata["unanswerable"] is False

    # 2. Abstractive sample
    s2 = samples[1]
    assert s2.id == "qasper_02_abstractive"
    assert any("different representation subspaces" in ans for ans in s2.ground_truth_answers)
    assert s2.metadata["unanswerable"] is False

    # 3. Boolean sample (yes/no)
    s3 = samples[2]
    assert s3.id == "qasper_03_boolean"
    assert "No" in s3.ground_truth_answers

    # 4. Unanswerable sample
    s4 = samples[3]
    assert s4.id == "qasper_04_unanswerable"
    assert s4.metadata["unanswerable"] is True
    assert len(s4.ground_truth_evidence) == 0


def test_qasper_adapter_parse_list_format() -> None:
    raw_list = [
        {
            "paper_id": "test_p1",
            "title": "Test Paper",
            "abstract": "Test Abstract",
            "qas": [
                {
                    "question_id": "q_test",
                    "question": "Is this a test?",
                    "answers": [
                        {
                            "answer": {
                                "yes_no": True,
                                "extractive_spans": ["Yes this is a test"],
                            }
                        }
                    ],
                }
            ],
        }
    ]

    adapter = QASPERAdapter()
    samples = adapter.parse_data(raw_list, split="test")
    assert len(samples) == 1
    assert samples[0].id == "q_test"
    assert "Yes" in samples[0].ground_truth_answers
    assert "Yes this is a test" in samples[0].ground_truth_answers
    assert samples[0].split == "test"


def test_qasper_adapter_empty_and_invalid_inputs(tmp_path: Path) -> None:
    adapter = QASPERAdapter()

    # Non-existent file
    with pytest.raises(FileNotFoundError):
        adapter.load_file(tmp_path / "non_existent.json")

    # Empty file
    empty_file = tmp_path / "empty.json"
    empty_file.write_text("", encoding="utf-8")
    assert adapter.load_file(empty_file) == []

    # Non-dict / non-list input
    assert adapter.parse_data("invalid string") == []
    assert adapter.parse_data(None) == []


def test_qasper_sample_serialization() -> None:
    adapter = QASPERAdapter()
    samples = adapter.load_file(QASPER_FIXTURE, split="dev")
    sample = samples[0]

    d = sample.to_dict()
    assert d["id"] == sample.id
    assert d["dataset"] == "qasper"
    assert d["ground_truth_bboxes"] == [[0.08, 0.25, 0.48, 0.55, 3]]

    restored = sample.from_dict(d)
    assert restored.id == sample.id
    assert restored.ground_truth_answers == sample.ground_truth_answers
    assert restored.ground_truth_bboxes == sample.ground_truth_bboxes
