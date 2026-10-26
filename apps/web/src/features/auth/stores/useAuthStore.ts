import { create } from "zustand";
import type { QueryClient } from "@tanstack/react-query";
import type { UserProfile, AuthResponse, ThemePreference } from "@/types/auth";
import { defaultQueryClient } from "@/lib/queryClient";
import { THEME_STORAGE_KEY } from "@/hooks/useTheme";

export const AUTH_TOKEN_STORAGE_KEY = "verischolar_auth_token";
export const AUTH_REFRESH_TOKEN_STORAGE_KEY = "verischolar_refresh_token";
export const AUTH_USER_STORAGE_KEY = "verischolar_auth_user";

export function applyThemePreference(theme: ThemePreference): void {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  const systemDark =
    typeof window !== "undefined" &&
    typeof window.matchMedia === "function" &&
    window.matchMedia("(prefers-color-scheme: dark)").matches;
  const shouldBeDark = theme === "dark" || (theme === "system" && systemDark);

  if (shouldBeDark) {
    root.classList.add("dark");
    root.setAttribute("data-theme", "dark");
    root.style.colorScheme = "dark";
  } else {
    root.classList.remove("dark");
    root.setAttribute("data-theme", "light");
    root.style.colorScheme = "light";
  }
}

interface AuthState {
  user: UserProfile | null;
  token: string | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  theme: ThemePreference;
  login: (authResponse: AuthResponse, rememberMe?: boolean) => void;
  logout: (queryClient?: QueryClient) => void;
  setAuth: (user: UserProfile, token: string, refreshToken?: string) => void;
  clearAuth: () => void;
  setTheme: (theme: ThemePreference) => void;
  updateUser: (partialUser: Partial<UserProfile>) => void;
}

function getInitialSession(): {
  user: UserProfile | null;
  token: string | null;
  refreshToken: string | null;
  theme: ThemePreference;
} {
  if (typeof window === "undefined") {
    return { user: null, token: null, refreshToken: null, theme: "system" };
  }
  try {
    const token = localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
    const refreshToken = localStorage.getItem(AUTH_REFRESH_TOKEN_STORAGE_KEY);
    const userStr = localStorage.getItem(AUTH_USER_STORAGE_KEY);
    const storedTheme = localStorage.getItem(THEME_STORAGE_KEY) as ThemePreference | null;
    if (token && userStr) {
      const user = JSON.parse(userStr) as UserProfile;
      const theme: ThemePreference =
        user.theme_preference ||
        (storedTheme === "light" || storedTheme === "dark" || storedTheme === "system"
          ? storedTheme
          : "system");
      return { user, token, refreshToken, theme };
    }
    if (storedTheme === "light" || storedTheme === "dark" || storedTheme === "system") {
      return { user: null, token: null, refreshToken: null, theme: storedTheme };
    }
  } catch {
    // Ignore storage parse issues
  }
  return { user: null, token: null, refreshToken: null, theme: "system" };
}

export const useAuthStore = create<AuthState>((set, get) => {
  const initial = getInitialSession();

  return {
    user: initial.user,
    token: initial.token,
    accessToken: initial.token,
    refreshToken: initial.refreshToken,
    isAuthenticated: Boolean(initial.token && initial.user),
    isLoading: false,
    theme: initial.theme,

    login: (authResponse: AuthResponse, rememberMe = true) => {
      const { user, tokens } = authResponse;
      const nextTheme: ThemePreference = user.theme_preference || get().theme || "system";
      if (rememberMe) {
        try {
          localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, tokens.access_token);
          if (tokens.refresh_token) {
            localStorage.setItem(AUTH_REFRESH_TOKEN_STORAGE_KEY, tokens.refresh_token);
          }
          localStorage.setItem(AUTH_USER_STORAGE_KEY, JSON.stringify(user));
        } catch {
          // Ignore storage write issues in private window
        }
      }
      if (user.theme_preference) {
        applyThemePreference(user.theme_preference);
      }
      set({
        user,
        token: tokens.access_token,
        accessToken: tokens.access_token,
        refreshToken: tokens.refresh_token ?? null,
        isAuthenticated: true,
        isLoading: false,
        theme: nextTheme,
      });
    },

    setAuth: (user: UserProfile, token: string, refreshToken?: string) => {
      const nextTheme: ThemePreference = user.theme_preference || get().theme || "system";
      try {
        localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, token);
        if (refreshToken) {
          localStorage.setItem(AUTH_REFRESH_TOKEN_STORAGE_KEY, refreshToken);
        }
        localStorage.setItem(AUTH_USER_STORAGE_KEY, JSON.stringify(user));
      } catch {
        // Ignore storage write issues
      }
      if (user.theme_preference) {
        applyThemePreference(user.theme_preference);
      }
      set({
        user,
        token,
        accessToken: token,
        refreshToken: refreshToken ?? get().refreshToken,
        isAuthenticated: true,
        isLoading: false,
        theme: nextTheme,
      });
    },

    logout: (customQueryClient?: QueryClient) => {
      try {
        localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
        localStorage.removeItem(AUTH_REFRESH_TOKEN_STORAGE_KEY);
        localStorage.removeItem(AUTH_USER_STORAGE_KEY);
      } catch {
        // Ignore storage removal errors
      }
      const client = customQueryClient ?? defaultQueryClient;
      try {
        client.clear();
      } catch {
        // Ignore in environments where query client is not available
      }
      set({
        user: null,
        token: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
      });
    },

    clearAuth: () => {
      get().logout();
    },

    setTheme: (theme: ThemePreference) => {
      try {
        localStorage.setItem(THEME_STORAGE_KEY, theme);
      } catch {
        // Ignore storage errors
      }
      applyThemePreference(theme);
      set((state) => {
        const updatedUser = state.user ? { ...state.user, theme_preference: theme } : null;
        if (updatedUser) {
          try {
            localStorage.setItem(AUTH_USER_STORAGE_KEY, JSON.stringify(updatedUser));
          } catch {
            // Ignore
          }
        }
        return { theme, user: updatedUser };
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
        if (partialUser.theme_preference) {
          applyThemePreference(partialUser.theme_preference);
        }
        return {
          user: updatedUser,
          theme: partialUser.theme_preference || state.theme,
        };
      });
    },
  };
});
