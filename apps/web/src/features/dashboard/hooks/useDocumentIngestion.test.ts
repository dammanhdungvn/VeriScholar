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

    expect(dashboardApi.createSession).toHaveBeenCalledWith({
      title: "Nghiên cứu: attention",
    });
    expect(documentsApi.uploadDocument).toHaveBeenCalledWith(validFile, mockSessionId);
    expect(documentsApi.parseDocument).toHaveBeenCalledWith(mockDocId, {
      chunk_size: 512,
      chunk_overlap: 50,
      extract_tables: true,
    });
    expect(documentsApi.getStatus).toHaveBeenCalledWith(mockDocId);

    const finalState = useWorkspaceStore.getState();
    expect(finalState.documentStatus).toBe("completed");
    expect(finalState.uploadProgress).toBe(100);
    expect(finalState.isStandby).toBe(false);
    expect(finalState.activeSessionId).toBe(mockSessionId);
    expect(finalState.activeDocumentId).toBe(mockDocId);
  });

  it("invokes onSessionCreated callback immediately when session is created before file processing", async () => {
    const mockDocId = "doc-999";
    const mockSessionId = "sess-888";

    vi.mocked(dashboardApi.createSession).mockResolvedValueOnce({
      id: mockSessionId,
      title: "Nghiên cứu: paper",
      document_ids: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      version: 1,
      viewport_state: { page: 1, zoom_ratio: 1.0, scroll_top: 0 },
      active_tab: "chat",
      is_archived: false,
    });

    vi.mocked(documentsApi.uploadDocument).mockResolvedValueOnce({
      id: mockDocId,
      filename: "paper.pdf",
      file_size_bytes: 1024,
      status: "uploaded",
      stage: "queued",
      session_id: mockSessionId,
      is_duplicate: false,
      title: "Paper Title",
    });

    vi.mocked(documentsApi.parseDocument).mockResolvedValueOnce({
      id: mockDocId,
      status: "processing",
      stage: "validation",
      progress: 0,
    });

    vi.mocked(documentsApi.getStatus).mockResolvedValueOnce({
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

    const onSessionCreated = vi.fn();
    const { result } = renderHook(() => useDocumentIngestion({ pollingIntervalMs: 10 }));
    const validFile = new File(["%PDF-1.5 test"], "paper.pdf", { type: "application/pdf" });

    await act(async () => {
      await result.current.ingest(validFile, onSessionCreated);
    });

    expect(dashboardApi.createSession).toHaveBeenCalled();
    expect(onSessionCreated).toHaveBeenCalledWith(mockSessionId);
    expect(documentsApi.uploadDocument).toHaveBeenCalledWith(validFile, mockSessionId);
  });

  it("reuses existingSessionId and skips createSession when session already exists", async () => {
    const mockDocId = "doc-reuse-123";
    const existingSessionId = "sess-existing-456";

    vi.mocked(documentsApi.uploadDocument).mockResolvedValueOnce({
      id: mockDocId,
      filename: "multi_paper.pdf",
      file_size_bytes: 4096,
      status: "uploaded",
      stage: "queued",
      session_id: existingSessionId,
      is_duplicate: false,
      title: "Multi Paper",
    });

    vi.mocked(documentsApi.parseDocument).mockResolvedValueOnce({
      id: mockDocId,
      status: "processing",
      stage: "validation",
      progress: 0,
    });

    vi.mocked(documentsApi.getStatus).mockResolvedValueOnce({
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
    const validFile = new File(["%PDF-1.5 test"], "multi_paper.pdf", { type: "application/pdf" });

    await act(async () => {
      await result.current.ingest(validFile, undefined, existingSessionId);
    });

    // Must NOT create a redundant session
    expect(dashboardApi.createSession).not.toHaveBeenCalled();
    // Must pass existing session ID to document upload
    expect(documentsApi.uploadDocument).toHaveBeenCalledWith(validFile, existingSessionId);
    expect(documentsApi.parseDocument).toHaveBeenCalledWith(mockDocId, {
      chunk_size: 512,
      chunk_overlap: 50,
      extract_tables: true,
    });
  });
});
