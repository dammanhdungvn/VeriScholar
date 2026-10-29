import { render, screen, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DashboardWorkspace } from "../components/DashboardWorkspace";
import { AcademicMarkdownRenderer } from "@/components/shared/AcademicMarkdownRenderer";
import { useWorkspaceStore } from "../stores/useWorkspaceStore";
import { useDashboardStore } from "../stores/useDashboardStore";
import { useReaderStore } from "@/features/reader/stores/useReaderStore";
import * as documentHooks from "@/features/documents/hooks/useDocumentQueries";
import * as sessionHooks from "@/features/sessions/hooks/useSessionsQuery";
import * as noteHooks from "@/features/notes/hooks/useNotesQuery";

// Mock child reader components
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

describe("LayoutScrollAndCaretFix", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });

    useWorkspaceStore.setState({
      activeSessionId: "session-1",
      activeDocumentId: "doc-1",
      documentTitle: "Sample Paper",
      activeRightTab: "chat",
      splitRatio: 50,
      zenMode: "none",
    });

    useDashboardStore.setState({
      activeBbox: null,
    });

    useReaderStore.setState({
      activeDocumentId: "doc-1",
      openDocumentIds: ["doc-1"],
      currentPage: 1,
      totalPages: 10,
      zoomRatio: 1.0,
      rotationDeg: 0,
    });

    vi.spyOn(documentHooks, "useDocumentsList").mockReturnValue({
      data: {
        data: [{ id: "doc-1", title: "Sample Paper", status: "completed" }],
        meta: { total: 1, page: 1, per_page: 10, total_pages: 1 },
      },
      isLoading: false,
    } as any);

    vi.spyOn(documentHooks, "useDocumentDetail").mockReturnValue({
      data: {
        id: "doc-1",
        title: "Sample Paper",
        status: "completed",
        access_status: "open_access_pdf",
        pages_metadata: [],
      },
      isLoading: false,
    } as any);

    vi.spyOn(documentHooks, "useDocumentStructure").mockReturnValue({ data: undefined } as any);
    vi.spyOn(documentHooks, "useDocumentReferences").mockReturnValue({ data: undefined } as any);
    vi.spyOn(documentHooks, "useDocumentSummary").mockReturnValue({ data: undefined } as any);
    vi.spyOn(documentHooks, "useDeleteDocumentMutation").mockReturnValue({ mutateAsync: vi.fn() } as any);

    vi.spyOn(sessionHooks, "useSessionDetail").mockReturnValue({
      data: { data: { id: "session-1", title: "Session 1", version: 1 } },
    } as any);
    vi.spyOn(sessionHooks, "useAddSessionDocumentMutation").mockReturnValue({ mutateAsync: vi.fn() } as any);
    vi.spyOn(sessionHooks, "useUpdateSessionViewportMutation").mockReturnValue({ mutateAsync: vi.fn() } as any);
    vi.spyOn(sessionHooks, "useUpdateSessionMetadataMutation").mockReturnValue({ mutateAsync: vi.fn() } as any);
    vi.spyOn(sessionHooks, "useDeleteSessionMutation").mockReturnValue({ mutateAsync: vi.fn() } as any);
    vi.spyOn(noteHooks, "useCreateNoteMutation").mockReturnValue({ mutateAsync: vi.fn() } as any);
  });

  describe("Container Scroll Isolation", () => {
    it("enforces overflow-hidden and overflow-x-hidden on the root layout container", () => {
      const { container } = render(
        <QueryClientProvider client={queryClient}>
          <DashboardWorkspace
            messages={[]}
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

      const rootLayout = container.firstChild as HTMLElement;
      expect(rootLayout.className).toContain("overflow-hidden");
      expect(rootLayout.className).toContain("overflow-x-hidden");
    });

    it("enforces overflow-x-hidden on the chat scroll container", () => {
      render(
        <QueryClientProvider client={queryClient}>
          <DashboardWorkspace
            messages={[]}
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

      const chatContainer = screen.getByTestId("chat-scroll-container");
      expect(chatContainer.className).toContain("overflow-x-hidden");
      expect(chatContainer.className).toContain("overflow-y-auto");
    });

    it("scrolls locally within the PDF viewer container instead of invoking global scrollIntoView on bbox", () => {
      const scrollIntoViewSpy = vi.fn();
      window.HTMLElement.prototype.scrollIntoView = scrollIntoViewSpy;

      useWorkspaceStore.setState({ activeDocumentId: "" });

      render(
        <QueryClientProvider client={queryClient}>
          <DashboardWorkspace
            messages={[]}
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

      // Trigger bbox update after mount
      act(() => {
        useDashboardStore.getState().setActiveBbox([0.1, 0.1, 0.5, 0.5, 1]);
      });

      expect(scrollIntoViewSpy).not.toHaveBeenCalled();
    });
  });

  describe("AcademicMarkdownRenderer Streaming Caret Refinement", () => {
    it("does not render a standalone chunky orange block w-1.5 h-4 on empty stream", () => {
      const { container } = render(
        <AcademicMarkdownRenderer content="" isStreaming={true} />
      );

      // Chunky orange block must NOT exist
      expect(container.querySelector(".w-1\\.5")).toBeNull();
      expect(container.querySelector(".h-4")).toBeNull();
      expect(container.querySelector(".bg-\\[\\#cc785c\\]")).toBeNull();
      expect(screen.queryByTestId("typing-caret")).toBeNull();
    });

    it("renders an inline subtle pulse caret when text is actively streaming without chunky w-1.5 h-4 classes", () => {
      const { container } = render(
        <AcademicMarkdownRenderer content="AI is synthesizing this response" isStreaming={true} />
      );

      const caret = screen.getByTestId("typing-caret");
      expect(caret).toBeInTheDocument();
      expect(caret.className).toContain("animate-pulse");
      // Must NOT be the chunky w-1.5 h-4 block
      expect(caret.className).not.toContain("w-1.5");
      expect(caret.className).not.toContain("h-4");
      expect(container.querySelector(".w-1\\.5.h-4")).toBeNull();
    });
  });
});

