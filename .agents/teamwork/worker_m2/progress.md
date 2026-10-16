# Progress Tracking — worker_m2

**Last visited**: 2026-10-15T03:20:00Z
**Milestone**: M2_PUBLIC_BENCHMARKS
**Current Status**: Complete & Verified

## Tasks
- [x] 1. Update embedding dimension validation in `packages/core/src/core/domain/entities/chunk.py` (accept 1024 or 1536)
- [x] 2. Create ports in `packages/core/src/core/ports/`:
  - [x] `retrieval.py` (`IRetrievalSearchPort`)
  - [x] `reranker.py` (`ICrossEncoderRerankerPort`)
  - [x] `eval.py` (`IDatasetAdapter`, `IEvalMetric`, `IBenchmarkEvaluator`)
- [x] 3. Create evaluation domain models in `packages/core/src/core/eval/models.py`:
  - [x] `EvalSample`
  - [x] `MetricResult`
  - [x] `BenchmarkReport`
  - [x] `EvalPrediction`
- [x] 4. Create adapters in `packages/core/src/core/eval/adapters/`:
  - [x] `base.py` (`BaseDatasetAdapter`)
  - [x] `qasper.py` (`QASPERAdapter`)
  - [x] `scifact.py` (`SciFactAdapter`)
  - [x] `pubmedqa.py` (`PubMedQAAdapter`)
  - [x] `regression.py` (`ProjectRegressionAdapter`)
  - [x] `__init__.py`
- [x] 5. Create metrics in `packages/core/src/core/eval/metrics/`:
  - [x] `base.py` (`BaseEvalMetric`)
  - [x] `token_f1.py` (`TokenF1Metric` with SQuAD answer normalization)
  - [x] `retrieval_recall.py` (`RetrievalRecallMetric`)
  - [x] `classification.py` (`ClassificationMetric` - accuracy and macro F1)
  - [x] `bbox_iou.py` (`BoundingBoxIoUMetric` - [x0, y0, x1, y1, page] spatial IoU)
  - [x] `spatial_geometry.py` (`SpatialGeometryMetric` - coordinates, bounds, area < 0.95)
  - [x] `safety.py` (`SafetyMetric` - prompt injection, active abstention, refutation, tenant isolation, ungrounded citations)
  - [x] `__init__.py`
- [x] 6. Create benchmark runner in `packages/core/src/core/eval/evaluators/`:
  - [x] `benchmark_runner.py`
  - [x] `__init__.py`
- [x] 7. Create offline fixture files in `packages/core/tests/eval/fixtures/`:
  - [x] `qasper_subset.json`
  - [x] `scifact_subset.json`
  - [x] `pubmedqa_subset.json`
  - [x] `regression_subset.json`
- [x] 8. Implement exhaustive unit tests in `packages/core/tests/eval/`:
  - [x] `test_qasper_adapter.py`
  - [x] `test_scifact_adapter.py`
  - [x] `test_pubmedqa_adapter.py`
  - [x] `test_regression_adapter.py`
  - [x] `test_token_f1_metric.py`
  - [x] `test_retrieval_recall_metric.py`
  - [x] `test_classification_metric.py`
  - [x] `test_bbox_iou_metric.py`
  - [x] `test_spatial_geometry_metric.py`
  - [x] `test_safety_metric.py`
  - [x] `test_benchmark_runner.py`
  - [x] `test_chunk_dimensions.py`
- [x] 9. Verify quality gates:
  - [x] `uv run pytest packages/core/tests` (135 passed in 0.45s, 100% in-memory)
  - [x] `uv run ruff check packages/core` (0 errors)
  - [x] `uv run ruff format --check packages/core` (0 errors)
- [x] 10. Update BRIEFING.md and write `handoff.md`.
