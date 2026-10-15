import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useLogin } from "./useLogin";
import { useRegister } from "./useRegister";
import { authApi } from "../api/authApi";
import { useAuthStore } from "../stores/useAuthStore";
import type { AuthResponse } from "@/types/auth";

describe("useLogin and useRegister hooks", () => {
  const mockAuthResponse: AuthResponse = {
    user: {
      id: "usr-hooks-123",
      email: "hooktest@verischolar.ai",
      full_name: "Hook Tester",
      role: "researcher",
      is_verified: true,
      created_at: "2026-01-01T00:00:00Z",
    },
    tokens: {
      access_token: "hook_access_token",
      refresh_token: "hook_refresh_token",
      token_type: "bearer",
      expires_in: 3600,
    },
    message: "Success",
  };

  const createWrapper = () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });

    return ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
  };

  beforeEach(() => {
    localStorage.clear();
    useAuthStore.getState().logout();
    vi.clearAllMocks();
  });

  it("useLogin calls authApi.login and logs user into useAuthStore", async () => {
    const loginSpy = vi.spyOn(authApi, "login").mockResolvedValueOnce(mockAuthResponse);

    const { result } = renderHook(() => useLogin(), { wrapper: createWrapper() });

    result.current.mutate({
      email: "hooktest@verischolar.ai",
      password: "Password123!",
      remember_me: true,
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(loginSpy).toHaveBeenCalledWith({
      email: "hooktest@verischolar.ai",
      password: "Password123!",
      remember_me: true,
    });
    expect(useAuthStore.getState().isAuthenticated).toBe(true);
    expect(useAuthStore.getState().user?.email).toBe("hooktest@verischolar.ai");
  });

  it("useRegister calls authApi.register and logs user into useAuthStore", async () => {
    const registerSpy = vi.spyOn(authApi, "register").mockResolvedValueOnce(mockAuthResponse);

    const { result } = renderHook(() => useRegister(), { wrapper: createWrapper() });

    result.current.mutate({
      full_name: "Hook Tester",
      email: "hooktest@verischolar.ai",
      password: "Password123!",
      accept_terms: true,
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(registerSpy).toHaveBeenCalledWith({
      full_name: "Hook Tester",
      email: "hooktest@verischolar.ai",
      password: "Password123!",
      accept_terms: true,
    });
    expect(useAuthStore.getState().isAuthenticated).toBe(true);
    expect(useAuthStore.getState().user?.email).toBe("hooktest@verischolar.ai");
  });
});
