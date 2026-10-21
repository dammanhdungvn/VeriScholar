import { useRef, useState, useEffect, type KeyboardEvent, type ChangeEvent } from "react";
import { Plus, Mic, ArrowUp, Paperclip, X, Brain, RotateCcw } from "lucide-react";
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

interface ReasoningStep {
  step: number;
  title: string;
  subtitle: string;
  effort: string;
  enabled: boolean;
  desc: string;
}

const REASONING_STEPS: ReasoningStep[] = [
  {
    step: 0,
    title: "Tắt",
    subtitle: "Direct Output >",
    effort: "Off",
    enabled: false,
    desc: "Trả lời trực tiếp, không qua phân rã bước suy luận trung gian.",
  },
  {
    step: 1,
    title: "Light",
    subtitle: "5.6 Luna • Fast >",
    effort: "Thấp",
    enabled: true,
    desc: "Suy luận nhanh, kiểm tra tiền đề câu hỏi và lọc dẫn chứng (1-2s).",
  },
  {
    step: 2,
    title: "Medium",
    subtitle: "Socratic 2.5 • Standard >",
    effort: "Tiêu chuẩn",
    enabled: true,
    desc: "Suy luận Socratic chuẩn mực, đối chiếu dẫn chứng đa chiều.",
  },
  {
    step: 3,
    title: "Deep",
    subtitle: "Socratic Deep Reasoning >",
    effort: "Cao",
    enabled: true,
    desc: "Phản biện sâu, chứng minh công thức và kiểm chứng triệt để từng tọa độ PDF.",
  },
];

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
  const popoverRef = useRef<HTMLDivElement>(null);

  const [isPopoverOpen, setIsPopoverOpen] = useState(false);

  const setVoiceModalOpen = useDashboardStore((s) => s.setVoiceModalOpen);
  const isReasoningEnabled = useDashboardStore((s) => s.isReasoningEnabled);
  const toggleReasoning = useDashboardStore((s) => s.toggleReasoning);
  const setReasoningEnabled = useDashboardStore((s) => s.setReasoningEnabled);
  const effortLevel = useDashboardStore((s) => s.effortLevel);
  const setEffortLevel = useDashboardStore((s) => s.setEffortLevel);

  // Close popover when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (popoverRef.current && !popoverRef.current.contains(event.target as Node)) {
        setIsPopoverOpen(false);
      }
    }
    if (isPopoverOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isPopoverOpen]);

  // Current reasoning step calculation
  const currentStepIndex = !isReasoningEnabled
    ? 0
    : effortLevel === "Thấp" || effortLevel === "Light"
    ? 1
    : effortLevel === "Tiêu chuẩn" || effortLevel === "Medium"
    ? 2
    : 3;

  const currentStepData = REASONING_STEPS[currentStepIndex];

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

  const handleReasoningButtonClick = () => {
    toggleReasoning();
    setIsPopoverOpen((prev) => !prev);
  };

  const handleSelectStep = (stepIdx: number) => {
    const step = REASONING_STEPS[stepIdx];
    if (!step.enabled) {
      setReasoningEnabled(false);
      setEffortLevel("Off");
    } else {
      setReasoningEnabled(true);
      setEffortLevel(step.effort);
    }
  };

  const handleResetReasoning = (e: React.MouseEvent) => {
    e.stopPropagation();
    setReasoningEnabled(true);
    setEffortLevel("Cao");
  };

  const hasText = inputText.trim().length > 0;
  const canSend = (hasText || Boolean(contextChip)) && !isGenerating;

  return (
    <div className="w-full max-w-3xl md:max-w-4xl mx-auto px-4 select-text relative">
      {/* ChatGPT/Codex-style Reasoning Popover Card */}
      {isPopoverOpen && (
        <div
          ref={popoverRef}
          data-testid="reasoning-popover"
          className="absolute right-6 bottom-[calc(100%+8px)] z-50 w-72 sm:w-80 p-4 rounded-2xl bg-[#262624] dark:bg-[#1a1918] text-white border border-[#3e3d39] dark:border-[#38342e] shadow-[0_16px_48px_rgba(0,0,0,0.5)] animate-in fade-in zoom-in-95 duration-150 select-none"
        >
          {/* Header with Title, Subtitle, and Reset */}
          <div className="flex items-center justify-between mb-3.5">
            <div className="flex-1 text-center">
              <div className="text-base font-bold text-sky-400 dark:text-sky-300 transition-colors">
                {currentStepData.title}
              </div>
              <div className="text-[11px] text-zinc-400 flex items-center justify-center gap-1 mt-0.5">
                <span>{currentStepData.subtitle}</span>
              </div>
            </div>
            <button
              type="button"
              onClick={handleResetReasoning}
              className="p-1 rounded-full text-zinc-400 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
              title="Đặt lại mức tiêu chuẩn"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* 4-Step Slider Track with Snapping White Thumb */}
          <div className="h-10 w-full bg-[#353533] dark:bg-[#121110] rounded-full relative flex items-center justify-between px-2 cursor-pointer border border-white/5">
            {[0, 1, 2, 3].map((step) => (
              <button
                key={step}
                type="button"
                data-testid={`reasoning-step-btn-${step}`}
                onClick={(e) => {
                  e.stopPropagation();
                  handleSelectStep(step);
                }}
                className="z-10 w-8 h-8 flex items-center justify-center rounded-full hover:bg-white/10 transition-colors cursor-pointer"
                title={REASONING_STEPS[step].title}
              >
                <div
                  className={`w-2 h-2 rounded-full transition-all ${
                    currentStepIndex === step ? "opacity-0" : "bg-zinc-500"
                  }`}
                />
              </button>
            ))}

            {/* Sliding White Circular Thumb */}
            <div
              className="w-7 h-7 rounded-full bg-white shadow-lg absolute transition-all duration-200 ease-out pointer-events-none"
              style={{
                left:
                  currentStepIndex === 0
                    ? "6px"
                    : currentStepIndex === 1
                    ? "calc(33.33% - 4px)"
                    : currentStepIndex === 2
                    ? "calc(66.66% - 18px)"
                    : "calc(100% - 34px)",
              }}
            />
          </div>

          {/* Dynamic Description for Current Reasoning Effort */}
          <p className="text-[11px] text-zinc-400 mt-2.5 text-center leading-relaxed font-sans">
            {currentStepData.desc}
          </p>
        </div>
      )}

      {/* Main Unified ChatGPT-style Chat Pill Box */}
      <div className="bg-[#fbf9f5] dark:bg-[#212120] border border-[#e5dfd4] dark:border-[#38342e] focus-within:border-coral-500/50 dark:focus-within:border-sky-400/50 focus-within:ring-3 focus-within:ring-coral-500/10 dark:focus-within:ring-sky-400/10 rounded-3xl shadow-[0_4px_24px_rgba(0,0,0,0.05)] dark:shadow-[0_8px_32px_rgba(0,0,0,0.45)] transition-all duration-200 overflow-hidden relative">
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
              contextChip
                ? "Đặt câu hỏi về đoạn trích dẫn này hoặc nhấn Enter để giải thích chi tiết..."
                : "Tôi có thể giúp gì cho bạn hôm nay?"
            }
            rows={1}
            className="w-full bg-transparent text-ink dark:text-[#f5f3ed] placeholder-muted/70 dark:placeholder-zinc-500 text-sm sm:text-base focus:outline-none resize-none min-h-[44px] max-h-[220px] leading-relaxed font-anthropic-sans"
          />
        </div>

        {/* Bottom Controls Toolbar Strip */}
        <div className="flex items-center justify-between px-3 pb-2.5 pt-0.5">
          {/* Left Controls: + Attachment icon */}
          <div className="flex items-center gap-1.5">
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
              title="Đính kèm bài báo PDF hoặc tác vụ (+ Do anything)"
              className="w-8 h-8 rounded-full flex items-center justify-center text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-black/5 dark:hover:bg-white/10 transition-colors cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              <span className="sr-only">+ Do anything</span>
            </button>
          </div>

          {/* Right Controls: Reasoning Brain Icon, Mic, Send Button */}
          <div className="flex items-center gap-1.5 sm:gap-2">
            {/* Socratic Reasoning Button with Brain Icon (Pure icon without text) */}
            <button
              type="button"
              onClick={handleReasoningButtonClick}
              data-testid="toggle-reasoning-btn"
              aria-label="Chế độ Suy luận Socratic (Deep Reasoning)"
              title={
                isReasoningEnabled
                  ? `Chế độ Suy luận Socratic (${currentStepData.title}): Đang BẬT. Nhấp để chỉnh mức độ.`
                  : "Chế độ Suy luận Socratic: Đang TẮT. Nhấp để bật."
              }
              className={`w-8 h-8 rounded-full flex items-center justify-center transition-all cursor-pointer relative ${
                isReasoningEnabled
                  ? "bg-sky-500/15 dark:bg-sky-400/20 text-sky-600 dark:text-sky-300 ring-1 ring-sky-400/40 shadow-2xs"
                  : "bg-black/[0.04] dark:bg-white/[0.05] text-muted dark:text-zinc-400 hover:bg-black/[0.08] dark:hover:bg-white/[0.08]"
              }`}
            >
              <Brain
                className={`w-4 h-4 transition-transform ${
                  isReasoningEnabled
                    ? "text-sky-600 dark:text-sky-400 scale-105"
                    : "text-muted dark:text-zinc-400"
                }`}
              />
              {isReasoningEnabled && (
                <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-sky-500 dark:bg-sky-400 ring-2 ring-white dark:ring-[#212120]" />
              )}
              <span className="sr-only">Suy luận Socratic</span>
            </button>

            {/* Voice Input Mic */}
            <button
              type="button"
              onClick={() => setVoiceModalOpen(true)}
              title="Nhập bằng giọng nói"
              className="w-8 h-8 rounded-full flex items-center justify-center text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-black/5 dark:hover:bg-white/10 transition-colors cursor-pointer"
            >
              <Mic className="w-4 h-4" />
            </button>

            {/* Circular Upward Arrow Send Button (ChatGPT/Codex Style) */}
            <button
              type="button"
              onClick={handleSendMessage}
              disabled={!canSend}
              aria-label="Gửi câu hỏi"
              title={canSend ? "Gửi câu hỏi (Enter)" : "Nhập câu hỏi để gửi"}
              className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-200 ${
                canSend
                  ? "bg-ink dark:bg-white text-white dark:text-black shadow-sm hover:scale-105 active:scale-95 cursor-pointer font-bold"
                  : "bg-black/10 dark:bg-white/10 text-muted/40 dark:text-zinc-600 cursor-not-allowed"
              }`}
            >
              <ArrowUp className="w-4 h-4 stroke-[2.5]" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
