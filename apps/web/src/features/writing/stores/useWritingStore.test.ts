import { describe, it, expect, beforeEach } from "vitest";
import { useWritingStore } from "./useWritingStore";
import type { Draft } from "../types";

describe("useWritingStore", () => {
  beforeEach(() => {
    useWritingStore.getState().reset();
  });

  it("initializes with default LaTeX content and tri-pane mode", () => {
    const state = useWritingStore.getState();
    expect(state.workspaceMode).toBe("tri-pane");
    expect(state.editorContent).toContain("\\documentclass{article}");
    expect(state.isDirty).toBe(false);
    expect(state.activeDraftId).toBeUndefined();
  });

  it("sets draft and synchronizes editor state", () => {
    const mockDraft: Draft = {
      id: "draft-123",
      user_id: "user-456",
      title: "My Research Paper",
      content: "\\begin{document}Testing\\end{document}",
      format: "latex",
      version: 2,
      created_at: "2026-10-15T00:00:00Z",
      updated_at: "2026-10-15T00:00:00Z",
    };

    useWritingStore.getState().setDraft(mockDraft);

    const state = useWritingStore.getState();
    expect(state.activeDraftId).toBe("draft-123");
    expect(state.draft).toEqual(mockDraft);
    expect(state.editorTitle).toBe("My Research Paper");
    expect(state.editorContent).toBe(mockDraft.content);
    expect(state.isDirty).toBe(false);
  });

  it("marks dirty when editor content or title changes", () => {
    useWritingStore.getState().setEditorContent("New content");
    expect(useWritingStore.getState().isDirty).toBe(true);

    useWritingStore.getState().reset();
    expect(useWritingStore.getState().isDirty).toBe(false);

    useWritingStore.getState().setEditorTitle("New Title");
    expect(useWritingStore.getState().isDirty).toBe(true);
  });

  it("updates workspace modes", () => {
    useWritingStore.getState().setWorkspaceMode("dual-code");
    expect(useWritingStore.getState().workspaceMode).toBe("dual-code");

    useWritingStore.getState().setWorkspaceMode("zen-pdf");
    expect(useWritingStore.getState().workspaceMode).toBe("zen-pdf");
  });

  it("sets active bounding boxes and page", () => {
    const boxes = [[0.1, 0.2, 0.8, 0.4, 2]];
    useWritingStore.getState().setActiveBoundingBoxes(boxes, 2);

    const state = useWritingStore.getState();
    expect(state.activeBoundingBoxes).toEqual(boxes);
    expect(state.activePage).toBe(2);
  });

  it("markSaved resets dirty flag and updates version", () => {
    useWritingStore.getState().setEditorContent("Modified");
    expect(useWritingStore.getState().isDirty).toBe(true);

    const updated: Draft = {
      id: "draft-123",
      user_id: "user-456",
      title: "Updated",
      content: "Modified",
      format: "latex",
      version: 3,
      created_at: "2026-10-15T00:00:00Z",
      updated_at: "2026-10-15T01:00:00Z",
    };

    useWritingStore.getState().markSaved(updated);
    const state = useWritingStore.getState();
    expect(state.isDirty).toBe(false);
    expect(state.draft?.version).toBe(3);
    expect(state.isSaving).toBe(false);
  });

  it("sets and resets assistant prompt buffer", () => {
    const buffer = "<pre_context>intro</pre_context><target_selection>test</target_selection><post_context>end</post_context>";
    useWritingStore.getState().setAssistantPrompt(buffer);
    expect(useWritingStore.getState().assistantPrompt).toBe(buffer);

    useWritingStore.getState().reset();
    expect(useWritingStore.getState().assistantPrompt).toBe("");
  });

  it("tracks selection range and resets properly", () => {
    expect(useWritingStore.getState().selectionRange).toBeNull();

    useWritingStore.getState().setSelectionRange({ start: 5, end: 15 });
    expect(useWritingStore.getState().selectionRange).toEqual({ start: 5, end: 15 });

    useWritingStore.getState().reset();
    expect(useWritingStore.getState().selectionRange).toBeNull();
  });

  it("handles asset modal state and actions", () => {
    expect(useWritingStore.getState().isAssetModalOpen).toBe(false);

    useWritingStore.getState().openAssetModal();
    expect(useWritingStore.getState().isAssetModalOpen).toBe(true);

    useWritingStore.getState().closeAssetModal();
    expect(useWritingStore.getState().isAssetModalOpen).toBe(false);

    // Verify reset restores initial false
    useWritingStore.getState().openAssetModal();
    useWritingStore.getState().reset();
    expect(useWritingStore.getState().isAssetModalOpen).toBe(false);
  });
});
