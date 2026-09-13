"""Core Domain Layer for VeriScholar.

Follows Hexagonal Architecture principles:
- Pure business logic, invariants, and domain contracts.
- Zero imports of external infrastructure (FastAPI, SQLAlchemy, Uvicorn, Docker, PyMuPDF).
"""

from core.domain.entities.blob import DocumentStorageBlob
from core.domain.entities.chunk import DocumentChunk
from core.domain.entities.document import Document
from core.domain.entities.session_turn import SessionTurn
from core.domain.exceptions import (
    DomainError,
    EntityNotFoundError,
    FileSizeLimitExceededError,
    InvalidBoundingBoxError,
    InvalidContentHashError,
    InvalidDocumentStateTransitionError,
    InvalidPageMetadataError,
    InvariantViolationError,
)
from core.domain.value_objects.bounding_box import BoundingBox
from core.domain.value_objects.enums import (
    BlobStatus,
    DocumentStage,
    DocumentStatus,
    SessionTurnFinishReason,
)
from core.domain.value_objects.page_metadata import PageDimensions, PageMetadata

__all__ = [
    "BlobStatus",
    "BoundingBox",
    "Document",
    "DocumentChunk",
    "DocumentStage",
    "DocumentStatus",
    "DocumentStorageBlob",
    "DomainError",
    "EntityNotFoundError",
    "FileSizeLimitExceededError",
    "InvalidBoundingBoxError",
    "InvalidContentHashError",
    "InvalidDocumentStateTransitionError",
    "InvalidPageMetadataError",
    "InvariantViolationError",
    "PageDimensions",
    "PageMetadata",
    "SessionTurn",
    "SessionTurnFinishReason",
]
