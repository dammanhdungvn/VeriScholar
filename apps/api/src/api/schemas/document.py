"""Document request and response schemas."""

from datetime import datetime
from uuid import UUID

from api.schemas.envelope import SingleResponseEnvelope
from pydantic import BaseModel, Field


class DocumentLinks(BaseModel):
    """HATEOAS hypermedia links for document operations."""

    self_url: str = Field(description="URL to retrieve document metadata")
    status_url: str = Field(description="URL to poll document processing progress")
    file_url: str = Field(description="URL to stream binary PDF for Canvas viewer")
    parse_url: str = Field(description="URL to trigger idempotent reparsing")


class DocumentUploadResponseData(BaseModel):
    """Payload data returned after uploading a document."""

    id: UUID = Field(description="Unique document ID")
    filename: str = Field(description="Original uploaded filename")
    file_size_bytes: int = Field(description="Total file size in bytes")
    content_hash: str = Field(description="SHA-256 content digest")
    status: str = Field(description="Document processing status")
    stage: str = Field(description="Pipeline ingestion stage")
    progress: int = Field(description="Processing completion percentage (0-100)")
    is_persistent: bool = Field(description="Whether document is saved to user library")
    session_id: UUID | None = Field(
        default=None,
        description="Linked research session ID if provided",
    )
    created_at: datetime = Field(description="Document creation timestamp")
    links: DocumentLinks = Field(description="Resource navigation links")


class DocumentUploadEnvelope(SingleResponseEnvelope[DocumentUploadResponseData]):
    """Top-level single resource envelope for document upload."""
