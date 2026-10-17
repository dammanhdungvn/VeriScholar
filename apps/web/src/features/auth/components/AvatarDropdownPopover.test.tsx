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

  it("renders with 2 options: 'Hồ sơ cá nhân' and 'Cài đặt' when isOpen is true", () => {
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
    expect(screen.getByText("GS. Nguyễn Văn A")).toBeInTheDocument();
    expect(screen.getByText("scholar@hcmut.edu.vn")).toBeInTheDocument();

    const profileBtn = screen.getByTestId("popover-profile-btn");
    expect(profileBtn).toBeInTheDocument();
    expect(profileBtn).toHaveTextContent("Hồ sơ cá nhân");

    const settingsBtn = screen.getByTestId("popover-settings-btn");
    expect(settingsBtn).toBeInTheDocument();
    expect(settingsBtn).toHaveTextContent("Cài đặt");
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

  it("navigates to /settings and calls onClose when clicking 'Cài đặt'", () => {
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
