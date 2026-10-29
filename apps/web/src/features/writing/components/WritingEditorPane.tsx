import { useState, useRef, useMemo, useEffect } from "react";
import {
  AlertTriangle,
  Wand2,
  Copy,
  Check,
  FileCode,
  Bold,
  Italic,
  Table as TableIcon,
  List as ListIcon,
  ListOrdered,
  Heading,
  BookMarked,
  X,
  PanelLeftOpen,
} from "lucide-react";
import { useWritingStore } from "../stores/useWritingStore";
import { draftsApi } from "../api/draftsApi";
import { buildSelectionContextBuffer } from "../lib/contextBuffer";
import { cn } from "@/lib/utils";

interface WritingEditorPaneProps {
  onSelectionAddToChat?: (contextBuffer: string) => void;
  scrollToLine?: number | null;
}

export function WritingEditorPane({
  onSelectionAddToChat,
  scrollToLine,
}: WritingEditorPaneProps) {
  const {
    activeDraftId,
    editorContent,
    setEditorContent,
    editorBibContent,
    setEditorBibContent,
    activeFile,
    setActiveFile,
    openFiles,
    closeFile,
    isFileTreeOpen,
    toggleFileTree,
    setActiveHighlightBox,
    lastCompileResult,
    setSelectionRange: setStoreSelectionRange,
  } = useWritingStore();

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [copied, setCopied] = useState(false);
  const [selectedText, setSelectedText] = useState("");
  const [selectionRange, setSelectionRange] = useState<{ start: number; end: number } | null>(null);

  const currentContent = activeFile === "main.tex" ? editorContent : editorBibContent;

  const lineCount = useMemo(() => {
    return currentContent.split("\n").length;
  }, [currentContent]);

  const jumpToLine = (targetLine: number) => {
    if (!textareaRef.current) return;
    const lines = currentContent.split("\n");
    let charIndex = 0;
    for (let i = 0; i < Math.min(targetLine - 1, lines.length); i++) {
      charIndex += lines[i].length + 1;
    }
    textareaRef.current.focus();
    textareaRef.current.setSelectionRange(
      charIndex,
      charIndex + (lines[targetLine - 1]?.length || 0)
    );
    const lineHeightPx = 20;
    textareaRef.current.scrollTop = Math.max(0, (targetLine - 4) * lineHeightPx);
  };

  // Jump to specific line when requested by Outline or SyncTeX inverse
  useEffect(() => {
    if (scrollToLine) {
      jumpToLine(scrollToLine);
    }
  }, [scrollToLine, currentContent]);

  // Handle Tab key in textarea
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Tab") {
      e.preventDefault();
      const target = e.currentTarget;
      const start = target.selectionStart;
      const end = target.selectionEnd;

      const newContent =
        currentContent.substring(0, start) + "  " + currentContent.substring(end);
      if (activeFile === "main.tex") {
        setEditorContent(newContent);
      } else {
        setEditorBibContent(newContent);
      }

      setTimeout(() => {
        target.selectionStart = target.selectionEnd = start + 2;
        setStoreSelectionRange({ start: start + 2, end: start + 2 });
      }, 0);
    }
  };

  const handleSelect = () => {
    if (!textareaRef.current) return;
    const start = textareaRef.current.selectionStart;
    const end = textareaRef.current.selectionEnd;
    setStoreSelectionRange({ start, end });
    if (start !== end) {
      setSelectedText(currentContent.substring(start, end).trim());
      setSelectionRange({ start, end });
    } else {
      setSelectedText("");
      setSelectionRange(null);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(currentContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Helper for inserting formatting snippets around cursor or selection
  const handleInsertFormat = (prefix: string, suffix: string = "", placeholder: string = "văn bản") => {
    if (!textareaRef.current) return;
    const start = textareaRef.current.selectionStart;
    const end = textareaRef.current.selectionEnd;
    const selected = currentContent.substring(start, end);
    const replacement = `${prefix}${selected || placeholder}${suffix}`;
    const newContent =
      currentContent.substring(0, start) + replacement + currentContent.substring(end);
    if (activeFile === "main.tex") {
      setEditorContent(newContent);
    } else {
      setEditorBibContent(newContent);
    }

    setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.focus();
        textareaRef.current.selectionStart = start + prefix.length;
        textareaRef.current.selectionEnd =
          start + prefix.length + (selected ? selected.length : placeholder.length);
      }
    }, 10);
  };

  const handleAddToChatClick = () => {
    if (!onSelectionAddToChat) return;

    let start = selectionRange?.start ?? -1;
    let end = selectionRange?.end ?? -1;
    if (start === -1 || start === end) {
      start = currentContent.indexOf(selectedText);
      end = start !== -1 ? start + selectedText.length : 0;
    }

    const contextBuffer =
      start !== -1
        ? buildSelectionContextBuffer(currentContent, start, end)
        : `<target_selection>\n${selectedText}\n</target_selection>`;

    onSelectionAddToChat(contextBuffer);
  };

  const errors = lastCompileResult?.errors || [];

  return (
    <div className="flex-1 flex flex-col h-full bg-[#ffffff] dark:bg-[#1a1917] border-r border-[#e8e4dc] dark:border-[#2e2b26] overflow-hidden relative">
      {/* 1. File Tabs Strip & Copy */}
      <div className="h-9 px-2 sm:px-3 border-b border-[#ece8df] dark:border-[#2a2824] bg-[#f7f5f0] dark:bg-[#1e1c19] flex items-center justify-between text-xs select-none shrink-0">
        {/* Tabs: main.tex / references.bib with unhide button when sidebar is collapsed */}
        <div className="flex items-center gap-1 min-w-0">
          {!isFileTreeOpen && (
            <button
              type="button"
              data-testid="unhide-sidebar-btn"
              onClick={toggleFileTree}
              className="p-1 mr-1 rounded hover:bg-[#eae4d9] dark:hover:bg-[#282622] text-[#c15f3e] transition-colors cursor-pointer shrink-0"
              title="Hiện danh sách tệp"
            >
              <PanelLeftOpen className="w-4 h-4" />
            </button>
          )}

          {openFiles.map((file) => {
            const isActive = activeFile === file;
            const isMain = file === "main.tex";
            return (
              <div
                key={file}
                data-testid={isMain ? "editor-tab-main" : "editor-tab-bib"}
                onClick={() => setActiveFile(file)}
                className={cn(
                  "px-2.5 py-1 rounded-t-lg font-mono text-xs flex items-center gap-1.5 transition-colors cursor-pointer border-t-2 shrink-0 group",
                  isActive
                    ? isMain
                      ? "bg-white dark:bg-[#1a1917] text-coral-600 dark:text-coral-400 font-semibold border-coral-500 shadow-2xs"
                      : "bg-white dark:bg-[#1a1917] text-emerald-600 dark:text-emerald-400 font-semibold border-emerald-500 shadow-2xs"
                    : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200 border-transparent hover:bg-[#eee8dd] dark:hover:bg-[#252320]"
                )}
              >
                {isMain ? (
                  <FileCode className="w-3.5 h-3.5 text-coral-600 dark:text-coral-400 shrink-0" />
                ) : (
                  <BookMarked className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
                )}
                <span>{file}</span>
                <button
                  type="button"
                  data-testid={`close-tab-${file}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    closeFile(file);
                  }}
                  className="p-0.5 rounded hover:bg-rose-500/15 hover:text-rose-500 text-zinc-400 dark:text-zinc-500 transition-colors cursor-pointer ml-0.5"
                  title={`Đóng ${file}`}
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            );
          })}
        </div>

        {/* Right side: Copy */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleCopy}
            className="p-1 rounded hover:bg-[#ece8df] dark:hover:bg-[#282623] text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 transition-colors cursor-pointer"
            title="Sao chép toàn bộ code"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* 2. Overleaf-style Rich Formatting Toolbar */}
      <div className="h-8 px-3 border-b border-[#ece8df] dark:border-[#2a2824] bg-[#fbf9f5] dark:bg-[#1c1b18] flex items-center justify-between text-xs text-muted dark:text-zinc-400 select-none overflow-x-auto">
        <div className="flex items-center gap-1">
          {/* Bold */}
          <button
            type="button"
            data-testid="format-bold-btn"
            onClick={() => handleInsertFormat("\\textbf{", "}", "văn bản in đậm")}
            className="p-1 rounded hover:bg-[#eae4d9] dark:hover:bg-[#252320] text-ink dark:text-zinc-200 cursor-pointer"
            title="Định dạng in đậm \\textbf{...}"
          >
            <Bold className="w-3.5 h-3.5" />
          </button>

          {/* Italic */}
          <button
            type="button"
            data-testid="format-italic-btn"
            onClick={() => handleInsertFormat("\\textit{", "}", "văn bản in nghiêng")}
            className="p-1 rounded hover:bg-[#eae4d9] dark:hover:bg-[#252320] text-ink dark:text-zinc-200 cursor-pointer"
            title="Định dạng in nghiêng \\textit{...}"
          >
            <Italic className="w-3.5 h-3.5" />
          </button>

          {/* Math */}
          <button
            type="button"
            data-testid="format-math-btn"
            onClick={() => handleInsertFormat("$", "$", "E = mc^2")}
            className="p-1 rounded hover:bg-[#eae4d9] dark:hover:bg-[#252320] text-ink dark:text-zinc-200 cursor-pointer font-serif italic text-xs font-semibold px-1.5"
            title="Chèn công thức toán học inline $...$"
          >
            Math
          </button>

          {/* Table */}
          <button
            type="button"
            data-testid="format-table-btn"
            onClick={() =>
              handleInsertFormat(
                "\n\\begin{table}[h]\n\\centering\n\\begin{tabular}{|c|c|}\n\\hline\nCột 1 & Cột 2 \\\\\n\\hline\nDữ liệu A & Dữ liệu B \\\\\n\\hline\n\\end{tabular}\n\\caption{Bảng thông số thực nghiệm}\n\\label{tab:results}\n\\end{table}\n",
                "",
                ""
              )
            }
            className="p-1 rounded hover:bg-[#eae4d9] dark:hover:bg-[#252320] text-ink dark:text-zinc-200 cursor-pointer"
            title="Chèn bảng biểu học thuật \\begin{table}..."
          >
            <TableIcon className="w-3.5 h-3.5" />
          </button>

          {/* Itemize List */}
          <button
            type="button"
            data-testid="format-list-btn"
            onClick={() =>
              handleInsertFormat("\n\\begin{itemize}\n  \\item ", "\n\\end{itemize}\n", "Luận điểm thứ nhất")
            }
            className="p-1 rounded hover:bg-[#eae4d9] dark:hover:bg-[#252320] text-ink dark:text-zinc-200 cursor-pointer"
            title="Chèn danh sách đầu dòng \\begin{itemize}..."
          >
            <ListIcon className="w-3.5 h-3.5" />
          </button>

          {/* Enumerate List */}
          <button
            type="button"
            data-testid="format-ordered-btn"
            onClick={() =>
              handleInsertFormat("\n\\begin{enumerate}\n  \\item ", "\n\\end{enumerate}\n", "Bước thực hiện 1")
            }
            className="p-1 rounded hover:bg-[#eae4d9] dark:hover:bg-[#252320] text-ink dark:text-zinc-200 cursor-pointer"
            title="Chèn danh sách đánh số \\begin{enumerate}..."
          >
            <ListOrdered className="w-3.5 h-3.5" />
          </button>

          {/* Section Heading */}
          <button
            type="button"
            data-testid="format-section-btn"
            onClick={() => handleInsertFormat("\n\\section{", "}\n", "Tiêu đề mục mới")}
            className="p-1 rounded hover:bg-[#eae4d9] dark:hover:bg-[#252320] text-ink dark:text-zinc-200 cursor-pointer"
            title="Chèn đề mục \\section{...}"
          >
            <Heading className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Selected text contextual tools */}
        {selectedText && (
          <div className="flex items-center gap-1 bg-coral-500/10 text-coral-700 dark:text-coral-300 px-2 py-0.5 rounded text-[11px] animate-in fade-in shrink-0">
            <span>Đã chọn {selectedText.length} ký tự</span>
            {onSelectionAddToChat && (
              <button
                type="button"
                onClick={handleAddToChatClick}
                className="font-medium hover:underline ml-1 cursor-pointer"
              >
                [Thêm vào Chat]
              </button>
            )}
          </div>
        )}
      </div>

      {/* 3. Editor Body: Code View */}
      <div className="flex-1 flex overflow-hidden relative font-mono text-xs">
        {/* Line numbers gutter */}
        <div className="w-12 py-3 bg-[#f7f5f0] dark:bg-[#161513] border-r border-[#ece8df] dark:border-[#2a2824] select-none text-right pr-2 text-zinc-400 dark:text-zinc-600 overflow-hidden leading-5">
          {Array.from({ length: lineCount }).map((_, i) => {
            const lineNum = i + 1;
            const hasError = errors.some((e) => e.line === lineNum);
            return (
              <div
                key={lineNum}
                onClick={() => hasError && jumpToLine(lineNum)}
                className={cn(
                  "h-5 flex items-center justify-end gap-1 cursor-default",
                  hasError && "text-rose-500 font-bold bg-rose-500/15 cursor-pointer hover:bg-rose-500/25 px-0.5 rounded-xs"
                )}
                title={hasError ? `Lỗi biên dịch tại dòng ${lineNum}. Nhấn để nhảy tới dòng này.` : undefined}
                data-testid={hasError ? `gutter-error-line-${lineNum}` : undefined}
              >
                {hasError && <span className="w-1.5 h-1.5 rounded-full bg-rose-500 inline-block animate-pulse shrink-0" />}
                <span>{lineNum}</span>
              </div>
            );
          })}
        </div>

        {/* Textarea */}
        <textarea
          ref={textareaRef}
          data-testid="writing-editor-textarea"
          aria-label="Soạn thảo mã nguồn LaTeX"
          value={currentContent}
          onChange={(e) => {
            if (activeFile === "main.tex") {
              setEditorContent(e.target.value);
            } else {
              setEditorBibContent(e.target.value);
            }
          }}
          onKeyDown={handleKeyDown}
          onKeyUp={handleSelect}
          onClick={handleSelect}
          onSelect={handleSelect}
          spellCheck={false}
          className="flex-1 p-3 bg-transparent text-ink dark:text-zinc-200 outline-none resize-none leading-5 overflow-auto font-mono text-xs selection:bg-coral-500/20"
        />
      </div>

      {/* Compile Diagnostics / Errors Panel */}
      {errors.length > 0 && (
        <div className="max-h-44 border-t border-rose-500/30 bg-rose-500/5 p-3 overflow-y-auto text-xs shrink-0 select-text">
          <div className="flex items-center gap-1.5 font-semibold text-rose-700 dark:text-rose-400 mb-1.5">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>Phát hiện {errors.length} cảnh báo cú pháp / lỗi biên dịch:</span>
          </div>
          <div className="space-y-1.5 font-mono text-[11px]">
            {errors.map((err, idx) => (
              <div
                key={idx}
                onClick={() => jumpToLine(err.line)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") jumpToLine(err.line);
                }}
                className="p-1.5 bg-white/80 dark:bg-[#201e1a] rounded border border-rose-500/20 text-rose-800 dark:text-rose-300 cursor-pointer hover:bg-rose-500/10 transition-colors"
                title="Nhấn để cuộn đến dòng này trong trình soạn thảo"
                data-testid={`error-item-${err.line}`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold">
                    Dòng {err.line}, Cột {err.column} [{err.rule}]
                  </span>
                </div>
                <div className="mt-0.5 text-zinc-700 dark:text-zinc-300">{err.message}</div>
                {err.suggested_fix && (
                  <div className="mt-1 flex items-center gap-1 text-emerald-700 dark:text-emerald-400">
                    <Wand2 className="w-3 h-3" />
                    <span>Gợi ý sửa: <code>{err.suggested_fix}</code></span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
