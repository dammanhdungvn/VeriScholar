"""Unit tests for SciFactAdapter in core evaluation domain."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from core.eval.adapters.scifact import SciFactAdapter

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SCIFACT_FIXTURE = FIXTURES_DIR / "scifact_subset.json"


def test_scifact_adapter_name() -> None:
    adapter = SciFactAdapter()
    assert adapter.dataset_name == "scifact"


def test_scifact_adapter_load_file_with_corpus(tmp_path: Path) -> None:
    corpus_dict = {
        "12345": {
            "title": "LoRA: Low-Rank Adaptation of Large Language Models",
            "abstract": [
                "Sentence 0: Recurrent architectures like LSTMs are sequence-aligned.",
                (
                    "Sentence 1: LoRA freezes pre-trained weights and injects trainable "
                    "rank decomposition matrices."
                ),
                (
                    "Sentence 2: This reduces the number of trainable parameters by up to "
                    "10,000 times."
                ),
            ],
        }
    }

    corpus_file = tmp_path / "corpus.jsonl"
    corpus_file.write_text(
        json.dumps({"doc_id": 12345, **corpus_dict["12345"]}) + "\n",
        encoding="utf-8",
    )

    adapter = SciFactAdapter()
    adapter.load_corpus(corpus_file)
    samples = adapter.load_file(SCIFACT_FIXTURE, split="test")

    assert len(samples) == 3

    # Claim 1: SUPPORT
    s1 = samples[0]
    assert s1.id == "101"
    assert s1.dataset == "scifact"
    assert s1.split == "test"
    assert s1.ground_truth_answers == ["SUPPORT"]
    assert s1.paper_title == "LoRA: Low-Rank Adaptation of Large Language Models"
    assert len(s1.ground_truth_evidence) == 1
    assert "reduces the number of trainable parameters" in s1.ground_truth_evidence[0]["text"]
    assert s1.ground_truth_bboxes == [[0.1, 0.2, 0.9, 0.4, 1.0]]
    assert s1.metadata["has_evidence"] is True

    # Claim 2: CONTRADICT
    s2 = samples[1]
    assert s2.id == "102"
    assert s2.ground_truth_answers == ["CONTRADICT"]
    assert len(s2.ground_truth_evidence) == 1
    assert "Recurrent architectures like LSTMs" in s2.ground_truth_evidence[0]["text"]

    # Claim 3: NOT_ENOUGH_INFO
    s3 = samples[2]
    assert s3.id == "103"
    assert s3.ground_truth_answers == ["NOT_ENOUGH_INFO"]
    assert len(s3.ground_truth_evidence) == 0
    assert s3.metadata["has_evidence"] is False


def test_scifact_adapter_corpus_constructor() -> None:
    corpus = {
        "doc_A": {
            "title": "Paper A",
            "abstract": ["Sentence zero.", "Sentence one."],
        }
    }
    adapter = SciFactAdapter(corpus=corpus)
    claims = [
        {
            "id": "c1",
            "claim": "Claim A",
            "evidence": {"doc_A": [{"sentences": [1], "label": "SUPPORT"}]},
            "cited_doc_ids": ["doc_A"],
        }
    ]
    samples = adapter.parse_data(claims)
    assert len(samples) == 1
    assert samples[0].paper_title == "Paper A"
    assert samples[0].ground_truth_evidence[0]["text"] == "Sentence one."


def test_scifact_adapter_empty_and_error_handling(tmp_path: Path) -> None:
    adapter = SciFactAdapter()

    # Missing corpus file
    with pytest.raises(FileNotFoundError):
        adapter.load_corpus(tmp_path / "missing_corpus.json")

    # Missing claims file
    with pytest.raises(FileNotFoundError):
        adapter.load_file(tmp_path / "missing_claims.json")

    # Empty data
    assert adapter.parse_data([]) == []
    assert adapter.parse_data(None) == []
