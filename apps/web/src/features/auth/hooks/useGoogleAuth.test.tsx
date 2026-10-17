import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useGoogleAuth } from "./useGoogleAuth";
import { authApi } from "../api/authApi";
import { useAuthStore } from "../stores/useAuthStore";

const mockNavigate = vi.fn();
vi.mock("react-router-dom", () => ({
  useNavigate: () => mockNavigate,
}));

describe("useGoogleAuth hook", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.unstubAllEnvs();
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    delete (window as unknown as { google?: unknown }).google;
  });

  it("identifies isConfigured based on VITE_GOOGLE_CLIENT_ID", () => {
    // 1. Explicitly isolate unconfigured state
    vi.stubEnv("VITE_GOOGLE_CLIENT_ID", "");
    const { result: unconfiguredResult } = renderHook(() => useGoogleAuth());
    expect(unconfiguredResult.current.isConfigured).toBe(false);
    expect(unconfiguredResult.current.clientId).toBe("");

    // 2. Explicitly isolate configured state
    vi.stubEnv("VITE_GOOGLE_CLIENT_ID", "test-client-id.apps.googleusercontent.com");
    const { result: configuredResult } = renderHook(() => useGoogleAuth());
    expect(configuredResult.current.isConfigured).toBe(true);
    expect(configuredResult.current.clientId).toBe("test-client-id.apps.googleusercontent.com");
  });

  it("handles empty token validation in loginWithGoogleToken", async () => {
    vi.stubEnv("VITE_GOOGLE_CLIENT_ID", "");
    const onError = vi.fn();
    const { result } = renderHook(() => useGoogleAuth({ onError }));

    await act(async () => {
      await result.current.loginWithGoogleToken("");
    });

    expect(result.current.error).toBe("Mã Google ID Token không hợp lệ.");
    expect(onError).toHaveBeenCalled();
  });

  it("successfully logs in with Google ID token and redirects to dashboard", async () => {
    vi.stubEnv("VITE_GOOGLE_CLIENT_ID", "test-client-id");
    const mockAuthResponse = {
      user: {
        id: "g-user-123",
        email: "scholar@oxford.ac.uk",
        full_name: "Prof. Oxford",
        role: "researcher" as const,
        is_verified: true,
        created_at: new Date().toISOString(),
      },
      tokens: {
        access_token: "google_jwt_access",
        refresh_token: "google_jwt_refresh",
        token_type: "bearer" as const,
        expires_in: 3600,
      },
      message: "Google login successful",
    };

    const googleLoginSpy = vi.spyOn(authApi, "googleLogin").mockResolvedValueOnce(mockAuthResponse);
    const onSuccess = vi.fn();

    const { result } = renderHook(() => useGoogleAuth({ onSuccess }));

    await act(async () => {
      await result.current.loginWithGoogleToken("valid_google_id_token_xyz");
    });

    expect(googleLoginSpy).toHaveBeenCalledWith("valid_google_id_token_xyz");
    expect(useAuthStore.getState().isAuthenticated).toBe(true);
    expect(useAuthStore.getState().user?.email).toBe("scholar@oxford.ac.uk");
    expect(onSuccess).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith("/dashboard");
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it("handles API rejection gracefully in loginWithGoogleToken", async () => {
    vi.stubEnv("VITE_GOOGLE_CLIENT_ID", "test-client-id");
    const googleLoginSpy = vi
      .spyOn(authApi, "googleLogin")
      .mockRejectedValueOnce(new Error("Email không thuộc nguồn học thuật hoặc uy tín hợp lệ."));
    const onError = vi.fn();

    const { result } = renderHook(() => useGoogleAuth({ onError }));

    await act(async () => {
      await result.current.loginWithGoogleToken("invalid_domain_token");
    });

    expect(googleLoginSpy).toHaveBeenCalledWith("invalid_domain_token");
    expect(result.current.error).toBe("Email không thuộc nguồn học thuật hoặc uy tín hợp lệ.");
    expect(onError).toHaveBeenCalled();
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
  });

  it("initializes GSI and handles prompt when GIS is present and configured", () => {
    const mockInitialize = vi.fn();
    const mockPrompt = vi.fn();

    (window as unknown as { google: unknown }).google = {
      accounts: {
        id: {
          initialize: mockInitialize,
          prompt: mockPrompt,
        },
      },
    };

    // 1. Unconfigured branch
    vi.stubEnv("VITE_GOOGLE_CLIENT_ID", "");
    const { result: unconfiguredResult } = renderHook(() => useGoogleAuth());
    expect(unconfiguredResult.current.initializeGsi()).toBe(false);
    unconfiguredResult.current.promptGoogle();
    expect(mockPrompt).not.toHaveBeenCalled();

    // 2. Configured branch
    vi.stubEnv("VITE_GOOGLE_CLIENT_ID", "test-client-id");
    const { result: configuredResult } = renderHook(() => useGoogleAuth());
    expect(configuredResult.current.initializeGsi()).toBe(true);
    expect(mockInitialize).toHaveBeenCalledWith(
      expect.objectContaining({
        client_id: "test-client-id",
      })
    );
    configuredResult.current.promptGoogle();
    expect(mockPrompt).toHaveBeenCalled();
  });
});
