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
    bib_content: str | None = Field(
        default=None,
        description="Initial BibTeX bibliography content.",
    )
    format: Literal["latex", "markdown"] = Field(
        default="latex",
        description="Source markup format.",
    )
    template: str | None = Field(
        default=None,
        description="Template style (e.g. 'academic_skeleton', 'blank').",
    )
    source_session_id: UUID | None = Field(
        default=None,
        description="Optional research session ID to initialize skeleton from reading papers.",
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
    bib_content: str | None = Field(
        default=None,
        description="Updated BibTeX bibliography.",
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
    bib_content: str = ""
    format: str
    template: str | None = None
    source_session_id: UUID | None = None
    pdf_preview_url: str | None = None
    previous_snapshot: dict | None = None
    version: int
    created_at: datetime
    updated_at: datetime


class DraftListResponse(BaseModel):
    """Paginated or listed collection of drafts."""

    items: list[DraftResponse]
    total: int


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
    is_sandboxed: bool = False


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
# Overleaf CLSI, SyncTeX & Streaming Chat Schemas
# ==============================================================================


class DraftChatStreamRequest(BaseModel):
    """Payload to initiate unbuffered SSE writing agent interaction."""

    model_config = ConfigDict(extra="forbid")

    prompt: str | None = Field(
        default=None,
        description="User instruction or prompt for the writing agent.",
    )
    message: str | None = Field(
        default=None,
        description="Alias for prompt.",
    )
    current_content: str | None = Field(
        default=None,
        description="Client-side latest draft LaTeX text.",
    )
    current_bib_content: str | None = Field(
        default=None,
        description="Client-side latest BibTeX bibliography text.",
    )
    version: int | None = Field(
        default=None,
        ge=1,
        description="Draft version for concurrency check.",
    )


class DraftSyncTexForwardRequest(BaseModel):
    """Payload to navigate from source code line/column to PDF page coordinates."""

    model_config = ConfigDict(extra="forbid")

    file: str = Field(
        default="main.tex",
        description="Source file name (default 'main.tex').",
    )
    line: int = Field(
        ge=1,
        description="Line number in LaTeX source code.",
    )
    column: int = Field(
        default=1,
        ge=1,
        description="Column number in LaTeX source code.",
    )


class DraftSyncTexForwardResponse(BaseModel):
    """PDF coordinates returned by forward SyncTeX search."""

    model_config = ConfigDict(from_attributes=True)

    page: int
    h: float
    v: float
    width: float
    height: float


class DraftSyncTexInverseRequest(BaseModel):
    """Payload to navigate from PDF point click to source code line/column."""

    model_config = ConfigDict(extra="forbid")

    page: int = Field(
        ge=1,
        description="PDF page number (1-indexed).",
    )
    x: float = Field(
        description="Horizontal coordinate on the PDF page.",
    )
    y: float = Field(
        description="Vertical coordinate on the PDF page.",
    )


class DraftSyncTexInverseResponse(BaseModel):
    """Source file and line returned by inverse SyncTeX search."""

    model_config = ConfigDict(from_attributes=True)

    file: str
    line: int
    column: int


class DraftCompileClearCacheResponse(BaseModel):
    """Response returned upon clearing compilation cache and recompiling."""

    model_config = ConfigDict(from_attributes=True)

    draft_id: UUID
    cache_cleared: bool = True
    success: bool
    pdf_preview_url: str | None = None
    logs: str = ""
    diagnostics: list[dict] = Field(default_factory=list)
