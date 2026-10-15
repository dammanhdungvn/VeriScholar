import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { WritingWorkspace } from "./WritingWorkspace";
import { useWritingStore } from "../stores/useWritingStore";

// Mock draftsApi
vi.mock("../api/draftsApi", () => ({
  draftsApi: {
    getPreviewPdfBlob: vi.fn().mockResolvedValue(new Blob(["mock-pdf"], { type: "application/pdf" })),
    getPreviewPdfUrl: vi.fn((id: string) => `http://localhost:8000/api/v1/drafts/${id}/preview.pdf`),
    updateDraft: vi.fn().mockImplementation((id, payload) =>
      Promise.resolve({
        id,
        user_id: "user-1",
        title: payload.title,
        content: payload.content,
        format: payload.format,
        version: payload.version + 1,
        created_at: "2026-10-15T00:00:00Z",
        updated_at: "2026-10-15T00:00:00Z",
      })
    ),
    assistDraft: vi.fn().mockResolvedValue({
      draft_id: "draft-1",
      prompt: "Viết thêm phần thảo luận về attention",
      original_text: "",
      suggested_text: "\n% AI Generated Discussion\nAttention mechanisms provide direct modeling.",
      explanation: "Bổ sung thảo luận",
      confidence_score: 0.95,
      suggested_at: "2026-10-15T10:30:00Z",
    }),
    verifyFacts: vi.fn().mockResolvedValue({
      draft_id: "draft-1",
      verified_text: "Content",
      claims: [],
      total_claims: 0,
      supported_claims: 0,
      contradicted_claims: 0,
      unverified_claims: 0,
      supported_ratio: 0,
      latency_ms: 50,
      verified_at: "2026-10-15T00:00:00Z",
    }),
    listAssets: vi.fn().mockResolvedValue({
      draft_id: "draft-1",
      items: [],
      total: 0,
    }),
    createAsset: vi.fn().mockResolvedValue({
      id: "a-1",
      draft_id: "draft-1",
      asset_type: "image",
      filename: "test.png",
      file_size_bytes: 100,
      storage_url: "/files/test.png",
      created_at: "2026-10-15T00:00:00Z",
    }),
    getShareSettings: vi.fn().mockResolvedValue({
      draft_id: "draft-1",
      share_token: "tok-1",
      share_url: "http://localhost:5173/share/tok-1",
      permission: "editor",
      allow_public_link: false,
      collaborators: [],
    }),
    shareDraft: vi.fn().mockResolvedValue({
      draft_id: "draft-1",
      share_token: "tok-1",
      share_url: "http://localhost:5173/share/tok-1",
      permission: "editor",
      allow_public_link: true,
      collaborators: [],
    }),
  },
}));

describe("WritingWorkspace", () => {
  beforeEach(() => {
    useWritingStore.getState().reset();
    useWritingStore.getState().setDraft({
      id: "draft-1",
      user_id: "user-1",
      title: "Self-Attention In Transformers",
      content: "\\section{Intro}\nTransformers replace recurrent networks completely.\n\\section{Methods}",
      format: "latex",
      version: 1,
      created_at: "2026-10-15T00:00:00Z",
      updated_at: "2026-10-15T00:00:00Z",
    });
  });

  it("renders tri-pane workspace with header bar, editor, preview, and assistant", () => {
    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    expect(screen.getByText("Self-Attention In Transformers")).toBeDefined();
    expect(screen.getByText("main.tex")).toBeDefined();
    expect(screen.getByText("Bản Dựng PDF Trực Tiếp")).toBeDefined();
    expect(screen.getByText("SAFE Fact-Checking")).toBeDefined();
  });

  it("forwards selection context buffer into assistant chat and switches dual-code to tri-pane", async () => {
    // Start in dual-code mode (where assistant is initially hidden)
    useWritingStore.getState().setWorkspaceMode("dual-code");

    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    // In dual-code mode, AI assistant header is not visible initially
    expect(screen.queryByText("SAFE Fact-Checking")).toBeNull();

    const textarea = screen.getByRole("textbox") as HTMLTextAreaElement;
    const content = useWritingStore.getState().editorContent;
    const target = "Transformers replace recurrent networks completely.";
    const start = content.indexOf(target);
    const end = start + target.length;

    textarea.selectionStart = start;
    textarea.selectionEnd = end;
    fireEvent.select(textarea);

    const addToChatBtn = screen.getByRole("button", { name: /Thêm vào Chat/i });
    expect(addToChatBtn).toBeDefined();

    // Click [Thêm vào Chat]
    await act(async () => {
      fireEvent.click(addToChatBtn);
    });

    // Verify workspaceMode automatically transitioned to tri-pane so assistant is revealed
    expect(useWritingStore.getState().workspaceMode).toBe("tri-pane");
    expect(screen.getByText("SAFE Fact-Checking")).toBeDefined();

    // Verify assistantPrompt was updated in the store with XML context tags
    const storePrompt = useWritingStore.getState().assistantPrompt;
    expect(storePrompt).toContain("<pre_context>");
    expect(storePrompt).toContain("\\section{Intro}");
    expect(storePrompt).toContain("<target_selection>");
    expect(storePrompt).toContain(target);
    expect(storePrompt).toContain("<post_context>");
    expect(storePrompt).toContain("\\section{Methods}");
  });

  it("renders SourceEvidenceModal when an evidence claim is opened from the workspace", () => {
    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    expect(screen.queryByRole("dialog", { name: /Chi tiết dẫn chứng bài báo nguồn/i })).toBeNull();

    act(() => {
      useWritingStore.getState().openEvidenceModal({
        id: "claim-open-1",
        claim_text: "Direct attention connections preserve gradients.",
        normalized_entities: ["attention"],
        status: "supported",
        confidence_score: 0.96,
        evidence_document_id: "doc-123",
        evidence_document_title: "Attention Is All You Need",
        evidence_page: 4,
        evidence_bounding_boxes: [[0.1, 0.2, 0.8, 0.4, 4]],
      });
    });

    const modal = screen.getByRole("dialog", { name: /Chi tiết dẫn chứng bài báo nguồn/i });
    expect(modal).toBeDefined();
    expect(screen.getByText(/Attention Is All You Need/i)).toBeDefined();
    expect(screen.getByTestId("source-evidence-bbox-overlay")).toBeDefined();
  });

  it("triggers assistDraft without overwriting editor content and opens SuggestionReviewPanel", async () => {
    const { draftsApi } = await import("../api/draftsApi");

    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    const initialContent = useWritingStore.getState().editorContent;

    // Type a prompt in the assistant pane input
    const input = screen.getByPlaceholderText(/Yêu cầu AI viết tiếp hoặc sửa văn phong/i);
    fireEvent.change(input, { target: { value: "Viết thêm phần thảo luận về attention" } });

    const sendBtn = screen.getByTitle("Gửi prompt");
    await act(async () => {
      fireEvent.click(sendBtn);
    });

    // Check that assistDraft was called with draft ID and payload
    expect(draftsApi.assistDraft).toHaveBeenCalledWith(
      "draft-1",
      expect.objectContaining({
        prompt: "Viết thêm phần thảo luận về attention",
      })
    );

    // CRITICAL: Active editor content must NOT be directly modified/overwritten!
    expect(useWritingStore.getState().editorContent).toBe(initialContent);

    // SuggestionReviewPanel must be rendered
    expect(screen.getByTestId("suggestion-review-panel")).toBeInTheDocument();
    expect(screen.getByText("Xem xét đề xuất AI Assistant")).toBeInTheDocument();
    expect(screen.getByText("95% tin cậy")).toBeInTheDocument();
  });

  it("accepts suggestion with OCC ETag guard (If-Match: v1) and inserts text into editor content", async () => {
    const { draftsApi } = await import("../api/draftsApi");

    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    // Simulate an open suggestion in store
    act(() => {
      useWritingStore.getState().openSuggestionPanel({
        id: "sugg-1",
        draft_id: "draft-1",
        prompt: "Viết thêm phần thảo luận về attention",
        original_text: "",
        suggested_text: "\n% AI Generated Discussion\nAttention mechanisms provide direct modeling.",
        explanation: "Bổ sung thảo luận",
        confidence_score: 0.95,
        cursor_start: 15,
        cursor_end: 15,
        expected_version: 1,
        created_at: "2026-10-15T10:30:00Z",
      });
    });

    expect(screen.getByTestId("suggestion-review-panel")).toBeInTheDocument();

    const acceptBtn = screen.getByTestId("accept-suggestion-btn");
    await act(async () => {
      fireEvent.click(acceptBtn);
    });

    // Verify updateDraft was called with OCC If-Match header 'v1'
    expect(draftsApi.updateDraft).toHaveBeenCalledWith(
      "draft-1",
      expect.objectContaining({
        content: expect.stringContaining("Attention mechanisms provide direct modeling."),
        version: 1,
      }),
      "v1"
    );

    // Verify draft was saved and suggestion panel closed
    expect(useWritingStore.getState().isSuggestionPanelOpen).toBe(false);
    expect(useWritingStore.getState().draft?.version).toBe(2);
    expect(useWritingStore.getState().editorContent).toContain(
      "Attention mechanisms provide direct modeling."
    );
  });

  it("rejects suggestion without touching editor content", async () => {
    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    const initialContent = useWritingStore.getState().editorContent;

    act(() => {
      useWritingStore.getState().openSuggestionPanel({
        id: "sugg-2",
        draft_id: "draft-1",
        prompt: "Viết thêm phần thảo luận về attention",
        original_text: "",
        suggested_text: "\n% Dangerous overwrite\nSomething bad.",
        explanation: "Thử nghiệm",
        confidence_score: 0.95,
        cursor_start: 10,
        cursor_end: 10,
        expected_version: 1,
        created_at: "2026-10-15T10:30:00Z",
      });
    });

    expect(screen.getByTestId("suggestion-review-panel")).toBeInTheDocument();

    const rejectBtn = screen.getByTestId("reject-suggestion-btn");
    act(() => {
      fireEvent.click(rejectBtn);
    });

    // Panel is closed
    expect(useWritingStore.getState().isSuggestionPanelOpen).toBe(false);
    expect(screen.queryByTestId("suggestion-review-panel")).toBeNull();

    // Editor content is completely untouched!
    expect(useWritingStore.getState().editorContent).toBe(initialContent);
  });

  it("opens DraftAssetManagementModal when clicking Assets button or setting store state", async () => {
    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    expect(screen.queryByTestId("draft-assets-modal")).toBeNull();

    const assetsBtn = screen.getByTestId("header-assets-btn");
    await act(async () => {
      fireEvent.click(assetsBtn);
    });

    expect(screen.getByTestId("draft-assets-modal")).toBeInTheDocument();
  });

  it("opens DraftSharingModal when clicking Share button or setting store state", async () => {
    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    expect(screen.queryByTestId("draft-sharing-modal")).toBeNull();

    const shareBtn = screen.getByTestId("header-share-btn");
    await act(async () => {
      fireEvent.click(shareBtn);
    });

    expect(screen.getByTestId("draft-sharing-modal")).toBeInTheDocument();
  });
});
