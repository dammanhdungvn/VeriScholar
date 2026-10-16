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

  it("handles openEvidenceModal and closeEvidenceModal", () => {
    const claim = {
      id: "claim-1",
      claim_text: "Transformers use self-attention.",
      normalized_entities: ["transformer", "self-attention"],
      status: "supported" as const,
      confidence_score: 0.95,
      evidence_document_id: "doc-1",
      evidence_page: 3,
      evidence_bounding_boxes: [[0.1, 0.2, 0.9, 0.5]],
    };

    useWritingStore.getState().openEvidenceModal(claim);
    let state = useWritingStore.getState();
    expect(state.isEvidenceModalOpen).toBe(true);
    expect(state.selectedEvidenceClaim).toEqual(claim);
    expect(state.activePage).toBe(3);
    expect(state.activeBoundingBoxes).toEqual([[0.1, 0.2, 0.9, 0.5]]);

    useWritingStore.getState().closeEvidenceModal();
    state = useWritingStore.getState();
    expect(state.isEvidenceModalOpen).toBe(false);
    expect(state.selectedEvidenceClaim).toBeNull();
  });

  it("sets and resets assistant prompt buffer", () => {
    const buffer = "<pre_context>intro</pre_context><target_selection>test</target_selection><post_context>end</post_context>";
    useWritingStore.getState().setAssistantPrompt(buffer);
    expect(useWritingStore.getState().assistantPrompt).toBe(buffer);

    useWritingStore.getState().reset();
    expect(useWritingStore.getState().assistantPrompt).toBe("");
  });

  it("handles suggestion panel state and actions", () => {
    const mockSuggestion = {
      id: "sugg-1",
      draft_id: "draft-1",
      prompt: "Improve intro",
      original_text: "Old text",
      suggested_text: "New improved text",
      confidence_score: 0.92,
      cursor_start: 10,
      cursor_end: 18,
      expected_version: 1,
      created_at: "2026-10-15T12:00:00Z",
    };

    expect(useWritingStore.getState().isSuggestionPanelOpen).toBe(false);
    expect(useWritingStore.getState().pendingSuggestion).toBeNull();
    expect(useWritingStore.getState().isAssisting).toBe(false);

    useWritingStore.getState().setAssisting(true);
    expect(useWritingStore.getState().isAssisting).toBe(true);

    useWritingStore.getState().openSuggestionPanel(mockSuggestion);
    expect(useWritingStore.getState().isSuggestionPanelOpen).toBe(true);
    expect(useWritingStore.getState().pendingSuggestion).toEqual(mockSuggestion);

    useWritingStore.getState().closeSuggestionPanel();
    expect(useWritingStore.getState().isSuggestionPanelOpen).toBe(false);
    expect(useWritingStore.getState().pendingSuggestion).toBeNull();
  });

  it("tracks selection range and resets properly", () => {
    expect(useWritingStore.getState().selectionRange).toBeNull();

    useWritingStore.getState().setSelectionRange({ start: 5, end: 15 });
    expect(useWritingStore.getState().selectionRange).toEqual({ start: 5, end: 15 });

    useWritingStore.getState().reset();
    expect(useWritingStore.getState().selectionRange).toBeNull();
  });

  it("handles asset and share modal state and actions", () => {
    expect(useWritingStore.getState().isAssetModalOpen).toBe(false);
    expect(useWritingStore.getState().isShareModalOpen).toBe(false);

    useWritingStore.getState().openAssetModal();
    expect(useWritingStore.getState().isAssetModalOpen).toBe(true);

    useWritingStore.getState().closeAssetModal();
    expect(useWritingStore.getState().isAssetModalOpen).toBe(false);

    useWritingStore.getState().openShareModal();
    expect(useWritingStore.getState().isShareModalOpen).toBe(true);

    useWritingStore.getState().closeShareModal();
    expect(useWritingStore.getState().isShareModalOpen).toBe(false);

    // Verify reset restores initial false
    useWritingStore.getState().openAssetModal();
    useWritingStore.getState().openShareModal();
    useWritingStore.getState().reset();
    expect(useWritingStore.getState().isAssetModalOpen).toBe(false);
    expect(useWritingStore.getState().isShareModalOpen).toBe(false);
  });

  it("handles peer review comments state and threaded actions", () => {
    expect(useWritingStore.getState().comments).toEqual([]);
    expect(useWritingStore.getState().activeCommentId).toBeNull();
    expect(useWritingStore.getState().isCommentsPaneOpen).toBe(false);

    // Toggle comments pane
    useWritingStore.getState().setCommentsPaneOpen(true);
    expect(useWritingStore.getState().isCommentsPaneOpen).toBe(true);

    // Set active comment id
    useWritingStore.getState().setActiveCommentId("comm-1");
    expect(useWritingStore.getState().activeCommentId).toBe("comm-1");

    // Add top-level comment
    const comment1 = {
      id: "comm-1",
      draft_id: "draft-1",
      author_id: "user-1",
      author_name: "Dr. Turing",
      start_offset: 10,
      end_offset: 25,
      selected_text: "transformers",
      comment_text: "Clarify model architecture.",
      is_resolved: false,
      created_at: "2026-10-15T00:00:00Z",
      updated_at: "2026-10-15T00:00:00Z",
      replies: [],
    };

    useWritingStore.getState().addComment(comment1);
    expect(useWritingStore.getState().comments).toHaveLength(1);
    expect(useWritingStore.getState().comments[0].id).toBe("comm-1");

    // Add threaded reply
    const reply1 = {
      id: "reply-1",
      draft_id: "draft-1",
      author_id: "user-2",
      author_name: "Ada Lovelace",
      start_offset: 10,
      end_offset: 25,
      selected_text: "transformers",
      comment_text: "Added Section 3 references.",
      parent_id: "comm-1",
      is_resolved: false,
      created_at: "2026-10-15T01:00:00Z",
      updated_at: "2026-10-15T01:00:00Z",
    };

    useWritingStore.getState().addComment(reply1);
    expect(useWritingStore.getState().comments[0].replies).toHaveLength(1);
    expect(useWritingStore.getState().comments[0].replies?.[0].id).toBe("reply-1");

    // Update comment
    useWritingStore.getState().updateCommentInStore({
      ...comment1,
      is_resolved: true,
    });
    expect(useWritingStore.getState().comments[0].is_resolved).toBe(true);

    // Remove comment
    useWritingStore.getState().removeCommentFromStore("comm-1");
    expect(useWritingStore.getState().comments).toHaveLength(0);
    expect(useWritingStore.getState().activeCommentId).toBeNull();

    // Verify reset restores default state
    useWritingStore.getState().setCommentsPaneOpen(true);
    useWritingStore.getState().setActiveCommentId("some-id");
    useWritingStore.getState().reset();
    expect(useWritingStore.getState().comments).toEqual([]);
    expect(useWritingStore.getState().activeCommentId).toBeNull();
    expect(useWritingStore.getState().isCommentsPaneOpen).toBe(false);
  });
});
