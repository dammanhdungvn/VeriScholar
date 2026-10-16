# Milestone 2 Handoff Report: Core Evaluation Domain & Public Benchmark Suite

**Agent**: worker_m2 (Roles: implementer, qa, specialist)  
**Recipient**: Orchestrator (Conversation ID: `a2173842-299f-4803-8153-e166837e5cde`)  
**Workspace**: `/home/dammanhdungvn/Downloads/Workspace/VeriScholar`  
**Date**: 2026-10-15  

---

## 1. Observation

1. **Initial Codebase Baseline in `packages/core`**:
   - `packages/core/src/core/domain/entities/chunk.py:16-56` enforced a single constant `BGE_M3_EMBEDDING_DIM = 1024` with `InvariantViolationError` if `len(embedding) != 1024`. This rejected 1536-dimensional embeddings used by OpenAI `text-embedding-3-small` in `apps/api/src/api/db/models/chunk.py:27` and `tests/evals/test_parse_chunking_eval.py:221`.
   - `packages/core/src/core/ports/` lacked protocols for hybrid retrieval (`IRetrievalSearchPort`), cross-encoder reranking (`ICrossEncoderRerankerPort`), and evaluation domain contracts (`IDatasetAdapter`, `IEvalMetric`, `IBenchmarkEvaluator`).
   - `packages/core/src/core/eval/` and `packages/core/tests/eval/` did not exist; evaluation logic was fragmented across `scripts/eval/` and `tests/evals/`.
   - `scripts/eval` had QASPER and SciFact adapters, but completely lacked a `PubMedQAAdapter`.
   - Baseline unit test run:
     ```bash
     uv run pytest packages/core/tests
     ```
     Result: **76 passed in 0.30s** with 100% in-memory isolation.

2. **Executed Modifications & Implementation**:
   - `packages/core/src/core/domain/entities/chunk.py`:
     Added `OPENAI_EMBEDDING_DIM = 1536` and `VALID_EMBEDDING_DIMS = (BGE_M3_EMBEDDING_DIM, OPENAI_EMBEDDING_DIM)`. Updated `validate_embedding_dimensions` and `attach_embedding` to allow either 1024 or 1536 dimensions.
   - `packages/core/src/core/ports/`:
     - Added `retrieval.py` (`IRetrievalSearchPort` protocol with `search_candidates`).
     - Added `reranker.py` (`ICrossEncoderRerankerPort` protocol with `rerank` and `DEFAULT_RELEVANCE_THRESHOLD = 0.35`).
     - Added `eval.py` (`IDatasetAdapter`, `IEvalMetric`, `IBenchmarkEvaluator` protocols).
     - Applied `@runtime_checkable` to all protocols to support runtime validation.
   - `packages/core/src/core/eval/`:
     - `models.py`: `EvalSample`, `MetricResult`, `BenchmarkReport`, `EvalPrediction` with serialization (`to_dict`, `from_dict`).
     - `adapters/`: `BaseDatasetAdapter`, `QASPERAdapter`, `SciFactAdapter`, `PubMedQAAdapter`, `ProjectRegressionAdapter`.
     - `metrics/`: `BaseEvalMetric`, `TokenF1Metric` (SQuAD lowercase, punctuation, and article stripping), `RetrievalRecallMetric` (Recall@k over evidence chunks), `ClassificationMetric` (accuracy and macro F1 for SciFact and PubMedQA), `BoundingBoxIoUMetric` (spatial IoU strictly on `[x0, y0, x1, y1, page]`, `page >= 1`, normalized `[0.0, 1.0]`, Top-Left origin), `SpatialGeometryMetric` (geometric invariants `x0 < x1`, `y0 < y1`, `page >= 1`, `area < 0.95`), `SafetyMetric` (prompt injection interception, active abstention, false-premise refutation, tenant 403 isolation, ungrounded citation detection).
     - `evaluators/benchmark_runner.py`: `BenchmarkRunner` implementing `IBenchmarkEvaluator`.
   - `packages/core/tests/eval/fixtures/`:
     - `qasper_subset.json`: Extractive, abstractive, boolean (yes/no), and unanswerable QA samples.
     - `scifact_subset.json`: SUPPORT, CONTRADICT, and NOT_ENOUGH_INFO claims with evidence sentence mappings and bounding boxes.
     - `pubmedqa_subset.json`: Biomedical questions with structured abstracts (BACKGROUND, METHODS, RESULTS) and yes/no/maybe decisions.
     - `regression_subset.json`: Curated cases across all 5 regression groups.
   - `packages/core/tests/eval/`:
     - 12 comprehensive unit test files: `test_qasper_adapter.py`, `test_scifact_adapter.py`, `test_pubmedqa_adapter.py`, `test_regression_adapter.py`, `test_token_f1_metric.py`, `test_retrieval_recall_metric.py`, `test_classification_metric.py`, `test_bbox_iou_metric.py`, `test_spatial_geometry_metric.py`, `test_safety_metric.py`, `test_benchmark_runner.py`, `test_chunk_dimensions.py`.

3. **Verification Command Results**:
   - `uv run pytest packages/core/tests`:
     ```text
     ============================= 135 passed in 0.45s ==============================
     ```
     (All 76 legacy domain tests + 59 new evaluation tests passed with 0 failures).
   - `uv run pytest packages/core/tests/eval/ -v`:
     ```text
     ============================== 59 passed in 0.18s ==============================
     ```
   - `uv run ruff check packages/core`:
     ```text
     All checks passed!
     ```
   - `uv run ruff format --check packages/core`:
     ```text
     85 files already formatted
     ```
   - `uv run pytest packages/core/tests/domain/test_hexagonal_invariants.py`:
     ```text
     1 passed in 0.01s (zero prohibited framework/infrastructure imports).
     ```

---

## 2. Logic Chain

1. **Embedding Dimension Validation** (Observation 1 -> Step 1):
   - To support multi-model pipelines where dense embeddings may come from BGE-M3 (1024 dimensions) or OpenAI `text-embedding-3-small` (1536 dimensions), `DocumentChunk` must validate against `VALID_EMBEDDING_DIMS = (1024, 1536)`.
   - Both dimensions pass invariant validation, while invalid dimensions (e.g. 128, 512, 768, 2048) continue to raise `InvariantViolationError`. Verified by `test_chunk_dimensions.py`.

2. **Hexagonal Architecture Compliance** (Observation 1 & AGENTS.md -> Step 2):
   - By creating `packages/core/src/core/ports/` protocols (`retrieval.py`, `reranker.py`, `eval.py`), core domain rules remain decoupled from concrete database drivers (pgvector, sqlalchemy) and concrete rerank APIs (Cohere API, HuggingFace transformers).
   - Adding `@runtime_checkable` ensures adapters and evaluators can be validated dynamically at runtime.

3. **Decoupled Evaluation Metrics** (Observation 1 & 2 -> Step 3):
   - Evaluation metrics are cleanly separated into single-responsibility evaluators:
     * `TokenF1Metric`: Evaluates generated answer tokens vs golden answer tokens with SQuAD article and punctuation stripping.
     * `RetrievalRecallMetric`: Evaluates retrieved chunk passages against golden evidence passages.
     * `ClassificationMetric`: Evaluates categorical decision labels (`SUPPORT`/`CONTRADICT`/`NOT_ENOUGH_INFO`, `yes`/`no`/`maybe`) calculating exact accuracy and balanced macro F1.
     * `BoundingBoxIoUMetric`: Evaluates spatial 2D IoU strictly on `[x0, y0, x1, y1, page]`, ensuring `page >= 1` and normalized `0.0-1.0`.
     * `SpatialGeometryMetric`: Audits geometric invariants (`x0 < x1`, `y0 < y1`, `page >= 1`, `area < 0.95`).
     * `SafetyMetric`: Validates prompt injection interception, active abstention on unanswerable queries, false-premise refutation, 403 tenant isolation, and ungrounded citation detection.
   - This eliminates the metric conflation observed in legacy eval scripts.

4. **100% In-Memory Test Isolation** (Observation 1 & 3 -> Step 4):
   - All tests in `packages/core/tests/eval/` execute against in-memory offline fixtures (`qasper_subset.json`, `scifact_subset.json`, `pubmedqa_subset.json`, `regression_subset.json`).
   - The entire 135-test suite runs in under 0.50 seconds without requiring external network connectivity or live databases.

---

## 3. Caveats

1. **Downstream API & CLI Runners**:
   - The CLI runner `scripts/eval/run_eval.py` currently imports from `scripts.eval.adapters` and `scripts.eval.metrics`. In Milestone 3 and Milestone 5, `scripts/eval` should be transitioned to import standardized domain models and metrics from `packages/core/src/core/eval/`.
2. **Corpus Expansion**:
   - Offline fixtures in `packages/core/tests/eval/fixtures/` are lightweight curated subsets (3-5 samples per benchmark) designed for sub-second deterministic CI runs. Nightly full benchmark evaluations should use full dataset files via `download_benchmarks.py`.
3. **No other caveats**: All requirements specified for Milestone 2 have been implemented and verified.

---

## 4. Conclusion

Milestone 2 (Core Evaluation Domain & Public Benchmark Suite) is **100% complete**:
- `DocumentChunk` embedding validation supports both 1024 and 1536 dimensions.
- Hexagonal ports for `IRetrievalSearchPort`, `ICrossEncoderRerankerPort`, `IDatasetAdapter`, `IEvalMetric`, and `IBenchmarkEvaluator` are defined.
- Core evaluation domain models, adapters for QASPER, SciFact, PubMedQA, and Project Regression, decoupled metric engines, and the `BenchmarkRunner` are implemented in `packages/core/src/core/eval/`.
- 59 comprehensive unit tests and offline fixtures verify the evaluation domain in `packages/core/tests/eval/`.
- All quality gates pass cleanly: `135 passed in 0.45s` across `packages/core/tests`, 0 ruff lint errors, 0 ruff format errors.

---

## 5. Verification Method

To independently verify the implementation and quality gates:

1. **Run Full Core Test Suite**:
   ```bash
   uv run pytest packages/core/tests
   ```
   *Expected outcome*: 135 passed in < 0.5s with 100% in-memory isolation.

2. **Run Evaluation Unit Test Suite Verbose**:
   ```bash
   uv run pytest packages/core/tests/eval/ -v
   ```
   *Expected outcome*: 59 passed in < 0.25s.

3. **Verify Zero Ruff Errors & Clean Formatting**:
   ```bash
   uv run ruff check packages/core
   uv run ruff format --check packages/core
   ```
   *Expected outcome*: Zero errors, zero warnings, all files formatted cleanly.

4. **Verify Hexagonal Domain Invariant**:
   ```bash
   uv run pytest packages/core/tests/domain/test_hexagonal_invariants.py
   ```
   *Expected outcome*: 1 passed with zero infrastructure/framework imports.

5. **Inspect Key Source Files**:
   - `packages/core/src/core/domain/entities/chunk.py` (lines 14-55)
   - `packages/core/src/core/ports/retrieval.py`
   - `packages/core/src/core/ports/reranker.py`
   - `packages/core/src/core/ports/eval.py`
   - `packages/core/src/core/eval/models.py`
   - `packages/core/src/core/eval/adapters/`
   - `packages/core/src/core/eval/metrics/`
   - `packages/core/src/core/eval/evaluators/benchmark_runner.py`
   - `packages/core/tests/eval/fixtures/`

6. **Invalidation Conditions**:
   - If `DocumentChunk` rejects valid 1536-dimensional embeddings or fails to reject invalid dimensions.
   - If tests in `packages/core/tests/eval/` require network calls to HuggingFace or PubMed.
   - If bounding box coordinates are downgraded from `[x0, y0, x1, y1, page]`, `0.0 <= x0 < x1 <= 1.0`, `0.0 <= y0 < y1 <= 1.0`, `page >= 1`, Top-Left origin.
