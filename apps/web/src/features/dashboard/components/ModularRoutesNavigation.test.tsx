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
              <Route path="/matrix" element={<div>Trang Ma trận 100+</div>} />
              <Route path="/notes" element={<div>Trang Sổ tay</div>} />
              <Route path="/writing" element={<div>Trang Soạn thảo</div>} />
              <Route path="/discovery" element={<div>Trang Khám phá</div>} />
              <Route path="/projects" element={<div>Trang Dự án</div>} />
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

  it("highlights 'Đọc & Nghiên cứu' when on /dashboard", () => {
    renderTaskbarWithRouter("/dashboard");
    expect(screen.getByTestId("location-display")).toHaveTextContent("/dashboard");

    const researchBtn = screen.getByTitle("Đọc & Nghiên cứu (Module 1)");
    expect(researchBtn).toBeInTheDocument();
    expect(researchBtn).toHaveClass("bg-coral-500/15");
  });

  it("navigates to /library when clicking 'Thư viện'", () => {
    renderTaskbarWithRouter("/dashboard");

    const libraryBtn = screen.getByTitle("Thư viện tài liệu nghiên cứu");
    fireEvent.click(libraryBtn);

    expect(screen.getByTestId("location-display")).toHaveTextContent("/library");
    expect(screen.getByText("Trang Thư viện")).toBeInTheDocument();
  });

  it("navigates to /matrix when clicking 'Ma trận đối chiếu 100+'", () => {
    renderTaskbarWithRouter("/dashboard");

    const matrixBtn = screen.getByTitle("Ma trận đối chiếu 100+");
    fireEvent.click(matrixBtn);

    expect(screen.getByTestId("location-display")).toHaveTextContent("/matrix");
    expect(screen.getByText("Trang Ma trận 100+")).toBeInTheDocument();
  });

  it("navigates to /notes when clicking 'Sổ tay tri thức & Tổng hợp'", () => {
    renderTaskbarWithRouter("/dashboard");

    const notesBtn = screen.getByTitle("Sổ tay tri thức & Tổng hợp");
    fireEvent.click(notesBtn);

    expect(screen.getByTestId("location-display")).toHaveTextContent("/notes");
    expect(screen.getByText("Trang Sổ tay")).toBeInTheDocument();
  });

  it("navigates to /writing when clicking 'Soạn thảo & Kiểm chứng (Module 2)'", () => {
    renderTaskbarWithRouter("/dashboard");

    const writingBtn = screen.getByTitle("Soạn thảo & Kiểm chứng (Module 2)");
    fireEvent.click(writingBtn);

    expect(screen.getByTestId("location-display")).toHaveTextContent("/writing");
    expect(screen.getByText("Trang Soạn thảo")).toBeInTheDocument();
  });

  it("navigates to /discovery when clicking 'Khám phá & Đồ thị trích dẫn (Module 3)'", () => {
    renderTaskbarWithRouter("/dashboard");

    const discoveryBtn = screen.getByTitle("Khám phá & Đồ thị trích dẫn (Module 3)");
    fireEvent.click(discoveryBtn);

    expect(screen.getByTestId("location-display")).toHaveTextContent("/discovery");
    expect(screen.getByText("Trang Khám phá")).toBeInTheDocument();
  });

  it("navigates to /projects when clicking 'Dự án nghiên cứu'", () => {
    renderTaskbarWithRouter("/dashboard");

    const projectsBtn = screen.getByTitle("Dự án nghiên cứu");
    fireEvent.click(projectsBtn);

    expect(screen.getByTestId("location-display")).toHaveTextContent("/projects");
    expect(screen.getByText("Trang Dự án")).toBeInTheDocument();
  });

  it("strictly prevents dual active highlights: exactly one item is active even if store appMode was 'library'", () => {
    // Simulate lingering or stale appMode = "library" in store
    useDashboardStore.setState({ appMode: "library" });

    renderTaskbarWithRouter("/dashboard");

    const researchBtn = screen.getByTitle("Đọc & Nghiên cứu (Module 1)");
    const libraryBtn = screen.getByTitle("Thư viện tài liệu nghiên cứu");
    const matrixBtn = screen.getByTitle("Ma trận đối chiếu 100+");
    const projectsBtn = screen.getByTitle("Dự án nghiên cứu");

    // ONLY research must be active
    expect(researchBtn).toHaveClass("bg-coral-500/15");
    // All other buttons must NOT be active
    expect(libraryBtn).not.toHaveClass("bg-coral-500/15");
    expect(matrixBtn).not.toHaveClass("bg-coral-500/15");
    expect(projectsBtn).not.toHaveClass("bg-coral-500/15");
  });

  it("highlights only 'Thư viện' when route is /library and leaves 'Đọc & Nghiên cứu' inactive", () => {
    renderTaskbarWithRouter("/library");

    const researchBtn = screen.getByTitle("Đọc & Nghiên cứu (Module 1)");
    const libraryBtn = screen.getByTitle("Thư viện tài liệu nghiên cứu");

    expect(libraryBtn).toHaveClass("bg-coral-500/15");
    expect(researchBtn).not.toHaveClass("bg-coral-500/15");
  });
});
