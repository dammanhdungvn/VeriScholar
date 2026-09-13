"""DocumentStorageBlob Domain Entity.

Represents a deduplicated binary file blob in Content-Addressable Storage (CAS).
Tracks reference counts across multiple user documents to uphold the Zero-Retention Guarantee.
"""

import re
from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.domain.exceptions import (
    FileSizeLimitExceededError,
    InvalidContentHashError,
    InvariantViolationError,
)
from core.domain.value_objects.enums import BlobStatus

MAX_FILE_SIZE_BYTES = 52_428_800  # 50 MB
SHA256_REGEX = re.compile(r"^[a-f0-9]{64}$")


class DocumentStorageBlob(BaseModel):
    """Domain Entity representing a CAS storage blob."""

    model_config = ConfigDict(validate_assignment=True)

    id: UUID = Field(default_factory=uuid4, description="Unique blob identifier")
    content_hash: str = Field(description="Hexadecimal SHA-256 hash of file contents")
    storage_path: str = Field(description="Relative or absolute storage path")
    file_size_bytes: int = Field(gt=0, description="File size in bytes")
    ref_count: int = Field(default=1, ge=0, description="Active references count across documents")
    status: BlobStatus = Field(default=BlobStatus.PROCESSING, description="Processing status")
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

    def increment_reference(self) -> None:
        """Increment reference count when another document links to this existing blob."""
        self.ref_count += 1
        self.updated_at = datetime.now(UTC)

    def decrement_reference(self) -> None:
        """Decrement reference count when a document is deleted.

        Raises InvariantViolationError if ref_count drops below 0.
        """
        if self.ref_count <= 0:
            raise InvariantViolationError(f"Cannot decrement ref_count below 0 for blob {self.id}.")
        self.ref_count -= 1
        self.updated_at = datetime.now(UTC)

    @property
    def is_orphan(self) -> bool:
        """Check if blob has zero active references and is eligible for physical purge."""
        return self.ref_count == 0

    def mark_completed(self) -> None:
        """Mark blob processing as successfully completed."""
        self.status = BlobStatus.COMPLETED
        self.updated_at = datetime.now(UTC)

    def mark_failed(self) -> None:
        """Mark blob processing as failed."""
        self.status = BlobStatus.FAILED
        self.updated_at = datetime.now(UTC)
