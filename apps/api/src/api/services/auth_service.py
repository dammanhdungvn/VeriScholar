"""Authentication, JWT Token & Account Management Service.

Implements OWASP PBKDF2-HMAC-SHA256 password hashing and HMAC-SHA256 JWT tokens.
"""

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any
from uuid import UUID, uuid4

import structlog
from api.core.config import settings
from api.db.models.user import UserModel
from api.schemas.auth import (
    AuthTokensResponse,
    LoginRequest,
    RegisterRequest,
    UpdateProfileRequest,
)
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger("api.services.auth")


class AuthService:
    """Service handling user registration, authentication, JWT tokens, and account profile."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # --------------------------------------------------------------------------
    # Cryptographic & Password Hashing Utilities (OWASP PBKDF2-HMAC-SHA256)
    # --------------------------------------------------------------------------
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using OWASP PBKDF2-HMAC-SHA256 with per-user random salt."""
        salt = secrets.token_hex(16)
        iterations = 100_000
        hash_bytes = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        )
        return f"pbkdf2_sha256${iterations}${salt}${hash_bytes.hex()}"

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify plain password against stored hash."""
        # Dev user fallback
        if hashed_password == "dev_dummy_password" and plain_password == "dev_dummy_password":
            return True

        if not hashed_password.startswith("pbkdf2_sha256$"):
            return hmac.compare_digest(plain_password, hashed_password)

        parts = hashed_password.split("$")
        if len(parts) != 4:
            return False

        try:
            iterations = int(parts[1])
            salt = parts[2]
            expected_hex = parts[3]
            calculated_hex = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                salt.encode("utf-8"),
                iterations,
            ).hex()
            return hmac.compare_digest(expected_hex, calculated_hex)
        except Exception as exc:
            logger.warning("password_verification_failed", error=str(exc))
            return False

    # --------------------------------------------------------------------------
    # Native HMAC-SHA256 JWT Token Handling (RFC 7519)
    # --------------------------------------------------------------------------
    @staticmethod
    def _b64_url_encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

    @staticmethod
    def _b64_url_decode(data_str: str) -> bytes:
        padding = 4 - (len(data_str) % 4)
        if padding != 4:
            data_str += "=" * padding
        return base64.urlsafe_b64decode(data_str.encode("ascii"))

    @classmethod
    def create_token(cls, payload: dict[str, Any], expires_delta_seconds: int) -> str:
        """Generate cryptographically signed HMAC-SHA256 JWT token."""
        header = {"alg": "HS256", "typ": "JWT"}
        now = int(time.time())
        claims = payload.copy()
        claims["iat"] = now
        claims["exp"] = now + expires_delta_seconds

        header_b64 = cls._b64_url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        payload_b64 = cls._b64_url_encode(json.dumps(claims, separators=(",", ":")).encode("utf-8"))
        signing_input = f"{header_b64}.{payload_b64}".encode("ascii")

        secret = settings.JWT_SECRET_KEY.encode("utf-8")
        signature = hmac.new(secret, signing_input, hashlib.sha256).digest()
        signature_b64 = cls._b64_url_encode(signature)

        return f"{header_b64}.{payload_b64}.{signature_b64}"

    @classmethod
    def decode_token(cls, token: str) -> dict[str, Any]:
        """Decode and verify HMAC-SHA256 JWT signature and expiration."""
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid JWT structure: must have 3 segments")

        header_b64, payload_b64, signature_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode("ascii")

        secret = settings.JWT_SECRET_KEY.encode("utf-8")
        expected_sig = hmac.new(secret, signing_input, hashlib.sha256).digest()

        try:
            actual_sig = cls._b64_url_decode(signature_b64)
        except Exception as exc:
            raise ValueError(f"Invalid base64 signature encoding: {exc}") from exc

        if not hmac.compare_digest(expected_sig, actual_sig):
            raise ValueError("JWT signature verification failed")

        try:
            payload_json = cls._b64_url_decode(payload_b64).decode("utf-8")
            claims = json.loads(payload_json)
        except Exception as exc:
            raise ValueError(f"Invalid JWT payload JSON: {exc}") from exc

        if "exp" in claims and time.time() > claims["exp"]:
            raise ValueError("JWT token has expired")

        return claims

    def create_tokens_for_user(
        self, user: UserModel, remember_me: bool = True
    ) -> AuthTokensResponse:
        """Create access and refresh token pair for a user."""
        access_lifetime = (
            settings.REFRESH_TOKEN_EXPIRE_SECONDS
            if remember_me
            else settings.ACCESS_TOKEN_EXPIRE_SECONDS
        )
        refresh_lifetime = settings.REFRESH_TOKEN_EXPIRE_SECONDS

        access_token = self.create_token(
            payload={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role,
                "type": "access",
            },
            expires_delta_seconds=access_lifetime,
        )

        refresh_token = self.create_token(
            payload={
                "sub": str(user.id),
                "type": "refresh",
            },
            expires_delta_seconds=refresh_lifetime,
        )

        return AuthTokensResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=access_lifetime,
        )

    # --------------------------------------------------------------------------
    # Authentication & Account Workflows
    # --------------------------------------------------------------------------
    async def register(self, payload: RegisterRequest) -> tuple[UserModel, AuthTokensResponse]:
        """Register a new user account with hashed password and initial credentials."""
        normalized_email = payload.email.strip().lower()

        # Check existing user
        stmt = select(UserModel).where(func.lower(UserModel.email) == normalized_email)
        res = await self.db.execute(stmt)
        if res.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "EMAIL_ALREADY_EXISTS",
                    "message": (
                        "Email học thuật này đã được đăng ký. "
                        "Vui lòng đăng nhập hoặc sử dụng email khác."
                    ),
                    "action": "Use an alternate email address or log in.",
                },
            )

        new_user = UserModel(
            id=uuid4(),
            email=normalized_email,
            full_name=payload.full_name.strip(),
            hashed_password=self.hash_password(payload.password),
            is_active=True,
            role="researcher",
            institution=payload.institution.strip() if payload.institution else None,
            academic_rank="Nhà nghiên cứu Khoa học",
            orcid_id=payload.orcid_id.strip() if payload.orcid_id else None,
            avatar_url=None,
            is_verified=False,
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        tokens = self.create_tokens_for_user(new_user, remember_me=True)
        return new_user, tokens

    async def login(self, payload: LoginRequest) -> tuple[UserModel, AuthTokensResponse]:
        """Authenticate user credentials and issue token pair."""
        normalized_email = payload.email.strip().lower()

        stmt = select(UserModel).where(func.lower(UserModel.email) == normalized_email)
        res = await self.db.execute(stmt)
        user = res.scalar_one_or_none()

        if user is None or not self.verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_CREDENTIALS",
                    "message": "Email hoặc mật khẩu không chính xác. Vui lòng thử lại.",
                    "action": "Verify your email and password or use password reset.",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "ACCOUNT_INACTIVE",
                    "message": "Tài khoản của bạn hiện đang bị vô hiệu hóa.",
                    "action": "Contact system administrator.",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        tokens = self.create_tokens_for_user(user, remember_me=payload.remember_me)
        return user, tokens

    async def refresh_tokens(self, refresh_token: str) -> AuthTokensResponse:
        """Renew access token pair using a valid refresh token."""
        try:
            claims = self.decode_token(refresh_token)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_REFRESH_TOKEN",
                    "message": f"Refresh token không hợp lệ hoặc đã hết hạn: {exc}",
                    "action": "Log in again to obtain a new session.",
                },
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        if claims.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_TOKEN_TYPE",
                    "message": "Token cung cấp không phải là refresh token.",
                    "action": "Provide a valid refresh token.",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id_str = claims.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_TOKEN_CLAIMS",
                    "message": "Token thiếu thông tin định danh người dùng.",
                    "action": "Log in again.",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            user_id = UUID(user_id_str)
        except (ValueError, TypeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_USER_ID", "message": "Định danh người dùng không hợp lệ."},
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        stmt = select(UserModel).where(UserModel.id == user_id)
        res = await self.db.execute(stmt)
        user = res.scalar_one_or_none()

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": "Người dùng không tồn tại hoặc đã bị khóa.",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        return self.create_tokens_for_user(user, remember_me=True)

    async def forgot_password(self, email: str) -> str:
        """Initiate password reset and generate a secure reset token."""
        normalized_email = email.strip().lower()
        stmt = select(UserModel).where(func.lower(UserModel.email) == normalized_email)
        res = await self.db.execute(stmt)
        user = res.scalar_one_or_none()

        if user is None:
            # Return dummy token or neutral success to prevent enumeration
            return self.create_token(
                payload={"sub": str(uuid4()), "email": normalized_email, "type": "reset"},
                expires_delta_seconds=900,
            )

        reset_token = self.create_token(
            payload={"sub": str(user.id), "email": user.email, "type": "reset"},
            expires_delta_seconds=900,  # 15 minutes
        )
        return reset_token

    async def reset_password(self, token: str, new_password: str) -> None:
        """Confirm password reset with valid token and update password."""
        try:
            claims = self.decode_token(token)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_RESET_TOKEN",
                    "message": f"Mã liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn: {exc}",
                    "action": "Request a new password reset link.",
                },
            ) from exc

        if claims.get("type") != "reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_TOKEN_TYPE",
                    "message": "Token không hợp lệ cho tác vụ đặt lại mật khẩu.",
                    "action": "Use the valid link sent to your email.",
                },
            )

        user_id_str = claims.get("sub")
        try:
            user_id = UUID(user_id_str)
        except (ValueError, TypeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_USER_ID",
                    "message": "ID người dùng trong token không hợp lệ.",
                },
            ) from exc

        stmt = select(UserModel).where(UserModel.id == user_id)
        res = await self.db.execute(stmt)
        user = res.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": "Không tìm thấy tài khoản người dùng.",
                },
            )

        user.hashed_password = self.hash_password(new_password)
        await self.db.commit()

    async def change_password(
        self, user: UserModel, current_password: str, new_password: str
    ) -> None:
        """Change password for an authenticated user."""
        if not self.verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INCORRECT_CURRENT_PASSWORD",
                    "message": "Mật khẩu hiện tại không chính xác.",
                    "action": "Check your current password and try again.",
                },
            )

        user.hashed_password = self.hash_password(new_password)
        await self.db.commit()

    async def update_profile(self, user: UserModel, payload: UpdateProfileRequest) -> UserModel:
        """Update authenticated user's profile details."""
        if payload.full_name is not None:
            user.full_name = payload.full_name.strip()
        if payload.institution is not None:
            user.institution = payload.institution.strip()
        if payload.academic_rank is not None:
            user.academic_rank = payload.academic_rank.strip()
        if payload.orcid_id is not None:
            user.orcid_id = payload.orcid_id.strip()
        if payload.avatar_url is not None:
            user.avatar_url = payload.avatar_url.strip()

        await self.db.commit()
        await self.db.refresh(user)
        return user
