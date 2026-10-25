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

  it("renders Kho Yêu thích and Soạn thảo LaTeX navigation items", () => {
    const handleLibrary = vi.fn();
    render(
      <MemoryRouter>
        <DashboardTaskbar
          sessions={RECENT_SESSIONS}
          onSelectSession={vi.fn()}
          onNewSession={vi.fn()}
          onOpenLibrary={handleLibrary}
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

    const writingBtn = screen.getByTitle(/Soạn thảo LaTeX/i);
    expect(writingBtn).toBeInTheDocument();
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

    // Click Taskbar Avatar opens popover with the required options
    fireEvent.click(avatarBtn);
    expect(screen.getByTestId("avatar-dropdown-popover")).toBeInTheDocument();
    expect(screen.getByText("Hồ sơ cá nhân")).toBeInTheDocument();
    expect(screen.getByText("Cài đặt")).toBeInTheDocument();
  });

  it("applies Cabinet Principle: renders single unified user button without exposed footer buttons", () => {
    render(
      <MemoryRouter>
        <DashboardTaskbar
          sessions={RECENT_SESSIONS}
          onSelectSession={vi.fn()}
          onNewSession={vi.fn()}
        />
      </MemoryRouter>
    );

    // No separate theme button in collapsed footer
    expect(screen.queryByTitle("Chế độ sáng")).not.toBeInTheDocument();
    expect(screen.queryByTitle("Chế độ tối")).not.toBeInTheDocument();
    expect(screen.queryByTitle("Cài đặt tài khoản")).not.toBeInTheDocument();
    expect(screen.queryByTitle("Đăng xuất")).not.toBeInTheDocument();

    // Expand sidebar
    const toggleBtn = screen.getByTitle("Mở rộng sidebar");
    fireEvent.click(toggleBtn);

    // Shows user name and 'Tài khoản cá nhân' label
    expect(screen.getByText("Tài khoản cá nhân")).toBeInTheDocument();

    // Click Taskbar Avatar to open popover, then click 'Cài đặt' to open AccountSettingsModal
    const avatarBtn = screen.getByTestId("taskbar-avatar-btn");
    fireEvent.click(avatarBtn);

    const settingsOption = screen.getByTestId("popover-settings-btn");
    fireEvent.click(settingsOption);

    // Modal is opened
    expect(screen.getByRole("dialog")).toBeInTheDocument();
  });

  it("renders only the 4 MVP global navigation items and excludes Matrix, Projects, and standalone Notes", () => {
    render(
      <MemoryRouter>
        <DashboardTaskbar
          sessions={RECENT_SESSIONS}
          onSelectSession={vi.fn()}
          onNewSession={vi.fn()}
        />
      </MemoryRouter>
    );
    const toggleBtn = screen.getByTitle("Mở rộng sidebar");
    fireEvent.click(toggleBtn);

    expect(screen.queryByTitle(/Ma trận đối sánh/i)).not.toBeInTheDocument();
    expect(screen.queryByTitle(/Dự án nghiên cứu/i)).not.toBeInTheDocument();
    expect(screen.queryByTitle(/Ghi chú nghiên cứu/i)).not.toBeInTheDocument();
  });
});
