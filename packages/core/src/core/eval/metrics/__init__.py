"""Evaluation metrics collection for VeriScholar AI benchmarks."""

from core.eval.metrics.base import BaseEvalMetric
from core.eval.metrics.bbox_iou import BoundingBoxIoUMetric, compute_box_iou
from core.eval.metrics.classification import ClassificationMetric, compute_macro_f1
from core.eval.metrics.retrieval_recall import RetrievalRecallMetric
from core.eval.metrics.safety import SafetyMetric
from core.eval.metrics.spatial_geometry import SpatialGeometryMetric
from core.eval.metrics.token_f1 import TokenF1Metric, compute_token_f1, normalize_answer

__all__ = [
    "BaseEvalMetric",
    "BoundingBoxIoUMetric",
    "ClassificationMetric",
    "RetrievalRecallMetric",
    "SafetyMetric",
    "SpatialGeometryMetric",
    "TokenF1Metric",
    "compute_box_iou",
    "compute_macro_f1",
    "compute_token_f1",
    "normalize_answer",
]
