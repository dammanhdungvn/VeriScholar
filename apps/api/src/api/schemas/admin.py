"""Schemas and response envelopes for Admin Console (BỔ SUNG 2)."""

from datetime import datetime
from uuid import UUID

from api.schemas.envelope import PaginatedResponseEnvelope, SingleResponseEnvelope
from pydantic import BaseModel, Field


class AdminDashboardMetricsResponse(BaseModel):
    """Global system health, storage, and token consumption metrics."""

    total_users: int = Field(..., description="Total registered accounts")
    active_users: int = Field(..., description="Active user accounts")
    total_documents: int = Field(..., description="Total indexed documents")
    total_storage_bytes: int = Field(..., description="Total CAS storage consumed in bytes")
    total_storage_formatted: str = Field(..., description="Human-readable storage size")
    total_tokens_consumed: int = Field(..., description="Aggregate LLM tokens consumed")
    total_cost_estimated_usd: float = Field(..., description="Estimated compute expenditure in USD")
    active_sessions: int = Field(..., description="Active research sessions")
    total_labs: int = Field(..., description="Total collaborative labs configured")
    system_status: str = Field(default="healthy", description="Global health state")


class AdminUserListItemResponse(BaseModel):
    """User row in admin management table."""

    id: UUID = Field(..., description="User unique identifier")
    email: str = Field(..., description="User email")
    full_name: str = Field(..., description="User full name")
    role: str = Field(..., description="System role: admin, researcher, member")
    is_active: bool = Field(..., description="Account status")
    token_quota: int = Field(..., description="Allocated token limit")
    tokens_used: int = Field(..., description="Consumed tokens")
    storage_quota_bytes: int = Field(..., description="Allocated storage limit in bytes")
    storage_used_bytes: int = Field(..., description="Consumed storage in bytes")
    created_at: datetime = Field(..., description="Account creation timestamp")


class AdminUpdateUserQuotaRequest(BaseModel):
    """Payload to adjust user quotas and role privileges."""

    token_quota: int | None = Field(default=None, ge=1000)
    storage_quota_bytes: int | None = Field(default=None, ge=1048576)
    role: str | None = Field(default=None, pattern=r"^(admin|researcher|member)$")
    is_active: bool | None = Field(default=None)


class AdminUsageLogItemResponse(BaseModel):
    """Individual resource consumption record."""

    id: UUID = Field(..., description="Record UUID")
    user_id: UUID = Field(..., description="User who triggered activity")
    user_email: str = Field(..., description="User email")
    activity_type: str = Field(..., description="Activity category")
    model_name: str | None = Field(default=None, description="LLM model used")
    tokens_prompt: int = Field(default=0, description="Input tokens")
    tokens_completion: int = Field(default=0, description="Output tokens")
    total_tokens: int = Field(default=0, description="Total tokens consumed")
    cost_cents: float = Field(default=0.0, description="Cost in cents")
    bytes_transferred: int = Field(default=0, description="Data volume transferred")
    created_at: datetime = Field(..., description="Execution timestamp")


class AdminSystemHealthResponse(BaseModel):
    """Underlying infrastructure health probe results."""

    database_connected: bool = Field(..., description="PostgreSQL operational status")
    storage_dir_healthy: bool = Field(..., description="CAS disk directory read/write check")
    storage_free_bytes: int = Field(..., description="Free filesystem storage bytes")
    total_storage_blobs: int = Field(..., description="Count of deduplicated CAS blobs")
    average_latency_ms: float = Field(..., description="Recent request latency estimate in ms")


class AdminDashboardEnvelope(SingleResponseEnvelope[AdminDashboardMetricsResponse]):
    """Envelope wrapping AdminDashboardMetricsResponse."""


class AdminUserListEnvelope(PaginatedResponseEnvelope[AdminUserListItemResponse]):
    """Envelope wrapping paginated user accounts list."""


class AdminUserEnvelope(SingleResponseEnvelope[AdminUserListItemResponse]):
    """Envelope wrapping individual updated user record."""


class AdminUsageListEnvelope(PaginatedResponseEnvelope[AdminUsageLogItemResponse]):
    """Envelope wrapping usage logs list."""


class AdminHealthEnvelope(SingleResponseEnvelope[AdminSystemHealthResponse]):
    """Envelope wrapping infrastructure health data."""
