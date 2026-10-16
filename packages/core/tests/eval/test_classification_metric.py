"""Unit tests for ClassificationMetric in core evaluation domain."""

from __future__ import annotations

from core.eval.metrics.classification import (
    ClassificationMetric,
    compute_macro_f1,
    normalize_label,
)


def test_normalize_label() -> None:
    assert normalize_label(" SUPPORT ") == "support"
    assert normalize_label("NOT-ENOUGH-INFO") == "not_enough_info"
    assert normalize_label("Maybe") == "maybe"


def test_compute_macro_f1_balanced() -> None:
    preds = ["support", "contradict", "not_enough_info", "support"]
    gts = ["support", "contradict", "not_enough_info", "contradict"]

    acc, macro_f1, per_class = compute_macro_f1(preds, gts)

    # 3 of 4 correct -> acc = 0.75
    assert acc == 0.75
    assert "support" in per_class
    assert "contradict" in per_class
    assert "not_enough_info" in per_class
    assert per_class["not_enough_info"] == 1.0  # 1 TP, 0 FP, 0 FN -> F1 = 1.0
    assert 0.0 < macro_f1 <= 1.0


def test_classification_metric_scifact_labels() -> None:
    metric = ClassificationMetric(min_accuracy=0.85)

    # Correct SUPPORT
    res_support = metric.measure("SUPPORT", ["SUPPORT"])
    assert res_support.passed is True
    assert res_support.score == 1.0

    # Dict input with predicted_label
    res_dict = metric.measure({"predicted_label": "CONTRADICT"}, ["CONTRADICT"])
    assert res_dict.passed is True
    assert res_dict.score == 1.0

    # Mismatch
    res_mismatch = metric.measure("SUPPORT", ["CONTRADICT"])
    assert res_mismatch.passed is False
    assert res_mismatch.score == 0.0


def test_classification_metric_pubmedqa_decisions() -> None:
    metric = ClassificationMetric(min_accuracy=0.85)

    # Correct decision
    res_yes = metric.measure("yes", ["yes"])
    assert res_yes.passed is True
    assert res_yes.score == 1.0

    # Decision from metadata fallback
    res_meta = metric.measure("no", None, metadata={"final_decision": "no"})
    assert res_meta.passed is True
    assert res_meta.score == 1.0

    # Maybe mismatch with yes
    res_maybe = metric.measure("maybe", ["yes"])
    assert res_maybe.passed is False
    assert res_maybe.score == 0.0


def test_classification_metric_no_ground_truth() -> None:
    metric = ClassificationMetric()
    res = metric.measure("yes", [])
    assert res.passed is True
    assert res.score == 1.0


def test_classification_metric_empty_or_none_prediction_rejected() -> None:
    metric = ClassificationMetric(min_accuracy=0.85)

    res_empty_str = metric.measure("", ["SUPPORT"])
    assert res_empty_str.passed is False
    assert res_empty_str.score == 0.0
    assert res_empty_str.details["matched"] is False

    res_whitespace = metric.measure("   ", ["SUPPORT"])
    assert res_whitespace.passed is False
    assert res_whitespace.score == 0.0

    res_none = metric.measure(None, ["SUPPORT"])
    assert res_none.passed is False
    assert res_none.score == 0.0

    res_dict_empty = metric.measure({"predicted_label": ""}, ["SUPPORT"])
    assert res_dict_empty.passed is False
    assert res_dict_empty.score == 0.0


def test_classification_metric_no_does_not_match_not_enough_info() -> None:
    metric = ClassificationMetric(min_accuracy=0.85)
    res = metric.measure("no", ["NOT_ENOUGH_INFO"])
    assert res.passed is False
    assert res.score == 0.0
    assert res.details["matched"] is False


def test_classification_metric_word_level_token_set_equality() -> None:
    metric = ClassificationMetric(min_accuracy=0.85)

    # Shuffled tokens match
    res_shuffled = metric.measure("not enough info", ["NOT_ENOUGH_INFO"])
    assert res_shuffled.passed is True
    assert res_shuffled.score == 1.0

    # Hyphenated variation
    res_hyphen = metric.measure("NOT-ENOUGH-INFO", ["not_enough_info"])
    assert res_hyphen.passed is True
    assert res_hyphen.score == 1.0
