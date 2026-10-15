import { useEffect, useCallback } from "react";
import { WritingHeaderBar } from "./WritingHeaderBar";
import { WritingEditorPane } from "./WritingEditorPane";
import { WritingPreviewPane } from "./WritingPreviewPane";
import { WritingAssistantPane } from "./WritingAssistantPane";
import { SourceEvidenceModal } from "./SourceEvidenceModal";
import { SuggestionReviewPanel } from "./SuggestionReviewPanel";
import { DraftAssetManagementModal } from "./DraftAssetManagementModal";
import { DraftSharingModal } from "./DraftSharingModal";
import { useWritingStore } from "../stores/useWritingStore";
import { draftsApi } from "../api/draftsApi";
import type { PendingSuggestion } from "../types";

export function WritingWorkspace() {

  const {
    activeDraftId,
    draft,
    editorTitle,
    editorContent,
    workspaceMode,
    isDirty,
    markSaved,
    setSaving,
    setCompiling,
    setVerifying,
    setCompileResult,
    setVerifyResult,
    setPreviewPdfBlobUrl,
    setWorkspaceMode,
    setAssistantPrompt,
    openSuggestionPanel,
    closeSuggestionPanel,
    setAssisting,
  } = useWritingStore();

  // Save handler with OCC version tracking
  const handleSave = useCallback(async () => {
    if (!activeDraftId || !draft) return;
    try {
      setSaving(true);
      const updated = await draftsApi.updateDraft(activeDraftId, {
        title: editorTitle,
        content: editorContent,
        format: draft.format,
        version: draft.version,
      });
      markSaved(updated);
    } catch (err) {
      console.error("Save draft failed:", err);
    } finally {
      setSaving(false);
    }
  }, [activeDraftId, draft, editorTitle, editorContent, markSaved, setSaving]);

  // Compile draft with sandbox self-healing
  const handleCompile = useCallback(async () => {
    if (!activeDraftId) return;
    try {
      // First save content if dirty
      if (isDirty) {
        await handleSave();
      }

      setCompiling(true);
      const result = await draftsApi.compileDraft(activeDraftId);
      setCompileResult(result);

      if (result.success) {
        // Fetch fresh preview blob
        const blob = await draftsApi.getPreviewPdfBlob(activeDraftId);
        const url = URL.createObjectURL(blob);
        setPreviewPdfBlobUrl(url);
      }
    } catch (err) {
      console.error("Compile draft failed:", err);
    } finally {
      setCompiling(false);
    }
  }, [
    activeDraftId,
    isDirty,
    handleSave,
    setCompiling,
    setCompileResult,
    setPreviewPdfBlobUrl,
  ]);

  // SAFE Fact-Checking trigger
  const handleVerifyFacts = useCallback(async () => {
    if (!activeDraftId) return;
    try {
      setVerifying(true);
      const report = await draftsApi.verifyFacts(activeDraftId, {
        text: editorContent,
      });
      setVerifyResult(report);
    } catch (err) {
      console.error("Fact verification failed:", err);
    } finally {
      setVerifying(false);
    }
  }, [activeDraftId, editorContent, setVerifying, setVerifyResult]);

  // Export Camera-Ready Academic Submission Bundle (.zip)
  const handleExportBundle = useCallback(async () => {
    if (!activeDraftId) return;
    try {
      const blob = await draftsApi.exportBundle(activeDraftId);
      const downloadUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = `draft_${activeDraftId.replace(/-/g, "").slice(0, 8)}_bundle.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      console.error("Export submission bundle failed:", err);
    }
  }, [activeDraftId]);

  // Keyboard shortcut Ctrl+S / ⌘S for saving
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "s") {
        e.preventDefault();
        handleSave();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleSave]);

  const showCode =
    workspaceMode === "tri-pane" ||
    workspaceMode === "dual-code" ||
    workspaceMode === "zen-code";

  const showPdf =
    workspaceMode === "tri-pane" ||
    workspaceMode === "dual-code" ||
    workspaceMode === "dual-ai" ||
    workspaceMode === "zen-pdf";

  const showAi =
    workspaceMode === "tri-pane" || workspaceMode === "dual-ai";

  // Handler for forwarding surrounding context buffer to AI Assistant Chat
  const handleSelectionAddToChat = useCallback((contextBuffer: string) => {
    // Ensure AI assistant panel is visible in current mode
    if (workspaceMode === "dual-code" || workspaceMode === "zen-code" || workspaceMode === "zen-pdf") {
      setWorkspaceMode("tri-pane");
    }
    setAssistantPrompt(contextBuffer);
  }, [workspaceMode, setWorkspaceMode, setAssistantPrompt]);

  // AI Writing Assist trigger - connects to real POST /api/v1/drafts/{id}/assist
  // Direct streaming/overwriting onto active editor draft content is strictly forbidden!
  const handleSendAssistantPrompt = useCallback(
    async (prompt: string) => {
      if (!activeDraftId || !draft) return;
      try {
        setAssisting(true);

        const currentContent = useWritingStore.getState().editorContent;
        const currentRange = useWritingStore.getState().selectionRange;
        const start = currentRange ? currentRange.start : currentContent.length;
        const end = currentRange ? currentRange.end : currentContent.length;
        const selectedText =
          currentRange && start !== end ? currentContent.substring(start, end) : "";

        // Context buffers around cursor/selection
        const preContext = currentContent.substring(Math.max(0, start - 500), start);
        const postContext = currentContent.substring(
          end,
          Math.min(currentContent.length, end + 500)
        );

        const res = await draftsApi.assistDraft(activeDraftId, {
          prompt,
          pre_context: preContext,
          target_selection: selectedText,
          post_context: postContext,
          cursor_position: start,
        });

        const newSuggestion: PendingSuggestion = {
          id: crypto.randomUUID(),
          draft_id: activeDraftId,
          prompt: res.prompt,
          original_text: res.original_text || selectedText,
          suggested_text: res.suggested_text,
          explanation: res.explanation || undefined,
          confidence_score: res.confidence_score,
          cursor_start: start,
          cursor_end: end,
          expected_version: draft.version,
          created_at: res.suggested_at || new Date().toISOString(),
        };

        openSuggestionPanel(newSuggestion);
      } catch (err) {
        console.error("AI writing assist failed:", err);
      } finally {
        setAssisting(false);
      }
    },
    [activeDraftId, draft, setAssisting, openSuggestionPanel]
  );

  // Safe insertion with OCC ETag guard (If-Match: "v{version}")
  // Preserves any typing done by user while waiting for AI response!
  const handleAcceptSuggestion = useCallback(
    async (suggestion: PendingSuggestion) => {
      if (!activeDraftId || !draft) return;
      try {
        setSaving(true);
        const currentContent = useWritingStore.getState().editorContent;
        const currentRange = useWritingStore.getState().selectionRange;

        // Determine insertion position based on current cursor/selection
        let insertStart = suggestion.cursor_start;
        let insertEnd = suggestion.cursor_end;
        if (currentRange && currentRange.start !== undefined) {
          insertStart = currentRange.start;
          insertEnd = currentRange.end;
        }

        const safeStart = Math.min(Math.max(0, insertStart), currentContent.length);
        const safeEnd = Math.min(Math.max(safeStart, insertEnd), currentContent.length);

        const newContent =
          currentContent.slice(0, safeStart) +
          suggestion.suggested_text +
          currentContent.slice(safeEnd);

        // Save with OCC ETag Guard: If-Match: "v{version}"
        const updated = await draftsApi.updateDraft(
          activeDraftId,
          {
            title: editorTitle,
            content: newContent,
            format: draft.format,
            version: draft.version,
          },
          `v${draft.version}`
        );

        markSaved(updated);
        closeSuggestionPanel();
      } catch (err) {
        console.error("Accept suggestion failed:", err);
      } finally {
        setSaving(false);
      }
    },
    [activeDraftId, draft, editorTitle, markSaved, closeSuggestionPanel, setSaving]
  );

  const handleRejectSuggestion = useCallback(() => {
    // Discard suggestion without touching editor content
    closeSuggestionPanel();
  }, [closeSuggestionPanel]);

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-canvas dark:bg-[#181715] text-ink dark:text-[#f3f2ef]">
      {/* 1. Header Bar with Controls */}
      <WritingHeaderBar
        onSave={handleSave}
        onCompile={handleCompile}
        onExportBundle={handleExportBundle}
      />

      {/* 2. Workspace Adaptive Grid / Flex */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Column 1: Code & Text Editor */}
        {showCode && (
          <WritingEditorPane
            onSelectionVerify={(selectedText) => {
              if (activeDraftId) {
                draftsApi
                  .verifyFacts(activeDraftId, { text: selectedText })
                  .then(setVerifyResult);
              }
            }}
            onSelectionAddToChat={handleSelectionAddToChat}
          />
        )}

        {/* Column 2: Live Compiled PDF Preview */}
        {showPdf && <WritingPreviewPane />}

        {/* Column 3: AI Assistant & SAFE Fact-Checking */}
        {showAi && (
          <WritingAssistantPane
            onVerifyFacts={handleVerifyFacts}
            onSendAssistantPrompt={handleSendAssistantPrompt}
          />
        )}
      </div>

      {/* 3. Source Document Evidence Modal (with Bounding Box Overlay on Source Paper) */}
      <SourceEvidenceModal />

      {/* 4. AI Suggestion Review Panel (Diff preview & OCC safe insertion) */}
      <SuggestionReviewPanel
        onAccept={handleAcceptSuggestion}
        onReject={handleRejectSuggestion}
        onClose={closeSuggestionPanel}
      />

      {/* 5. Academic Asset Management Modal (.png, .pdf, .bib, .cls, .sty) */}
      <DraftAssetManagementModal />

      {/* 6. Draft Sharing & Permissions Modal (roles: view, comment, edit) */}
      <DraftSharingModal />
    </div>
  );
}
