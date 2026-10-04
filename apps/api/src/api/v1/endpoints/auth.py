"""Authentication and user account endpoints."""

from typing import Any

from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import get_auth_service, get_cost_control_service, get_current_user
from api.schemas.auth import (
    AuthTokenEnvelope,
    GoogleLoginRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenQuotaEnvelope,
    UserProfileEnvelope,
)
from api.schemas.envelope import ResponseMeta
from api.services.auth_service import AuthService
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserProfileEnvelope,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản người dùng mới",
    description=(
        "Tạo tài khoản người dùng mới với mật khẩu được băm bằng thuật toán Argon2id an toàn."
    ),
)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserProfileEnvelope:
    """Register a new user account."""
    user = await auth_service.register_user(db=db, request=request)
    return UserProfileEnvelope(
        success=True,
        data=auth_service.to_user_response(user),
        meta=ResponseMeta(),
    )


@router.post(
    "/login",
    response_model=AuthTokenEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập tài khoản & Nhận JWT tokens",
    description=(
        "Xác thực người dùng qua email và mật khẩu, trả về cặp Access Token và Refresh Token."
    ),
)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthTokenEnvelope:
    """Authenticate user and issue JWT token pair."""
    user = await auth_service.authenticate_user(db=db, request=request)
    tokens = auth_service.create_token_response(user)
    return AuthTokenEnvelope(
        success=True,
        data=tokens,
        meta=ResponseMeta(),
    )


@router.post(
    "/refresh",
    response_model=AuthTokenEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Cấp mới Access Token bằng Refresh Token",
    description=(
        "Kiểm tra tính hợp lệ của Refresh Token và cấp phát cặp token mới mà không cần "
        "đăng nhập lại."
    ),
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthTokenEnvelope:
    """Issue new token pair using valid refresh token."""
    tokens = await auth_service.refresh_access_token(db=db, refresh_token_str=request.refresh_token)
    return AuthTokenEnvelope(
        success=True,
        data=tokens,
        meta=ResponseMeta(),
    )


@router.post(
    "/google",
    response_model=AuthTokenEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập hoặc đăng ký bằng tài khoản Google",
    description=(
        "Xác thực qua Google ID token, tự động tạo tài khoản nếu chưa tồn tại "
        "và cấp phát JWT tokens."
    ),
)
async def google_login(
    request: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthTokenEnvelope:
    """Authenticate or register user with Google OAuth."""
    user = await auth_service.authenticate_google(db=db, credential=request.credential)
    tokens = auth_service.create_token_response(user)
    return AuthTokenEnvelope(
        success=True,
        data=tokens,
        meta=ResponseMeta(),
    )


@router.get(
    "/me",
    response_model=UserProfileEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Lấy thông tin người dùng hiện tại",
    description="Trả về thông tin hồ sơ của người dùng đang được xác thực qua Bearer JWT Token.",
)
async def get_me(
    current_user: UserModel = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserProfileEnvelope:
    """Return profile of currently authenticated user."""
    return UserProfileEnvelope(
        success=True,
        data=auth_service.to_user_response(current_user),
        meta=ResponseMeta(),
    )


@router.get(
    "/quota",
    response_model=TokenQuotaEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Kiểm tra hạn mức Token và dung lượng lưu trữ (BỔ SUNG 1)",
    description=(
        "Trả về chi tiết số token đã dùng, số token còn lại, tỷ lệ sử dụng "
        "và cảnh báo vượt hạn mức."
    ),
)
async def get_quota_status(
    current_user: UserModel = Depends(get_current_user),
    cost_service: Any = Depends(get_cost_control_service),
) -> TokenQuotaEnvelope:
    """Return live token quota and storage allocation status."""
    status_data = cost_service.get_quota_status(current_user)
    return TokenQuotaEnvelope(
        success=True,
        data=status_data,
        meta=ResponseMeta(),
    )
