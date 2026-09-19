import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { LandingNavbar } from "./LandingNavbar";
import { useAuthStore } from "@/features/auth/stores/useAuthStore";

describe("LandingNavbar component", () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.getState().logout();
  });

  it("renders streamlined unauthenticated action cluster: 'Dùng thử ngay' links to /login", () => {
    render(
      <MemoryRouter>
        <LandingNavbar />
      </MemoryRouter>
    );

    // Verifies the high-converting single primary CTA
    const tryBtn = screen.getByTestId("nav-try-btn");
    expect(tryBtn).toBeInTheDocument();
    expect(tryBtn).toHaveTextContent("Dùng thử ngay");
    expect(tryBtn.closest("a")).toHaveAttribute("href", "/login");

    // Confirms redundant separate 'Đăng nhập' is removed for big-tech streamlined simplicity
    expect(screen.queryByTestId("nav-login-link")).not.toBeInTheDocument();
  });

  it("renders streamlined 'Dashboard' link to /dashboard when authenticated", () => {
    useAuthStore.getState().login({
      user: {
        id: "demo-user-1",
        email: "nguyen.scholar@hcmut.edu.vn",
        full_name: "GS.TS. Nguyễn Văn Scholar",
        role: "researcher",
        is_verified: true,
        created_at: new Date().toISOString(),
      },
      tokens: {
        access_token: "token-xyz",
        refresh_token: "refresh-xyz",
        token_type: "bearer",
        expires_in: 3600,
      },
    });

    render(
      <MemoryRouter>
        <LandingNavbar />
      </MemoryRouter>
    );

    // Profile chip and logout button are removed for sleek minimalist header
    expect(screen.queryByText("GS.TS. Nguyễn Văn Scholar")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Đăng xuất")).not.toBeInTheDocument();

    // Primary CTA switches to 'Dashboard' navigating to /dashboard
    const dashboardBtn = screen.getByTestId("nav-try-btn");
    expect(dashboardBtn).toBeInTheDocument();
    expect(dashboardBtn).toHaveTextContent("Dashboard");
    expect(dashboardBtn.closest("a")).toHaveAttribute("href", "/dashboard");
  });
});
