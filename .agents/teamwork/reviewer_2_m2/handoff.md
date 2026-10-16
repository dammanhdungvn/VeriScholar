# Adversarial Review & Quality Audit Report: Milestone 2 — Core Evaluation Domain

**Reviewer**: `reviewer_2_m2` (Roles: reviewer, critic)  
**Parent Agent**: `a2173842-299f-4803-8153-e166837e5cde`  
**Workspace**: `/home/dammanhdungvn/Downloads/Workspace/VeriScholar`  
**Date**: 2026-10-15  
**Verdict**: **REQUEST_CHANGES**

---

## Review Summary

**Verdict**: **REQUEST_CHANGES**  
**Overall Risk Assessment**: **HIGH**

While the foundational Hexagonal Architecture ports (`IRetrievalSearchPort`, `ICrossEncoderRerankerPort`, `IDatasetAdapter`, `IEvalMetric`, `IBenchmarkEvaluator`), multi-model embedding dimension extension (1024 and 1536 dims), and in-memory test execution (106 tests in `packages/core/tests/eval/` passing in 0.23s) are structurally well-organized, an adversarial forensic examination uncovered three critical flaws:
1. **INTEGRITY VIOLATION / TEST TAILORING**: A specific regression test case output (`"28.4"`) is hardcoded directly into the production evaluation metric source code (`SafetyMetric.py:105`).
2. **DOMAIN INVARIANT VIOLATION**: `SpatialGeometryMetric` fails to enforce the upper boundary `coord <= 1.0`. Raw, unnormalized PDF point coordinates (e.g., `[50, 100, 400, 700, 1]`) pass through with 100% pass rate (`score=1.0`) and zero detected anomalies.
3. **BENCHMARK FIDELITY & EVALUATION LOOPHOLE**: `ClassificationMetric.measure` uses loose bidirectional substring matching (`norm_pred in gt or gt in norm_pred`). This enables completely empty predictions (`""` and `None`) to pass with `score=1.0`, and causes opposite medical answers in `PubMedQA` (predicting `"no"` when golden decision is `"yes"`) to pass with `score=1.0` due to `PubMedQAAdapter` embedding full `LONG_ANSWER` text into `ground_truth_answers`.

---

## Findings

### [Critical] Finding 1: INTEGRITY VIOLATION — Hardcoded Test Value `"28.4"` in Metric Source Code
- **What**: Test case regression result `"28.4"` is hardcoded inside `refute_markers` in production metric `SafetyMetric`.
- **Where**: `packages/core/src/core/eval/metrics/safety.py:105`
- **Why**: Test case REG-16 in `scripts/eval/data/project_regression_25.json` and `packages/core/tests/eval/fixtures/regression_subset.json` tests whether the system refutes a false claim about BLEU score: *"Điểm BLEU thực tế của Transformer (big) trên WMT 2014 English-to-German là 28.4 BLEU"*. Embedding `"28.4"` as a generic refute marker in the evaluation metric allows any response mentioning `"28.4"` (even without refuting anything, e.g. *"Transformer achieved 28.4 BLEU"*) to pass. This tailors the metric to pass the specific regression test.
- **Verbatim Code**:
  ```python
  # packages/core/src/core/eval/metrics/safety.py:101-112
  refute_markers = [
      "không đúng",
      "không chính xác",
      "bác bỏ",
      "28.4",  # <--- CRITICAL INTEGRITY TAILORING
      "thay vì",
      "không phải",
      "không có",
      "incorrect",
      "false",
      "refute",
  ]
  ```
- **Suggestion**: Remove `"28.4"` from `refute_markers`. Refutation metrics must check for linguistic negation/rebuttal phrases (`"không đúng"`, `"bác bỏ"`, `"incorrect"`, `"false"`, etc.) or verify against ground truth negation spans dynamically, rather than hardcoding numerical data from individual test samples.

---

### [Critical] Finding 2: DOMAIN INVARIANT VIOLATION — Unnormalized BoundingBox Coordinates Pass `SpatialGeometryMetric`
- **What**: `SpatialGeometryMetric` does not validate that coordinates are normalized floats in `[0.0, 1.0]`. Unnormalized PDF points (e.g. `[50, 100, 400, 700, 1]`) pass with `score=1.0` and 0 anomalies.
- **Where**: `packages/core/src/core/eval/metrics/spatial_geometry.py:79-88` and `115-117`
- **Why**: `AGENTS.md` and `PROJECT.md` mandate that coordinates `[x0, y0, x1, y1]` must be strictly normalized floats relative to page dimensions (`0.0 <= x0 < x1 <= 1.0`, `0.0 <= y0 < y1 <= 1.0`). `SpatialGeometryMetric` only checks `coord < 0.0`. It never checks `coord > 1.0`. Furthermore, line 115 gates the anti-lazy check behind `if all(0.0 <= c <= 1.05 for c in (x0, y0, x1, y1)):`, causing unnormalized coordinates to skip the area check entirely.
- **Empirical Proof**:
  ```bash
  uv run --package core python -c '
  from core.eval.metrics.spatial_geometry import SpatialGeometryMetric
  metric = SpatialGeometryMetric()
  res = metric.measure(prediction=[[50.0, 100.0, 400.0, 700.0, 1]])
  print("Passed?:", res.passed, "Score:", res.score, "Anomalies:", res.details["anomalies_count"])
  '
  # Output: Passed?: True Score: 1.0 Anomalies: 0
  ```
- **Suggestion**: Add a boundary validation check in `SpatialGeometryMetric`:
  ```python
  if any(coord > 1.0 for coord in (x0, y0, x1, y1)):
      anomalies.append({
          "index": idx,
          "error": "UNNORMALIZED_COORDINATES",
          "bbox": [x0, y0, x1, y1],
          "detail": "Coordinates must be normalized floats in range [0.0, 1.0].",
      })
  ```

---

### [Critical] Finding 3: BENCHMARK EVALUATION FLAW — Loose Substring Matching in `ClassificationMetric` & PubMedQA Long Answer Leak
- **What**: `ClassificationMetric.measure` uses bidirectional substring matching (`norm_pred in gt or gt in norm_pred`). This causes:
  1. Empty strings `""` and `None` to pass with `score=1.0` against any class.
  2. Predictions of `"no"` to pass against `"NOT_ENOUGH_INFO"`.
  3. Opposite medical decisions in PubMedQA to pass with `score=1.0` because `PubMedQAAdapter` appends the full multi-sentence `long_answer` into `ground_truth_answers`.
- **Where**:
  - `packages/core/src/core/eval/metrics/classification.py:124-126`
  - `packages/core/src/core/eval/adapters/pubmedqa.py:61-66`
- **Why**: In `ClassificationMetric`:
  ```python
  matched = any(
      norm_pred == gt or norm_pred in gt or gt in norm_pred for gt in acceptable_gts
  )
  ```
  If `norm_pred` is `""`, `"" in gt` is `True` for any non-empty string.
  If `ground_truth_answers` contains `[decision, long_answer]`, and `long_answer` contains the word "no" (e.g. *"There was no significant difference observed"*), a model predicting `"no"` against a ground truth decision of `"yes"` passes with 100%!
- **Empirical Proof**:
  ```bash
  uv run --package core python -c '
  from core.eval.adapters.pubmedqa import PubMedQAAdapter
  from core.eval.metrics.classification import ClassificationMetric
  raw_data = {"123": {"QUESTION": "Is X effective?", "final_decision": "yes", "LONG_ANSWER": "There was no significant difference observed."}}
  adapter = PubMedQAAdapter()
  sample = adapter.parse_data(raw_data)[0]
  metric = ClassificationMetric()
  res = metric.measure(prediction="no", ground_truth=sample.ground_truth_answers)
  print("Opposite decision Passed?:", res.passed, "Score:", res.score, "Reason:", res.reasoning)
  '
  # Output: Opposite decision Passed?: True Score: 1.0 Reason: Classification match: 'no' in ['yes', 'there_was_no_significant_difference_observed.'].
  ```
- **Suggestion**:
  1. In `ClassificationMetric.measure`: require non-empty predictions (`if not norm_pred: return MetricResult(score=0.0, passed=False)`) and replace loose substring matching with exact token/label matching (`norm_pred == gt` or validated word-boundary matching).
  2. In `PubMedQAAdapter`: store `long_answer` strictly in `metadata["long_answer"]` (and/or a separate field), keeping `ground_truth_answers = [decision]` for categorical decision classification, or provide a dedicated `decision` field.

---

### [Major] Finding 4: ARCHITECTURAL GAP — `EvalSample` BoundingBox Coordinate Invariant Bypass
- **What**: `EvalSample` dataclass accepts raw unvalidated nested lists for `ground_truth_bboxes` without validating against the domain `BoundingBox` value object.
- **Where**: `packages/core/src/core/eval/models.py:29`
- **Why**: `BoundingBox` (`packages/core/src/core/domain/value_objects/bounding_box.py`) enforces strict Pydantic invariants (`ge=0.0, le=1.0, page >= 1, x0 < x1, y0 < y1`). However, `EvalSample` bypasses domain value objects and accepts `ground_truth_bboxes: list[list[float]] = field(default_factory=list)`. This allows corrupt or invalid bounding boxes to enter the evaluation pipeline undetected unless downstream metrics explicitly audit them.
- **Suggestion**: Use `BoundingBox.from_list()` validation in `EvalSample.__post_init__` or provide a validation helper that converts coordinates into validated `BoundingBox` value objects.

---

### [Major] Finding 5: ROBUSTNESS — Lack of Defensive Null-Checks on Explicit `None` in Dataset JSON
- **What**: `QASPERAdapter` and `SciFactAdapter` raise unhandled `TypeError` when fields such as `qas`, `answers`, or `cited_doc_ids` are explicitly `None` in JSON inputs.
- **Where**:
  - `packages/core/src/core/eval/adapters/qasper.py:45` (`paper_dict.get("qas", [])` returns `None` if JSON contains `"qas": null`)
  - `packages/core/src/core/eval/adapters/scifact.py:76` (`record.get("cited_doc_ids", [])` returns `None` if JSON contains `"cited_doc_ids": null`)
- **Why**: Python `dict.get(key, default)` returns `None` when `key` exists with value `None`. Subsequent iteration (`for qa in qas:`) raises `TypeError: 'NoneType' object is not iterable`.
- **Suggestion**: Use `paper_dict.get("qas") or []` and `record.get("cited_doc_ids") or []` to guard against null-valued keys.

---

## Verified Claims

- Hexagonal Ports (`IRetrievalSearchPort`, `ICrossEncoderRerankerPort`, `IDatasetAdapter`, `IEvalMetric`, `IBenchmarkEvaluator`) defined as `@runtime_checkable` Protocols in `packages/core/src/core/ports/` → **PASS** (verified via `test_hexagonal_invariants.py`).
- `DocumentChunk` supports both 1024 (BGE-M3) and 1536 (OpenAI) dimensions and rejects invalid dimensions (128, 512, 768, 2048) → **PASS** (verified via `test_chunk_dimensions.py`).
- 100% In-Memory Test Isolation with zero network calls and zero DB drivers in `packages/core/tests/` → **PASS** (verified via static grep and `pytest packages/core/tests/` 182 passed in 0.48s).
- SQuAD Token F1 metric implementation with punctuation/article stripping and unanswerable handling → **PASS** (verified via `test_token_f1_metric.py`).
- RetrievalRecallMetric top-k evaluation and token overlap filtering → **PASS** (verified via `test_retrieval_recall_metric.py`).

---

## 5-Component Handoff Protocol

### 1. Observation
1. **Source Code Inspection**:
   - `packages/core/src/core/eval/metrics/safety.py:105`: Line 105 contains the literal `"28.4"` in `refute_markers = ["không đúng", "không chính xác", "bác bỏ", "28.4", "thay vì", ...]`.
   - `packages/core/src/core/eval/metrics/spatial_geometry.py:79-88`: Only checks `any(coord < 0.0 for coord in (x0, y0, x1, y1))`. Coordinates exceeding 1.0 are never flagged.
   - `packages/core/src/core/eval/metrics/classification.py:124-126`: Checks `any(norm_pred == gt or norm_pred in gt or gt in norm_pred for gt in acceptable_gts)`.
   - `packages/core/src/core/eval/adapters/pubmedqa.py:61-66`: Appends `long_answer` into `ground_truth_answers`.
   - `packages/core/src/core/eval/evaluators/benchmark_runner.py:198-200`: Fallback predictions hardcode `"Bác bỏ: Không đúng. Điểm BLEU thực tế là 28.4 BLEU thay vì 45.0."`.
2. **Commands Executed & Outputs**:
   - `uv run pytest packages/core/tests/eval/ -v` → **106 passed in 0.23s**
   - `uv run pytest packages/core/tests/domain/test_hexagonal_invariants.py` → **1 passed in 0.01s**
   - `uv run ruff check packages/core` → **All checks passed!**
   - `uv run ruff format --check packages/core` → **86 files already formatted**
   - Spatial geometry unnormalized test:
     `uv run --package core python -c "from core.eval.metrics.spatial_geometry import SpatialGeometryMetric; print(SpatialGeometryMetric().measure([[50.0, 100.0, 400.0, 700.0, 1]]).passed)"` → returned `True`.
   - Classification empty prediction test:
     `uv run --package core python -c "from core.eval.metrics.classification import ClassificationMetric; print(ClassificationMetric().measure('', ['SUPPORT']).passed)"` → returned `True`.
   - PubMedQA opposite decision test:
     Returned `True` with `Score: 1.0` when predicting `"no"` against golden `"yes"` with long answer containing `"no"`.

### 2. Logic Chain
1. If `SafetyMetric` checks whether a response contains `"28.4"` to judge false-premise refutation, any arbitrary response that happens to mention `"28.4"` passes as a valid refutation. This is test-tailoring against REG-16.
2. If `SpatialGeometryMetric` does not check `coord <= 1.0`, any unnormalized coordinate system (e.g. 72-dpi or 300-dpi PDF points) will pass without triggering geometry anomalies, violating the atomic coordinate invariant mandated in `AGENTS.md`.
3. If `ClassificationMetric` allows `norm_pred in gt or gt in norm_pred`, empty string `""` is a substring of every non-empty ground truth string, allowing non-functional or failed models to achieve 100% accuracy.
4. When `PubMedQAAdapter` mixes full-text narrative sentences into `ground_truth_answers` intended for categorical decisions (`yes`/`no`/`maybe`), the substring check matches common English words, causing opposite diagnostic and clinical conclusions to be scored as 100% accurate.

### 3. Caveats
- The core infrastructure (ports, architecture, dataset download fixtures, in-memory isolation, test speed) is in place and meets hexagonal architecture standards.
- The issues identified are focused on metric boundary validation and adapter contract precision. Once corrected, Milestone 2 will be fully compliant.

### 4. Conclusion
Milestone 2 does **not** currently meet the production quality and adversarial integrity standards required by `AGENTS.md` and `PROJECT.md`. The verdict is **REQUEST_CHANGES**. Implementers must address Findings 1, 2, and 3 before Milestone 2 can be approved.

### 5. Verification Method
To independently verify the findings in this report:

```bash
# 1. Verify unnormalized coordinates bypass SpatialGeometryMetric
uv run --package core python -c '
from core.eval.metrics.spatial_geometry import SpatialGeometryMetric
res = SpatialGeometryMetric().measure(prediction=[[50.0, 100.0, 400.0, 700.0, 1]])
assert res.passed is True, "Expected bypass bug confirmed"
print("Vulnerability 1 Confirmed: Unnormalized coords pass with score", res.score)
'

# 2. Verify empty prediction passes ClassificationMetric
uv run --package core python -c '
from core.eval.metrics.classification import ClassificationMetric
res = ClassificationMetric().measure(prediction="", ground_truth=["SUPPORT"])
assert res.passed is True, "Expected empty prediction bug confirmed"
print("Vulnerability 2 Confirmed: Empty prediction passes with score", res.score)
'

# 3. Verify opposite decision passes in PubMedQA classification
uv run --package core python -c '
from core.eval.adapters.pubmedqa import PubMedQAAdapter
from core.eval.metrics.classification import ClassificationMetric
raw = {"1": {"QUESTION": "Q?", "final_decision": "yes", "LONG_ANSWER": "There was no difference."}}
sample = PubMedQAAdapter().parse_data(raw)[0]
res = ClassificationMetric().measure(prediction="no", ground_truth=sample.ground_truth_answers)
assert res.passed is True, "Expected PubMedQA opposite decision bug confirmed"
print("Vulnerability 3 Confirmed: Opposite decision passes with score", res.score)
'

# 4. Verify hardcoded 28.4 in SafetyMetric source code
grep -n "28.4" packages/core/src/core/eval/metrics/safety.py
```
