import { useState } from "react";
import { Link } from "react-router-dom";
import {
  Save,
  Play,
  Download,
  Columns3,
  SplitSquareVertical,
  Sidebar,
  Maximize2,
  FileCode,
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  Loader2,
  FolderArchive,
  Share2,
} from "lucide-react";
import { useWritingStore } from "../stores/useWritingStore";
import type { WorkspaceMode } from "../types";
import { cn } from "@/lib/utils";


interface WritingHeaderBarProps {
  onSave?: () => Promise<void>;
  onCompile?: () => Promise<void>;
  onExportBundle?: () => Promise<void>;
  onOpenAssets?: () => void;
  onOpenShare?: () => void;
}

export function WritingHeaderBar({
  onSave,
  onCompile,
  onExportBundle,
  onOpenAssets,
  onOpenShare,
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
    openShareModal,
  } = useWritingStore();

  const [isEditingTitle, setIsEditingTitle] = useState(false);

  const modeButtons: { mode: WorkspaceMode; label: string; icon: typeof Columns3 }[] = [
    { mode: "tri-pane", label: "3 Cột (Code | PDF | AI)", icon: Columns3 },
    { mode: "dual-code", label: "Code & PDF", icon: SplitSquareVertical },
    { mode: "dual-ai", label: "PDF & AI", icon: Sidebar },
    { mode: "zen-pdf", label: "Zen PDF (100%)", icon: Maximize2 },
    { mode: "zen-code", label: "Zen Code (100%)", icon: FileCode },
  ];

  return (
    <header className="h-14 border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#fbf9f5] dark:bg-[#1c1b18] px-4 flex items-center justify-between shrink-0 select-none">
      {/* 1. Left: Navigation back & Title */}
      <div className="flex items-center gap-3 min-w-0">
        <Link
          to="/dashboard"
          className="p-1.5 rounded-lg text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#ece8df] dark:hover:bg-[#282623] transition-colors"
          title="Quay lại Dashboard"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>

        <div className="flex items-center gap-2 min-w-0">
          {isEditingTitle ? (
            <input
              type="text"
              value={editorTitle}
              onChange={(e) => setEditorTitle(e.target.value)}
              onBlur={() => setIsEditingTitle(false)}
              onKeyDown={(e) => e.key === "Enter" && setIsEditingTitle(false)}
              autoFocus
              className="px-2 py-0.5 text-sm font-semibold font-anthropic-serif bg-surface-cream dark:bg-[#24221e] border border-coral-500 rounded text-ink dark:text-zinc-100 outline-none w-64"
            />
          ) : (
            <button
              type="button"
              onClick={() => setIsEditingTitle(true)}
              className="text-sm font-semibold font-anthropic-serif text-ink dark:text-zinc-100 truncate hover:underline text-left cursor-pointer"
              title="Click để đổi tên bản thảo"
            >
              {editorTitle || "Untitled Draft"}
            </button>
          )}

          {draft && (
            <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-zinc-200/60 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400">
              v{draft.version}
            </span>
          )}

          {/* Save Status Indicator */}
          <div className="flex items-center gap-1 text-[11px] text-muted dark:text-zinc-500 ml-1">
            {isSaving ? (
              <span className="flex items-center gap-1 text-amber-600 dark:text-amber-400">
                <Loader2 className="w-3 h-3 animate-spin" /> Đang lưu...
              </span>
            ) : isDirty ? (
              <span className="flex items-center gap-1 text-amber-600 dark:text-amber-400">
                <AlertCircle className="w-3 h-3" /> Chưa lưu
              </span>
            ) : (
              <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
                <CheckCircle2 className="w-3 h-3" /> Đã lưu
              </span>
            )}
          </div>
        </div>
      </div>

      {/* 2. Middle: Workspace Mode Toggles */}
      <div className="hidden lg:flex items-center bg-[#f0eae1] dark:bg-[#252320] p-1 rounded-xl border border-[#e2dcd2] dark:border-[#2e2b26] gap-1">
        {modeButtons.map(({ mode, label, icon: Icon }) => (
          <button
            key={mode}
            type="button"
            onClick={() => setWorkspaceMode(mode)}
            title={label}
            className={cn(
              "px-2.5 py-1 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors cursor-pointer",
              workspaceMode === mode
                ? "bg-white dark:bg-[#181715] text-coral-600 dark:text-coral-400 shadow-xs font-semibold"
                : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100"
            )}
          >
            <Icon className="w-3.5 h-3.5" />
            <span className="text-[11px] hidden xl:inline">{mode.replace("-", " ").toUpperCase()}</span>
          </button>
        ))}
      </div>

      {/* 3. Right: Action Buttons (Assets, Share, Save, Compile, Export Bundle) */}
      <div className="flex items-center gap-2">
        {/* Assets button */}
        <button
          type="button"
          onClick={onOpenAssets || openAssetModal}
          data-testid="header-assets-btn"
          className="h-8 px-2.5 rounded-lg text-xs font-medium flex items-center gap-1.5 bg-[#ece8df] dark:bg-[#262420] text-ink dark:text-zinc-200 hover:bg-[#e4dfd4] dark:hover:bg-[#2d2a26] transition-colors cursor-pointer"
          title="Quản lý assets học thuật (.png, .pdf, .bib, .cls, .sty)"
        >
          <FolderArchive className="w-3.5 h-3.5 text-coral-600 dark:text-coral-400" />
          <span className="hidden md:inline">Assets</span>
        </button>

        {/* Share button */}
        <button
          type="button"
          onClick={onOpenShare || openShareModal}
          data-testid="header-share-btn"
          className="h-8 px-2.5 rounded-lg text-xs font-medium flex items-center gap-1.5 bg-[#ece8df] dark:bg-[#262420] text-ink dark:text-zinc-200 hover:bg-[#e4dfd4] dark:hover:bg-[#2d2a26] transition-colors cursor-pointer"
          title="Chia sẻ bản thảo và phân quyền cộng tác"
        >
          <Share2 className="w-3.5 h-3.5 text-coral-600 dark:text-coral-400" />
          <span className="hidden md:inline">Chia sẻ</span>
        </button>

        {/* Save button */}
        <button
          type="button"
          onClick={onSave}
          disabled={isSaving || !isDirty}
          className="h-8 px-3 rounded-lg text-xs font-medium flex items-center gap-1.5 bg-[#ece8df] dark:bg-[#262420] text-ink dark:text-zinc-200 hover:bg-[#e4dfd4] dark:hover:bg-[#2d2a26] disabled:opacity-50 transition-colors cursor-pointer"
          title="Lưu bản thảo (Ctrl+S / ⌘S)"
        >
          {isSaving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
          <span>Lưu</span>
        </button>

        {/* Compile button */}
        <button
          type="button"
          onClick={onCompile}
          disabled={isCompiling}
          className="h-8 px-3 rounded-lg text-xs font-medium flex items-center gap-1.5 bg-coral-500 hover:bg-coral-600 text-white shadow-xs disabled:opacity-50 transition-colors cursor-pointer"
          title="Biên dịch Sandbox & Tự vá lỗi (LaTeX Engine)"
        >
          {isCompiling ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Play className="w-3.5 h-3.5 fill-current" />
          )}
          <span>Biên dịch</span>
        </button>

        {/* Export submission bundle (.zip) */}
        <button
          type="button"
          onClick={onExportBundle}
          className="h-8 px-3 rounded-lg text-xs font-medium flex items-center gap-1.5 bg-[#2d6a4f] hover:bg-[#245640] text-white shadow-xs transition-colors cursor-pointer"
          title="Xuất gói nộp bài chuẩn học thuật quốc tế (.zip: main.tex, references.bib, preview.pdf)"
        >
          <Download className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Xuất Gói Nộp Bài</span>
        </button>
      </div>
    </header>
  );
}
