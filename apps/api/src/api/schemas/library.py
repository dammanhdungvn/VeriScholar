"""Pydantic schemas for Personal Library & Multi-paper Synthesis (Module 4)."""

from uuid import UUID

from api.schemas.envelope import SingleResponseEnvelope
from pydantic import BaseModel, Field


class BulkImportRequest(BaseModel):
    """Payload to batch import research papers by identifiers into user library."""

    identifiers: list[str] = Field(
        min_length=1,
        max_length=50,
        description="List of academic identifiers (DOIs, arXiv IDs) to import (1-50 items)",
        examples=[["10.1145/3308558.3313562", "1706.03762"]],
    )
    target_folder_id: UUID | None = Field(
        default=None,
        description="Optional target folder UUID where imported papers will be placed",
    )


class BulkImportResponseData(BaseModel):
    """Tracking response for queued bulk import task."""

    batch_id: UUID = Field(description="Unique batch import tracking ID")
    total_items: int = Field(description="Total number of items in the batch")
    accepted_identifiers: list[str] = Field(
        description="List of validated identifiers queued for import"
    )
    status: str = Field(
        default="queued",
        description="Current batch status ('queued', 'processing', 'completed')",
    )
    message: str = Field(description="Human-readable processing message")


class BulkImportEnvelope(SingleResponseEnvelope[BulkImportResponseData]):
    """Standard Single Resource Envelope for bulk import initiation."""


class LibrarySynthesizeRequest(BaseModel):
    """Payload to trigger hierarchical RAG synthesis across library or folder."""

    query: str = Field(
        min_length=1,
        description="Research question or comparative synthesis query",
        examples=["Trong các bài báo tôi đã lưu, những bài nào thử nghiệm Transformer?"],
    )


class SynthesizeSourceReference(BaseModel):
    """Grounded evidence source reference with exact spatial bounding boxes."""

    document_id: UUID = Field(description="Source document identifier")
    title: str = Field(description="Academic paper title")
    page_number: int = Field(ge=1, description="1-indexed source page number")
    bounding_boxes: list[list[float]] = Field(
        default_factory=list,
        description="Normalized [x0, y0, x1, y1, page] spatial bounding boxes (Top-Left, 0.0-1.0)",
    )


class LibrarySynthesizeResponseData(BaseModel):
    """Payload for multi-paper synthesis with Sufficiency Verification Gate details."""

    answer: str = Field(description="Synthesized academic response grounded in evidence")
    retrieval_tier_reached: str = Field(
        description="Tier: 'tier_1_smart_notes', 'tier_2_metadata', 'tier_3_deep_raw_chunks'",
    )
    sufficiency_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Sufficiency verification gate score indicating evidence completeness",
    )
    sources: list[SynthesizeSourceReference] = Field(
        default_factory=list,
        description="List of grounding evidence sources",
    )


class LibrarySynthesizeEnvelope(SingleResponseEnvelope[LibrarySynthesizeResponseData]):
    """Standard Single Resource Envelope for library synthesis."""


class LibraryCompareRequest(BaseModel):
    """Payload to build an automated comparison matrix across papers."""

    document_ids: list[UUID] = Field(
        min_length=2,
        max_length=10,
        description="List of 2 to 10 document IDs to compare side-by-side",
    )
    columns: list[str] = Field(
        default_factory=lambda: ["Method", "Dataset", "Results", "Limitations"],
        description="Comparison columns / dimensions to extract from each document",
    )


class ComparedDocumentInfo(BaseModel):
    """Summary metadata of a compared document."""

    id: UUID = Field(description="Unique document ID")
    title: str = Field(description="Document title")
    authors: list[str] | None = Field(default=None, description="Author list")
    publication_year: int | None = Field(default=None, description="Publication year")


class LibraryCompareResponseData(BaseModel):
    """Comparative table data comparing documents across dimensions."""

    columns: list[str] = Field(description="Comparison columns evaluated")
    documents: list[ComparedDocumentInfo] = Field(description="List of evaluated documents")
    comparison_matrix: dict[str, dict[str, str]] = Field(
        description="Mapping from document_id (string) to column name to extracted findings",
    )


class LibraryCompareEnvelope(SingleResponseEnvelope[LibraryCompareResponseData]):
    """Standard Single Resource Envelope for library document comparison."""
