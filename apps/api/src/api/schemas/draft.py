"""Pydantic schemas for Module 2: Drafting Workspace, Compile Broker & SAFE Fact-Checking."""

from datetime import datetime
from uuid import UUID

from api.schemas.envelope import (
    PaginatedResponseEnvelope,
    SingleResponseEnvelope,
)
from pydantic import BaseModel, Field


class CreateDraftRequest(BaseModel):
    """Payload to create a new draft."""

    title: str = Field(..., max_length=255, description="Draft paper title")
    format: str = Field(
        default="latex",
        pattern="^(latex|markdown)$",
        description="Document markup format",
    )
    template: str = Field(default="ieee_conference", description="Paper template name")
    initial_content: str = Field(default="", description="Initial draft source content")


class UpdateDraftContentRequest(BaseModel):
    """Payload to update full draft content with OCC If-Match header."""

    content: str = Field(..., description="Full updated source code")


class PatchDraftRequest(BaseModel):
    """Payload to update draft metadata."""

    title: str | None = Field(default=None, max_length=255, description="Updated title")
    template: str | None = Field(default=None, description="Updated template name")


class DraftResponseData(BaseModel):
    """Representation of an academic draft."""

    id: UUID = Field(description="Draft UUID")
    user_id: UUID = Field(description="Owner UUID")
    title: str = Field(description="Draft title")
    format: str = Field(description="Markup format ('latex' | 'markdown')")
    template: str = Field(description="Template name")
    content: str = Field(description="Draft source code")
    version: int = Field(description="OCC version counter")
    last_compiled_at: datetime | None = Field(
        default=None, description="Last compilation timestamp"
    )
    last_compile_status: str | None = Field(default=None, description="Last compilation status")
    pdf_preview_storage_path: str | None = Field(
        default=None, description="Compiled PDF preview path"
    )
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Update timestamp")


class DraftEnvelope(SingleResponseEnvelope[DraftResponseData]):
    """Standard Envelope for a single draft."""


class DraftsPageEnvelope(PaginatedResponseEnvelope[DraftResponseData]):
    """Standard Paginated Envelope for user drafts."""


class CompileDraftRequest(BaseModel):
    """Payload to trigger isolated sandbox compilation."""

    compiler_engine: str = Field(default="tectonic", description="LaTeX compiler engine")
    auto_self_heal: bool = Field(
        default=True, description="Enable agentic self-healing on compile errors"
    )
    max_heal_attempts: int = Field(default=3, ge=1, le=5, description="Max self-healing iterations")


class CreateDraftCommentRequest(BaseModel):
    """Payload to add a line/sentence-level review comment."""

    line_number: int = Field(..., ge=1, description="Line number of text anchor")
    selected_text: str = Field(..., min_length=1, description="Selected text fragment")
    comment: str = Field(..., min_length=1, description="Review feedback or suggestion")


class DraftCommentResponseData(BaseModel):
    """Representation of a peer review comment on a draft."""

    id: UUID = Field(description="Comment UUID")
    draft_id: UUID = Field(description="Associated Draft UUID")
    user_id: UUID = Field(description="Author UUID")
    author_name: str = Field(description="Display name of author")
    line_number: int = Field(description="Line number anchor")
    selected_text: str = Field(description="Selected text fragment")
    comment: str = Field(description="Review comment text")
    status: str = Field(description="Status ('open' | 'resolved')")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Update timestamp")


class DraftCommentEnvelope(SingleResponseEnvelope[DraftCommentResponseData]):
    """Standard Envelope for a single comment."""


class DraftCommentsPageEnvelope(PaginatedResponseEnvelope[DraftCommentResponseData]):
    """Standard Paginated Envelope for draft comments."""


class ClaimCitation(BaseModel):
    """Grounding citation for an atomic claim."""

    document_id: UUID | None = Field(default=None, description="Source document UUID")
    page_number: int | None = Field(default=None, description="Source page number (1-indexed)")
    bounding_boxes: list[list[float | int]] = Field(
        default_factory=list,
        description="Normalized bounding boxes [[x0, y0, x1, y1, page], ...]",
    )
    quote: str | None = Field(default=None, description="Exact matching quote excerpt")


class ClaimVerificationResult(BaseModel):
    """Result of an individual decomposed claim verification."""

    claim_index: int = Field(description="0-indexed order of the claim")
    claim_text: str = Field(description="Decomposed atomic proposition")
    verdict: str = Field(
        description="Verification verdict ('supported' | 'contradicted' | 'not_enough_info')"
    )
    confidence: float = Field(description="Confidence score [0.0, 1.0]")
    citation: ClaimCitation | None = Field(
        default=None, description="Grounding citation if supported"
    )


class VerifyClaimsRequest(BaseModel):
    """Payload to run 4-stage SAFE Fact-Checking on selected draft text."""

    selected_text: str = Field(..., min_length=5, description="Text snippet to fact-check")
    document_ids: list[UUID] = Field(
        default_factory=list,
        description="Optional scoping list of document UUIDs to search for evidence",
    )


class VerifyClaimsResponseData(BaseModel):
    """Overall outcome of the SAFE Fact-Checking pipeline."""

    verification_id: UUID = Field(description="Audit log record UUID")
    draft_id: UUID = Field(description="Associated Draft UUID")
    selected_text: str = Field(description="Original verified text")
    claims: list[ClaimVerificationResult] = Field(description="List of verified atomic claims")
    total_claims: int = Field(description="Total count of claims")
    supported_count: int = Field(description="Number of supported claims")
    contradicted_count: int = Field(description="Number of contradicted claims")
    not_enough_info_count: int = Field(description="Number of unverified claims")


class VerifyClaimsEnvelope(SingleResponseEnvelope[VerifyClaimsResponseData]):
    """Standard Envelope for SAFE Fact-Checking outcome."""
