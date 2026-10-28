import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DashboardWorkspace } from "../components/DashboardWorkspace";
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

describe("DashboardAlphaXivLayout", () => {
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

  it("verifies 100% paper width and floating AI FAB when assistant is closed, opens on click, and closes via ✕", () => {
    const handleResetChat = vi.fn();

    render(
      <QueryClientProvider client={queryClient}>
        <DashboardWorkspace
          messages={[]}
          inputText=""
          onChangeText={vi.fn()}
          onSend={vi.fn()}
          isGenerating={false}
          onStopGeneration={vi.fn()}
          onResetChat={handleResetChat}
          sessionId="session-1"
          initialAssistantOpen={false}
        />
      </QueryClientProvider>
    );

    // 1. When assistant is closed, paper container is 100% width and floating AI FAB is rendered at bottom right
    const paperContainer = screen.getByTestId("paper-reader-container");
    expect(paperContainer).toHaveStyle({ width: "100%" });
    expect(paperContainer.className).toContain("w-full");

    const fab = screen.getByTestId("floating-assistant-fab");
    expect(fab).toBeInTheDocument();
    expect(fab.className).toContain("fixed");
    expect(fab.className).toContain("bottom-6");
    expect(fab.className).toContain("right-6");

    // Right assistant panel should be hidden
    const assistantPane = screen.getByTestId("assistant-pane-container");
    expect(assistantPane).toHaveStyle({ display: "none" });

    // 2. Clicking floating-assistant-fab opens the Assistant panel
    fireEvent.click(fab);

    // Assistant panel is now visible
    expect(assistantPane).not.toHaveStyle({ display: "none" });
    // FAB is hidden when assistant is open
    expect(screen.queryByTestId("floating-assistant-fab")).not.toBeInTheDocument();

    // 3. Assistant header displays "Assistant", (+) New Chat, and ✕ close button
    expect(screen.getByText("Assistant")).toBeInTheDocument();

    const newChatBtn = screen.getByTestId("new-chat-btn");
    expect(newChatBtn).toBeInTheDocument();
    expect(newChatBtn.textContent).toContain("New Chat");

    // Clicking New Chat calls onResetChat
    fireEvent.click(newChatBtn);
    expect(handleResetChat).toHaveBeenCalledTimes(1);

    const closeBtn = screen.getByTestId("close-assistant-btn");
    expect(closeBtn).toBeInTheDocument();

    // 4. Clicking close-assistant-btn closes the Assistant panel and returns paper to 100% width with floating FAB visible
    fireEvent.click(closeBtn);

    expect(assistantPane).toHaveStyle({ display: "none" });
    expect(paperContainer).toHaveStyle({ width: "100%" });
    expect(screen.getByTestId("floating-assistant-fab")).toBeInTheDocument();
  });

  it("renders VerticalEdgeDock with info, notes, and assistant triggers", () => {
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
          initialAssistantOpen={false}
        />
      </QueryClientProvider>
    );

    const dock = screen.getByTestId("vertical-edge-dock");
    expect(dock).toBeInTheDocument();

    const infoBtn = screen.getByTestId("edge-dock-info-btn");
    expect(infoBtn).toBeInTheDocument();

    const notesBtn = screen.getByTestId("edge-dock-notes-btn");
    expect(notesBtn).toBeInTheDocument();

    const assistantBtn = screen.getByTestId("edge-dock-assistant-btn");
    expect(assistantBtn).toBeInTheDocument();

    // Clicking edge-dock-assistant-btn opens the assistant
    fireEvent.click(assistantBtn);
    const assistantPane = screen.getByTestId("assistant-pane-container");
    expect(assistantPane).not.toHaveStyle({ display: "none" });
  });
});
