import { useState } from "react";
import {
  Quote,
  BookOpen,
  X,
  Sparkles,
  Check,
} from "lucide-react";
import { cn } from "@/lib/utils";

export interface AssociativeMemoryCardProps {
  title: string;
  page?: number | string;
  citationKey?: string;
  noteId?: string;
  noteSnippet?: string;
  similarityScore?: number;
  onInsertCitation?: (citationKey: string) => void;
  onViewNote?: (noteId?: string) => void;
  onDismiss?: () => void;
  className?: string;
}

export function AssociativeMemoryCard({
  title,
  page = 1,
  citationKey,
  noteId,
  noteSnippet,
  similarityScore,
  onInsertCitation,
  onViewNote,
  onDismiss,
  className,
}: AssociativeMemoryCardProps) {
  const [isInserted, setIsInserted] = useState(false);

  const effectiveCitationKey = citationKey || title.toLowerCase().replace(/[^a-z0-9]/g, "").slice(0, 16);

  const handleInsert = () => {
    onInsertCitation?.(effectiveCitationKey);
    setIsInserted(true);
    setTimeout(() => setIsInserted(false), 2000);
  };

  return (
    <div
      role="region"
      aria-label="Gợi ý liên kết tri thức"
      data-testid="associative-memory-card"
      className={cn(
        "p-3.5 rounded-xl border border-coral-500/30 dark:border-coral-500/25",
        "bg-[#fdfcf9] dark:bg-[#1e1c19] text-ink dark:text-zinc-100 shadow-lg",
        "backdrop-blur-xs transition-all duration-200 space-y-2.5 max-w-sm",
        "animate-in fade-in slide-in-from-bottom-2",
        className
      )}
    >
      {/* Top bar */}
      <div className="flex items-center justify-between text-2xs font-medium text-coral-600 dark:text-coral-400">
        <div className="flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5" />
          <span className="font-semibold uppercase tracking-wider">Proactive Associative Memory</span>
        </div>

        {onDismiss && (
          <button
            type="button"
            onClick={onDismiss}
            aria-label="Đóng gợi ý"
            className="p-1 rounded-md text-muted hover:text-ink dark:hover:text-zinc-100 hover:bg-black/5 dark:hover:bg-white/5 transition-colors cursor-pointer"
          >
            <X className="w-3 h-3" />
          </button>
        )}
      </div>

      {/* Main message */}
      <div className="text-xs leading-relaxed text-zinc-800 dark:text-zinc-200">
        <span className="font-medium">
          💡 Gợi ý liên kết: Đoạn này tương đồng với ghi chú tại bài{" "}
          <strong className="font-semibold font-serif text-coral-700 dark:text-coral-300">
            {title}
          </strong>{" "}
          (Trang {page})
        </span>
      </div>

      {/* Snippet preview if available */}
      {noteSnippet && (
        <div className="text-[11px] italic text-muted dark:text-zinc-400 border-l-2 border-coral-400/50 pl-2.5 py-0.5 font-serif line-clamp-2 bg-surface-soft/40 dark:bg-black/10 rounded-r">
          &ldquo;{noteSnippet}&rdquo;
        </div>
      )}

      {/* Similarity score indicator if provided */}
      {similarityScore !== undefined && (
        <div className="flex items-center gap-1.5 text-2xs text-muted dark:text-zinc-400 font-mono">
          <span>Độ tương quan ngữ nghĩa:</span>
          <span className="px-1.5 py-0.2 rounded bg-coral-500/10 text-coral-700 dark:text-coral-300 font-bold">
            {(similarityScore * 100).toFixed(0)}%
          </span>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-2 pt-1">
        <button
          type="button"
          onClick={handleInsert}
          data-testid="insert-citation-btn"
          className={cn(
            "flex-1 inline-flex items-center justify-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium shadow-2xs transition-all cursor-pointer",
            isInserted
              ? "bg-emerald-600 text-white"
              : "bg-coral-500 hover:bg-coral-600 text-white"
          )}
        >
          {isInserted ? (
            <>
              <Check className="w-3 h-3" />
              <span>Đã chèn</span>
            </>
          ) : (
            <>
              <Quote className="w-3 h-3" />
              <span>Chèn trích dẫn</span>
            </>
          )}
        </button>

        <button
          type="button"
          onClick={() => onViewNote?.(noteId)}
          data-testid="view-note-btn"
          className="inline-flex items-center justify-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium border border-hairline dark:border-zinc-700 bg-surface-soft hover:bg-surface-cream text-ink dark:text-zinc-200 transition-colors cursor-pointer"
        >
          <BookOpen className="w-3 h-3" />
          <span>Xem ghi chú</span>
        </button>
      </div>
    </div>
  );
}
