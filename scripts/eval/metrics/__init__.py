"""Pluggable Evaluation Metrics Engine for VeriScholar API Harness."""

from scripts.eval.metrics.base import BaseEvalMetric, MetricResult
from scripts.eval.metrics.cascading_f1 import CascadingF1Metric
from scripts.eval.metrics.entity_sanity import EntitySanityMetric
from scripts.eval.metrics.spatial_geometry import SpatialGeometryMetric
from scripts.eval.metrics.text_integrity import TextIntegrityMetric

__all__ = [
    "BaseEvalMetric",
    "CascadingF1Metric",
    "EntitySanityMetric",
    "MetricResult",
    "SpatialGeometryMetric",
    "TextIntegrityMetric",
]
