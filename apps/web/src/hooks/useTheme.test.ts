import { describe, it, expect, beforeEach } from "vitest";
import { useTheme, THEME_STORAGE_KEY, applyThemeToDom } from "./useTheme";

describe("useTheme", () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.className = "";
    document.documentElement.removeAttribute("data-theme");
  });

  it("applies light theme to DOM correctly", () => {
    applyThemeToDom("light");
    expect(document.documentElement.classList.contains("dark")).toBe(false);
    expect(document.documentElement.getAttribute("data-theme")).toBe("light");
  });

  it("applies dark theme to DOM correctly", () => {
    applyThemeToDom("dark");
    expect(document.documentElement.classList.contains("dark")).toBe(true);
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
  });

  it("toggles theme from light to dark and persists to localStorage", () => {
    const { setTheme, toggleTheme } = useTheme.getState();
    setTheme("light");

    expect(useTheme.getState().theme).toBe("light");
    expect(useTheme.getState().isDark).toBe(false);
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe("light");

    toggleTheme();

    expect(useTheme.getState().theme).toBe("dark");
    expect(useTheme.getState().isDark).toBe(true);
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe("dark");
    expect(document.documentElement.classList.contains("dark")).toBe(true);

    toggleTheme();

    expect(useTheme.getState().theme).toBe("light");
    expect(useTheme.getState().isDark).toBe(false);
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe("light");
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });
});
