import { useRef, useEffect, useState, useMemo } from "react";
import { Copy, Check, ThumbsUp, ThumbsDown, Square, Sparkles, User, BrainCircuit } from "lucide-react";
import type { ChatMessage } from "@/types/dashboard";
import { MathRenderer } from "@/components/shared/MathRenderer";
import { CitationBadge } from "./CitationBadge";
import { PresuppositionBanner } from "./PresuppositionBanner";
import { DashboardChatInputBox } from "./DashboardChatInputBox";

interface DashboardChatStreamViewProps {
  messages: ChatMessage[];
  inputText: string;
  onChangeText: (text: string) => void;
  onSend: (text?: string) => void;
  isGenerating: boolean;
  onStopGeneration: () => void;
  onUploadFile?: (file: File) => void;
}

/**
 * Parses markdown into sequential paragraphs with KaTeX math block/inline support
 */
function FormattedAssistantMessage({ content }: { content: string }) {
  const renderedContent = useMemo(() => {
    // Split by $$...$$ for block math
    const blocks = content.split("$$");

    return blocks.map((chunk, idx) => {
      // Odd indices are block math
      if (idx % 2 === 1) {
        return (
          <div
            key={idx}
            className="my-3 p-3.5 rounded-2xl bg-[#f7f4ee] dark:bg-[#21201d] border border-[#e5dfd4] dark:border-[#38332c] text-center overflow-x-auto text-coral-600 dark:text-amber-400 shadow-2xs"
          >
            <MathRenderer math={chunk.trim()} block />
          </div>
        );
      }

      // Even indices are regular text with possible inline $...$ or **...**
      const lines = chunk.split("\n").filter((l) => l.length > 0);
      return (
        <div key={idx} className="space-y-2.5">
          {lines.map((line, lIdx) => {
            const tokens = line.split(/(\*\*[^*]+\*\*|\$[^$]+\$)/g);

            return (
              <p key={lIdx} className="leading-relaxed text-xs sm:text-sm text-ink dark:text-zinc-200">
                {tokens.map((token, tIdx) => {
                  if (token.startsWith("**") && token.endsWith("**")) {
                    return (
                      <strong key={tIdx} className="font-semibold text-ink dark:text-zinc-100">
                        {token.slice(2, -2)}
                      </strong>
                    );
                  }
                  if (token.startsWith("$") && token.endsWith("$") && token.length > 2) {
                    return (
                      <MathRenderer
                        key={tIdx}
                        math={token.slice(1, -1)}
                        className="text-coral-600 dark:text-amber-400 px-0.5"
                      />
                    );
                  }
                  return token;
                })}
              </p>
            );
          })}
        </div>
      );
    });
  }, [content]);

  return <div className="space-y-3 font-anthropic-sans leading-relaxed">{renderedContent}</div>;
}

export function DashboardChatStreamView({
  messages,
  inputText,
  onChangeText,
  onSend,
  isGenerating,
  onStopGeneration,
  onUploadFile
}: DashboardChatStreamViewProps) {
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
        className="flex-1 overflow-y-auto px-4 sm:px-6 py-6 space-y-6 max-w-4xl w-full mx-auto custom-scrollbar"
      >
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
                  {message.is_streaming && (
                    <span className="inline-flex items-center gap-1 text-coral-600 dark:text-coral-400 animate-pulse">
                      <span className="w-1.5 h-1.5 rounded-full bg-coral-500" />
                      <span>Đang suy luận...</span>
                    </span>
                  )}
                </div>

                {/* Collapsible Reasoning / Thinking Tokens if available */}
                {message.thought && (
                  <details className="group p-2 rounded-xl bg-[#f4efe6]/80 dark:bg-[#211f1c] border border-[#e5dfd4] dark:border-[#332f28] text-2xs font-mono text-muted dark:text-zinc-400">
                    <summary className="cursor-pointer font-medium select-none flex items-center gap-1.5 text-ink dark:text-zinc-300 hover:text-coral-600 dark:hover:text-coral-400 transition-colors">
                      <BrainCircuit className="w-3.5 h-3.5 text-coral-500" />
                      <span>Suy luận</span>
                    </summary>
                    <div className="mt-2 pt-2 border-t border-hairline/60 dark:border-zinc-800 text-3xs font-mono leading-relaxed whitespace-pre-wrap">
                      {message.thought}
                    </div>
                  </details>
                )}

                {/* Socratic Presupposition Alert if detected */}
                {message.presupposition_alert && (
                  <PresuppositionBanner alert={message.presupposition_alert} />
                )}

                {/* Formatted Markdown & KaTeX Math */}
                <FormattedAssistantMessage content={message.content} />

                {/* Interactive Citation Badges */}
                {message.citations && message.citations.length > 0 && (
                  <div className="pt-2 flex flex-wrap items-center gap-1.5">
                    {message.citations.map((cite, cIdx) => (
                      <CitationBadge key={cIdx} citation={cite} />
                    ))}
                  </div>
                )}

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
              <span>Dừng suy luận</span>
            </button>
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
