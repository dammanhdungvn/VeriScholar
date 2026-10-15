"""Authentication and Account Management API Endpoints."""

import structlog
from api.db.models.user import UserModel
from api.deps import get_auth_service, get_current_user
from api.schemas.auth import (
    AuthMessageResponse,
    AuthResponse,
    AuthTokensResponse,
    ChangePasswordRequest,
    LoginRequest,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    RegisterRequest,
    TokenRefreshRequest,
    UpdateProfileRequest,
    UserProfileResponse,
)
from api.schemas.envelope import ResponseMeta, SingleResponseEnvelope
from api.services.auth_service import AuthService
from fastapi import APIRouter, Depends, status

logger = structlog.get_logger("api.endpoints.auth")

router = APIRouter(prefix="/auth", tags=["auth"])


# ==============================================================================
# 1. POST /api/v1/auth/register
# ==============================================================================
@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleResponseEnvelope[AuthResponse],
    summary="Đăng ký tài khoản học thuật mới (Register)",
    description=(
        "Tạo tài khoản nhà nghiên cứu mới với mật khẩu bảo mật PBKDF2-HMAC-SHA256 "
        "và sinh bộ JWT tokens."
    ),
)
async def register(
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleResponseEnvelope[AuthResponse]:
    """Register a new user account and return profile with credentials."""
    user, tokens = await auth_service.register(payload)
    return SingleResponseEnvelope(
        data=AuthResponse(
            user=UserProfileResponse.model_validate(user),
            tokens=tokens,
            message=(
                "Đăng ký tài khoản thành viên nghiên cứu thành công! "
                "Chào mừng bạn đến với VeriScholar."
            ),
        ),
        meta=ResponseMeta(),
    )


# ==============================================================================
# 2. POST /api/v1/auth/login
# ==============================================================================
@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=SingleResponseEnvelope[AuthResponse],
    summary="Đăng nhập tài khoản (Login)",
    description="Xác thực thông tin đăng nhập và cấp cặp access_token/refresh_token HMAC-SHA256.",
)
async def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleResponseEnvelope[AuthResponse]:
    """Authenticate user with email and password."""
    user, tokens = await auth_service.login(payload)
    return SingleResponseEnvelope(
        data=AuthResponse(
            user=UserProfileResponse.model_validate(user),
            tokens=tokens,
            message="Đăng nhập thành công vào VeriScholar.",
        ),
        meta=ResponseMeta(),
    )


# ==============================================================================
# 3. POST /api/v1/auth/logout
# ==============================================================================
@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    response_model=SingleResponseEnvelope[AuthMessageResponse],
    summary="Đăng xuất phiên làm việc (Logout)",
    description="Hủy bỏ phiên làm việc của người dùng hiện tại.",
)
async def logout(
    current_user: UserModel = Depends(get_current_user),
) -> SingleResponseEnvelope[AuthMessageResponse]:
    """Invalidate current user session."""
    return SingleResponseEnvelope(
        data=AuthMessageResponse(message="Đăng xuất thành công khỏi hệ thống."),
        meta=ResponseMeta(),
    )


# ==============================================================================
# 4. POST /api/v1/auth/refresh
# ==============================================================================
@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=SingleResponseEnvelope[AuthTokensResponse],
    summary="Làm mới Access Token (Token Refresh)",
    description="Cấp mới cặp tokens từ refresh_token hợp lệ mà không cần đăng nhập lại.",
)
async def refresh_tokens(
    payload: TokenRefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleResponseEnvelope[AuthTokensResponse]:
    """Renew authentication tokens using valid refresh token."""
    new_tokens = await auth_service.refresh_tokens(payload.refresh_token)
    return SingleResponseEnvelope(
        data=new_tokens,
        meta=ResponseMeta(),
    )


# ==============================================================================
# 5. POST /api/v1/auth/forgot-password
# ==============================================================================
@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    response_model=SingleResponseEnvelope[dict[str, str]],
    summary="Yêu cầu đặt lại mật khẩu (Forgot Password)",
    description="Gửi mã liên kết khôi phục mật khẩu tới địa chỉ email đăng ký.",
)
async def forgot_password(
    payload: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleResponseEnvelope[dict[str, str]]:
    """Initiate password recovery flow."""
    reset_token = await auth_service.forgot_password(payload.email)
    return SingleResponseEnvelope(
        data={
            "message": f"Liên kết thiết lập lại mật khẩu đã được xử lý cho {payload.email}.",
            "reset_token": reset_token,
        },
        meta=ResponseMeta(),
    )


# ==============================================================================
# 6. POST /api/v1/auth/reset-password
# ==============================================================================
@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    response_model=SingleResponseEnvelope[AuthMessageResponse],
    summary="Xác nhận đặt lại mật khẩu mới (Reset Password)",
    description="Thiết lập mật khẩu mới bằng mã reset_token đã nhận được.",
)
async def reset_password(
    payload: PasswordResetConfirmRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleResponseEnvelope[AuthMessageResponse]:
    """Complete password reset using token."""
    await auth_service.reset_password(token=payload.token, new_password=payload.new_password)
    return SingleResponseEnvelope(
        data=AuthMessageResponse(
            message="Mật khẩu của bạn đã được cập nhật thành công. Vui lòng đăng nhập lại."
        ),
        meta=ResponseMeta(),
    )


# ==============================================================================
# 7. GET /api/v1/auth/me
# ==============================================================================
@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=SingleResponseEnvelope[UserProfileResponse],
    summary="Lấy thông tin tài khoản hiện tại (Get Profile)",
    description="Truy xuất hồ sơ nhà nghiên cứu đã được xác thực qua JWT token.",
)
async def get_my_profile(
    current_user: UserModel = Depends(get_current_user),
) -> SingleResponseEnvelope[UserProfileResponse]:
    """Retrieve currently authenticated user's profile."""
    return SingleResponseEnvelope(
        data=UserProfileResponse.model_validate(current_user),
        meta=ResponseMeta(),
    )


# ==============================================================================
# 8. PATCH /api/v1/auth/me
# ==============================================================================
@router.patch(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=SingleResponseEnvelope[UserProfileResponse],
    summary="Cập nhật thông tin tài khoản (Update Profile)",
    description=(
        "Chỉnh sửa họ tên, cơ quan, chức danh, ORCID hoặc ảnh đại diện của người dùng hiện tại."
    ),
)
async def update_my_profile(
    payload: UpdateProfileRequest,
    current_user: UserModel = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleResponseEnvelope[UserProfileResponse]:
    """Update profile attributes for currently authenticated user."""
    updated_user = await auth_service.update_profile(user=current_user, payload=payload)
    return SingleResponseEnvelope(
        data=UserProfileResponse.model_validate(updated_user),
        meta=ResponseMeta(),
    )


# ==============================================================================
# 9. POST /api/v1/auth/change-password
# ==============================================================================
@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    response_model=SingleResponseEnvelope[AuthMessageResponse],
    summary="Đổi mật khẩu tài khoản (Change Password)",
    description="Người dùng đã đăng nhập đổi sang mật khẩu mới sau khi xác thực mật khẩu hiện tại.",
)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: UserModel = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleResponseEnvelope[AuthMessageResponse]:
    """Change password for authenticated user."""
    await auth_service.change_password(
        user=current_user,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )
    return SingleResponseEnvelope(
        data=AuthMessageResponse(message="Đổi mật khẩu thành công."),
        meta=ResponseMeta(),
    )
