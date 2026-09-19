import { create } from "zustand";
import type { UserProfile, AuthResponse } from "@/types/auth";

export const AUTH_TOKEN_STORAGE_KEY = "verischolar_auth_token";
export const AUTH_USER_STORAGE_KEY = "verischolar_auth_user";

interface AuthState {
  user: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (authResponse: AuthResponse, rememberMe?: boolean) => void;
  logout: () => void;
  updateUser: (partialUser: Partial<UserProfile>) => void;
}

function getInitialSession(): { user: UserProfile | null; token: string | null } {
  if (typeof window === "undefined") {
    return { user: null, token: null };
  }
  try {
    const token = localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
    const userStr = localStorage.getItem(AUTH_USER_STORAGE_KEY);
    if (token && userStr) {
      const user = JSON.parse(userStr) as UserProfile;
      return { user, token };
    }
  } catch {
    // Ignore storage parse issues
  }
  return { user: null, token: null };
}

export const useAuthStore = create<AuthState>((set) => {
  const initial = getInitialSession();

  return {
    user: initial.user,
    token: initial.token,
    isAuthenticated: Boolean(initial.token && initial.user),
    isLoading: false,

    login: (authResponse: AuthResponse, rememberMe = true) => {
      const { user, tokens } = authResponse;
      if (rememberMe) {
        try {
          localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, tokens.access_token);
          localStorage.setItem(AUTH_USER_STORAGE_KEY, JSON.stringify(user));
        } catch {
          // Ignore storage write issues in private window
        }
      }
      set({
        user,
        token: tokens.access_token,
        isAuthenticated: true,
        isLoading: false,
      });
    },

    logout: () => {
      try {
        localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
        localStorage.removeItem(AUTH_USER_STORAGE_KEY);
      } catch {
        // Ignore storage removal errors
      }
      set({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      });
    },

    updateUser: (partialUser: Partial<UserProfile>) => {
      set((state) => {
        if (!state.user) return state;
        const updatedUser = { ...state.user, ...partialUser };
        try {
          localStorage.setItem(AUTH_USER_STORAGE_KEY, JSON.stringify(updatedUser));
        } catch {
          // Ignore
        }
        return { user: updatedUser };
      });
    },
  };
});
