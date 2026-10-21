import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { WritingHeaderBar } from "./WritingHeaderBar";
import { useWritingStore } from "../stores/useWritingStore";
import type { Draft } from "../types";

describe("WritingHeaderBar", () => {
  const mockDraft: Draft = {
    id: "draft-xyz",
    user_id: "user-1",
    title: "Quantum Transformer Paper",
    content: "Content",
    format: "latex",
    version: 4,
    created_at: "2026-10-15T00:00:00Z",
    updated_at: "2026-10-15T00:00:00Z",
  };

  beforeEach(() => {
    useWritingStore.getState().reset();
    useWritingStore.getState().setDraft(mockDraft);
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("renders draft title, version tag, and saved status", () => {
    render(
      <BrowserRouter>
        <WritingHeaderBar />
      </BrowserRouter>
    );

    expect(screen.getByText("Quantum Transformer Paper")).toBeInTheDocument();
    expect(screen.getByText("v4")).toBeInTheDocument();
    expect(screen.getByText("Đã lưu")).toBeInTheDocument();
  });

  it("opens layout pocket popover and switches mode on option click", () => {
    render(
      <BrowserRouter>
        <WritingHeaderBar />
      </BrowserRouter>
    );

    // Click layout dropdown trigger
    const layoutTrigger = screen.getByTestId("header-layout-dropdown");
    fireEvent.click(layoutTrigger);

    // Popover content should be open
    expect(screen.getByTestId("layout-popover-content")).toBeInTheDocument();

    const dualCodeBtn = screen.getByTestId("mode-dual-code");
    fireEvent.click(dualCodeBtn);

    expect(useWritingStore.getState().workspaceMode).toBe("dual-code");
  });

  it("calls onSave and onCompile directly from prominent buttons, and onExportBundle from tools popover", () => {
    const onSave = vi.fn();
    const onCompile = vi.fn();
    const onExportBundle = vi.fn();

    // Mark dirty so save button is enabled
    useWritingStore.getState().setEditorContent("Modified");

    render(
      <BrowserRouter>
        <WritingHeaderBar
          onSave={onSave}
          onCompile={onCompile}
          onExportBundle={onExportBundle}
        />
      </BrowserRouter>
    );

    // 1. Save button is prominent
    const saveBtn = screen.getByText("Lưu");
    fireEvent.click(saveBtn);
    expect(onSave).toHaveBeenCalledTimes(1);

    // 2. Compile button is prominent
    const compileBtn = screen.getByText("Biên dịch");
    fireEvent.click(compileBtn);
    expect(onCompile).toHaveBeenCalledTimes(1);

    // 3. Export bundle is inside tools popover
    const toolsTrigger = screen.getByTestId("header-tools-dropdown");
    fireEvent.click(toolsTrigger);

    const exportBtn = screen.getByTestId("header-export-bundle-btn");
    fireEvent.click(exportBtn);
    expect(onExportBundle).toHaveBeenCalledTimes(1);
  });

  it("opens Asset modal from tools pocket dropdown", () => {
    render(
      <BrowserRouter>
        <WritingHeaderBar />
      </BrowserRouter>
    );

    expect(useWritingStore.getState().isAssetModalOpen).toBe(false);

    // Open tools dropdown
    fireEvent.click(screen.getByTestId("header-tools-dropdown"));
    const assetsBtn = screen.getByTestId("header-assets-btn");
    fireEvent.click(assetsBtn);

    expect(useWritingStore.getState().isAssetModalOpen).toBe(true);
  });

  it("opens Share modal from tools pocket dropdown", () => {
    render(
      <BrowserRouter>
        <WritingHeaderBar />
      </BrowserRouter>
    );

    expect(useWritingStore.getState().isShareModalOpen).toBe(false);

    // Open tools dropdown
    fireEvent.click(screen.getByTestId("header-tools-dropdown"));
    const shareBtn = screen.getByTestId("header-share-btn");
    fireEvent.click(shareBtn);

    expect(useWritingStore.getState().isShareModalOpen).toBe(true);
  });

  it("toggles comments pane and displays badge count for unresolved comments", () => {
    useWritingStore.getState().setComments([
      {
        id: "c-1",
        draft_id: "draft-xyz",
        author_id: "u-1",
        author_name: "Author 1",
        start_offset: 0,
        end_offset: 10,
        selected_text: "Text",
        comment_text: "Note 1",
        is_resolved: false,
        created_at: "2026-10-15T00:00:00Z",
        updated_at: "2026-10-15T00:00:00Z",
      },
      {
        id: "c-2",
        draft_id: "draft-xyz",
        author_id: "u-2",
        author_name: "Author 2",
        start_offset: 10,
        end_offset: 20,
        selected_text: "Text 2",
        comment_text: "Note 2",
        is_resolved: false,
        created_at: "2026-10-15T00:00:00Z",
        updated_at: "2026-10-15T00:00:00Z",
      },
      {
        id: "c-3",
        draft_id: "draft-xyz",
        author_id: "u-3",
        author_name: "Author 3",
        start_offset: 20,
        end_offset: 30,
        selected_text: "Text 3",
        comment_text: "Note 3",
        is_resolved: true,
        created_at: "2026-10-15T00:00:00Z",
        updated_at: "2026-10-15T00:00:00Z",
      },
    ]);

    render(
      <BrowserRouter>
        <WritingHeaderBar />
      </BrowserRouter>
    );

    // Open tools dropdown
    fireEvent.click(screen.getByTestId("header-tools-dropdown"));

    // Verify unresolved count badge is displayed
    const badge = screen.getByTestId("unresolved-comments-badge");
    expect(badge).toHaveTextContent("2");

    // Toggle comments pane
    expect(useWritingStore.getState().isCommentsPaneOpen).toBe(false);
    const commentsBtn = screen.getByTestId("header-comments-btn");
    fireEvent.click(commentsBtn);
    expect(useWritingStore.getState().isCommentsPaneOpen).toBe(true);
  });

  it("disables Overleaf sync button and displays spinning loader during sync (isSyncingOverleaf=true)", () => {
    const onSyncOverleaf = vi.fn();

    const { container } = render(
      <BrowserRouter>
        <WritingHeaderBar
          onSyncOverleaf={onSyncOverleaf}
          isSyncingOverleaf={true}
        />
      </BrowserRouter>
    );

    // Open tools dropdown
    fireEvent.click(screen.getByTestId("header-tools-dropdown"));

    const overleafBtn = screen.getByTestId("header-overleaf-btn");
    expect(overleafBtn).toBeInTheDocument();
    expect(overleafBtn).toBeDisabled();

    // Check spinning loader icon
    const spinner = container.querySelector(".animate-spin");
    expect(spinner).toBeInTheDocument();

    // Attempt clicking disabled button - should not trigger callback
    fireEvent.click(overleafBtn);
    expect(onSyncOverleaf).not.toHaveBeenCalled();
  });

  it("enables Overleaf sync button and triggers callback on click when idle (isSyncingOverleaf=false)", () => {
    const onSyncOverleaf = vi.fn();

    const { container } = render(
      <BrowserRouter>
        <WritingHeaderBar
          onSyncOverleaf={onSyncOverleaf}
          isSyncingOverleaf={false}
        />
      </BrowserRouter>
    );

    // Open tools dropdown
    fireEvent.click(screen.getByTestId("header-tools-dropdown"));

    const overleafBtn = screen.getByTestId("header-overleaf-btn");
    expect(overleafBtn).toBeInTheDocument();
    expect(overleafBtn).not.toBeDisabled();

    // No spinner when not syncing
    const spinner = container.querySelector(".animate-spin");
    expect(spinner).not.toBeInTheDocument();

    // Click triggers onSyncOverleaf
    fireEvent.click(overleafBtn);
    expect(onSyncOverleaf).toHaveBeenCalledTimes(1);
  });

  it("toggles secondary toolbar ribbon and auto-hides after 5 seconds of inactivity", () => {
    vi.useFakeTimers();

    render(
      <BrowserRouter>
        <WritingHeaderBar />
      </BrowserRouter>
    );

    // Initially secondary ribbon is not visible
    expect(screen.queryByTestId("secondary-toolbar-ribbon")).not.toBeInTheDocument();

    // Toggle ribbon open
    const toggleBtn = screen.getByTestId("toggle-secondary-toolbar-btn");
    fireEvent.click(toggleBtn);

    // Ribbon should now be in the document
    expect(screen.getByTestId("secondary-toolbar-ribbon")).toBeInTheDocument();
    expect(screen.getByText(/Tự ẩn sau 5s/)).toBeInTheDocument();

    // Advance 3 seconds - still visible
    act(() => {
      vi.advanceTimersByTime(3000);
    });
    expect(screen.getByTestId("secondary-toolbar-ribbon")).toBeInTheDocument();

    // Advance remaining 2 seconds (total 5s) - ribbon auto-hides
    act(() => {
      vi.advanceTimersByTime(2000);
    });
    expect(screen.queryByTestId("secondary-toolbar-ribbon")).not.toBeInTheDocument();
  });
});
