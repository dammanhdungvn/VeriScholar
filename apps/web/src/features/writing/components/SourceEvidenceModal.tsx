import { useEffect } from "react";
import {
  X,
  BookOpen,
  ExternalLink,
  Layers,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Quote,
} from "lucide-react";
import type { AtomicClaim } from "../types";
import { useWritingStore } from "../stores/useWritingStore";
import { documentsApi } from "@/features/documents/api/documentsApi";
import { cn } from "@/lib/utils";

export interface SourceEvidenceModalProps {
  isOpen?: boolean;
  onClose?: () => void;
  claim?: AtomicClaim | null;
}

export function SourceEvidenceModal({
  isOpen,
  onClose,
  claim,
}: SourceEvidenceModalProps) {
  const storeClaim = useWritingStore((s) => s.selectedEvidenceClaim);
  const storeIsOpen = useWritingStore((s) => s.isEvidenceModalOpen);
  const storeClose = useWritingStore((s) => s.closeEvidenceModal);

  const effectiveClaim = claim !== undefined ? claim : storeClaim;
  const effectiveIsOpen = isOpen !== undefined ? isOpen : storeIsOpen;
  const handleClose = onClose || storeClose;

  // ESC to close
  useEffect(() => {
    if (!effectiveIsOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") handleClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [effectiveIsOpen, handleClose]);

  if (!effectiveIsOpen || !effectiveClaim) return null;

  const page = effectiveClaim.evidence_page || 1;
  const boxes = effectiveClaim.evidence_bounding_boxes || [];
  const isSupported = effectiveClaim.status === "supported";
  const isContradicted = effectiveClaim.status === "contradicted";
  const fileUrl = effectiveClaim.evidence_document_id
    ? documentsApi.getDocumentFileUrl(effectiveClaim.evidence_document_id)
    : null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Chi tiết dẫn chứng bài báo nguồn"
      onClick={(e) => {
        if (e.target === e.currentTarget) handleClose();
      }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-in fade-in duration-150 text-xs"
    >
      <div className="w-full max-w-4xl max-h-[90vh] bg-white dark:bg-[#181715] rounded-xl shadow-2xl border border-[#e2dcd2] dark:border-[#2e2b26] flex flex-col overflow-hidden">
        {/* Modal Header */}
        <div className="h-12 px-5 border-b border-[#ece8df] dark:border-[#2a2824] flex items-center justify-between shrink-0 bg-[#fbf9f5] dark:bg-[#1f1d1a]">
          <div className="flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-coral-600 dark:text-coral-400" />
            <span className="font-semibold text-sm text-ink dark:text-zinc-100 font-anthropic-serif">
              Dẫn chứng: {effectiveClaim.evidence_document_title || "Tài liệu nguồn"}
            </span>
          </div>

          <div className="flex items-center gap-3">
            {/* Status Badge */}
            <span
              className={cn(
                "px-2 py-0.5 rounded-full text-[10px] font-semibold flex items-center gap-1",
                isSupported && "bg-emerald-500/20 text-emerald-800 dark:text-emerald-300",
                isContradicted && "bg-rose-500/20 text-rose-800 dark:text-rose-300",
                !isSupported && !isContradicted && "bg-amber-500/20 text-amber-800 dark:text-amber-300"
              )}
            >
              {isSupported && <CheckCircle2 className="w-3 h-3 text-emerald-600" />}
              {isContradicted && <XCircle className="w-3 h-3 text-rose-600" />}
              {!isSupported && !isContradicted && <HelpCircle className="w-3 h-3 text-amber-600" />}
              <span>{effectiveClaim.status.toUpperCase()}</span>
            </span>

            {/* Page info badge */}
            <span className="px-2 py-0.5 rounded-full bg-zinc-200 dark:bg-zinc-800 text-[10px] font-mono text-zinc-700 dark:text-zinc-300">
              Trang {page}
            </span>

            <button
              type="button"
              onClick={handleClose}
              aria-label="Đóng"
              className="p-1 rounded-md hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {/* Claim & Evidence Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {/* Claim Card */}
            <div className="p-3 rounded-lg bg-[#fbf9f5] dark:bg-[#201e1a] border border-[#ece8df] dark:border-[#2a2824]">
              <div className="flex items-center justify-between text-[10px] font-semibold text-muted dark:text-zinc-400 uppercase tracking-wider mb-1">
                <span>Mệnh đề</span>
                <span className="font-mono text-coral-600 dark:text-coral-400">
                  <span aria-hidden="true">{Math.round(effectiveClaim.confidence_score * 100)}% tin cậy</span>
                  <span className="sr-only">{Math.round(effectiveClaim.confidence_score * 100)}% độ tin cậy</span>
                </span>
              </div>
              <p className="font-medium text-ink dark:text-zinc-100 text-xs leading-snug">
                "{effectiveClaim.claim_text}"
              </p>
              {effectiveClaim.reasoning && (
                <div className="mt-1.5 text-[11px] text-zinc-500 dark:text-zinc-400">
                  <span className="font-medium text-ink dark:text-zinc-300">Lý do: </span>
                  {effectiveClaim.reasoning}
                </div>
              )}
            </div>

            {/* Evidence Quote Card */}
            <div className="p-3 rounded-lg bg-[#fbf9f5] dark:bg-[#201e1a] border border-[#ece8df] dark:border-[#2a2824]">
              <div className="flex items-center gap-1 text-[10px] font-semibold text-muted dark:text-zinc-400 uppercase tracking-wider mb-1">
                <Quote className="w-3 h-3 text-coral-500" />
                <span>Đoạn trích đối chiếu</span>
              </div>
              <blockquote className="font-serif italic text-xs leading-snug text-ink dark:text-zinc-200 border-l-2 border-coral-500 pl-2">
                "{effectiveClaim.evidence_text || 'Không có đoạn trích văn bản kèm theo.'}"
              </blockquote>
            </div>
          </div>

          {/* PDF Viewer with Bounding Box Overlay Layer */}
          {fileUrl ? (
            <div
              className="relative w-full h-[520px] bg-zinc-900 rounded-lg overflow-hidden border border-[#e2dcd2] dark:border-[#2e2b26] flex items-center justify-center"
              data-testid="source-pdf-container"
            >
              <iframe
                src={`${fileUrl}#page=${page}&view=FitH`}
                title={`Tài liệu nguồn - Trang ${page}`}
                className="w-full h-full border-0 rounded"
              />

              {/* Bounding Box Highlights Overlay Layer (Directly on Source Paper Page) */}
              {boxes.length > 0 && (
                <div
                  className="absolute inset-0 pointer-events-none z-20"
                  data-testid="source-evidence-bbox-overlay"
                  aria-label="Khung tọa độ trích dẫn trên bài báo gốc"
                >
                  {boxes.map((box, idx) => {
                    const [x0, y0, x1, y1] = box;
                    return (
                      <div
                        key={idx}
                        data-testid="evidence-bbox-highlight"
                        className="absolute border-2 border-amber-500 bg-amber-400/25 rounded-xs animate-pulse shadow-md pointer-events-none"
                        style={{
                          left: `${x0 * 100}%`,
                          top: `${y0 * 100}%`,
                          width: `${(x1 - x0) * 100}%`,
                          height: `${(y1 - y0) * 100}%`,
                        }}
                      >
                        <span className="absolute -top-5 left-0 px-1.5 py-0.5 bg-amber-600 text-white font-mono text-[10px] rounded shadow-xs font-semibold whitespace-nowrap">
                          Dẫn chứng #{idx + 1} (Trang {page})
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          ) : (
            <div
              className="p-8 rounded-lg bg-[#fbf9f5] dark:bg-[#201e1a] border border-dashed border-[#e2dcd2] dark:border-[#2e2b26] text-center space-y-3"
              data-testid="source-pdf-fallback"
            >
              <BookOpen className="w-8 h-8 text-coral-500 mx-auto" />
              <div className="font-semibold text-xs text-ink dark:text-zinc-200">
                Chứng cứ học thuật trích dẫn
              </div>
              <p className="text-xs text-muted dark:text-zinc-400 max-w-lg mx-auto italic">
                "{effectiveClaim.evidence_text || 'Chưa liên kết tệp PDF nhị phân cho bài báo này.'}"
              </p>
            </div>
          )}

          {/* Coordinate Details & Inspector Footer */}
          {boxes.length > 0 && (
            <div className="p-2.5 rounded-lg bg-[#fbf9f5] dark:bg-[#201e1a] border border-[#ece8df] dark:border-[#2a2824] flex flex-wrap items-center justify-between text-[11px] font-mono text-muted dark:text-zinc-400 gap-2">
              <div className="flex items-center gap-2 flex-wrap">
                <Layers className="w-3.5 h-3.5 text-coral-500" />
                <span className="font-semibold text-ink dark:text-zinc-300">
                  Tọa độ Bounding Box [x0, y0, x1, y1]:
                </span>
                {boxes.map((b, idx) => (
                  <span
                    key={idx}
                    className="px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-500/20"
                  >
                    #{idx + 1}: [
                    {b
                      .slice(0, 4)
                      .map((v) => (typeof v === "number" ? v.toFixed(3) : v))
                      .join(", ")}
                    ]
                  </span>
                ))}
              </div>

              {fileUrl && (
                <a
                  href={fileUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1 text-coral-600 dark:text-coral-400 hover:underline ml-auto"
                >
                  <span>Mở toàn bộ PDF</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
