import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { LibraryPage } from "../components/LibraryPage";
import { sessionsApi } from "@/features/sessions/api/sessionsApi";
import * as dashboardSessionsHook from "@/features/dashboard/hooks/useDashboardSessions";
import * as documentHooks from "@/features/documents/hooks/useDocumentQueries";

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe("LibraryPaperSelectionNavigation", () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  const dummyDoc = {
    id: "doc-target-123",
    title: "Attention Is All You Need",
    filename: "attention.pdf",
    is_starred: true,
    is_persistent: true,
    status: "completed",
    page_count: 15,
    created_at: "2026-10-28T00:00:00Z",
  };

  beforeEach(() => {
    vi.clearAllMocks();

    vi.spyOn(documentHooks, "useDocumentsList").mockReturnValue({
      data: {
        data: [dummyDoc],
        total: 1,
        page: 1,
        per_page: 24,
        total_pages: 1,
      },
      isLoading: false,
    } as any);

    vi.spyOn(sessionsApi, "addDocumentToSession").mockResolvedValue({
      id: "sd-1",
      session_id: "sess-new-456",
      document_id: "doc-target-123",
      source_type: "document_id",
      status: "ready",
      created_at: "2026-10-29T00:00:00Z",
    } as any);
  });

  it("calls addDocumentToSession before navigating when clicking a paper card", async () => {
    const mockCreateSession = vi.fn().mockResolvedValue({ id: "sess-new-456", title: "Research: Attention Is All You Need" });
    const mockSelectSession = vi.fn();

    vi.spyOn(dashboardSessionsHook, "useDashboardSessions").mockReturnValue({
      sessions: [],
      createSession: mockCreateSession,
      selectSession: mockSelectSession,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <LibraryPage />
        </BrowserRouter>
      </QueryClientProvider>
    );

    // Find and click the paper card
    const paperTitle = screen.getByText("Attention Is All You Need");
    fireEvent.click(paperTitle.closest("div")!);

    await waitFor(() => {
      expect(mockCreateSession).toHaveBeenCalled();
      expect(sessionsApi.addDocumentToSession).toHaveBeenCalledWith("sess-new-456", {
        source_type: "document_id",
        document_id: "doc-target-123",
      });
      expect(mockSelectSession).toHaveBeenCalledWith("sess-new-456");
      expect(mockNavigate).toHaveBeenCalledWith("/dashboard/sess-new-456");
    });
  });
});
