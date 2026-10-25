import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter, Routes, Route, useLocation } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DashboardTaskbar } from "./DashboardTaskbar";
import { useDashboardStore } from "../stores/useDashboardStore";
import { RECENT_SESSIONS } from "../data/mockDashboardData";

function LocationDisplay() {
  const location = useLocation();
  return <div data-testid="location-display">{location.pathname}</div>;
}

function renderTaskbarWithRouter(initialRoute = "/dashboard") {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[initialRoute]}>
        <div className="flex">
          <DashboardTaskbar
            sessions={RECENT_SESSIONS}
            onSelectSession={vi.fn()}
            onNewSession={vi.fn()}
          />
          <main>
            <LocationDisplay />
            <Routes>
              <Route path="/dashboard" element={<div>Trang Nghiên cứu</div>} />
              <Route path="/library" element={<div>Trang Thư viện</div>} />
              <Route path="/writing" element={<div>Trang Soạn thảo</div>} />
              <Route path="/discovery" element={<div>Trang Khám phá</div>} />
            </Routes>
          </main>
        </div>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("Modular PRD Routes & Taskbar Navigation", () => {
  beforeEach(() => {
    useDashboardStore.getState().reset();
  });

  it("highlights 'Khám phá & Phiên đọc' when on /dashboard", () => {
    renderTaskbarWithRouter("/dashboard");
    expect(screen.getByTestId("location-display")).toHaveTextContent("/dashboard");

    const researchBtn = screen.getByTitle(/Khám phá & Phiên đọc/i);
    expect(researchBtn).toBeInTheDocument();
    expect(researchBtn).toHaveClass("bg-coral-500/15");
  });

  it("navigates to /library when clicking 'Kho Yêu thích'", () => {
    renderTaskbarWithRouter("/dashboard");

    const libraryBtn = screen.getByTitle("Thư viện tài liệu nghiên cứu");
    fireEvent.click(libraryBtn);

    expect(screen.getByTestId("location-display")).toHaveTextContent("/library");
    expect(screen.getByText("Trang Thư viện")).toBeInTheDocument();
  });

  it("navigates to /writing when clicking 'Soạn thảo LaTeX'", () => {
    renderTaskbarWithRouter("/dashboard");

    const writingBtn = screen.getByTitle(/Soạn thảo LaTeX/i);
    fireEvent.click(writingBtn);

    expect(screen.getByTestId("location-display")).toHaveTextContent("/writing");
    expect(screen.getByText("Trang Soạn thảo")).toBeInTheDocument();
  });

  it("excludes out-of-scope Matrix, Projects, and standalone Notes buttons from taskbar", () => {
    renderTaskbarWithRouter("/dashboard");

    expect(screen.queryByTitle(/Ma trận đối chiếu/i)).not.toBeInTheDocument();
    expect(screen.queryByTitle(/Dự án nghiên cứu/i)).not.toBeInTheDocument();
    expect(screen.queryByTitle(/Sổ tay tri thức/i)).not.toBeInTheDocument();
  });

  it("strictly prevents dual active highlights: exactly one item is active even if store appMode was 'library'", () => {
    // Simulate lingering or stale appMode = "library" in store
    useDashboardStore.setState({ appMode: "library" });

    renderTaskbarWithRouter("/dashboard");

    const researchBtn = screen.getByTitle(/Khám phá & Phiên đọc/i);
    const libraryBtn = screen.getByTitle("Thư viện tài liệu nghiên cứu");
    const writingBtn = screen.getByTitle(/Soạn thảo LaTeX/i);

    // ONLY research must be active
    expect(researchBtn).toHaveClass("bg-coral-500/15");
    // All other buttons must NOT be active
    expect(libraryBtn).not.toHaveClass("bg-coral-500/15");
    expect(writingBtn).not.toHaveClass("bg-coral-500/15");
  });

  it("highlights only 'Kho Yêu thích' when route is /library and leaves 'Khám phá & Phiên đọc' inactive", () => {
    renderTaskbarWithRouter("/library");

    const researchBtn = screen.getByTitle(/Khám phá & Phiên đọc/i);
    const libraryBtn = screen.getByTitle("Thư viện tài liệu nghiên cứu");

    expect(libraryBtn).toHaveClass("bg-coral-500/15");
    expect(researchBtn).not.toHaveClass("bg-coral-500/15");
  });
});
