import { useRef, useEffect, type KeyboardEvent, type ChangeEvent } from "react";
import { Plus, Mic, ArrowUp } from "lucide-react";
import { useDashboardStore } from "../stores/useDashboardStore";

interface DashboardChatInputBoxProps {
  inputText: string;
  onChangeText: (text: string) => void;
  onSend: (text?: string) => void;
  isGenerating?: boolean;
  onUploadFile?: (file: File) => void;
}

export function DashboardChatInputBox({
  inputText,
  onChangeText,
  onSend,
  isGenerating = false,
  onUploadFile
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

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (inputText.trim() && !isGenerating) {
        onSend();
      }
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

  return (
    <div className="w-full max-w-3xl md:max-w-4xl mx-auto px-4 select-text">
      <div className="bg-white dark:bg-[#22211e] border border-[#e5dfd5] dark:border-[#38342e] focus-within:border-coral-500/50 dark:focus-within:border-coral-500/60 focus-within:ring-3 focus-within:ring-coral-500/10 rounded-2xl sm:rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-[0_12px_36px_rgba(0,0,0,0.4)] transition-all duration-200 overflow-hidden">
        {/* 1. Main Text Input Area */}
        <div className="p-4 sm:p-5 pb-2.5 sm:pb-3">
          <textarea
            ref={textareaRef}
            value={inputText}
            onChange={(e) => onChangeText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Tìm kiếm tài liệu, kiểm chứng giả thuyết hoặc phân tích phương pháp..."
            rows={2}
            className="w-full bg-transparent text-ink dark:text-[#f5f3ed] placeholder-muted/80 dark:placeholder-zinc-500 text-sm sm:text-base focus:outline-none resize-none min-h-[52px] max-h-[240px] leading-relaxed font-sans"
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

              {/* Send / Action Button: Always visible, active on input */}
              <button
                type="button"
                onClick={() => onSend()}
                disabled={!hasText || isGenerating}
                aria-label="Gửi câu hỏi"
                title={hasText ? "Gửi câu hỏi (Enter)" : "Nhập câu hỏi để gửi"}
                className={`w-8 h-8 flex items-center justify-center rounded-xl transition-all duration-200 cursor-pointer ${
                  hasText && !isGenerating
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
