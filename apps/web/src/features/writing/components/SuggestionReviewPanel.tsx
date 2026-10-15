import { useState, useMemo, useEffect, useCallback } from "react";
import {
  Sparkles,
  X,
  Check,
  AlertCircle,
  FileDiff,
  Loader2,
  HelpCircle,
  Clock,
} from "lucide-react";
import type { PendingSuggestion } from "../types";
import { useWritingStore } from "../stores/useWritingStore";
import { computeSimpleDiff } from "../lib/diffUtils";
import { cn } from "@/lib/utils";

export interface SuggestionReviewPanelProps {
  isOpen?: boolean;
  suggestion?: PendingSuggestion | null;
  onClose?: () => void;
  onAccept?: (suggestion: PendingSuggestion) => Promise<void> | void;
  onReject?: (suggestion: PendingSuggestion) => void;
  isSaving?: boolean;
}

export function SuggestionReviewPanel({
  isOpen,
  suggestion,
  onClose,
  onAccept,
  onReject,
  isSaving: externalSaving,
}: SuggestionReviewPanelProps) {
  const storeIsOpen = useWritingStore((s) => s.isSuggestionPanelOpen);
  const storeSuggestion = useWritingStore((s) => s.pendingSuggestion);
  const storeClose = useWritingStore((s) => s.closeSuggestionPanel);
  const storeSaving = useWritingStore((s) => s.isSaving);

  const effectiveIsOpen = isOpen !== undefined ? isOpen : storeIsOpen;
  const effectiveSuggestion =
    suggestion !== undefined ? suggestion : storeSuggestion;
  const effectiveSaving =
    externalSaving !== undefined ? externalSaving : storeSaving;

  const [activeTab, setActiveTab] = useState<"diff" | "clean">("diff");
  const [localSaving, setLocalSaving] = useState(false);
  const isBusy = effectiveSaving || localSaving;

  const handleClose = () => {
    if (onClose) {
      onClose();
    } else {
      storeClose();
    }
  };

  const handleReject = useCallback(() => {
    if (!effectiveSuggestion) return;
    if (onReject) {
      onReject(effectiveSuggestion);
    } else {
      storeClose();
    }
  }, [effectiveSuggestion, onReject, storeClose]);

  const handleAccept = async () => {
    if (!effectiveSuggestion || isBusy) return;
    try {
      setLocalSaving(true);
      if (onAccept) {
        await onAccept(effectiveSuggestion);
      }
    } finally {
      setLocalSaving(false);
    }
  };

  // Keyboard shortcut: ESC to dismiss/reject
  useEffect(() => {
    if (!effectiveIsOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !isBusy) {
        handleReject();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [effectiveIsOpen, isBusy, handleReject]);

  const diffLines = useMemo(() => {
    if (!effectiveSuggestion) return [];
    return computeSimpleDiff(
      effectiveSuggestion.original_text,
      effectiveSuggestion.suggested_text
    );
  }, [effectiveSuggestion]);

  if (!effectiveIsOpen || !effectiveSuggestion) return null;

  const confidencePercent = Math.round(
    (effectiveSuggestion.confidence_score || 0) * 100
  );

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Xem xét đề xuất của AI Assistant"
      data-testid="suggestion-review-panel"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-in fade-in duration-150 text-xs"
      onClick={(e) => {
        if (e.target === e.currentTarget && !isBusy) handleClose();
      }}
    >
      <div className="w-full max-w-3xl max-h-[85vh] bg-white dark:bg-[#181715] rounded-xl shadow-2xl border border-[#e2dcd2] dark:border-[#2e2b26] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="h-12 px-5 border-b border-[#ece8df] dark:border-[#2a2824] flex items-center justify-between shrink-0 bg-[#fbf9f5] dark:bg-[#1f1d1a]">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-coral-600 dark:text-coral-400" />
            <span className="font-semibold text-sm text-ink dark:text-zinc-100 font-anthropic-serif">
              Xem xét đề xuất AI Assistant
            </span>
          </div>

          <div className="flex items-center gap-2">
            {/* Confidence Badge */}
            <span
              className={cn(
                "px-2 py-0.5 rounded-full text-[10px] font-semibold flex items-center gap-1",
                confidencePercent >= 80
                  ? "bg-emerald-500/15 text-emerald-800 dark:text-emerald-300"
                  : confidencePercent >= 50
                  ? "bg-amber-500/15 text-amber-800 dark:text-amber-300"
                  : "bg-rose-500/15 text-rose-800 dark:text-rose-300"
              )}
            >
              <Check className="w-3 h-3" />
              <span>{confidencePercent}% tin cậy</span>
            </span>

            <button
              type="button"
              onClick={handleClose}
              disabled={isBusy}
              aria-label="Đóng"
              className="p-1 rounded-md hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 cursor-pointer disabled:opacity-50"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {/* Prompt & Explanation Box */}
          <div className="p-3 rounded-lg bg-[#fbf9f5] dark:bg-[#201e1a] border border-[#ece8df] dark:border-[#2a2824] space-y-1.5">
            <div className="flex items-center justify-between text-[11px] font-semibold text-muted dark:text-zinc-400">
              <span className="flex items-center gap-1">
                <HelpCircle className="w-3.5 h-3.5 text-coral-500" />
                <span>Yêu cầu ban đầu:</span>
              </span>
              {effectiveSuggestion.created_at && (
                <span className="text-[10px] font-mono flex items-center gap-1 text-zinc-400">
                  <Clock className="w-3 h-3" />
                  {new Date(effectiveSuggestion.created_at).toLocaleTimeString()}
                </span>
              )}
            </div>
            <p className="font-medium text-ink dark:text-zinc-200 text-xs italic pl-4">
              "{effectiveSuggestion.prompt}"
            </p>

            {effectiveSuggestion.explanation && (
              <div className="mt-2 pt-2 border-t border-[#ece8df] dark:border-[#2a2824] text-[11px] text-zinc-600 dark:text-zinc-400">
                <span className="font-semibold text-ink dark:text-zinc-300">
                  Ghi chú tối ưu:{" "}
                </span>
                {effectiveSuggestion.explanation}
              </div>
            )}
          </div>

          {/* View Tab Toggle */}
          <div className="flex items-center justify-between border-b border-[#ece8df] dark:border-[#2a2824] pb-1 text-xs">
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={() => setActiveTab("diff")}
                className={cn(
                  "px-2.5 py-1 rounded font-medium transition-colors cursor-pointer flex items-center gap-1.5",
                  activeTab === "diff"
                    ? "bg-coral-500/10 text-coral-600 dark:text-coral-400"
                    : "text-muted hover:text-ink dark:text-zinc-400"
                )}
              >
                <FileDiff className="w-3.5 h-3.5" />
                <span>So sánh trực quan (Diff)</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("clean")}
                className={cn(
                  "px-2.5 py-1 rounded font-medium transition-colors cursor-pointer",
                  activeTab === "clean"
                    ? "bg-coral-500/10 text-coral-600 dark:text-coral-400"
                    : "text-muted hover:text-ink dark:text-zinc-400"
                )}
              >
                <span>Văn bản đề xuất hoàn chỉnh</span>
              </button>
            </div>
            <span className="text-[11px] text-zinc-400 font-mono">
              Phiên bản nháp bảo vệ: v{effectiveSuggestion.expected_version}
            </span>
          </div>

          {/* Diff / Text Content Display */}
          {activeTab === "diff" ? (
            <div
              data-testid="diff-container"
              className="font-mono text-xs p-3 rounded-lg bg-[#faf8f5] dark:bg-[#151413] border border-[#e2dcd2] dark:border-[#2e2b26] max-h-72 overflow-y-auto space-y-0.5"
            >
              {diffLines.length > 0 ? (
                diffLines.map((line, idx) => (
                  <div
                    key={idx}
                    className={cn(
                      "px-2 py-0.5 rounded leading-relaxed whitespace-pre-wrap break-all flex items-start gap-2",
                      line.type === "added" &&
                        "bg-emerald-500/15 text-emerald-800 dark:text-emerald-300 border-l-2 border-emerald-500",
                      line.type === "removed" &&
                        "bg-rose-500/15 text-rose-800 dark:text-rose-300 border-l-2 border-rose-500 line-through opacity-80",
                      line.type === "unchanged" &&
                        "text-zinc-700 dark:text-zinc-300"
                    )}
                  >
                    <span className="select-none font-bold shrink-0 w-3 text-center">
                      {line.type === "added"
                        ? "+"
                        : line.type === "removed"
                        ? "-"
                        : " "}
                    </span>
                    <span className="flex-1">{line.text || "\u00A0"}</span>
                  </div>
                ))
              ) : (
                <div className="text-zinc-400 italic">Không có nội dung so sánh</div>
              )}
            </div>
          ) : (
            <div
              data-testid="clean-text-container"
              className="font-mono text-xs p-3 rounded-lg bg-[#faf8f5] dark:bg-[#151413] border border-[#e2dcd2] dark:border-[#2e2b26] max-h-72 overflow-y-auto whitespace-pre-wrap leading-relaxed text-ink dark:text-zinc-100"
            >
              {effectiveSuggestion.suggested_text}
            </div>
          )}

          <div className="flex items-center gap-1.5 text-[11px] text-zinc-500 dark:text-zinc-400">
            <AlertCircle className="w-3.5 h-3.5 text-amber-500 shrink-0" />
            <span>
              Chấp nhận sẽ chèn nội dung vào vị trí con trỏ và lưu với cơ chế OCC ETag (If-Match) để bảo vệ toàn vẹn dữ liệu.
            </span>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="h-14 px-5 border-t border-[#ece8df] dark:border-[#2a2824] bg-[#fbf9f5] dark:bg-[#1f1d1a] flex items-center justify-between shrink-0">
          <button
            type="button"
            onClick={handleReject}
            disabled={isBusy}
            data-testid="reject-suggestion-btn"
            className="px-4 py-2 rounded-lg border border-[#e2dcd2] dark:border-[#2e2b26] bg-white dark:bg-[#252320] text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/20 font-medium transition-colors cursor-pointer disabled:opacity-50"
          >
            Từ chối (Hủy bỏ)
          </button>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleClose}
              disabled={isBusy}
              className="px-3 py-2 rounded-lg text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200 transition-colors cursor-pointer disabled:opacity-50"
            >
              Xem sau
            </button>

            <button
              type="button"
              onClick={handleAccept}
              disabled={isBusy}
              data-testid="accept-suggestion-btn"
              className="px-4 py-2 rounded-lg bg-coral-500 hover:bg-coral-600 text-white font-medium shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
            >
              {isBusy ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Đang lưu bản nháp...</span>
                </>
              ) : (
                <>
                  <Check className="w-4 h-4" />
                  <span>Chấp nhận & Chèn</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
