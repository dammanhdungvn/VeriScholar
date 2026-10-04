"""Pydantic schemas for Public Resource Sharing & Instant Revocation (Module 1/4 Collaboration)."""

from datetime import datetime
from typing import Any
from uuid import UUID

from api.schemas.envelope import SingleResponseEnvelope
from pydantic import BaseModel, Field


class CreateShareRequest(BaseModel):
    """Payload to create a new public shareable link."""

    resource_type: str = Field(
        description="Type of resource being shared ('document', 'note', 'draft', 'collection')",
        examples=["note"],
    )
    resource_id: UUID = Field(description="UUID of the resource being shared")
    permission: str = Field(
        default="read_only",
        description="Access permission for the share link ('read_only')",
    )
    expires_at: datetime | None = Field(
        default=None,
        description="Optional expiration timestamp in UTC",
    )


class ShareResponseData(BaseModel):
    """Metadata for an active shareable link."""

    share_token: str = Field(description="Opaque public token identifying the share link")
    resource_type: str = Field(description="Resource type")
    resource_id: UUID = Field(description="Resource UUID")
    permission: str = Field(description="Access permission")
    share_url: str = Field(description="Public share URL path")
    expires_at: datetime | None = Field(default=None, description="Expiration timestamp")
    created_at: datetime = Field(description="Share link creation timestamp")


class ShareEnvelope(SingleResponseEnvelope[ShareResponseData]):
    """Standard Envelope for share creation and status."""


class PublicShareResourceData(BaseModel):
    """Public read-only resource payload rendered for unauthenticated guests."""

    share_token: str = Field(description="Share token")
    resource_type: str = Field(description="Type of the shared resource")
    resource_id: UUID = Field(description="ID of the shared resource")
    permission: str = Field(description="Granted permission ('read_only')")
    resource_data: dict[str, Any] = Field(description="Public resource content snapshot")
    created_at: datetime = Field(description="Share creation timestamp")


class PublicShareEnvelope(SingleResponseEnvelope[PublicShareResourceData]):
    """Standard Envelope for unauthenticated public share retrieval."""
