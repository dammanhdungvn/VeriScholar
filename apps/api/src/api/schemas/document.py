"""Document request and response schemas."""

from datetime import datetime
from uuid import UUID

from api.schemas.envelope import PaginatedResponseEnvelope, SingleResponseEnvelope
from pydantic import BaseModel, ConfigDict, Field, model_validator


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

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"folder_id": None},
                {"folder_id": "8a391512-4217-48f1-a1b7-d1fa18600d89"},
            ]
        }
    )

    folder_id: UUID | None = Field(
        default=None,
        description="Optional folder UUID to organize the starred document into (default: null)",
        examples=[None],
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


class DocumentParseRequest(BaseModel):
    """Configuration options for triggering or re-triggering document parsing."""

    chunk_size: int = Field(
        default=512,
        ge=100,
        le=2048,
        description="Target token count per semantic chunk (default: 512)",
    )
    chunk_overlap: int = Field(
        default=50,
        ge=0,
        le=200,
        description="Token overlap between adjacent chunks (default: 50)",
    )
    extract_tables: bool = Field(
        default=True,
        description="Whether to perform specialized layout detection for tables and figures",
    )
    force_reparse: bool = Field(
        default=False,
        description="Force re-parsing even if document was already processed or is processing",
    )

    @model_validator(mode="after")
    def validate_overlap_less_than_size(self) -> "DocumentParseRequest":
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be strictly less than chunk_size")
        return self


class DocumentParseLinks(BaseModel):
    """Navigation links for polling parsing progress and accessing parsed document."""

    status_url: str = Field(description="URL to poll parsing progress and stage breakdown")
    detail_url: str = Field(description="URL to access document metadata and pages")


class DocumentParseResponseData(BaseModel):
    """Payload data returned when a document parse task is accepted."""

    id: UUID = Field(description="Unique document identifier")
    status: str = Field(description="Updated document status ('processing', 'completed')")
    stage: str = Field(description="Ingestion pipeline stage ('validation', 'queued')")
    progress: int = Field(
        ge=0,
        le=100,
        description="Initial parsing progress percentage (0-100)",
    )
    message: str = Field(description="Human-readable guidance message regarding the parse task")
    links: DocumentParseLinks = Field(description="HATEOAS resource links")


class DocumentParseEnvelope(SingleResponseEnvelope[DocumentParseResponseData]):
    """Top-level single resource envelope for document parse initiation."""


class ParsedReferenceItemSchema(BaseModel):
    """Structured fields parsed from academic citation text."""

    title: str | None = Field(default=None, description="Extracted scholarly paper title")
    authors: list[str] = Field(default_factory=list, description="Extracted list of author names")
    year: int | None = Field(default=None, description="Publication year")
    arxiv_id: str | None = Field(default=None, description="arXiv identifier if present")
    doi: str | None = Field(default=None, description="Digital Object Identifier if present")


class ReferenceItemResponse(BaseModel):
    """Single reference item within the extracted bibliography."""

    ref_index: int = Field(ge=1, description="1-indexed reference position")
    raw_text: str = Field(description="Full raw reference citation string")
    parsed: ParsedReferenceItemSchema = Field(description="Parsed academic metadata")


class DocumentExtractReferencesRequest(BaseModel):
    """Configuration options for extracting document references."""

    model_config = ConfigDict(extra="forbid")

    force_reextract: bool = Field(
        default=False,
        description="If True, bypass database cache and re-extract references from PDF file",
    )


class DocumentExtractReferencesResponseData(BaseModel):
    """Payload data returned when document references are extracted."""

    document_id: UUID = Field(description="Unique document identifier")
    total_extracted: int = Field(ge=0, description="Total number of extracted references")
    references: list[ReferenceItemResponse] = Field(
        default_factory=list, description="List of structured reference items"
    )


class DocumentExtractReferencesEnvelope(
    SingleResponseEnvelope[DocumentExtractReferencesResponseData]
):
    """Top-level single resource envelope for document reference extraction."""


class DocumentSectionResponse(BaseModel):
    """Section or heading item in the document's structure."""

    title: str = Field(description="Heading or section title text")
    page_number: int = Field(ge=1, description="1-indexed page number where heading is located")
    bounding_boxes: list[list[float]] = Field(
        default_factory=list,
        description="Normalized bounding boxes [[x0, y0, x1, y1, page], ...]",
    )


class DocumentStructureData(BaseModel):
    """Structured outline, abstract, and sections of an academic paper."""

    document_id: UUID = Field(description="Unique document identifier")
    title: str | None = Field(default=None, description="Extracted scholarly paper title")
    abstract: str | None = Field(default=None, description="Extracted paper abstract text")
    abstract_bounding_boxes: list[list[float]] = Field(
        default_factory=list,
        description="Normalized bounding boxes covering abstract [[x0, y0, x1, y1, page], ...]",
    )
    sections: list[DocumentSectionResponse] = Field(
        default_factory=list,
        description="Ordered list of document headings and sections",
    )


class DocumentStructureEnvelope(SingleResponseEnvelope[DocumentStructureData]):
    """Top-level single resource envelope for document structure."""


class DocumentChunkItem(BaseModel):
    """Single chunk item in paginated collection."""

    id: UUID = Field(description="Unique chunk identifier")
    document_id: UUID = Field(description="Parent document identifier")
    chunk_index: int = Field(ge=0, description="0-indexed sequence position in document")
    page_number: int = Field(ge=1, description="1-indexed page where chunk begins")
    content: str | None = Field(
        default=None,
        description=(
            "Textual content of the chunk. Returned as null when "
            "include_content=false to save bandwidth."
        ),
    )
    bounding_boxes: list[list[float | int]] = Field(
        default_factory=list,
        description="List of normalized [x0, y0, x1, y1, page] bounding boxes for Canvas overlay",
    )
    token_count: int = Field(gt=0, description="Calculated token count of chunk content")


class DocumentChunkPaginatedEnvelope(PaginatedResponseEnvelope[DocumentChunkItem]):
    """Top-level RFC 8288 paginated collection envelope for document chunks."""


class DocumentChunkNavigationLinks(BaseModel):
    """Hypermedia navigation links for chunk detail and reader traversal."""

    self: str = Field(description="Canonical URI of current chunk")
    document: str = Field(description="Parent document resource URI")
    chunks: str = Field(description="Collection URI of all chunks for parent document")
    prev_chunk: str | None = Field(
        default=None,
        description="URI of sequentially preceding chunk, if available",
    )
    next_chunk: str | None = Field(
        default=None,
        description="URI of sequentially succeeding chunk, if available",
    )


class DocumentChunkDetailData(BaseModel):
    """Detailed representation of an academic evidence chunk."""

    id: UUID = Field(description="Unique chunk identifier")
    document_id: UUID = Field(description="Parent document identifier")
    chunk_index: int = Field(ge=0, description="0-indexed sequence position in document")
    page_number: int = Field(ge=1, description="1-indexed page where chunk begins")
    content: str = Field(description="Full textual content of the chunk")
    bounding_boxes: list[list[float | int]] = Field(
        default_factory=list,
        description="List of normalized [x0, y0, x1, y1, page] bounding boxes for Canvas overlay",
    )
    token_count: int = Field(gt=0, description="Calculated token count of chunk content")
    embedding_dimension: int | None = Field(
        default=None,
        description="Dimension size of dense vector embedding if generated",
    )
    created_at: datetime | None = Field(
        default=None,
        description="Timestamp when chunk was extracted and persisted",
    )
    updated_at: datetime | None = Field(
        default=None,
        description="Timestamp of last chunk update",
    )
    links: DocumentChunkNavigationLinks = Field(
        description="Hypermedia navigational links for sequential reading traversal"
    )


class DocumentChunkDetailEnvelope(SingleResponseEnvelope[DocumentChunkDetailData]):
    """Top-level single resource envelope for document chunk detail."""


class SummaryPointResponse(BaseModel):
    """Grounded summary point containing textual synthesis and visual citations."""

    text: str = Field(description="Synthesized summary claim or narrative")
    bounding_boxes: list[list[float | int]] = Field(
        default_factory=list,
        description="List of normalized [x0, y0, x1, y1, page] bounding boxes for Canvas grounding",
    )


class DocumentSummaryData(BaseModel):
    """Singleton 3-point grounded summary representation."""

    document_id: UUID = Field(description="Associated parent document UUID")
    problem_statement: SummaryPointResponse = Field(
        description="Core research problem addressed by the paper"
    )
    contributions: SummaryPointResponse = Field(
        description="Key contributions, methodology, and novel proposals"
    )
    limitations: SummaryPointResponse = Field(
        description="Remaining limitations, assumptions, and research gaps"
    )
    total_tokens: int | None = Field(
        default=0, description="Estimated or actual tokens consumed during generation"
    )
    latency_ms: int | None = Field(
        default=0, description="Generation latency in milliseconds"
    )
    created_at: datetime | None = Field(
        default=None, description="Timestamp when summary was generated and stored"
    )
    updated_at: datetime | None = Field(
        default=None, description="Timestamp when summary was last modified"
    )


class DocumentSummaryEnvelope(SingleResponseEnvelope[DocumentSummaryData]):
    """Top-level single resource envelope for 3-point grounded document summary."""
