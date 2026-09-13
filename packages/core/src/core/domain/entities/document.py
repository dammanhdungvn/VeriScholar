"""Document Domain Entity.

Represents an academic paper uploaded by a specific user.
Encapsulates metadata, lifecycle progression, page geometric metadata,
and star persistence states.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.domain.entities.blob import MAX_FILE_SIZE_BYTES, SHA256_REGEX
from core.domain.exceptions import (
    FileSizeLimitExceededError,
    InvalidContentHashError,
    InvalidDocumentStateTransitionError,
)
from core.domain.value_objects.enums import DocumentStage, DocumentStatus
from core.domain.value_objects.page_metadata import PageMetadata


class Document(BaseModel):
    """Domain Entity representing a user-owned scholarly document."""

    model_config = ConfigDict(validate_assignment=True)

    id: UUID = Field(default_factory=uuid4, description="Unique document identifier")
    user_id: UUID = Field(description="Owning user identifier")
    blob_id: UUID | None = Field(default=None, description="Linked storage blob identifier")
    folder_id: UUID | None = Field(default=None, description="Library folder container identifier")
    filename: str = Field(min_length=1, max_length=255, description="Original uploaded filename")
    title: str | None = Field(default=None, description="Extracted academic paper title")
    authors: list[str] = Field(default_factory=list, description="Extracted list of author names")
    publication_year: int | None = Field(default=None, ge=1800, description="Publication year")
    doi: str | None = Field(default=None, description="Digital Object Identifier")
    content_hash: str = Field(description="SHA-256 hash of the document content")
    file_size_bytes: int = Field(gt=0, description="File size in bytes")
    page_count: int | None = Field(default=None, gt=0, description="Total number of pages")
    chunk_count: int = Field(default=0, ge=0, description="Total number of extracted chunks")
    pages_metadata: list[PageMetadata] = Field(
        default_factory=list,
        description="List of geometrical page dimensions and rotation orientations",
    )
    parsed_metadata: dict[str, Any] | None = Field(
        default=None, description="Structured TOC, abstract, and sections"
    )
    status: DocumentStatus = Field(
        default=DocumentStatus.UPLOADED, description="Overall document status"
    )
    stage: DocumentStage = Field(default=DocumentStage.QUEUED, description="Pipeline stage")
    progress: int = Field(default=0, ge=0, le=100, description="Processing progress percentage")
    error_message: str | None = Field(default=None, description="Failure description if failed")
    is_persistent: bool = Field(default=False, description="Whether document is saved to library")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("content_hash")
    @classmethod
    def validate_hash_format(cls, v: str) -> str:
        """Enforce strict 64-character lowercase hexadecimal SHA-256 format."""
        normalized = v.lower().strip()
        if not SHA256_REGEX.match(normalized):
            raise InvalidContentHashError(
                f"Invalid content hash '{v}'. Must be a 64-char lowercase SHA-256 hex string."
            )
        return normalized

    @field_validator("file_size_bytes")
    @classmethod
    def validate_size_ceiling(cls, v: int) -> int:
        """Enforce maximum document file size of 50MB."""
        if v > MAX_FILE_SIZE_BYTES:
            raise FileSizeLimitExceededError(
                f"File size {v} bytes exceeds maximum limit of {MAX_FILE_SIZE_BYTES} bytes (50MB)."
            )
        return v

    def start_processing(self) -> None:
        """Transition document status to PROCESSING and set initial stage."""
        if self.status == DocumentStatus.COMPLETED:
            raise InvalidDocumentStateTransitionError(
                f"Cannot re-process document {self.id} that is already COMPLETED."
            )
        self.status = DocumentStatus.PROCESSING
        self.stage = DocumentStage.PARSING
        self.progress = 10
        self.error_message = None
        self.updated_at = datetime.now(UTC)

    def advance_stage(self, stage: DocumentStage, progress: int) -> None:
        """Advance document processing stage and progress indicator."""
        if self.status != DocumentStatus.PROCESSING:
            raise InvalidDocumentStateTransitionError(
                f"Cannot advance stage for document {self.id} in state {self.status}."
            )
        self.stage = stage
        self.progress = min(max(progress, 0), 100)
        self.updated_at = datetime.now(UTC)

    def mark_completed(
        self,
        page_count: int,
        chunk_count: int,
        pages_metadata: list[PageMetadata],
        title: str | None = None,
        authors: list[str] | None = None,
    ) -> None:
        """Transition document to COMPLETED state and attach extracted metadata."""
        self.status = DocumentStatus.COMPLETED
        self.stage = DocumentStage.COMPLETED
        self.progress = 100
        self.page_count = page_count
        self.chunk_count = chunk_count
        self.pages_metadata = pages_metadata
        if title:
            self.title = title
        if authors is not None:
            self.authors = authors
        self.error_message = None
        self.updated_at = datetime.now(UTC)

    def mark_failed(self, error_message: str) -> None:
        """Transition document to FAILED state and record error diagnostics."""
        self.status = DocumentStatus.FAILED
        self.stage = DocumentStage.FAILED
        self.error_message = error_message
        self.updated_at = datetime.now(UTC)

    def set_persistence(self, persistent: bool) -> None:
        """Toggle persistent library retention (Star / Unstar)."""
        self.is_persistent = persistent
        self.updated_at = datetime.now(UTC)
