import { useState } from "react";
import { Quote, Tag, Trash2, Edit3, ArrowUpRight, Check, Eye } from "lucide-react";
import type { NoteResponse, NoteListItemResponse } from "@/types/note";

interface NoteCardProps {
  note: NoteResponse | NoteListItemResponse;
  onJumpToPage?: (page: number, noteId: string) => void;
  onUpdateNote?: (noteId: string, updatedNote: string, tags: string[], version: number) => Promise<void>;
  onDeleteNote?: (noteId: string) => Promise<void>;
  onInspectNote?: (noteId: string) => void;
}

export function NoteCard({
  note,
  onJumpToPage,
  onUpdateNote,
  onDeleteNote,
  onInspectNote,
}: NoteCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedUserNote, setEditedUserNote] = useState(note.user_note || "");
  const [editedTags, setEditedTags] = useState(note.tags.join(", "));
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSave = async () => {
    if (!onUpdateNote) return;
    setIsSubmitting(true);
    try {
      const parsedTags = editedTags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);
      await onUpdateNote(note.id, editedUserNote, parsedTags, note.version);
      setIsEditing(false);
    } catch {
      // Error handled by parent toast
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      role="article"
      aria-label={`Ghi chú tại trang ${note.page_number}`}
      className="p-4 rounded-lg bg-surface-card dark:bg-[#1f1e1b] border border-hairline dark:border-[#332f29] space-y-2.5 transition-all duration-150 hover:shadow-2xs text-xs"
    >
      {/* Quotation block with Citation Reference */}
      <div className="flex items-start gap-2 text-ink dark:text-zinc-100">
        <Quote className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
        <p className="flex-1 font-serif italic text-xs leading-relaxed line-clamp-4">
          &ldquo;{note.selected_text}&rdquo;
        </p>
      </div>

      {/* Page Badge & Detached Status */}
      <div className="flex items-center justify-between text-[11px] pt-1">
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => onJumpToPage?.(note.page_number, note.id)}
            aria-label={`Xem trên trang ${note.page_number}`}
            className="inline-flex items-center gap-0.5 px-2 py-0.5 rounded-full font-mono text-[10px] font-semibold bg-surface-soft hover:bg-surface-cream-strong dark:bg-[#282622] text-primary transition-colors border border-hairline"
          >
            <span>Trang {note.page_number}</span>
            <ArrowUpRight className="w-2.5 h-2.5" />
          </button>

          {note.is_source_detached && (
            <span className="px-1.5 py-0.5 rounded text-[10px] bg-amber-500/10 text-amber-600 dark:text-amber-400 font-mono">
              Nguồn đã gỡ
            </span>
          )}
        </div>

        {/* Action icons */}
        <div className="flex items-center gap-1">
          {onInspectNote && (
            <button
              type="button"
              onClick={() => onInspectNote(note.id)}
              aria-label="Xem chi tiết ghi chú & snapshot đóng băng"
              title="Xem chi tiết ghi chú (Frozen Snapshot)"
              className="p-1 rounded text-muted hover:text-ink transition-colors cursor-pointer"
            >
              <Eye className="w-3.5 h-3.5" />
            </button>
          )}

          {onUpdateNote && !isEditing && (
            <button
              type="button"
              onClick={() => setIsEditing(true)}
              aria-label="Chỉnh sửa ghi chú"
              className="p-1 rounded text-muted hover:text-ink transition-colors"
            >
              <Edit3 className="w-3.5 h-3.5" />
            </button>
          )}

          {onDeleteNote && (
            <button
              type="button"
              onClick={() => onDeleteNote(note.id)}
              aria-label="Xóa ghi chú"
              className="p-1 rounded text-muted hover:text-rose-500 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* User Memo Note or Edit Form */}
      {isEditing ? (
        <div className="pt-2 border-t border-hairline dark:border-[#332f29] space-y-2">
          <textarea
            value={editedUserNote}
            onChange={(e) => setEditedUserNote(e.target.value)}
            placeholder="Ghi chú phản biện cá nhân..."
            rows={2}
            className="w-full p-2 text-xs rounded-md bg-canvas dark:bg-[#161513] border border-hairline focus:border-primary outline-none resize-none font-sans"
          />
          <input
            type="text"
            value={editedTags}
            onChange={(e) => setEditedTags(e.target.value)}
            placeholder="Tags (phân cách dấu phẩy: method, formula...)"
            className="w-full px-2 py-1 text-xs rounded-md bg-canvas dark:bg-[#161513] border border-hairline focus:border-primary outline-none font-mono"
          />
          <div className="flex justify-end gap-1.5 pt-1">
            <button
              type="button"
              onClick={() => setIsEditing(false)}
              className="px-2 py-1 rounded text-[11px] hover:bg-black/5 dark:hover:bg-white/5 text-muted"
            >
              Hủy
            </button>
            <button
              type="button"
              onClick={handleSave}
              disabled={isSubmitting}
              className="px-2.5 py-1 rounded text-[11px] font-medium bg-primary text-white hover:bg-primary/90 flex items-center gap-1"
            >
              <Check className="w-3 h-3" />
              <span>Lưu</span>
            </button>
          </div>
        </div>
      ) : (
        note.user_note && (
          <div className="p-2 rounded bg-surface-soft/60 dark:bg-[#252320] border border-hairline/60 dark:border-[#2f2b26] text-muted-strong dark:text-zinc-300 font-sans text-xs leading-relaxed">
            {note.user_note}
          </div>
        )
      )}

      {/* Tags list */}
      {note.tags && note.tags.length > 0 && !isEditing && (
        <div className="flex flex-wrap items-center gap-1 pt-1">
          <Tag className="w-2.5 h-2.5 text-muted/60 shrink-0" />
          {note.tags.map((tag, idx) => (
            <span
              key={idx}
              className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-surface-cream-strong/50 dark:bg-[#2c2925] text-muted border border-hairline/40"
            >
              #{tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
