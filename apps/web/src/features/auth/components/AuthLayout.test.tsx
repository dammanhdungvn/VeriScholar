import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { AuthLayout } from "./AuthLayout";

describe("AuthLayout component", () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.classList.remove("dark");
  });

  it("renders centered layout with back link, brand logo, theme toggle and outlet content", () => {
    render(
      <MemoryRouter initialEntries={["/login"]}>
        <Routes>
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<div data-testid="mock-login-form">Mock Form Content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    );

    // Verify top bar elements
    expect(screen.getByTestId("auth-back-link")).toHaveAttribute("href", "/");
    expect(screen.getByText("Về trang chủ")).toBeInTheDocument();
    expect(screen.getByTestId("auth-brand-logo")).toHaveAttribute("href", "/");
    expect(screen.getByTestId("auth-theme-toggle")).toBeInTheDocument();

    // Verify outlet rendered inside centered card
    expect(screen.getByTestId("mock-login-form")).toBeInTheDocument();
    expect(screen.getByText("Mock Form Content")).toBeInTheDocument();
  });

  it("toggles light/dark theme when clicking theme switcher button", () => {
    render(
      <MemoryRouter initialEntries={["/login"]}>
        <Routes>
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<div>Form</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    );

    const toggleBtn = screen.getByTestId("auth-theme-toggle");
    expect(toggleBtn).toBeInTheDocument();

    // Click to switch theme
    fireEvent.click(toggleBtn);
    expect(document.documentElement.classList.contains("dark")).toBe(true);

    // Click again to switch back
    fireEvent.click(toggleBtn);
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });
});
