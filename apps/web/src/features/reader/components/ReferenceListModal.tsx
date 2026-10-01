import { useEffect, useState } from "react";
import { X, ExternalLink, BookMarked, RefreshCw } from "lucide-react";
import type { ReferenceItemResponse } from "@/types/document";

interface ReferenceListModalProps {
  isOpen: boolean;
  onClose: () => void;
  references: ReferenceItemResponse[];
  isLoading?: boolean;
  onReextract?: () => Promise<void>;
}

export function ReferenceListModal({
  isOpen,
  onClose,
  references,
  isLoading = false,
  onReextract,
}: ReferenceListModalProps) {
  const [isReextracting, setIsReextracting] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleReextractClick = async () => {
    if (!onReextract || isReextracting) return;
    setIsReextracting(true);
    try {
      await onReextract();
    } finally {
      setIsReextracting(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Danh mục tài liệu tham khảo"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in duration-150"
    >
      <div className="w-full max-w-2xl max-h-[85vh] bg-canvas dark:bg-[#1a1917] rounded-lg shadow-2xl border border-hairline dark:border-[#2f2b26] flex flex-col overflow-hidden">
        {/* Modal Header */}
        <div className="h-12 px-5 border-b border-hairline dark:border-[#2f2b26] flex items-center justify-between">
          <div className="flex items-center gap-2 font-serif font-semibold text-sm text-ink dark:text-zinc-100">
            <BookMarked className="w-4 h-4 text-primary" />
            <span>Tài liệu tham khảo ({references.length})</span>
          </div>
          <div className="flex items-center gap-2">
            {onReextract && (
              <button
                type="button"
                onClick={handleReextractClick}
                disabled={isReextracting || isLoading}
                aria-label="Bóc tách lại danh mục tham khảo"
                title="Bóc tách lại danh mục tham khảo (Force Re-extract)"
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md border border-hairline hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink text-xs transition-colors cursor-pointer disabled:opacity-40"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isReextracting ? "animate-spin" : ""}`} />
                <span className="hidden sm:inline">
                  {isReextracting ? "Đang trích xuất..." : "Bóc tách lại"}
                </span>
              </button>
            )}
            <button
              type="button"
              onClick={onClose}
              aria-label="Đóng danh mục tham khảo"
              className="p-1 rounded-md hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-3 text-xs">
          {isLoading ? (
            <div className="text-center py-12 text-muted font-mono animate-pulse">
              Đang phân tích danh mục tài liệu tham khảo...
            </div>
          ) : references.length === 0 ? (
            <div className="text-center py-12 text-muted">
              Chưa có tài liệu tham khảo được bóc tách cho bài báo này.
            </div>
          ) : (
            references.map((ref) => {
              const parsed = ref.parsed;
              const arxivUrl = parsed.arxiv_id ? `https://arxiv.org/abs/${parsed.arxiv_id}` : null;
              const doiUrl = parsed.doi ? `https://doi.org/${parsed.doi}` : null;

              return (
                <div
                  key={ref.ref_index}
                  className="p-3.5 rounded-md bg-surface-soft/60 dark:bg-[#22201d] border border-hairline dark:border-[#302c26] space-y-1.5"
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="inline-flex items-center justify-center w-5 h-5 rounded bg-primary/10 text-primary font-mono text-[11px] font-semibold shrink-0">
                      [{ref.ref_index}]
                    </span>
                    <h5 className="flex-1 font-serif font-medium text-ink dark:text-zinc-100 text-xs leading-snug">
                      {parsed.title || ref.raw_text}
                    </h5>
                  </div>

                  {parsed.authors && parsed.authors.length > 0 && (
                    <p className="text-[11px] text-muted font-sans pl-7">
                      {parsed.authors.join(", ")} {parsed.year ? `(${parsed.year})` : ""}
                    </p>
                  )}

                  {/* External scholarly links */}
                  <div className="flex items-center gap-3 pl-7 pt-1">
                    {arxivUrl && (
                      <a
                        href={arxivUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-[11px] text-primary hover:underline font-mono"
                      >
                        <span>arXiv:{parsed.arxiv_id}</span>
                        <ExternalLink className="w-2.5 h-2.5" />
                      </a>
                    )}
                    {doiUrl && (
                      <a
                        href={doiUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-[11px] text-teal-600 dark:text-teal-400 hover:underline font-mono"
                      >
                        <span>DOI:{parsed.doi}</span>
                        <ExternalLink className="w-2.5 h-2.5" />
                      </a>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
