import { Info, BookMarked, Bot } from "lucide-react";
import { cn } from "@/lib/utils";

export interface VerticalEdgeDockProps {
  onToggleInfo?: () => void;
  onToggleNotes?: () => void;
  onToggleAssistant?: () => void;
  isAssistantOpen?: boolean;
  className?: string;
}

export function VerticalEdgeDock({
  onToggleInfo,
  onToggleNotes,
  onToggleAssistant,
  isAssistantOpen = false,
  className,
}: VerticalEdgeDockProps) {
  return (
    <aside
      data-testid="vertical-edge-dock"
      aria-label="Thanh công cụ bổ trợ"
      className={cn(
        "flex flex-col items-center gap-1.5 p-1 rounded-2xl bg-white/90 dark:bg-[#201e1b]/90 backdrop-blur-md border border-[#e5dfd4] dark:border-[#38332c] shadow-md transition-all select-none",
        className
      )}
    >
      {/* Paper Info / Abstract Sheet trigger (ⓘ) */}
      <button
        type="button"
        data-testid="edge-dock-info-btn"
        onClick={onToggleInfo}
        aria-label="Thông tin bài báo"
        title="Thông tin bài báo (ⓘ)"
        className="w-8 h-8 rounded-xl flex items-center justify-center text-ink-muted dark:text-zinc-400 hover:text-primary hover:bg-[#f5f1ea] dark:hover:bg-[#2e2a25] transition-colors cursor-pointer"
      >
        <Info className="w-4 h-4" />
      </button>

      {/* Notes trigger (📝) */}
      <button
        type="button"
        data-testid="edge-dock-notes-btn"
        onClick={onToggleNotes}
        aria-label="Sổ tay ghi chú"
        title="Sổ tay ghi chú (📝)"
        className="w-8 h-8 rounded-xl flex items-center justify-center text-ink-muted dark:text-zinc-400 hover:text-primary hover:bg-[#f5f1ea] dark:hover:bg-[#2e2a25] transition-colors cursor-pointer"
      >
        <BookMarked className="w-4 h-4" />
      </button>

      {/* Assistant toggle / status (🤖) */}
      <button
        type="button"
        data-testid="edge-dock-assistant-btn"
        onClick={onToggleAssistant}
        aria-label={isAssistantOpen ? "Đóng trợ lý" : "Mở trợ lý"}
        title={isAssistantOpen ? "Đóng trợ lý (🤖)" : "Mở trợ lý (🤖)"}
        className={cn(
          "w-8 h-8 rounded-xl flex items-center justify-center transition-colors cursor-pointer",
          isAssistantOpen
            ? "bg-[#cc785c]/15 text-[#cc785c] font-semibold"
            : "text-ink-muted dark:text-zinc-400 hover:text-primary hover:bg-[#f5f1ea] dark:hover:bg-[#2e2a25]"
        )}
      >
        <Bot className="w-4 h-4" />
      </button>
    </aside>
  );
}
