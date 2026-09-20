import { describe, it, expect, beforeEach, vi } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useDocumentIngestion } from "./useDocumentIngestion";
import { useWorkspaceStore } from "../stores/useWorkspaceStore";
import { documentsApi } from "@/features/documents/api/documentsApi";
import { dashboardApi } from "../api/dashboardApi";

vi.mock("@/features/documents/api/documentsApi", () => ({
  documentsApi: {
    uploadDocument: vi.fn(),
    parseDocument: vi.fn(),
    getStatus: vi.fn(),
    getSummary: vi.fn(),
  },
}));

vi.mock("../api/dashboardApi", () => ({
  dashboardApi: {
    createSession: vi.fn(),
  },
}));

describe("useDocumentIngestion Hook (TDD)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useWorkspaceStore.getState().resetWorkspace();
  });

  it("rejects non-PDF files immediately at client layer without network calls", async () => {
    const { result } = renderHook(() => useDocumentIngestion());
    const invalidFile = new File(["test content"], "report.docx", {
      type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    });

    await act(async () => {
      await expect(result.current.ingest(invalidFile)).rejects.toThrow(
        /Chỉ chấp nhận tệp định dạng PDF/i
      );
    });

    expect(documentsApi.uploadDocument).not.toHaveBeenCalled();
    expect(useWorkspaceStore.getState().documentStatus).toBe("error");
    expect(useWorkspaceStore.getState().errorMessage).toMatch(/Chỉ chấp nhận tệp định dạng PDF/i);
  });

  it("rejects files exceeding 50MB size limit without network calls", async () => {
    const { result } = renderHook(() => useDocumentIngestion());
    // Mock 51MB file
    const oversizedFile = new File(["x"], "huge_book.pdf", { type: "application/pdf" });
    Object.defineProperty(oversizedFile, "size", { value: 55 * 1024 * 1024 });

    await act(async () => {
      await expect(result.current.ingest(oversizedFile)).rejects.toThrow(
        /Dung lượng tệp vượt quá giới hạn 50MB/i
      );
    });

    expect(documentsApi.uploadDocument).not.toHaveBeenCalled();
    expect(useWorkspaceStore.getState().documentStatus).toBe("error");
    expect(useWorkspaceStore.getState().errorMessage).toMatch(/50MB/i);
  });

  it("orchestrates upload -> lazy session -> parse -> poll -> complete successfully", async () => {
    const mockDocId = "doc-1111-2222";
    const mockSessionId = "sess-3333-4444";

    vi.mocked(documentsApi.uploadDocument).mockResolvedValueOnce({
      id: mockDocId,
      filename: "attention.pdf",
      file_size_bytes: 2048,
      status: "uploaded",
      stage: "queued",
      session_id: null,
      is_duplicate: false,
      title: "Attention Is All You Need",
    });

    vi.mocked(dashboardApi.createSession).mockResolvedValueOnce({
      id: mockSessionId,
      title: "Attention Is All You Need",
      document_ids: [mockDocId],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      version: 1,
      viewport_state: { page: 1, zoom_ratio: 1.0, scroll_top: 0 },
      active_tab: "chat",
      is_archived: false,
    });

    vi.mocked(documentsApi.parseDocument).mockResolvedValueOnce({
      id: mockDocId,
      status: "processing",
      stage: "validation",
      progress: 0,
    });

    // Polling status: first processing, then completed
    vi.mocked(documentsApi.getStatus)
      .mockResolvedValueOnce({
        id: mockDocId,
        status: "processing",
        stage: "ocr",
        progress: 50,
        stages_detail: {
          validation: "completed",
          layout_detection: "completed",
          ocr: "in_progress",
          chunking: "pending",
          embedding: "pending",
        },
      })
      .mockResolvedValueOnce({
        id: mockDocId,
        status: "completed",
        stage: "completed",
        progress: 100,
        stages_detail: {
          validation: "completed",
          layout_detection: "completed",
          ocr: "completed",
          chunking: "completed",
          embedding: "completed",
        },
      });

    const { result } = renderHook(() => useDocumentIngestion({ pollingIntervalMs: 10 }));
    const validFile = new File(["%PDF-1.5 test"], "attention.pdf", { type: "application/pdf" });

    await act(async () => {
      await result.current.ingest(validFile);
    });

    expect(documentsApi.uploadDocument).toHaveBeenCalledWith(validFile);
    expect(dashboardApi.createSession).toHaveBeenCalledWith({
      title: "Attention Is All You Need",
      initial_document_ids: [mockDocId],
    });
    expect(documentsApi.parseDocument).toHaveBeenCalledWith(mockDocId);
    expect(documentsApi.getStatus).toHaveBeenCalledWith(mockDocId);

    const finalState = useWorkspaceStore.getState();
    expect(finalState.documentStatus).toBe("completed");
    expect(finalState.uploadProgress).toBe(100);
    expect(finalState.isStandby).toBe(false);
    expect(finalState.activeSessionId).toBe(mockSessionId);
    expect(finalState.activeDocumentId).toBe(mockDocId);
  });
});
