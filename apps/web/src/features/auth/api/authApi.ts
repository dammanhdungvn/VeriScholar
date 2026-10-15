import { apiClient } from "@/lib/api-client";
import type {
  AuthResponse,
  LoginCredentials,
  RegisterPayload,
  UserProfile,
  ChangePasswordPayload,
  UpdateProfilePayload,
  PasswordResetRequest,
  PasswordResetConfirm,
  AuthMessageResponse,
} from "@/types/auth";

export const authApi = {
  /**
   * POST /api/v1/auth/login
   * Xác thực người dùng bằng email và mật khẩu, trả về UserProfile và AuthTokens
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    return apiClient<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    });
  },

  /**
   * POST /api/v1/auth/register
   * Đăng ký tài khoản học thuật mới
   */
  async register(payload: RegisterPayload): Promise<AuthResponse> {
    return apiClient<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * POST /api/v1/auth/logout
   * Thu hồi phiên đăng nhập hiện tại trên máy chủ
   */
  async logout(): Promise<AuthMessageResponse | void> {
    return apiClient<AuthMessageResponse | void>("/auth/logout", {
      method: "POST",
    });
  },

  /**
   * GET /api/v1/auth/me
   * Lấy thông tin hồ sơ người dùng hiện tại
   */
  async getMe(): Promise<UserProfile> {
    return apiClient<UserProfile>("/auth/me", {
      method: "GET",
    });
  },

  /**
   * PATCH /api/v1/auth/me
   * Cập nhật thông tin hồ sơ học giả (full_name, institution, academic_rank, orcid_id)
   */
  async updateProfile(payload: UpdateProfilePayload): Promise<UserProfile> {
    return apiClient<UserProfile>("/auth/me", {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  /**
   * POST /api/v1/auth/change-password
   * Thay đổi mật khẩu người dùng đang đăng nhập
   */
  async changePassword(payload: ChangePasswordPayload): Promise<AuthMessageResponse> {
    return apiClient<AuthMessageResponse>("/auth/change-password", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * POST /api/v1/auth/forgot-password
   * Yêu cầu gửi email khôi phục mật khẩu
   */
  async forgotPassword(payload: PasswordResetRequest): Promise<AuthMessageResponse> {
    return apiClient<AuthMessageResponse>("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * POST /api/v1/auth/reset-password
   * Xác nhận đặt lại mật khẩu bằng token
   */
  async resetPassword(payload: PasswordResetConfirm): Promise<AuthMessageResponse> {
    return apiClient<AuthMessageResponse>("/auth/reset-password", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};
