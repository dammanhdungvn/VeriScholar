import { create } from "zustand";

export type Theme = "light" | "dark";

export const THEME_STORAGE_KEY = "verischolar_theme";

export function getInitialTheme(): Theme {
  if (typeof window === "undefined") return "light";
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored === "light" || stored === "dark") {
      return stored;
    }
    if (window.matchMedia?.("(prefers-color-scheme: dark)").matches) {
      return "dark";
    }
  } catch {
    // Ignore storage access issues in sandboxed environments
  }
  return "light";
}

export function applyThemeToDom(theme: Theme): void {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  if (theme === "dark") {
    root.classList.add("dark");
    root.setAttribute("data-theme", "dark");
    root.style.colorScheme = "dark";
  } else {
    root.classList.remove("dark");
    root.setAttribute("data-theme", "light");
    root.style.colorScheme = "light";
  }
}

interface ThemeState {
  theme: Theme;
  isDark: boolean;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

export const useTheme = create<ThemeState>((set) => {
  const initialTheme = getInitialTheme();
  applyThemeToDom(initialTheme);

  return {
    theme: initialTheme,
    isDark: initialTheme === "dark",
    setTheme: (theme: Theme) => {
      try {
        localStorage.setItem(THEME_STORAGE_KEY, theme);
      } catch {
        // Ignore storage access issues
      }
      applyThemeToDom(theme);
      set({ theme, isDark: theme === "dark" });
    },
    toggleTheme: () => {
      set((state) => {
        const nextTheme: Theme = state.theme === "light" ? "dark" : "light";
        try {
          localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
        } catch {
          // Ignore storage access issues
        }
        applyThemeToDom(nextTheme);
        return { theme: nextTheme, isDark: nextTheme === "dark" };
      });
    },
  };
});
