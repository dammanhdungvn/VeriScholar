import { useRef, useEffect, useState } from "react";
import { Copy, Check, ThumbsUp, ThumbsDown, Square, Sparkles, User, Brain } from "lucide-react";
import type { ChatMessage } from "@/types/dashboard";
import { AcademicMarkdownRenderer } from "@/components/shared/AcademicMarkdownRenderer";
import { TypingWaveIndicator } from "@/components/shared/TypingWaveIndicator";
import { PresuppositionBanner } from "./PresuppositionBanner";
import { DashboardChatInputBox } from "./DashboardChatInputBox";
import { useDashboardStore } from "../stores/useDashboardStore";
import { useReaderStore } from "@/features/reader/stores/useReaderStore";

interface DashboardChatStreamViewProps {
  messages: ChatMessage[];
  inputText: string;
  onChangeText: (text: string) => void;
  onSend: (text?: string) => void;
  isGenerating: boolean;
  onStopGeneration: () => void;
  onUploadFile?: (file: File) => void;
  onOpenReferences?: () => void;
}

export function DashboardChatStreamView({
  messages,
  inputText,
  onChangeText,
  onSend,
  isGenerating,
  onStopGeneration,
  onUploadFile,
  onOpenReferences: _onOpenReferences,
}: DashboardChatStreamViewProps) {
  const setActiveBbox = useDashboardStore((s) => s.setActiveBbox);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [copiedMsgId, setCopiedMsgId] = useState<string | null>(null);

  // Auto scroll to bottom when messages update
  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
    }
  }, [messages, isGenerating]);

  const handleCopy = (msgId: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedMsgId(msgId);
    setTimeout(() => setCopiedMsgId(null), 2000);
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#faf9f5] dark:bg-[#181715] select-text relative">
      {/* 1. Scrollable Messages Stream */}
      <div
        ref={scrollContainerRef}
        className="flex-1 overflow-y-auto px-4 sm:px-6 py-6 space-y-6 max-w-4xl w-full mx-auto scrollbar-none"
      >
        {messages.length === 0 && (
          <div
            data-testid="chat-empty-state"
            className="flex-1 flex flex-col items-center justify-center text-center py-12 px-4 select-none space-y-4 max-w-lg mx-auto my-auto animate-in fade-in duration-200"
          >
            <div className="w-12 h-12 rounded-2xl bg-coral-500/10 text-coral-600 dark:text-coral-400 flex items-center justify-center border border-coral-500/20 shadow-xs">
              <Sparkles className="w-6 h-6" />
            </div>

            <div className="space-y-1.5">
              <h3 className="font-serif font-semibold text-base text-ink dark:text-zinc-100">
                Socratic Copilot sẵn sàng đối thoại
              </h3>
              <p className="text-xs text-muted dark:text-zinc-400 leading-relaxed font-sans max-w-md mx-auto">
                Đặt câu hỏi nghiên cứu hoặc chọn gợi ý để đối thoại phản biện.
              </p>
            </div>

            {/* Empty state hint chips grid */}
            <div className="w-full pt-3 grid grid-cols-1 sm:grid-cols-2 gap-2 text-left relative z-20 pointer-events-auto">
              {[
                {
                  label: "Tóm tắt paper",
                  prompt: "Hãy tóm tắt ngắn gọn và toàn diện nội dung bài báo này (mục tiêu, phương pháp chính và kết luận).",
                },
                {
                  label: "Đóng góp chính",
                  prompt: "Những đóng góp và điểm mới cốt lõi (key contributions) của nghiên cứu này là gì?",
                },
                {
                  label: "Phương pháp & Kiến trúc",
                  prompt: "Giải thích chi tiết phương pháp nghiên cứu và kiến trúc mô hình được đề xuất trong bài báo.",
                },
                {
                  label: "Hạn chế & Thách thức",
                  prompt: "Những hạn chế và thách thức chính của nghiên cứu này là gì, và các tác giả gợi ý hướng phát triển ra sao?",
                },
              ].map((item, idx) => (
                <button
                  key={idx}
                  type="button"
                  data-testid={`empty-hint-chip-${idx}`}
                  onClick={() => {
                    onChangeText(item.prompt);
                    onSend(item.prompt);
                  }}
                  className="flex items-center gap-2 p-3 rounded-xl border border-[#e5dfd4] dark:border-[#38332c] bg-white dark:bg-[#201e1a] hover:border-coral-500/60 hover:bg-coral-500/5 transition-all cursor-pointer shadow-2xs text-left group active:scale-95 select-none"
                >
                  <Sparkles className="w-3.5 h-3.5 text-coral-600 dark:text-coral-400 shrink-0" />
                  <span className="text-xs font-semibold text-ink dark:text-zinc-200 group-hover:text-coral-600 dark:group-hover:text-coral-400">
                    {item.label}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message) => {
          const isUser = message.role === "user";

          if (isUser) {
            return (
              <div key={message.id} className="flex justify-end">
                <div className="max-w-2xl px-4 sm:px-5 py-3 rounded-2xl rounded-tr-xs bg-white dark:bg-[#252320] border border-[#e8e4dc] dark:border-[#38332c] text-ink dark:text-zinc-100 text-xs sm:text-sm font-anthropic-sans shadow-xs">
                  <div className="flex items-center gap-1.5 text-3xs font-mono text-muted dark:text-zinc-400 mb-1.5">
                    <User className="w-3 h-3 text-coral-600 dark:text-coral-400" />
                    <span className="font-medium">Học giả</span>
                  </div>
                  <div className="leading-relaxed whitespace-pre-wrap">{message.content}</div>
                </div>
              </div>
            );
          }

          return (
            <div key={message.id} className="flex gap-3.5 max-w-3xl">
              {/* Socratic Avatar Emblem */}
              <div className="w-8 h-8 rounded-xl bg-coral-500/10 border border-coral-500/20 text-coral-600 dark:text-coral-400 flex items-center justify-center shrink-0 mt-1 shadow-2xs">
                <Sparkles className="w-4 h-4" />
              </div>

              {/* Assistant Message Body */}
              <div className="flex-1 space-y-3 min-w-0">
                <div className="text-3xs font-mono font-medium text-muted dark:text-zinc-500 flex items-center gap-2">
                  <span className="font-semibold text-ink dark:text-zinc-300 font-anthropic-sans">Socratic</span>
                </div>

                {/* Collapsible Reasoning / Thinking Tokens if available */}
                {message.thought && (
                  <details
                    open={Boolean(message.is_streaming && !message.content)}
                    data-testid="reasoning-accordion"
                    className="group p-2 rounded-xl bg-[#f4efe6]/80 dark:bg-[#211f1c] border border-[#e5dfd4] dark:border-[#332f28] text-2xs font-mono text-muted dark:text-zinc-400"
                  >
                    <summary className="cursor-pointer font-medium select-none flex items-center justify-between text-ink dark:text-zinc-300 hover:text-coral-600 dark:hover:text-coral-400 transition-colors">
                      <div className="flex items-center gap-1.5">
                        <Brain className="w-3.5 h-3.5 text-coral-500" />
                        <span aria-hidden="true">Suy luận</span>
                        <span className="sr-only">Suy luận học thuật</span>
                      </div>
                      {message.is_streaming && !message.content && (
                        <span className="text-3xs text-coral-600 dark:text-coral-400 animate-pulse">
                          Đang tư duy...
                        </span>
                      )}
                    </summary>
                    <div className="mt-2 pt-2 border-t border-hairline/60 dark:border-zinc-800 text-3xs font-mono leading-relaxed whitespace-pre-wrap text-zinc-700 dark:text-zinc-300">
                      {message.thought}
                    </div>
                  </details>
                )}

                {/* Pre-content Typing Wave Indicator */}
                {message.is_streaming && !message.content && !message.thought && (
                  <div className="py-1">
                    <TypingWaveIndicator />
                  </div>
                )}

                {/* Socratic Presupposition Alert if detected */}
                {message.presupposition_alert && (
                  <PresuppositionBanner alert={message.presupposition_alert} />
                )}

                {/* Formatted Markdown, KaTeX Math & Inline Citations */}
                <AcademicMarkdownRenderer
                  content={message.content}
                  isStreaming={message.is_streaming}
                  citations={message.citations}
                  onCitationClick={(citationOrId, maybeCitId) => {
                    const citId = typeof citationOrId === "string" ? citationOrId : (maybeCitId || "");
                    let matched = typeof citationOrId === "object" ? citationOrId : null;
                    if (!matched && message.citations && message.citations.length > 0) {
                      matched = message.citations.find(
                        (c) => c.citation_id === citId || c.citation_id === `cit_${citId}`
                      ) || null;
                      if (!matched && citId) {
                        const numericPart = citId.replace(/\D/g, "");
                        if (numericPart) {
                          const idx = parseInt(numericPart, 10) - 1;
                          if (!isNaN(idx) && message.citations[idx]) {
                            matched = message.citations[idx];
                          }
                        }
                      }
                      if (!matched && message.citations.length === 1) {
                        matched = message.citations[0];
                      }
                    }
                    if (matched?.bbox) {
                      const targetPage = matched.bbox[4] || matched.page || 1;
                      useReaderStore.getState().setCurrentPage(targetPage);
                      setActiveBbox(matched.bbox);
                    } else if (matched?.page) {
                      useReaderStore.getState().setCurrentPage(matched.page);
                    }
                  }}
                />

                {/* Action Toolbar */}
                {!message.is_streaming && (
                  <div className="flex items-center gap-1.5 pt-1.5 text-muted dark:text-zinc-500 text-xs">
                    <button
                      type="button"
                      onClick={() => handleCopy(message.id, message.content)}
                      title="Sao chép câu trả lời"
                      className="p-1.5 rounded-lg hover:bg-white dark:hover:bg-[#252320] border border-transparent hover:border-[#e5dfd4] dark:hover:border-[#38332c] hover:text-ink dark:hover:text-zinc-200 transition-all cursor-pointer"
                    >
                      {copiedMsgId === message.id ? (
                        <Check className="w-3.5 h-3.5 text-emerald-500" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                    </button>
                    <button
                      type="button"
                      title="Hữu ích"
                      className="p-1.5 rounded-lg hover:bg-white dark:hover:bg-[#252320] border border-transparent hover:border-[#e5dfd4] dark:hover:border-[#38332c] hover:text-ink dark:hover:text-zinc-200 transition-all cursor-pointer"
                    >
                      <ThumbsUp className="w-3.5 h-3.5" />
                    </button>
                    <button
                      type="button"
                      title="Chưa chính xác"
                      className="p-1.5 rounded-lg hover:bg-white dark:hover:bg-[#252320] border border-transparent hover:border-[#e5dfd4] dark:hover:border-[#38332c] hover:text-ink dark:hover:text-zinc-200 transition-all cursor-pointer"
                    >
                      <ThumbsDown className="w-3.5 h-3.5" />
                    </button>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* 2. Floating Bottom Input Area & Stop Button */}
      <div className="shrink-0 pb-5 pt-2 bg-gradient-to-t from-[#faf9f5] via-[#faf9f5]/90 to-transparent dark:from-[#181715] dark:via-[#181715]/90">
        {isGenerating && (
          <div className="flex justify-center mb-2.5">
            <button
              type="button"
              onClick={onStopGeneration}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-white dark:bg-[#252320] border border-[#e5dfd4] dark:border-zinc-700/60 text-ink dark:text-zinc-200 text-xs font-sans shadow-xs hover:bg-[#f4efe6] dark:hover:bg-[#2e2a25] transition-colors cursor-pointer"
            >
              <Square className="w-3 h-3 fill-current text-coral-500" />
              <span>Dừng</span>
            </button>
          </div>
        )}

        {/* Prompt Suggestions Pills above input box */}
        {messages.length === 0 && !isGenerating && (
          <div className="w-full max-w-3xl md:max-w-4xl mx-auto px-4 mb-2.5 relative z-20 pointer-events-auto">
            <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none flex-nowrap touch-pan-x py-1">
              {[
                {
                  label: "Tóm tắt paper",
                  prompt: "Hãy tóm tắt ngắn gọn và toàn diện nội dung bài báo này (mục tiêu, phương pháp chính và kết luận).",
                },
                {
                  label: "Đóng góp chính",
                  prompt: "Những đóng góp và điểm mới cốt lõi (key contributions) của nghiên cứu này là gì?",
                },
                {
                  label: "Phương pháp & Kiến trúc",
                  prompt: "Giải thích chi tiết phương pháp nghiên cứu và kiến trúc mô hình được đề xuất trong bài báo.",
                },
                {
                  label: "Hạn chế & Thách thức",
                  prompt: "Những hạn chế và thách thức chính của nghiên cứu này là gì, và các tác giả gợi ý hướng phát triển ra sao?",
                },
              ].map((item, idx) => (
                <button
                  key={idx}
                  type="button"
                  data-testid={`bottom-hint-chip-${idx}`}
                  onClick={() => {
                    onChangeText(item.prompt);
                    onSend(item.prompt);
                  }}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-sans border border-[#e5dfd4] dark:border-[#38342e] bg-white/90 dark:bg-[#22211e] text-ink-muted dark:text-zinc-400 hover:text-ink dark:hover:text-zinc-100 hover:border-coral-500/50 hover:bg-[#f6f2ea] dark:hover:bg-[#2b2722] transition-all cursor-pointer shrink-0 shadow-2xs whitespace-nowrap active:scale-95 select-none"
                >
                  <Sparkles className="w-3 h-3 text-coral-500 shrink-0" />
                  <span>{item.label}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        <DashboardChatInputBox
          inputText={inputText}
          onChangeText={onChangeText}
          onSend={onSend}
          isGenerating={isGenerating}
          onUploadFile={onUploadFile}
        />
      </div>
    </div>
  );
}
