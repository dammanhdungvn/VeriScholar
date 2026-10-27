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

vi.mock("@/features/documents/api/documentsApi", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/features/documents/api/documentsApi")>();
  return {
    ...actual,
    documentsApi: {
      ...actual.documentsApi,
      uploadDocument: vi.fn(),
      parseDocument: vi.fn(),
      getDocumentFileUrl: vi.fn().mockReturnValue("http://localhost:8000/mock.pdf"),
    },
  };
});

import { useState } from "react";

const mockSendMessage = vi.fn();
const mockLoadExistingSession = vi.fn();

vi.mock("../hooks/useStreamingChat", () => ({
  useStreamingChat: () => {
    const [text, setText] = useState("");
    return {
      messages: [],
      inputText: text,
      setInputText: setText,
      isGenerating: false,
      sendMessage: mockSendMessage,
      stopGeneration: vi.fn(),
      resetChat: vi.fn(),
      loadExistingSession: mockLoadExistingSession,
    };
  },
}));

const mockIngest = vi.fn();

vi.mock("../hooks/useDocumentIngestion", () => ({
  useDocumentIngestion: () => ({
    ingest: mockIngest,
  }),
}));

vi.mock("@/features/sessions/hooks/useSessionsQuery", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/features/sessions/hooks/useSessionsQuery")>();
  return {
    ...actual,
    useSessionDetail: () => ({ data: null }),
    useRestoreArchivedSessionMutation: () => ({ mutateAsync: vi.fn() }),
    useUpdateSessionMetadataMutation: () => ({ mutateAsync: vi.fn() }),
    useAddSessionDocumentMutation: () => ({ mutateAsync: vi.fn() }),
    useUpdateSessionViewportMutation: () => ({ mutateAsync: vi.fn() }),
    useDeleteSessionMutation: () => ({ mutateAsync: vi.fn() }),
  };
});

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

  it("handles multi-file staging (3 files) and dispatches prompt to the created session with all tabs opened", async () => {
    const { documentsApi } = await import("@/features/documents/api/documentsApi");
    const { useReaderStore } = await import("@/features/reader/stores/useReaderStore");

    mockIngest.mockResolvedValueOnce({
      sessionId: "session-multi-123",
      documentId: "doc-1",
    });

    (documentsApi.uploadDocument as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce({ id: "doc-2", title: "Paper 2" })
      .mockResolvedValueOnce({ id: "doc-3", title: "Paper 3" });

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/dashboard"]}>
          <DashboardContainer />
        </MemoryRouter>
      </QueryClientProvider>
    );

    // Switch to 'Nghiên cứu' (chat) mode tab
    const researchTab = screen.getByRole("button", { name: /Nghiên cứu/i });
    fireEvent.click(researchTab);

    // Drop 3 PDF files onto the input container
    const dropContainer = screen.getByTestId("chat-input-pill-container");
    const file1 = new File(["pdf1"], "paper1.pdf", { type: "application/pdf" });
    const file2 = new File(["pdf2"], "paper2.pdf", { type: "application/pdf" });
    const file3 = new File(["pdf3"], "paper3.pdf", { type: "application/pdf" });

    fireEvent.drop(dropContainer, {
      dataTransfer: {
        files: [file1, file2, file3],
      },
    });

    // Enter prompt "summay these paper"
    const textarea = screen.getByPlaceholderText(/Đặt câu hỏi nghiên cứu/i);
    fireEvent.change(textarea, { target: { value: "summay these paper" } });

    // Press Enter to submit
    fireEvent.keyDown(textarea, { key: "Enter", shiftKey: false });

    // File 1 must be ingested
    expect(mockIngest).toHaveBeenCalledWith(file1, expect.any(Function), undefined);

    // Files 2 and 3 must also be uploaded to the session
    await vi.waitFor(() => {
      expect(documentsApi.uploadDocument).toHaveBeenCalledWith(file2, "session-multi-123", true);
      expect(documentsApi.uploadDocument).toHaveBeenCalledWith(file3, "session-multi-123", true);
    });

    // useReaderStore must have all 3 document IDs opened
    await vi.waitFor(() => {
      expect(useReaderStore.getState().openDocumentIds).toEqual(["doc-1", "doc-2", "doc-3"]);
    });

    // Prompt must be sent directly with targetSessionId
    await vi.waitFor(() => {
      expect(mockSendMessage).toHaveBeenCalledWith("summay these paper", undefined, "session-multi-123");
    });
  });
});
