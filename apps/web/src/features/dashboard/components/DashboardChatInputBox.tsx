import { useState, useRef, useEffect, type KeyboardEvent, type ChangeEvent } from "react";
import { Plus, Mic, ArrowUp, Paperclip, X, Brain, Loader2, FileText } from "lucide-react";
import { useDashboardStore } from "../stores/useDashboardStore";
import type { ActiveContextChip } from "../stores/useWorkspaceStore";
import { ReasoningPopover } from "./ReasoningPopover";
import { cn } from "@/lib/utils";

export interface DashboardChatInputBoxProps {
  inputText: string;
  onChangeText: (text: string) => void;
  onSend: (text?: string) => void;
  onSendWithFiles?: (text: string, files: File[]) => void;
  isGenerating?: boolean;
  onUploadFile?: (file: File) => void;
  contextChip?: ActiveContextChip | null;
  onRemoveContextChip?: () => void;
  onContextChipClick?: (chip: ActiveContextChip) => void;
  placeholder?: string;
  showReasoning?: boolean;
  mode?: "search" | "chat";
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function DashboardChatInputBox({
  inputText,
  onChangeText,
  onSend,
  onSendWithFiles,
  isGenerating = false,
  onUploadFile,
  contextChip = null,
  onRemoveContextChip,
  onContextChipClick,
  placeholder,
  showReasoning = true,
  mode = "chat",
}: DashboardChatInputBoxProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [isPopoverOpen, setIsPopoverOpen] = useState(false);
  const [stagedFiles, setStagedFiles] = useState<File[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);

  const setVoiceModalOpen = useDashboardStore((s) => s.setVoiceModalOpen);
  const reasoningEffort = useDashboardStore((s) => s.reasoningEffort);

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

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    if (mode === "search") return;
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    if (mode === "search") return;
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    if (mode === "search") return;
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFiles = Array.from(e.dataTransfer.files).filter(
        (f) => f.name.toLowerCase().endsWith(".pdf") || f.type === "application/pdf"
      );
      if (droppedFiles.length > 0) {
        setStagedFiles((prev) => [...prev, ...droppedFiles]);
      }
    }
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFiles = Array.from(e.target.files).filter(
        (f) => f.name.toLowerCase().endsWith(".pdf") || f.type === "application/pdf"
      );
      if (selectedFiles.length > 0) {
        setStagedFiles((prev) => [...prev, ...selectedFiles]);
      }
    }
    e.target.value = "";
  };

  const handleRemoveStagedFile = (index: number) => {
    setStagedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSendMessage = () => {
    if (isGenerating) return;

    if (stagedFiles.length > 0) {
      if (onSendWithFiles) {
        onSendWithFiles(inputText.trim(), stagedFiles);
      } else if (onUploadFile) {
        stagedFiles.forEach(onUploadFile);
        if (inputText.trim()) {
          onSend(inputText.trim());
        }
      }
      setStagedFiles([]);
      onChangeText("");
      return;
    }

    if (contextChip) {
      const quoteHeader = `📎 [${contextChip.documentTitle || "Tài liệu"} - Trang ${contextChip.pageNumber}]: "${contextChip.text}"`;
      const fullPrompt = inputText.trim()
        ? `${quoteHeader}\n\n${inputText.trim()}`
        : `Hãy giải thích chi tiết ý nghĩa và luận điểm trong đoạn trích sau (Trang ${contextChip.pageNumber}):\n\n"${contextChip.text}"`;

      onSend(fullPrompt);
      onChangeText("");
      onRemoveContextChip?.();
    } else if (inputText.trim()) {
      onSend(inputText.trim());
      onChangeText("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleReasoningButtonClick = () => {
    setIsPopoverOpen((prev) => !prev);
  };

  const hasText = inputText.trim().length > 0;
  const hasFiles = stagedFiles.length > 0;
  const canSend = (hasText || hasFiles || Boolean(contextChip)) && !isGenerating;

  return (
    <div className="w-full max-w-3xl md:max-w-4xl mx-auto px-4 select-text relative">
      {/* Main Unified ChatGPT-style Chat Pill Box with Direct Drag & Drop */}
      <div
        data-testid="chat-input-pill-container"
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          "transition-all duration-200 relative rounded-3xl shadow-[0_4px_24px_rgba(0,0,0,0.05)] dark:shadow-[0_8px_32px_rgba(0,0,0,0.45)] border",
          isDragOver
            ? "border-[#cc785c] ring-3 ring-[#cc785c]/25 bg-[#cc785c]/5 dark:bg-[#cc785c]/10"
            : "bg-[#fbf9f5] dark:bg-[#212120] border-[#e5dfd4] dark:border-[#38342e] focus-within:border-coral-500/50 dark:focus-within:border-[#cc785c]/60 focus-within:ring-3 focus-within:ring-coral-500/10 dark:focus-within:ring-[#cc785c]/15"
        )}
      >
        {/* Staged File Attachments (Rule Item 10) */}
        {stagedFiles.length > 0 && (
          <div
            data-testid="staged-files-container"
            className="px-4 pt-3 pb-0 flex flex-wrap gap-2 items-center"
          >
            {stagedFiles.map((file, idx) => (
              <div
                key={`${file.name}-${idx}`}
                data-testid="staged-file-chip"
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-[#ede8df] dark:bg-[#2a2723] border border-[#ded8cd] dark:border-[#3a3630] text-xs text-ink dark:text-zinc-200 animate-in fade-in zoom-in-95 duration-100"
              >
                <FileText className="w-3.5 h-3.5 text-[#cc785c] shrink-0" />
                <span className="font-medium max-w-[160px] truncate" title={file.name}>
                  {file.name}
                </span>
                <span className="text-3xs text-muted dark:text-zinc-400 font-mono">
                  ({formatFileSize(file.size)})
                </span>
                <button
                  type="button"
                  onClick={() => handleRemoveStagedFile(idx)}
                  aria-label={`Xóa tệp ${file.name}`}
                  title="Gỡ tệp này"
                  className="p-0.5 rounded-full hover:bg-black/10 dark:hover:bg-white/10 text-muted hover:text-ink dark:hover:text-zinc-100 transition-colors cursor-pointer"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        )}
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

        {/* Text Input Area */}
        <div className="px-4 pt-3.5 pb-1">
          <textarea
            ref={textareaRef}
            value={inputText}
            onChange={(e) => onChangeText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              placeholder ||
              (contextChip
                ? "Đặt câu hỏi về đoạn trích dẫn này hoặc nhấn Enter để giải thích chi tiết..."
                : "Tôi có thể giúp gì cho bạn hôm nay?")
            }
            rows={1}
            className="w-full bg-transparent text-ink dark:text-[#f5f3ed] placeholder-muted/70 dark:placeholder-zinc-500 text-sm sm:text-base focus:outline-none resize-none min-h-[44px] max-h-[220px] leading-relaxed font-anthropic-sans"
          />
        </div>

        {/* Bottom Controls Toolbar Strip */}
        <div className="flex items-center justify-between px-3 pb-2.5 pt-0.5">
          {/* Left Controls: + Attachment icon (Hidden in search mode, Rule Item 5) */}
          {mode !== "search" ? (
            <div className="flex items-center gap-1.5">
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,application/pdf"
                className="hidden"
                aria-label="Đính kèm bài báo PDF"
                onChange={handleFileChange}
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                title="Đính kèm bài báo PDF hoặc tác vụ (+ Do anything)"
                className="w-8 h-8 rounded-full flex items-center justify-center text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-black/5 dark:hover:bg-white/10 transition-colors cursor-pointer"
              >
                <Plus className="w-4 h-4" />
                <span className="sr-only">+ Do anything</span>
              </button>
            </div>
          ) : (
            <div />
          )}

          {/* Right Controls: Reasoning Brain Icon, Mic, Send Button */}
          <div className="flex items-center gap-1.5 sm:gap-2 relative">
            {showReasoning && (
              <>
                <ReasoningPopover
                  isOpen={isPopoverOpen}
                  onClose={() => setIsPopoverOpen(false)}
                />

                {/* Socratic Reasoning Button with Brain Icon (Pure icon without text) */}
                <button
                  type="button"
                  onClick={handleReasoningButtonClick}
                  data-testid="toggle-reasoning-btn"
                  aria-label="Cài đặt Mức độ Suy luận 5.6 Luna"
                  title={`Mức độ Suy luận: ${reasoningEffort.toUpperCase()}. Nhấp để tinh chỉnh.`}
                  className={`w-8 h-8 rounded-full flex items-center justify-center transition-all cursor-pointer relative ${
                    reasoningEffort !== "light" && reasoningEffort !== "off"
                      ? "bg-sky-500/15 dark:bg-sky-400/20 text-sky-600 dark:text-sky-300 ring-1 ring-sky-400/40 shadow-2xs"
                      : "bg-black/[0.04] dark:bg-white/[0.05] text-muted dark:text-zinc-500 hover:bg-black/[0.08] dark:hover:bg-white/[0.08]"
                  }`}
                >
                  <Brain
                    className={`w-4 h-4 transition-transform ${
                      reasoningEffort !== "light" && reasoningEffort !== "off"
                        ? "text-sky-600 dark:text-sky-400 scale-105"
                        : "text-muted dark:text-zinc-500"
                    }`}
                  />
                  {reasoningEffort !== "light" && reasoningEffort !== "off" && (
                    <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-sky-500 dark:bg-sky-400 ring-2 ring-white dark:ring-[#212120]" />
                  )}
                  <span className="sr-only">Suy luận Socratic</span>
                </button>
              </>
            )}

            {/* Voice Input Mic (Hidden in search mode, Rule Item 5) */}
            {mode !== "search" && (
              <button
                type="button"
                onClick={() => setVoiceModalOpen(true)}
                title="Nhập bằng giọng nói"
                className="w-8 h-8 rounded-full flex items-center justify-center text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-black/5 dark:hover:bg-white/10 transition-colors cursor-pointer"
              >
                <Mic className="w-4 h-4" />
              </button>
            )}

            {/* Circular Upward Arrow Send Button (ChatGPT/Codex Style) */}
            <button
              type="button"
              onClick={handleSendMessage}
              disabled={!canSend}
              aria-label={isGenerating ? "Đang xử lý..." : "Gửi câu hỏi"}
              title={
                isGenerating
                  ? "Đang xử lý..."
                  : canSend
                    ? "Gửi câu hỏi (Enter)"
                    : "Nhập câu hỏi để gửi"
              }
              className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-200 ${
                isGenerating
                  ? "bg-ink dark:bg-white text-white dark:text-black cursor-wait opacity-80"
                  : canSend
                    ? "bg-ink dark:bg-white text-white dark:text-black shadow-sm hover:scale-105 active:scale-95 cursor-pointer font-bold"
                    : "bg-black/10 dark:bg-white/10 text-muted/40 dark:text-zinc-600 cursor-not-allowed"
              }`}
            >
              {isGenerating ? (
                <Loader2 className="w-4 h-4 animate-spin stroke-[2.5]" data-testid="send-spinner" />
              ) : (
                <ArrowUp className="w-4 h-4 stroke-[2.5]" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
