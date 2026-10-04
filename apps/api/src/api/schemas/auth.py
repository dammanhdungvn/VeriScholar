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
    is_active: bool = Field(default=True, description="Account active status")
    created_at: datetime = Field(..., description="Creation timestamp in UTC")


class AuthTokenEnvelope(SingleResponseEnvelope[TokenResponse]):
    """Standard Single Resource Envelope wrapping TokenResponse."""


class UserProfileEnvelope(SingleResponseEnvelope[UserResponse]):
    """Standard Single Resource Envelope wrapping UserResponse."""
