import React from "react";
import { cn } from "@/lib/utils";

interface TypingWaveIndicatorProps {
  className?: string;
}

/**
 * Minimalist 3-dot typing wave indicator.
 * Displays three staggered bouncing dots inspired by modern chat interfaces (Claude, ChatGPT).
 */
export function TypingWaveIndicator({ className }: TypingWaveIndicatorProps) {
  return (
    <div
      data-testid="typing-wave-indicator"
      className={cn("inline-flex items-center gap-1 py-1 text-ink-muted dark:text-zinc-400", className)}
      aria-label="Đang soạn thảo"
    >
      <span className="w-1.5 h-1.5 rounded-full bg-[#cc785c] dark:bg-coral-400 animate-bounce [animation-delay:-0.3s]" />
      <span className="w-1.5 h-1.5 rounded-full bg-[#cc785c] dark:bg-coral-400 animate-bounce [animation-delay:-0.15s]" />
      <span className="w-1.5 h-1.5 rounded-full bg-[#cc785c] dark:bg-coral-400 animate-bounce" />
    </div>
  );
}
