import { describe, it, expect, beforeEach, vi } from "vitest";
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
        role: "researcher",
        is_verified: true,
        created_at: "2026-10-26T00:00:00Z",
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

  it("closes context menu when clicking outside", () => {
    const dummySessions = [
      { id: "s-1", title: "Test Session 1", document_count: 1, active_tab: "chat", is_archived: false, created_at: "", updated_at: "" },
    ];
    render(
      <BrowserRouter>
        <DashboardTaskbar sessions={dummySessions as any} />
      </BrowserRouter>
    );

    const moreBtn = screen.getByTestId("session-more-btn-s-1");
    fireEvent.click(moreBtn);

    expect(screen.getByTestId("session-context-menu-s-1")).toBeInTheDocument();

    // Click outside
    fireEvent.mouseDown(document.body);
    expect(screen.queryByTestId("session-context-menu-s-1")).not.toBeInTheDocument();
  });

  it("shows unread coral indicator for unread sessions and toggles status", () => {
    localStorage.setItem("verischolar_unread_sessions_v1", JSON.stringify(["s-unread"]));
    const dummySessions = [
      { id: "s-unread", title: "Unread Paper Session", document_count: 1, active_tab: "chat", is_archived: false, created_at: "", updated_at: "" },
    ];
    render(
      <BrowserRouter>
        <DashboardTaskbar sessions={dummySessions as any} />
      </BrowserRouter>
    );

    // Coral unread dot should be visible
    expect(screen.getByTestId("session-unread-dot-s-unread")).toBeInTheDocument();

    // Open context menu to mark as read
    const moreBtn = screen.getByTestId("session-more-btn-s-unread");
    fireEvent.click(moreBtn);

    const toggleReadBtn = screen.getByText("Đánh dấu đã đọc");
    expect(toggleReadBtn).toBeInTheDocument();
    fireEvent.click(toggleReadBtn);

    // Indicator should be gone
    expect(screen.queryByTestId("session-unread-dot-s-unread")).not.toBeInTheDocument();
  });

  it("allows renaming a session via inline input and calls onRenameSession", async () => {
    const onRenameSession = vi.fn().mockResolvedValue(undefined);
    const dummySessions = [
      { id: "s-rename", title: "Original Title", document_count: 1, active_tab: "chat", is_archived: false, created_at: "", updated_at: "" },
    ];
    render(
      <BrowserRouter>
        <DashboardTaskbar sessions={dummySessions as any} onRenameSession={onRenameSession} />
      </BrowserRouter>
    );

    const moreBtn = screen.getByTestId("session-more-btn-s-rename");
    fireEvent.click(moreBtn);

    const renameBtn = screen.getByText("Đổi tên");
    fireEvent.click(renameBtn);

    const renameInput = screen.getByTestId("session-rename-input-s-rename") as HTMLInputElement;
    expect(renameInput).toBeInTheDocument();
    expect(renameInput.value).toBe("Original Title");

    fireEvent.change(renameInput, { target: { value: "Updated Academic Title" } });
    const saveBtn = screen.getByTestId("session-rename-save-s-rename");
    fireEvent.click(saveBtn);

    expect(onRenameSession).toHaveBeenCalledWith("s-rename", "Updated Academic Title");
  });

  it("prompts confirmation dialog and calls onDeleteSession when confirmed", async () => {
    const onDeleteSession = vi.fn().mockResolvedValue(undefined);
    const dummySessions = [
      { id: "s-del", title: "Session To Delete", document_count: 1, active_tab: "chat", is_archived: false, created_at: "", updated_at: "" },
    ];
    render(
      <BrowserRouter>
        <DashboardTaskbar sessions={dummySessions as any} onDeleteSession={onDeleteSession} />
      </BrowserRouter>
    );

    const moreBtn = screen.getByTestId("session-more-btn-s-del");
    fireEvent.click(moreBtn);

    const deleteBtn = screen.getByText("Xóa");
    fireEvent.click(deleteBtn);

    const deleteDialog = screen.getByTestId("delete-session-dialog");
    expect(deleteDialog).toBeInTheDocument();
    expect(deleteDialog).toHaveTextContent("Session To Delete");

    const confirmBtn = screen.getByTestId("confirm-delete-session-btn");
    fireEvent.click(confirmBtn);

    expect(onDeleteSession).toHaveBeenCalledWith("s-del");
  });

  it("renders 'Viết paper' and eliminates 'Khám phá & Phiên đọc' from taskbar", () => {
    render(
      <BrowserRouter>
        <DashboardTaskbar />
      </BrowserRouter>
    );

    expect(screen.getByText("Viết paper")).toBeInTheDocument();
    expect(screen.queryByText(/Khám phá & Phiên đọc/i)).toBeNull();
  });
});
