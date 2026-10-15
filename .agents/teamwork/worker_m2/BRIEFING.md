# BRIEFING — 2026-10-15T03:20:00Z

## Mission
Implement Milestone 2: Core Evaluation Domain & Public Benchmark Suite (QASPER, SciFact, PubMedQA, and Project Regression) in `packages/core`, update embedding dimensions in `DocumentChunk`, define hexagonal ports (`retrieval.py`, `reranker.py`, `eval.py`), implement domain models, adapters, metrics, runner, and offline unit test suite with 100% in-memory isolation.

## 🔒 My Identity
- Archetype: worker_m2
- Roles: implementer, qa, specialist
- Working directory: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/worker_m2
- Original parent: a2173842-299f-4803-8153-e166837e5cde
- Milestone: M2_PUBLIC_BENCHMARKS

## 🔒 Key Constraints
- Strict monorepo invariants: `packages/core` must NEVER import from `apps/api` or `apps/web`.
- 100% in-memory isolation: zero external network, zero live DB in `packages/core/tests`.
- Normalized BoundingBox: `[x0, y0, x1, y1, page]`, `0.0 <= x0 < x1 <= 1.0`, `0.0 <= y0 < y1 <= 1.0`, `page >= 1`, Top-Left origin.
- Zero ruff lint/format warnings.
- DO NOT CHEAT: Genuine implementations only, no dummy facade or hardcoded test returns.

## Current Parent
- Conversation ID: a2173842-299f-4803-8153-e166837e5cde
- Updated: 2026-10-15T03:20:00Z

## Task Summary
- **What to build**:
  1. `DocumentChunk` embedding dimension validation accepting both 1024 (BGE-M3) and 1536 (OpenAI).
  2. Ports: `IRetrievalSearchPort`, `ICrossEncoderRerankerPort`, `IDatasetAdapter`, `IEvalMetric`, `IBenchmarkEvaluator`.
  3. `core/eval/models.py`: `EvalSample`, `MetricResult`, `BenchmarkReport`, `EvalPrediction`.
  4. `core/eval/adapters/`: `BaseDatasetAdapter`, `QASPERAdapter`, `SciFactAdapter`, `PubMedQAAdapter`, `ProjectRegressionAdapter`.
  5. `core/eval/metrics/`: `BaseEvalMetric`, `TokenF1Metric`, `RetrievalRecallMetric`, `ClassificationMetric`, `BoundingBoxIoUMetric`, `SpatialGeometryMetric`, `SafetyMetric`.
  6. `core/eval/evaluators/benchmark_runner.py`: Benchmark runner.
  7. `packages/core/tests/eval/fixtures/`: Offline JSON fixtures for QASPER, SciFact, PubMedQA, Regression.
  8. `packages/core/tests/eval/`: 12 test modules covering all adapters, metrics, runner, and multi-model dimensions.
- **Success criteria**:
  - `uv run pytest packages/core/tests` passes 100% (135 passed in 0.45s).
  - `uv run ruff check packages/core` and `uv run ruff format --check packages/core` exit with 0 errors/warnings.
- **Interface contracts**: `PROJECT.md` & `explorer_survey_2/handoff.md`.
- **Code layout**: `packages/core/src/core/eval/`, `packages/core/src/core/ports/`, `packages/core/tests/eval/`.

## Key Decisions Made
- Standardized `EvalSample`, `MetricResult`, and `BenchmarkReport` as lightweight dataclasses with serialization and deserialization helpers (`to_dict`, `from_dict`).
- Used `@runtime_checkable` for all newly introduced port protocols (`IRetrievalSearchPort`, `ICrossEncoderRerankerPort`, `IDatasetAdapter`, `IEvalMetric`, `IBenchmarkEvaluator`).
- Decoupled `TokenF1Metric` (answer vs golden answer using SQuAD article/punctuation normalization) from `RetrievalRecallMetric` (chunks vs evidence passages) and `ClassificationMetric` (macro F1 and decision accuracy for SciFact/PubMedQA).
- Supported both 1024 (BGE-M3) and 1536 (OpenAI text-embedding-3-small) dimensions in `DocumentChunk` through `VALID_EMBEDDING_DIMS = (1024, 1536)` without breaking existing invariant checks.

## Artifact Index
- `.agents/teamwork/worker_m2/DISPATCH.md` — Dispatch task instructions
- `.agents/teamwork/worker_m2/BRIEFING.md` — Situational awareness
- `.agents/teamwork/worker_m2/progress.md` — Progress and heartbeat tracking
- `.agents/teamwork/worker_m2/handoff.md` — Final handoff report
- `packages/core/src/core/domain/entities/chunk.py` — Multi-model embedding dimension support
- `packages/core/src/core/ports/retrieval.py` — Hybrid search port protocol
- `packages/core/src/core/ports/reranker.py` — Cross-encoder reranker port protocol
- `packages/core/src/core/ports/eval.py` — Evaluation domain port protocols
- `packages/core/src/core/eval/` — Evaluation domain implementation (models, adapters, metrics, runner)
- `packages/core/tests/eval/` — Comprehensive in-memory evaluation test suite and offline fixtures

## Change Tracker
- **Files modified**:
  - `packages/core/src/core/domain/entities/chunk.py`: Support 1024 and 1536 dimensions
  - `packages/core/src/core/ports/retrieval.py`: `IRetrievalSearchPort`
  - `packages/core/src/core/ports/reranker.py`: `ICrossEncoderRerankerPort`
  - `packages/core/src/core/ports/eval.py`: `IDatasetAdapter`, `IEvalMetric`, `IBenchmarkEvaluator`
  - `packages/core/src/core/eval/**`: Models, adapters (QASPER, SciFact, PubMedQA, Regression), metrics (TokenF1, Recall@k, Classification, BBoxIoU, SpatialGeometry, Safety), runner
  - `packages/core/tests/eval/**`: Offline fixtures and unit test suite
- **Build status**: 135 passed in 0.45s (0 failures, 0 warnings)
- **Pending issues**: None

## Quality Status
- **Build/test result**: Pass (135/135 tests in packages/core/tests passed)
- **Lint status**: Clean (0 errors, 85 files formatted cleanly)
- **Tests added/modified**: 59 new unit tests in `packages/core/tests/eval/`

## Loaded Skills
- **Source**: `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/skills/hexagonal-architecture/SKILL.md`
  - **Local copy**: `.agents/teamwork/worker_m2/skills/hexagonal-architecture/SKILL.md`
  - **Core methodology**: Ports & Adapters separation, dependency inversion inward toward domain models.
- **Source**: `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/skills/scholar-evaluation/SKILL.md`
  - **Local copy**: `.agents/teamwork/worker_m2/skills/scholar-evaluation/SKILL.md`
  - **Core methodology**: Scholarly evaluation rubric, evidence checking, claim verification.
- **Source**: `/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/skills/verischolar-agent-protocol/SKILL.md`
  - **Local copy**: `.agents/teamwork/worker_m2/skills/verischolar-agent-protocol/SKILL.md`
  - **Core methodology**: Non-negotiable domain invariants: normalized bounding boxes [x0, y0, x1, y1, page], 1-indexed pages, in-memory test isolation.
