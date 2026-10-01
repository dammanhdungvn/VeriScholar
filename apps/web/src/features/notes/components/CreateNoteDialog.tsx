import { useState } from "react";
import { X, BookmarkPlus, Quote } from "lucide-react";
import type { BoundingBox } from "@/types/api";

interface CreateNoteDialogProps {
  isOpen: boolean;
  onClose: () => void;
  documentId?: string | null;
  selectedText: string;
  pageNumber: number;
  bbox?: BoundingBox;
  onSubmit: (payload: {
    document_id?: string | null;
    selected_text: string;
    page_number: number;
    bounding_boxes?: BoundingBox[];
    user_note?: string;
    tags?: string[];
  }) => Promise<void>;
}

export function CreateNoteDialog({
  isOpen,
  onClose,
  documentId,
  selectedText,
  pageNumber,
  bbox,
  onSubmit,
}: CreateNoteDialogProps) {
  const [userNote, setUserNote] = useState("");
  const [tagsInput, setTagsInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const tags = tagsInput
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);

      await onSubmit({
        document_id: documentId,
        selected_text: selectedText,
        page_number: pageNumber,
        bounding_boxes: bbox ? [bbox] : [],
        user_note: userNote.trim() || undefined,
        tags: tags.length > 0 ? tags : undefined,
      });

      setUserNote("");
      setTagsInput("");
      onClose();
    } catch {
      // Handled by parent toast
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Lưu trích dẫn vào sổ tay"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in duration-150"
    >
      <div className="w-full max-w-lg bg-canvas dark:bg-[#1a1917] rounded-lg shadow-2xl border border-hairline dark:border-[#2f2b26] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="h-11 px-4 border-b border-hairline dark:border-[#2f2b26] flex items-center justify-between">
          <div className="flex items-center gap-2 font-serif font-semibold text-xs text-ink dark:text-zinc-100">
            <BookmarkPlus className="w-4 h-4 text-primary" />
            <span>Lưu trích dẫn vào sổ tay (Trang {pageNumber})</span>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Đóng hộp thoại"
            className="p-1 rounded hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-4 space-y-3.5 text-xs">
          {/* Selected Quote Preview */}
          <div className="p-3 rounded-md bg-surface-soft dark:bg-[#22201d] border border-hairline dark:border-[#2e2a25] space-y-1">
            <div className="flex items-center gap-1 text-[10px] text-muted font-mono uppercase">
              <Quote className="w-3 h-3 text-primary" />
              <span>Đoạn văn trích dẫn nguyên văn</span>
            </div>
            <p className="font-serif italic text-ink dark:text-zinc-200 line-clamp-4 leading-relaxed">
              &ldquo;{selectedText}&rdquo;
            </p>
          </div>

          {/* User Reflection Memo */}
          <div className="space-y-1">
            <label className="block text-[11px] font-sans font-medium text-ink dark:text-zinc-200">
              Ghi chú phản biện / ý tưởng cá nhân (Tùy chọn)
            </label>
            <textarea
              value={userNote}
              onChange={(e) => setUserNote(e.target.value)}
              placeholder="Nhập suy nghĩ hoặc lý do trích dẫn luận điểm này..."
              rows={3}
              className="w-full p-2.5 rounded-md bg-canvas dark:bg-[#141311] border border-hairline focus:border-primary outline-none resize-none font-sans text-xs"
            />
          </div>

          {/* Tags */}
          <div className="space-y-1">
            <label className="block text-[11px] font-sans font-medium text-ink dark:text-zinc-200">
              Nhãn phân loại (Tags)
            </label>
            <input
              type="text"
              value={tagsInput}
              onChange={(e) => setTagsInput(e.target.value)}
              placeholder="ví dụ: methodology, formula, limitation..."
              className="w-full px-2.5 py-1.5 rounded-md bg-canvas dark:bg-[#141311] border border-hairline focus:border-primary outline-none font-mono text-xs"
            />
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-end gap-2 pt-2 border-t border-hairline dark:border-[#2f2b26]">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 rounded-md hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink font-medium"
            >
              Hủy
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-1.5 rounded-md bg-primary hover:bg-primary/90 text-white font-medium shadow-xs disabled:opacity-50"
            >
              {isSubmitting ? "Đang lưu..." : "Lưu vào sổ tay"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
