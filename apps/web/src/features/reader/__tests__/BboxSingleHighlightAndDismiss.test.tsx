import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BboxHighlightLayer } from "../components/BboxHighlightLayer";
import { useReaderStore } from "../stores/useReaderStore";
import { DashboardWorkspace } from "@/features/dashboard/components/DashboardWorkspace";
import { useWorkspaceStore } from "@/features/dashboard/stores/useWorkspaceStore";
import { useDashboardStore } from "@/features/dashboard/stores/useDashboardStore";
import type { BoundingBox } from "@/types/api";
import type { ChatMessage } from "@/types/dashboard";
import * as documentHooks from "@/features/documents/hooks/useDocumentQueries";
import * as sessionHooks from "@/features/sessions/hooks/useSessionsQuery";
import * as noteHooks from "@/features/notes/hooks/useNotesQuery";

// Mock child reader components for DashboardWorkspace test
vi.mock("@/features/reader/components/PdfCanvasViewer", () => ({
  PdfCanvasViewer: () => <div data-testid="mock-pdf-canvas-viewer">PdfCanvasViewer</div>,
}));

vi.mock("@/features/reader/components/AbstractOnlyViewer", () => ({
  AbstractOnlyViewer: () => <div data-testid="mock-abstract-only-viewer">AbstractOnlyViewer</div>,
}));

vi.mock("@/features/documents/api/documentsApi", () => ({
  documentsApi: {
    getDocumentFileUrl: vi.fn((id: string) => `/api/v1/documents/${id}/file`),
  },
}));

describe("BboxSingleHighlightAndDismiss", () => {
  describe("BboxHighlightLayer component invariants", () => {
    it("renders at most ONE bounding box even when multiple bboxes are provided for the current page", () => {
      const multiBboxes: BoundingBox[] = [
        [0.1, 0.2, 0.4, 0.3, 1],
        [0.15, 0.25, 0.45, 0.35, 1],
        [0.2, 0.3, 0.5, 0.4, 1],
      ];

      render(
        <BboxHighlightLayer
          bboxes={multiBboxes}
          currentPage={1}
          isActive={true}
        />
      );

      const overlays = screen.getAllByTestId("grounded-bbox-overlay");
      expect(overlays).toHaveLength(1);
    });

    it("triggers onClear when Escape key is pressed", () => {
      const onClear = vi.fn();
      const mockBbox: BoundingBox = [0.1, 0.2, 0.4, 0.3, 1];

      render(
        <BboxHighlightLayer
          bbox={mockBbox}
          currentPage={1}
          isActive={true}
          onClear={onClear}
        />
      );

      expect(screen.getByTestId("grounded-bbox-overlay")).toBeInTheDocument();

      fireEvent.keyDown(window, { key: "Escape" });
      expect(onClear).toHaveBeenCalledTimes(1);
    });

    it("triggers onClear when clicking the dismiss button ✕", () => {
      const onClear = vi.fn();
      const mockBbox: BoundingBox = [0.1, 0.2, 0.4, 0.3, 1];

      render(
        <BboxHighlightLayer
          bbox={mockBbox}
          currentPage={1}
          isActive={true}
          onClear={onClear}
        />
      );

      const dismissBtn = screen.getByRole("button", { name: /đóng khung trích dẫn/i });
      expect(dismissBtn).toBeInTheDocument();
      expect(dismissBtn.textContent).toContain("✕");

      fireEvent.click(dismissBtn);
      expect(onClear).toHaveBeenCalledTimes(1);
    });
  });

  describe("Reader store single bounding box cap", () => {
    beforeEach(() => {
      useReaderStore.getState().resetReader();
    });

    it("enforces at most ONE box in activeBboxes when setActiveCitation is called with multiple boxes", () => {
      const multiBboxes: BoundingBox[] = [
        [0.1, 0.2, 0.4, 0.3, 1],
        [0.15, 0.25, 0.45, 0.35, 1],
        [0.2, 0.3, 0.5, 0.4, 1],
      ];

      useReaderStore.getState().setActiveCitation("cit_1", null, 1, multiBboxes);

      const state = useReaderStore.getState();
      expect(state.activeCitationId).toBe("cit_1");
      expect(state.activeBbox).toEqual([0.1, 0.2, 0.4, 0.3, 1]);
      expect(state.activeBboxes).toHaveLength(1);
      expect(state.activeBboxes).toEqual([[0.1, 0.2, 0.4, 0.3, 1]]);
    });
  });

  describe("Citation re-click toggle-off mechanism in DashboardWorkspace", () => {
    let queryClient: QueryClient;

    beforeEach(() => {
      vi.clearAllMocks();
      queryClient = new QueryClient({
        defaultOptions: { queries: { retry: false } },
      });

      useWorkspaceStore.setState({
        activeSessionId: "session-1",
        activeDocumentId: "doc-1",
        documentTitle: "Sample Paper",
        activeRightTab: "chat",
        splitRatio: 50,
        zenMode: "none",
      });

      useReaderStore.getState().resetReader();
      useReaderStore.setState({
        activeDocumentId: "doc-1",
        openDocumentIds: ["doc-1"],
        currentPage: 1,
        totalPages: 10,
        zoomRatio: 1.0,
        rotationDeg: 0,
      });

      useDashboardStore.setState({
        activeBbox: null,
      });

      vi.spyOn(documentHooks, "useDocumentsList").mockReturnValue({
        data: {
          data: [
            {
              id: "doc-1",
              filename: "sample.pdf",
              title: "Sample Paper",
              status: "completed",
              is_persistent: true,
              created_at: new Date().toISOString(),
            },
          ],
          meta: { total: 1, page: 1, per_page: 10, total_pages: 1 },
        },
        isLoading: false,
      } as any);

      vi.spyOn(documentHooks, "useDocumentDetail").mockReturnValue({
        data: {
          id: "doc-1",
          filename: "sample.pdf",
          title: "Sample Paper",
          authors: ["Author 1"],
          publication_year: 2024,
          doi: "10.1234/test",
          chunk_count: 5,
          file_size_bytes: 1024,
          status: "ready",
          access_status: "full_text",
          is_persistent: true,
          pages_metadata: [],
          created_at: new Date().toISOString(),
        },
        isLoading: false,
      } as any);

      vi.spyOn(documentHooks, "useDocumentStructure").mockReturnValue({ data: undefined } as any);
      vi.spyOn(documentHooks, "useDocumentReferences").mockReturnValue({ data: undefined } as any);
      vi.spyOn(documentHooks, "useDocumentSummary").mockReturnValue({ data: undefined } as any);
      vi.spyOn(documentHooks, "useDeleteDocumentMutation").mockReturnValue({ mutateAsync: vi.fn() } as any);

      vi.spyOn(sessionHooks, "useSessionDetail").mockReturnValue({
        data: {
          data: {
            id: "session-1",
            title: "Session 1",
            version: 1,
            viewport_state: { page: 1, zoom_ratio: 1.0 },
          },
        },
      } as any);

      vi.spyOn(sessionHooks, "useAddSessionDocumentMutation").mockReturnValue({ mutateAsync: vi.fn() } as any);
      vi.spyOn(sessionHooks, "useUpdateSessionViewportMutation").mockReturnValue({ mutateAsync: vi.fn() } as any);
      vi.spyOn(sessionHooks, "useUpdateSessionMetadataMutation").mockReturnValue({ mutateAsync: vi.fn() } as any);
      vi.spyOn(sessionHooks, "useDeleteSessionMutation").mockReturnValue({ mutateAsync: vi.fn() } as any);
      vi.spyOn(noteHooks, "useCreateNoteMutation").mockReturnValue({ mutateAsync: vi.fn() } as any);
    });

    it("activates citation on first click, and toggles it off on second click", () => {
      const messages: ChatMessage[] = [
        {
          id: "msg-1",
          session_id: "session-1",
          role: "assistant",
          content: "Here is grounded evidence [1].",
          citations: [
            {
              citation_id: "cit_1",
              paper_id: "doc-1",
              paper_title: "Sample Paper",
              page: 1,
              bbox: [0.1, 0.2, 0.3, 0.4, 1],
              bounding_boxes: [[0.1, 0.2, 0.3, 0.4, 1]],
            },
          ],
          created_at: new Date().toISOString(),
        },
      ];

      render(
        <QueryClientProvider client={queryClient}>
          <DashboardWorkspace
            messages={messages}
            inputText=""
            onChangeText={vi.fn()}
            onSend={vi.fn()}
            isGenerating={false}
            onStopGeneration={vi.fn()}
            onResetChat={vi.fn()}
            sessionId="session-1"
          />
        </QueryClientProvider>
      );

      // First click: should activate the citation and bounding box
      fireEvent.click(screen.getByTestId("citation-badge"));
      expect(useReaderStore.getState().activeCitationId).toBe("cit_1");
      expect(useReaderStore.getState().activeBbox).toEqual([0.1, 0.2, 0.3, 0.4, 1]);
      expect(useDashboardStore.getState().activeBbox).toEqual([0.1, 0.2, 0.3, 0.4, 1]);

      // Second click: should toggle off both reader citation and dashboard activeBbox
      fireEvent.click(screen.getByTestId("citation-badge"));
      expect(useReaderStore.getState().activeCitationId).toBeNull();
      expect(useReaderStore.getState().activeBbox).toBeNull();
      expect(useDashboardStore.getState().activeBbox).toBeNull();
    });
  });
});
