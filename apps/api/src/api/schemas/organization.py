"""Schemas and DTOs for Research Organizations and Labs (BỔ SUNG 2)."""

from datetime import datetime
from uuid import UUID

from api.schemas.envelope import PaginatedResponseEnvelope, SingleResponseEnvelope
from pydantic import BaseModel, Field

SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


class CreateOrganizationRequest(BaseModel):
    """Payload to create a new research lab/organization."""

    name: str = Field(..., min_length=2, max_length=255, description="Lab or team name")
    slug: str = Field(
        ...,
        min_length=2,
        max_length=100,
        pattern=SLUG_PATTERN,
        description="URL-friendly unique slug identifier",
    )
    description: str | None = Field(default=None, max_length=1000, description="Lab description")


class UpdateOrganizationRequest(BaseModel):
    """Payload to update an existing research lab."""

    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    token_quota: int | None = Field(default=None, ge=10000)
    storage_quota_bytes: int | None = Field(default=None, ge=1048576)


class AddOrganizationMemberRequest(BaseModel):
    """Payload to add a collaborator to a research lab."""

    email: str = Field(..., description="Email address of the collaborator")
    role: str = Field(
        default="member",
        pattern=r"^(admin|member|guest)$",
        description="Role in lab: admin, member, or guest",
    )


class UpdateMemberRoleRequest(BaseModel):
    """Payload to change member role."""

    role: str = Field(
        ...,
        pattern=r"^(owner|admin|member|guest)$",
        description="New role in lab",
    )


class OrganizationMemberResponse(BaseModel):
    """Member profile within a lab."""

    id: UUID = Field(..., description="Membership record ID")
    user_id: UUID = Field(..., description="User ID")
    email: str = Field(..., description="Member email")
    full_name: str = Field(..., description="Member full name")
    role: str = Field(..., description="Member role in lab")
    created_at: datetime = Field(..., description="Join timestamp")


class OrganizationResponse(BaseModel):
    """Research Lab summary data."""

    id: UUID = Field(..., description="Unique organization ID")
    name: str = Field(..., description="Lab or team name")
    slug: str = Field(..., description="Lab unique slug")
    description: str | None = Field(default=None, description="Description")
    storage_quota_bytes: int = Field(..., description="Storage quota allocated to lab")
    storage_used_bytes: int = Field(..., description="Storage consumed by lab")
    token_quota: int = Field(..., description="Token quota allocated to lab")
    tokens_used: int = Field(..., description="Tokens consumed by lab")
    members_count: int = Field(default=1, description="Total active members")
    user_role: str = Field(default="member", description="Current user's role in this lab")
    created_at: datetime = Field(..., description="Created timestamp")


class OrganizationDetailResponse(OrganizationResponse):
    """Detailed research lab data including member list."""

    members: list[OrganizationMemberResponse] = Field(default_factory=list)


class OrganizationEnvelope(SingleResponseEnvelope[OrganizationResponse]):
    """Single envelope for OrganizationResponse."""


class OrganizationDetailEnvelope(SingleResponseEnvelope[OrganizationDetailResponse]):
    """Single envelope for OrganizationDetailResponse."""


class OrganizationListEnvelope(PaginatedResponseEnvelope[OrganizationResponse]):
    """Paginated collection envelope for organizations."""
