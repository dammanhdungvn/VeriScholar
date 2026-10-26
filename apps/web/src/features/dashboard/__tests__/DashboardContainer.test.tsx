import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DashboardContainer } from "../components/DashboardContainer";
import { useWorkspaceStore } from "../stores/useWorkspaceStore";
import { useDashboardStore } from "../stores/useDashboardStore";

vi.mock("../components/DashboardAmbientBackground", () => ({
  DashboardAmbientBackground: () => <div data-testid="ambient-bg" />,
}));

vi.mock("../hooks/useDashboardSessions", () => ({
  useDashboardSessions: () => ({
    sessions: [],
    activeSession: null,
    selectSession: vi.fn(),
    createSession: vi.fn(),
  }),
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

vi.mock("../hooks/useDocumentIngestion", () => ({
  useDocumentIngestion: () => ({
    ingest: vi.fn(),
  }),
}));

vi.mock("@/features/sessions/hooks/useSessionsQuery", () => ({
  useSessionDetail: () => ({ data: null }),
  useRestoreArchivedSessionMutation: () => ({ mutateAsync: vi.fn() }),
}));

describe("DashboardContainer handleNewSession", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    useWorkspaceStore.getState().resetWorkspace();
    useDashboardStore.setState({ activeSessionId: undefined });
  });

  it("resets workspace store including pending parsing status when 'Đoạn chat mới' is clicked", () => {
    // Put workspace into processing/parsing state with progress
    useWorkspaceStore.setState({
      activeSessionId: "sess-test",
      activeDocumentId: "doc-test",
      documentTitle: "Active Research Paper",
      documentStatus: "parsing",
      uploadProgress: 94,
      statusStage: "Đang phân tích cấu trúc...",
      isStandby: false,
    });

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/dashboard"]}>
          <DashboardContainer />
        </MemoryRouter>
      </QueryClientProvider>
    );

    // Verify taskbar new session button is present
    const newChatButton = screen.getByTitle("Đoạn chat mới");
    expect(newChatButton).toBeInTheDocument();

    // Click "Đoạn chat mới"
    fireEvent.click(newChatButton);

    // Workspace store must be completely reset to initial idle standby state
    const workspaceState = useWorkspaceStore.getState();
    expect(workspaceState.documentStatus).toBe("idle");
    expect(workspaceState.uploadProgress).toBe(0);
    expect(workspaceState.statusStage).toBeNull();
    expect(workspaceState.activeDocumentId).toBeNull();
    expect(workspaceState.activeSessionId).toBeNull();
    expect(workspaceState.isStandby).toBe(true);
  });
});
