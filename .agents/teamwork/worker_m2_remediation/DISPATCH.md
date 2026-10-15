## 2026-10-15T05:32:46Z
You are worker_m2_remediation.
Your working directory is: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/worker_m2_remediation
Read the original user request at: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md
Read the project specifications at: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/PROJECT.md
Read the reports from Reviewer 1 and Reviewer 2 at:
/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/reviewer_1_m2/handoff.md
/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/reviewer_2_m2/handoff.md
Read the engineering guidelines in /home/dammanhdungvn/Downloads/Workspace/VeriScholar/AGENTS.md.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

EXCLUSIVE WRITE OWNERSHIP:
- packages/core/src/core/eval/evaluators/benchmark_runner.py
- packages/core/src/core/eval/metrics/safety.py
- packages/core/src/core/eval/metrics/spatial_geometry.py
- packages/core/src/core/eval/metrics/classification.py
- packages/core/src/core/eval/adapters/pubmedqa.py
- packages/core/tests/eval/**

REMEDIATION TASKS:
1. In `packages/core/src/core/eval/evaluators/benchmark_runner.py`:
   - Remove lines 178-207 that fabricated synthetic regression predictions with hardcoded strings (e.g. "28.4 BLEU", etc.). If `predictions` is None or omitted, raise ValueError: "Predictions must be provided to evaluate(). BenchmarkRunner does not fabricate synthetic predictions."
   - Remove line 146 where empty `pred_bboxes` silently fell back to `sample.ground_truth_bboxes`. It must strictly be: `pred_bboxes = pred.predicted_bboxes if pred.predicted_bboxes is not None else []`.
2. In `packages/core/src/core/eval/metrics/safety.py`:
   - Remove `"28.4"` from `refute_markers` (line 105). Keep only genuine generic refutation phrases (e.g. `"không đúng"`, `"bác bỏ"`, `"sai"`, `"incorrect"`, `"refute"`, `"false"`, `"không phải"`, `"không có cơ sở"`).
3. In `packages/core/src/core/eval/metrics/spatial_geometry.py`:
   - Enforce upper bound `coord <= 1.0` (in addition to `coord >= 0.0`) for `x0`, `y0`, `x1`, `y1`. Unnormalized pixel coordinates (> 1.0) must trigger an anomaly.
4. In `packages/core/src/core/eval/metrics/classification.py` & `pubmedqa.py`:
   - In `ClassificationMetric.measure`: Reject empty predictions `""` or `None` (return score 0.0, passed False). Replace loose substring matching (`norm_pred in gt or gt in norm_pred`) with exact matching or word-level token set equality (`norm_pred == gt` or set of words matching). Ensure `"no"` does not match `"NOT_ENOUGH_INFO"`.
   - In `PubMedQAAdapter.parse_data`: `ground_truth_answers` must contain ONLY the categorical decision (`"yes"`, `"no"`, or `"maybe"`). The long answer explanation must reside strictly in `metadata["long_answer"]`, NOT in `ground_truth_answers`.
5. Update tests in `packages/core/tests/eval/`:
   - Ensure `test_benchmark_runner.py` passes explicit `EvalPrediction` objects with genuine predicted text and bounding boxes instead of relying on synthetic fallback.
   - Run full test suite: `uv run pytest packages/core/tests`
   - Run linter & formatter: `uv run ruff check packages/core` and `uv run ruff format --check packages/core`
   - Verify 100% tests pass with 0 errors and 0 warnings.

Write your complete handoff report to:
/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/worker_m2_remediation/handoff.md
When done, notify parent (conversation ID: a2173842-299f-4803-8153-e166837e5cde) via send_message.
