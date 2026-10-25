"""Pydantic v2 schemas for Research Notes."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateNoteRequest(BaseModel):
    """Payload for saving an academic quotation and personal memo to notebook."""

    model_config = ConfigDict(extra="forbid")

    document_id: UUID | None = Field(
        default=None,
        description="Optional UUID of the source document.",
    )
    chunk_id: UUID | None = Field(
        default=None,
        description="Optional UUID of the matching document chunk.",
    )
    selected_text: str = Field(
        ...,
        min_length=1,
        description="Exact quote or text selected from the PDF.",
        examples=["Attention(Q, K, V) = softmax(QK^T / sqrt(d_k))V"],
    )
    bounding_boxes: list[list[float | int]] = Field(
        default_factory=list,
        description="Normalized coordinates [ymin, xmin, ymax, xmax, page] on PDF canvas.",
        examples=[[[0.21, 0.52, 0.79, 0.58, 4]]],
    )
    page_number: int = Field(
        default=1,
        ge=1,
        description="Page number in the PDF where the quotation appears.",
    )
    user_note: str | None = Field(
        default=None,
        description="Optional personal memo or reflection written by the researcher.",
        examples=["Công thức cốt lõi cần dùng cho phần phương pháp."],
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Semantic or academic category tags.",
        examples=[["methodology", "core-formula"]],
    )


class UpdateNoteRequest(BaseModel):
    """Payload for modifying a note's personal memo or tags (OCC protected)."""

    model_config = ConfigDict(extra="forbid")

    user_note: str | None = Field(
        default=None,
        description="Updated personal memo.",
    )
    tags: list[str] | None = Field(
        default=None,
        description="Updated tags list.",
    )


class NoteResponse(BaseModel):
    """Single note response data model."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID | None = None
    chunk_id: UUID | None = None
    selected_text: str
    bounding_boxes: list[list[float | int]] = Field(default_factory=list)
    page_number: int
    user_note: str | None = None
    tags: list[str] = Field(default_factory=list)
    frozen_snapshot: dict[str, Any] = Field(default_factory=dict)
    is_source_detached: bool = False
    version: int = 1
    created_at: datetime
    updated_at: datetime


class NoteListItemResponse(BaseModel):
    """Item in paginated notes list."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID | None = None
    document_title: str | None = None
    selected_text: str
    page_number: int
    user_note: str | None = None
    tags: list[str] = Field(default_factory=list)
    is_source_detached: bool = False
    version: int = 1
    created_at: datetime
    updated_at: datetime
