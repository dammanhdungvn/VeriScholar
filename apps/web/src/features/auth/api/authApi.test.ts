import { describe, it, expect, vi, beforeEach } from "vitest";
import { authApi } from "./authApi";
import * as apiClientModule from "@/lib/api-client";

describe("authApi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("calls POST /auth/login with credentials", async () => {
    const mockApiClient = vi.spyOn(apiClientModule, "apiClient").mockResolvedValueOnce({
      user: { id: "1", email: "test@verischolar.ai" },
      tokens: { access_token: "token123" },
    });

    const res = await authApi.login({
      email: "test@verischolar.ai",
      password: "Password123!",
    });

    expect(mockApiClient).toHaveBeenCalledWith("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email: "test@verischolar.ai",
        password: "Password123!",
      }),
    });
    expect(res.user.email).toBe("test@verischolar.ai");
  });

  it("calls POST /auth/register with registration payload", async () => {
    const mockApiClient = vi.spyOn(apiClientModule, "apiClient").mockResolvedValueOnce({
      user: { id: "2", email: "new@verischolar.ai" },
      tokens: { access_token: "token456" },
    });

    const payload = {
      full_name: "New Scholar",
      email: "new@verischolar.ai",
      password: "Password123!",
      accept_terms: true,
    };

    const res = await authApi.register(payload);

    expect(mockApiClient).toHaveBeenCalledWith("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    expect(res.user.email).toBe("new@verischolar.ai");
  });

  it("calls POST /auth/logout", async () => {
    const mockApiClient = vi.spyOn(apiClientModule, "apiClient").mockResolvedValueOnce({
      message: "Logged out successfully",
    });

    const res = await authApi.logout();

    expect(mockApiClient).toHaveBeenCalledWith("/auth/logout", {
      method: "POST",
    });
    expect(res).toEqual({ message: "Logged out successfully" });
  });

  it("calls GET /auth/me to retrieve current user profile", async () => {
    const mockApiClient = vi.spyOn(apiClientModule, "apiClient").mockResolvedValueOnce({
      id: "usr-1",
      email: "scholar@verischolar.ai",
      full_name: "Prof. Test",
    });

    const res = await authApi.getMe();

    expect(mockApiClient).toHaveBeenCalledWith("/auth/me", {
      method: "GET",
    });
    expect(res.full_name).toBe("Prof. Test");
  });

  it("calls PATCH /auth/me to update profile", async () => {
    const mockApiClient = vi.spyOn(apiClientModule, "apiClient").mockResolvedValueOnce({
      id: "usr-1",
      full_name: "Prof. Updated",
    });

    const res = await authApi.updateProfile({ full_name: "Prof. Updated" });

    expect(mockApiClient).toHaveBeenCalledWith("/auth/me", {
      method: "PATCH",
      body: JSON.stringify({ full_name: "Prof. Updated" }),
    });
    expect(res.full_name).toBe("Prof. Updated");
  });

  it("calls POST /auth/change-password", async () => {
    const mockApiClient = vi.spyOn(apiClientModule, "apiClient").mockResolvedValueOnce({
      message: "Password changed",
    });

    const res = await authApi.changePassword({
      current_password: "old",
      new_password: "new",
    });

    expect(mockApiClient).toHaveBeenCalledWith("/auth/change-password", {
      method: "POST",
      body: JSON.stringify({ current_password: "old", new_password: "new" }),
    });
    expect(res.message).toBe("Password changed");
  });

  it("calls POST /auth/forgot-password", async () => {
    const mockApiClient = vi.spyOn(apiClientModule, "apiClient").mockResolvedValueOnce({
      message: "Reset email sent",
    });

    const res = await authApi.forgotPassword({ email: "test@verischolar.ai" });

    expect(mockApiClient).toHaveBeenCalledWith("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email: "test@verischolar.ai" }),
    });
    expect(res.message).toBe("Reset email sent");
  });

  it("calls POST /auth/reset-password", async () => {
    const mockApiClient = vi.spyOn(apiClientModule, "apiClient").mockResolvedValueOnce({
      message: "Password reset completed",
    });

    const res = await authApi.resetPassword({
      token: "tok123",
      new_password: "brandNewPassword123!",
    });

    expect(mockApiClient).toHaveBeenCalledWith("/auth/reset-password", {
      method: "POST",
      body: JSON.stringify({
        token: "tok123",
        new_password: "brandNewPassword123!",
      }),
    });
    expect(res.message).toBe("Password reset completed");
  });

  it("calls POST /auth/google with id_token payload", async () => {
    const mockApiClient = vi.spyOn(apiClientModule, "apiClient").mockResolvedValueOnce({
      user: { id: "g-1", email: "scholar@stanford.edu" },
      tokens: { access_token: "google_access_token_xyz" },
      message: "Xác thực Google thành công!",
    });

    const res = await authApi.googleLogin("mock_google_id_token_123");

    expect(mockApiClient).toHaveBeenCalledWith("/auth/google", {
      method: "POST",
      body: JSON.stringify({
        id_token: "mock_google_id_token_123",
      }),
    });
    expect(res.user.email).toBe("scholar@stanford.edu");
    expect(res.tokens.access_token).toBe("google_access_token_xyz");
  });
});
