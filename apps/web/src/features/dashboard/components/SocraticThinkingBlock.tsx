import { useState, useEffect, useRef } from "react";
import { Brain, Loader2, ChevronDown, ChevronRight } from "lucide-react";
import type { ChatMessage } from "@/types/dashboard";

export interface SocraticThinkingBlockProps {
  message: ChatMessage;
}

/**
 * SocraticThinkingBlock:
 * Minimalist AI reasoning presentation modeled after leading AI research platforms
 * (Claude, DeepSeek, ChatGPT).
 * - During streaming: displays a subtle live stopwatch ("Thought for Xs >") and optional
 *   streaming thought monologue.
 * - When finished: automatically collapses into a clean, single-line header ("Thought for Xs >").
 * - When expanded: reveals the pure internal thought monologue without robotic debug logs.
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
        className="p-2.5 rounded-xl bg-[#f4efe6]/60 dark:bg-[#211f1c]/60 border border-[#e5dfd4] dark:border-[#332f28] text-2xs space-y-2"
      >
        {/* Working status indicator with live timer */}
        <div
          data-testid="socratic-working-status"
          className="flex items-center justify-between text-coral-600 dark:text-coral-400 font-medium"
        >
          <div className="flex items-center gap-2">
            <Loader2 className="w-3.5 h-3.5 animate-spin text-coral-500" />
            <span className="font-mono">{`Thought for ${seconds}s >`}</span>
          </div>
        </div>

        {/* Streaming Thought Text if available */}
        {message.thought && (
          <div
            data-testid="socratic-thought-content"
            className="pt-2 border-t border-hairline/60 dark:border-zinc-800 text-3xs font-sans leading-relaxed whitespace-pre-wrap text-zinc-600 dark:text-zinc-400 italic pl-2 border-l-2 border-coral-500/40"
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
          ? "space-y-2 p-2.5 rounded-xl bg-[#f4efe6]/60 dark:bg-[#211f1c]/60 border border-[#e5dfd4] dark:border-[#332f28] text-2xs"
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
            ? "cursor-pointer font-medium select-none flex items-center justify-between w-full text-ink-muted dark:text-zinc-400 hover:text-ink dark:hover:text-zinc-200 transition-colors"
            : "cursor-pointer font-medium select-none inline-flex items-center gap-1.5 text-ink-muted dark:text-zinc-400 hover:text-ink dark:hover:text-zinc-200 transition-colors text-2xs py-1 px-2 rounded-lg hover:bg-black/5 dark:hover:bg-white/5"
        }
      >
        <div className="flex items-center gap-1.5">
          <Brain className="w-3.5 h-3.5 text-coral-500/80" />
          <span className="font-mono">{`Thought for ${duration}s >`}</span>
        </div>
        {isExpanded ? (
          <ChevronDown className="w-3.5 h-3.5 text-muted dark:text-zinc-400" />
        ) : (
          <ChevronRight className="w-3.5 h-3.5 text-muted dark:text-zinc-400 sr-only" />
        )}
      </button>

      {/* Expanded Thought Monologue */}
      {isExpanded && message.thought && (
        <div
          data-testid="socratic-thought-content"
          className="mt-2 pt-2 border-t border-[#e5dfd4]/60 dark:border-zinc-800 text-3xs font-sans leading-relaxed whitespace-pre-wrap text-zinc-600 dark:text-zinc-400 italic pl-2 border-l-2 border-coral-500/40"
        >
          {message.thought}
        </div>
      )}
    </div>
  );
}
