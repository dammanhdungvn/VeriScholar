"""Evaluation dataset adapters for public benchmarks and project regression."""

from core.eval.adapters.base import BaseDatasetAdapter
from core.eval.adapters.pubmedqa import PubMedQAAdapter
from core.eval.adapters.qasper import QASPERAdapter
from core.eval.adapters.regression import ProjectRegressionAdapter
from core.eval.adapters.scifact import SciFactAdapter

__all__ = [
    "BaseDatasetAdapter",
    "ProjectRegressionAdapter",
    "PubMedQAAdapter",
    "QASPERAdapter",
    "SciFactAdapter",
]
