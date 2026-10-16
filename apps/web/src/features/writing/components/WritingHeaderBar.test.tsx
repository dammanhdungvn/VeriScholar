import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
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

  it("renders draft title, version tag, and saved status", () => {
    render(
      <BrowserRouter>
        <WritingHeaderBar />
      </BrowserRouter>
    );

    expect(screen.getByText("Quantum Transformer Paper")).toBeDefined();
    expect(screen.getByText("v4")).toBeDefined();
    expect(screen.getByText("Đã lưu")).toBeDefined();
  });

  it("triggers layout mode switch when clicking mode button", () => {
    render(
      <BrowserRouter>
        <WritingHeaderBar />
      </BrowserRouter>
    );

    const dualCodeBtn = screen.getByTitle("Code & PDF");
    fireEvent.click(dualCodeBtn);

    expect(useWritingStore.getState().workspaceMode).toBe("dual-code");
  });

  it("calls onSave, onCompile, and onExportBundle callbacks", () => {
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

    const saveBtn = screen.getByText("Lưu");
    fireEvent.click(saveBtn);
    expect(onSave).toHaveBeenCalledTimes(1);

    const compileBtn = screen.getByText("Biên dịch");
    fireEvent.click(compileBtn);
    expect(onCompile).toHaveBeenCalledTimes(1);

    const exportBtn = screen.getByText("Xuất Gói Nộp Bài");
    fireEvent.click(exportBtn);
    expect(onExportBundle).toHaveBeenCalledTimes(1);
  });

  it("opens Asset modal when clicking Assets button", () => {
    render(
      <BrowserRouter>
        <WritingHeaderBar />
      </BrowserRouter>
    );

    expect(useWritingStore.getState().isAssetModalOpen).toBe(false);
    const assetsBtn = screen.getByTestId("header-assets-btn");
    fireEvent.click(assetsBtn);

    expect(useWritingStore.getState().isAssetModalOpen).toBe(true);
  });

  it("opens Share modal when clicking Share button", () => {
    render(
      <BrowserRouter>
        <WritingHeaderBar />
      </BrowserRouter>
    );

    expect(useWritingStore.getState().isShareModalOpen).toBe(false);
    const shareBtn = screen.getByTestId("header-share-btn");
    fireEvent.click(shareBtn);

    expect(useWritingStore.getState().isShareModalOpen).toBe(true);
  });

  it("toggles comments pane and displays badge count for unresolved comments", () => {
    // Add 2 unresolved comments and 1 resolved comment
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

    // Verify unresolved count badge is displayed
    const badge = screen.getByTestId("unresolved-comments-badge");
    expect(badge).toHaveTextContent("2");

    // Toggle comments pane
    expect(useWritingStore.getState().isCommentsPaneOpen).toBe(false);
    const commentsBtn = screen.getByTestId("header-comments-btn");
    fireEvent.click(commentsBtn);
    expect(useWritingStore.getState().isCommentsPaneOpen).toBe(true);
  });
});
