import { Plus, RefreshCw, X } from "lucide-react";
import { cn } from "@/lib/utils";

export interface BridgeHintCardProps {
  refIndex: number;
  conceptName: string;
  paperTitle: string;
  authors?: string | string[];
  year?: number | string | null;
  reason: string;
  canIngest?: boolean;
  onIngest: () => void | Promise<void>;
  onDismiss: () => void;
  isIngesting?: boolean;
  className?: string;
}

export function BridgeHintCard({
  refIndex,
  conceptName,
  paperTitle,
  authors,
  year,
  reason,
  canIngest = true,
  onIngest,
  onDismiss,
  isIngesting = false,
  className,
}: BridgeHintCardProps) {
  const formattedAuthors = Array.isArray(authors)
    ? authors.join(", ")
    : authors || "";

  return (
    <div
      role="region"
      aria-label={`Gợi ý lộ trình học tuần tự: ${conceptName}`}
      data-testid="bridge-hint-card"
      className={cn(
        "my-3 p-4 rounded-xl border border-amber-300 dark:border-amber-700/60",
        "bg-amber-50/90 dark:bg-amber-950/30 text-ink dark:text-zinc-100",
        "shadow-xs transition-all space-y-3",
        className
      )}
    >
      {/* Header: Amber Badge & Dismiss icon */}
      <div className="flex items-center justify-between gap-2">
        <span
          data-testid="badge-socratic-roadmap"
          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-bold tracking-wide uppercase bg-amber-500/15 text-amber-900 dark:text-amber-300 border border-amber-400/40"
        >
          <span aria-hidden="true">💡</span>
          <span>GỢI Ý LỘ TRÌNH HỌC TUẦN TỰ (A → B → C → D)</span>
        </span>

        <button
          type="button"
          onClick={onDismiss}
          aria-label="Đóng thẻ gợi ý"
          className="p-1 rounded-md text-amber-800/70 dark:text-amber-400/70 hover:text-amber-950 dark:hover:text-amber-200 hover:bg-amber-500/10 transition-colors cursor-pointer"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Main Content: Concept & Paper & Reason */}
      <div className="space-y-1.5 text-xs">
        <div>
          <span className="text-zinc-600 dark:text-zinc-400 font-medium">Khái niệm: </span>
          <strong className="text-ink dark:text-zinc-100 font-semibold">{conceptName}</strong>
        </div>

        <div>
          <span className="text-zinc-600 dark:text-zinc-400 font-medium">
            Bài tham khảo nền tảng:{" "}
          </span>
          <span className="font-serif font-bold text-ink dark:text-zinc-100">
            [{refIndex}] {paperTitle}
          </span>
          {(formattedAuthors || year) && (
            <span className="text-zinc-600 dark:text-zinc-400 font-sans ml-1">
              ({formattedAuthors}
              {formattedAuthors && year ? `, ${year}` : year || ""})
            </span>
          )}
        </div>

        <div className="pt-0.5">
          <span className="text-zinc-600 dark:text-zinc-400 font-medium">Lý do: </span>
          <span className="text-zinc-800 dark:text-zinc-200 leading-relaxed italic">
            "{reason}"
          </span>
        </div>
      </div>

      {/* Action Footer */}
      <div className="flex items-center gap-2 pt-1">
        <button
          type="button"
          onClick={onIngest}
          disabled={!canIngest || isIngesting}
          data-testid="ingest-bridge-paper-btn"
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-amber-600 hover:bg-amber-700 text-white shadow-xs transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isIngesting ? (
            <>
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              <span>Đang nạp bài [{refIndex}]...</span>
            </>
          ) : (
            <>
              <Plus className="w-3.5 h-3.5" />
              <span>➕ Nạp bài [{refIndex}] vào phiên chat này</span>
            </>
          )}
        </button>

        <button
          type="button"
          onClick={onDismiss}
          data-testid="dismiss-bridge-card-btn"
          className="px-3 py-1.5 rounded-lg border border-amber-300/80 dark:border-amber-700/60 hover:bg-amber-500/10 text-amber-900 dark:text-amber-200 text-xs font-medium transition-colors cursor-pointer"
        >
          Bỏ qua
        </button>
      </div>
    </div>
  );
}
