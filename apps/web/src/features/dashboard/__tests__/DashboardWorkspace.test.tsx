import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DashboardWorkspace } from "../components/DashboardWorkspace";
import { useWorkspaceStore } from "../stores/useWorkspaceStore";
import { useReaderStore } from "@/features/reader/stores/useReaderStore";
import * as documentHooks from "@/features/documents/hooks/useDocumentQueries";
import * as sessionHooks from "@/features/sessions/hooks/useSessionsQuery";
import * as noteHooks from "@/features/notes/hooks/useNotesQuery";

// Mock child reader components
vi.mock("@/features/reader/components/PdfCanvasViewer", () => ({
  PdfCanvasViewer: () => <div data-testid="mock-pdf-canvas-viewer">PdfCanvasViewer</div>,
}));

vi.mock("@/features/reader/components/AbstractOnlyViewer", () => ({
  AbstractOnlyViewer: ({ document }: { document: { title?: string } }) => (
    <div data-testid="mock-abstract-only-viewer">AbstractOnlyViewer: {document?.title}</div>
  ),
}));

// Mock API client
vi.mock("@/features/documents/api/documentsApi", () => ({
  documentsApi: {
    getDocumentFileUrl: vi.fn((id: string) => `/api/v1/documents/${id}/file`),
  },
}));

describe("DashboardWorkspace Conditional Reader Routing", () => {
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

    useReaderStore.setState({
      activeDocumentId: "doc-1",
      openDocumentIds: ["doc-1"],
      currentPage: 1,
      totalPages: 10,
      zoomRatio: 1.0,
      rotationDeg: 0,
    });

    // Default mock hook returns
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

    vi.spyOn(documentHooks, "useDocumentStructure").mockReturnValue({
      data: undefined,
    } as any);

    vi.spyOn(documentHooks, "useDocumentReferences").mockReturnValue({
      data: undefined,
    } as any);

    vi.spyOn(documentHooks, "useDocumentSummary").mockReturnValue({
      data: undefined,
    } as any);

    vi.spyOn(documentHooks, "useDeleteDocumentMutation").mockReturnValue({
      mutateAsync: vi.fn(),
    } as any);

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

    vi.spyOn(sessionHooks, "useAddSessionDocumentMutation").mockReturnValue({
      mutateAsync: vi.fn(),
    } as any);

    vi.spyOn(sessionHooks, "useUpdateSessionViewportMutation").mockReturnValue({
      mutateAsync: vi.fn(),
    } as any);

    vi.spyOn(sessionHooks, "useUpdateSessionMetadataMutation").mockReturnValue({
      mutateAsync: vi.fn(),
    } as any);

    vi.spyOn(sessionHooks, "useDeleteSessionMutation").mockReturnValue({
      mutateAsync: vi.fn(),
    } as any);

    vi.spyOn(noteHooks, "useCreateNoteMutation").mockReturnValue({
      mutateAsync: vi.fn(),
    } as any);
  });

  it("renders AbstractOnlyViewer and does NOT render PdfCanvasViewer when access_status is 'abstract_only'", () => {
    vi.spyOn(documentHooks, "useDocumentDetail").mockReturnValue({
      data: {
        id: "doc-1",
        filename: "sample.pdf",
        title: "Abstract Only Paper",
        authors: ["Author 1"],
        publication_year: 2024,
        doi: "10.1234/test",
        chunk_count: 0,
        file_size_bytes: 0,
        status: "abstract_only",
        access_status: "abstract_only",
        is_persistent: false,
        pages_metadata: [],
        created_at: new Date().toISOString(),
      },
      isLoading: false,
    } as any);

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

    expect(screen.getByTestId("mock-abstract-only-viewer")).toBeInTheDocument();
    expect(screen.getByText(/AbstractOnlyViewer: Abstract Only Paper/)).toBeInTheDocument();
    expect(screen.queryByTestId("mock-pdf-canvas-viewer")).not.toBeInTheDocument();
  });

  it("renders PdfCanvasViewer and does NOT render AbstractOnlyViewer when access_status is 'open_access_pdf'", () => {
    vi.spyOn(documentHooks, "useDocumentDetail").mockReturnValue({
      data: {
        id: "doc-1",
        filename: "sample.pdf",
        title: "Full PDF Paper",
        authors: ["Author 2"],
        publication_year: 2023,
        doi: "10.1234/full",
        chunk_count: 5,
        file_size_bytes: 10240,
        status: "completed",
        access_status: "open_access_pdf",
        is_persistent: true,
        pages_metadata: [],
        created_at: new Date().toISOString(),
      },
      isLoading: false,
    } as any);

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

    expect(screen.getByTestId("mock-pdf-canvas-viewer")).toBeInTheDocument();
    expect(screen.queryByTestId("mock-abstract-only-viewer")).not.toBeInTheDocument();
  });
});
