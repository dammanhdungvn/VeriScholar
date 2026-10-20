"""Pydantic v2 schemas for Research Writing Drafts."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateDraftRequest(BaseModel):
    """Payload for creating a new research writing draft."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        default="Untitled Draft",
        min_length=1,
        max_length=255,
        description="Title or topic of the draft.",
        examples=["A Survey of Transformer Architectures"],
    )
    content: str = Field(
        default="",
        description="Initial LaTeX or Markdown text body.",
        examples=["\\section{Introduction}\nDeep learning has revolutionized NLP."],
    )
    format: Literal["latex", "markdown"] = Field(
        default="latex",
        description="Source markup format.",
    )


class UpdateDraftRequest(BaseModel):
    """Payload for updating a research writing draft (OCC protected)."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Updated title of the draft.",
    )
    content: str | None = Field(
        default=None,
        description="Updated text body.",
    )
    format: Literal["latex", "markdown"] | None = Field(
        default=None,
        description="Updated format.",
    )
    version: int | None = Field(
        default=None,
        ge=1,
        description=(
            "Expected current version for optimistic concurrency control (OCC). "
            "Optional if If-Match header is provided."
        ),
        examples=[1],
    )


class DraftResponse(BaseModel):
    """Public representation of a research draft."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    content: str
    format: str
    version: int
    created_at: datetime
    updated_at: datetime


class DraftListResponse(BaseModel):
    """Paginated or listed collection of drafts."""

    items: list[DraftResponse]
    total: int


class VerifyFactsRequest(BaseModel):
    """Request payload to trigger SAFE fact-checking on a draft or excerpt."""

    model_config = ConfigDict(extra="forbid")

    text: str | None = Field(
        default=None,
        description="Optional text snippet to verify. If omitted, verifies draft content.",
    )
    document_ids: list[UUID] | None = Field(
        default=None,
        description="Optional document UUIDs to constrain retrieval search.",
    )


class AtomicClaimResponse(BaseModel):
    """Response representing a verified atomic factual claim."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    claim_text: str
    normalized_entities: list[str]
    status: str
    confidence_score: float
    evidence_text: str | None = None
    evidence_document_id: UUID | None = None
    evidence_document_title: str | None = None
    evidence_page: int | None = None
    evidence_bounding_boxes: list[list[float]] = Field(default_factory=list)
    reasoning: str = ""


class VerifyFactsResponse(BaseModel):
    """Full verification report containing atomic claims and summary metrics."""

    model_config = ConfigDict(from_attributes=True)

    draft_id: UUID | None = None
    verified_text: str
    claims: list[AtomicClaimResponse]
    total_claims: int
    supported_claims: int
    contradicted_claims: int
    unverified_claims: int
    supported_ratio: float
    latency_ms: float
    verified_at: datetime


class LatexSyntaxErrorResponse(BaseModel):
    """Schema representing a LaTeX syntax/linter error."""

    model_config = ConfigDict(from_attributes=True)

    line: int
    column: int
    rule: str
    message: str
    suggested_fix: str | None = None


class CompileDraftResponse(BaseModel):
    """Response returned upon compiling a draft."""

    model_config = ConfigDict(from_attributes=True)

    draft_id: UUID
    success: bool
    pdf_preview_url: str | None = None
    errors: list[LatexSyntaxErrorResponse] = Field(default_factory=list)
    logs: str = ""
    retries_attempted: int = 0


# ==============================================================================
# AI Writing Assistant Schemas (/drafts/{id}/assist)
# ==============================================================================


class DraftAssistRequest(BaseModel):
    """Payload to request AI writing assistance on a draft."""

    model_config = ConfigDict(extra="forbid")

    action: Literal["expand", "summarize", "polish", "continue", "cite", "critique"] = Field(
        default="polish",
        description="Type of AI writing assistance requested",
    )
    instruction: str | None = Field(
        default=None,
        description="Optional custom prompt or guideline for the assistant",
    )
    prompt: str | None = Field(
        default=None,
        description="Alias or direct prompt for writing assist",
    )
    target_selection: str | None = Field(
        default=None,
        description="Specific highlighted text passage in the draft to transform",
    )
    pre_context: str | None = Field(
        default=None,
        description="Surrounding text context immediately preceding the selection.",
    )
    post_context: str | None = Field(
        default=None,
        description="Surrounding text context immediately following the selection.",
    )
    section_title: str | None = Field(
        default=None,
        description="Target section context (e.g. 'Methodology', 'Results')",
    )
    cursor_position: int | None = Field(
        default=None,
        ge=0,
        description="Current character index position of cursor.",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Sampling temperature for creative balance",
    )


class DraftAssistResponse(BaseModel):
    """Response returned from AI writing assistance."""

    model_config = ConfigDict(from_attributes=True)

    draft_id: UUID
    action: str = "polish"
    prompt: str = ""
    generated_text: str = Field(
        default="", description="AI synthesized text or replacement snippet"
    )
    suggested_text: str = Field(default="", description="Alias for generated text for review UI")
    original_text: str | None = None
    explanation: str | None = None
    confidence_score: float = 0.95
    suggested_citations: list[str] = Field(
        default_factory=list,
        description="Relevant academic citation keys suggested for this content",
    )
    diff_preview: str | None = Field(
        default=None,
        description="Optional unified diff between target selection and generated text",
    )
    suggested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ==============================================================================
# Assets Management Schemas (/drafts/{id}/assets)
# ==============================================================================


class CreateDraftAssetRequest(BaseModel):
    """Payload to register or upload a draft asset."""

    model_config = ConfigDict(extra="forbid")

    asset_type: Literal[
        "image", "bibtex", "table", "dataset", "supplementary", "style", "archive"
    ] = Field(
        default="image",
        description="Type of asset (image, bibtex, table, dataset, supplementary, style, archive)",
    )
    filename: str = Field(
        min_length=1,
        max_length=255,
        description="Name of the file asset",
        examples=["figure1_architecture.png", "references.bib", "custom.cls"],
    )
    content_base64: str | None = Field(
        default=None,
        description="Base64-encoded file content if uploaded inline",
    )
    caption: str | None = Field(
        default=None,
        description="Optional figure or table caption",
    )
    latex_label: str | None = Field(
        default=None,
        description="LaTeX label for referencing (e.g. 'fig:arch', 'tab:metrics')",
    )


class DraftAssetResponse(BaseModel):
    """Representation of an uploaded draft asset."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    draft_id: UUID
    asset_type: str
    filename: str
    file_size_bytes: int
    storage_url: str | None = None
    caption: str | None = None
    latex_label: str | None = None
    created_at: datetime


class DraftAssetListResponse(BaseModel):
    """List of assets associated with a draft."""

    model_config = ConfigDict(from_attributes=True)

    draft_id: UUID
    items: list[DraftAssetResponse]
    total: int


# ==============================================================================
# Collaborative Sharing Schemas (/drafts/{id}/share)
# ==============================================================================


class DraftShareRequest(BaseModel):
    """Payload to configure draft sharing and permissions."""

    model_config = ConfigDict(extra="forbid")

    target_email: str | None = Field(
        default=None,
        description="Optional specific collaborator email to invite",
    )
    permission: Literal["viewer", "commenter", "editor", "view", "comment", "edit"] = Field(
        default="editor",
        description="Access permission granted: viewer, commenter, or editor",
    )
    allow_public_link: bool = Field(
        default=False,
        description="Whether to generate an open public shareable link",
    )

    def normalized_permission(self) -> str:
        """Normalize legacy or shorthand permission names to canonical roles."""
        perm = self.permission.lower().strip()
        if perm in ("edit", "editor"):
            return "editor"
        elif perm in ("comment", "commenter"):
            return "commenter"
        return "viewer"


class DraftCollaboratorResponse(BaseModel):
    """Collaborator with granted draft permissions."""

    model_config = ConfigDict(from_attributes=True)

    user_id: UUID | None = None
    email: str
    permission: str
    granted_at: datetime


class DraftShareResponse(BaseModel):
    """Sharing configuration and invitation response."""

    model_config = ConfigDict(from_attributes=True)

    draft_id: UUID
    share_token: str
    share_url: str
    permission: str
    allow_public_link: bool
    collaborators: list[DraftCollaboratorResponse] = Field(default_factory=list)


# ==============================================================================
# Peer Review Comments & Annotations Schemas (/drafts/{id}/comments) - PRD §3.2
# ==============================================================================


class CreateDraftCommentRequest(BaseModel):
    """Payload to create a peer review comment or reply on a draft."""

    model_config = ConfigDict(extra="forbid")

    start_offset: int = Field(
        default=0,
        ge=0,
        description="Character start offset in the draft text",
    )
    end_offset: int = Field(
        default=0,
        ge=0,
        description="Character end offset in the draft text",
    )
    selected_text: str = Field(
        default="",
        description="Selected text excerpt being commented on",
    )
    comment_text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Feedback or peer review comment content",
    )
    parent_id: UUID | None = Field(
        default=None,
        description="Optional parent comment ID for threaded replies",
    )


class UpdateDraftCommentRequest(BaseModel):
    """Payload to update comment text or resolve/unresolve status."""

    model_config = ConfigDict(extra="forbid")

    comment_text: str | None = Field(
        default=None,
        min_length=1,
        max_length=10000,
        description="Updated comment body (only author permitted)",
    )
    is_resolved: bool | None = Field(
        default=None,
        description="Resolution status (author, editor, or owner permitted)",
    )


class DraftCommentResponse(BaseModel):
    """Public representation of a peer review comment or reply."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    draft_id: UUID
    author_id: UUID
    author_name: str
    start_offset: int
    end_offset: int
    selected_text: str
    comment_text: str
    parent_id: UUID | None = None
    is_resolved: bool = False
    created_at: datetime
    updated_at: datetime
    replies: list["DraftCommentResponse"] = Field(default_factory=list)


class DraftCommentListResponse(BaseModel):
    """List of comments attached to a draft."""

    model_config = ConfigDict(from_attributes=True)

    draft_id: UUID
    items: list[DraftCommentResponse]
    total: int


# ==============================================================================
# Overleaf 1-Click Sync Schemas (Pillar 2)
# ==============================================================================


class OverleafExportResponse(BaseModel):
    """Metadata and direct launch link for Overleaf 1-Click Sync (Pillar 2)."""

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    draft_id: UUID = Field(description="ID of the draft being launched.")
    title: str = Field(description="Title of the paper.")
    format: str = Field(description="Document format (latex / markdown).")
    overleaf_url: str = Field(description="Overleaf direct web launch URL with encoded snippet.")
    launch_url: str = Field(description="Alias for overleaf_url for frontend compatibility.")
    latex_snip: str = Field(description="Raw LaTeX source code.")
    snip_length: int = Field(description="Length in characters of the LaTeX snippet.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ==============================================================================
# Proactive Associative Memory Engine Schemas (Pillar 3)
# ==============================================================================


class AssociativeSuggestionsRequest(BaseModel):
    """Payload to request proactive associative memory suggestions for a draft."""

    model_config = ConfigDict(extra="forbid")

    text: str | None = Field(
        default=None,
        description="Optional current paragraph or selected text. If omitted, uses draft body.",
    )
    limit: int = Field(default=5, ge=1, le=50, description="Max suggestions to return.")
    min_similarity: float = Field(
        default=0.1, ge=0.0, le=1.0, description="Minimum similarity threshold."
    )


class AssociativeSuggestionItem(BaseModel):
    """A proactive associative suggestion linking past research notes to the current draft."""

    note_id: UUID
    document_id: UUID | None = None
    paper_title: str | None = None
    page_number: int | None = None
    note_content: str
    selected_text: str
    tags: list[str] = Field(default_factory=list)
    similarity_score: float
    suggested_citation: str
    relevance_explanation: str
    matched_keywords: list[str] = Field(default_factory=list)


class AssociativeSuggestionsResponse(BaseModel):
    """Collection of proactive associative memory suggestions."""

    draft_id: UUID
    suggestions: list[AssociativeSuggestionItem]
    total_found: int
    analyzed_text_length: int
