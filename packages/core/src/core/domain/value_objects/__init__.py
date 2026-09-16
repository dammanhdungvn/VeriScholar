"""Domain Value Objects for VeriScholar Core."""

from core.domain.value_objects.bounding_box import BoundingBox
from core.domain.value_objects.enums import (
    BlobStatus,
    DocumentStage,
    DocumentStatus,
    SessionTurnFinishReason,
)
from core.domain.value_objects.page_metadata import PageDimensions, PageMetadata
from core.domain.value_objects.pdf_annotation import AnnotationCategory, PdfAnnotation

__all__ = [
    "AnnotationCategory",
    "BlobStatus",
    "BoundingBox",
    "DocumentStage",
    "DocumentStatus",
    "PageDimensions",
    "PageMetadata",
    "PdfAnnotation",
    "SessionTurnFinishReason",
]
