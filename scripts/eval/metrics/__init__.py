"""Pluggable Evaluation Metrics Engine for VeriScholar API Harness."""

from scripts.eval.metrics.base import BaseEvalMetric, MetricResult
from scripts.eval.metrics.bbox_iou import BoundingBoxIoUMetric
from scripts.eval.metrics.cascading_f1 import CascadingF1Metric
from scripts.eval.metrics.entity_sanity import EntitySanityMetric
from scripts.eval.metrics.groundedness_f1 import GroundednessF1Metric
from scripts.eval.metrics.retrieval_recall import RetrievalRecallMetric
from scripts.eval.metrics.safety import SafetyMetric
from scripts.eval.metrics.spatial_geometry import SpatialGeometryMetric
from scripts.eval.metrics.text_integrity import TextIntegrityMetric

__all__ = [
    "BaseEvalMetric",
    "BoundingBoxIoUMetric",
    "CascadingF1Metric",
    "EntitySanityMetric",
    "GroundednessF1Metric",
    "MetricResult",
    "RetrievalRecallMetric",
    "SafetyMetric",
    "SpatialGeometryMetric",
    "TextIntegrityMetric",
]
