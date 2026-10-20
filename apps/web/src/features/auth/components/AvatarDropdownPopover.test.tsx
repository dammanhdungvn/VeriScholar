import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AvatarDropdownPopover } from "./AvatarDropdownPopover";
import { useAuthStore } from "../stores/useAuthStore";

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const mockToggleTheme = vi.fn();
vi.mock("@/hooks/useTheme", () => ({
  useTheme: () => ({
    theme: "light",
    isDark: false,
    toggleTheme: mockToggleTheme,
  }),
}));

describe("AvatarDropdownPopover component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthStore.getState().logout();
  });

  it("does not render when isOpen is false", () => {
    render(
      <MemoryRouter>
        <AvatarDropdownPopover isOpen={false} onClose={vi.fn()} />
      </MemoryRouter>
    );

    expect(screen.queryByTestId("avatar-dropdown-popover")).not.toBeInTheDocument();
  });

  it("renders with 3 sections: Header Card, Action List, and Footer List", () => {
    useAuthStore.getState().login({
      user: {
        id: "u-1",
        email: "scholar@hcmut.edu.vn",
        full_name: "GS. Nguyễn Văn A",
        role: "researcher",
        is_verified: true,
        created_at: new Date().toISOString(),
      },
      tokens: {
        access_token: "t-1",
        refresh_token: "r-1",
        token_type: "bearer",
        expires_in: 3600,
      },
    });

    render(
      <MemoryRouter>
        <AvatarDropdownPopover isOpen={true} onClose={vi.fn()} />
      </MemoryRouter>
    );

    expect(screen.getByTestId("avatar-dropdown-popover")).toBeInTheDocument();

    // 1. Header Card
    expect(screen.getByTestId("popover-header-card")).toBeInTheDocument();
    expect(screen.getByText("GS. Nguyễn Văn A")).toBeInTheDocument();
    expect(screen.getByText("scholar@hcmut.edu.vn")).toBeInTheDocument();

    // 2. Action List
    expect(screen.getByTestId("popover-upgrade-btn")).toHaveTextContent("Nâng cấp gói");
    expect(screen.getByTestId("popover-profile-btn")).toHaveTextContent("Hồ sơ cá nhân");
    expect(screen.getByTestId("popover-settings-btn")).toHaveTextContent("Cài đặt");
    expect(screen.getByTestId("popover-theme-btn")).toHaveTextContent("Chế độ giao diện: Sáng");

    // 3. Footer List
    expect(screen.getByTestId("popover-help-btn")).toHaveTextContent("Trợ giúp & Tài liệu");
    expect(screen.getByTestId("popover-logout-btn")).toHaveTextContent("Đăng xuất");
  });

  it("navigates to /profile and calls onClose when clicking Header Card", () => {
    const handleClose = vi.fn();

    render(
      <MemoryRouter>
        <AvatarDropdownPopover isOpen={true} onClose={handleClose} />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByTestId("popover-header-card"));

    expect(handleClose).toHaveBeenCalledTimes(1);
    expect(mockNavigate).toHaveBeenCalledWith("/profile");
  });

  it("navigates to /profile and calls onClose when clicking 'Hồ sơ cá nhân'", () => {
    const handleClose = vi.fn();

    render(
      <MemoryRouter>
        <AvatarDropdownPopover isOpen={true} onClose={handleClose} />
      </MemoryRouter>
    );

    const profileBtn = screen.getByTestId("popover-profile-btn");
    fireEvent.click(profileBtn);

    expect(handleClose).toHaveBeenCalledTimes(1);
    expect(mockNavigate).toHaveBeenCalledWith("/profile");
  });

  it("calls onOpenSettings and closes popover when clicking 'Cài đặt' if prop provided", () => {
    const handleClose = vi.fn();
    const handleOpenSettings = vi.fn();

    render(
      <MemoryRouter>
        <AvatarDropdownPopover
          isOpen={true}
          onClose={handleClose}
          onOpenSettings={handleOpenSettings}
        />
      </MemoryRouter>
    );

    const settingsBtn = screen.getByTestId("popover-settings-btn");
    fireEvent.click(settingsBtn);

    expect(handleClose).toHaveBeenCalledTimes(1);
    expect(handleOpenSettings).toHaveBeenCalledTimes(1);
    expect(mockNavigate).not.toHaveBeenCalledWith("/settings");
  });

  it("navigates to /settings and calls onClose when clicking 'Cài đặt' without onOpenSettings", () => {
    const handleClose = vi.fn();

    render(
      <MemoryRouter>
        <AvatarDropdownPopover isOpen={true} onClose={handleClose} />
      </MemoryRouter>
    );

    const settingsBtn = screen.getByTestId("popover-settings-btn");
    fireEvent.click(settingsBtn);

    expect(handleClose).toHaveBeenCalledTimes(1);
    expect(mockNavigate).toHaveBeenCalledWith("/settings");
  });

  it("toggles theme when clicking theme option", () => {
    render(
      <MemoryRouter>
        <AvatarDropdownPopover isOpen={true} onClose={vi.fn()} />
      </MemoryRouter>
    );

    const themeBtn = screen.getByTestId("popover-theme-btn");
    fireEvent.click(themeBtn);

    expect(mockToggleTheme).toHaveBeenCalledTimes(1);
  });

  it("calls logout, navigates to /login and closes popover on clicking 'Đăng xuất'", () => {
    const handleClose = vi.fn();
    const logoutSpy = vi.spyOn(useAuthStore.getState(), "logout");

    render(
      <MemoryRouter>
        <AvatarDropdownPopover isOpen={true} onClose={handleClose} />
      </MemoryRouter>
    );

    const logoutBtn = screen.getByTestId("popover-logout-btn");
    fireEvent.click(logoutBtn);

    expect(handleClose).toHaveBeenCalledTimes(1);
    expect(logoutSpy).toHaveBeenCalledTimes(1);
    expect(mockNavigate).toHaveBeenCalledWith("/login");
  });

  it("closes popover when pressing Escape key", () => {
    const handleClose = vi.fn();

    render(
      <MemoryRouter>
        <AvatarDropdownPopover isOpen={true} onClose={handleClose} />
      </MemoryRouter>
    );

    fireEvent.keyDown(window, { key: "Escape" });
    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});
