## 2026-10-15T03:03:36Z
You are worker_m2.
Your working directory is: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/worker_m2
Read the original user request at: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md
Read the project specifications at: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/PROJECT.md
Read the detailed survey report from explorer_survey_2 at: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/explorer_survey_2/handoff.md
Read the engineering guidelines in /home/dammanhdungvn/Downloads/Workspace/VeriScholar/AGENTS.md.
Also read skills:
/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/skills/hexagonal-architecture/SKILL.md
/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/skills/scholar-evaluation/SKILL.md
/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/skills/verischolar-agent-protocol/SKILL.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

EXCLUSIVE WRITE OWNERSHIP:
You own these files/directories exclusively:
- packages/core/src/core/domain/entities/chunk.py
- packages/core/src/core/ports/retrieval.py
- packages/core/src/core/ports/reranker.py
- packages/core/src/core/ports/eval.py
- packages/core/src/core/eval/** (all modules under packages/core/src/core/eval/)
- packages/core/tests/eval/** (all test files and fixtures under packages/core/tests/eval/)

TASK OBJECTIVES (Milestone 2: Core Evaluation Domain & Public Benchmark Suite):
1. In `packages/core/src/core/domain/entities/chunk.py`:
   - Update embedding dimension validation so that `embedding` accepts either 1024 (BGE-M3) or 1536 (OpenAI text-embedding-3-small) dimensions, preventing invariant violation errors when testing multi-model pipelines.
2. In `packages/core/src/core/ports/`:
   - Add `packages/core/src/core/ports/retrieval.py`: `IRetrievalSearchPort` protocol for candidate chunk retrieval (dense + sparse).
   - Add `packages/core/src/core/ports/reranker.py`: `ICrossEncoderRerankerPort` protocol for cross-encoder reranking and relevance threshold cutoff (>= 0.35).
   - Add `packages/core/src/core/ports/eval.py`: `IDatasetAdapter`, `IEvalMetric`, `IBenchmarkEvaluator` protocols.
3. In `packages/core/src/core/eval/`:
   - Implement `models.py`: `EvalSample`, `MetricResult`, `BenchmarkReport` dataclasses / Pydantic models.
   - Implement `adapters/base.py`: `BaseDatasetAdapter` with `parse_data()` and `load_file()`.
   - Implement `adapters/qasper.py`: `QASPERAdapter` converting QASPER dataset into `EvalSample` list.
   - Implement `adapters/scifact.py`: `SciFactAdapter` converting SciFact claims/rationales into `EvalSample` list.
   - Implement `adapters/pubmedqa.py`: `PubMedQAAdapter` converting PubMedQA into `EvalSample` list with structured abstracts, labels, and decisions.
   - Implement `adapters/regression.py`: `ProjectRegressionAdapter` converting `project_regression_25.json` format into `EvalSample` list.
   - Implement `metrics/`:
     * `base.py`: `BaseEvalMetric`
     * `token_f1.py`: `TokenF1Metric` (SQuAD answer token F1 with lowercase, punctuation, and article stripping).
     * `retrieval_recall.py`: `RetrievalRecallMetric` (Recall@k over evidence chunks).
     * `classification.py`: `ClassificationMetric` (Accuracy and Macro F1 for categorical decisions).
     * `bbox_iou.py`: `BoundingBoxIoUMetric` (Spatial IoU strictly on `[x0, y0, x1, y1, page]`, `page >= 1`, normalized `0.0-1.0`, Top-Left origin).
     * `spatial_geometry.py`: `SpatialGeometryMetric` (Validates spatial invariants: `x0 < x1`, `y0 < y1`, `page >= 1`, `area < 0.95`).
     * `safety.py`: `SafetyMetric` (Adversarial injections, jailbreak attempts, ungrounded citation detection).
   - Implement `evaluators/benchmark_runner.py`: In-memory evaluation runner orchestrating adapters and metrics to generate a `BenchmarkReport`.
4. In `packages/core/tests/eval/`:
   - Create offline in-memory fixtures in `packages/core/tests/eval/fixtures/`:
     * `qasper_subset.json` (curated samples covering extractive, abstractive, yes/no, unanswerable)
     * `scifact_subset.json` (curated claims covering SUPPORT, CONTRADICT, NOT_ENOUGH_INFO)
     * `pubmedqa_subset.json` (curated samples with structured abstracts and yes/no/maybe decisions)
     * `regression_subset.json` (curated samples)
   - Implement exhaustive unit tests in `packages/core/tests/eval/`:
     * `test_qasper_adapter.py`
     * `test_scifact_adapter.py`
     * `test_pubmedqa_adapter.py`
     * `test_regression_adapter.py`
     * `test_token_f1_metric.py`
     * `test_retrieval_recall_metric.py`
     * `test_classification_metric.py`
     * `test_bbox_iou_metric.py`
     * `test_spatial_geometry_metric.py`
     * `test_safety_metric.py`
     * `test_benchmark_runner.py`
5. Verification & Quality Gates:
   - Mandatory invariant: 100% in-memory isolation, zero live network, zero live DB in `packages/core/tests`.
   - Run: `uv run pytest packages/core/tests`
   - Run: `uv run pytest packages/core/tests/eval/ -v`
   - Run: `uv run ruff check packages/core` and `uv run ruff format --check packages/core`
   - Verify all pass with 0 errors and 0 warnings.

Write your complete handoff report to:
/home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/teamwork/worker_m2/handoff.md
When done, notify parent (conversation ID: a2173842-299f-4803-8153-e166837e5cde) via send_message.
