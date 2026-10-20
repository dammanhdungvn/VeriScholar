import { useEffect, useCallback, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { WritingHeaderBar } from "./WritingHeaderBar";
import { WritingEditorPane } from "./WritingEditorPane";
import { WritingPreviewPane } from "./WritingPreviewPane";
import { WritingAssistantPane } from "./WritingAssistantPane";
import { WritingSidebar } from "./WritingSidebar";
import { DashboardTaskbar } from "@/features/dashboard/components/DashboardTaskbar";
import { SourceEvidenceModal } from "./SourceEvidenceModal";
import { SuggestionReviewPanel } from "./SuggestionReviewPanel";
import { DraftAssetManagementModal } from "./DraftAssetManagementModal";
import { DraftSharingModal } from "./DraftSharingModal";
import { DraftCommentsPane } from "./DraftCommentsPane";
import { AssociativeMemoryCard } from "./AssociativeMemoryCard";
import { useWritingStore } from "../stores/useWritingStore";
import { draftsApi } from "../api/draftsApi";
import { calculateRebasedRange } from "../lib/diffUtils";
import { cn } from "@/lib/utils";
import { X, Sparkles } from "lucide-react";
import type { PendingSuggestion } from "../types";
import type { SessionItem } from "@/types/dashboard";

interface WritingWorkspaceProps {
  sessions?: SessionItem[];
}

export function WritingWorkspace({ sessions }: WritingWorkspaceProps = {}) {

  const {
    activeDraftId,
    draft,
    editorTitle,
    editorContent,
    setEditorContent,
    workspaceMode,
    mobileActiveTab,
    setMobileActiveTab,
    isDirty,
    markSaved,
    setSaving,
    isCompiling,
    setCompiling,
    setVerifying,
    setCompileResult,
    setVerifyResult,
    previewPdfBlobUrl,
    setPreviewPdfBlobUrl,
    setWorkspaceMode,
    setAssistantPrompt,
    openSuggestionPanel,
    closeSuggestionPanel,
    setAssisting,
    isCommentsPaneOpen,
    setComments,
    isFileTreeOpen,
    toggleFileTree,
    openAssetModal,
  } = useWritingStore();

  const navigate = useNavigate();

  const [conflictMessage, setConflictMessage] = useState<string | null>(null);

  // Overleaf-style draggable splitters & navigation
  const [sidebarWidth, setSidebarWidth] = useState(240);
  const [isDraggingSidebar, setIsDraggingSidebar] = useState(false);
  const [editorRatio, setEditorRatio] = useState(50);
  const [isDraggingEditor, setIsDraggingEditor] = useState(false);
  const [targetScrollLine, setTargetScrollLine] = useState<number | null>(null);
  const mainWorkspaceRef = useRef<HTMLDivElement>(null);
  const workspaceContainerRef = useRef<HTMLDivElement>(null);

  // Drag handler for Sidebar Width relative to workspace container
  useEffect(() => {
    if (!isDraggingSidebar) return;
    const handlePointerMove = (e: PointerEvent) => {
      if (!workspaceContainerRef.current) return;
      const rect = workspaceContainerRef.current.getBoundingClientRect();
      const currentX = e.clientX - rect.left;
      const newWidth = Math.max(160, Math.min(420, currentX));
      setSidebarWidth(newWidth);
    };
    const handlePointerUp = () => setIsDraggingSidebar(false);

    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("pointerup", handlePointerUp);
    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", handlePointerUp);
    };
  }, [isDraggingSidebar]);

  // Drag handler for Editor / Preview split ratio
  useEffect(() => {
    if (!isDraggingEditor) return;
    const handlePointerMove = (e: PointerEvent) => {
      if (!mainWorkspaceRef.current) return;
      const rect = mainWorkspaceRef.current.getBoundingClientRect();
      const currentX = e.clientX - rect.left;
      const totalWidth = rect.width;
      if (totalWidth <= 0) return;
      const ratio = Math.max(25, Math.min(75, (currentX / totalWidth) * 100));
      setEditorRatio(Math.round(ratio));
    };
    const handlePointerUp = () => setIsDraggingEditor(false);

    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("pointerup", handlePointerUp);
    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", handlePointerUp);
    };
  }, [isDraggingEditor]);

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
        if (typeof window !== "undefined" && window.innerWidth < 768) {
          setMobileActiveTab("preview");
        }
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
    setMobileActiveTab,
  ]);

  // Auto-compile on initial mount if preview is not loaded and content is present
  const hasAutoCompiledRef = useRef<string | null>(null);
  useEffect(() => {
    if (!activeDraftId) return;

    if (!previewPdfBlobUrl && !isCompiling && hasAutoCompiledRef.current !== activeDraftId && editorContent?.trim()) {
      hasAutoCompiledRef.current = activeDraftId;
      handleCompile();
    }
  }, [
    activeDraftId,
    previewPdfBlobUrl,
    isCompiling,
    editorContent,
    handleCompile,
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
    <div className="flex h-screen w-screen overflow-hidden bg-canvas dark:bg-[#181715] text-ink dark:text-[#f3f2ef]">
      {/* 1. Left Navigation Taskbar (Inherited from Dashboard) */}
      <DashboardTaskbar
        sessions={sessions}
        onSelectSession={(id) => navigate(`/dashboard/${id}`)}
        onNewSession={() => navigate("/dashboard")}
      />

      {/* 2. Main Writing Area */}
      <div
        ref={workspaceContainerRef}
        className="flex-1 flex flex-col h-screen overflow-hidden relative min-w-0"
      >
        {/* Header Bar with Controls */}
        <WritingHeaderBar
          onSave={handleSave}
          onCompile={handleCompile}
          onExportBundle={handleExportBundle}
          onSyncOverleaf={handleSyncOverleaf}
          isSyncingOverleaf={isSyncingOverleaf}
          onInsertLatexSnippet={(snippet) => {
            setEditorContent(editorContent + "\n" + snippet);
          }}
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

        {/* Workspace Adaptive Grid / Flex */}
        <div className="flex-1 flex overflow-hidden relative">
          {/* Collapsible Overleaf-style Sidebar (File Tree & Outline) */}
          {isFileTreeOpen && (
          <>
            {/* Mobile backdrop */}
            <div
              data-testid="mobile-sidebar-backdrop"
              onClick={toggleFileTree}
              className="md:hidden fixed inset-0 bg-black/50 backdrop-blur-2xs z-40 transition-opacity animate-in fade-in"
            />

            {/* Unified Sidebar Container: Drawer on mobile, inline resizable panel on desktop */}
            <div
              data-testid="sidebar-container"
              style={{ width: `${sidebarWidth}px` }}
              className="fixed inset-y-0 left-0 z-50 w-72 max-w-[85vw] h-full shadow-2xl md:relative md:inset-auto md:z-auto md:shadow-none md:w-auto md:h-full shrink-0 overflow-hidden bg-[#fbf9f5] dark:bg-[#181715] border-r border-[#e5dfd4] dark:border-[#2a2824] flex flex-col animate-in slide-in-from-left duration-200 md:animate-none"
            >
              {/* Mobile Drawer Header with Close Button */}
              <div className="md:hidden h-11 px-3 border-b border-[#e5dfd4] dark:border-[#2a2824] flex items-center justify-between bg-[#f4eee5] dark:bg-[#1e1c19] text-xs font-semibold shrink-0">
                <span className="font-serif">Tệp & Dàn ý Bài Báo</span>
                <button
                  type="button"
                  data-testid="close-mobile-sidebar-btn"
                  onClick={toggleFileTree}
                  className="p-1 rounded hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink cursor-pointer"
                  title="Đóng thanh bên"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Sidebar Content */}
              <div className="flex-1 overflow-hidden">
                <WritingSidebar
                  onSelectOutlineItem={(line) => {
                    setTargetScrollLine(line);
                    if (typeof window !== "undefined" && window.innerWidth < 768) {
                      setMobileActiveTab("editor");
                      toggleFileTree();
                    }
                  }}
                  onUploadAsset={() => {
                    if (typeof window !== "undefined" && window.innerWidth < 768) {
                      toggleFileTree();
                    }
                    openAssetModal();
                  }}
                />
              </div>
            </div>

            {/* Draggable Resizable Splitter 1: Sidebar | Workspace (Desktop only) */}
            <div
              data-testid="sidebar-resizable-splitter"
              onPointerDown={(e) => {
                e.preventDefault();
                setIsDraggingSidebar(true);
              }}
              title="Kéo chuột để co giãn danh sách tệp"
              className={cn(
                "hidden md:flex w-1.5 shrink-0 bg-[#f0eae1] dark:bg-[#252320] hover:bg-coral-500/60 transition-colors cursor-col-resize relative items-center justify-center select-none group z-10",
                isDraggingSidebar && "bg-coral-500"
              )}
            >
              <div className="w-0.5 h-6 rounded-full bg-zinc-300 dark:bg-zinc-600 group-hover:bg-coral-500 transition-colors" />
            </div>
          </>
        )}

        {/* Main Work Columns (Editor | Preview | AI | Comments) */}
        <div
          ref={mainWorkspaceRef}
          className="flex-1 flex overflow-hidden relative min-w-0 h-full w-full"
        >
          {/* Column 1: Code & Text Editor */}
          {showCode && (
            <div
              style={showPdf ? { flex: `${editorRatio} 1 0%` } : undefined}
              className={cn(
                "flex-col relative min-w-0 h-full",
                mobileActiveTab === "editor" ? "flex w-full" : "hidden md:flex",
                !showPdf && "flex-1"
              )}
            >
              <WritingEditorPane
                scrollToLine={targetScrollLine}
                onSelectionVerify={(selectedText) => {
                  if (activeDraftId) {
                    draftsApi
                      .verifyFacts(activeDraftId, { text: selectedText })
                      .then(setVerifyResult);
                  }
                }}
                onSelectionAddToChat={(buffer) => {
                  handleSelectionAddToChat(buffer);
                  if (typeof window !== "undefined" && window.innerWidth < 768) {
                    setMobileActiveTab("assistant");
                  }
                }}
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

          {/* Draggable Resizable Splitter 2: Editor | Preview (Desktop only) */}
          {showCode && showPdf && (
            <div
              data-testid="editor-preview-splitter"
              onPointerDown={(e) => {
                e.preventDefault();
                setIsDraggingEditor(true);
              }}
              title="Kéo chuột để co giãn Editor và Preview"
              className={cn(
                "hidden md:flex w-1.5 shrink-0 bg-[#f0eae1] dark:bg-[#252320] hover:bg-coral-500/60 transition-colors cursor-col-resize relative items-center justify-center select-none group z-10",
                isDraggingEditor && "bg-coral-500"
              )}
            >
              <div className="w-0.5 h-6 rounded-full bg-zinc-300 dark:bg-zinc-600 group-hover:bg-coral-500 transition-colors" />
            </div>
          )}

          {/* Column 2: Live Compiled PDF Preview */}
          {showPdf && (
            <div
              style={showCode ? { flex: `${100 - editorRatio} 1 0%` } : undefined}
              className={cn(
                "flex-col relative min-w-0 h-full",
                mobileActiveTab === "preview" ? "flex w-full" : "hidden md:flex",
                !showCode && "flex-1"
              )}
            >
              <WritingPreviewPane
                onRecompile={handleCompile}
                showDoAnything={false}
              />
            </div>
          )}

          {/* Column 3: AI Assistant & SAFE Fact-Checking */}
          {showAi && (
            <div
              className={cn(
                "flex-col relative min-w-0 h-full",
                mobileActiveTab === "assistant" ? "flex w-full" : "hidden md:flex"
              )}
            >
              <WritingAssistantPane
                onVerifyFacts={handleVerifyFacts}
                onSendAssistantPrompt={handleSendAssistantPrompt}
                onClose={() => {
                  setWorkspaceMode("dual-code");
                  if (mobileActiveTab === "assistant") {
                    setMobileActiveTab("editor");
                  }
                }}
              />
            </div>
          )}

          {/* Column 4: Peer Review Comments & Annotations */}
          {isCommentsPaneOpen && (
            <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-96 md:relative md:inset-auto md:w-auto h-full shadow-2xl md:shadow-none">
              <DraftCommentsPane />
            </div>
          )}
        </div>
      </div>
      </div>

      {/* Floating AI Chat Bubble when Assistant is closed */}
      {!showAi && (
        <div className="fixed bottom-5 right-5 z-30 pointer-events-auto">
          <button
            type="button"
            data-testid="floating-ai-chat-bubble"
            onClick={() => {
              setWorkspaceMode("tri-pane");
              if (typeof window !== "undefined" && window.innerWidth < 768) {
                setMobileActiveTab("assistant");
              }
            }}
            className="h-10 px-4 rounded-full bg-white dark:bg-[#201e1a] border border-[#e2dcd2] dark:border-[#38332c] hover:border-coral-500/50 hover:bg-coral-500/10 text-ink dark:text-zinc-100 shadow-xl flex items-center gap-2 text-xs font-semibold font-anthropic-serif transition-all hover:scale-105 active:scale-95 cursor-pointer group"
            title="Mở Trợ lý AI & Kiểm chứng (Chat AI)"
          >
            <Sparkles className="w-4 h-4 text-coral-500 group-hover:rotate-12 transition-transform" />
            <span>Chat AI</span>
          </button>
        </div>
      )}

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
