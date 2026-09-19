import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { LandingNavbar } from "./LandingNavbar";
import { useAuthStore } from "@/features/auth/stores/useAuthStore";
import { useLandingStore } from "../stores/useLandingStore";

describe("LandingNavbar component", () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.getState().logout();
    useLandingStore.getState().setUploadModalOpen(false);
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

  it("renders user profile chip and triggers upload modal when authenticated", () => {
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

    // Profile chip visible
    expect(screen.getByText("GS.TS. Nguyễn Văn Scholar")).toBeInTheDocument();

    // Logout button visible
    const logoutBtn = screen.getByLabelText("Đăng xuất");
    expect(logoutBtn).toBeInTheDocument();

    // In authenticated state, clicking 'Dùng thử ngay' opens QuickUploadModal
    const tryBtn = screen.getByTestId("nav-try-btn");
    fireEvent.click(tryBtn);
    expect(useLandingStore.getState().isUploadModalOpen).toBe(true);

    // Clicking logout returns to unauthenticated state
    fireEvent.click(logoutBtn);
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
  });
});
