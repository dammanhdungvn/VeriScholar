import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, screen, fireEvent, act, within } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { WritingWorkspace } from "./WritingWorkspace";
import { useWritingStore } from "../stores/useWritingStore";
import { draftsApi } from "../api/draftsApi";

// Mock draftsApi
vi.mock("../api/draftsApi", () => ({
  draftsApi: {
    compileDraft: vi.fn().mockResolvedValue({
      draft_id: "draft-1",
      success: true,
      pdf_preview_url: "http://localhost:8000/api/v1/drafts/draft-1/preview.pdf",
      errors: [],
      logs: "Compiled successfully",
      retries_attempted: 0,
    }),
    getPreviewPdfBlob: vi.fn().mockResolvedValue(new Blob(["mock-pdf"], { type: "application/pdf" })),
    getPreviewPdfUrl: vi.fn((id: string) => `http://localhost:8000/api/v1/drafts/${id}/preview.pdf`),
    getDraft: vi.fn().mockImplementation((id: string) =>
      Promise.resolve({
        id,
        user_id: "user-1",
        title: "Test Draft",
        content: "Test Content",
        format: "latex",
        version: 1,
        created_at: "2026-10-15T00:00:00Z",
        updated_at: "2026-10-15T00:00:00Z",
      })
    ),
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
    getComments: vi.fn().mockResolvedValue([]),
    createComment: vi.fn().mockResolvedValue({
      id: "c-1",
      draft_id: "draft-1",
      author_id: "u-1",
      author_name: "Author",
      start_offset: 0,
      end_offset: 10,
      selected_text: "Sample",
      comment_text: "Test comment",
      is_resolved: false,
      created_at: "2026-10-15T00:00:00Z",
      updated_at: "2026-10-15T00:00:00Z",
    }),
    updateComment: vi.fn().mockResolvedValue({}),
    deleteComment: vi.fn().mockResolvedValue(undefined),
    exportToOverleaf: vi.fn().mockResolvedValue({
      draft_id: "draft-1",
      title: "Test Draft",
      format: "latex",
      overleaf_url: "https://www.overleaf.com/docs?snip=mock",
      snip_length: 10,
      latex_snip: "% test",
    }),
    getAssociativeSuggestions: vi.fn().mockResolvedValue({
      draft_id: "draft-1",
      suggestions: [],
      total_found: 0,
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

    expect(screen.getByText("Self-Attention In Transformers")).toBeInTheDocument();
    expect(screen.getAllByText("main.tex")[0]).toBeInTheDocument();
    expect(screen.getByText("Bản Dựng PDF Trực Tiếp")).toBeInTheDocument();
    expect(screen.getByText("SAFE Fact-Checking")).toBeInTheDocument();
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

    const textarea = screen.getByTestId("writing-editor-textarea") as HTMLTextAreaElement;
    const content = useWritingStore.getState().editorContent;
    const target = "Transformers replace recurrent networks completely.";
    const start = content.indexOf(target);
    const end = start + target.length;

    textarea.selectionStart = start;
    textarea.selectionEnd = end;
    fireEvent.select(textarea);

    const addToChatBtn = screen.getByRole("button", { name: /Thêm vào Chat/i });
    expect(addToChatBtn).toBeInTheDocument();

    // Click [Thêm vào Chat]
    await act(async () => {
      fireEvent.click(addToChatBtn);
    });

    // Verify workspaceMode automatically transitioned to tri-pane so assistant is revealed
    expect(useWritingStore.getState().workspaceMode).toBe("tri-pane");
    expect(screen.getByText("SAFE Fact-Checking")).toBeInTheDocument();

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
    expect(modal).toBeInTheDocument();
    expect(within(modal).getByText(/Attention Is All You Need/i)).toBeInTheDocument();
    expect(screen.getByTestId("source-evidence-bbox-overlay")).toBeInTheDocument();
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

    // Open tools dropdown first
    const toolsBtn = screen.getByTestId("header-tools-dropdown");
    await act(async () => {
      fireEvent.click(toolsBtn);
    });

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

    // Open tools dropdown first
    const toolsBtn = screen.getByTestId("header-tools-dropdown");
    await act(async () => {
      fireEvent.click(toolsBtn);
    });

    const shareBtn = screen.getByTestId("header-share-btn");
    await act(async () => {
      fireEvent.click(shareBtn);
    });

    expect(screen.getByTestId("draft-sharing-modal")).toBeInTheDocument();
  });

  it("rebases offset and preserves user local edits typed before the suggestion range (DEFECT-01)", async () => {
    const { draftsApi } = await import("../api/draftsApi");

    const baseContent = "Transformers replace recurrent networks completely.";
    useWritingStore.getState().setDraft({
      id: "draft-1",
      user_id: "user-1",
      title: "Paper Title",
      content: baseContent,
      format: "latex",
      version: 1,
      created_at: "2026-10-15T00:00:00Z",
      updated_at: "2026-10-15T00:00:00Z",
    });

    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    const origStart = baseContent.indexOf("recurrent networks"); // 21
    const origEnd = origStart + "recurrent networks".length; // 39

    // Open suggestion generated against baseContent
    act(() => {
      useWritingStore.getState().openSuggestionPanel({
        id: "sugg-rebase-1",
        draft_id: "draft-1",
        prompt: "Refine phrasing",
        original_text: "recurrent networks",
        suggested_text: "sequential recurrent units",
        explanation: "Refined phrasing",
        confidence_score: 0.96,
        cursor_start: origStart,
        cursor_end: origEnd,
        expected_version: 1,
        created_at: "2026-10-15T10:30:00Z",
        base_content: baseContent,
      });
    });

    // While panel is open, user types "Recent advances: " at position 0
    act(() => {
      useWritingStore.getState().setEditorContent("Recent advances: " + baseContent);
    });

    const acceptBtn = screen.getByTestId("accept-suggestion-btn");
    await act(async () => {
      fireEvent.click(acceptBtn);
    });

    // Verify updateDraft received rebased content preserving "Recent advances: "
    expect(draftsApi.updateDraft).toHaveBeenCalledWith(
      "draft-1",
      expect.objectContaining({
        content: "Recent advances: Transformers replace sequential recurrent units completely.",
        version: 1,
      }),
      "v1"
    );

    // Verify local editorContent is also updated correctly
    expect(useWritingStore.getState().editorContent).toBe(
      "Recent advances: Transformers replace sequential recurrent units completely."
    );
  });

  it("handles HTTP 412 Precondition Failed gracefully, shows conflict alert banner, and preserves local unpersisted edits (DEFECT-01 / FINDING-01 & 04)", async () => {
    const { draftsApi } = await import("../api/draftsApi");

    const baseContent = "Transformers replace recurrent networks completely.";
    useWritingStore.getState().setDraft({
      id: "draft-1",
      user_id: "user-1",
      title: "Paper Title",
      content: baseContent,
      format: "latex",
      version: 1,
      created_at: "2026-10-15T00:00:00Z",
      updated_at: "2026-10-15T00:00:00Z",
    });

    // Mock updateDraft to throw HTTP 412
    const error412 = new Error("HTTP 412 Precondition Failed");
    Object.assign(error412, { status: 412 });
    vi.mocked(draftsApi.updateDraft).mockRejectedValueOnce(error412);
    vi.mocked(draftsApi.getDraft).mockResolvedValueOnce({
      id: "draft-1",
      user_id: "user-1",
      title: "Paper Title",
      content: "Server modified content by another collaborator.",
      format: "latex",
      version: 2,
      created_at: "2026-10-15T00:00:00Z",
      updated_at: "2026-10-15T00:00:00Z",
    });

    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    act(() => {
      useWritingStore.getState().openSuggestionPanel({
        id: "sugg-412",
        draft_id: "draft-1",
        prompt: "Refine phrasing",
        original_text: "",
        suggested_text: "New text",
        confidence_score: 0.9,
        cursor_start: 0,
        cursor_end: 0,
        expected_version: 1,
        created_at: "2026-10-15T10:30:00Z",
        base_content: baseContent,
      });
    });

    // User types local unpersisted edits while suggestion is open
    const localEdits = "User typed unpersisted paragraph. " + baseContent;
    act(() => {
      useWritingStore.getState().setEditorContent(localEdits);
    });

    expect(useWritingStore.getState().isDirty).toBe(true);

    const acceptBtn = screen.getByTestId("accept-suggestion-btn");
    await act(async () => {
      fireEvent.click(acceptBtn);
    });

    // Conflict alert banner is rendered
    expect(screen.getByTestId("occ-conflict-alert")).toBeInTheDocument();
    expect(screen.getByText(/HTTP 412/i)).toBeInTheDocument();

    // Suggestion panel remains open so user does not lose proposal
    expect(useWritingStore.getState().isSuggestionPanelOpen).toBe(true);

    // CRITICAL (FINDING-DEFECT-01-01 & 04): editorContent MUST NOT be overwritten by freshDraft.content!
    expect(useWritingStore.getState().editorContent).toBe(localEdits);
    expect(useWritingStore.getState().isDirty).toBe(true);

    // Draft metadata version is refreshed so subsequent save uses v2
    expect(useWritingStore.getState().draft?.version).toBe(2);

    // Dismiss alert banner
    const closeAlertBtn = screen.getByTestId("close-conflict-alert-btn");
    act(() => {
      fireEvent.click(closeAlertBtn);
    });
    expect(screen.queryByTestId("occ-conflict-alert")).toBeNull();
  });

  it("prevents text corruption and displays conflict banner when original text was deleted/modified (FINDING-DEFECT-01-02)", async () => {
    const { draftsApi } = await import("../api/draftsApi");
    vi.mocked(draftsApi.updateDraft).mockClear();

    const baseContent = "Hello world, this is a test.";
    useWritingStore.getState().setDraft({
      id: "draft-1",
      user_id: "user-1",
      title: "Paper Title",
      content: baseContent,
      format: "latex",
      version: 1,
      created_at: "2026-10-15T00:00:00Z",
      updated_at: "2026-10-15T00:00:00Z",
    });

    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    // Open suggestion targeting "world" at [6, 11]
    act(() => {
      useWritingStore.getState().openSuggestionPanel({
        id: "sugg-conflict-del",
        draft_id: "draft-1",
        prompt: "Replace world",
        original_text: "world",
        suggested_text: "universe",
        confidence_score: 0.95,
        cursor_start: 6,
        cursor_end: 11,
        expected_version: 1,
        created_at: "2026-10-15T10:30:00Z",
        base_content: baseContent,
      });
    });

    // User deleted "world" in the editor
    const modifiedContent = "Hello , this is a test.";
    act(() => {
      useWritingStore.getState().setEditorContent(modifiedContent);
    });

    const acceptBtn = screen.getByTestId("accept-suggestion-btn");
    await act(async () => {
      fireEvent.click(acceptBtn);
    });

    // Conflict banner must be shown
    expect(screen.getByTestId("occ-conflict-alert")).toBeInTheDocument();
    expect(
      screen.getByText(/Văn bản gốc của đề xuất đã bị thay đổi hoặc không còn khớp/i)
    ).toBeInTheDocument();

    // updateDraft must NOT have been called
    expect(draftsApi.updateDraft).not.toHaveBeenCalled();

    // Editor content must NOT be mangled/corrupted
    expect(useWritingStore.getState().editorContent).toBe(modifiedContent);

    // Suggestion panel remains open
    expect(useWritingStore.getState().isSuggestionPanelOpen).toBe(true);
  });

  it("opens DraftCommentsPane when clicking Comments button in header or [💬 Nhận xét] in editor toolbar", async () => {
    const { container } = render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    expect(screen.queryByTestId("draft-comments-pane")).toBeNull();

    // 1. Open tools dropdown and click header comments button
    const toolsBtn = screen.getByTestId("header-tools-dropdown");
    await act(async () => {
      fireEvent.click(toolsBtn);
    });

    const commentsBtn = screen.getByTestId("header-comments-btn");
    await act(async () => {
      fireEvent.click(commentsBtn);
    });

    expect(screen.getByTestId("draft-comments-pane")).toBeInTheDocument();

    // Close pane
    const closeBtn = screen.getByTestId("close-comments-pane-btn");
    await act(async () => {
      fireEvent.click(closeBtn);
    });
    expect(screen.queryByTestId("draft-comments-pane")).toBeNull();

    // 2. Select text in editor and click [💬 Nhận xét]
    const textarea = container.querySelector("textarea") as HTMLTextAreaElement;
    textarea.selectionStart = 0;
    textarea.selectionEnd = 12;
    fireEvent.select(textarea);

    const addCommentBtn = screen.getByTestId("editor-add-comment-btn");
    await act(async () => {
      fireEvent.click(addCommentBtn);
    });

    expect(screen.getByTestId("draft-comments-pane")).toBeInTheDocument();
  });
});

describe("WritingWorkspace Associative Memory Integration", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    useWritingStore.getState().reset();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("starts with activeMemorySuggestion=null and unmounted card on blank drafts", async () => {
    useWritingStore.getState().setDraft({
      id: "draft-blank-1",
      user_id: "user-1",
      title: "Blank Draft",
      content: "",
      format: "latex",
      version: 1,
      created_at: "2026-10-16T00:00:00Z",
      updated_at: "2026-10-16T00:00:00Z",
    });

    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    expect(screen.queryByTestId("associative-memory-card")).toBeNull();

    act(() => {
      vi.advanceTimersByTime(1200);
    });

    expect(screen.queryByTestId("associative-memory-card")).toBeNull();
    expect(draftsApi.getAssociativeSuggestions).not.toHaveBeenCalled();
  });

  it("does not call associative suggestions API when draft content is shorter than 10 characters", async () => {
    useWritingStore.getState().setDraft({
      id: "draft-short-1",
      user_id: "user-1",
      title: "Short Draft",
      content: "   short   ",
      format: "latex",
      version: 1,
      created_at: "2026-10-16T00:00:00Z",
      updated_at: "2026-10-16T00:00:00Z",
    });

    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    act(() => {
      vi.advanceTimersByTime(1200);
    });

    expect(screen.queryByTestId("associative-memory-card")).toBeNull();
    expect(draftsApi.getAssociativeSuggestions).not.toHaveBeenCalled();
  });

  it("remains unmounted when draft text >= 10 chars produces 0 associative suggestions", async () => {
    vi.mocked(draftsApi.getAssociativeSuggestions).mockResolvedValueOnce({
      draft_id: "draft-empty-sugg",
      suggestions: [],
      total_found: 0,
    });

    useWritingStore.getState().setDraft({
      id: "draft-empty-sugg",
      user_id: "user-1",
      title: "Unmatched Research Topic",
      content: "This is a sufficiently long draft text discussing unrelated concepts.",
      format: "latex",
      version: 1,
      created_at: "2026-10-16T00:00:00Z",
      updated_at: "2026-10-16T00:00:00Z",
    });

    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    await act(async () => {
      vi.advanceTimersByTime(850);
    });

    expect(draftsApi.getAssociativeSuggestions).toHaveBeenCalledWith(
      "draft-empty-sugg",
      expect.objectContaining({
        content: "This is a sufficiently long draft text discussing unrelated concepts.",
        limit: 3,
      })
    );

    expect(screen.queryByTestId("associative-memory-card")).toBeNull();
  });

  it("mounts AssociativeMemoryCard when dynamic text matching notes is provided and API returns suggestions", async () => {
    vi.mocked(draftsApi.getAssociativeSuggestions).mockResolvedValue({
      draft_id: "draft-assoc-match",
      total_found: 1,
      suggestions: [
        {
          note_id: "note-attn-99",
          document_title: "Attention Is All You Need",
          paper_title: "Attention Is All You Need",
          page_number: 4,
          selected_text: "Multi-Head Attention replaces recurrence.",
          suggested_citation: "\\cite{vaswani2017attention}",
          user_note: "Multi-Head Attention removes recurrence completely.",
          similarity_score: 0.95,
          reason: "High lexical and semantic overlap with Transformer architecture",
          relevance_explanation: "Detailed explanation of attention mechanisms",
        },
      ],
    });

    useWritingStore.getState().setDraft({
      id: "draft-assoc-match",
      user_id: "user-1",
      title: "Draft on Transformers",
      content: "",
      format: "latex",
      version: 1,
      created_at: "2026-10-16T00:00:00Z",
      updated_at: "2026-10-16T00:00:00Z",
    });

    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    expect(screen.queryByTestId("associative-memory-card")).toBeNull();

    act(() => {
      useWritingStore
        .getState()
        .setEditorContent("We explore self-attention mechanisms in transformer networks.");
    });

    await act(async () => {
      vi.advanceTimersByTime(850);
    });

    const card = screen.getByTestId("associative-memory-card");
    expect(card).toBeInTheDocument();
    expect(screen.getByText("Attention Is All You Need")).toBeInTheDocument();
    expect(screen.getByText(/\(Trang 4\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Multi-Head Attention removes recurrence/i)).toBeInTheDocument();
    expect(screen.getByText("95%")).toBeInTheDocument();
  });

  it("inserts citation and unmounts card when [Chèn trích dẫn] is clicked", async () => {
    vi.mocked(draftsApi.getAssociativeSuggestions).mockResolvedValue({
      draft_id: "draft-insert-test",
      total_found: 1,
      suggestions: [
        {
          note_id: "note-flash-1",
          document_title: "FlashAttention: Fast and Memory-Efficient Exact Attention",
          paper_title: "FlashAttention: Fast and Memory-Efficient Exact Attention",
          page_number: 2,
          selected_text: "IO-aware exact attention tiling.",
          suggested_citation: "\\cite{dao2022flashattention}",
          user_note: "IO-aware exact attention tiling.",
          similarity_score: 0.93,
          reason: "IO-aware attention tiling speedup",
          relevance_explanation: "Tiling attention into SRAM blocks",
        },
      ],
    });

    const initialContent = "We implement IO-aware exact attention tiling for CUDA speedup.";
    useWritingStore.getState().setDraft({
      id: "draft-insert-test",
      user_id: "user-1",
      title: "Kernel Optimizations",
      content: initialContent,
      format: "latex",
      version: 1,
      created_at: "2026-10-16T00:00:00Z",
      updated_at: "2026-10-16T00:00:00Z",
    });

    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    await act(async () => {
      vi.advanceTimersByTime(850);
    });

    expect(screen.getByTestId("associative-memory-card")).toBeInTheDocument();

    const insertBtn = screen.getByTestId("insert-citation-btn");
    act(() => {
      fireEvent.click(insertBtn);
    });

    expect(screen.queryByTestId("associative-memory-card")).toBeNull();

    const currentContent = useWritingStore.getState().editorContent;
    expect(currentContent).toContain("\\cite{dao2022flashattention}");
    expect(currentContent).toBe(initialContent + " \\cite{dao2022flashattention} ");
  });

  it("unmounts card when user clicks dismiss close button", async () => {
    vi.mocked(draftsApi.getAssociativeSuggestions).mockResolvedValue({
      draft_id: "draft-dismiss-test",
      total_found: 1,
      suggestions: [
        {
          note_id: "note-lora-1",
          document_title: "LoRA: Low-Rank Adaptation of Large Language Models",
          paper_title: "LoRA: Low-Rank Adaptation of Large Language Models",
          page_number: 3,
          selected_text: "Freezes weights and injects low rank decomposition.",
          suggested_citation: "\\cite{hu2021lora}",
          user_note: "Freezes pre-trained weights and injects trainable rank decomposition matrices.",
          similarity_score: 0.88,
          reason: "Parameter-efficient adaptation",
          relevance_explanation: "Low-rank parameter matrix update decomposition",
        },
      ],
    });

    useWritingStore.getState().setDraft({
      id: "draft-dismiss-test",
      user_id: "user-1",
      title: "PEFT Survey",
      content: "Low-rank parameter efficient fine-tuning adaptations.",
      format: "latex",
      version: 1,
      created_at: "2026-10-16T00:00:00Z",
      updated_at: "2026-10-16T00:00:00Z",
    });

    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    await act(async () => {
      vi.advanceTimersByTime(850);
    });

    expect(screen.getByTestId("associative-memory-card")).toBeInTheDocument();

    const dismissBtn = screen.getByRole("button", { name: "Đóng gợi ý" });
    act(() => {
      fireEvent.click(dismissBtn);
    });

    expect(screen.queryByTestId("associative-memory-card")).toBeNull();
  });

  it("debounces rapid typing so API is only called once after typing stops", async () => {
    vi.mocked(draftsApi.getAssociativeSuggestions).mockResolvedValue({
      draft_id: "draft-debounce-test",
      total_found: 0,
      suggestions: [],
    });

    useWritingStore.getState().setDraft({
      id: "draft-debounce-test",
      user_id: "user-1",
      title: "Typing Test",
      content: "",
      format: "latex",
      version: 1,
      created_at: "2026-10-16T00:00:00Z",
      updated_at: "2026-10-16T00:00:00Z",
    });

    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    act(() => {
      useWritingStore.getState().setEditorContent("Initial typing...");
    });
    act(() => {
      vi.advanceTimersByTime(200);
    });

    act(() => {
      useWritingStore.getState().setEditorContent("Initial typing... continuing draft");
    });
    act(() => {
      vi.advanceTimersByTime(200);
    });

    act(() => {
      useWritingStore.getState().setEditorContent("Initial typing... continuing draft and finishing paragraph.");
    });

    expect(draftsApi.getAssociativeSuggestions).not.toHaveBeenCalled();

    await act(async () => {
      vi.advanceTimersByTime(850);
    });

    expect(draftsApi.getAssociativeSuggestions).toHaveBeenCalledTimes(1);
    expect(draftsApi.getAssociativeSuggestions).toHaveBeenCalledWith(
      "draft-debounce-test",
      expect.objectContaining({
        content: "Initial typing... continuing draft and finishing paragraph.",
      })
    );
  });

  it("gracefully catches and logs API errors without crashing UI", async () => {
    const consoleWarnSpy = vi.spyOn(console, "warn").mockImplementation(() => {});
    vi.mocked(draftsApi.getAssociativeSuggestions).mockRejectedValueOnce(
      new Error("Network timeout")
    );

    useWritingStore.getState().setDraft({
      id: "draft-error-test",
      user_id: "user-1",
      title: "Error Draft",
      content: "This is a valid long text that triggers an API call that fails.",
      format: "latex",
      version: 1,
      created_at: "2026-10-16T00:00:00Z",
      updated_at: "2026-10-16T00:00:00Z",
    });

    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    await act(async () => {
      vi.advanceTimersByTime(850);
    });

    expect(consoleWarnSpy).toHaveBeenCalledWith(
      "Failed to fetch proactive associative suggestions:",
      expect.any(Error)
    );
    expect(screen.queryByTestId("associative-memory-card")).toBeNull();

    consoleWarnSpy.mockRestore();
  });

  it("renders Overleaf layout: Left Icon Rail, File Tree & Outline Sidebar, and Draggable Splitters", () => {
    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    // 1. Inherited Taskbar from Dashboard
    expect(screen.getByRole("complementary", { name: /thanh điều hướng chính/i })).toBeInTheDocument();
    expect(screen.getByTitle("Đoạn chat mới")).toBeInTheDocument();
    expect(screen.getByTestId("toggle-file-tree-btn")).toBeInTheDocument();

    // 2. Sidebar with File Tree
    expect(screen.getByTestId("writing-sidebar")).toBeInTheDocument();
    expect(screen.getByTestId("sidebar-tab-files")).toBeInTheDocument();
    expect(screen.getByTestId("sidebar-tab-outline")).toBeInTheDocument();

    // 3. Resizable splitters
    expect(screen.getByTestId("sidebar-resizable-splitter")).toBeInTheDocument();
    expect(screen.getByTestId("editor-preview-splitter")).toBeInTheDocument();

    // 4. Toggle sidebar off and on
    const toggleBtn = screen.getByTestId("toggle-file-tree-btn");
    fireEvent.click(toggleBtn);
    expect(screen.queryByTestId("writing-sidebar")).toBeNull();

    fireEvent.click(toggleBtn);
    expect(screen.getByTestId("writing-sidebar")).toBeInTheDocument();
  });

  it("handles AI chat close button and floating bubble visibility toggling", async () => {
    // 1. In tri-pane mode: AI chat is visible, floating chat bubble and Do Anything are NOT visible
    useWritingStore.getState().setWorkspaceMode("tri-pane");
    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    // AI chat pane is shown with close button
    const closeBtn = screen.getByTestId("close-assistant-pane-btn");
    expect(closeBtn).toBeInTheDocument();
    // Floating chat bubble is not shown when chat is visible
    expect(screen.queryByTestId("floating-ai-chat-bubble")).toBeNull();

    // 2. Click X: hides AI chat and shows floating chat bubble
    await act(async () => {
      fireEvent.click(closeBtn);
    });
    expect(useWritingStore.getState().workspaceMode).toBe("dual-code");
    expect(screen.queryByTestId("close-assistant-pane-btn")).toBeNull();

    // Floating chat bubble is now visible
    const floatingBubble = screen.getByTestId("floating-ai-chat-bubble");
    expect(floatingBubble).toBeInTheDocument();

    // 3. Click floating chat bubble: reveals AI chat again and hides floating bubble
    await act(async () => {
      fireEvent.click(floatingBubble);
    });
    expect(useWritingStore.getState().workspaceMode).toBe("tri-pane");
    expect(screen.getByTestId("close-assistant-pane-btn")).toBeInTheDocument();
    expect(screen.queryByTestId("floating-ai-chat-bubble")).toBeNull();
  });
});

