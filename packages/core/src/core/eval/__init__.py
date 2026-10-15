"""Core Evaluation Domain & Public Benchmark Suite.

Provides in-memory datasets, adapters, metrics, and runners for scientific AI evaluation.
"""

from core.eval.adapters import (
    BaseDatasetAdapter,
    ProjectRegressionAdapter,
    PubMedQAAdapter,
    QASPERAdapter,
    SciFactAdapter,
)
from core.eval.evaluators import BenchmarkRunner
from core.eval.metrics import (
    BaseEvalMetric,
    BoundingBoxIoUMetric,
    ClassificationMetric,
    RetrievalRecallMetric,
    SafetyMetric,
    SpatialGeometryMetric,
    TokenF1Metric,
)
from core.eval.models import BenchmarkReport, EvalPrediction, EvalSample, MetricResult

__all__ = [
    "BaseDatasetAdapter",
    "BaseEvalMetric",
    "BenchmarkReport",
    "BenchmarkRunner",
    "BoundingBoxIoUMetric",
    "ClassificationMetric",
    "EvalPrediction",
    "EvalSample",
    "MetricResult",
    "ProjectRegressionAdapter",
    "PubMedQAAdapter",
    "QASPERAdapter",
    "RetrievalRecallMetric",
    "SafetyMetric",
    "SciFactAdapter",
    "SpatialGeometryMetric",
    "TokenF1Metric",
]
