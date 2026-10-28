import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { AppLayout } from "../components/AppLayout";

// Mock react-query and hooks
vi.mock("@/features/dashboard/hooks/useDashboardSessions", () => ({
  useDashboardSessions: () => ({
    sessions: [],
    createSession: vi.fn(),
    selectSession: vi.fn(),
    deleteSession: vi.fn(),
    renameSession: vi.fn(),
  }),
}));

describe("AppLayout Navigation & Persistence", () => {
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
});
