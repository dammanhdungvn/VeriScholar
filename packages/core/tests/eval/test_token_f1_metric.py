"""Unit tests for TokenF1Metric in core evaluation domain."""

from __future__ import annotations

from core.eval.metrics.token_f1 import TokenF1Metric, compute_token_f1, normalize_answer


def test_normalize_answer_removes_articles_and_punctuation() -> None:
    raw = "The quick, brown fox jumps over a lazy dog!"
    normalized = normalize_answer(raw)
    assert normalized == "quick brown fox jumps over lazy dog"


def test_compute_token_f1_exact_and_disjoint() -> None:
    # Exact match
    p, r, f1 = compute_token_f1("encoder has 6 layers", "The encoder has 6 layers.")
    assert p == 1.0
    assert r == 1.0
    assert f1 == 1.0

    # Completely disjoint
    p_zero, r_zero, f1_zero = compute_token_f1("cats felines", "apples oranges")
    assert f1_zero == 0.0

    # Both empty
    p_empty, r_empty, f1_empty = compute_token_f1("", "")
    assert f1_empty == 1.0

    # One empty
    p_one, r_one, f1_one = compute_token_f1("something", "")
    assert f1_one == 0.0


def test_compute_token_f1_partial_overlap() -> None:
    pred = "stack of 6 layers"
    gt = "stack of 6 identical layers in encoder"
    # pred tokens: [stack, of, 6, layers] (4)
    # gt tokens: [stack, of, 6, identical, layers, in, encoder] (7)
    # common: [stack, of, 6, layers] (4)
    # p = 4/4 = 1.0, r = 4/7 = 0.5714, f1 = 2 * 1 * (4/7) / (1 + 4/7) = 8/11 = 0.7272
    p, r, f1 = compute_token_f1(pred, gt)
    assert p == 1.0
    assert round(r, 4) == round(4 / 7, 4)
    assert round(f1, 4) == round(8 / 11, 4)


def test_token_f1_metric_multi_ground_truth() -> None:
    metric = TokenF1Metric(min_f1=0.70)
    prediction = "There are 6 layers in the encoder."
    gt_answers = [
        "N = 6 identical layers",
        "There are 6 layers in encoder stack.",
    ]

    res = metric.measure(prediction, gt_answers)
    assert res.passed is True
    assert res.score >= 0.70
    assert "best_ground_truth" in res.details


def test_token_f1_metric_threshold_failure() -> None:
    metric = TokenF1Metric(min_f1=0.80)
    prediction = "Apples red."
    gt_answers = ["Bananas yellow."]

    res = metric.measure(prediction, gt_answers)
    assert res.passed is False
    assert res.score == 0.0


def test_token_f1_metric_unanswerable_handling() -> None:
    metric = TokenF1Metric(min_f1=0.70)

    # Correct unanswerable handling
    res = metric.measure("", [], unanswerable=True)
    assert res.passed is True
    assert res.score == 1.0

    res_str = metric.measure("This question is unanswerable from the text.", [], unanswerable=True)
    assert res_str.passed is True
    assert res_str.score == 1.0
