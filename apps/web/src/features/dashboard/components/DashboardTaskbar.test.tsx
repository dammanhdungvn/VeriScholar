import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { DashboardTaskbar } from "./DashboardTaskbar";
import { useDashboardStore } from "../stores/useDashboardStore";
import { RECENT_SESSIONS } from "../data/mockDashboardData";

describe("DashboardTaskbar component", () => {
  beforeEach(() => {
    useDashboardStore.getState().reset();
  });

  it("renders in collapsed mode by default", () => {
    render(
      <MemoryRouter>
        <DashboardTaskbar
          sessions={RECENT_SESSIONS}
          onSelectSession={vi.fn()}
          onNewSession={vi.fn()}
        />
      </MemoryRouter>
    );

    expect(screen.getByRole("complementary", { name: /thanh điều hướng chính/i })).toHaveClass("w-14");
    expect(screen.getByTitle("Mở rộng sidebar")).toBeInTheDocument();
  });

  it("expands when clicking toggle button and displays recent sessions", () => {
    const handleSelect = vi.fn();
    render(
      <MemoryRouter>
        <DashboardTaskbar
          sessions={RECENT_SESSIONS}
          onSelectSession={handleSelect}
          onNewSession={vi.fn()}
        />
      </MemoryRouter>
    );

    const toggleBtn = screen.getByTitle("Mở rộng sidebar");
    fireEvent.click(toggleBtn);

    expect(useDashboardStore.getState().sidebarState).toBe("expanded");
    expect(screen.getByText(/Attention Is All You Need/i)).toBeInTheDocument();

    // Clicking a session invokes callback
    const firstSessionBtn = screen.getByText(/Attention Is All You Need/i);
    fireEvent.click(firstSessionBtn);
    expect(handleSelect).toHaveBeenCalledWith(RECENT_SESSIONS[0].id);
  });

  it("triggers onNewSession when clicking plus button", () => {
    const handleNew = vi.fn();
    render(
      <MemoryRouter>
        <DashboardTaskbar
          sessions={RECENT_SESSIONS}
          onSelectSession={vi.fn()}
          onNewSession={handleNew}
        />
      </MemoryRouter>
    );

    const newBtn = screen.getByTitle("Đoạn chat mới");
    fireEvent.click(newBtn);
    expect(handleNew).toHaveBeenCalledTimes(1);
  });

  it("renders Thư viện and Dự án navigation items", () => {
    const handleLibrary = vi.fn();
    const handleProjects = vi.fn();
    render(
      <MemoryRouter>
        <DashboardTaskbar
          sessions={RECENT_SESSIONS}
          onSelectSession={vi.fn()}
          onNewSession={vi.fn()}
          onOpenLibrary={handleLibrary}
          onOpenProjects={handleProjects}
        />
      </MemoryRouter>
    );

    // Expand sidebar to view full labels
    const toggleBtn = screen.getByTitle("Mở rộng sidebar");
    fireEvent.click(toggleBtn);

    const libraryBtn = screen.getByTitle("Thư viện tài liệu nghiên cứu");
    expect(libraryBtn).toBeInTheDocument();
    fireEvent.click(libraryBtn);
    expect(handleLibrary).toHaveBeenCalledTimes(1);

    const projectsBtn = screen.getByTitle("Dự án nghiên cứu");
    expect(projectsBtn).toBeInTheDocument();
    fireEvent.click(projectsBtn);
    expect(handleProjects).toHaveBeenCalledTimes(1);
  });

  it("opens elegant dropdown popover with 'Hồ sơ cá nhân' and 'Cài đặt' when clicking Taskbar Avatar", () => {
    render(
      <MemoryRouter>
        <DashboardTaskbar
          sessions={RECENT_SESSIONS}
          onSelectSession={vi.fn()}
          onNewSession={vi.fn()}
        />
      </MemoryRouter>
    );

    const avatarBtn = screen.getByTestId("taskbar-avatar-btn");
    expect(avatarBtn).toBeInTheDocument();

    // Popover is initially closed
    expect(screen.queryByTestId("avatar-dropdown-popover")).not.toBeInTheDocument();

    // Click Taskbar Avatar opens popover with the 2 required options
    fireEvent.click(avatarBtn);
    expect(screen.getByTestId("avatar-dropdown-popover")).toBeInTheDocument();
    expect(screen.getByText("Hồ sơ cá nhân")).toBeInTheDocument();
    expect(screen.getByText("Cài đặt")).toBeInTheDocument();
  });
});
