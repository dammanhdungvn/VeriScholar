"""Pydantic schemas for Authentication, Authorization & User Profiles.

Strictly 1-1 aligned with Frontend domain types (apps/web/src/types/auth.ts).
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from api.core.email_validator import (
    validate_academic_or_trusted_email,
    validate_user_full_name,
)
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

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
    department: str | None = Field(
        default=None, description="Department or faculty within institution"
    )
    bio: str | None = Field(default=None, description="Scholar biographical summary")
    research_interests: str | None = Field(
        default=None, description="Primary research domains and keywords"
    )
    google_scholar_url: str | None = Field(
        default=None, description="Link to Google Scholar profile"
    )
    theme_preference: str = Field(
        default="system", description="UI color theme preference (light, dark, system)"
    )
    has_byok: bool = Field(
        default=False, description="Whether the user has configured a personal BYOK API key"
    )
    byok_masked: str | None = Field(
        default=None, description="Masked representation of the user's BYOK API key"
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
    verification_code_debug: str | None = Field(
        default=None, description="Debug OTP code in staging / dev environments"
    )


class LoginRequest(BaseModel):
    """Request payload for logging in with email and password with Layer-2 schema validation."""

    email: str = Field(pattern=EMAIL_REGEX, description="Account email address")
    password: str = Field(min_length=1, description="Account password")
    remember_me: bool = Field(default=True, description="Extend session duration flag (30 days)")

    @field_validator("email", mode="before")
    @classmethod
    def normalize_and_validate_email(cls, v: str) -> str:
        if isinstance(v, str):
            clean = v.strip().lower()
            if not clean:
                raise ValueError("Email không được để trống.")
            return clean
        return v

    @field_validator("password")
    @classmethod
    def validate_password_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Mật khẩu không được để trống.")
        return v


class RegisterRequest(BaseModel):
    """Request payload for registering a new scholar account with Layer-2 validation."""

    full_name: str = Field(min_length=2, max_length=100, description="Full name of researcher")
    email: str = Field(pattern=EMAIL_REGEX, description="Academic or institutional email address")
    password: str = Field(min_length=6, description="Strong password for authentication")
    confirm_password: str | None = Field(default=None, description="Optional password confirmation")
    institution: str | None = Field(
        default=None, max_length=255, description="Academic institution"
    )
    orcid_id: str | None = Field(default=None, max_length=50, description="ORCID identifier")
    accept_terms: bool = Field(default=True, description="Acceptance of terms of service")

    @field_validator("email", mode="before")
    @classmethod
    def validate_trusted_email(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Email không được để trống.")
        clean_email = v.strip().lower()
        is_valid, err_msg = validate_academic_or_trusted_email(clean_email)
        if not is_valid:
            raise ValueError(err_msg or "Email không thuộc nguồn học thuật hoặc uy tín hợp lệ.")
        return clean_email

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        is_valid, err_msg = validate_user_full_name(v)
        if not is_valid:
            raise ValueError(err_msg or "Họ và tên không hợp lệ.")
        return " ".join(v.strip().split())

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Mật khẩu không được để trống.")
        if len(v) < 6:
            raise ValueError("Mật khẩu phải có độ dài tối thiểu 6 ký tự.")
        return v

    @model_validator(mode="after")
    def validate_confirm_password(self) -> "RegisterRequest":
        if self.confirm_password is not None and self.confirm_password != self.password:
            raise ValueError("Mật khẩu xác nhận không khớp.")
        return self


class VerifyEmailRequest(BaseModel):
    """Request payload to verify scholarly email via OTP code or JWT token."""

    email: str = Field(pattern=EMAIL_REGEX, description="Email address being verified")
    token: str | None = Field(default=None, description="JWT verification token")
    code: str | None = Field(default=None, description="6-digit verification OTP code")
    otp: str | None = Field(default=None, description="Alias for 6-digit verification OTP code")

    @model_validator(mode="after")
    def check_token_or_code(self) -> "VerifyEmailRequest":
        if not self.token and not self.code and not self.otp:
            raise ValueError("Vui lòng cung cấp mã OTP 6 số hoặc liên kết token xác thực.")
        if not self.code and self.otp:
            self.code = self.otp
        return self


class ResendVerificationRequest(BaseModel):
    """Request payload to resend verification email."""

    email: str = Field(pattern=EMAIL_REGEX, description="Email address to resend verification to")


class PasswordResetRequest(BaseModel):
    """Request payload to initiate forgot password workflow."""

    email: str = Field(pattern=EMAIL_REGEX, description="Email address registered with account")


class PasswordResetConfirmRequest(BaseModel):
    """Request payload to confirm password reset using token or 6-digit OTP code."""

    token: str = Field(
        min_length=1, description="Password reset verification token or 6-digit code"
    )
    new_password: str = Field(min_length=6, description="New secure password")
    email: str | None = Field(
        default=None, description="Optional email when using 6-digit OTP code"
    )


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
    department: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=1000)
    research_interests: str | None = Field(default=None, max_length=500)
    google_scholar_url: str | None = Field(default=None, max_length=500)
    theme_preference: str | None = Field(default=None, max_length=20)
    byok_api_key: str | None = Field(default=None, max_length=500)


class TokenRefreshRequest(BaseModel):
    """Request payload to renew access token using refresh token."""

    refresh_token: str = Field(min_length=1, description="Valid refresh token")


class GoogleAuthRequest(BaseModel):
    """Request payload for Google OAuth 2.0 id_token authentication."""

    id_token: str = Field(min_length=1, description="Google OAuth 2.0 ID Token (JWT)")


class GitHubAuthRequest(BaseModel):
    """Request payload for GitHub OAuth authentication.

    Accepts either an authorization code (with optional redirect_uri)
    or a pre-obtained GitHub access_token.
    """

    code: str | None = Field(
        default=None,
        description="GitHub OAuth authorization code",
    )
    redirect_uri: str | None = Field(
        default=None,
        description="Optional OAuth redirect URI",
    )
    access_token: str | None = Field(
        default=None,
        description="GitHub OAuth access token",
    )

    @model_validator(mode="after")
    def validate_code_or_token(self) -> "GitHubAuthRequest":
        has_code = bool(self.code and self.code.strip())
        has_token = bool(self.access_token and self.access_token.strip())
        if not has_code and not has_token:
            raise ValueError("Vui lòng cung cấp 'code' hoặc 'access_token' từ GitHub.")
        return self


class AuthMessageResponse(BaseModel):
    """Generic message response envelope."""

    message: str = Field(description="Operation result message")
