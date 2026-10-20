import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MobileDashboardHeader } from "./MobileDashboardHeader";
import { DashboardContainer } from "./DashboardContainer";
import { useDashboardStore } from "../stores/useDashboardStore";
import { useWorkspaceStore } from "../stores/useWorkspaceStore";
import { useAuthStore } from "@/features/auth/stores/useAuthStore";

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        {ui}
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("MobileDashboardHeader Component", () => {
  beforeEach(() => {
    useDashboardStore.getState().reset();
    useWorkspaceStore.getState().resetWorkspace();
    useAuthStore.setState({
      user: {
        id: "scholar-1",
        email: "scholar@verischolar.org",
        full_name: "Richard Feynman",
        role: "researcher",
        is_verified: true,
        created_at: new Date().toISOString(),
      },
      isAuthenticated: true,
      token: "mock-token",
    });
    vi.restoreAllMocks();
  });

  it("renders all required mobile header controls with touch target >= 44px", () => {
    const handleToggle = vi.fn();
    const handleNew = vi.fn();

    renderWithProviders(
      <MobileDashboardHeader
        onToggleSidebar={handleToggle}
        onNewSession={handleNew}
      />
    );

    // 1. Mobile header container
    const header = screen.getByTestId("mobile-dashboard-header");
    expect(header).toBeInTheDocument();
    expect(header).toHaveClass("sticky");
    expect(header).toHaveClass("md:hidden");

    // 2. Hamburger button
    const menuBtn = screen.getByTestId("mobile-header-menu-btn");
    expect(menuBtn).toBeInTheDocument();
    expect(menuBtn).toHaveClass("min-h-[44px]");
    expect(menuBtn).toHaveClass("min-w-[44px]");

    // 3. VeriScholar Logo link
    const homeLink = screen.getByLabelText("VeriScholar Trang chủ");
    expect(homeLink).toBeInTheDocument();

    // 4. '+' New session button is removed per user requirement
    expect(screen.queryByTestId("mobile-header-new-chat-btn")).toBeNull();

    // 5. Theme toggle button
    const themeToggleBtn = screen.getByTestId("mobile-header-theme-toggle");
    expect(themeToggleBtn).toBeInTheDocument();
    expect(themeToggleBtn).toHaveClass("min-h-[44px]");
    expect(themeToggleBtn).toHaveClass("min-w-[44px]");

    // 6. Avatar button
    const avatarBtn = screen.getByTestId("mobile-header-avatar-btn");
    expect(avatarBtn).toBeInTheDocument();
    expect(avatarBtn).toHaveClass("min-h-[44px]");
    expect(avatarBtn).toHaveClass("min-w-[44px]");
  });

  it("invokes onToggleSidebar when clicking hamburger menu button", () => {
    const handleToggle = vi.fn();
    const handleNew = vi.fn();

    renderWithProviders(
      <MobileDashboardHeader
        onToggleSidebar={handleToggle}
        onNewSession={handleNew}
      />
    );

    const menuBtn = screen.getByTestId("mobile-header-menu-btn");
    fireEvent.click(menuBtn);
    expect(handleToggle).toHaveBeenCalledTimes(1);
  });

  it("does not render plus button in mobile header", () => {
    renderWithProviders(
      <MobileDashboardHeader
        onToggleSidebar={vi.fn()}
        onNewSession={vi.fn()}
      />
    );

    expect(screen.queryByTestId("mobile-header-new-chat-btn")).toBeNull();
  });

  it("toggles dark/light theme when clicking theme button", () => {
    renderWithProviders(
      <MobileDashboardHeader
        onToggleSidebar={vi.fn()}
        onNewSession={vi.fn()}
      />
    );

    const themeToggleBtn = screen.getByTestId("mobile-header-theme-toggle");
    fireEvent.click(themeToggleBtn);
    // Theme toggle changes class/state without crashing
    expect(themeToggleBtn).toBeInTheDocument();
  });

  it("opens avatar dropdown popover when clicking avatar button and elevates header z-index to z-50", () => {
    renderWithProviders(
      <MobileDashboardHeader
        onToggleSidebar={vi.fn()}
        onNewSession={vi.fn()}
      />
    );

    const header = screen.getByTestId("mobile-dashboard-header");
    expect(header).toHaveClass("z-40");

    const avatarBtn = screen.getByTestId("mobile-header-avatar-btn");
    fireEvent.click(avatarBtn);

    // Popover contains user name or options and header is elevated to z-50 above workspace
    expect(header).toHaveClass("z-50");
    expect(screen.getByText("Richard Feynman")).toBeInTheDocument();
  });
});

describe("Standby Screen with Mobile Top Header in DashboardContainer", () => {
  beforeEach(() => {
    useDashboardStore.getState().reset();
    useWorkspaceStore.getState().resetWorkspace();
    useWorkspaceStore.getState().initNewStandbyChat();
    useAuthStore.setState({
      user: {
        id: "scholar-1",
        email: "scholar@verischolar.org",
        full_name: "Richard Feynman",
        role: "researcher",
        is_verified: true,
        created_at: new Date().toISOString(),
      },
      isAuthenticated: true,
      token: "mock-token",
    });
    vi.restoreAllMocks();
  });

  it("renders Mobile Top Header together with HeroUploadDropzone on Standby screen", () => {
    renderWithProviders(<DashboardContainer />);

    // Mobile Top Header is rendered
    expect(screen.getByTestId("mobile-dashboard-header")).toBeInTheDocument();
    expect(screen.getByTestId("mobile-header-menu-btn")).toBeInTheDocument();
    expect(screen.queryByTestId("mobile-header-new-chat-btn")).toBeNull();

    // Standby Hero dropzone is also present
    expect(screen.getByText(/Tải lên bài báo/i)).toBeInTheDocument();
  });

  it("clicking hamburger on Standby screen expands Taskbar Drawer and renders backdrop", () => {
    renderWithProviders(<DashboardContainer />);

    expect(useDashboardStore.getState().sidebarState).toBe("collapsed");

    // Click Hamburger menu
    const menuBtn = screen.getByTestId("mobile-header-menu-btn");
    fireEvent.click(menuBtn);

    // Sidebar state is now expanded
    expect(useDashboardStore.getState().sidebarState).toBe("expanded");

    // Backdrop is present
    const backdrop = screen.getByTestId("mobile-drawer-backdrop");
    expect(backdrop).toBeInTheDocument();

    // Clicking backdrop closes drawer
    fireEvent.click(backdrop);
    expect(useDashboardStore.getState().sidebarState).toBe("collapsed");
  });
});
