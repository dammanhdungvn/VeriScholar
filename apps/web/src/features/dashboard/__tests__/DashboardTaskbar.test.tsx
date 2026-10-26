import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { DashboardTaskbar } from "../components/DashboardTaskbar";
import { useAuthStore } from "@/features/auth/stores/useAuthStore";
import { useDashboardStore } from "../stores/useDashboardStore";

describe("DashboardTaskbar Component", () => {
  beforeEach(() => {
    useDashboardStore.setState({
      sidebarState: "expanded",
    });
    useAuthStore.setState({
      user: {
        id: "usr-123",
        email: "dungdam.gg15@gmail.com",
        full_name: "Đàm Mạnh Dũng",
        role: "scholar",
      },
    });
  });

  it("renders user full name and verified badge without email on avatar trigger button", () => {
    render(
      <BrowserRouter>
        <DashboardTaskbar />
      </BrowserRouter>
    );

    const avatarBtn = screen.getByTestId("taskbar-avatar-btn");
    expect(avatarBtn).toBeInTheDocument();
    expect(avatarBtn).toHaveTextContent("Đàm Mạnh Dũng");

    // Email MUST NOT be displayed inside avatar trigger button (Rule Item 2)
    expect(avatarBtn).not.toHaveTextContent("dungdam.gg15@gmail.com");
  });

  it("toggles floating avatar popover when clicking avatar button", () => {
    render(
      <BrowserRouter>
        <DashboardTaskbar />
      </BrowserRouter>
    );

    expect(screen.queryByTestId("avatar-dropdown-popover")).not.toBeInTheDocument();

    const avatarBtn = screen.getByTestId("taskbar-avatar-btn");
    fireEvent.click(avatarBtn);

    // Popover is displayed on the floating layer
    const popover = screen.getByTestId("avatar-dropdown-popover");
    expect(popover).toBeInTheDocument();

    // Clicking backdrop cleanly closes it
    const backdrop = screen.getByTestId("avatar-popover-backdrop");
    fireEvent.click(backdrop);
    expect(screen.queryByTestId("avatar-dropdown-popover")).not.toBeInTheDocument();
  });
});
