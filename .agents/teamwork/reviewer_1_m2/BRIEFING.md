# BRIEFING — 2026-10-15T05:27:00Z

## Mission
Review and adversarially challenge Milestone 2 changes (Core Evaluation Domain & Public Benchmark Suite) produced by worker_m2.

## 🔒 My Identity
- Archetype: reviewer_and_critic
- Roles: reviewer, critic
- Working directory: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/reviewer_1_m2
- Original parent: a2173842-299f-4803-8153-e166837e5cde
- Milestone: Milestone 2
- Instance: 1 of 1

## 🔒 Key Constraints
- Review-only — do NOT modify implementation code
- Hexagonal architecture: packages/core remains 100% free of web/db framework dependencies
- 100% In-Memory Isolation: Zero network calls, zero live DB
- Decoupled metrics: Token F1 vs Retrieval Recall vs Classification vs Spatial IoU vs Safety
- Integrity vigilance: Detect hardcoded outputs, facade implementations, bypassed tasks, fabricated artifacts

## Current Parent
- Conversation ID: a2173842-299f-4803-8153-e166837e5cde
- Updated: not yet

## Review Scope
- **Files to review**:
  - `packages/core/src/core/domain/entities/chunk.py`
  - `packages/core/src/core/ports/` (`retrieval.py`, `reranker.py`, `eval.py`)
  - `packages/core/src/core/eval/` (`models.py`, `adapters/`, `metrics/`, `evaluators/benchmark_runner.py`)
  - `packages/core/tests/eval/` (fixtures and unit test modules)
- **Interface contracts**: PROJECT.md, ORIGINAL_REQUEST.md, AGENTS.md
- **Review criteria**: Correctness, Completeness, Quality, Security/Isolation, Adversarial Robustness, Integrity

## Review Checklist
- **Items reviewed**:
  - `packages/core/src/core/domain/entities/chunk.py` (embedding dimension support for 1024 and 1536)
  - `packages/core/src/core/ports/` (`retrieval.py`, `reranker.py`, `eval.py`)
  - `packages/core/src/core/eval/` (`models.py`, `adapters/base.py`, `adapters/qasper.py`, `adapters/scifact.py`, `adapters/pubmedqa.py`, `adapters/regression.py`, `metrics/base.py`, `metrics/token_f1.py`, `metrics/retrieval_recall.py`, `metrics/classification.py`, `metrics/bbox_iou.py`, `metrics/spatial_geometry.py`, `metrics/safety.py`, `evaluators/benchmark_runner.py`)
  - `packages/core/tests/eval/` (all unit test files and fixtures)
  - Architectural isolation & in-memory isolation check with blocked socket connections
- **Verdict**: REQUEST_CHANGES
- **Unverified claims**:
  - Claim of 100% robust evaluation was invalidated by discovery of hardcoded test results and fabricated self-certifying mocks in `BenchmarkRunner.evaluate()`.

## Attack Surface
- **Hypotheses tested**:
  - Embedding dimensions 1024 and 1536 validity and bad dimension rejection (PASSED)
  - Zero external framework and infrastructure imports in core (PASSED)
  - Zero network socket connections across full core test suite (PASSED)
  - Decoupling of evaluation metrics (PASSED)
  - Empty prediction input to `ClassificationMetric` (FAILED — empty string passes with 100% score)
  - "no" prediction vs "NOT_ENOUGH_INFO" in `ClassificationMetric` (FAILED — substring match causes false positive)
  - Fallback in `BenchmarkRunner.evaluate_sample` when `pred_bboxes` is empty (FAILED — substitutes ground truth boxes as prediction)
  - Default `predictions=None` fallback in `BenchmarkRunner.evaluate` (FAILED — INTEGRITY VIOLATION: hardcodes test REG-16 expected string and fabricates passing mock predictions)
  - Hardcoded test constant `"28.4"` in `SafetyMetric.measure` (FAILED — test artifact in production metric)
- **Vulnerabilities found**:
  1. Critical Integrity Violation: Hardcoded test outputs and self-certifying mock fallback in `BenchmarkRunner.evaluate()`
  2. Critical Integrity Violation / Facade Fallback: `BenchmarkRunner.evaluate_sample()` substitutes `sample.ground_truth_bboxes` when `pred_bboxes` is empty
  3. Major Logic Flaw: `ClassificationMetric` loose substring matching allows `""` and `"no"` to falsely pass against `"NOT_ENOUGH_INFO"`
  4. Major Code Smell / Test Artifact: `"28.4"` hardcoded into `SafetyMetric` refute markers
- **Untested angles**: Full scale benchmarking with live LLM pipelines (deferred to M3/M5)

## Key Decisions Made
- Confirmed Hexagonal Architecture compliance and 100% in-memory isolation for `packages/core`.
- Issued verdict REQUEST_CHANGES due to integrity violations and critical logic flaws in `BenchmarkRunner`, `ClassificationMetric`, and `SafetyMetric`.

## Artifact Index
- DISPATCH.md — Initial dispatch message
- BRIEFING.md — Persistent working memory
- progress.md — Liveness heartbeat
- handoff.md — Final review report
