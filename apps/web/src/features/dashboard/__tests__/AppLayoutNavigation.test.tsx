import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { AppLayout } from "../components/AppLayout";
import { useReaderStore } from "@/features/reader/stores/useReaderStore";
import { useDashboardStore } from "../stores/useDashboardStore";

const mockCreateSession = vi.fn();

// Mock react-query and hooks
vi.mock("@/features/dashboard/hooks/useDashboardSessions", () => ({
  useDashboardSessions: () => ({
    sessions: [],
    createSession: mockCreateSession,
    selectSession: vi.fn(),
    deleteSession: vi.fn(),
    renameSession: vi.fn(),
    updateTitle: vi.fn(),
  }),
}));

describe("AppLayout Navigation & Persistence", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders AppLayout with persistent taskbar and renders outlet content", () => {
    render(
      <MemoryRouter initialEntries={["/dashboard"]}>
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<div data-testid="dashboard-content">Dashboard Content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByLabelText("Thanh điều hướng chính")).toBeInTheDocument();
    expect(screen.getByTestId("dashboard-content")).toBeInTheDocument();
  });

  it("handles 'New Session' with Zero DB Junk: resets to standby without calling createSession", () => {
    render(
      <MemoryRouter initialEntries={["/dashboard"]}>
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<div data-testid="dashboard-content">Dashboard Content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    );

    const newSessionBtn = screen.getByTitle("New Session");
    fireEvent.click(newSessionBtn);

    // BẤT BIẾN 1: Never create session in DB before first action
    expect(mockCreateSession).not.toHaveBeenCalled();
    expect(useDashboardStore.getState().appMode).toBe("chat");
    expect(useDashboardStore.getState().activeSessionId).toBeUndefined();
    expect(useReaderStore.getState().activeDocumentId).toBeNull();
  });
});
