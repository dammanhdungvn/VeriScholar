import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { DashboardPage } from "./DashboardPage";
import { useAuthStore } from "@/features/auth/stores/useAuthStore";

describe("DashboardPage component", () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.getState().login(
      {
        user: {
          id: "usr-test-1",
          email: "scholar@verischolar.ai",
          full_name: "GS.TS. Nguyen Van A",
          role: "faculty",
          is_verified: true,
          created_at: "2026-01-01",
        },
        tokens: {
          access_token: "mock-token",
          refresh_token: "mock-refresh",
          token_type: "bearer",
          expires_in: 3600,
        },
      },
      false
    );
  });

  it("renders Dashboard heading and user details properly", () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );

    expect(screen.getByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
    expect(screen.getByText(/GS.TS. Nguyen Van A/i)).toBeInTheDocument();
    expect(screen.getByText("scholar@verischolar.ai")).toBeInTheDocument();
    expect(screen.getByTestId("dashboard-logout-btn")).toBeInTheDocument();
  });

  it("logs out user when clicking logout button", () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );

    const logoutBtn = screen.getByTestId("dashboard-logout-btn");
    fireEvent.click(logoutBtn);

    expect(useAuthStore.getState().isAuthenticated).toBe(false);
  });
});
