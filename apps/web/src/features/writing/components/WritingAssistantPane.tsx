import { useState, useRef, useEffect } from "react";
import {
  Sparkles,
  Loader2,
  Brain,
  ArrowUp,
  X,
} from "lucide-react";
import { useWritingStore } from "../stores/useWritingStore";

interface WritingAssistantPaneProps {
  onSendAssistantPrompt?: (prompt: string) => Promise<void>;
  onClose?: () => void;
  externalPrompt?: string;
}

export function WritingAssistantPane({
  onSendAssistantPrompt,
  onClose,
  externalPrompt,
}: WritingAssistantPaneProps) {
  const {
    assistantPrompt,
    setAssistantPrompt,
    isAssisting,
  } = useWritingStore();

  const [promptInput, setPromptInput] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  // Zero-Click Focus when selection context buffer is passed
  useEffect(() => {
    const promptToSet = externalPrompt !== undefined ? externalPrompt : assistantPrompt;
    if (promptToSet) {
      const timer = setTimeout(() => {
        setPromptInput(promptToSet);
        if (inputRef.current) {
          inputRef.current.focus();
          inputRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [externalPrompt, assistantPrompt]);

  const handleSendPrompt = async () => {
    if (!promptInput.trim()) return;
    const p = promptInput;
    setPromptInput("");
    setAssistantPrompt("");
    if (onSendAssistantPrompt) {
      await onSendAssistantPrompt(p);
    }
  };

  const promptPresets = [
    "Viết Literature Review từ các bài đã đọc",
    "Chuẩn hóa văn phong học thuật",
    "Rà soát tính nhất quán luận điểm",
  ];

  return (
    <div className="w-full md:w-80 xl:w-96 flex flex-col h-full bg-[#fbf9f5] dark:bg-[#181715] overflow-hidden select-none shrink-0 border-l border-[#ece8df] dark:border-[#2a2824]">
      {/* 1. Header with Close Button */}
      <div className="h-9 px-3 border-b border-[#ece8df] dark:border-[#2a2824] bg-[#f5f1e8] dark:bg-[#1e1c19] flex items-center justify-between text-xs font-semibold text-ink dark:text-zinc-200">
        <div className="flex items-center gap-1.5 font-anthropic-serif">
          <Sparkles className="w-4 h-4 text-coral-600 dark:text-coral-400" />
          <span aria-hidden="true">Trợ lý Học thuật AI</span>
          <span className="sr-only">AI Writing Assistant</span>
        </div>

        <div className="flex items-center gap-1">
          {onClose && (
            <button
              type="button"
              data-testid="close-assistant-pane-btn"
              onClick={onClose}
              className="p-1 rounded-md hover:bg-[#eae4d9] dark:hover:bg-[#282622] text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200 transition-colors cursor-pointer"
              title="Ẩn trợ lý AI (X)"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* 2. Assistant Guidance Body */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        <div className="p-4 rounded-xl border border-dashed border-[#e2dcd2] dark:border-[#2e2b26] text-center text-xs text-muted dark:text-zinc-400">
          <Sparkles className="w-6 h-6 text-coral-500 mx-auto mb-1.5" />
          <p className="font-medium text-ink dark:text-zinc-200">Hỗ trợ soạn thảo LaTeX học thuật</p>
          <p className="text-[11px] mt-1">
            Chọn văn bản trong trình soạn thảo và nhấn "[Thêm vào Chat]" hoặc nhập yêu cầu bên dưới.
          </p>
        </div>
      </div>

      {/* 3. AI Writing Assistant Prompt Box */}
      <div className="p-3 border-t border-[#ece8df] dark:border-[#2a2824] bg-[#f5f1e8] dark:bg-[#1c1b18] shrink-0 space-y-2">
        {/* Preset chips */}
        <div className="flex flex-wrap gap-1">
          {promptPresets.map((preset, i) => (
            <button
              key={i}
              type="button"
              onClick={() => setPromptInput(preset)}
              className="text-[10px] px-2 py-0.5 rounded-full bg-white dark:bg-[#252320] border border-[#e2dcd2] dark:border-[#2e2b26] text-muted hover:text-ink dark:text-zinc-300 transition-colors cursor-pointer"
            >
              {preset}
            </button>
          ))}
        </div>

        {/* Prompt Input Box */}
        <div className="bg-white dark:bg-[#201e1a] p-1.5 rounded-2xl border border-[#e2dcd2] dark:border-[#2e2b26] shadow-2xs focus-within:border-sky-400/60 dark:focus-within:border-sky-400/50 transition-all flex flex-col gap-1.5">
          <input
            ref={inputRef}
            type="text"
            value={promptInput}
            onChange={(e) => setPromptInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !isAssisting && handleSendPrompt()}
            disabled={isAssisting}
            placeholder={
              isAssisting
                ? "AI đang tạo đề xuất gợi ý..."
                : "Yêu cầu AI viết tiếp hoặc sửa văn phong..."
            }
            className="w-full text-xs px-2.5 pt-1.5 pb-0.5 bg-transparent text-ink dark:text-zinc-100 outline-none placeholder:text-zinc-400 disabled:opacity-50"
          />

          <div className="flex items-center justify-between px-1.5 pb-0.5">
            {/* Socratic Reasoning Pure Icon */}
            <div
              className="w-7 h-7 rounded-full flex items-center justify-center bg-sky-500/15 dark:bg-sky-400/20 text-sky-600 dark:text-sky-300 border border-sky-400/30"
              title="Chế độ Socratic Reasoning đang kích hoạt"
            >
              <Brain className="w-3.5 h-3.5" />
              <span className="sr-only">Socratic Reasoning</span>
            </div>

            {/* Circular Send Button */}
            <button
              type="button"
              onClick={handleSendPrompt}
              disabled={!promptInput.trim() || isAssisting}
              className={`w-7 h-7 rounded-full transition-all duration-150 cursor-pointer flex items-center justify-center ${
                promptInput.trim() && !isAssisting
                  ? "bg-ink dark:bg-white text-white dark:text-black hover:scale-105 active:scale-95 shadow-2xs font-bold"
                  : "bg-black/10 dark:bg-white/10 text-muted/40 dark:text-zinc-500 cursor-not-allowed"
              }`}
              title="Gửi prompt"
            >
              {isAssisting ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <ArrowUp className="w-3.5 h-3.5 stroke-[2.5]" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
