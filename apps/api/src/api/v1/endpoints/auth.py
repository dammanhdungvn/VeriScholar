import os

import structlog
from api.core.config import settings
from api.db.models.user import UserModel
from api.deps import get_auth_service, get_current_user
from api.schemas.auth import (
    AuthMessageResponse,
    AuthResponse,
    AuthTokensResponse,
    ChangePasswordRequest,
    GitHubAuthRequest,
    GoogleAuthRequest,
    LoginRequest,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    RegisterRequest,
    ResendVerificationRequest,
    TokenRefreshRequest,
    UpdateProfileRequest,
    UserProfileResponse,
    VerifyEmailRequest,
)
from api.schemas.envelope import ResponseMeta, SingleResponseEnvelope
from api.services.auth_service import AuthService
from fastapi import APIRouter, Depends, HTTPException, status

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
        "Tạo tài khoản nhà nghiên cứu mới với mật khẩu bảo mật PBKDF2-HMAC-SHA256, "
        "chặn disposable emails, ưu tiên domain học thuật, sinh bộ JWT tokens và mã OTP xác thực."
    ),
)
async def register(
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleResponseEnvelope[AuthResponse]:
    """Register a new user account and return profile with credentials."""
    res = await auth_service.register(payload)
    if len(res) == 3:
        user, tokens, otp_code = res
    else:
        user, tokens = res  # type: ignore[misc]
        otp_code = None

    expose_debug_otp = (
        settings.DEBUG
        or settings.ENVIRONMENT in ("development", "test")
        or not (os.getenv("SMTP_HOST", "").strip() and os.getenv("SMTP_USER", "").strip())
    )

    return SingleResponseEnvelope(
        data=AuthResponse(
            user=UserProfileResponse.model_validate(user),
            tokens=tokens,
            message=(
                "Đăng ký tài khoản thành viên nghiên cứu thành công! "
                "Chào mừng bạn đến với VeriScholar."
            ),
            verification_code_debug=otp_code if expose_debug_otp else None,
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
    description=(
        "Xác thực thông tin đăng nhập và cấp cặp access_token/refresh_token "
        "HMAC-SHA256 (30 ngày khi remember_me=True)."
    ),
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
# 3. POST /api/v1/auth/google
# ==============================================================================
@router.post(
    "/google",
    status_code=status.HTTP_200_OK,
    response_model=SingleResponseEnvelope[AuthResponse],
    summary="Xác thực Google OAuth 2.0 (Google Sign-In)",
    description=(
        "Xác thực Google ID Token với Google Identity Services. "
        "Tự động cấp tài khoản học thuật hoặc đồng bộ tài khoản hiện có, cấp cặp JWT tokens."
    ),
)
async def google_auth(
    payload: GoogleAuthRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleResponseEnvelope[AuthResponse]:
    """Authenticate scholar using Google OAuth 2.0 id_token."""
    user, tokens = await auth_service.authenticate_google(payload.id_token)
    return SingleResponseEnvelope(
        data=AuthResponse(
            user=UserProfileResponse.model_validate(user),
            tokens=tokens,
            message="Xác thực Google thành công! Chào mừng bạn đến với VeriScholar.",
        ),
        meta=ResponseMeta(),
    )


# ==============================================================================
# 4. POST /api/v1/auth/github
# ==============================================================================
@router.post(
    "/github",
    status_code=status.HTTP_200_OK,
    response_model=SingleResponseEnvelope[AuthResponse],
    summary="Xác thực GitHub OAuth (GitHub Sign-In)",
    description=(
        "Xác thực tài khoản GitHub bằng OAuth authorization code hoặc access token. "
        "Tự động cấp tài khoản học thuật hoặc liên kết tài khoản hiện có, cấp cặp JWT tokens."
    ),
)
async def github_auth(
    payload: GitHubAuthRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleResponseEnvelope[AuthResponse]:
    """Authenticate scholar using GitHub OAuth code or access token."""
    user, tokens = await auth_service.authenticate_github(
        code=payload.code,
        redirect_uri=payload.redirect_uri,
        access_token=payload.access_token,
    )
    return SingleResponseEnvelope(
        data=AuthResponse(
            user=UserProfileResponse.model_validate(user),
            tokens=tokens,
            message="Xác thực GitHub thành công! Chào mừng bạn đến với VeriScholar.",
        ),
        meta=ResponseMeta(),
    )


# ==============================================================================
# 5. POST /api/v1/auth/logout
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
    description="Gửi mã liên kết khôi phục mật khẩu và OTP 6 số tới địa chỉ email đăng ký.",
)
async def forgot_password(
    payload: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleResponseEnvelope[dict[str, str]]:
    """Initiate password recovery flow."""
    res = await auth_service.forgot_password(payload.email)
    if isinstance(res, tuple):
        reset_token, otp_code = res
    else:
        reset_token = res
        otp_code = None

    data: dict[str, str] = {
        "message": f"Liên kết thiết lập lại mật khẩu đã được xử lý cho {payload.email}.",
        "reset_token": reset_token,
    }
    if otp_code:
        data["otp_code"] = otp_code

    return SingleResponseEnvelope(
        data=data,
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
    description="Thiết lập mật khẩu mới bằng mã reset_token hoặc mã OTP 6 số đã nhận được.",
)
async def reset_password(
    payload: PasswordResetConfirmRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleResponseEnvelope[AuthMessageResponse]:
    """Complete password reset using token or OTP code."""
    await auth_service.reset_password(
        token=payload.token,
        new_password=payload.new_password,
        email=payload.email,
    )
    return SingleResponseEnvelope(
        data=AuthMessageResponse(
            message="Mật khẩu của bạn đã được cập nhật thành công. Vui lòng đăng nhập lại."
        ),
        meta=ResponseMeta(),
    )


# ==============================================================================
# 7. POST /api/v1/auth/verify-email
# ==============================================================================
@router.post(
    "/verify-email",
    status_code=status.HTTP_200_OK,
    response_model=SingleResponseEnvelope[AuthMessageResponse],
    summary="Xác thực email tài khoản nghiên cứu (Verify Email)",
    description="Xác thực email bằng mã OTP 6 số hoặc JWT token từ liên kết email.",
)
async def verify_email(
    payload: VerifyEmailRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleResponseEnvelope[AuthMessageResponse]:
    """Verify user's scholarly email with 6-digit OTP code or JWT token."""
    token_or_code = payload.code or payload.otp or payload.token
    if not token_or_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "MISSING_VERIFICATION_CREDENTIAL",
                "message": "Vui lòng cung cấp mã OTP 6 số hoặc liên kết token xác thực.",
            },
        )
    user = await auth_service.verify_email(email=payload.email, token_or_code=token_or_code)
    return SingleResponseEnvelope(
        data=AuthMessageResponse(
            message=(
                f"Xác thực email thành công cho tài khoản {user.email}. "
                "Chào mừng bạn đến với VeriScholar!"
            )
        ),
        meta=ResponseMeta(),
    )


# ==============================================================================
# 8. POST /api/v1/auth/resend-verification
# ==============================================================================
@router.post(
    "/resend-verification",
    status_code=status.HTTP_200_OK,
    response_model=SingleResponseEnvelope[AuthMessageResponse],
    summary="Gửi lại mã xác thực email (Resend Verification)",
    description="Gửi lại mã OTP 6 số và liên kết xác thực mới tới địa chỉ email đăng ký.",
)
async def resend_verification(
    payload: ResendVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleResponseEnvelope[AuthMessageResponse]:
    """Resend email verification OTP and token."""
    await auth_service.resend_verification(email=payload.email)
    return SingleResponseEnvelope(
        data=AuthMessageResponse(
            message=(
                f"Mã xác thực mới đã được gửi tới email {payload.email}. Vui lòng kiểm tra hộp thư."
            )
        ),
        meta=ResponseMeta(),
    )


# ==============================================================================
# 9. GET /api/v1/auth/me
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
# 10. PATCH /api/v1/auth/me
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
@router.put(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=SingleResponseEnvelope[UserProfileResponse],
    include_in_schema=False,
)
@router.patch(
    "/profile",
    status_code=status.HTTP_200_OK,
    response_model=SingleResponseEnvelope[UserProfileResponse],
    include_in_schema=False,
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
# 11. POST /api/v1/auth/change-password
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
