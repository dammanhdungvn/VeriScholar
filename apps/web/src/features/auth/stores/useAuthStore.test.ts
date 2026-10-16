import { describe, it, expect, beforeEach, vi } from "vitest";

import {
  useAuthStore,
  AUTH_TOKEN_STORAGE_KEY,
  AUTH_USER_STORAGE_KEY,
} from "./useAuthStore";
import type { AuthResponse } from "@/types/auth";

describe("useAuthStore", () => {
  const mockAuthResponse: AuthResponse = {
    user: {
      id: "usr-test-123",
      email: "test@verischolar.ai",
      full_name: "Test Scholar",
      institution: "VeriScholar Lab",
      role: "researcher",
      is_verified: true,
      created_at: "2026-01-01T00:00:00Z",
    },
    tokens: {
      access_token: "jwt_access_token_abc123",
      refresh_token: "jwt_refresh_token_xyz789",
      token_type: "bearer",
      expires_in: 3600,
    },
    message: "Success",
  };

  beforeEach(() => {
    localStorage.clear();
    useAuthStore.getState().logout();
  });

  it("initializes with unauthenticated default state", () => {
    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
  });

  it("stores auth session and saves to localStorage when rememberMe is true", () => {
    useAuthStore.getState().login(mockAuthResponse, true);

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(true);
    expect(state.user?.email).toBe("test@verischolar.ai");
    expect(state.token).toBe("jwt_access_token_abc123");

    expect(localStorage.getItem(AUTH_TOKEN_STORAGE_KEY)).toBe("jwt_access_token_abc123");
    expect(localStorage.getItem(AUTH_USER_STORAGE_KEY)).toContain("Test Scholar");
  });

  it("stores auth session without localStorage when rememberMe is false", () => {
    useAuthStore.getState().login(mockAuthResponse, false);

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(true);
    expect(state.user?.email).toBe("test@verischolar.ai");

    expect(localStorage.getItem(AUTH_TOKEN_STORAGE_KEY)).toBeNull();
    expect(localStorage.getItem(AUTH_USER_STORAGE_KEY)).toBeNull();
  });

  it("clears session and removes tokens on logout", () => {
    useAuthStore.getState().login(mockAuthResponse, true);
    expect(useAuthStore.getState().isAuthenticated).toBe(true);

    useAuthStore.getState().logout();

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
    expect(localStorage.getItem(AUTH_TOKEN_STORAGE_KEY)).toBeNull();
    expect(localStorage.getItem(AUTH_USER_STORAGE_KEY)).toBeNull();
  });

  it("updates user profile partially and persists changes", () => {
    useAuthStore.getState().login(mockAuthResponse, true);
    useAuthStore.getState().updateUser({ institution: "Harvard Medical School" });

    const state = useAuthStore.getState();
    expect(state.user?.institution).toBe("Harvard Medical School");
    expect(state.user?.full_name).toBe("Test Scholar");
    expect(localStorage.getItem(AUTH_USER_STORAGE_KEY)).toContain("Harvard Medical School");
  });

  it("clears queryClient cache on logout to prevent session and document leaks", () => {
    const mockClear = vi.fn();
    const mockQueryClient = {
      clear: mockClear,
    } as unknown as import("@tanstack/react-query").QueryClient;

    useAuthStore.getState().login(mockAuthResponse, true);
    useAuthStore.getState().logout(mockQueryClient);

    expect(mockClear).toHaveBeenCalledTimes(1);
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
    expect(useAuthStore.getState().user).toBeNull();
  });
});

