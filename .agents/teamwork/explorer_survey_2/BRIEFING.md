# BRIEFING — 2026-10-15T02:35:30Z

## Mission
Survey and investigate Module 1 domain logic in packages/core and design the AI Evaluation Benchmark Suite (QASPER, SciFact, PubMedQA, regression evals, metric adapters, coordinate validators).

## 🔒 My Identity
- Archetype: explorer
- Roles: investigator, architect, domain evaluator
- Working directory: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/explorer_survey_2
- Original parent: a2173842-299f-4803-8153-e166837e5cde
- Milestone: Survey & Architectural Design for Module 1 AI Evaluation Benchmark Suite

## 🔒 Key Constraints
- Read-only investigation — do NOT implement
- In-memory isolation: Zero external dependencies, no live network calls during unit/eval tests
- Atomic Evidence Invariant: DocumentChunk bounding boxes must be preserved ([page >= 1, normalized 0.0-1.0], Top-Left origin)
- Files for content delivery, Messages for coordination

## Current Parent
- Conversation ID: a2173842-299f-4803-8153-e166837e5cde
- Updated: 2026-10-15T02:35:30Z

## Investigation State
- **Explored paths**:
  - `packages/core/src/core/domain/entities/chunk.py`, `value_objects/bounding_box.py`
  - `packages/core/src/core/ports/chunk.py`
  - `packages/core/src/core/services/guardrails.py`
  - `apps/api/src/api/adapters/chunk_extractor.py`
  - `apps/api/src/api/services/session_chat_service.py`
  - `apps/api/tests/test_golden_papers_matrix.py`
  - `tests/evals/` (`test_eval_metrics.py`, `test_chunking_quality.py`, `test_parse_chunking_eval.py`, `test_two_tier_eval.py`)
  - `scripts/eval/` (`adapters/`, `metrics/`, `data/project_regression_25.json`, `run_eval.py`, `eval_module_01_ai_quality.py`)
  - `docs/vi/` and `docs/vi/decided/module-01/`
- **Key findings**:
  1. `DocumentChunk` and `BoundingBox` enforce strict geometric invariants in `packages/core`. However, embedding dimensions have a slight discrepancy: `chunk.py` enforces 1024 (BGE-M3), whereas DB schema and some eval tests use 1536 (OpenAI `text-embedding-3-small`).
  2. Hybrid search and Cross-Encoder reranking are currently handled via in-memory heuristics in `session_chat_service.py`, lacking explicit Hexagonal ports in `packages/core/ports/`.
  3. QASPER and SciFact adapters already exist in `scripts/eval/adapters/`, but PubMedQA is completely missing.
  4. Metrics (`SpatialGeometryMetric`, `BoundingBoxIoUMetric`, `RetrievalRecallMetric`, `GroundednessF1Metric`, `SafetyMetric`, `CascadingF1Metric`) exist in `scripts/eval/metrics/` but are not yet formalized inside `packages/core/src/core/eval/`.
  5. In `test_two_tier_eval.py`, `test_run_eval_cli_runner_regression_execution` failed because `GroundednessF1Metric` was evaluated by comparing Vietnamese answer strings with English paper evidence chunks rather than comparing answer to answer or evidence to evidence.
- **Unexplored areas**: None for this survey milestone.

## Key Decisions Made
- Structure a clean Hexagonal evaluation architecture in `packages/core/src/core/eval/` containing domain evaluation schemas, ports, adapters (QASPER, SciFact, PubMedQA, Regression), and pure metric calculators.
- Provide full specification of models, ports, adapters, and directory layout for handoff.

## Artifact Index
- DISPATCH.md — Received task instructions
- BRIEFING.md — Working memory & status
- progress.md — Liveness & heartbeat
- handoff.md — Final 5-component handoff report
