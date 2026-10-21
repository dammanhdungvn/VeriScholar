import { useState, useMemo } from "react";
import {
  FileCode,
  Folder,
  FolderPlus,
  Upload,
  ListTree,
  FilePlus,
  PanelLeftClose,
  Hash,
} from "lucide-react";
import { useWritingStore } from "../stores/useWritingStore";
import { cn } from "@/lib/utils";

interface OutlineItem {
  id: string;
  type: "section" | "subsection" | "subsubsection";
  title: string;
  line: number;
  index: number;
}

interface WritingSidebarProps {
  onSelectOutlineItem?: (line: number, title: string) => void;
  onUploadAsset?: () => void;
}

export function WritingSidebar({
  onSelectOutlineItem,
  onUploadAsset,
}: WritingSidebarProps) {
  const {
    editorContent,
    activeSidebarTab,
    setActiveSidebarTab,
    openAssetModal,
    toggleFileTree,
  } = useWritingStore();

  const [activeFile, setActiveFile] = useState<string>("main.tex");
  const [customFiles, setCustomFiles] = useState<string[]>([]);

  // Parse sections, subsections, subsubsections from editorContent
  const outlineItems = useMemo<OutlineItem[]>(() => {
    if (!editorContent) return [];

    const lines = editorContent.split("\n");
    const items: OutlineItem[] = [];

    const regex = /\\(section|subsection|subsubsection)\*?\{([^}]+)\}/;

    let charCount = 0;
    lines.forEach((lineText, lineIdx) => {
      const match = lineText.match(regex);
      if (match) {
        items.push({
          id: `outline-${lineIdx}-${match[2]}`,
          type: match[1] as "section" | "subsection" | "subsubsection",
          title: match[2].trim(),
          line: lineIdx + 1,
          index: charCount,
        });
      }
      charCount += lineText.length + 1; // +1 for newline
    });

    return items;
  }, [editorContent]);

  const handleAddNewFile = () => {
    const fileName = window.prompt("Nhập tên tệp mới (ví dụ: abstract.tex, appendix.tex):", "section1.tex");
    if (fileName && fileName.trim()) {
      const trimmed = fileName.trim();
      if (!customFiles.includes(trimmed) && trimmed !== "main.tex") {
        setCustomFiles((prev) => [...prev, trimmed]);
      }
    }
  };

  const handleAddNewFolder = () => {
    window.prompt("Nhập tên thư mục mới:", "data");
  };

  return (
    <div
      data-testid="writing-sidebar"
      className="h-full flex flex-col bg-[#fdfcf9] dark:bg-[#1a1917] border-r border-[#e8e4dc] dark:border-[#2e2b26] select-none text-xs overflow-hidden"
    >
      {/* 1. Header Tabs: Files / Outline + Collapse Button */}
      <div className="h-10 px-2 border-b border-[#ece8df] dark:border-[#2a2824] bg-[#f7f5f0] dark:bg-[#1e1c19] flex items-center justify-between shrink-0 gap-1">
        <div className="flex items-center gap-1 flex-1">
          <button
            type="button"
            data-testid="sidebar-tab-files"
            onClick={() => setActiveSidebarTab("files")}
            className={cn(
              "flex-1 py-1 px-2 rounded-md font-medium text-xs flex items-center justify-center gap-1.5 transition-colors cursor-pointer",
              activeSidebarTab === "files"
                ? "bg-white dark:bg-[#282622] text-[#c15f3e] shadow-2xs font-semibold"
                : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200"
            )}
          >
            <Folder className="w-3.5 h-3.5" />
            <span>Files</span>
          </button>

          <button
            type="button"
            data-testid="sidebar-tab-outline"
            onClick={() => setActiveSidebarTab("outline")}
            className={cn(
              "flex-1 py-1 px-2 rounded-md font-medium text-xs flex items-center justify-center gap-1.5 transition-colors cursor-pointer",
              activeSidebarTab === "outline"
                ? "bg-white dark:bg-[#282622] text-[#c15f3e] shadow-2xs font-semibold"
                : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200"
            )}
          >
            <ListTree className="w-3.5 h-3.5" />
            <span>Outline</span>
            {outlineItems.length > 0 && (
              <span className="px-1.5 py-0.2 rounded-full text-[10px] font-mono bg-stone-500/10 text-ink dark:text-zinc-200">
                {outlineItems.length}
              </span>
            )}
          </button>
        </div>

        {/* Collapse button */}
        <button
          type="button"
          data-testid="sidebar-collapse-btn"
          onClick={toggleFileTree}
          className="p-1.5 rounded-md hover:bg-[#eae4d9] dark:hover:bg-[#282622] text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200 transition-colors cursor-pointer shrink-0"
          title="Hide Sidebar"
        >
          <PanelLeftClose className="w-4 h-4" />
        </button>
      </div>

      {/* 2. File Tree Tab View */}
      {activeSidebarTab === "files" && (
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Action buttons toolbar: + File, + Folder, Upload */}
          <div className="p-2 border-b border-[#ece8df] dark:border-[#2a2824] flex items-center gap-1 text-[11px] text-muted dark:text-zinc-400">
            <button
              type="button"
              data-testid="sidebar-new-file-btn"
              onClick={handleAddNewFile}
              className="p-1 rounded hover:bg-[#eae4d9] dark:hover:bg-[#282622] text-ink dark:text-zinc-200 flex items-center gap-1 cursor-pointer transition-colors"
              title="Add File"
            >
              <FilePlus className="w-3.5 h-3.5 text-[#c15f3e]" />
              <span>+ File</span>
            </button>

            <button
              type="button"
              data-testid="sidebar-new-folder-btn"
              onClick={handleAddNewFolder}
              className="p-1 rounded hover:bg-[#eae4d9] dark:hover:bg-[#282622] text-ink dark:text-zinc-200 flex items-center gap-1 cursor-pointer transition-colors"
              title="Add Folder"
            >
              <FolderPlus className="w-3.5 h-3.5 text-zinc-500" />
              <span>+ Folder</span>
            </button>

            <button
              type="button"
              data-testid="sidebar-upload-btn"
              onClick={() => {
                if (onUploadAsset) onUploadAsset();
                else openAssetModal();
              }}
              className="p-1 rounded hover:bg-[#eae4d9] dark:hover:bg-[#282622] text-ink dark:text-zinc-200 flex items-center gap-1 cursor-pointer transition-colors ml-auto"
              title="Upload Assets (.bib, .png, .sty)"
            >
              <Upload className="w-3.5 h-3.5 text-[#c15f3e]" />
              <span>Upload</span>
            </button>
          </div>

          {/* File Tree List */}
          <div className="flex-1 overflow-y-auto p-2 space-y-1 font-mono text-xs">
            {/* main.tex */}
            <button
              type="button"
              data-testid="file-main-tex"
              onClick={() => setActiveFile("main.tex")}
              className={cn(
                "w-full px-2 py-1.5 rounded-lg flex items-center gap-2 text-left transition-colors cursor-pointer",
                activeFile === "main.tex"
                  ? "bg-stone-500/10 text-ink dark:text-zinc-100 font-semibold"
                  : "text-ink dark:text-zinc-200 hover:bg-[#f0ebe0] dark:hover:bg-[#262420]"
              )}
            >
              <FileCode className="w-3.5 h-3.5 text-[#c15f3e] shrink-0" />
              <span className="truncate flex-1">main.tex</span>
              <span className="text-[10px] font-sans px-1 rounded bg-zinc-200/60 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400">
                Main
              </span>
            </button>

            {/* Custom added files */}
            {customFiles.map((file) => (
              <button
                key={file}
                type="button"
                data-testid={`file-${file}`}
                onClick={() => setActiveFile(file)}
                className={cn(
                  "w-full px-2 py-1.5 rounded-lg flex items-center gap-2 text-left transition-colors cursor-pointer",
                  activeFile === file
                    ? "bg-stone-500/10 text-ink dark:text-zinc-100 font-semibold"
                    : "text-ink dark:text-zinc-200 hover:bg-[#f0ebe0] dark:hover:bg-[#262420]"
                )}
              >
                <FileCode className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
                <span className="truncate flex-1">{file}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 3. Outline Tab View */}
      {activeSidebarTab === "outline" && (
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {outlineItems.length === 0 ? (
            <div className="p-4 text-center text-muted dark:text-zinc-500 text-xs">
              <Hash className="w-6 h-6 mx-auto mb-1.5 text-zinc-400 opacity-60" />
              <p>No sections found in document.</p>
              <p className="text-[11px] text-zinc-400 mt-1">
                Add \section&#123;...&#125; to build the outline tree.
              </p>
            </div>
          ) : (
            outlineItems.map((item) => (
              <button
                key={item.id}
                type="button"
                data-testid={`outline-item-${item.line}`}
                onClick={() => onSelectOutlineItem?.(item.line, item.title)}
                className={cn(
                  "w-full py-1.5 px-2 rounded-lg text-left flex items-start gap-1.5 hover:bg-[#f0ebe0] dark:hover:bg-[#262420] transition-colors cursor-pointer group",
                  item.type === "section" && "font-semibold text-ink dark:text-zinc-100",
                  item.type === "subsection" && "pl-5 text-muted dark:text-zinc-300 text-[11px]",
                  item.type === "subsubsection" && "pl-8 text-muted/80 dark:text-zinc-400 text-[10px]"
                )}
                title={`Line ${item.line}`}
              >
                <span className="text-[10px] font-mono text-[#c15f3e] opacity-60 group-hover:opacity-100 pt-0.5">
                  L{item.line}
                </span>
                <span className="truncate flex-1 group-hover:underline">{item.title}</span>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}
