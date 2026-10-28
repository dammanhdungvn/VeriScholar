import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { DashboardContainer } from "../components/DashboardContainer";
import { useReaderStore } from "@/features/reader/stores/useReaderStore";
import { useWorkspaceStore } from "../stores/useWorkspaceStore";
import { useDashboardStore } from "../stores/useDashboardStore";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Routes, Route } from "react-router-dom";

let mockSessionDetailData: any = null;
let mockActiveSession: any = undefined;

vi.mock("@/features/sessions/hooks/useSessionsQuery", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/features/sessions/hooks/useSessionsQuery")>();
  return {
    ...actual,
    useSessionDetail: () => ({ data: mockSessionDetailData }),
    useRestoreArchivedSessionMutation: () => ({ mutateAsync: vi.fn() }),
    useUpdateSessionMetadataMutation: () => ({ mutateAsync: vi.fn() }),
    useAddSessionDocumentMutation: () => ({ mutateAsync: vi.fn() }),
    useUpdateSessionViewportMutation: () => ({ mutateAsync: vi.fn() }),
    useDeleteSessionMutation: () => ({ mutateAsync: vi.fn() }),
    SESSION_QUERY_KEYS: { all: ["sessions"] },
  };
});

vi.mock("@/features/dashboard/hooks/useDashboardSessions", () => ({
  useDashboardSessions: () => ({
    sessions: [],
    activeSession: mockActiveSession,
    selectSession: vi.fn(),
    createSession: vi.fn(),
  }),
}));

vi.mock("@/features/documents/hooks/useDocumentIngestion", () => ({
  useDocumentIngestion: () => ({
    isProcessing: false,
    ingest: vi.fn(),
  }),
  useDocumentsList: () => ({ data: { data: [] }, isLoading: false }),
  useDocumentDetail: () => ({ data: undefined, isLoading: false }),
  useDocumentStructure: () => ({ data: undefined }),
  useDocumentReferences: () => ({ data: undefined }),
  useDocumentSummary: () => ({ data: undefined }),
  useDeleteDocumentMutation: () => ({ mutateAsync: vi.fn() }),
}));

vi.mock("../components/DashboardAmbientBackground", () => ({
  DashboardAmbientBackground: () => <div data-testid="ambient-bg" />,
}));

vi.mock("@/features/reader/components/PdfCanvasViewer", () => ({
  PdfCanvasViewer: () => <div data-testid="mock-pdf-canvas-viewer" />,
}));

vi.mock("@/features/reader/components/AbstractOnlyViewer", () => ({
  AbstractOnlyViewer: () => <div data-testid="mock-abstract-only-viewer" />,
}));

vi.mock("../hooks/useStreamingChat", () => ({
  useStreamingChat: () => ({
    messages: [],
    inputText: "",
    setInputText: vi.fn(),
    isGenerating: false,
    sendMessage: vi.fn(),
    stopGeneration: vi.fn(),
    resetChat: vi.fn(),
    loadExistingSession: vi.fn(),
  }),
}));

describe("DashboardContainer Session Document Lifecycle", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    vi.clearAllMocks();
    mockSessionDetailData = null;
    mockActiveSession = undefined;
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    useReaderStore.setState({
      openDocumentIds: ["doc-previous"],
      activeDocumentId: "doc-previous",
    });
    useWorkspaceStore.setState({
      activeDocumentId: "doc-previous",
      documentTitle: "Previous Paper",
      isStandby: false,
    });
    useDashboardStore.setState({
      activeSessionId: "session-old",
    });
  });

  it("clears openDocumentIds and activeDocumentId when session has 0 documents", async () => {
    mockSessionDetailData = {
      data: {
        id: "session-empty",
        title: "Nghiên cứu: Empty Session",
        document_ids: [],
        documents: [],
      },
    };

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/dashboard/session-empty"]}>
          <Routes>
            <Route path="/dashboard/:sessionId" element={<DashboardContainer />} />
            <Route path="/dashboard" element={<DashboardContainer />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(useReaderStore.getState().openDocumentIds).toEqual([]);
    expect(useReaderStore.getState().activeDocumentId).toBeNull();
  });

  it("clears openDocumentIds and activeDocumentId when activeSession has 0 documents", async () => {
    mockActiveSession = {
      id: "session-active-empty",
      title: "Active Session Empty",
      document_ids: [],
    };

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/dashboard"]}>
          <Routes>
            <Route path="/dashboard" element={<DashboardContainer />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(useReaderStore.getState().openDocumentIds).toEqual([]);
    expect(useReaderStore.getState().activeDocumentId).toBeNull();
  });

  it("resets reader store on new session click", async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/dashboard"]}>
          <Routes>
            <Route path="/dashboard" element={<DashboardContainer />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    const newChatButton = screen.getByTitle("Đoạn chat mới");
    fireEvent.click(newChatButton);

    expect(useReaderStore.getState().openDocumentIds).toEqual([]);
    expect(useReaderStore.getState().activeDocumentId).toBeNull();
    expect(useWorkspaceStore.getState().activeDocumentId).toBeNull();
  });
});
