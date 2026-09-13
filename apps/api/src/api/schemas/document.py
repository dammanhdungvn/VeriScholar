"""Document request and response schemas."""

from datetime import datetime
from uuid import UUID

from api.schemas.envelope import PaginatedResponseEnvelope, SingleResponseEnvelope
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


class DocumentListItem(BaseModel):
    """Document summary item in paginated collection."""

    id: UUID = Field(description="Unique document ID")
    filename: str = Field(description="Original uploaded filename")
    title: str | None = Field(
        default=None,
        description="Extracted academic paper title if available",
    )
    status: str = Field(description="Document processing status")
    is_persistent: bool = Field(
        description="Whether document is permanently saved to library",
    )
    created_at: datetime = Field(description="Document creation timestamp")


class DocumentListPaginatedEnvelope(PaginatedResponseEnvelope[DocumentListItem]):
    """Top-level paginated collection envelope for documents."""


class PageMetadataItem(BaseModel):
    """Geometric and orientation metadata for a single PDF page."""

    page_number: int = Field(ge=1, description="1-indexed document page number")
    dimensions: list[float] = Field(
        description="Page dimensions in typographical points [width_pt, height_pt]"
    )
    rotation_deg: int = Field(
        default=0, description="Page rotation orientation in degrees (0, 90, 180, 270)"
    )


class DocumentDetailResponseData(BaseModel):
    """Detailed document metadata including spatial page dimensions."""

    id: UUID = Field(description="Unique document ID")
    filename: str = Field(description="Original uploaded filename")
    title: str | None = Field(
        default=None, description="Extracted academic paper title if available"
    )
    authors: list[str] | None = Field(default=None, description="Extracted list of author names")
    publication_year: int | None = Field(default=None, description="Publication year")
    doi: str | None = Field(default=None, description="Digital Object Identifier")
    page_count: int | None = Field(default=None, description="Total page count")
    chunk_count: int = Field(default=0, description="Total extracted text chunks")
    file_size_bytes: int = Field(description="Total file size in bytes")
    status: str = Field(description="Document processing status")
    is_persistent: bool = Field(description="Whether document is permanently saved to library")
    folder_id: UUID | None = Field(
        default=None, description="Associated folder UUID if categorized"
    )
    pages_metadata: list[PageMetadataItem] = Field(
        default_factory=list,
        description="Spatial page dimensions and rotation for Canvas rendering",
    )
    created_at: datetime = Field(description="Document creation timestamp")


class DocumentDetailEnvelope(SingleResponseEnvelope[DocumentDetailResponseData]):
    """Top-level single resource envelope for document detail."""


class StagesDetail(BaseModel):
    """Execution status breakdown across the 5-stage ingestion pipeline."""

    validation: str = Field(
        default="pending",
        description="Format, integrity and PDF magic bytes validation stage",
    )
    layout_detection: str = Field(
        default="pending",
        description="Two-tier layout and column structure analysis stage",
    )
    ocr: str = Field(
        default="pending",
        description="Text, table and mathematical formula extraction stage",
    )
    chunking: str = Field(
        default="pending",
        description="Semantic chunking and spatial BoundingBox grounding stage",
    )
    embedding: str = Field(
        default="pending",
        description="Dense vector embedding generation and HNSW indexing stage",
    )


class DocumentStatusResponseData(BaseModel):
    """Payload data returned when polling document processing status."""

    id: UUID = Field(description="Unique document identifier")
    status: str = Field(
        description="High-level document status ('uploaded', 'processing', 'completed', 'failed')",
    )
    stage: str = Field(
        description="Active ingestion stage ('queued', 'running_ocr', 'chunking', etc.)",
    )
    progress: int = Field(
        ge=0, le=100, description="Overall processing completion percentage (0-100)"
    )
    stages_detail: StagesDetail = Field(description="Sub-stage breakdown of the ingestion pipeline")
    error_message: str | None = Field(
        default=None, description="Detailed failure description if failed"
    )


class DocumentStatusEnvelope(SingleResponseEnvelope[DocumentStatusResponseData]):
    """Top-level single resource envelope for document status polling."""


class DocumentStarRequest(BaseModel):
    """Payload for starring a document and optionally associating it with a folder."""

    folder_id: UUID | None = Field(
        default=None,
        description="Optional folder UUID to organize the starred document into",
    )


class DocumentStarResponseData(BaseModel):
    """Payload data returned after starring a document."""

    id: UUID = Field(description="Unique document identifier")
    filename: str = Field(description="Original uploaded filename")
    title: str | None = Field(default=None, description="Document academic title")
    status: str = Field(description="Document processing status")
    is_persistent: bool = Field(
        default=True,
        description="Whether document is permanently saved to library (always True after star)",
    )
    folder_id: UUID | None = Field(
        default=None,
        description="Associated folder UUID if organized into a folder",
    )
    updated_at: datetime = Field(description="Last updated timestamp")


class DocumentStarEnvelope(SingleResponseEnvelope[DocumentStarResponseData]):
    """Top-level single resource envelope for document star promotion."""
