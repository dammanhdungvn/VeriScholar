# Milestone 2 Remediation Handoff Report

**Agent**: `worker_m2_remediation` (Roles: implementer, qa, specialist)  
**Parent Agent**: `a2173842-299f-4803-8153-e166837e5cde`  
**Working Directory**: `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/worker_m2_remediation`  
**Date**: 2026-10-15  
**Verdict**: **COMPLETE — READY FOR RE-REVIEW / APPROVAL**

---

## 1. Observation

### 1.1. Pre-Remediation Vulnerabilities (Direct Observations)
1. **Synthetic Facade Predictions in `BenchmarkRunner`**:
   - In `packages/core/src/core/eval/evaluators/benchmark_runner.py` (lines 178-207 prior to edit), when `predictions` was omitted, the runner fabricated synthetic predictions copying golden answers, including verbatim regression output `"Bác bỏ: Không đúng. Điểm BLEU thực tế là 28.4 BLEU thay vì 45.0."` and setting `is_blocked=True` from sample metadata.
2. **Bounding Box Ground Truth Fallback in `BenchmarkRunner`**:
   - In `packages/core/src/core/eval/evaluators/benchmark_runner.py` (line 146 prior to edit), the runner evaluated `prediction=pred_bboxes or sample.ground_truth_bboxes`. When an evaluation prediction contained empty bounding boxes (`[]`), the runner silently substituted ground truth boxes and awarded 100% pass score.
3. **Hardcoded Test Constant in `SafetyMetric`**:
   - In `packages/core/src/core/eval/metrics/safety.py` (line 105 prior to edit), `"28.4"` was hardcoded as a generic refute marker in `refute_markers = ["không đúng", "không chính xác", "bác bỏ", "28.4", ...]`.
4. **Unnormalized Bounding Box Bypass in `SpatialGeometryMetric`**:
   - In `packages/core/src/core/eval/metrics/spatial_geometry.py` (lines 79-88 prior to edit), only `coord < 0.0` was checked. Coordinates exceeding 1.0 (e.g. raw pixel coordinates `[50, 100, 400, 700, 1]`) skipped anomaly detection and passed with `score=1.0`. Furthermore, empty predicted boxes when ground truth expected boxes passed with 1.0.
5. **Empty Prediction Pass & Substring False Positives in `ClassificationMetric`**:
   - In `packages/core/src/core/eval/metrics/classification.py` (lines 124-126 prior to edit), `any(norm_pred == gt or norm_pred in gt or gt in norm_pred for gt in acceptable_gts)` allowed empty predictions `""` to pass against any class with `score=1.0` (because `"" in gt` is True). In addition, `"no"` falsely matched `"NOT_ENOUGH_INFO"`.
6. **Long Answer Leak in `PubMedQAAdapter`**:
   - In `packages/core/src/core/eval/adapters/pubmedqa.py` (lines 61-66 prior to edit), the adapter appended `long_answer` into `ground_truth_answers`. When `long_answer` contained words like "no", opposite medical classifications passed with `score=1.0`.

### 1.2. Post-Remediation Verification Commands & Results
- **Full Core Test Suite**:
  ```bash
  uv run pytest packages/core/tests -v
  ```
  Result: **249 passed in 0.65s** (zero network calls, 100% in-memory isolated).
- **Core Linter & Formatter**:
  ```bash
  uv run ruff check packages/core
  uv run ruff format --check packages/core
  ```
  Result: **All checks passed! 87 files already formatted** (0 errors, 0 warnings).
- **Downstream API Regression Suite**:
  ```bash
  uv run pytest apps/api/tests
  ```
  Result: **239 passed, 0 failures in 28.98s**.
- **Source Code Grep for Hardcoded Artifact `"28.4"`**:
  ```bash
  grep -n "28.4" packages/core/src/core/eval/evaluators/benchmark_runner.py packages/core/src/core/eval/metrics/safety.py
  ```
  Result: **0 occurrences found in source code**.

---

## 2. Logic Chain

1. **Elimination of Synthetic Facade & Mandatory Predictions**:
   - In `benchmark_runner.py`:
     - Lines 178-207 were completely deleted.
     - Added validation at the entry point of `BenchmarkRunner.evaluate()`:
       ```python
       if predictions is None:
           raise ValueError(
               "Predictions must be provided to evaluate(). "
               "BenchmarkRunner does not fabricate synthetic predictions."
           )
       ```
     - In `evaluate_sample()`: Replaced `prediction=pred_bboxes or sample.ground_truth_bboxes` with explicit resolution `pred_bboxes = raw_pred_boxes if raw_pred_boxes is not None else []` and passed `prediction=pred_bboxes` directly.
     - `pred_dict` now extracts prediction attributes (`predicted_answer`, `response`, `is_blocked`, `block_reason`) cleanly from both `dict` and `EvalPrediction` models.
2. **Excising `"28.4"` from Refutation Markers**:
   - In `safety.py`:
     - Removed `"28.4"` from `refute_markers`.
     - Retained strictly generic linguistic refutation markers: `"không đúng"`, `"không chính xác"`, `"bác bỏ"`, `"sai"`, `"không phải"`, `"không có cơ sở"`, `"không có"`, `"thay vì"`, `"incorrect"`, `"false"`, `"refute"`.
     - Verified with a dedicated test that mentioning `"28.4"` alone without a linguistic refutation marker fails with `score=0.0, passed=False`.
3. **Enforcing Strict Normalized Bounds `[0.0, 1.0]` in `SpatialGeometryMetric`**:
   - In `spatial_geometry.py`:
     - Added check:
       ```python
       if any(coord > 1.0 for coord in (x0, y0, x1, y1)):
           anomalies.append({
               "index": idx,
               "error": "UNNORMALIZED_COORDINATES",
               "bbox": [x0, y0, x1, y1],
               "detail": "Coordinates must be normalized floats in range [0.0, 1.0].",
           })
       ```
     - Enforced that if `not boxes` and `ground_truth` has bounding boxes, the metric returns `score=0.0, passed=False` rather than silently passing.
     - Anti-lazy full-page bounding box check updated to strictly require `all(0.0 <= c <= 1.0 for c in (x0, y0, x1, y1))`.
4. **Remediating `ClassificationMetric` & `PubMedQAAdapter` Contracts**:
   - In `classification.py`:
     - Empty predictions (`""`, whitespace, `None`) immediately return `MetricResult(score=0.0, passed=False, details={"matched": False})`.
     - Replaced loose substring check `norm_pred in gt or gt in norm_pred` with `_match_label(p, g)` which checks exact normalized equality (`p == g`) or token set equality (`set(p.split("_")) == set(g.split("_"))`).
     - `"no"` does NOT match `"NOT_ENOUGH_INFO"` (`{"no"} != {"not", "enough", "info"}`).
   - In `pubmedqa.py`:
     - `gt_answers = [decision] if decision else []`. Long narrative text is strictly stored in `metadata["long_answer"]`, never leaked into `ground_truth_answers`.
     - Predicting `"no"` against a golden decision of `"yes"` strictly returns `score=0.0, passed=False`.
5. **Comprehensive Test Suite Alignment**:
   - `test_benchmark_runner.py`: Provided explicit `EvalPrediction` instances with genuine text, bounding boxes, and evidence chunks. Added tests for omitted predictions (`ValueError`) and missing bounding box fallback prevention.
   - `test_adversarial_metrics_runner.py`: Provided explicit prediction generators for 100-sample scalability batch, serialization round-trip, and empty sample list.
   - `test_adversarial_adapters.py`: Updated `test_pubmedqa_questions_without_contexts` to assert categorical `ground_truth_answers == ["yes"]`, and updated `test_classification_metric_substring_vulnerability` to assert that `"no"` against `"NOT_ENOUGH_INFO"` produces `passed=False, score=0.0`.
   - `test_spatial_geometry_metric.py`: Added tests verifying unnormalized pixel coordinates `[50, 100, 400, 700, 1]` trigger `UNNORMALIZED_COORDINATES` anomaly, and missing predicted boxes fail when ground truth boxes exist.
   - `test_classification_metric.py`: Added tests for empty string / None rejection, `"no"` vs `"NOT_ENOUGH_INFO"`, and word token set equality.
   - `test_safety_metric.py`: Added test ensuring mentioning `"28.4"` alone fails false premise refutation.
   - `test_pubmedqa_adapter.py`: Added test verifying that opposite decision predicting `"no"` against `"yes"` fails with score 0.0 even when the long answer text contains the word "no".

---

## 3. Caveats

- **No Caveats**: All 5 remediation tasks and reviewer findings have been resolved in their entirety without shortcuts or facade workarounds.
- Scope remained strictly within `packages/core/src/core/eval/**` and `packages/core/tests/eval/**`, respecting exclusive write ownership.

---

## 4. Conclusion

All integrity violations, test-tailoring artifacts (`"28.4"`), synthetic self-certifying fallbacks, and boundary check flaws identified by Reviewer 1 and Reviewer 2 in Milestone 2 have been successfully remediated with genuine domain logic.
- Total core tests: **249 passed** in 0.65s (100% in-memory isolated).
- Total API tests: **239 passed** in 28.98s.
- Linter & Formatter: **0 errors, 0 warnings** across `packages/core`.
- Milestone 2 is fully ready for re-review and final approval.

---

## 5. Verification Method

To independently verify all remediations:

```bash
# 1. Verify unnormalized coordinates are rejected by SpatialGeometryMetric
uv run --package core python -c '
from core.eval.metrics.spatial_geometry import SpatialGeometryMetric
res = SpatialGeometryMetric().measure(prediction=[[50.0, 100.0, 400.0, 700.0, 1]])
assert res.passed is False, "Expected unnormalized coords to fail"
assert res.error_samples[0]["error"] == "UNNORMALIZED_COORDINATES"
print("Verification 1 Passed: Unnormalized coordinates properly rejected.")
'

# 2. Verify empty prediction is rejected by ClassificationMetric
uv run --package core python -c '
from core.eval.metrics.classification import ClassificationMetric
res = ClassificationMetric().measure(prediction="", ground_truth=["SUPPORT"])
assert res.passed is False, "Empty prediction must fail"
assert res.score == 0.0
print("Verification 2 Passed: Empty prediction rejected with score 0.0.")
'

# 3. Verify 'no' does not match 'NOT_ENOUGH_INFO'
uv run --package core python -c '
from core.eval.metrics.classification import ClassificationMetric
res = ClassificationMetric().measure(prediction="no", ground_truth=["NOT_ENOUGH_INFO"])
assert res.passed is False, "no must not match NOT_ENOUGH_INFO"
assert res.score == 0.0
print("Verification 3 Passed: Substring false positive prevented.")
'

# 4. Verify PubMedQA opposite decision fails with score 0.0
uv run --package core python -c '
from core.eval.adapters.pubmedqa import PubMedQAAdapter
from core.eval.metrics.classification import ClassificationMetric
raw = {"1": {"QUESTION": "Q?", "final_decision": "yes", "LONG_ANSWER": "There was no difference."}}
sample = PubMedQAAdapter().parse_data(raw)[0]
assert sample.ground_truth_answers == ["yes"]
res = ClassificationMetric().measure(prediction="no", ground_truth=sample.ground_truth_answers)
assert res.passed is False
assert res.score == 0.0
print("Verification 4 Passed: PubMedQA opposite decision correctly rejected.")
'

# 5. Verify BenchmarkRunner requires predictions and raises ValueError if omitted
uv run --package core python -c '
from core.eval.evaluators.benchmark_runner import BenchmarkRunner
from core.eval.models import EvalSample
sample = EvalSample(id="s1", dataset="qasper", split="dev", paper_id="p1", paper_title="T", query="Q?")
try:
    BenchmarkRunner().evaluate([sample])
    assert False, "Should have raised ValueError"
except ValueError as e:
    assert "Predictions must be provided to evaluate()" in str(e)
print("Verification 5 Passed: BenchmarkRunner raises ValueError when predictions omitted.")
'

# 6. Verify missing bbox prediction does not fallback to ground truth
uv run --package core python -c '
from core.eval.evaluators.benchmark_runner import BenchmarkRunner
from core.eval.models import EvalSample
sample = EvalSample(id="t1", dataset="qasper", split="dev", paper_id="p1", paper_title="T", query="Q?", ground_truth_bboxes=[[0.1, 0.2, 0.5, 0.6, 1]])
res = BenchmarkRunner().evaluate_sample(sample, {"predicted_bboxes": []})
assert res["spatial_geometry"].passed is False
assert res["spatial_geometry"].score == 0.0
print("Verification 6 Passed: Missing bboxes fail without ground truth fallback.")
'

# 7. Verify no hardcoded "28.4" in source code
grep -n "28.4" packages/core/src/core/eval/evaluators/benchmark_runner.py packages/core/src/core/eval/metrics/safety.py || echo "Verification 7 Passed: Zero occurrences of 28.4 in source code."

# 8. Run full test suites and linting
uv run pytest packages/core/tests
uv run ruff check packages/core
uv run ruff format --check packages/core
```
