import { useState, useEffect, useRef } from "react";
import {
  Save,
  Play,
  Download,
  Columns3,
  SplitSquareVertical,
  Sidebar,
  Maximize2,
  FileCode,
  CheckCircle2,
  AlertCircle,
  Loader2,
  FolderArchive,
  ChevronDown,
  Wrench,
  Sparkles,
  FileText,
} from "lucide-react";
import { useWritingStore } from "../stores/useWritingStore";
import type { WorkspaceMode } from "../types";
import { cn } from "@/lib/utils";

interface WritingHeaderBarProps {
  onSave?: () => Promise<void>;
  onCompile?: () => Promise<void>;
  onExportBundle?: () => Promise<void>;
  onOpenAssets?: () => void;
}

export function WritingHeaderBar({
  onSave,
  onCompile,
  onExportBundle,
  onOpenAssets,
}: WritingHeaderBarProps) {
  const {
    draft,
    editorTitle,
    setEditorTitle,
    workspaceMode,
    setWorkspaceMode,
    isDirty,
    isSaving,
    isCompiling,
    openAssetModal,
    mobileActiveTab,
    setMobileActiveTab,
  } = useWritingStore();

  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [isLayoutOpen, setIsLayoutOpen] = useState(false);
  const [isToolsOpen, setIsToolsOpen] = useState(false);

  const layoutRef = useRef<HTMLDivElement | null>(null);
  const toolsRef = useRef<HTMLDivElement | null>(null);

  // Close dropdowns on click outside
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (layoutRef.current && !layoutRef.current.contains(e.target as Node)) {
        setIsLayoutOpen(false);
      }
      if (toolsRef.current && !toolsRef.current.contains(e.target as Node)) {
        setIsToolsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const modeButtons: { mode: WorkspaceMode; label: string; icon: typeof Columns3 }[] = [
    { mode: "tri-pane", label: "3-Pane", icon: Columns3 },
    { mode: "dual-code", label: "Code & PDF", icon: SplitSquareVertical },
    { mode: "dual-ai", label: "PDF & AI", icon: Sidebar },
    { mode: "zen-pdf", label: "PDF Only", icon: Maximize2 },
    { mode: "zen-code", label: "Code Only", icon: FileCode },
  ];

  const currentModeObj = modeButtons.find((m) => m.mode === workspaceMode) || modeButtons[0];
  const CurrentModeIcon = currentModeObj.icon;

  const handleSelectMode = (mode: WorkspaceMode) => {
    setWorkspaceMode(mode);
    setIsLayoutOpen(false);
  };

  return (
    <div className="flex flex-col shrink-0 select-none border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#fbf9f5] dark:bg-[#1c1b18]">
      {/* 1. Main Top Header Bar */}
      <header className="h-14 px-3 sm:px-4 flex items-center justify-between gap-2 sm:gap-3 relative z-30">
        {/* Left: Draft Title & Save status */}
        <div className="flex items-center gap-2 sm:gap-3 min-w-0">
          <div className="flex items-center gap-1.5 sm:gap-2 min-w-0">
            {isEditingTitle ? (
              <input
                type="text"
                value={editorTitle}
                onChange={(e) => setEditorTitle(e.target.value)}
                onBlur={() => setIsEditingTitle(false)}
                onKeyDown={(e) => e.key === "Enter" && setIsEditingTitle(false)}
                autoFocus
                className="px-2 py-0.5 text-xs sm:text-sm font-semibold font-anthropic-serif bg-surface-cream dark:bg-[#24221e] border border-[#c15f3e] rounded text-ink dark:text-zinc-100 outline-none w-32 xs:w-48 sm:w-64 max-w-[45vw]"
              />
            ) : (
              <button
                type="button"
                onClick={() => setIsEditingTitle(true)}
                className="text-xs sm:text-sm font-semibold font-anthropic-serif text-ink dark:text-zinc-100 truncate hover:underline text-left cursor-pointer max-w-[120px] xs:max-w-[180px] sm:max-w-[280px] md:max-w-md"
                title="Rename draft"
              >
                {editorTitle || "Untitled Draft"}
              </button>
            )}

            {/* Save Status Indicator */}
            <div className="flex items-center gap-1 text-[11px] text-muted dark:text-zinc-500 ml-0.5 sm:ml-1 shrink-0">
              {isSaving ? (
                <span className="flex items-center gap-1 text-amber-600 dark:text-amber-400">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  <span className="sr-only">Đang lưu...</span>
                  <span className="hidden sm:inline">Saving...</span>
                </span>
              ) : isDirty ? (
                <span className="flex items-center gap-1 text-amber-600 dark:text-amber-400">
                  <AlertCircle className="w-3 h-3" />
                  <span className="sr-only">Chưa lưu</span>
                  <span className="hidden sm:inline">Unsaved</span>
                </span>
              ) : (
                <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
                  <CheckCircle2 className="w-3 h-3" />
                  <span className="sr-only">Đã lưu</span>
                  <span className="hidden sm:inline">Saved</span>
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Center / Right: Pockets & Prominent Actions */}
        <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
          {/* POCKET 1: Layout Popover/Dropdown (Desktop only) */}
          <div className="relative hidden md:block" ref={layoutRef}>
            <button
              type="button"
              data-testid="header-layout-dropdown"
              onClick={() => {
                setIsLayoutOpen(!isLayoutOpen);
                setIsToolsOpen(false);
              }}
              className={cn(
                "h-8 px-2.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors cursor-pointer border",
                isLayoutOpen
                  ? "bg-white dark:bg-[#24221e] text-ink dark:text-zinc-100 border-[#c15f3e] shadow-xs"
                  : "bg-[#ece8df] dark:bg-[#262420] text-ink dark:text-zinc-200 border-transparent hover:bg-[#e4dfd4] dark:hover:bg-[#2d2a26]"
              )}
              title="Layout"
            >
              <CurrentModeIcon className="w-3.5 h-3.5 text-[#c15f3e]" />
              <span className="hidden sm:inline">Layout</span>
              <ChevronDown className="w-3 h-3 text-muted dark:text-zinc-400" />
            </button>

            {isLayoutOpen && (
              <div
                data-testid="layout-popover-content"
                className="absolute left-0 sm:right-0 sm:left-auto top-10 w-52 bg-white dark:bg-[#24221e] border border-[#e2dcd2] dark:border-[#33302b] rounded-xl shadow-xl z-50 p-1.5 text-xs space-y-1 animate-in fade-in zoom-in-95 duration-100"
              >
                <div className="px-2 py-1 text-[10px] font-mono font-semibold text-muted dark:text-zinc-400 uppercase tracking-wider">
                  Chế độ hiển thị
                </div>
                {modeButtons.map(({ mode, label, icon: Icon }) => (
                  <button
                    key={mode}
                    type="button"
                    data-testid={`mode-${mode}`}
                    onClick={() => handleSelectMode(mode)}
                    title={label}
                    className={cn(
                      "w-full px-2.5 py-1.5 rounded-lg text-left flex items-center gap-2 transition-colors cursor-pointer",
                      workspaceMode === mode
                        ? "bg-coral-500/10 text-coral-700 dark:text-coral-300 font-semibold"
                        : "text-ink dark:text-zinc-200 hover:bg-[#f2ece1] dark:hover:bg-[#2e2b26]"
                    )}
                  >
                    <Icon className="w-3.5 h-3.5 text-coral-600 dark:text-coral-400 shrink-0" />
                    <span className="truncate">{label}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* POCKET 2: Tools & Export Dropdown */}
          <div className="relative" ref={toolsRef}>
            <button
              type="button"
              data-testid="header-tools-dropdown"
              onClick={() => {
                setIsToolsOpen(!isToolsOpen);
                setIsLayoutOpen(false);
              }}
              className={cn(
                "h-8 px-2.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors cursor-pointer border",
                isToolsOpen
                  ? "bg-white dark:bg-[#24221e] text-ink dark:text-zinc-100 border-[#c15f3e] shadow-xs"
                  : "bg-[#ece8df] dark:bg-[#262420] text-ink dark:text-zinc-200 border-transparent hover:bg-[#e4dfd4] dark:hover:bg-[#2d2a26]"
              )}
              title="Tools"
            >
              <Wrench className="w-3.5 h-3.5 text-[#c15f3e]" />
              <span className="hidden sm:inline">Tools</span>
              <ChevronDown className="w-3 h-3 text-muted dark:text-zinc-400" />
            </button>

            {isToolsOpen && (
              <div
                data-testid="tools-popover-content"
                className="absolute right-0 top-10 w-56 bg-white dark:bg-[#24221e] border border-[#e2dcd2] dark:border-[#33302b] rounded-xl shadow-xl z-50 p-1.5 text-xs space-y-1 animate-in fade-in zoom-in-95 duration-100"
              >
                <div className="px-2 py-1 text-[10px] font-mono font-semibold text-muted dark:text-zinc-400 uppercase tracking-wider">
                  Assets & Export
                </div>

                {/* Assets button */}
                <button
                  type="button"
                  data-testid="header-assets-btn"
                  onClick={() => {
                    setIsToolsOpen(false);
                    if (onOpenAssets) onOpenAssets();
                    else openAssetModal();
                  }}
                  className="w-full px-2.5 py-1.5 rounded-lg text-left flex items-center gap-2 hover:bg-[#f2ece1] dark:hover:bg-[#2e2b26] text-ink dark:text-zinc-200 cursor-pointer"
                  title="Assets"
                >
                  <FolderArchive className="w-3.5 h-3.5 text-[#c15f3e]" />
                  <span>Assets</span>
                </button>

                {/* Export submission bundle (.zip) */}
                <button
                  type="button"
                  data-testid="header-export-bundle-btn"
                  onClick={() => {
                    setIsToolsOpen(false);
                    if (onExportBundle) onExportBundle();
                  }}
                  className="w-full px-2.5 py-1.5 rounded-lg text-left flex items-center gap-2 hover:bg-[#f2ece1] dark:hover:bg-[#2e2b26] text-ink dark:text-zinc-200 cursor-pointer"
                  title="Export ZIP"
                >
                  <Download className="w-3.5 h-3.5 text-[#c15f3e]" />
                  <span>Export ZIP</span>
                </button>
              </div>
            )}
          </div>

          <div className="h-4 w-px bg-[#e2dcd2] dark:border-[#2e2b26] mx-0.5 sm:mx-1 hidden sm:block" />

          {/* PROMINENT BUTTON 1: Save */}
          <button
            type="button"
            onClick={onSave}
            disabled={isSaving || !isDirty}
            className="h-8 px-2.5 sm:px-3 rounded-lg text-xs font-medium flex items-center gap-1.5 bg-[#ece8df] dark:bg-[#262420] text-ink dark:text-zinc-200 hover:bg-[#e4dfd4] dark:hover:bg-[#2d2a26] disabled:opacity-40 transition-colors cursor-pointer border border-[#ded8cc] dark:border-[#322f2b]"
            title="Save (Ctrl+S / ⌘S)"
          >
            {isSaving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
            <span className="sr-only">Lưu</span>
            <span className="hidden sm:inline">Save</span>
          </button>

          {/* PROMINENT BUTTON 2: Compile (Primary Accent) */}
          <button
            type="button"
            onClick={onCompile}
            disabled={isCompiling}
            className="h-8 px-2.5 sm:px-3.5 rounded-lg text-xs font-semibold font-anthropic-serif flex items-center gap-1.5 bg-[#c15f3e] hover:bg-[#a84f32] text-white shadow-sm disabled:opacity-50 transition-colors cursor-pointer"
            title="Compile (LaTeX Engine)"
          >
            {isCompiling ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Play className="w-3.5 h-3.5 fill-current" />
            )}
            <span className="sr-only">Biên dịch</span>
            <span className="hidden xs:inline">Compile</span>
          </button>
        </div>
      </header>

      {/* Mobile Segmented View Switcher: [ Editor ] [ PDF ] [ AI ] */}
      <div
        data-testid="mobile-view-switcher"
        className="md:hidden h-11 px-3 border-t border-[#ece8df] dark:border-[#2a2824] bg-white/90 dark:bg-[#181715]/90 backdrop-blur-md flex items-center justify-between shrink-0 select-none z-20"
      >
        <div className="inline-flex p-0.5 rounded-lg bg-[#eee9df] dark:bg-[#24221f] text-xs font-medium border border-[#ded8cc] dark:border-[#33302b] w-full justify-between">
          <button
            type="button"
            data-testid="mobile-tab-editor"
            onClick={() => setMobileActiveTab("editor")}
            className={cn(
              "flex-1 inline-flex items-center justify-center gap-1.5 px-2 py-1.5 min-h-[32px] rounded-md transition-all cursor-pointer text-xs font-medium select-none",
              mobileActiveTab === "editor"
                ? "bg-white dark:bg-[#322f2b] text-[#c15f3e] font-semibold shadow-xs"
                : "text-muted hover:text-ink dark:text-zinc-400"
            )}
          >
            <FileCode className="w-3.5 h-3.5" />
            <span className="sr-only">Soạn thảo</span>
            <span>Editor</span>
          </button>
          <button
            type="button"
            data-testid="mobile-tab-preview"
            onClick={() => setMobileActiveTab("preview")}
            className={cn(
              "flex-1 inline-flex items-center justify-center gap-1.5 px-2 py-1.5 min-h-[32px] rounded-md transition-all cursor-pointer text-xs font-medium select-none",
              mobileActiveTab === "preview"
                ? "bg-white dark:bg-[#322f2b] text-[#c15f3e] font-semibold shadow-xs"
                : "text-muted hover:text-ink dark:text-zinc-400"
            )}
          >
            <FileText className="w-3.5 h-3.5" />
            <span className="sr-only">Xem PDF</span>
            <span>PDF</span>
          </button>
          <button
            type="button"
            data-testid="mobile-tab-assistant"
            onClick={() => setMobileActiveTab("assistant")}
            className={cn(
              "flex-1 inline-flex items-center justify-center gap-1.5 px-2 py-1.5 min-h-[32px] rounded-md transition-all cursor-pointer text-xs font-medium select-none",
              mobileActiveTab === "assistant"
                ? "bg-white dark:bg-[#322f2b] text-[#c15f3e] font-semibold shadow-xs"
                : "text-muted hover:text-ink dark:text-zinc-400"
            )}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span className="sr-only">Trợ lý AI</span>
            <span>AI</span>
          </button>
        </div>
      </div>
    </div>
  );
}
