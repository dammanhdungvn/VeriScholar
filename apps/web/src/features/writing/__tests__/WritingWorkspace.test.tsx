import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { WritingWorkspace } from "../components/WritingWorkspace";
import { useWritingStore } from "../stores/useWritingStore";
import { draftsApi } from "../api/draftsApi";
import type { Draft, DraftAssetListResponse, CompileDraftResponse } from "../types";

// Mock draftsApi
vi.mock("../api/draftsApi", () => ({
  draftsApi: {
    getDraft: vi.fn(),
    updateDraft: vi.fn(),
    compileDraft: vi.fn(),
    recompileClearCache: vi.fn(),
    undoDraft: vi.fn(),
    synctexForward: vi.fn(),
    synctexInverse: vi.fn(),
    streamDraftChat: vi.fn(),
    listAssets: vi.fn(),
    createAsset: vi.fn(),
    getPreviewPdfBlob: vi.fn(),
    getPreviewPdfUrl: vi.fn((id: string) => `/api/v1/drafts/${id}/preview.pdf`),
    exportBundle: vi.fn(),
    assistDraft: vi.fn(),
  },
}));

// Mock pdfjs-init
vi.mock("@/features/reader/lib/pdfjs-init", () => ({
  pdfjsLib: {
    getDocument: vi.fn().mockReturnValue({
      promise: Promise.resolve({
        numPages: 2,
        getPage: vi.fn().mockResolvedValue({
          getViewport: vi.fn().mockReturnValue({ width: 595.32, height: 841.92 }),
          render: vi.fn().mockReturnValue({
            promise: Promise.resolve(),
            cancel: vi.fn(),
          }),
        }),
      }),
    }),
  },
}));

// Mock Canvas getContext in jsdom
HTMLCanvasElement.prototype.getContext = vi.fn().mockReturnValue({
  setTransform: vi.fn(),
  scale: vi.fn(),
}) as any;

// Mock IntersectionObserver in jsdom
class MockIntersectionObserver {
  callback: any;
  observe = vi.fn((_el) => {
    this.callback([{ isIntersecting: true, intersectionRatio: 1.0 }], this);
  });
  unobserve = vi.fn();
  disconnect = vi.fn();
  constructor(callback: any) {
    this.callback = callback;
  }
}
window.IntersectionObserver = MockIntersectionObserver as any;
globalThis.IntersectionObserver = MockIntersectionObserver as any;

// Helper to render with MemoryRouter
const renderWithRouter = (ui: React.ReactElement) => render(<MemoryRouter>{ui}</MemoryRouter>);

describe("Overleaf-Parity Writing Workspace (Plan 06, Task 6)", () => {
  const mockDraft: Draft = {
    id: "draft-456",
    user_id: "user-123",
    title: "Deep Reinforcement Learning Survey",
    content: "\\documentclass{article}\n\\begin{document}\nHello World\n\\end{document}",
    bib_content: "@article{sample,\n  title={Sample},\n  year={2026}\n}",
    format: "latex",
    previous_snapshot: {
      undo: { content: "old" },
    },
    version: 3,
    created_at: "2026-10-25T10:00:00Z",
    updated_at: "2026-10-25T10:00:00Z",
  };

  beforeEach(() => {
    vi.clearAllMocks();
    useWritingStore.getState().reset();

    // Default mock returns
    vi.mocked(draftsApi.listAssets).mockResolvedValue({
      draft_id: "draft-456",
      items: [
        {
          id: "asset-1",
          draft_id: "draft-456",
          asset_type: "image",
          filename: "figures/pipeline_arch.png",
          file_size_bytes: 1024,
          storage_url: "/api/v1/drafts/draft-456/assets/asset-1/figures/pipeline_arch.png",
          caption: "Architecture",
          latex_label: "fig:pipeline",
          created_at: "2026-10-25T10:00:00Z",
        },
      ],
      total: 1,
    } as DraftAssetListResponse);

    vi.mocked(draftsApi.compileDraft).mockResolvedValue({
      draft_id: "draft-456",
      success: true,
      pdf_preview_url: "/api/v1/drafts/draft-456/preview.pdf",
      errors: [],
      logs: "Compiled successfully",
      retries_attempted: 0,
    } as CompileDraftResponse);

    vi.mocked(draftsApi.recompileClearCache).mockResolvedValue({
      draft_id: "draft-456",
      success: true,
      pdf_preview_url: "/api/v1/drafts/draft-456/preview.pdf",
      errors: [],
      logs: "Cache cleared and compiled clean",
      retries_attempted: 0,
    } as CompileDraftResponse);

    vi.mocked(draftsApi.getPreviewPdfBlob).mockResolvedValue(
      new Blob(["fake pdf content"], { type: "application/pdf" })
    );

    // Initialize store with test draft
    act(() => {
      useWritingStore.getState().setDraft(mockDraft);
    });
  });

  it("renders single smart Recompile button and removes bulky clear-cache action bar", async () => {
    renderWithRouter(<WritingWorkspace />);
    expect(screen.getByTestId("recompile-btn")).toBeInTheDocument();
    expect(screen.queryByText(/Bản Dựng PDF Trực Tiếp/i)).toBeNull();
    expect(screen.queryByText(/🧹 Xóa đệm & Dựng lại/i)).toBeNull();
  });

  it("renders Socratic Assistant floating action button at bottom right", async () => {
    renderWithRouter(<WritingWorkspace />);
    const fab = screen.getByTestId("writing-assistant-fab");
    expect(fab).toBeInTheDocument();
    fireEvent.click(fab);
    expect(screen.getByTestId("writing-assistant-drawer")).toBeInTheDocument();
  });

  it("1. Renders 2 columns workspace (Editor, PDF Preview) with Assistant in drawer", () => {
    renderWithRouter(<WritingWorkspace />);

    // Verify Editor & Preview are in the document
    expect(screen.getByTestId("writing-editor-textarea")).toBeInTheDocument();
    expect(screen.getByTestId("writing-preview-pane")).toBeInTheDocument();
    // Assistant FAB is present
    expect(screen.getByTestId("writing-assistant-fab")).toBeInTheDocument();
  });

  it("2. Supports file tab switching between main.tex and references.bib", () => {
    render(
      <MemoryRouter>
        <WritingWorkspace />
      </MemoryRouter>
    );

    const textarea = screen.getByTestId("writing-editor-textarea") as HTMLTextAreaElement;
    expect(textarea.value).toContain("\\documentclass{article}");

    // Click references.bib tab
    const bibTab = screen.getByTestId("editor-tab-bib");
    fireEvent.click(bibTab);

    // Textarea value should now show bib_content
    expect(textarea.value).toContain("@article{sample");

    // Edit references.bib
    fireEvent.change(textarea, { target: { value: "@article{modified,\n  title={Modified}\n}" } });
    expect(useWritingStore.getState().editorBibContent).toContain("@article{modified");

    // Switch back to main.tex
    const mainTab = screen.getByTestId("editor-tab-main");
    fireEvent.click(mainTab);
    expect(textarea.value).toContain("\\documentclass{article}");
  });

  it("3. File tree displays main.tex, references.bib, and figures/ assets", async () => {
    render(
      <MemoryRouter>
        <WritingWorkspace />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByTestId("file-main-tex")).toBeInTheDocument();
      expect(screen.getByTestId("file-references-bib")).toBeInTheDocument();
      expect(screen.getByText(/pipeline_arch\.png/i)).toBeInTheDocument();
    });
  });

  it("4. Action [Clear cache & Recompile] calls draftsApi.recompileClearCache", async () => {
    renderWithRouter(<WritingWorkspace />);

    // Click recompile dropdown trigger
    const dropdownTrigger = await screen.findByTestId("recompile-dropdown-trigger");
    fireEvent.click(dropdownTrigger);

    const clearCacheBtn = await screen.findByTestId("recompile-clear-cache-btn");
    expect(clearCacheBtn).toBeInTheDocument();

    await act(async () => {
      fireEvent.click(clearCacheBtn);
    });

    expect(draftsApi.recompileClearCache).toHaveBeenCalledWith("draft-456");
  });

  it("5. SyncTeX forward displays highlight box, and inverse search double-click jumps editor to file and line", async () => {
    vi.mocked(draftsApi.synctexInverse).mockResolvedValue({
      file: "main.tex",
      line: 42,
      col: 1,
    });

    render(
      <MemoryRouter>
        <WritingWorkspace />
      </MemoryRouter>
    );

    // Forward search test: manually set highlight box or trigger forward search
    act(() => {
      useWritingStore.getState().setActiveHighlightBox({
        page: 1,
        x: 72,
        y: 100,
        width: 400,
        height: 20,
      });
    });

    // Yellow highlight box should be present on page 1
    const highlightBox = await screen.findByTestId("synctex-highlight-box");
    expect(highlightBox).toBeInTheDocument();

    // Inverse search test: double-click on PDF page canvas container
    const previewPage1 = await screen.findByTestId("preview-page-1");
    await act(async () => {
      fireEvent.doubleClick(previewPage1, { clientX: 150, clientY: 200 });
    });

    expect(draftsApi.synctexInverse).toHaveBeenCalledWith("draft-456", 1, expect.any(Number), expect.any(Number));
  });

  it("6. AI Assistant Chat streams response and dynamically displays execution badges", async () => {
    vi.mocked(draftsApi.streamDraftChat).mockImplementation(async (_id, _prompt, callbacks) => {
      callbacks.onBadge?.("🔍 Tra cứu GraphRAG");
      callbacks.onBadge?.("⚙️ Biên dịch E2B");
      callbacks.onToken?.("Đang tối ưu cấu trúc bài báo...");
      callbacks.onComplete?.({
        main_tex: "\\documentclass{article}\n\\begin{document}\nPatched\n\\end{document}",
      });
    });

    renderWithRouter(<WritingWorkspace />);

    // Open assistant drawer via FAB
    fireEvent.click(screen.getByTestId("writing-assistant-fab"));

    const promptInput = screen.getByPlaceholderText(/Yêu cầu AI/i);
    fireEvent.change(promptInput, { target: { value: "Viết lại phần tóm tắt" } });

    const sendBtn = screen.getByTitle("Gửi prompt");
    await act(async () => {
      fireEvent.click(sendBtn);
    });

    expect(draftsApi.streamDraftChat).toHaveBeenCalledWith(
      "draft-456",
      "Viết lại phần tóm tắt",
      expect.any(Object)
    );

    // Badges should be displayed
    await waitFor(() => {
      expect(screen.getByText("🔍 Tra cứu GraphRAG")).toBeInTheDocument();
      expect(screen.getByText("⚙️ Biên dịch E2B")).toBeInTheDocument();
      expect(screen.getByText("Đang tối ưu cấu trúc bài báo...")).toBeInTheDocument();
    });
  });

  it("7. Undo button [↩️ Hoàn tác] triggers undoDraft and restores editor content and bib content", async () => {
    vi.mocked(draftsApi.undoDraft).mockResolvedValue({
      ...mockDraft,
      content: "\\documentclass{article}\n% Restored original\n\\end{document}",
      bib_content: "@article{restored,\n  year={2025}\n}",
      version: 4,
    });

    renderWithRouter(<WritingWorkspace />);

    // Open assistant drawer via FAB
    fireEvent.click(screen.getByTestId("writing-assistant-fab"));

    const undoBtn = screen.getByTestId("undo-draft-btn");
    expect(undoBtn).toBeInTheDocument();

    await act(async () => {
      fireEvent.click(undoBtn);
    });

    expect(draftsApi.undoDraft).toHaveBeenCalledWith("draft-456");

    await waitFor(() => {
      expect(useWritingStore.getState().editorContent).toContain("% Restored original");
      expect(useWritingStore.getState().editorBibContent).toContain("@article{restored");
    });
  });

  it("8. Minimalist header and tabs: removes <-, Files, v1 badge, and line counts from tabs", () => {
    renderWithRouter(<WritingWorkspace />);

    // Arrow back link and files button should not exist in header
    expect(screen.queryByTitle("Dashboard")).toBeNull();
    expect(screen.queryByTestId("toggle-file-tree-btn")).toBeNull();
    expect(screen.queryByText(/^v\d+$/)).toBeNull();

    // Line counts should not be in tabs
    expect(screen.queryByText(/\(\d+\s*dòng\)/)).toBeNull();
  });

  it("9. Supports closing tabs with X and unhiding sidebar when collapsed", async () => {
    renderWithRouter(<WritingWorkspace />);

    // references.bib tab has close button X
    const closeBibBtn = screen.getByTestId("close-tab-references.bib");
    expect(closeBibBtn).toBeInTheDocument();

    fireEvent.click(closeBibBtn);

    // Tab references.bib is now closed
    expect(screen.queryByTestId("editor-tab-bib")).toBeNull();

    // Collapse sidebar
    const collapseBtn = screen.getByTestId("sidebar-collapse-btn");
    fireEvent.click(collapseBtn);

    // Sidebar should be hidden
    expect(useWritingStore.getState().isFileTreeOpen).toBe(false);

    // Unhide button should appear on tab strip
    const unhideBtn = screen.getByTestId("unhide-sidebar-btn");
    expect(unhideBtn).toBeInTheDocument();

    // Click unhide button
    fireEvent.click(unhideBtn);
    expect(useWritingStore.getState().isFileTreeOpen).toBe(true);

    // Now clicking references.bib in sidebar re-opens it
    const sidebarBib = await screen.findByTestId("file-references-bib");
    fireEvent.click(sidebarBib);
    expect(screen.getByTestId("editor-tab-bib")).toBeInTheDocument();
  });
});
