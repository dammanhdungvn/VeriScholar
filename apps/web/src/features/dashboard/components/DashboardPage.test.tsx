import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DashboardPage } from "./DashboardPage";
import { useAuthStore } from "@/features/auth/stores/useAuthStore";
import { useDashboardStore } from "../stores/useDashboardStore";
import { useWorkspaceStore } from "../stores/useWorkspaceStore";
import { dashboardApi } from "../api/dashboardApi";

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("DashboardPage component - Lazy Session & Dynamic Workspace Flow", () => {
  beforeEach(() => {
    localStorage.clear();
    useDashboardStore.getState().reset();
    useWorkspaceStore.getState().resetWorkspace();
    useAuthStore.getState().login(
      {
        user: {
          id: "usr-test-1",
          email: "scholar@verischolar.ai",
          full_name: "GS.TS. Nguyen Van A",
          role: "faculty",
          is_verified: true,
          created_at: "2026-01-01",
        },
        tokens: {
          access_token: "mock-token",
          refresh_token: "mock-refresh",
          token_type: "bearer",
          expires_in: 3600,
        },
      },
      false
    );
  });

  it("test_hero_dropzone_visible_and_chat_input_hidden: renders Hero Dropzone and hides chat input in standby mode", () => {
    renderWithProviders(<DashboardPage />);

    // Sidebar exists
    expect(
      screen.getByRole("complementary", { name: /thanh điều hướng chính/i })
    ).toBeInTheDocument();

    // Standby Hero Dropzone title & subtitle are visible
    expect(
      screen.getByText(/Tải lên bài báo/i)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Kéo thả hoặc chọn tệp PDF/i)
    ).toBeInTheDocument();
    expect(screen.getByText(/PDF • Tối đa 50MB/i)).toBeInTheDocument();

    // Invariant 1: Chat input is NOT rendered when standby
    expect(
      screen.queryByPlaceholderText(/Tôi có thể giúp gì/i)
    ).not.toBeInTheDocument();
  });

  it("test_lazy_session_zero_api_call_on_init: clicking 'Đoạn chat mới' does not call POST /api/v1/sessions", async () => {
    const createSessionSpy = vi.spyOn(dashboardApi, "createSession");

    renderWithProviders(<DashboardPage />);

    // Click "Đoạn chat mới" button
    const newChatBtn = screen.getByTitle("Đoạn chat mới");
    fireEvent.click(newChatBtn);

    // Invariant 1 (Zero DB Junk): Must NOT call API to create session
    expect(createSessionSpy).not.toHaveBeenCalled();

    // Still in Standby mode
    expect(
      screen.getByText(/Tải lên bài báo/i)
    ).toBeInTheDocument();
    expect(
      screen.queryByPlaceholderText(/Tôi có thể giúp gì/i)
    ).not.toBeInTheDocument();

    createSessionSpy.mockRestore();
  });

  it("test_workspace_transition_on_upload_success: switches to Split-Pane workspace when document is loaded", async () => {
    renderWithProviders(<DashboardPage />);

    // Simulate completion of ingestion
    act(() => {
      useWorkspaceStore.getState().setDocument("doc-test", "Attention Is All You Need");
      useWorkspaceStore.getState().setStatus("completed", 100);
    });

    await waitFor(() => {
      // PDF Canvas pane with document title
      expect(
        screen.getAllByText(/Attention Is All You Need/i).length
      ).toBeGreaterThan(0);

      // Socratic Copilot Pane
      expect(screen.getByText(/Socratic Copilot/i)).toBeInTheDocument();

      // Bottom-docked Chat Input appears in Workspace
      expect(
        screen.getByPlaceholderText(/Tôi có thể giúp gì/i)
      ).toBeInTheDocument();
    });
  });

  it("renders Cowork mode when appMode is cowork and allows returning to chat", () => {
    useDashboardStore.getState().setAppMode("cowork");
    renderWithProviders(<DashboardPage />);

    expect(screen.getByText("Kế Hoạch Thực Thi")).toBeInTheDocument();

    const backBtn = screen.getByTitle("Quay lại hội thoại");
    fireEvent.click(backBtn);
    expect(useDashboardStore.getState().appMode).toBe("chat");
  });
});
