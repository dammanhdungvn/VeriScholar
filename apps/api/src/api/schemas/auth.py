"""Authentication schemas and response envelopes."""

from datetime import datetime
from uuid import UUID

from api.schemas.envelope import SingleResponseEnvelope
from pydantic import BaseModel, Field

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class RegisterRequest(BaseModel):
    """Payload for user registration."""

    email: str = Field(
        ...,
        min_length=5,
        max_length=255,
        pattern=EMAIL_PATTERN,
        description="Unique email address",
    )
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name of user")


class LoginRequest(BaseModel):
    """Payload for user login."""

    email: str = Field(
        ...,
        min_length=5,
        max_length=255,
        pattern=EMAIL_PATTERN,
        description="Registered email address",
    )
    password: str = Field(..., min_length=1, description="Account password")


class GoogleLoginRequest(BaseModel):
    """Payload for Google OAuth login/registration."""

    credential: str = Field(..., description="Google ID Token JWT or simulated authorization token")
    client_id: str | None = Field(default=None, description="Optional Google OAuth Client ID")


class RefreshTokenRequest(BaseModel):
    """Payload for refreshing access token."""

    refresh_token: str = Field(..., description="Valid refresh token")


class TokenResponse(BaseModel):
    """Token response containing access and refresh tokens."""

    access_token: str = Field(..., description="JWT access token (short-lived)")
    refresh_token: str = Field(..., description="JWT refresh token (long-lived)")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration window in seconds")


class UserResponse(BaseModel):
    """User profile data model."""

    id: UUID = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User email address")
    full_name: str = Field(..., description="User full name")
    role: str = Field(default="researcher", description="System role: admin, researcher, member")
    avatar_url: str | None = Field(default=None, description="User avatar image URL")
    token_quota: int = Field(default=200000, description="Allocated LLM token quota")
    tokens_used: int = Field(default=0, description="Tokens consumed by user")
    storage_quota_bytes: int = Field(
        default=1073741824, description="Storage quota ceiling in bytes"
    )
    storage_used_bytes: int = Field(default=0, description="Storage currently consumed in bytes")
    is_active: bool = Field(default=True, description="Account active status")
    created_at: datetime = Field(..., description="Creation timestamp in UTC")


class TokenQuotaStatusResponse(BaseModel):
    """Real-time token and storage quota status."""

    token_quota: int = Field(..., description="Total token quota allocated")
    tokens_used: int = Field(..., description="Total tokens consumed")
    tokens_remaining: int = Field(..., description="Tokens left to consume")
    percent_tokens_used: float = Field(
        ..., description="Percentage of token quota used [0.0 - 100.0]"
    )
    storage_quota_bytes: int = Field(..., description="Total storage bytes allocated")
    storage_used_bytes: int = Field(..., description="Total storage bytes consumed")
    storage_remaining_bytes: int = Field(..., description="Storage bytes remaining")
    percent_storage_used: float = Field(..., description="Percentage of storage used [0.0 - 100.0]")
    is_quota_exceeded: bool = Field(..., description="True if token or storage limit exceeded")


class AuthTokenEnvelope(SingleResponseEnvelope[TokenResponse]):
    """Standard Single Resource Envelope wrapping TokenResponse."""


class UserProfileEnvelope(SingleResponseEnvelope[UserResponse]):
    """Standard Single Resource Envelope wrapping UserResponse."""


class TokenQuotaEnvelope(SingleResponseEnvelope[TokenQuotaStatusResponse]):
    """Standard Single Resource Envelope wrapping TokenQuotaStatusResponse."""
