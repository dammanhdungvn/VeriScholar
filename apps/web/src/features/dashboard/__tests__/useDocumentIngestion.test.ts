import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useDocumentIngestion } from "../hooks/useDocumentIngestion";
import { useWorkspaceStore } from "../stores/useWorkspaceStore";
import { dashboardApi } from "../api/dashboardApi";
import { documentsApi } from "@/features/documents/api/documentsApi";

vi.mock("../api/dashboardApi", () => ({
  dashboardApi: {
    createSession: vi.fn(),
  },
}));

vi.mock("@/features/documents/api/documentsApi", () => ({
  documentsApi: {
    uploadDocument: vi.fn(),
    parseDocument: vi.fn(),
    getStatus: vi.fn(),
  },
}));

describe("useDocumentIngestion Hook Cancellation", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useWorkspaceStore.getState().resetWorkspace();
  });

  it("aborts polling cleanly and returns null when workspace is reset to idle", async () => {
    vi.mocked(dashboardApi.createSession).mockResolvedValue({ id: "sess-cancel-1" } as any);
    vi.mocked(documentsApi.uploadDocument).mockResolvedValue({
      id: "doc-cancel-1",
      title: "Test Cancel Paper",
    } as any);
    vi.mocked(documentsApi.parseDocument).mockResolvedValue({ success: true } as any);

    // Mock getStatus to return parsing, then reset workspace on first poll
    let pollCount = 0;
    vi.mocked(documentsApi.getStatus).mockImplementation(async () => {
      pollCount++;
      if (pollCount === 1) {
        // Trigger cancel via workspace reset
        useWorkspaceStore.getState().resetWorkspace();
      }
      return { status: "parsing", progress: 50, stage: "chunking" } as any;
    });

    const { result } = renderHook(() =>
      useDocumentIngestion({ pollingIntervalMs: 10, minDurationMs: 10 })
    );

    const testFile = new File(["dummy pdf content"], "cancel_test.pdf", {
      type: "application/pdf",
    });

    let ingestResult: any;
    await act(async () => {
      ingestResult = await result.current.ingest(testFile);
    });

    // Should return null upon cancellation
    expect(ingestResult).toBeNull();
    // Workspace state should remain idle
    expect(useWorkspaceStore.getState().documentStatus).toBe("idle");
    // Polling should have stopped immediately without continuing to max attempts
    expect(pollCount).toBe(1);
  });
});
