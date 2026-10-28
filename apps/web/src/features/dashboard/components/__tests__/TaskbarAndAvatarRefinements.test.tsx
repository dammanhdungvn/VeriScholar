import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { DashboardTaskbar } from "../DashboardTaskbar";
import { AvatarDropdownPopover } from "@/features/auth/components/AvatarDropdownPopover";
import { useDashboardStore } from "../../stores/useDashboardStore";

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
    toggleTheme: mockToggleTheme,
  }),
}));

describe("Taskbar and Avatar Refinements", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders new chat button as circular when collapsed", () => {
    useDashboardStore.setState({ sidebarState: "collapsed" });

    render(
      <MemoryRouter>
        <DashboardTaskbar />
      </MemoryRouter>
    );

    const newChatBtn = screen.getByTitle("Đoạn chat mới");
    expect(newChatBtn).toBeDefined();
    // In collapsed mode, it must have rounded-full and centered Plus icon
    expect(newChatBtn.className).toContain("rounded-full");
    expect(newChatBtn.className).toContain("w-10");
    expect(newChatBtn.className).toContain("h-10");
  });

  it("does not render glowing active background on navigation items", () => {
    useDashboardStore.setState({ sidebarState: "expanded" });

    render(
      <MemoryRouter>
        <DashboardTaskbar />
      </MemoryRouter>
    );

    const writingBtn = screen.getByTitle("Viết paper (Agentic Overleaf)");
    expect(writingBtn).toBeDefined();
    // Glowing border and background must be removed
    expect(writingBtn.className).not.toContain("bg-coral-500/15");
    expect(writingBtn.className).not.toContain("border-coral-500/25");
  });

  it("toggles recents list when clicking Recents header", () => {
    useDashboardStore.setState({ sidebarState: "expanded" });
    const dummySessions = [
      { id: "s1", title: "Paper Attention Transformer", is_archived: false, created_at: "", updated_at: "" },
      { id: "s2", title: "Selective Attention Analysis", is_archived: false, created_at: "", updated_at: "" },
    ];

    render(
      <MemoryRouter>
        <DashboardTaskbar sessions={dummySessions as any} />
      </MemoryRouter>
    );

    expect(screen.getByText("Paper Attention Transformer")).toBeDefined();
    const recentsToggle = screen.getByTestId("recents-collapse-toggle");
    expect(recentsToggle).toBeDefined();

    // Collapse
    fireEvent.click(recentsToggle);
    expect(screen.queryByText("Paper Attention Transformer")).toBeNull();

    // Expand
    fireEvent.click(recentsToggle);
    expect(screen.getByText("Paper Attention Transformer")).toBeDefined();
  });

  it("renders session context menu with Pin, Mark unread, Rename, Delete but no Add to project", () => {
    useDashboardStore.setState({ sidebarState: "expanded" });
    const dummySessions = [
      { id: "s1", title: "Session With Menu", is_archived: false, created_at: "", updated_at: "" },
    ];

    render(
      <MemoryRouter>
        <DashboardTaskbar sessions={dummySessions as any} />
      </MemoryRouter>
    );

    const moreBtn = screen.getByTestId("session-more-btn-s1");
    expect(moreBtn).toBeDefined();
    fireEvent.click(moreBtn);

    // Verify context menu options
    expect(screen.getByText("Ghim")).toBeDefined();
    expect(screen.getByText("Đánh dấu chưa đọc")).toBeDefined();
    expect(screen.getByText("Đổi tên")).toBeDefined();
    expect(screen.getByText("Xóa")).toBeDefined();

    // Verify "Add to project" is absent
    expect(screen.queryByText(/Add to project/i)).toBeNull();
    expect(screen.queryByText(/Thêm vào project/i)).toBeNull();
  });

  it("renders Dark/Light mode toggle in AvatarDropdownPopover replacing upgrade button", () => {
    const handleClose = vi.fn();

    render(
      <MemoryRouter>
        <AvatarDropdownPopover isOpen={true} onClose={handleClose} />
      </MemoryRouter>
    );

    // Upgrade button must NOT exist
    expect(screen.queryByTestId("popover-upgrade-btn")).toBeNull();
    expect(screen.queryByText("Nâng cấp gói")).toBeNull();

    // Theme toggle button MUST exist
    const themeBtn = screen.getByTestId("popover-theme-toggle-btn");
    expect(themeBtn).toBeDefined();
    expect(screen.getByText(/Chế độ tối|Chế độ sáng/i)).toBeDefined();

    fireEvent.click(themeBtn);
    expect(mockToggleTheme).toHaveBeenCalledTimes(1);
  });
});
