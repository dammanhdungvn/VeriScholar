import { useEffect } from "react";
import {
  X,
  FileText,
  Quote,
  Tag,
  ArrowUpRight,
  ShieldCheck,
  AlertTriangle,
  Code,
  Layers,
} from "lucide-react";
import { useNoteDetail } from "../hooks/useNotesQuery";

interface NoteDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  noteId: string | null;
  onJumpToPage?: (page: number, noteId: string) => void;
}

export function NoteDetailModal({
  isOpen,
  onClose,
  noteId,
  onJumpToPage,
}: NoteDetailModalProps) {
  const { data: noteResponse, isLoading, isError } = useNoteDetail(noteId);
  const note = noteResponse?.data;

  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !noteId) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Chi tiết ghi chú nghiên cứu"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in duration-150 text-xs"
    >
      <div className="w-full max-w-xl max-h-[85vh] bg-canvas dark:bg-[#1a1917] rounded-xl shadow-2xl border border-hairline dark:border-[#2f2b26] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="h-12 px-5 border-b border-hairline dark:border-[#2f2b26] flex items-center justify-between shrink-0 bg-surface-soft/40 dark:bg-[#1f1d1a]">
          <div className="flex items-center gap-2 font-serif font-semibold text-sm text-ink dark:text-zinc-100">
            <FileText className="w-4 h-4 text-coral-600 dark:text-coral-400" />
            <span aria-hidden="true">Chi tiết ghi chú</span>
            <span className="sr-only">Chi tiết ghi chú & Bản sao bằng chứng đóng băng (Frozen Snapshot)</span>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Đóng chi tiết ghi chú"
            className="p-1 rounded-md hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {isLoading ? (
            <div className="space-y-3 py-10">
              <div className="h-16 rounded-lg bg-surface-soft/60 dark:bg-[#201e1b] animate-pulse" />
              <div className="h-24 rounded-lg bg-surface-soft/60 dark:bg-[#201e1b] animate-pulse" />
            </div>
          ) : isError || !note ? (
            <div className="text-center py-12 text-muted">
              Không thể tải chi tiết ghi chú từ máy chủ.
            </div>
          ) : (
            <>
              {/* Quotation Section */}
              <div className="p-4 rounded-xl bg-surface-card dark:bg-[#201e1b] border border-hairline dark:border-[#332f29] space-y-2">
                <div className="flex items-center justify-between text-muted text-[11px]">
                  <span className="flex items-center gap-1 font-semibold text-ink dark:text-zinc-200">
                    <Quote className="w-3.5 h-3.5 text-coral-600 dark:text-coral-400" />
                    <span>Trích dẫn gốc</span>
                  </span>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        onJumpToPage?.(note.page_number, note.id);
                        onClose();
                      }}
                      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full font-mono text-[10px] bg-coral-500/10 text-coral-700 dark:text-coral-400 border border-coral-500/20 hover:bg-coral-500/20 transition-colors"
                    >
                      <span>Trang {note.page_number}</span>
                      <ArrowUpRight className="w-2.5 h-2.5" />
                    </button>
                  </div>
                </div>
                <blockquote className="font-serif italic text-xs leading-relaxed text-ink dark:text-zinc-100 pl-2 border-l-2 border-coral-500">
                  &ldquo;{note.selected_text}&rdquo;
                </blockquote>
              </div>

              {/* User Annotation Memo */}
              {note.user_note && (
                <div className="p-4 rounded-xl bg-surface-card dark:bg-[#201e1b] border border-hairline dark:border-[#332f29] space-y-1.5">
                  <span className="text-[11px] font-semibold text-ink dark:text-zinc-200 block">
                    Ghi chú cá nhân:
                  </span>
                  <p className="font-sans text-xs text-ink dark:text-zinc-200 leading-relaxed whitespace-pre-wrap">
                    {note.user_note}
                  </p>
                </div>
              )}

              {/* Tags Section */}
              {note.tags && note.tags.length > 0 && (
                <div className="flex items-center gap-1.5 flex-wrap">
                  <Tag className="w-3.5 h-3.5 text-muted shrink-0" />
                  {note.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-0.5 rounded-md font-mono text-[10px] bg-surface-soft dark:bg-[#282622] text-ink dark:text-zinc-200 border border-hairline"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              )}

              {/* Frozen Evidence Snapshot Section */}
              <div className="p-4 rounded-xl bg-surface-card dark:bg-[#201e1b] border border-hairline dark:border-[#332f29] space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5 font-semibold text-ink dark:text-zinc-200">
                    <ShieldCheck className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                    <span aria-hidden="true">Bản sao bằng chứng</span>
                    <span className="sr-only">Bản sao bằng chứng đóng băng (Frozen Snapshot)</span>
                  </span>
                  {note.is_source_detached ? (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-500/20 font-mono">
                      <AlertTriangle className="w-3 h-3" />
                      <span aria-hidden="true">Nguồn đã gỡ</span>
                      <span className="sr-only">Nguồn đã tách rời (Detached)</span>
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20 font-mono">
                      <ShieldCheck className="w-3 h-3" />
                      <span>Đã bảo chứng</span>
                    </span>
                  )}
                </div>

                <p className="text-[11px] text-muted leading-relaxed">
                  Dữ liệu bằng chứng được bảo toàn độc lập với bài báo gốc.
                </p>

                {/* Bounding Box Coordinates */}
                {note.bounding_boxes && note.bounding_boxes.length > 0 && (
                  <div className="p-2.5 rounded-lg bg-surface-soft/60 dark:bg-[#161513] border border-hairline font-mono text-[10px] space-y-1">
                    <div className="flex items-center gap-1 text-muted">
                      <Layers className="w-3 h-3" />
                      <span>Tọa độ trích dẫn:</span>
                    </div>
                    {note.bounding_boxes.map((box, idx) => (
                      <div key={idx} className="text-coral-600 dark:text-coral-400">
                        Box #{idx + 1}: [{box.map((n) => (typeof n === "number" ? n.toFixed(3) : n)).join(", ")}]
                      </div>
                    ))}
                  </div>
                )}

                {/* Raw Snapshot JSON viewer */}
                {note.frozen_snapshot && Object.keys(note.frozen_snapshot).length > 0 && (
                  <details className="text-[10px] font-mono text-muted">
                    <summary className="cursor-pointer hover:text-ink flex items-center gap-1">
                      <Code className="w-3 h-3" />
                      <span>Dữ liệu thô (JSON)</span>
                    </summary>
                    <pre className="mt-2 p-2 rounded bg-black/5 dark:bg-black/40 overflow-x-auto text-[10px]">
                      {JSON.stringify(note.frozen_snapshot, null, 2)}
                    </pre>
                  </details>
                )}
              </div>

              {/* Metadata Footer */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 pt-2 border-t border-hairline dark:border-[#2f2b26] text-[11px] text-muted font-mono">
                <div>
                  <span className="block text-[10px]">Phiên bản:</span>
                  <span className="text-ink dark:text-zinc-200 font-semibold">v{note.version}</span>
                </div>
                <div>
                  <span className="block text-[10px]">Ngày tạo:</span>
                  <span className="text-ink dark:text-zinc-200">
                    {new Date(note.created_at).toLocaleString("vi-VN")}
                  </span>
                </div>
                <div>
                  <span className="block text-[10px]">Cập nhật:</span>
                  <span className="text-ink dark:text-zinc-200">
                    {new Date(note.updated_at).toLocaleString("vi-VN")}
                  </span>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
