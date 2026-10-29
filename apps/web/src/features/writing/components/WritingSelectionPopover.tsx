import { MessageSquarePlus, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

export interface WritingSelectionPopoverProps {
  selectedText: string;
  position: { top: number; left: number };
  isOpen: boolean;
  onAddToChat?: (text: string) => void;
  onAskAi?: (text: string) => void;
}

export function WritingSelectionPopover({
  selectedText,
  position,
  isOpen,
  onAddToChat,
  onAskAi,
}: WritingSelectionPopoverProps) {
  if (!isOpen || !selectedText.trim()) {
    return null;
  }

  return (
    <div
      data-testid="selection-popover-container"
      style={{
        position: "absolute",
        top: `${position.top}px`,
        left: `${position.left}px`,
        transform: "translate(-50%, -100%) translateY(-8px)",
      }}
      className={cn(
        "z-50 inline-flex items-center gap-1 p-1 rounded-xl shadow-xl",
        "bg-stone-900/90 dark:bg-stone-950/95 backdrop-blur-md border border-white/10 dark:border-white/15 text-white",
        "text-xs font-sans select-none animate-in fade-in zoom-in-95 duration-150"
      )}
      onClick={(e) => e.stopPropagation()}
    >
      <button
        type="button"
        data-testid="selection-add-to-chat-btn"
        onClick={() => onAddToChat?.(selectedText)}
        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-zinc-200 hover:text-white hover:bg-white/10 transition-colors cursor-pointer text-[11px] font-medium"
        title="Add quoted excerpt to chat input"
      >
        <MessageSquarePlus className="w-3.5 h-3.5 text-coral-400" />
        <span>Add to Chat</span>
      </button>

      <div className="w-[1px] h-3 bg-white/20" />

      <button
        type="button"
        data-testid="selection-ask-ai-btn"
        onClick={() => onAskAi?.(selectedText)}
        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-zinc-200 hover:text-white hover:bg-white/10 transition-colors cursor-pointer text-[11px] font-medium"
        title="Ask AI Copilot about this section"
      >
        <Sparkles className="w-3.5 h-3.5 text-sky-400" />
        <span>Ask AI</span>
      </button>
    </div>
  );
}
