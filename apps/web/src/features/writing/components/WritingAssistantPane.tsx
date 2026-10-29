import { useState, useRef, useEffect } from "react";
import {
  Sparkles,
  Loader2,
  Brain,
  ArrowUp,
  X,
  RotateCcw,
  RotateCw,
} from "lucide-react";
import { useWritingStore } from "../stores/useWritingStore";
import { draftsApi } from "../api/draftsApi";
import { cn } from "@/lib/utils";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  badges?: string[];
}

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
    activeDraftId,
    draft,
    setDraft,
    setEditorContent,
    setEditorBibContent,
    assistantPrompt,
    setAssistantPrompt,
    isAssisting,
    setAssisting,
    addExecutionBadge,
  } = useWritingStore();

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [promptInput, setPromptInput] = useState("");
  const [undoWarning, setUndoWarning] = useState<string | null>(null);
  const [isUndoing, setIsUndoing] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

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

  const handleUndo = async () => {
    if (!activeDraftId) return;
    try {
      setIsUndoing(true);
      setUndoWarning(null);
      const restored = await draftsApi.undoDraft(activeDraftId);
      if (restored) {
        setEditorContent(restored.content);
        setEditorBibContent(restored.bib_content || "");
        if (draft) {
          setDraft(restored);
        }
      }
    } catch (err: any) {
      const msg =
        err?.message ||
        "Không có bản sao lưu trước đó để thực hiện thao tác hoàn tác.";
      setUndoWarning(msg);
    } finally {
      setIsUndoing(false);
    }
  };

  const handleSendPrompt = async () => {
    if (!promptInput.trim() || !activeDraftId || isAssisting) return;
    const p = promptInput.trim();
    setPromptInput("");
    setAssistantPrompt("");

    const userMsgId = `user-${Date.now()}`;
    const assistantMsgId = `assistant-${Date.now()}`;

    setMessages((prev) => [
      ...prev,
      { id: userMsgId, role: "user", content: p },
      { id: assistantMsgId, role: "assistant", content: "", badges: [] },
    ]);

    setAssisting(true);

    try {
      await draftsApi.streamDraftChat(activeDraftId, p, {
        onBadge: (badge) => {
          addExecutionBadge(badge);
          setMessages((prev) =>
            prev.map((msg) => {
              if (msg.id === assistantMsgId) {
                const currentBadges = msg.badges || [];
                return currentBadges.includes(badge)
                  ? msg
                  : { ...msg, badges: [...currentBadges, badge] };
              }
              return msg;
            })
          );
        },
        onToken: (token) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMsgId
                ? { ...msg, content: msg.content + token }
                : msg
            )
          );
        },
        onComplete: (data) => {
          if (data?.main_tex) {
            setEditorContent(data.main_tex);
          }
          if (data?.bib_content) {
            setEditorBibContent(data.bib_content);
          }
        },
        onError: (err) => {
          console.error("Stream draft chat error:", err);
        },
      });
    } catch (err: any) {
      console.error("Failed to stream chat:", err);
    } finally {
      setAssisting(false);
    }

    if (onSendAssistantPrompt) {
      await onSendAssistantPrompt(p);
    }
  };

  const promptPresets = [
    "Viết Literature Review từ các bài đã đọc",
    "Chuẩn hóa văn phong học thuật",
    "Rà soát tính nhất quán luận điểm",
  ];

  const previousSnapshot = draft?.previous_snapshot;
  const isRedoAvailable = Boolean(previousSnapshot?.redo && !previousSnapshot?.undo);
  const isUndoAvailable = Boolean(
    previousSnapshot?.undo ||
      (!previousSnapshot?.undo && !previousSnapshot?.redo && previousSnapshot?.content)
  );
  const hasSnapshot = isRedoAvailable || isUndoAvailable;

  return (
    <div className="w-full h-full flex flex-col bg-[#fbf9f5] dark:bg-[#181715] overflow-hidden select-none shrink-0">
      {/* 1. Header with Undo & Close Button */}
      <div className="h-10 px-3 border-b border-[#ece8df] dark:border-[#2a2824] bg-[#f5f1e8] dark:bg-[#1e1c19] flex items-center justify-between text-xs font-semibold text-ink dark:text-zinc-200">
        <div className="flex items-center gap-1.5 font-anthropic-serif">
          <Sparkles className="w-4 h-4 text-coral-600 dark:text-coral-400" />
          <span aria-hidden="true">Trợ lý Học thuật AI</span>
          <span className="sr-only">AI Writing Assistant</span>
        </div>

        <div className="flex items-center gap-1.5">
          {/* Symmetrical Undo / Redo Button */}
          <button
            type="button"
            data-testid="undo-draft-btn"
            onClick={handleUndo}
            disabled={isUndoing || isAssisting || !hasSnapshot}
            className={cn(
              "px-2 py-1 rounded-md bg-white dark:bg-[#282622] hover:bg-[#eae4d9] dark:hover:bg-[#302d28] border border-[#e2dcd2] dark:border-[#38332c] text-ink dark:text-zinc-200 text-[11px] font-sans flex items-center gap-1 cursor-pointer disabled:opacity-40 transition-colors shadow-2xs",
              isRedoAvailable && "text-emerald-700 dark:text-emerald-400 border-emerald-500/30"
            )}
            title={
              isRedoAvailable
                ? "Khôi phục lại thay đổi AI vừa sinh (Redo)"
                : "Hoàn tác thay đổi của AI về bản trước"
            }
          >
            {isRedoAvailable ? (
              <>
                <RotateCw className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
                <span>Khôi phục (Redo)</span>
              </>
            ) : (
              <>
                <RotateCcw className="w-3 h-3 text-amber-600 dark:text-amber-400" />
                <span>Hoàn tác</span>
              </>
            )}
          </button>

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

      {/* Undo Warning Banner */}
      {undoWarning && (
        <div className="mx-3 mt-2 p-2 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-800 dark:text-amber-200 text-xs flex items-center justify-between">
          <span className="truncate pr-2">{undoWarning}</span>
          <button
            type="button"
            onClick={() => setUndoWarning(null)}
            className="p-0.5 hover:bg-amber-500/20 rounded cursor-pointer shrink-0"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* 2. Assistant Guidance & Messages Body */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {messages.length === 0 ? (
          <div className="p-4 rounded-xl border border-dashed border-[#e2dcd2] dark:border-[#2e2b26] text-center text-xs text-muted dark:text-zinc-400">
            <Sparkles className="w-6 h-6 text-coral-500 mx-auto mb-1.5" />
            <p className="font-medium text-ink dark:text-zinc-200">
              Hỗ trợ soạn thảo LaTeX học thuật
            </p>
            <p className="text-[11px] mt-1">
              Chọn văn bản trong trình soạn thảo và nhấn "[Thêm vào Chat]" hoặc nhập yêu cầu bên dưới.
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={cn(
                "rounded-xl p-3 text-xs leading-relaxed space-y-2 select-text",
                msg.role === "user"
                  ? "bg-[#eee8dd] dark:bg-[#2a2824] text-ink dark:text-zinc-100 ml-6"
                  : "bg-white dark:bg-[#201e1a] border border-[#e5dfd4] dark:border-[#2e2b26] text-ink dark:text-zinc-200 mr-2 shadow-2xs"
              )}
            >
              {/* Dynamic Execution Badges */}
              {msg.badges && msg.badges.length > 0 && (
                <div className="flex flex-wrap gap-1.5 pb-1">
                  {msg.badges.map((badge, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-sans font-medium bg-coral-500/10 text-coral-700 dark:text-coral-300 border border-coral-500/20 animate-in fade-in"
                    >
                      {badge}
                    </span>
                  ))}
                </div>
              )}

              {/* Message text content */}
              {msg.content ? (
                <div className="whitespace-pre-wrap">{msg.content}</div>
              ) : isAssisting && msg.role === "assistant" ? (
                <div className="flex items-center gap-1.5 text-zinc-400">
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span className="text-[11px]">AI đang tương tác và suy nghĩ...</span>
                </div>
              ) : null}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
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
