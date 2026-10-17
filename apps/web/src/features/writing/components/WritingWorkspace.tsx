import { useEffect, useCallback, useState } from "react";
import { WritingHeaderBar } from "./WritingHeaderBar";
import { WritingEditorPane } from "./WritingEditorPane";
import { WritingPreviewPane } from "./WritingPreviewPane";
import { WritingAssistantPane } from "./WritingAssistantPane";
import { SourceEvidenceModal } from "./SourceEvidenceModal";
import { SuggestionReviewPanel } from "./SuggestionReviewPanel";
import { DraftAssetManagementModal } from "./DraftAssetManagementModal";
import { DraftSharingModal } from "./DraftSharingModal";
import { DraftCommentsPane } from "./DraftCommentsPane";
import { AssociativeMemoryCard } from "./AssociativeMemoryCard";
import { useWritingStore } from "../stores/useWritingStore";
import { draftsApi } from "../api/draftsApi";
import { calculateRebasedRange } from "../lib/diffUtils";
import type { PendingSuggestion } from "../types";

export function WritingWorkspace() {

  const {
    activeDraftId,
    draft,
    editorTitle,
    editorContent,
    setEditorContent,
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
    isCommentsPaneOpen,
    setComments,
  } = useWritingStore();

  const [conflictMessage, setConflictMessage] = useState<string | null>(null);

  // Fetch peer review comments on draft load
  useEffect(() => {
    if (!activeDraftId) return;
    let active = true;
    draftsApi
      .getComments(activeDraftId)
      .then((data) => {
        if (active && Array.isArray(data)) {
          setComments(data);
        }
      })
      .catch((err) => {
        console.error("Failed to fetch draft comments:", err);
      });
    return () => {
      active = false;
    };
  }, [activeDraftId, setComments]);

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

  // Sync draft directly to Overleaf (1-Click Launch)
  const [isSyncingOverleaf, setIsSyncingOverleaf] = useState(false);
  const handleSyncOverleaf = useCallback(async () => {
    if (!activeDraftId) return;
    try {
      setIsSyncingOverleaf(true);
      const res = await draftsApi.exportToOverleaf(activeDraftId);
      if (res?.launch_url) {
        window.open(res.launch_url, "_blank");
      }
    } catch (err) {
      console.error("Overleaf 1-click sync failed:", err);
    } finally {
      setIsSyncingOverleaf(false);
    }
  }, [activeDraftId]);

  // Proactive Associative Memory Card suggestion state
  const [activeMemorySuggestion, setActiveMemorySuggestion] = useState<{
    id: string;
    title: string;
    page: number;
    citationKey: string;
    noteSnippet?: string;
    noteId?: string;
    similarityScore?: number;
  } | null>(null);

  const handleInsertAssociativeCitation = useCallback(
    (citationKey: string) => {
      const citeTag = `\\cite{${citationKey}}`;
      setEditorContent(editorContent + ` ${citeTag} `);
      setActiveMemorySuggestion(null);
    },
    [editorContent, setEditorContent]
  );

  const handleViewAssociativeNote = useCallback((noteId?: string) => {
    console.info("Viewing associative note:", noteId);
  }, []);

  // Proactively fetch scholarly associative suggestions from historical research notes
  useEffect(() => {
    if (!activeDraftId || !editorContent || editorContent.trim().length < 10) return;

    const timer = setTimeout(async () => {
      try {
        const res = await draftsApi.getAssociativeSuggestions(activeDraftId, {
          content: editorContent,
          limit: 3,
        });
        if (res?.suggestions && res.suggestions.length > 0) {
          const top = res.suggestions[0];
          let citationKey = top.suggested_citation || "";
          const citeMatch = citationKey.match(/\\cite\{([^}]+)\}/);
          if (citeMatch) {
            citationKey = citeMatch[1];
          }
          setActiveMemorySuggestion({
            id: top.note_id,
            title: top.paper_title || top.document_title || "Relevant Note",
            page: top.page_number || 1,
            citationKey: citationKey || "ref",
            noteSnippet: top.user_note || top.selected_text || top.note_content,
            noteId: top.note_id,
            similarityScore: top.similarity_score,
          });
        }
      } catch (err) {
        console.warn("Failed to fetch proactive associative suggestions:", err);
      }
    }, 800);

    return () => clearTimeout(timer);
  }, [activeDraftId, editorContent]);

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
          base_content: currentContent,
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
        const baseContent = suggestion.base_content ?? draft.content ?? "";

        // Rebase target range to accurately preserve local unpersisted edits (DEFECT-01)
        const { start: rebasedStart, end: rebasedEnd, hasConflict } = calculateRebasedRange(
          baseContent,
          currentContent,
          suggestion.cursor_start,
          suggestion.cursor_end,
          suggestion.original_text
        );

        if (hasConflict) {
          setConflictMessage(
            "Văn bản gốc của đề xuất đã bị thay đổi hoặc không còn khớp trên trình soạn thảo. Vui lòng kiểm tra lại trước khi áp dụng."
          );
          return;
        }

        const safeStart = Math.min(Math.max(0, rebasedStart), currentContent.length);
        const safeEnd = Math.min(Math.max(safeStart, rebasedEnd), currentContent.length);

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
        setConflictMessage(null);
      } catch (err: unknown) {
        console.error("Accept suggestion failed:", err);
        const isPreconditionFailed =
          (err && typeof err === "object" && "status" in err && (err as { status: number }).status === 412) ||
          (err instanceof Error && err.message.includes("412"));

        if (isPreconditionFailed) {
          try {
            const freshDraft = await draftsApi.getDraft(activeDraftId);
            useWritingStore.setState({ draft: freshDraft });
          } catch {
            // Keep draft state if fetch fails
          }
          setConflictMessage(
            "Bản thảo trên máy chủ đã thay đổi phiên bản (HTTP 412). Phiên bản cơ sở đã được cập nhật, vui lòng xác nhận áp dụng lại đề xuất."
          );
        } else {
          setConflictMessage("Không thể lưu đề xuất. Vui lòng thử lại.");
        }
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
        onSyncOverleaf={handleSyncOverleaf}
        isSyncingOverleaf={isSyncingOverleaf}
      />

      {/* OCC Conflict Alert Banner */}
      {conflictMessage && (
        <div
          data-testid="occ-conflict-alert"
          className="bg-amber-500/10 border-b border-amber-500/30 px-4 py-2 flex items-center justify-between text-amber-700 dark:text-amber-300 text-xs font-medium z-20"
        >
          <span>{conflictMessage}</span>
          <button
            type="button"
            data-testid="close-conflict-alert-btn"
            onClick={() => setConflictMessage(null)}
            className="hover:underline ml-4 cursor-pointer text-amber-800 dark:text-amber-200"
          >
            Đóng
          </button>
        </div>
      )}

      {/* 2. Workspace Adaptive Grid / Flex */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Column 1: Code & Text Editor */}
        {showCode && (
          <div className="flex-1 flex flex-col relative min-w-0">
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

            {/* Proactive Associative Memory Card floating on editor margin */}
            {activeMemorySuggestion && (
              <div className="absolute bottom-4 right-4 z-20 max-w-sm">
                <AssociativeMemoryCard
                  title={activeMemorySuggestion.title}
                  page={activeMemorySuggestion.page}
                  citationKey={activeMemorySuggestion.citationKey}
                  noteSnippet={activeMemorySuggestion.noteSnippet}
                  similarityScore={activeMemorySuggestion.similarityScore}
                  onInsertCitation={handleInsertAssociativeCitation}
                  onViewNote={handleViewAssociativeNote}
                  onDismiss={() => setActiveMemorySuggestion(null)}
                />
              </div>
            )}
          </div>
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

        {/* Column 4: Peer Review Comments & Annotations */}
        {isCommentsPaneOpen && <DraftCommentsPane />}
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
