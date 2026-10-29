import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Mock hooks to simulate initial session & document loading
vi.mock("@/features/documents/hooks/useDocumentQueries", () => ({
  useDocumentsList: () => ({ data: undefined, isLoading: true }),
  useDocumentDetail: () => ({ data: undefined, isLoading: true }),
  useDocumentStatusQuery: () => ({ data: undefined, isLoading: false }),
  useDocumentStructure: () => ({ data: undefined }),
  useDocumentReferences: () => ({ data: undefined }),
  useDocumentSummary: () => ({ data: undefined }),
  useDocumentChunks: () => ({ data: undefined }),
  useChunkDetail: () => ({ data: undefined }),
  useDeleteDocumentMutation: () => ({ mutateAsync: vi.fn() }),
  useStarDocumentMutation: () => ({ mutateAsync: vi.fn() }),
  useGenerateSummaryMutation: () => ({ mutateAsync: vi.fn() }),
  DOCUMENT_QUERY_KEYS: {
    list: () => ["documents"],
    detail: (id: string) => ["documents", id],
    summary: (id: string) => ["documents", id, "summary"],
    chunks: () => ["documents", "chunks"],
    chunkDetail: () => ["documents", "chunkDetail"],
  },
}));

vi.mock("@/features/sessions/hooks/useSessionsQuery", () => ({
  useSessionDetail: () => ({ data: undefined, isLoading: true }),
  useUpdateSessionViewportMutation: () => ({ mutateAsync: vi.fn() }),
  useAddSessionDocumentMutation: () => ({ mutateAsync: vi.fn() }),
  useUpdateSessionMetadataMutation: () => ({ mutateAsync: vi.fn() }),
  useDeleteSessionMutation: () => ({ mutateAsync: vi.fn() }),
  SESSION_QUERY_KEYS: {
    detail: (id?: string) => ["sessions", id],
    list: () => ["sessions"],
  },
}));

vi.mock("@/features/notes/hooks/useNotesQuery", () => ({
  useCreateNoteMutation: () => ({ mutateAsync: vi.fn() }),
}));

// Also alias/mock brief-specified paths
vi.mock("@/features/documents/hooks/useDocumentIngestion", () => ({
  useDocumentsList: () => ({ data: undefined, isLoading: true }),
  useDocumentDetail: () => ({ data: undefined, isLoading: true }),
  useDocumentStructure: () => ({ data: undefined }),
  useDocumentReferences: () => ({ data: undefined }),
  useDocumentSummary: () => ({ data: undefined }),
  useDeleteDocumentMutation: () => ({ mutateAsync: vi.fn() }),
}));

vi.mock("@/features/sessions/hooks/useSessionDetail", () => ({
  useSessionDetail: () => ({ data: undefined, isLoading: true }),
  useUpdateSessionViewportMutation: () => ({ mutateAsync: vi.fn() }),
  useAddSessionDocumentMutation: () => ({ mutateAsync: vi.fn() }),
}));

describe("DashboardWorkspace Loading State", () => {
  it("renders paper-loading-skeleton and does NOT render empty state when loading docs/session", async () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    // Dynamic import to pick up mocks
    const { DashboardWorkspace } = await import("../components/DashboardWorkspace");
    render(
      <QueryClientProvider client={queryClient}>
        <DashboardWorkspace />
      </QueryClientProvider>
    );
    
    expect(screen.getByTestId("paper-loading-skeleton")).toBeInTheDocument();
    expect(screen.queryByText("Chưa có tài liệu nghiên cứu nào")).not.toBeInTheDocument();
  });
});
