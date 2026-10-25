import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { WritingWorkspace } from "./WritingWorkspace";
import { useWritingStore } from "../stores/useWritingStore";

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
    expect(screen.getByText("AI Writing Assistant")).toBeInTheDocument();
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
    expect(screen.queryByText("AI Writing Assistant")).toBeNull();

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
    expect(screen.getByText("AI Writing Assistant")).toBeInTheDocument();

    // Verify assistantPrompt was updated in the store with XML context tags
    const storePrompt = useWritingStore.getState().assistantPrompt;
    expect(storePrompt).toContain("<pre_context>");
    expect(storePrompt).toContain("\\section{Intro}");
    expect(storePrompt).toContain("<target_selection>");
    expect(storePrompt).toContain(target);
    expect(storePrompt).toContain("<post_context>");
    expect(storePrompt).toContain("\\section{Methods}");
  });

  it("triggers assistDraft and inserts suggested text into editor content", async () => {
    const { draftsApi } = await import("../api/draftsApi");

    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    // Type a prompt in the assistant pane input
    const input = screen.getByPlaceholderText(/Yêu cầu AI viết tiếp hoặc sửa văn phong/i);
    fireEvent.change(input, { target: { value: "Viết thêm phần thảo luận về attention" } });

    const sendBtn = screen.getByTitle("Gửi prompt");
    await act(async () => {
      fireEvent.click(sendBtn);
    });

    expect(draftsApi.assistDraft).toHaveBeenCalledWith(
      "draft-1",
      expect.objectContaining({
        prompt: "Viết thêm phần thảo luận về attention",
      })
    );

    expect(useWritingStore.getState().editorContent).toContain(
      "Attention mechanisms provide direct modeling."
    );
  });

  it("opens DraftAssetManagementModal when clicking Assets button in Tools dropdown", async () => {
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

  it("renders Overleaf layout: Left Taskbar, File Tree & Outline Sidebar, and Draggable Splitters", () => {
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
    useWritingStore.getState().setWorkspaceMode("tri-pane");
    render(
      <BrowserRouter>
        <WritingWorkspace />
      </BrowserRouter>
    );

    const closeBtn = screen.getByTestId("close-assistant-pane-btn");
    expect(closeBtn).toBeInTheDocument();
    expect(screen.queryByTestId("floating-ai-chat-bubble")).toBeNull();

    await act(async () => {
      fireEvent.click(closeBtn);
    });
    expect(useWritingStore.getState().workspaceMode).toBe("dual-code");
    expect(screen.queryByTestId("close-assistant-pane-btn")).toBeNull();

    const floatingBubble = screen.getByTestId("floating-ai-chat-bubble");
    expect(floatingBubble).toBeInTheDocument();

    await act(async () => {
      fireEvent.click(floatingBubble);
    });
    expect(useWritingStore.getState().workspaceMode).toBe("tri-pane");
    expect(screen.getByTestId("close-assistant-pane-btn")).toBeInTheDocument();
    expect(screen.queryByTestId("floating-ai-chat-bubble")).toBeNull();
  });
});
