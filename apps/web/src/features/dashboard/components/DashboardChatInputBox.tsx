import { useRef, useEffect, type KeyboardEvent, type ChangeEvent } from "react";
import { Plus, Mic, ArrowUp, Paperclip, X } from "lucide-react";
import { useDashboardStore } from "../stores/useDashboardStore";
import type { ActiveContextChip } from "../stores/useWorkspaceStore";

export interface DashboardChatInputBoxProps {
  inputText: string;
  onChangeText: (text: string) => void;
  onSend: (text?: string) => void;
  isGenerating?: boolean;
  onUploadFile?: (file: File) => void;
  contextChip?: ActiveContextChip | null;
  onRemoveContextChip?: () => void;
  onContextChipClick?: (chip: ActiveContextChip) => void;
}

export function DashboardChatInputBox({
  inputText,
  onChangeText,
  onSend,
  isGenerating = false,
  onUploadFile,
  contextChip = null,
  onRemoveContextChip,
  onContextChipClick,
}: DashboardChatInputBoxProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const setVoiceModalOpen = useDashboardStore((s) => s.setVoiceModalOpen);

  // Auto-resize textarea height up to 240px
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 240)}px`;
    }
  }, [inputText]);

  // Zero-click auto-focus when context chip is attached
  useEffect(() => {
    if (contextChip && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [contextChip]);

  const handleSendMessage = () => {
    if (isGenerating) return;

    if (contextChip) {
      const quoteHeader = `📎 [${contextChip.documentTitle || "Tài liệu"} - Trang ${contextChip.pageNumber}]: "${contextChip.text}"`;
      const fullPrompt = inputText.trim()
        ? `${quoteHeader}\n\n${inputText.trim()}`
        : `Hãy giải thích chi tiết ý nghĩa và luận điểm trong đoạn trích sau (Trang ${contextChip.pageNumber}):\n\n"${contextChip.text}"`;

      onSend(fullPrompt);
      onChangeText("");
      onRemoveContextChip?.();
    } else if (inputText.trim()) {
      onSend();
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onUploadFile) {
      onUploadFile(file);
    }
    e.target.value = "";
  };

  const hasText = inputText.trim().length > 0;
  const canSend = (hasText || Boolean(contextChip)) && !isGenerating;

  return (
    <div className="w-full max-w-3xl md:max-w-4xl mx-auto px-4 select-text">
      <div className="bg-white dark:bg-[#22211e] border border-[#e5dfd5] dark:border-[#38342e] focus-within:border-coral-500/50 dark:focus-within:border-coral-500/60 focus-within:ring-3 focus-within:ring-coral-500/10 rounded-2xl sm:rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-[0_12px_36px_rgba(0,0,0,0.4)] transition-all duration-200 overflow-hidden">
        {/* Context Chip (Zero-Click Contextual Evidence) */}
        {contextChip && (
          <div
            data-testid="context-chip"
            className="px-4 pt-3 pb-0 flex items-center justify-between gap-2"
          >
            <button
              type="button"
              onClick={() => onContextChipClick?.(contextChip)}
              title="Nhấp để chuyển đến trang dẫn chứng trên PDF"
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-coral-50 dark:bg-coral-950/40 border border-coral-200/80 dark:border-coral-800/60 text-xs text-coral-900 dark:text-coral-200 max-w-[calc(100%-28px)] cursor-pointer hover:bg-coral-100/70 dark:hover:bg-coral-900/40 transition-colors text-left"
            >
              <Paperclip className="w-3.5 h-3.5 text-coral-600 dark:text-coral-400 shrink-0" />
              <span className="font-semibold text-coral-800 dark:text-coral-300 shrink-0">
                [{contextChip.documentTitle || "Tài liệu"} • Tr. {contextChip.pageNumber}]
              </span>
              <span className="truncate italic text-muted dark:text-zinc-400">
                "{contextChip.text}"
              </span>
            </button>

            {onRemoveContextChip && (
              <button
                type="button"
                onClick={onRemoveContextChip}
                aria-label="Xóa đoạn trích ngữ cảnh"
                title="Gỡ bỏ đoạn trích"
                className="p-1 rounded-full text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200 hover:bg-surface-soft dark:hover:bg-[#252320] transition-colors cursor-pointer shrink-0"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        )}

        {/* 1. Main Text Input Area */}
        <div className="p-4 sm:p-5 pb-2.5 sm:pb-3">
          <textarea
            ref={textareaRef}
            value={inputText}
            onChange={(e) => onChangeText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              contextChip
                ? "Đặt câu hỏi về đoạn trích dẫn này hoặc nhấn Enter để giải thích chi tiết..."
                : "Tôi có thể giúp gì cho bạn hôm nay?"
            }
            rows={2}
            className="w-full bg-transparent text-ink dark:text-[#f5f3ed] placeholder-muted/80 dark:placeholder-zinc-500 text-sm sm:text-base focus:outline-none resize-none min-h-[52px] max-h-[240px] leading-relaxed font-anthropic-sans"
          />

          {/* 2. Controls Toolbar Strip */}
          <div className="flex items-center justify-between pt-2">
            {/* Left Controls: Attachment */}
            <div className="flex items-center gap-2">
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                className="hidden"
                aria-label="Đính kèm bài báo PDF"
                onChange={handleFileChange}
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                title="Đính kèm bài báo PDF (tối đa 50MB)"
                className="w-8 h-8 flex items-center justify-center text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#f4efe6] dark:hover:bg-[#2e2a25] rounded-xl transition-colors cursor-pointer"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>

            {/* Right Controls: Mic, Send */}
            <div className="flex items-center gap-1.5 sm:gap-2">
              {/* Voice Input Mic */}
              <button
                type="button"
                onClick={() => setVoiceModalOpen(true)}
                title="Nhập bằng giọng nói"
                className="w-8 h-8 flex items-center justify-center text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#f4efe6] dark:hover:bg-[#2e2a25] rounded-xl transition-colors cursor-pointer"
              >
                <Mic className="w-4 h-4" />
              </button>

              {/* Send / Action Button: Always visible, active on input or context chip */}
              <button
                type="button"
                onClick={handleSendMessage}
                disabled={!canSend}
                aria-label="Gửi câu hỏi"
                title={canSend ? "Gửi câu hỏi (Enter)" : "Nhập câu hỏi để gửi"}
                className={`w-8 h-8 flex items-center justify-center rounded-xl transition-all duration-200 cursor-pointer ${
                  canSend
                    ? "bg-coral-500 hover:bg-coral-600 text-white shadow-xs hover:scale-105 active:scale-95"
                    : "bg-black/[0.04] dark:bg-white/[0.06] text-muted/50 dark:text-zinc-600 cursor-not-allowed"
                }`}
              >
                <ArrowUp className="w-4 h-4 stroke-[2.5]" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
