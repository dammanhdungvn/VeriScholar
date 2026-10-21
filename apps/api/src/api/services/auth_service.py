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

import httpx
import structlog
from api.core.config import settings
from api.db.models.user import UserModel
from api.schemas.auth import (
    AuthTokensResponse,
    LoginRequest,
    RegisterRequest,
    UpdateProfileRequest,
)
from api.services.email_service import EmailService
from api.utils.email_validator import validate_academic_or_trusted_email
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger("api.services.auth")

# In-memory OTP cache with TTL: key -> {"code": str, "user_id": str, "exp": float}
_otp_cache: dict[str, dict[str, Any]] = {}


async def _save_otp_cache(key: str, data: dict[str, Any], ttl_seconds: int = 900) -> None:
    """Store OTP in in-memory cache and Redis if available for multi-worker support."""
    _otp_cache[key] = data
    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(
            settings.REDIS_URL, decode_responses=True, socket_connect_timeout=0.5
        )
        await client.set(f"verischolar:otp:{key}", json.dumps(data), ex=ttl_seconds)
        await client.aclose()
    except Exception as exc:
        logger.debug("redis_otp_save_fallback_in_memory", error=str(exc))


async def _get_otp_cache(key: str) -> dict[str, Any] | None:
    """Retrieve OTP from Redis or in-memory cache."""
    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(
            settings.REDIS_URL, decode_responses=True, socket_connect_timeout=0.5
        )
        val = await client.get(f"verischolar:otp:{key}")
        await client.aclose()
        if val:
            return json.loads(val)  # type: ignore[no-any-return]
    except Exception:
        pass

    cached = _otp_cache.get(key)
    if cached and time.time() < cached.get("exp", 0):
        return cached
    return None


class AuthService:
    """Service handling user registration, authentication, JWT tokens, and account profile."""

    def __init__(self, db: AsyncSession, email_service: EmailService | None = None) -> None:
        self.db = db
        self.email_service = email_service or EmailService()

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
        """Create access and refresh token pair for a user with persistent 30-day lifetime."""
        access_lifetime = (
            settings.REMEMBER_ME_ACCESS_TOKEN_EXPIRE_SECONDS
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
    async def register(self, payload: RegisterRequest) -> tuple[UserModel, AuthTokensResponse, str]:
        """Register a new user account with hashed password and initial credentials."""
        normalized_email = payload.email.strip().lower()

        # Check trusted email source (second-line defense)
        is_valid, err_msg = validate_academic_or_trusted_email(normalized_email)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "code": "INVALID_EMAIL_DOMAIN",
                    "message": err_msg or "Email không thuộc nguồn học thuật hoặc uy tín hợp lệ.",
                    "action": (
                        "Use an official academic email or trusted provider "
                        "(Gmail, Outlook, iCloud...)."
                    ),
                },
            )

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

        # Generate 6-digit OTP code and verification token
        otp_code = f"{secrets.randbelow(900000) + 100000}"
        verify_token = self.create_token(
            payload={
                "sub": str(new_user.id),
                "email": new_user.email,
                "type": "verify_email",
                "code": otp_code,
            },
            expires_delta_seconds=900,  # 15 minutes
        )
        await _save_otp_cache(
            f"verify:{normalized_email}",
            {
                "code": otp_code,
                "user_id": str(new_user.id),
                "exp": time.time() + 900,
            },
            ttl_seconds=900,
        )

        # Dispatch verification email (SMTP or audit log fallback)
        try:
            await self.email_service.send_verification_email(new_user.email, otp_code, verify_token)
        except Exception as exc:
            logger.warning("send_verification_email_error", error=str(exc))

        tokens = self.create_tokens_for_user(new_user, remember_me=True)
        return new_user, tokens, otp_code

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

    async def authenticate_google(self, id_token: str) -> tuple[UserModel, AuthTokensResponse]:
        """Verify Google ID token via Google tokeninfo API and authenticate/provision scholar."""
        if not id_token or not id_token.strip():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token Google không hợp lệ hoặc đã hết hạn",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_url = "https://oauth2.googleapis.com/tokeninfo"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(token_url, params={"id_token": id_token.strip()})
        except Exception as exc:
            logger.warning("google_tokeninfo_network_error", error=str(exc))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token Google không hợp lệ hoặc đã hết hạn",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        if resp.status_code != 200:
            logger.warning("google_tokeninfo_invalid", status_code=resp.status_code, body=resp.text)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token Google không hợp lệ hoặc đã hết hạn",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            token_data = resp.json()
        except Exception as exc:
            logger.warning("google_tokeninfo_json_error", error=str(exc))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token Google không hợp lệ hoặc đã hết hạn",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        # Verify audience to prevent OIDC Confused Deputy Attack
        expected_client_id = settings.GOOGLE_CLIENT_ID.strip()
        aud = token_data.get("aud")
        if not expected_client_id or aud != expected_client_id:
            logger.warning(
                "google_tokeninfo_audience_mismatch",
                expected_client_id=expected_client_id,
                actual_aud=aud,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token Google không hợp lệ hoặc audience không khớp với ứng dụng.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        email = token_data.get("email")
        if not email or not isinstance(email, str) or not email.strip():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token Google không hợp lệ hoặc đã hết hạn",
                headers={"WWW-Authenticate": "Bearer"},
            )

        email_verified = token_data.get("email_verified")
        if not (email_verified is True or str(email_verified).lower() == "true"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email Google chưa được xác thực bởi nhà cung cấp.",
            )

        normalized_email = email.strip().lower()

        # Strict whitelist domain validation
        is_valid, err_msg = validate_academic_or_trusted_email(normalized_email)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "code": "INVALID_EMAIL_DOMAIN",
                    "message": err_msg or "Email không thuộc nguồn học thuật hoặc uy tín hợp lệ.",
                    "action": (
                        "Vui lòng sử dụng tài khoản Google có email học thuật "
                        "(.edu, .edu.vn, .ac.*) hoặc nhà cung cấp uy tín (Gmail, Outlook, Proton)."
                    ),
                },
            )

        # Lookup existing user
        stmt = select(UserModel).where(func.lower(UserModel.email) == normalized_email)
        res = await self.db.execute(stmt)
        user = res.scalar_one_or_none()

        google_name = (
            token_data.get("name") or token_data.get("given_name") or normalized_email.split("@")[0]
        )
        full_name = " ".join(str(google_name).strip().split()) or "Nhà nghiên cứu Google"
        google_picture = token_data.get("picture")

        if user is None:
            random_pw = secrets.token_urlsafe(32)
            user = UserModel(
                id=uuid4(),
                email=normalized_email,
                full_name=full_name,
                hashed_password=self.hash_password(random_pw),
                role="researcher",
                is_active=True,
                is_verified=True,
                academic_rank="Nhà nghiên cứu Khoa học",
                avatar_url=str(google_picture).strip() if google_picture else None,
            )
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            logger.info(
                "google_auth_provisioned_new_user",
                user_id=str(user.id),
                email=normalized_email,
            )
        else:
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

            updated = False
            if not user.is_verified:
                user.is_verified = True
                updated = True
            if not user.avatar_url and google_picture:
                user.avatar_url = str(google_picture).strip()
                updated = True

            if updated:
                await self.db.commit()
                await self.db.refresh(user)

            logger.info(
                "google_auth_authenticated_existing_user",
                user_id=str(user.id),
                email=normalized_email,
            )

        tokens = self.create_tokens_for_user(user, remember_me=True)
        return user, tokens

    async def authenticate_github(
        self,
        code: str | None = None,
        redirect_uri: str | None = None,
        access_token: str | None = None,
    ) -> tuple[UserModel, AuthTokensResponse]:
        """Verify GitHub OAuth credentials and authenticate or provision scholar.

        Accepts either an authorization code (exchanged via GitHub OAuth API)
        or a pre-obtained GitHub access_token.
        Fetches scholar profile from https://api.github.com/user (and /user/emails
        if primary email is private), validates against trusted scholarly domains,
        and provisions or links user record with persistent JWT tokens.
        """
        github_token = access_token.strip() if (access_token and access_token.strip()) else None

        if not github_token:
            if not code or not code.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Vui lòng cung cấp mã code hoặc access_token từ GitHub.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            client_id = settings.GITHUB_CLIENT_ID.strip() if settings.GITHUB_CLIENT_ID else ""
            client_secret = (
                settings.GITHUB_CLIENT_SECRET.get_secret_value().strip()
                if hasattr(settings.GITHUB_CLIENT_SECRET, "get_secret_value")
                else str(settings.GITHUB_CLIENT_SECRET or "").strip()
            )

            if not client_id or not client_secret:
                logger.warning(
                    "github_oauth_unconfigured_client_credentials",
                    has_client_id=bool(client_id),
                    has_client_secret=bool(client_secret),
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=(
                        "GitHub OAuth chưa được cấu hình hoặc thông tin xác thực "
                        "ứng dụng không hợp lệ."
                    ),
                    headers={"WWW-Authenticate": "Bearer"},
                )

            token_url = "https://github.com/login/oauth/access_token"
            exchange_data: dict[str, str] = {
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code.strip(),
            }
            if redirect_uri and redirect_uri.strip():
                exchange_data["redirect_uri"] = redirect_uri.strip()

            exchange_headers = {
                "Accept": "application/json",
                "User-Agent": "VeriScholar-Backend/1.0",
            }

            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(
                        token_url, json=exchange_data, headers=exchange_headers
                    )
            except Exception as exc:
                logger.warning("github_token_exchange_network_error", error=str(exc))
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Không thể kết nối đến GitHub OAuth để đổi mã xác thực.",
                    headers={"WWW-Authenticate": "Bearer"},
                ) from exc

            if resp.status_code != 200:
                logger.warning(
                    "github_token_exchange_invalid_status",
                    status_code=resp.status_code,
                    body=resp.text,
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Mã xác thực GitHub không hợp lệ hoặc đã hết hạn",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            try:
                token_data = resp.json()
            except Exception as exc:
                logger.warning("github_token_exchange_json_error", error=str(exc))
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Phản hồi từ GitHub OAuth không hợp lệ.",
                    headers={"WWW-Authenticate": "Bearer"},
                ) from exc

            if "error" in token_data:
                err_desc = (
                    token_data.get("error_description")
                    or "Mã xác thực GitHub không hợp lệ hoặc đã hết hạn"
                )
                logger.warning(
                    "github_token_exchange_error_response",
                    error=token_data.get("error"),
                    description=err_desc,
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=err_desc,
                    headers={"WWW-Authenticate": "Bearer"},
                )

            github_token = token_data.get("access_token")
            if not github_token and "access_token=" in resp.text:
                from urllib.parse import parse_qs

                parsed = parse_qs(resp.text)
                if "access_token" in parsed and parsed["access_token"]:
                    github_token = parsed["access_token"][0]

            if not github_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Không thể lấy access token từ GitHub",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        # 2. Fetch User Profile from https://api.github.com/user
        user_url = "https://api.github.com/user"
        user_headers = {
            "Authorization": f"Bearer {github_token.strip()}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "VeriScholar-Backend/1.0",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                user_resp = await client.get(user_url, headers=user_headers)
        except Exception as exc:
            logger.warning("github_user_api_network_error", error=str(exc))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Không thể kết nối đến GitHub API để lấy thông tin người dùng.",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        if user_resp.status_code != 200:
            logger.warning(
                "github_user_api_invalid_status",
                status_code=user_resp.status_code,
                body=user_resp.text,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token GitHub không hợp lệ hoặc đã hết hạn",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            user_data = user_resp.json()
        except Exception as exc:
            logger.warning("github_user_json_error", error=str(exc))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Phản hồi từ GitHub API không đúng định dạng.",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        if user_data.get("email_verified") is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email GitHub chưa được xác thực bởi nhà cung cấp.",
            )

        # 3. Extract verified email (querying /user/emails if needed)
        email = user_data.get("email")
        if not email or not isinstance(email, str) or not email.strip():
            emails_url = "https://api.github.com/user/emails"
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    emails_resp = await client.get(emails_url, headers=user_headers)
                if emails_resp.status_code == 200:
                    emails_list = emails_resp.json()
                    if isinstance(emails_list, list) and emails_list:
                        verified_emails = [
                            e
                            for e in emails_list
                            if isinstance(e, dict) and e.get("verified") is True
                        ]
                        if verified_emails:
                            primary_email = next(
                                (
                                    e.get("email")
                                    for e in verified_emails
                                    if e.get("primary") is True and e.get("email")
                                ),
                                None,
                            )
                            email = primary_email or verified_emails[0].get("email")
                        else:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Email GitHub chưa được xác thực bởi nhà cung cấp.",
                            )
            except HTTPException:
                raise
            except Exception as exc:
                logger.warning("github_user_emails_api_error", error=str(exc))

        if not email or not isinstance(email, str) or not email.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không tìm thấy email hợp lệ gắn với tài khoản GitHub.",
            )

        normalized_email = email.strip().lower()

        is_valid, err_msg = validate_academic_or_trusted_email(normalized_email)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "code": "INVALID_EMAIL_DOMAIN",
                    "message": err_msg or "Email không thuộc nguồn học thuật hoặc uy tín hợp lệ.",
                    "action": (
                        "Vui lòng sử dụng tài khoản GitHub có email học thuật "
                        "(.edu, .edu.vn, .ac.*) hoặc nhà cung cấp uy tín (Gmail, Outlook, Proton)."
                    ),
                },
            )

        # 4. Lookup existing user
        stmt = select(UserModel).where(func.lower(UserModel.email) == normalized_email)
        res = await self.db.execute(stmt)
        user = res.scalar_one_or_none()

        github_name = (
            user_data.get("name") or user_data.get("login") or normalized_email.split("@")[0]
        )
        full_name = " ".join(str(github_name).strip().split()) or "Nhà nghiên cứu GitHub"
        github_avatar = user_data.get("avatar_url")

        if user is None:
            random_pw = secrets.token_urlsafe(32)
            user = UserModel(
                id=uuid4(),
                email=normalized_email,
                full_name=full_name,
                hashed_password=self.hash_password(random_pw),
                role="researcher",
                is_active=True,
                is_verified=True,
                academic_rank="Nhà nghiên cứu Khoa học",
                avatar_url=str(github_avatar).strip() if github_avatar else None,
            )
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            logger.info(
                "github_auth_provisioned_new_user",
                user_id=str(user.id),
                email=normalized_email,
            )
        else:
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

            updated = False
            if not user.is_verified:
                user.is_verified = True
                updated = True
            if not user.avatar_url and github_avatar:
                user.avatar_url = str(github_avatar).strip()
                updated = True

            if updated:
                await self.db.commit()
                await self.db.refresh(user)

            logger.info(
                "github_auth_authenticated_existing_user",
                user_id=str(user.id),
                email=normalized_email,
            )

        tokens = self.create_tokens_for_user(user, remember_me=True)
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

    async def forgot_password(self, email: str) -> tuple[str, str]:
        """Initiate password reset and generate a secure reset token & 6-digit OTP code."""
        normalized_email = email.strip().lower()
        stmt = select(UserModel).where(func.lower(UserModel.email) == normalized_email)
        res = await self.db.execute(stmt)
        user = res.scalar_one_or_none()

        otp_code = f"{secrets.randbelow(900000) + 100000}"

        if user is None:
            # Return dummy token or neutral success to prevent enumeration
            dummy_token = self.create_token(
                payload={
                    "sub": str(uuid4()),
                    "email": normalized_email,
                    "type": "reset",
                    "code": otp_code,
                },
                expires_delta_seconds=900,
            )
            return dummy_token, otp_code

        reset_token = self.create_token(
            payload={
                "sub": str(user.id),
                "email": user.email,
                "type": "reset",
                "code": otp_code,
            },
            expires_delta_seconds=900,  # 15 minutes
        )
        await _save_otp_cache(
            f"reset:{normalized_email}",
            {
                "code": otp_code,
                "user_id": str(user.id),
                "exp": time.time() + 900,
            },
            ttl_seconds=900,
        )

        # Dispatch email with OTP code and link
        try:
            await self.email_service.send_password_reset_email(user.email, otp_code, reset_token)
        except Exception as exc:
            logger.warning("send_password_reset_email_error", error=str(exc))

        return reset_token, otp_code

    async def reset_password(self, token: str, new_password: str, email: str | None = None) -> None:
        """Confirm password reset with valid token or 6-digit OTP code and update password."""
        user_id = None
        clean_token = token.strip()

        # Check if 6-digit OTP code was provided
        if len(clean_token) == 6 and clean_token.isdigit() and email:
            normalized_email = email.strip().lower()
            cached = await _get_otp_cache(f"reset:{normalized_email}")
            if cached and cached.get("code") == clean_token:
                user_id = UUID(cached["user_id"])
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "INVALID_RESET_CODE",
                        "message": "Mã xác thực 6 số không chính xác hoặc đã hết hạn (15 phút).",
                        "action": "Request a new password reset code.",
                    },
                )
        else:
            try:
                claims = self.decode_token(clean_token)
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "INVALID_RESET_TOKEN",
                        "message": (
                            f"Mã liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn: {exc}"
                        ),
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

    async def verify_email(self, email: str, token_or_code: str) -> UserModel:
        """Verify scholarly email address using 6-digit OTP code or JWT token."""
        normalized_email = email.strip().lower()
        clean_input = token_or_code.strip()

        is_valid = False

        if len(clean_input) == 6 and clean_input.isdigit():
            cached = await _get_otp_cache(f"verify:{normalized_email}")
            if cached and cached.get("code") == clean_input:
                is_valid = True
        else:
            try:
                claims = self.decode_token(clean_input)
                if claims.get("type") == "verify_email":
                    claim_email = claims.get("email")
                    if claim_email and (
                        not normalized_email or normalized_email == claim_email.lower()
                    ):
                        is_valid = True
                        normalized_email = claim_email.lower()
            except Exception:
                pass

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_VERIFICATION_CODE",
                    "message": (
                        "Mã xác thực không hợp lệ hoặc đã hết hạn (15 phút). "
                        "Vui lòng yêu cầu gửi lại mã mới."
                    ),
                },
            )

        stmt = select(UserModel).where(func.lower(UserModel.email) == normalized_email)
        res = await self.db.execute(stmt)
        user = res.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy tài khoản người dùng tương ứng với email này.",
            )

        user.is_verified = True
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def resend_verification(self, email: str) -> str:
        """Resend email verification OTP code and token."""
        normalized_email = email.strip().lower()
        stmt = select(UserModel).where(func.lower(UserModel.email) == normalized_email)
        res = await self.db.execute(stmt)
        user = res.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy tài khoản đăng ký với email này.",
            )

        otp_code = f"{secrets.randbelow(900000) + 100000}"
        verify_token = self.create_token(
            payload={
                "sub": str(user.id),
                "email": user.email,
                "type": "verify_email",
                "code": otp_code,
            },
            expires_delta_seconds=900,
        )
        await _save_otp_cache(
            f"verify:{normalized_email}",
            {
                "code": otp_code,
                "user_id": str(user.id),
                "exp": time.time() + 900,
            },
            ttl_seconds=900,
        )
        try:
            await self.email_service.send_verification_email(user.email, otp_code, verify_token)
        except Exception as exc:
            logger.warning("resend_verification_email_error", error=str(exc))
        return otp_code

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
        if payload.department is not None:
            user.department = payload.department.strip()
        if payload.bio is not None:
            user.bio = payload.bio.strip()
        if payload.research_interests is not None:
            user.research_interests = payload.research_interests.strip()
        if payload.google_scholar_url is not None:
            user.google_scholar_url = payload.google_scholar_url.strip()

        await self.db.commit()
        await self.db.refresh(user)
        return user
