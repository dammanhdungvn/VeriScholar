import { useState, useEffect, useRef } from "react";
import { Brain, Check, Loader2, ChevronDown, ChevronRight } from "lucide-react";
import type { ChatMessage } from "@/types/dashboard";

export interface SocraticThinkingBlockProps {
  message: ChatMessage;
}

/**
 * SocraticThinkingBlock:
 * Live agent activity stepper during streaming inference, displaying live stopwatch,
 * chunk retrieval, and grounding actions. Automatically collapses into a sleek single-line
 * header ("Thought for Xs >") when inference concludes, with expandable action history
 * and full chain-of-thought internal monologue.
 */
export function SocraticThinkingBlock({ message }: SocraticThinkingBlockProps) {
  const isStreaming = Boolean(message.is_streaming);
  const [isExpanded, setIsExpanded] = useState(false);

  const [seconds, setSeconds] = useState(() => {
    if (typeof message.thought_duration_seconds === "number") {
      return message.thought_duration_seconds;
    }
    if (message.created_at) {
      const diff = Math.floor(
        (Date.now() - new Date(message.created_at).getTime()) / 1000
      );
      return Math.max(1, diff);
    }
    return 1;
  });

  // Track elapsed seconds live while streaming
  useEffect(() => {
    if (!isStreaming) return;
    const timer = setInterval(() => {
      setSeconds((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [isStreaming]);

  // When streaming transitions to false, auto-collapse into single-line header
  const prevStreamingRef = useRef(isStreaming);
  useEffect(() => {
    if (prevStreamingRef.current && !isStreaming) {
      setIsExpanded(false);
    }
    prevStreamingRef.current = isStreaming;
  }, [isStreaming]);

  // If message has no thought and is not streaming, do not render
  if (!message.thought && !isStreaming) {
    return null;
  }

  const duration =
    typeof message.thought_duration_seconds === "number"
      ? message.thought_duration_seconds
      : seconds;

  // Active state during streaming
  if (isStreaming) {
    return (
      <div
        data-testid="socratic-thinking-block"
        className="p-2.5 rounded-xl bg-[#f4efe6]/80 dark:bg-[#211f1c] border border-[#e5dfd4] dark:border-[#332f28] text-2xs font-mono space-y-2"
      >
        {/* Working status indicator */}
        <div
          data-testid="socratic-working-status"
          className="flex items-center gap-2 text-coral-600 dark:text-coral-400 font-medium"
        >
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
          <span>Working...</span>
        </div>

        {/* Live activity stepper */}
        <div
          data-testid="socratic-activity-stepper"
          className="space-y-1 text-3xs text-muted dark:text-zinc-400 pl-4 border-l border-coral-400/40 dark:border-coral-500/40"
        >
          <div className="flex items-center gap-1.5 text-ink dark:text-zinc-300">
            <Check className="w-3 h-3 text-emerald-500 shrink-0" />
            <span>Reading paper chunks... ∨</span>
          </div>
          <div className="flex items-center gap-1.5 text-coral-600 dark:text-coral-400">
            <Brain className="w-3 h-3 text-coral-500 shrink-0 animate-pulse" />
            <span>{`Thought for ${seconds}s >`}</span>
          </div>
          {message.citations?.map((c, idx) => (
            <div
              key={c.citation_id || idx}
              className="flex items-center gap-1.5 text-ink dark:text-zinc-300"
            >
              <Check className="w-3 h-3 text-emerald-500 shrink-0" />
              <span>{`Analyzed Bounding Box #Page ${c.page}`}</span>
            </div>
          ))}
        </div>

        {/* Streaming Thought Text if available */}
        {message.thought && (
          <div
            data-testid="socratic-thought-content"
            className="mt-2 pt-2 border-t border-hairline/60 dark:border-zinc-800 text-3xs font-mono leading-relaxed whitespace-pre-wrap text-zinc-700 dark:text-zinc-300"
          >
            {message.thought}
          </div>
        )}
      </div>
    );
  }

  // Finished state: single-line collapsible header
  return (
    <div
      data-testid="socratic-thinking-block"
      className={
        isExpanded
          ? "space-y-2 p-2.5 rounded-xl bg-[#f4efe6]/80 dark:bg-[#211f1c] border border-[#e5dfd4] dark:border-[#332f28] text-2xs font-mono"
          : undefined
      }
    >
      <button
        type="button"
        onClick={() => setIsExpanded((prev) => !prev)}
        data-testid="socratic-thinking-header"
        aria-expanded={isExpanded}
        className={
          isExpanded
            ? "cursor-pointer font-medium select-none flex items-center justify-between w-full text-ink dark:text-zinc-300 hover:text-coral-600 dark:hover:text-coral-400 transition-colors"
            : "cursor-pointer font-medium select-none flex items-center gap-1.5 text-ink dark:text-zinc-300 hover:text-coral-600 dark:hover:text-coral-400 transition-colors text-2xs font-mono py-1 px-2 rounded-lg hover:bg-black/5 dark:hover:bg-white/5"
        }
      >
        <div className="flex items-center gap-1.5">
          <Brain className="w-3.5 h-3.5 text-coral-500" />
          <span>{`Thought for ${duration}s ${isExpanded ? "∨" : ">"}`}</span>
        </div>
        {isExpanded ? (
          <ChevronDown className="w-3.5 h-3.5 text-muted dark:text-zinc-400" />
        ) : (
          <ChevronRight className="w-3.5 h-3.5 text-muted dark:text-zinc-400 sr-only" />
        )}
      </button>

      {/* Expanded Action History & Thought Monologue */}
      {isExpanded && (
        <>
          <div
            data-testid="socratic-action-history"
            className="space-y-1 text-3xs text-muted dark:text-zinc-400 pl-4 border-l border-zinc-200 dark:border-zinc-800"
          >
            <div className="flex items-center gap-1.5">
              <Check className="w-3 h-3 text-emerald-500 shrink-0" />
              <span>Reading paper chunks...</span>
            </div>
            {message.citations?.map((c, idx) => (
              <div
                key={c.citation_id || idx}
                className="flex items-center gap-1.5"
              >
                <Check className="w-3 h-3 text-emerald-500 shrink-0" />
                <span>{`Analyzed Bounding Box #Page ${c.page}`}</span>
              </div>
            ))}
          </div>

          {message.thought && (
            <div
              data-testid="socratic-thought-content"
              className="mt-2 pt-2 border-t border-hairline/60 dark:border-zinc-800 text-3xs font-mono leading-relaxed whitespace-pre-wrap text-zinc-700 dark:text-zinc-300"
            >
              {message.thought}
            </div>
          )}
        </>
      )}
    </div>
  );
}
