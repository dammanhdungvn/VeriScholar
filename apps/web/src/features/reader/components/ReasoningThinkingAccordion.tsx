import { useState } from "react";
import { ChevronDown, ChevronRight, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ReasoningThinkingAccordionProps {
  thoughtContent?: string;
  isStreaming?: boolean;
  defaultExpanded?: boolean;
  className?: string;
}

/**
 * Scholarly Chain-of-Thought Reasoning Accordion:
 * Displays active thinking state with shimmer animation during streaming inference,
 * and collapses into a "✓ Thinking Finished" accordion once reasoning concludes.
 */
export function ReasoningThinkingAccordion({
  thoughtContent = "",
  isStreaming = false,
  defaultExpanded = false,
  className,
}: ReasoningThinkingAccordionProps) {
  const [isOpen, setIsOpen] = useState(defaultExpanded);

  // If there is no thought content and not streaming, do not render
  if (!thoughtContent && !isStreaming) {
    return null;
  }

  const toggleOpen = () => {
    setIsOpen((prev) => !prev);
  };

  return (
    <div
      data-testid="reasoning-thinking-accordion"
      className={cn(
        "rounded-xl border border-hairline/70 dark:border-zinc-800 bg-sand-50/70 dark:bg-zinc-900/60 overflow-hidden my-2 text-xs transition-all duration-200",
        className
      )}
    >
      <button
        type="button"
        onClick={toggleOpen}
        aria-expanded={isOpen}
        className="w-full flex items-center justify-between px-3.5 py-2.5 select-none text-left font-medium transition-colors hover:bg-sand-100/50 dark:hover:bg-zinc-800/50 cursor-pointer"
      >
        {isStreaming ? (
          <div className="flex items-center gap-2 text-amber-600 dark:text-amber-400 font-medium">
            <Sparkles className="w-4 h-4 animate-spin text-amber-500" style={{ animationDuration: "3s" }} />
            <span className="font-medium tracking-tight animate-pulse">
              Thinking...
            </span>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <span className="flex items-center justify-center w-4 h-4 rounded-full bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 text-[11px] font-bold">
              ✓
            </span>
            <span className="tracking-tight text-ink/80 dark:text-zinc-300">
              Thinking Finished
            </span>
          </div>
        )}

        <div className="flex items-center gap-1.5 text-ink-muted/70 dark:text-zinc-500">
          {isOpen ? (
            <ChevronDown className="w-3.5 h-3.5" />
          ) : (
            <ChevronRight className="w-3.5 h-3.5" />
          )}
        </div>
      </button>

      {/* Collapsible Chain-of-Thought Content */}
      {isOpen && (
        <div
          data-testid="reasoning-thought-content"
          className="px-3.5 py-2.5 border-t border-hairline/60 dark:border-zinc-800 font-mono text-[11px] leading-relaxed whitespace-pre-wrap text-ink-muted dark:text-zinc-400 bg-sand-100/30 dark:bg-zinc-950/40"
        >
          {thoughtContent}
        </div>
      )}
    </div>
  );
}
