import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DashboardPage } from "./DashboardPage";
import { useAuthStore } from "@/features/auth/stores/useAuthStore";
import { useDashboardStore } from "../stores/useDashboardStore";

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

describe("DashboardPage component", () => {
  beforeEach(() => {
    localStorage.clear();
    useDashboardStore.getState().reset();
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

  it("renders Dashboard workspace with Taskbar and Hero section", () => {
    renderWithProviders(<DashboardPage />);

    // Sidebar exists
    expect(screen.getByRole("complementary", { name: /thanh điều hướng chính/i })).toBeInTheDocument();

    // Hero title with user name
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(/không gian nghiên cứu/i);

    // Input textarea exists
    expect(
      screen.getByPlaceholderText(/Tìm kiếm tài liệu/i)
    ).toBeInTheDocument();

    // New session control exists
    expect(screen.getByTitle("Đoạn chat mới")).toBeInTheDocument();
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
