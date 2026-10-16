import { useState, useRef, useMemo } from "react";
import {
  AlertTriangle,
  Wand2,
  Copy,
  Check,
  FileCode,
} from "lucide-react";

import { useWritingStore } from "../stores/useWritingStore";
import { buildSelectionContextBuffer } from "../lib/contextBuffer";
import { cn } from "@/lib/utils";

interface WritingEditorPaneProps {
  onSelectionVerify?: (selectedText: string) => void;
  onSelectionAddToChat?: (contextBuffer: string) => void;
  onSelectionAddComment?: (selection: { start: number; end: number; text: string }) => void;
}

export function WritingEditorPane({
  onSelectionVerify,
  onSelectionAddToChat,
  onSelectionAddComment,
}: WritingEditorPaneProps) {
  const {
    editorContent,
    setEditorContent,
    lastCompileResult,
    setSelectionRange: setStoreSelectionRange,
    setCommentsPaneOpen,
  } = useWritingStore();

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [copied, setCopied] = useState(false);
  const [selectedText, setSelectedText] = useState("");
  const [selectionRange, setSelectionRange] = useState<{ start: number; end: number } | null>(null);

  const lineCount = useMemo(() => {
    return editorContent.split("\n").length;
  }, [editorContent]);

  // Handle Tab key in textarea
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Tab") {
      e.preventDefault();
      const target = e.currentTarget;
      const start = target.selectionStart;
      const end = target.selectionEnd;

      const newContent =
        editorContent.substring(0, start) + "  " + editorContent.substring(end);
      setEditorContent(newContent);

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
      setSelectedText(editorContent.substring(start, end).trim());
      setSelectionRange({ start, end });
    } else {
      setSelectedText("");
      setSelectionRange(null);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(editorContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleAddToChatClick = () => {
    if (!onSelectionAddToChat) return;

    let start = selectionRange?.start ?? -1;
    let end = selectionRange?.end ?? -1;
    if (start === -1 || start === end) {
      start = editorContent.indexOf(selectedText);
      end = start !== -1 ? start + selectedText.length : 0;
    }

    const contextBuffer =
      start !== -1
        ? buildSelectionContextBuffer(editorContent, start, end)
        : `<target_selection>\n${selectedText}\n</target_selection>`;

    onSelectionAddToChat(contextBuffer);
  };

  const handleAddCommentClick = () => {
    let start = selectionRange?.start ?? -1;
    let end = selectionRange?.end ?? -1;
    if (start === -1 || start === end) {
      start = editorContent.indexOf(selectedText);
      end = start !== -1 ? start + selectedText.length : 0;
    }
    setStoreSelectionRange({ start, end });
    setCommentsPaneOpen(true);
    onSelectionAddComment?.({ start, end, text: selectedText });
  };

  const errors = lastCompileResult?.errors || [];

  return (
    <div className="flex-1 flex flex-col h-full bg-[#ffffff] dark:bg-[#1a1917] border-r border-[#e8e4dc] dark:border-[#2e2b26] overflow-hidden relative">
      {/* Sub-header toolbar */}
      <div className="h-9 px-4 border-b border-[#ece8df] dark:border-[#2a2824] bg-[#fbf9f5] dark:bg-[#1e1c19] flex items-center justify-between text-xs text-muted dark:text-zinc-400 select-none">
        <div className="flex items-center gap-2 font-mono">
          <FileCode className="w-3.5 h-3.5 text-coral-600 dark:text-coral-400" />
          <span>main.tex</span>
          <span className="text-[11px] text-zinc-400">({lineCount} dòng)</span>
        </div>

        <div className="flex items-center gap-2">
          {selectedText && (
            <div className="flex items-center gap-1 bg-coral-500/10 text-coral-700 dark:text-coral-300 px-2 py-0.5 rounded text-[11px] animate-in fade-in">
              <span>Đã chọn {selectedText.length} ký tự</span>
              {onSelectionVerify && (
                <button
                  type="button"
                  onClick={() => onSelectionVerify(selectedText)}
                  className="font-medium hover:underline ml-1 cursor-pointer"
                >
                  [Kiểm chứng]
                </button>
              )}
              {onSelectionAddToChat && (
                <button
                  type="button"
                  onClick={handleAddToChatClick}
                  className="font-medium hover:underline ml-1 cursor-pointer"
                >
                  [Thêm vào Chat]
                </button>
              )}
              <button
                type="button"
                data-testid="editor-add-comment-btn"
                onClick={handleAddCommentClick}
                className="font-medium hover:underline ml-1 cursor-pointer text-coral-700 dark:text-coral-300"
              >
                [💬 Nhận xét]
              </button>
            </div>
          )}

          <button
            type="button"
            onClick={handleCopy}
            className="p-1 rounded hover:bg-[#ece8df] dark:hover:bg-[#282623] text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 transition-colors"
            title="Sao chép toàn bộ code"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Editor Body: Line numbers + Textarea */}
      <div className="flex-1 flex overflow-hidden relative font-mono text-xs">
        {/* Line numbers gutter */}
        <div className="w-12 py-3 bg-[#f7f5f0] dark:bg-[#161513] border-r border-[#ece8df] dark:border-[#2a2824] select-none text-right pr-2 text-zinc-400 dark:text-zinc-600 overflow-hidden leading-5">
          {Array.from({ length: lineCount }).map((_, i) => {
            const lineNum = i + 1;
            const hasError = errors.some((e) => e.line === lineNum);
            return (
              <div
                key={lineNum}
                className={cn(
                  "h-5",
                  hasError && "text-rose-500 font-bold bg-rose-500/10 rounded-xs"
                )}
              >
                {lineNum}
              </div>
            );
          })}
        </div>

        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={editorContent}
          onChange={(e) => setEditorContent(e.target.value)}
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
                className="p-1.5 bg-white/80 dark:bg-[#201e1a] rounded border border-rose-500/20 text-rose-800 dark:text-rose-300"
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
