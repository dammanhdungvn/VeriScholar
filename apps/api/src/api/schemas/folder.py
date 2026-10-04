"""Pydantic schemas for Project Folders (Module 4 Library categorization)."""

from datetime import datetime
from uuid import UUID

from api.schemas.envelope import SingleResponseEnvelope
from pydantic import BaseModel, Field


class FolderCreateRequest(BaseModel):
    """Payload to create a new research topic folder."""

    name: str = Field(
        min_length=1,
        max_length=255,
        description="Folder display name",
        examples=["Deep Learning Architectures"],
    )
    parent_id: UUID | None = Field(
        default=None,
        description="Optional parent folder UUID for hierarchical nested subfolders",
    )


class FolderUpdateRequest(BaseModel):
    """Payload to rename or move a research topic folder."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Updated folder name",
        examples=["Transformers & Attention Mechanisms"],
    )
    parent_id: UUID | None = Field(
        default=None,
        description="Updated parent folder UUID (null to move to root)",
    )


class FolderItemResponseData(BaseModel):
    """Folder representation with aggregated document count."""

    id: UUID = Field(description="Unique folder identifier")
    name: str = Field(description="Folder name")
    parent_id: UUID | None = Field(
        default=None,
        description="Parent folder UUID if nested under another folder",
    )
    document_count: int = Field(
        default=0,
        ge=0,
        description="Total number of user-starred research papers inside this folder",
    )
    created_at: datetime = Field(description="Creation timestamp in UTC")
    updated_at: datetime = Field(description="Last update timestamp in UTC")


class FolderItemEnvelope(SingleResponseEnvelope[FolderItemResponseData]):
    """Standard Single Resource Envelope for folder response."""


class FolderListEnvelope(SingleResponseEnvelope[list[FolderItemResponseData]]):
    """Standard Envelope wrapping the list of user research folders."""
