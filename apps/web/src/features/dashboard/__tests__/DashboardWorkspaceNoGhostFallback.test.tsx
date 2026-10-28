import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DashboardWorkspace } from "../components/DashboardWorkspace";
import { useReaderStore } from "@/features/reader/stores/useReaderStore";
import { useWorkspaceStore } from "../stores/useWorkspaceStore";

vi.mock("@/features/documents/hooks/useDocumentQueries", () => ({
  DOCUMENT_QUERY_KEYS: {
    all: ["documents"],
    list: () => ["documents", "list"],
    detail: (id: string) => ["documents", "detail", id],
    structure: (id: string) => ["documents", "structure", id],
    summary: (id: string) => ["documents", "summary", id],
    chunks: (id: string) => ["documents", "chunks", id],
    references: (id: string) => ["documents", "references", id],
  },
  useDocumentsList: () => ({
    data: {
      data: [
        {
          id: "doc-attention-first",
          title: "Attention Is All You Need",
          filename: "attention.pdf",
          status: "completed",
        },
      ],
    },
    isLoading: false,
  }),
  useDocumentDetail: () => ({ data: undefined, isLoading: false }),
  useDocumentStructure: () => ({ data: undefined }),
  useDocumentReferences: () => ({ data: undefined }),
  useDocumentSummary: () => ({ data: undefined }),
  useDocumentChunks: () => ({ data: undefined, isLoading: false }),
  useChunkDetail: () => ({ data: undefined, isLoading: false }),
  useDocumentStatusQuery: () => ({ data: undefined, isLoading: false }),
  useDeleteDocumentMutation: () => ({ mutateAsync: vi.fn() }),
  useStarDocumentMutation: () => ({ mutateAsync: vi.fn() }),
  useGenerateSummaryMutation: () => ({ mutateAsync: vi.fn() }),
}));

vi.mock("@/features/sessions/hooks/useSessionsQuery", () => ({
  useSessionDetail: () => ({
    data: {
      data: {
        id: "session-empty",
        title: "Nghiên cứu: Empty Session",
        document_ids: [],
        documents: [],
      },
    },
    isLoading: false,
  }),
  useAddSessionDocumentMutation: () => ({ mutateAsync: vi.fn() }),
  useUpdateSessionViewportMutation: () => ({ mutate: vi.fn(), mutateAsync: vi.fn() }),
  useUpdateSessionMetadataMutation: () => ({ mutateAsync: vi.fn() }),
  useDeleteSessionMutation: () => ({ mutateAsync: vi.fn() }),
  useRestoreArchivedSessionMutation: () => ({ mutateAsync: vi.fn() }),
}));

vi.mock("@/features/notes/hooks/useNotesQuery", () => ({
  useCreateNoteMutation: () => ({ mutateAsync: vi.fn() }),
}));

// Mock child reader components
vi.mock("@/features/reader/components/PdfCanvasViewer", () => ({
  PdfCanvasViewer: () => <div data-testid="mock-pdf-canvas-viewer">PdfCanvasViewer</div>,
}));

vi.mock("@/features/reader/components/AbstractOnlyViewer", () => ({
  AbstractOnlyViewer: ({ document }: { document: { title?: string } }) => (
    <div data-testid="mock-abstract-only-viewer">AbstractOnlyViewer: {document?.title}</div>
  ),
}));

describe("DashboardWorkspace No Ghost Fallback", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    useReaderStore.setState({
      openDocumentIds: [],
      activeDocumentId: null,
    });
    useWorkspaceStore.setState({
      activeSessionId: null,
      activeDocumentId: null,
      documentTitle: "",
    });
  });

  it("renders Empty State and does NOT display Attention Is All You Need when session has 0 documents", () => {
    render(
      <QueryClientProvider client={queryClient}>
        <DashboardWorkspace
          sessionId="session-empty"
          sessionTitle="Nghiên cứu: Empty Session"
        />
      </QueryClientProvider>
    );

    // Empty state should be rendered
    expect(screen.getByText("Chưa có tài liệu nghiên cứu nào")).toBeInTheDocument();
    // Ghost document must NOT be rendered in tabs or viewer!
    expect(screen.queryByText("Attention Is All You Need")).not.toBeInTheDocument();
  });
});
