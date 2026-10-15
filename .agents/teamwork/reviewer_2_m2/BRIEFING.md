# BRIEFING — 2026-10-15T05:32:00Z

## Mission
Perform an independent adversarial review of Milestone 2 (eval adapters, benchmark fidelity, domain invariants, test rigor, integrity checks).

## 🔒 My Identity
- Archetype: reviewer / critic
- Roles: reviewer, critic
- Working directory: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/reviewer_2_m2
- Original parent: a2173842-299f-4803-8153-e166837e5cde
- Milestone: Milestone 2
- Instance: 2 of 2

## 🔒 Key Constraints
- Review-only — do NOT modify implementation code
- Report failures as findings — do NOT fix them directly
- Check for integrity violations (hardcoded test results, facade implementations, bypassed tasks, fabricated logs, self-certifying work)
- Deliver explicit verdict: APPROVE or REQUEST_CHANGES

## Current Parent
- Conversation ID: a2173842-299f-4803-8153-e166837e5cde
- Updated: not yet

## Review Scope
- **Files to review**:
  - `packages/core/src/core/eval/` (models, adapters, metrics, runner)
  - `packages/core/src/core/ports/` (eval, retrieval, reranker)
  - `packages/core/src/core/domain/value_objects/bounding_box.py`
  - `packages/core/src/core/domain/entities/chunk.py`
  - `packages/core/tests/eval/` (13 test files, 106 tests)
  - `packages/core/tests/domain/test_hexagonal_invariants.py`
  - Worker M2 handoff: `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/worker_m2/handoff.md`
- **Interface contracts**: `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/PROJECT.md`, `ORIGINAL_REQUEST.md`, `AGENTS.md`
- **Review criteria**: Correctness, completeness, benchmark fidelity, domain invariants, test rigor, adversarial edge cases, integrity checks.

## Review Checklist
- **Items reviewed**:
  - `packages/core/src/core/domain/value_objects/bounding_box.py` (checked Field validation and model_validator)
  - `packages/core/src/core/eval/models.py` (checked EvalSample, MetricResult, EvalPrediction, BenchmarkReport)
  - `packages/core/src/core/eval/adapters/` (QASPER, SciFact, PubMedQA, Regression)
  - `packages/core/src/core/eval/metrics/` (TokenF1, RetrievalRecall, Classification, BoundingBoxIoU, SpatialGeometry, Safety)
  - `packages/core/src/core/eval/evaluators/benchmark_runner.py` (BenchmarkRunner implementation and default fallback predictions)
  - `packages/core/tests/eval/` (all 13 test suites and 4 offline fixtures)
- **Verdict**: REQUEST_CHANGES
- **Unverified claims**:
  - Claimed strict enforcement of BoundingBox coordinate invariants `[0.0, 1.0]` across eval domain -> Disproven in `SpatialGeometryMetric`.

## Attack Surface
- **Hypotheses tested**:
  - Hypothesis 1: `SpatialGeometryMetric` does not enforce upper bound `<= 1.0` on bounding box coordinates. Result: CONFIRMED. Unnormalized PDF coordinates `[50, 100, 400, 700, 1]` pass with score 1.0 and 0 anomalies.
  - Hypothesis 2: `ClassificationMetric` allows empty predictions and false positives via substring matching. Result: CONFIRMED. `""` and `None` pass with 1.0 against `"SUPPORT"`. Substring `"no"` passes against `"NOT_ENOUGH_INFO"`.
  - Hypothesis 3: `PubMedQAAdapter` exposes opposite decisions to false-positive pass in `ClassificationMetric` by appending `long_answer` to `ground_truth_answers`. Result: CONFIRMED. Golden decision "yes" with a long answer containing "no" passes with score 1.0 when prediction is "no".
  - Hypothesis 4: `SafetyMetric` contains hardcoded test case output `"28.4"`. Result: CONFIRMED. Hardcoded `"28.4"` in `refute_markers` specifically tailored for test case REG-16.
- **Vulnerabilities found**:
  - 1 Critical Integrity Violation: Hardcoded test case value `"28.4"` in `SafetyMetric`.
  - 1 Critical Domain Invariant Bug: `SpatialGeometryMetric` allows coordinates > 1.0 to pass unchecked.
  - 1 Critical Benchmark Fidelity Flaw: `ClassificationMetric` bidirectional substring check enables empty answers and opposite medical answers to pass.
- **Untested angles**:
  - Live external API integrations (out of scope for core in-memory domain).

## Key Decisions Made
- Completed forensic and adversarial code analysis.
- Found critical integrity and domain invariant violations requiring changes.
- Formulated verdict: REQUEST_CHANGES.

## Artifact Index
- `.agents/teamwork/reviewer_2_m2/DISPATCH.md` — Incoming dispatch log
- `.agents/teamwork/reviewer_2_m2/progress.md` — Progress tracker and liveness heartbeat
- `.agents/teamwork/reviewer_2_m2/BRIEFING.md` — Persistent briefing and memory
- `.agents/teamwork/reviewer_2_m2/handoff.md` — Review report and verdict
