"""Domain Value Objects for VeriScholar Core."""

from core.domain.value_objects.bounding_box import BoundingBox
from core.domain.value_objects.enums import (
    AcademicRank,
    BlobStatus,
    DocumentStage,
    DocumentStatus,
    SessionActiveTab,
    SessionTurnFinishReason,
    ThemePreference,
)
from core.domain.value_objects.page_metadata import PageDimensions, PageMetadata
from core.domain.value_objects.viewport_state import ViewportState

__all__ = [
    "AcademicRank",
    "BlobStatus",
    "BoundingBox",
    "DocumentStage",
    "DocumentStatus",
    "PageDimensions",
    "PageMetadata",
    "SessionActiveTab",
    "SessionTurnFinishReason",
    "ThemePreference",
    "ViewportState",
]
