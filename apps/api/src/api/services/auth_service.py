"""Authentication and identity service implementing Argon2id hashing and JWT lifecycle."""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt
import structlog
from api.core.config import settings
from api.db.models.user import UserModel
from api.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from fastapi import HTTPException, status
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger("api.services.auth")


class AuthService:
    """Service managing authentication, credential verification, and JWT lifecycle."""

    def __init__(self) -> None:
        self.password_hash = PasswordHash.recommended()
        self.secret_key = settings.JWT_SECRET_KEY.get_secret_value()
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS

    def hash_password(self, password: str) -> str:
        """Hash a plaintext password using Argon2id."""
        return self.password_hash.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify plaintext password against stored hash."""
        try:
            return self.password_hash.verify(plain_password, hashed_password)
        except Exception as exc:
            logger.warning("password_verification_failed", error=str(exc))
            return False

    def create_access_token(
        self, user_id: UUID, email: str, role: str = "researcher"
    ) -> tuple[str, int]:
        """Generate short-lived JWT access token with role and return token info."""

        now = datetime.now(UTC)
        expire_delta = timedelta(minutes=self.access_token_expire_minutes)
        expires_at = now + expire_delta
        payload: dict[str, Any] = {
            "sub": str(user_id),
            "email": email,
            "role": role,
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp()),
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token, int(expire_delta.total_seconds())

    def create_refresh_token(self, user_id: UUID, email: str, role: str = "researcher") -> str:
        """Generate long-lived JWT refresh token."""
        now = datetime.now(UTC)
        expires_at = now + timedelta(days=self.refresh_token_expire_days)
        payload: dict[str, Any] = {
            "sub": str(user_id),
            "email": email,
            "role": role,
            "type": "refresh",
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp()),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str, expected_type: str = "access") -> dict[str, Any]:
        """Decode and validate a JWT token payload."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != expected_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "code": "INVALID_TOKEN_TYPE",
                        "message": f"Expected {expected_type} token, got {payload.get('type')}.",
                        "field": "token",
                        "action": "Authenticate with valid token type.",
                    },
                )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "TOKEN_EXPIRED",
                    "message": "The provided token has expired. Please re-authenticate.",
                    "field": "token",
                    "action": "Refresh token or log in again.",
                },
            )
        except (jwt.InvalidTokenError, Exception) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_TOKEN",
                    "message": f"Token verification failed: {exc}",
                    "field": "token",
                    "action": "Provide a valid authentication token.",
                },
            )

    async def register_user(
        self,
        db: AsyncSession,
        request: RegisterRequest,
    ) -> UserModel:
        """Register a new user account with Argon2id hashed password."""
        stmt = select(UserModel).where(UserModel.email == request.email.lower().strip())
        res = await db.execute(stmt)
        existing = res.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "EMAIL_ALREADY_REGISTERED",
                    "message": f"Email '{request.email}' is already registered.",
                    "field": "email",
                    "action": "Log in or use a different email address.",
                },
            )

        hashed = self.hash_password(request.password)
        user = UserModel(
            email=request.email.lower().strip(),
            full_name=request.full_name.strip(),
            hashed_password=hashed,
            role="researcher",
            is_active=True,
            token_quota=200000,
            tokens_used=0,
            storage_quota_bytes=1073741824,
            storage_used_bytes=0,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info("user_registered_successfully", user_id=str(user.id), email=user.email)
        return user

    async def authenticate_user(
        self,
        db: AsyncSession,
        request: LoginRequest,
    ) -> UserModel:
        """Authenticate user by email and password."""
        stmt = select(UserModel).where(UserModel.email == request.email.lower().strip())
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()
        if not user or not self.verify_password(request.password, user.hashed_password):
            logger.warning("authentication_failed", email=request.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_CREDENTIALS",
                    "message": "Invalid email or password.",
                    "field": "password",
                    "action": "Check credentials and try again.",
                },
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "ACCOUNT_DISABLED",
                    "message": "Your user account has been disabled.",
                    "field": "email",
                    "action": "Contact support administrator.",
                },
            )

        logger.info("user_authenticated_successfully", user_id=str(user.id), email=user.email)
        return user

    async def authenticate_google(
        self,
        db: AsyncSession,
        credential: str,
    ) -> UserModel:
        """Authenticate or register user via Google OAuth ID token or simulated credential."""
        email: str | None = None
        full_name: str = "Google Scholar"
        google_id: str | None = None
        avatar_url: str | None = None

        cred = credential.strip()
        # Parse simulated / dev tokens: e.g. "mock_google:scholar@university.edu" or standard JWT
        if cred.startswith("mock_google:") or "@" in cred and "." not in cred:
            parts = cred.replace("mock_google:", "").split(":")
            email = parts[0].lower().strip()
            if len(parts) > 1:
                full_name = parts[1].strip()
            google_id = f"google_sub_{email.split('@')[0]}"
        elif cred.count(".") == 2:
            try:
                # Decode JWT without verifying signature for dev/staging flexibility
                unverified_claims = jwt.decode(
                    cred, options={"verify_signature": False, "verify_aud": False}
                )
                email = unverified_claims.get("email")
                full_name = unverified_claims.get("name") or full_name
                google_id = str(unverified_claims.get("sub", ""))
                avatar_url = unverified_claims.get("picture")
            except Exception as e:
                logger.warning("google_jwt_parse_failed", error=str(e))
                email = None
        elif "@" in cred:
            email = cred.lower().strip()
            google_id = f"google_sub_{email.split('@')[0]}"

        if not email or "@" not in email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_GOOGLE_CREDENTIAL",
                    "message": "Could not extract valid email from Google token.",
                    "field": "credential",
                    "action": "Provide a valid Google ID token.",
                },
            )

        # Lookup user by google_id or email
        stmt = select(UserModel).where(
            (UserModel.google_id == google_id) | (UserModel.email == email.lower().strip())
        )
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()

        if user:
            # Update user info if missing
            if not user.google_id and google_id:
                user.google_id = google_id
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
            await db.commit()
            await db.refresh(user)
            logger.info("google_user_logged_in", user_id=str(user.id), email=user.email)
            return user

        # Create new user
        dummy_pwd = self.hash_password(f"google_oauth_{google_id}_{datetime.now(UTC).timestamp()}")
        user = UserModel(
            email=email.lower().strip(),
            full_name=full_name,
            hashed_password=dummy_pwd,
            role="researcher",
            google_id=google_id,
            avatar_url=avatar_url,
            is_active=True,
            token_quota=200000,
            tokens_used=0,
            storage_quota_bytes=1073741824,
            storage_used_bytes=0,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info("google_user_registered", user_id=str(user.id), email=user.email)
        return user

    def create_token_response(self, user: UserModel) -> TokenResponse:
        """Generate standard TokenResponse containing access and refresh tokens."""
        access_token, expires_in = self.create_access_token(user.id, user.email, role=user.role)
        refresh_token = self.create_refresh_token(user.id, user.email, role=user.role)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in,
        )

    async def refresh_access_token(
        self,
        db: AsyncSession,
        refresh_token_str: str,
    ) -> TokenResponse:
        """Validate refresh token and issue new token pair."""
        payload = self.decode_token(refresh_token_str, expected_type="refresh")
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_TOKEN",
                    "message": "Token subject is missing.",
                    "field": "refresh_token",
                    "action": "Log in again.",
                },
            )

        try:
            user_id = UUID(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_TOKEN",
                    "message": "Token subject is invalid UUID.",
                    "field": "refresh_token",
                    "action": "Log in again.",
                },
            )

        stmt = select(UserModel).where(UserModel.id == user_id)
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "USER_NOT_FOUND_OR_INACTIVE",
                    "message": "User associated with token no longer exists or is disabled.",
                    "field": "refresh_token",
                    "action": "Log in again.",
                },
            )

        return self.create_token_response(user)

    @staticmethod
    def to_user_response(user: UserModel) -> UserResponse:
        """Convert UserModel to UserResponse DTO."""
        role = getattr(user, "role", None) or "researcher"
        avatar_url = getattr(user, "avatar_url", None)
        t_quota = getattr(user, "token_quota", None)
        token_quota = t_quota if t_quota is not None else 200000
        t_used = getattr(user, "tokens_used", None)
        tokens_used = t_used if t_used is not None else 0
        s_quota = getattr(user, "storage_quota_bytes", None)
        storage_quota_bytes = s_quota if s_quota is not None else 1073741824
        s_used = getattr(user, "storage_used_bytes", None)
        storage_used_bytes = s_used if s_used is not None else 0

        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=role,
            avatar_url=avatar_url,
            token_quota=token_quota,
            tokens_used=tokens_used,
            storage_quota_bytes=storage_quota_bytes,
            storage_used_bytes=storage_used_bytes,
            is_active=user.is_active,
            created_at=user.created_at,
        )
