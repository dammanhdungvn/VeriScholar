"""Pydantic schemas for Authentication, Authorization & User Profiles.

Strictly 1-1 aligned with Frontend domain types (apps/web/src/types/auth.ts).
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

UserRole = Literal["researcher", "faculty", "postdoc", "student", "guest"]

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class UserProfileResponse(BaseModel):
    """User profile response representation."""

    id: UUID = Field(description="User unique identifier (UUID v4)")
    email: str = Field(description="User email address")
    full_name: str = Field(description="User full name")
    institution: str | None = Field(default=None, description="Affiliated academic institution")
    academic_rank: str | None = Field(default=None, description="Academic title or position")
    orcid_id: str | None = Field(default=None, description="ORCID researcher identifier")
    avatar_url: str | None = Field(default=None, description="URL of user profile avatar image")
    role: str = Field(default="researcher", description="Platform permission role")
    is_verified: bool = Field(
        default=False, description="Whether academic credentials are verified"
    )
    created_at: datetime = Field(description="Timestamp when account was created")

    model_config = ConfigDict(from_attributes=True)


class AuthTokensResponse(BaseModel):
    """JWT bearer and refresh token response."""

    access_token: str = Field(description="Cryptographically signed HMAC-SHA256 JWT access token")
    refresh_token: str = Field(description="Durable refresh token for renewing sessions")
    token_type: Literal["bearer"] = Field(
        default="bearer", description="Token authentication scheme"
    )
    expires_in: int = Field(default=3600, description="Access token expiration lifetime in seconds")


class AuthResponse(BaseModel):
    """Complete authentication payload containing user profile and tokens."""

    user: UserProfileResponse = Field(description="Authenticated user profile")
    tokens: AuthTokensResponse = Field(description="Access and refresh tokens")
    message: str | None = Field(
        default=None, description="Human-readable status or welcome message"
    )


class LoginRequest(BaseModel):
    """Request payload for logging in with email and password."""

    email: str = Field(pattern=EMAIL_REGEX, description="Account email address")
    password: str = Field(min_length=1, description="Account password")
    remember_me: bool = Field(default=True, description="Extend session duration flag")


class RegisterRequest(BaseModel):
    """Request payload for registering a new scholar account."""

    full_name: str = Field(min_length=1, max_length=100, description="Full name of researcher")
    email: str = Field(pattern=EMAIL_REGEX, description="Academic or institutional email address")
    password: str = Field(min_length=6, description="Strong password for authentication")
    confirm_password: str | None = Field(default=None, description="Optional password confirmation")
    institution: str | None = Field(
        default=None, max_length=255, description="Academic institution"
    )
    orcid_id: str | None = Field(default=None, max_length=50, description="ORCID identifier")
    accept_terms: bool = Field(default=True, description="Acceptance of terms of service")


class PasswordResetRequest(BaseModel):
    """Request payload to initiate forgot password workflow."""

    email: str = Field(pattern=EMAIL_REGEX, description="Email address registered with account")


class PasswordResetConfirmRequest(BaseModel):
    """Request payload to confirm password reset using token."""

    token: str = Field(min_length=1, description="Password reset verification token")
    new_password: str = Field(min_length=6, description="New secure password")


class ChangePasswordRequest(BaseModel):
    """Request payload for authenticated password change."""

    current_password: str = Field(min_length=1, description="Current valid password")
    new_password: str = Field(min_length=6, description="New secure password")
    confirm_password: str | None = Field(
        default=None, description="Optional confirmation of new password"
    )


class UpdateProfileRequest(BaseModel):
    """Request payload for updating user profile fields."""

    full_name: str | None = Field(default=None, min_length=1, max_length=100)
    institution: str | None = Field(default=None, max_length=255)
    academic_rank: str | None = Field(default=None, max_length=100)
    orcid_id: str | None = Field(default=None, max_length=50)
    avatar_url: str | None = Field(default=None, max_length=500)


class TokenRefreshRequest(BaseModel):
    """Request payload to renew access token using refresh token."""

    refresh_token: str = Field(min_length=1, description="Valid refresh token")


class AuthMessageResponse(BaseModel):
    """Generic message response envelope."""

    message: str = Field(description="Operation result message")
