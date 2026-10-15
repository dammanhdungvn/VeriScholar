"""Adversarial stress-test harness for evaluation benchmark adapters.

Empirically challenges QASPERAdapter, SciFactAdapter, PubMedQAAdapter, and
ProjectRegressionAdapter across:
1. Edge cases: Empty datasets, malformed JSON, missing fields, questions without evidence,
   unanswerable queries.
2. Coordinate extremes: Bounding boxes touching 0.0, 1.0, single-point boxes, multi-page documents.
3. Label variations: PubMedQA uppercase/lowercase YES/No/Maybe;
   SciFact SUPPORT/CONTRADICT/NOT_ENOUGH_INFO.
4. Serialization: Round-trip EvalSample to_dict and from_dict fidelity.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from core.eval.adapters.base import BaseDatasetAdapter
from core.eval.adapters.pubmedqa import PubMedQAAdapter
from core.eval.adapters.qasper import QASPERAdapter
from core.eval.adapters.regression import ProjectRegressionAdapter
from core.eval.adapters.scifact import SciFactAdapter
from core.eval.metrics.bbox_iou import BoundingBoxIoUMetric, compute_box_iou
from core.eval.metrics.classification import ClassificationMetric
from core.eval.metrics.spatial_geometry import SpatialGeometryMetric
from core.eval.models import EvalSample

# ==============================================================================
# AREA 1: EDGE CASES & ROBUSTNESS
# ==============================================================================


class TestAdapterEdgeCases:
    """Stress tests empty inputs, corrupted JSON, missing fields, and unanswerable queries."""

    @pytest.mark.parametrize(
        "adapter_cls",
        [QASPERAdapter, SciFactAdapter, PubMedQAAdapter, ProjectRegressionAdapter],
    )
    def test_empty_datasets_and_trivial_inputs(self, adapter_cls: type[BaseDatasetAdapter]) -> None:
        """Adapters must return empty list for empty datasets or non-dict/list types."""
        adapter = adapter_cls()
        assert adapter.parse_data([]) == []
        assert adapter.parse_data({}) == []
        assert adapter.parse_data(None) == []
        assert adapter.parse_data("random text") == []
        assert adapter.parse_data(12345) == []

    @pytest.mark.parametrize(
        "adapter_cls",
        [QASPERAdapter, SciFactAdapter, PubMedQAAdapter, ProjectRegressionAdapter],
    )
    def test_empty_and_whitespace_files(
        self, adapter_cls: type[BaseDatasetAdapter], tmp_path: Path
    ) -> None:
        """Loading zero-byte or whitespace-only files returns an empty list without error."""
        adapter = adapter_cls()
        empty_file = tmp_path / "empty.json"
        empty_file.write_text("", encoding="utf-8")
        assert adapter.load_file(empty_file) == []

        whitespace_file = tmp_path / "whitespace.json"
        whitespace_file.write_text("   \n\t  \n  ", encoding="utf-8")
        assert adapter.load_file(whitespace_file) == []

    @pytest.mark.parametrize(
        "adapter_cls",
        [QASPERAdapter, SciFactAdapter, PubMedQAAdapter, ProjectRegressionAdapter],
    )
    def test_nonexistent_file_raises_filenotfound(
        self, adapter_cls: type[BaseDatasetAdapter], tmp_path: Path
    ) -> None:
        """Loading a non-existent file must explicitly raise FileNotFoundError."""
        adapter = adapter_cls()
        with pytest.raises(FileNotFoundError):
            adapter.load_file(tmp_path / "does_not_exist.json")

    def test_malformed_json_file_raises_jsondecodeerror(self, tmp_path: Path) -> None:
        """Truly malformed JSON syntax raises json.JSONDecodeError."""
        adapter = PubMedQAAdapter()
        malformed_file = tmp_path / "corrupted.json"
        malformed_file.write_text("{ unclosed json: [", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            adapter.load_file(malformed_file)

        malformed_jsonl = tmp_path / "corrupted.jsonl"
        malformed_jsonl.write_text('{"valid": 1}\n{broken json\n', encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            adapter.load_file(malformed_jsonl)

    def test_non_dict_elements_in_dataset_list(self) -> None:
        """Non-dict items in raw_data list trigger AttributeError in QASPER and PubMedQA."""
        # SciFact and ProjectRegression gracefully filter out non-dict items
        s_adapter = SciFactAdapter()
        assert s_adapter.parse_data([None, 123, "corrupted"]) == []

        r_adapter = ProjectRegressionAdapter()
        assert r_adapter.parse_data([None, 123, "corrupted"]) == []

        # QASPER and PubMedQA crash with AttributeError because of unguarded list comprehensions
        q_adapter = QASPERAdapter()
        with pytest.raises(AttributeError):
            q_adapter.parse_data([None, 123])

        p_adapter = PubMedQAAdapter()
        with pytest.raises(AttributeError):
            p_adapter.parse_data([None, 123])

    def test_none_valued_fields_injection(self) -> None:
        """Empirically test vulnerability when fields contain explicit None."""
        # QASPER crashes if paper_dict['qas'] is None or qa['answers'] is None
        q_adapter = QASPERAdapter()
        with pytest.raises(TypeError):
            q_adapter.parse_data([{"paper_id": "p1", "title": "T", "qas": None}])

        with pytest.raises(TypeError):
            q_adapter.parse_data(
                {"p1": {"title": "T", "qas": [{"question": "Q?", "answers": None}]}}
            )

        # SciFact crashes if cited_doc_ids is None or sentences is None
        s_adapter = SciFactAdapter()
        with pytest.raises(TypeError):
            s_adapter.parse_data([{"id": "c1", "claim": "text", "cited_doc_ids": None}])

        with pytest.raises(TypeError):
            s_adapter.parse_data(
                [
                    {
                        "id": "c1",
                        "claim": "text",
                        "cited_doc_ids": [],
                        "evidence": {"doc1": [{"sentences": None}]},
                    }
                ]
            )

        # PubMedQA handles None contexts/labels gracefully via `or []`
        p_adapter = PubMedQAAdapter()
        p_samples = p_adapter.parse_data(
            [{"pubid": "p1", "question": "Q?", "contexts": None, "labels": None}]
        )
        assert len(p_samples) == 1
        assert p_samples[0].ground_truth_evidence == []

    def test_qasper_questions_without_evidence_and_unanswerable(self) -> None:
        """QASPER questions with unanswerable=True or missing evidence spans."""
        raw_data = {
            "paper_1": {
                "title": "Quantum Attention",
                "abstract": "Quantum computing meets transformers.",
                "qas": [
                    {
                        "question_id": "q_unanswerable",
                        "question": "What is the quantum fidelity of layer 5?",
                        "answers": [{"answer": {"unanswerable": True}}],
                    },
                    {
                        "question_id": "q_no_evidence",
                        "question": "What is the parameter count?",
                        "answers": [
                            {
                                "answer": {
                                    "unanswerable": False,
                                    "extractive_spans": ["110M parameters"],
                                    "evidence": [],  # No evidence sentences provided
                                }
                            }
                        ],
                    },
                ],
            }
        }
        adapter = QASPERAdapter()
        samples = adapter.parse_data(raw_data, split="dev")
        assert len(samples) == 2

        # Unanswerable query
        s_unans = samples[0]
        assert s_unans.id == "q_unanswerable"
        assert s_unans.ground_truth_answers == []
        assert s_unans.ground_truth_evidence == []
        assert s_unans.metadata["unanswerable"] is True

        # Question without evidence
        s_no_ev = samples[1]
        assert s_no_ev.id == "q_no_evidence"
        assert s_no_ev.ground_truth_answers == ["110M parameters"]
        assert s_no_ev.ground_truth_evidence == []
        assert s_no_ev.ground_truth_bboxes == []
        assert s_no_ev.metadata["unanswerable"] is False

    def test_scifact_claims_without_evidence_defaults_to_not_enough_info(self) -> None:
        """SciFact claim with empty evidence dict defaults to NOT_ENOUGH_INFO."""
        raw_data = [
            {
                "id": 42,
                "claim": "0-field exposure reduces cognitive fatigue.",
                "cited_doc_ids": ["doc_123"],
                "evidence": {},  # No evidence
            }
        ]
        adapter = SciFactAdapter(corpus={"doc_123": {"title": "Doc 123", "abstract": ["Sent 0"]}})
        samples = adapter.parse_data(raw_data, split="test")
        assert len(samples) == 1
        s = samples[0]
        assert s.id == "42"
        assert s.paper_id == "doc_123"
        assert s.paper_title == "Doc 123"
        assert s.ground_truth_answers == ["NOT_ENOUGH_INFO"]
        assert s.ground_truth_evidence == []
        assert s.metadata["has_evidence"] is False
        assert s.metadata["label"] == "NOT_ENOUGH_INFO"

    def test_pubmedqa_questions_without_contexts(self) -> None:
        """PubMedQA sample where contexts and labels are empty lists."""
        raw_data = {
            "pmid_empty_ctx": {
                "QUESTION": "Can diet affect microbiome diversity?",
                "final_decision": "yes",
                "LONG_ANSWER": "Diet strongly influences microbiome diversity.",
                "CONTEXTS": [],
                "LABELS": [],
            }
        }
        adapter = PubMedQAAdapter()
        samples = adapter.parse_data(raw_data, split="dev")
        assert len(samples) == 1
        s = samples[0]
        assert s.id == "pmid_empty_ctx"
        assert s.ground_truth_answers == ["yes"]
        assert s.metadata["long_answer"] == "Diet strongly influences microbiome diversity."
        assert s.ground_truth_evidence == []

    def test_adapter_missing_optional_fields_handling(self) -> None:
        """Adapters handle items with sparse or missing optional fields without crashing."""
        # QASPER missing title/abstract
        q_adapter = QASPERAdapter()
        q_res = q_adapter.parse_data(
            {"p_sparse": {"qas": [{"question": "Valid question?", "answers": []}]}}
        )
        assert len(q_res) == 1
        assert q_res[0].paper_title == ""

        # SciFact missing cited_doc_ids and title
        s_adapter = SciFactAdapter()
        s_res = s_adapter.parse_data([{"claim": "Valid claim text"}])
        assert len(s_res) == 1
        assert s_res[0].paper_id == "unknown"
        assert s_res[0].ground_truth_answers == ["NOT_ENOUGH_INFO"]

        # PubMedQA missing decision and long answer
        p_adapter = PubMedQAAdapter()
        p_res = p_adapter.parse_data([{"question": "Valid medical query?"}])
        assert len(p_res) == 1
        assert p_res[0].ground_truth_answers == []
        assert p_res[0].metadata["final_decision"] == ""


# ==============================================================================
# AREA 2: COORDINATE EXTREMES & SPATIAL BOUNDARIES
# ==============================================================================


class TestAdapterCoordinateExtremes:
    """Stress tests boundary coordinates (0.0, 1.0), single points, and multi-page documents."""

    def test_bounding_boxes_touching_exact_boundaries(self) -> None:
        """Bounding boxes touching 0.0 and 1.0 are parsed accurately across adapters."""
        raw_pubmed = [
            {
                "pubid": "pmid_edge",
                "question": "Is radiotherapy effective?",
                "final_decision": "yes",
                "ground_truth_bboxes": [
                    [0.0, 0.0, 0.5, 0.5, 1],  # Top-left corner
                    [0.5, 0.5, 1.0, 1.0, 1],  # Bottom-right corner
                    [0.0, 0.2, 1.0, 0.8, 2],  # Full width spanning page 2
                ],
            }
        ]
        adapter = PubMedQAAdapter()
        samples = adapter.parse_data(raw_pubmed)
        assert len(samples) == 1
        bboxes = samples[0].ground_truth_bboxes
        assert len(bboxes) == 3
        assert bboxes[0] == [0.0, 0.0, 0.5, 0.5, 1.0]
        assert bboxes[1] == [0.5, 0.5, 1.0, 1.0, 1.0]
        assert bboxes[2] == [0.0, 0.2, 1.0, 0.8, 2.0]

    def test_single_point_and_degenerate_bounding_boxes(self) -> None:
        """Adapters extract degenerate single-point boxes; geometry metric flags them."""
        raw_qasper = {
            "p_degen": {
                "title": "Degenerate Geometry Test",
                "qas": [
                    {
                        "question": "What is the point?",
                        "answers": [
                            {
                                "extractive_spans": ["point"],
                                "evidence": [
                                    {
                                        "section": "Sec 1",
                                        "text": "Single point",
                                        "bbox": [0.5, 0.5, 0.5, 0.5, 1],  # Single point
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        }
        adapter = QASPERAdapter()
        samples = adapter.parse_data(raw_qasper)
        assert len(samples) == 1
        assert samples[0].ground_truth_bboxes == [[0.5, 0.5, 0.5, 0.5, 1.0]]

        # Verify downstream metric behavior: single-point box violates strict ordering (x1 <= x0)
        geom_metric = SpatialGeometryMetric()
        geom_result = geom_metric.measure(prediction=samples[0].ground_truth_bboxes)
        assert geom_result.passed is False
        assert any(e["error"] == "INVERTED_COORDINATES" for e in geom_result.error_samples)

        # IoU on single-point box against identical single-point box evaluates to 0.0 (zero area)
        iou = compute_box_iou([0.5, 0.5, 0.5, 0.5, 1], [0.5, 0.5, 0.5, 0.5, 1])
        assert iou == 0.0

    def test_multi_page_document_coordinate_isolation(self) -> None:
        """Boxes with identical 2D coordinates on different pages must have 0.0 IoU."""
        box_page_1 = [0.1, 0.1, 0.9, 0.5, 1.0]
        box_page_2 = [0.1, 0.1, 0.9, 0.5, 2.0]
        box_page_10 = [0.1, 0.1, 0.9, 0.5, 10.0]

        # Exact match on same page -> 1.0
        assert compute_box_iou(box_page_1, box_page_1) == 1.0

        # Different pages -> strictly 0.0
        assert compute_box_iou(box_page_1, box_page_2) == 0.0
        assert compute_box_iou(box_page_2, box_page_10) == 0.0

        iou_metric = BoundingBoxIoUMetric(min_iou=0.70)
        res = iou_metric.measure(prediction=[box_page_2], ground_truth=[box_page_1])
        assert res.score == 0.0
        assert res.passed is False

    def test_4_element_vs_5_element_bounding_box_compatibility(self) -> None:
        """Adapters parse both 4-element and 5-element bounding boxes."""
        raw_scifact = [
            {
                "id": 1,
                "claim": "Vitamin D improves bone density.",
                "evidence": {
                    "doc_1": [
                        {"label": "SUPPORT", "sentences": [0], "bbox": [0.1, 0.2, 0.8, 0.9]},
                        {"label": "SUPPORT", "sentences": [1], "bbox": [0.1, 0.2, 0.8, 0.9, 3]},
                    ]
                },
            }
        ]
        adapter = SciFactAdapter(corpus={"doc_1": {"abstract": ["S0", "S1"]}})
        samples = adapter.parse_data(raw_scifact)
        assert len(samples) == 1
        bboxes = samples[0].ground_truth_bboxes
        assert len(bboxes) == 2
        # First box has 4 elements preserved
        assert len(bboxes[0]) == 4
        # Second box has 5 elements preserved
        assert len(bboxes[1]) == 5
        assert bboxes[1][4] == 3.0


# ==============================================================================
# AREA 3: LABEL VARIATIONS & NORMALIZATION
# ==============================================================================


class TestAdapterLabelVariations:
    """Stress tests label casing, synonyms, and decision formats."""

    @pytest.mark.parametrize(
        "raw_decision, expected_normalized",
        [
            ("YES", "yes"),
            ("yes", "yes"),
            ("Yes", "yes"),
            ("YEs", "yes"),
            ("  yes  \n", "yes"),
            ("NO", "no"),
            ("no", "no"),
            ("No", "no"),
            ("MAYBE", "maybe"),
            ("maybe", "maybe"),
            ("Maybe", "maybe"),
            ("  MAYBE\t", "maybe"),
        ],
    )
    def test_pubmedqa_label_casing_variations(
        self, raw_decision: str, expected_normalized: str
    ) -> None:
        """PubMedQAAdapter normalizes all variations of YES/NO/MAYBE to lowercase."""
        raw_data = [
            {
                "pubid": "pmid_test",
                "question": "Does aspirin prevent clotting?",
                "final_decision": raw_decision,
            }
        ]
        adapter = PubMedQAAdapter()
        samples = adapter.parse_data(raw_data)
        assert len(samples) == 1
        assert samples[0].ground_truth_answers[0] == expected_normalized
        assert samples[0].metadata["final_decision"] == expected_normalized

        # Downstream metric should match matching prediction regardless of prediction casing
        metric = ClassificationMetric(min_accuracy=0.85)
        decision_variants = [
            expected_normalized.upper(),
            expected_normalized.lower(),
            expected_normalized.capitalize(),
        ]
        for pred_case in decision_variants:
            res = metric.measure(prediction=pred_case, ground_truth=samples[0].ground_truth_answers)
            assert res.passed is True
            assert res.score == 1.0

    @pytest.mark.parametrize(
        "label, expected_gt",
        [
            ("SUPPORT", "SUPPORT"),
            ("CONTRADICT", "CONTRADICT"),
            ("NOT_ENOUGH_INFO", "NOT_ENOUGH_INFO"),
            ("support", "support"),
            ("contradict", "contradict"),
        ],
    )
    def test_scifact_label_variations(self, label: str, expected_gt: str) -> None:
        """SciFactAdapter accurately extracts golden evidence labels."""
        raw_data = [
            {
                "id": 100,
                "claim": "Gene X expression correlates with phenotype Y.",
                "evidence": {
                    "doc_99": [
                        {"label": label, "sentences": [0]},
                    ]
                },
            }
        ]
        adapter = SciFactAdapter(corpus={"doc_99": {"abstract": ["Sentence 0"]}})
        samples = adapter.parse_data(raw_data)
        assert len(samples) == 1
        assert samples[0].ground_truth_answers == [expected_gt]
        assert samples[0].metadata["label"] == expected_gt

        # Downstream classification metric should match via normalize_label
        metric = ClassificationMetric(min_accuracy=0.85)
        res = metric.measure(prediction=label.lower(), ground_truth=[expected_gt])
        assert res.passed is True
        assert res.score == 1.0

    def test_classification_metric_substring_vulnerability(self) -> None:
        """Verify ClassificationMetric substring vulnerability is resolved:

        'no' is NOT an exact or token match for 'not_enough_info', so predicting
        'no' against 'NOT_ENOUGH_INFO' correctly fails.
        """
        metric = ClassificationMetric(min_accuracy=0.85)
        res = metric.measure(prediction="no", ground_truth=["NOT_ENOUGH_INFO"])
        assert res.passed is False
        assert res.score == 0.0
        assert res.details["matched"] is False

    def test_qasper_boolean_answers(self) -> None:
        """QASPERAdapter extracts boolean yes_no as 'Yes' or 'No' string answers."""
        raw_data = {
            "p_bool": {
                "title": "Boolean QA",
                "qas": [
                    {
                        "question": "Is the code open-source?",
                        "answers": [{"answer": {"yes_no": True}}],
                    },
                    {
                        "question": "Was GPU training used?",
                        "answers": [{"answer": {"yes_no": False}}],
                    },
                    {
                        "question": "What is the batch size?",
                        "answers": [{"answer": {"yes_no": None, "free_form_answer": "64"}}],
                    },
                ],
            }
        }
        adapter = QASPERAdapter()
        samples = adapter.parse_data(raw_data)
        assert len(samples) == 3
        assert samples[0].ground_truth_answers == ["Yes"]
        assert samples[1].ground_truth_answers == ["No"]
        assert samples[2].ground_truth_answers == ["64"]


# ==============================================================================
# AREA 4: SERIALIZATION & ROUND-TRIP FIDELITY
# ==============================================================================


class TestEvalSampleSerialization:
    """Stress tests round-trip serialization and field fidelity for EvalSample."""

    def test_eval_sample_full_round_trip_equality(self) -> None:
        """EvalSample to_dict and from_dict round-trip preserves all fields exactly."""
        sample = EvalSample(
            id="q_adversarial_42",
            dataset="project_regression",
            split="test",
            paper_id="attention_is_all_you_need",
            paper_title="Attention Is All You Need",
            query="What is the scaling factor of scaled dot-product attention?",
            ground_truth_answers=["1 / sqrt(d_k)", "sqrt(d_k)"],
            ground_truth_evidence=[
                {
                    "section": "Section 3.2.1",
                    "text": "We divide by sqrt(d_k) to prevent extremely small gradients.",
                    "page": 4,
                }
            ],
            ground_truth_bboxes=[[0.15, 0.35, 0.85, 0.45, 4.0]],
            metadata={
                "category": "formula",
                "difficulty": "hard",
                "verified": True,
                "sub_dict": {"inner_key": 100},
            },
        )

        d = sample.to_dict()
        assert isinstance(d, dict)

        # JSON serialization round trip
        json_str = json.dumps(d)
        loaded_d = json.loads(json_str)

        restored_sample = EvalSample.from_dict(loaded_d)
        assert restored_sample == sample
        assert restored_sample.id == sample.id
        assert restored_sample.dataset == sample.dataset
        assert restored_sample.split == sample.split
        assert restored_sample.paper_id == sample.paper_id
        assert restored_sample.paper_title == sample.paper_title
        assert restored_sample.query == sample.query
        assert restored_sample.ground_truth_answers == sample.ground_truth_answers
        assert restored_sample.ground_truth_evidence == sample.ground_truth_evidence
        assert restored_sample.ground_truth_bboxes == sample.ground_truth_bboxes
        assert restored_sample.metadata == sample.metadata

    def test_eval_sample_serialization_deep_copy_isolation(self) -> None:
        """Mutating the dictionary returned by to_dict does not mutate the source EvalSample."""
        sample = EvalSample(
            id="sample_iso",
            dataset="qasper",
            split="dev",
            paper_id="paper_iso",
            paper_title="Title",
            query="Query?",
            ground_truth_answers=["Answer A"],
            ground_truth_evidence=[{"section": "Intro", "text": "Text"}],
            ground_truth_bboxes=[[0.1, 0.1, 0.9, 0.9, 1.0]],
            metadata={"tag": "initial"},
        )

        d = sample.to_dict()
        d["ground_truth_answers"].append("Answer B")
        d["ground_truth_bboxes"].append([0.2, 0.2, 0.8, 0.8, 2.0])
        d["metadata"]["tag"] = "mutated"

        assert len(sample.ground_truth_answers) == 1
        assert len(sample.ground_truth_bboxes) == 1
        assert sample.metadata["tag"] == "initial"

    def test_eval_sample_from_dict_defaults_on_sparse_input(self) -> None:
        """EvalSample.from_dict applies safe default values for missing fields."""
        sparse_dict: dict[str, Any] = {"id": "sparse_1"}
        s = EvalSample.from_dict(sparse_dict)

        assert s.id == "sparse_1"
        assert s.dataset == "unknown"
        assert s.split == "dev"
        assert s.paper_id == ""
        assert s.paper_title == ""
        assert s.query == ""
        assert s.ground_truth_answers == []
        assert s.ground_truth_evidence == []
        assert s.ground_truth_bboxes == []
        assert s.metadata == {}

    def test_eval_sample_from_dict_none_fields_vulnerability(self) -> None:
        """Document vulnerability: EvalSample.from_dict crashes if list/dict fields are None."""
        with pytest.raises(TypeError):
            EvalSample.from_dict({"id": "1", "ground_truth_answers": None})

        with pytest.raises(TypeError):
            EvalSample.from_dict({"id": "1", "metadata": None})

    def test_eval_sample_from_dict_type_coercion(self) -> None:
        """EvalSample.from_dict coerces non-string identifiers to strings."""
        data = {
            "id": 9999,
            "dataset": "pubmedqa",
            "paper_id": 12345,
            "paper_title": 2026,
            "query": "Is protein X essential?",
        }
        s = EvalSample.from_dict(data)
        assert s.id == "9999"
        assert s.paper_id == "12345"
        assert s.paper_title == "2026"
        assert isinstance(s.id, str)
        assert isinstance(s.paper_id, str)

    def test_pubmedqa_mismatched_context_and_label_lengths(self) -> None:
        """Adversarial probe: zip(contexts, labels) drops contexts when lengths mismatch."""
        raw_data = {
            "pmid_mismatch": {
                "QUESTION": "Is drug X effective?",
                "final_decision": "yes",
                "CONTEXTS": [
                    "Context 1 (Background)",
                    "Context 2 (Methods)",
                    "Context 3 (Results)",
                ],
                "LABELS": ["BACKGROUND"],  # Only 1 label provided for 3 contexts
            }
        }
        adapter = PubMedQAAdapter()
        samples = adapter.parse_data(raw_data)
        assert len(samples) == 1
        # Empirically verify that zip(contexts, labels) truncates to the shorter list (len 1)
        assert len(samples[0].ground_truth_evidence) == 1
        assert samples[0].ground_truth_evidence[0]["section"] == "BACKGROUND"

    def test_scifact_conflicting_evidence_across_documents(self) -> None:
        """Adversarial probe: Multi-doc evidence with conflicting labels resolves to first."""
        raw_data = [
            {
                "id": 55,
                "claim": "Intermittent fasting improves longevity.",
                "evidence": {
                    "doc_positive": [{"label": "SUPPORT", "sentences": [0]}],
                    "doc_negative": [{"label": "CONTRADICT", "sentences": [1]}],
                },
            }
        ]
        adapter = SciFactAdapter(
            corpus={
                "doc_positive": {"abstract": ["Study shows lifespan increase."]},
                "doc_negative": {"abstract": ["Overview", "No significant effect observed."]},
            }
        )
        samples = adapter.parse_data(raw_data)
        assert len(samples) == 1
        s = samples[0]
        # First encountered label becomes primary answer
        assert s.ground_truth_answers == ["SUPPORT"]
        assert s.metadata["label"] == "SUPPORT"
        # But both evidence items are preserved in ground_truth_evidence
        assert len(s.ground_truth_evidence) == 2
        labels_in_evidence = [ev["label"] for ev in s.ground_truth_evidence]
        assert "SUPPORT" in labels_in_evidence
        assert "CONTRADICT" in labels_in_evidence

    def test_qasper_mixed_annotators_unanswerable_and_extractive(self) -> None:
        """Adversarial probe: Multi-annotator QA with both unanswerable and extractive answers."""
        raw_data = {
            "p_mixed": {
                "title": "Mixed Annotators",
                "qas": [
                    {
                        "question_id": "q_mixed",
                        "question": "What is the peak memory usage?",
                        "answers": [
                            {"answer": {"unanswerable": True}},
                            {"answer": {"unanswerable": False, "extractive_spans": ["14.2 GB"]}},
                        ],
                    }
                ],
            }
        }
        adapter = QASPERAdapter()
        samples = adapter.parse_data(raw_data)
        assert len(samples) == 1
        s = samples[0]
        # Metadata reflects unanswerable flag while answers retains extractive span
        assert s.metadata["unanswerable"] is True
        assert s.ground_truth_answers == ["14.2 GB"]
        assert s.metadata["total_annotators"] == 2

    def test_adapter_throughput_linear_scaling(self) -> None:
        """Stress test: verify all 4 adapters parse 1,000 items in < 500ms (O(N) linear time)."""
        import time

        q_adapter = QASPERAdapter()
        s_adapter = SciFactAdapter(corpus={"d1": {"title": "Doc 1", "abstract": ["A", "B"]}})
        p_adapter = PubMedQAAdapter()
        r_adapter = ProjectRegressionAdapter()

        # 1. QASPER 1,000 items
        t0 = time.perf_counter()
        q_data = {
            f"p_{i}": {
                "title": "Paper Title",
                "qas": [
                    {
                        "question": "Query?",
                        "answers": [{"answer": {"extractive_spans": ["Ans"]}}],
                    }
                ],
            }
            for i in range(1000)
        }
        q_res = q_adapter.parse_data(q_data)
        dur_q = time.perf_counter() - t0
        assert len(q_res) == 1000
        assert dur_q < 0.50

        # 2. SciFact 1,000 items
        t0 = time.perf_counter()
        s_data = [
            {
                "id": i,
                "claim": "Claim text",
                "cited_doc_ids": ["d1"],
                "evidence": {"d1": [{"label": "SUPPORT", "sentences": [0]}]},
            }
            for i in range(1000)
        ]
        s_res = s_adapter.parse_data(s_data)
        dur_s = time.perf_counter() - t0
        assert len(s_res) == 1000
        assert dur_s < 0.50

        # 3. PubMedQA 1,000 items
        t0 = time.perf_counter()
        p_data = {
            f"pmid_{i}": {
                "QUESTION": "Question?",
                "final_decision": "yes",
                "CONTEXTS": ["Context text"],
                "LABELS": ["RESULTS"],
            }
            for i in range(1000)
        }
        p_res = p_adapter.parse_data(p_data)
        dur_p = time.perf_counter() - t0
        assert len(p_res) == 1000
        assert dur_p < 0.50

        # 4. Regression 1,000 items
        sample_dict = q_res[0].to_dict()
        t0 = time.perf_counter()
        r_data = [dict(sample_dict, id=f"reg_{i}") for i in range(1000)]
        r_res = r_adapter.parse_data(r_data)
        dur_r = time.perf_counter() - t0
        assert len(r_res) == 1000
        assert dur_r < 0.50
