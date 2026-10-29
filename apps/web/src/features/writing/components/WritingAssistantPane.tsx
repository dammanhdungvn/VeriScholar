import { useState, useRef, useEffect, type KeyboardEvent } from "react";
import {
  Sparkles,
  Loader2,
  Brain,
  ArrowUp,
  X,
  RotateCcw,
  RotateCw,
  Copy,
  Check,
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
  const [copiedMsgId, setCopiedMsgId] = useState<string | null>(null);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-resize textarea up to 160px
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [promptInput]);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isAssisting]);

  // Zero-Click Focus when selection context buffer is passed
  useEffect(() => {
    const promptToSet = externalPrompt !== undefined ? externalPrompt : assistantPrompt;
    if (promptToSet) {
      const timer = setTimeout(() => {
        setPromptInput(promptToSet);
        if (textareaRef.current) {
          textareaRef.current.focus();
          textareaRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [externalPrompt, assistantPrompt]);

  const handleCopy = (msgId: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedMsgId(msgId);
    setTimeout(() => setCopiedMsgId(null), 2000);
  };

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
          const errorMsg =
            typeof err === "string"
              ? err
              : err?.error || err?.message || "Có lỗi xảy ra khi trợ lý AI xử lý yêu cầu.";
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMsgId
                ? {
                    ...msg,
                    content: msg.content
                      ? `${msg.content}\n\n❌ ${errorMsg}`
                      : `❌ ${errorMsg}`,
                  }
                : msg
            )
          );
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

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!isAssisting && promptInput.trim()) {
        handleSendPrompt();
      }
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
    <div className="w-full h-full flex flex-col bg-[#faf9f5] dark:bg-[#181715] overflow-hidden select-none shrink-0 font-anthropic-sans">
      {/* 1. Header with Undo & Close Button */}
      <div className="h-11 px-3.5 border-b border-[#ece8df] dark:border-[#2a2824] bg-[#f5f1e8] dark:bg-[#1e1c19] flex items-center justify-between text-xs font-semibold text-ink dark:text-zinc-200 shrink-0">
        <div className="flex items-center gap-2 font-anthropic-serif">
          <div className="w-5 h-5 rounded-lg bg-coral-500/10 flex items-center justify-center text-coral-600 dark:text-coral-400">
            <Sparkles className="w-3.5 h-3.5" />
          </div>
          <span className="font-semibold text-ink dark:text-zinc-100 tracking-tight">Trợ lý Học thuật AI</span>
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
              "px-2.5 py-1 rounded-lg bg-white dark:bg-[#282622] hover:bg-[#eae4d9] dark:hover:bg-[#302d28] border border-[#e2dcd2] dark:border-[#38332c] text-ink dark:text-zinc-200 text-xs font-sans flex items-center gap-1.5 cursor-pointer disabled:opacity-40 transition-colors shadow-2xs",
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
                <RotateCw className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                <span>Khôi phục (Redo)</span>
              </>
            ) : (
              <>
                <RotateCcw className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
                <span>Hoàn tác</span>
              </>
            )}
          </button>

          {onClose && (
            <button
              type="button"
              data-testid="close-assistant-pane-btn"
              onClick={onClose}
              className="p-1.5 rounded-lg hover:bg-[#eae4d9] dark:hover:bg-[#282622] text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200 transition-colors cursor-pointer"
              title="Ẩn trợ lý AI (X)"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Undo Warning Banner */}
      {undoWarning && (
        <div className="mx-3 mt-2 p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-800 dark:text-amber-200 text-xs flex items-center justify-between animate-in fade-in">
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

      {/* 2. Messages Stream */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 scrollbar-none select-text">
        {messages.length === 0 ? (
          <div
            data-testid="writing-assistant-empty-state"
            className="my-auto flex flex-col items-center justify-center text-center py-12 px-3 select-none space-y-3 max-w-sm mx-auto animate-in fade-in duration-200"
          >
            <div className="w-11 h-11 rounded-2xl bg-coral-500/10 text-coral-600 dark:text-coral-400 flex items-center justify-center border border-coral-500/20 shadow-xs">
              <Sparkles className="w-5 h-5 stroke-[2.2]" />
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-semibold font-anthropic-serif text-ink dark:text-zinc-100">
                Trợ lý Soạn thảo LaTeX Học thuật
              </h3>
              <p className="text-xs text-muted dark:text-zinc-400 leading-relaxed">
                Yêu cầu viết Literature Review từ bài đọc trong Thư viện, chuẩn hóa văn phong hoặc tự động sửa lỗi biên dịch.
              </p>
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={cn(
                "rounded-2xl p-3.5 text-xs leading-relaxed space-y-2 select-text",
                msg.role === "user"
                  ? "bg-[#ede8df] dark:bg-[#282622] text-ink dark:text-zinc-100 ml-8 self-end shadow-2xs"
                  : "bg-white dark:bg-[#201e1a] border border-[#e5dfd4] dark:border-[#2e2b26] text-ink dark:text-zinc-200 mr-2 shadow-xs"
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
                <div className="space-y-2">
                  <div className="whitespace-pre-wrap leading-relaxed font-sans">{msg.content}</div>
                  {msg.role === "assistant" && (
                    <div className="flex items-center justify-end pt-1 border-t border-[#ece8df] dark:border-[#2a2824]">
                      <button
                        type="button"
                        onClick={() => handleCopy(msg.id, msg.content)}
                        className="inline-flex items-center gap-1 text-[11px] text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200 transition-colors cursor-pointer"
                        title="Sao chép nội dung"
                      >
                        {copiedMsgId === msg.id ? (
                          <>
                            <Check className="w-3 h-3 text-emerald-600" />
                            <span>Đã chép</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3" />
                            <span>Sao chép</span>
                          </>
                        )}
                      </button>
                    </div>
                  )}
                </div>
              ) : isAssisting && msg.role === "assistant" ? (
                <div className="flex items-center gap-2 text-muted dark:text-zinc-400 py-1">
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-coral-500" />
                  <span className="text-xs">AI đang tra cứu và soạn thảo nội dung...</span>
                </div>
              ) : null}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 3. AI Writing Assistant Prompt Box (Matches DashboardChatInputBox) */}
      <div className="p-3 border-t border-[#ece8df] dark:border-[#2a2824] bg-[#f5f1e8] dark:bg-[#1c1b18] shrink-0 space-y-2.5">
        {/* Preset chips */}
        <div className="flex flex-wrap gap-1.5">
          {promptPresets.map((preset, i) => (
            <button
              key={i}
              type="button"
              onClick={() => {
                setPromptInput(preset);
                textareaRef.current?.focus();
              }}
              className="text-xs px-2.5 py-1 rounded-full bg-white dark:bg-[#252320] border border-[#e2dcd2] dark:border-[#2e2b26] text-muted hover:text-ink dark:text-zinc-300 hover:border-coral-500/40 transition-all cursor-pointer shadow-2xs whitespace-nowrap"
            >
              {preset}
            </button>
          ))}
        </div>

        {/* Unified ChatGPT / Dashboard-style Chat Pill Box */}
        <div
          data-testid="writing-chat-input-container"
          className="bg-white dark:bg-[#201e1a] rounded-2xl border border-[#e2dcd2] dark:border-[#2e2b26] shadow-xs focus-within:border-coral-500/50 dark:focus-within:border-[#cc785c]/60 focus-within:ring-2 focus-within:ring-coral-500/10 dark:focus-within:ring-[#cc785c]/15 transition-all p-2 flex flex-col gap-1.5"
        >
          <textarea
            ref={textareaRef}
            rows={1}
            value={promptInput}
            onChange={(e) => setPromptInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isAssisting}
            placeholder={
              isAssisting
                ? "AI đang tiến hành phân tích..."
                : "Yêu cầu AI viết tiếp hoặc sửa văn phong..."
            }
            className="w-full text-xs sm:text-sm px-2 pt-1 pb-1 bg-transparent text-ink dark:text-zinc-100 outline-none placeholder:text-muted dark:placeholder:text-zinc-500 resize-none min-h-[38px] max-h-[160px] leading-relaxed disabled:opacity-50"
          />

          <div className="flex items-center justify-between px-1 pt-0.5">
            {/* Socratic Reasoning Indicator Button */}
            <div
              className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-sky-500/10 dark:bg-sky-400/15 text-sky-700 dark:text-sky-300 border border-sky-400/30 text-[11px] font-medium"
              title="Chế độ Socratic Reasoning đang kích hoạt"
            >
              <Brain className="w-3.5 h-3.5 text-sky-600 dark:text-sky-400" />
              <span>Socratic Reasoning</span>
            </div>

            {/* Circular Send Button */}
            <button
              type="button"
              onClick={handleSendPrompt}
              disabled={!promptInput.trim() || isAssisting}
              className={cn(
                "w-7 h-7 rounded-full transition-all duration-150 cursor-pointer flex items-center justify-center",
                promptInput.trim() && !isAssisting
                  ? "bg-ink dark:bg-white text-white dark:text-black hover:scale-105 active:scale-95 shadow-2xs font-bold"
                  : "bg-black/10 dark:bg-white/10 text-muted/40 dark:text-zinc-500 cursor-not-allowed"
              )}
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
