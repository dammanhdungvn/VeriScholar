import { useEffect, useCallback, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { WritingHeaderBar } from "./WritingHeaderBar";
import { WritingEditorPane } from "./WritingEditorPane";
import { WritingPreviewPane } from "./WritingPreviewPane";
import { WritingAssistantPane } from "./WritingAssistantPane";
import { WritingSidebar } from "./WritingSidebar";
import { DashboardTaskbar } from "@/features/dashboard/components/DashboardTaskbar";
import { DraftAssetManagementModal } from "./DraftAssetManagementModal";
import { useWritingStore } from "../stores/useWritingStore";
import { draftsApi } from "../api/draftsApi";
import { cn } from "@/lib/utils";
import { X, Sparkles } from "lucide-react";
import type { SessionItem } from "@/types/dashboard";

interface WritingWorkspaceProps {
  sessions?: SessionItem[];
  hideTaskbar?: boolean;
}

export function WritingWorkspace({ sessions, hideTaskbar = true }: WritingWorkspaceProps = {}) {
  const {
    activeDraftId,
    draft,
    editorTitle,
    editorContent,
    editorBibContent,
    workspaceMode,
    mobileActiveTab,
    setMobileActiveTab,
    isDirty,
    markSaved,
    setSaving,
    isCompiling,
    setCompiling,
    setCompileResult,
    previewPdfBlobUrl,
    setPreviewPdfBlobUrl,
    setWorkspaceMode,
    setAssistantPrompt,
    isFileTreeOpen,
    toggleFileTree,
    openAssetModal,
  } = useWritingStore();

  const navigate = useNavigate();

  // Overleaf-style draggable splitters & navigation
  const [sidebarWidth, setSidebarWidth] = useState(240);
  const [isDraggingSidebar, setIsDraggingSidebar] = useState(false);
  const [editorRatio, setEditorRatio] = useState(50);
  const [isDraggingEditor, setIsDraggingEditor] = useState(false);
  const [targetScrollLine, setTargetScrollLine] = useState<number | null>(null);
  const [isAssistantOpen, setIsAssistantOpen] = useState(false);
  const mainWorkspaceRef = useRef<HTMLDivElement>(null);
  const workspaceContainerRef = useRef<HTMLDivElement>(null);

  // Sync assistant drawer state with mode & mobile tab
  useEffect(() => {
    if (workspaceMode === "tri-pane" || workspaceMode === "dual-ai" || mobileActiveTab === "assistant") {
      setIsAssistantOpen(true);
    }
  }, [workspaceMode, mobileActiveTab]);

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

  // Save handler with OCC version tracking
  const handleSave = useCallback(async () => {
    if (!activeDraftId || !draft) return;
    try {
      setSaving(true);
      const updated = await draftsApi.updateDraft(activeDraftId, {
        title: editorTitle,
        content: editorContent,
        bib_content: editorBibContent,
        format: draft.format,
        version: draft.version,
      });
      markSaved(updated);
    } catch (err) {
      console.error("Save draft failed:", err);
    } finally {
      setSaving(false);
    }
  }, [
    activeDraftId,
    draft,
    editorTitle,
    editorContent,
    editorBibContent,
    markSaved,
    setSaving,
  ]);

  // Clear cache and compile clean
  const handleClearCacheRecompile = useCallback(async () => {
    if (!activeDraftId) return;
    try {
      if (isDirty) {
        await handleSave();
      }
      setCompiling(true);
      const result = await draftsApi.recompileClearCache(activeDraftId);
      setCompileResult(result);

      if (result.success) {
        const blob = await draftsApi.getPreviewPdfBlob(activeDraftId);
        const url = URL.createObjectURL(blob);
        setPreviewPdfBlobUrl(url);
        if (typeof window !== "undefined" && window.innerWidth < 768) {
          setMobileActiveTab("preview");
        }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Compile request failed.";
      setCompileResult({
        draft_id: activeDraftId,
        success: false,
        errors: [{ line: 0, column: 0, rule: "request", message }],
        logs: message,
        retries_attempted: 0,
      });
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
      const message = err instanceof Error ? err.message : "Compile request failed.";
      setCompileResult({
        draft_id: activeDraftId,
        success: false,
        errors: [{ line: 0, column: 0, rule: "request", message }],
        logs: message,
        retries_attempted: 0,
      });
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

  // Handler for forwarding surrounding context buffer to AI Assistant Chat
  const handleSelectionAddToChat = useCallback((contextBuffer: string) => {
    setIsAssistantOpen(true);
    setAssistantPrompt(contextBuffer);
  }, [setAssistantPrompt]);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-canvas dark:bg-[#181715] text-ink dark:text-[#f3f2ef]">
      {/* 1. Left Navigation Taskbar (Optional if not wrapped in AppLayout) */}
      {!hideTaskbar && (
        <DashboardTaskbar
          sessions={sessions}
          onSelectSession={(id) => navigate(`/dashboard/${id}`)}
          onNewSession={() => navigate("/dashboard")}
        />
      )}

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
        />

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

          {/* Main Work Columns (Editor | Preview | AI) */}
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
                  onSelectionAddToChat={(buffer) => {
                    handleSelectionAddToChat(buffer);
                    if (typeof window !== "undefined" && window.innerWidth < 768) {
                      setMobileActiveTab("assistant");
                    }
                  }}
                />
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
                  onRecompileClearCache={handleClearCacheRecompile}
                  onNavigateToLine={(line) => setTargetScrollLine(line)}
                  showDoAnything={false}
                />
              </div>
            )}

          </div>
        </div>
      </div>

      {/* Socratic Assistant Overlay Drawer (420px slide-out) */}
      {isAssistantOpen && (
        <>
          <div
            data-testid="writing-assistant-backdrop"
            onClick={() => setIsAssistantOpen(false)}
            className="fixed inset-0 bg-black/20 z-40 md:hidden backdrop-blur-2xs transition-opacity animate-in fade-in"
          />
          <div
            data-testid="writing-assistant-drawer"
            className="fixed inset-y-0 right-0 w-full sm:w-[420px] max-w-[90vw] shadow-2xl z-40 bg-[#fbf9f5] dark:bg-[#181715] border-l border-[#ece8df] dark:border-[#2a2824] flex flex-col animate-in slide-in-from-right duration-200"
          >
            <WritingAssistantPane
              onClose={() => {
                setIsAssistantOpen(false);
                if (mobileActiveTab === "assistant") {
                  setMobileActiveTab("editor");
                }
                if (workspaceMode === "tri-pane") {
                  setWorkspaceMode("dual-code");
                }
              }}
            />
          </div>
        </>
      )}

      {/* Socratic Assistant Floating Action Button (FAB) at bottom right */}
      {!isAssistantOpen && (
        <div className="fixed bottom-5 right-5 z-30 pointer-events-auto">
          <button
            type="button"
            data-testid="writing-assistant-fab"
            onClick={() => {
              setIsAssistantOpen(true);
              if (typeof window !== "undefined" && window.innerWidth < 768) {
                setMobileActiveTab("assistant");
              }
            }}
            className="h-10 px-4 rounded-full bg-[#c15f3e] hover:bg-[#a84f32] text-white shadow-xl flex items-center gap-2 text-xs font-semibold font-anthropic-serif transition-all hover:scale-105 active:scale-95 cursor-pointer group"
            title="Mở Trợ lý Socratic Assistant"
          >
            <Sparkles className="w-4 h-4 text-white group-hover:rotate-12 transition-transform" />
            <span>Socratic Assistant</span>
          </button>
        </div>
      )}

      {/* Academic Asset Management Modal (.png, .pdf, .bib, .cls, .sty) */}
      <DraftAssetManagementModal />
    </div>
  );
}
