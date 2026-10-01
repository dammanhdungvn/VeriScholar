import { useState, useMemo } from "react";
import { Sparkles, Search, Plus, BookOpen, AlertCircle, RefreshCw } from "lucide-react";
import {
  useNotesList,
  useCreateNoteMutation,
  useUpdateNoteMutation,
  useDeleteNoteMutation,
  useSynthesizeNotesMutation,
} from "../hooks/useNotesQuery";
import { NoteCard } from "./NoteCard";
import { CreateNoteDialog } from "./CreateNoteDialog";
import { NoteSynthesisModal } from "./NoteSynthesisModal";
import { SynthesizedLessonCard } from "./SynthesizedLessonCard";
import { NoteDetailModal } from "./NoteDetailModal";
import { useReaderStore } from "@/features/reader/stores/useReaderStore";
import type { NoteSynthesisResponse, InteractiveBadgeResponse } from "@/types/note";
import type { BoundingBox } from "@/types/api";

interface NotesPanelContainerProps {
  documentId?: string | null;
}

export function NotesPanelContainer({ documentId }: NotesPanelContainerProps) {
  const [searchTag, setSearchTag] = useState("");
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isSynthesisOpen, setIsSynthesisOpen] = useState(false);
  const [activeSynthesis, setActiveSynthesis] = useState<NoteSynthesisResponse | null>(null);
  const [inspectNoteId, setInspectNoteId] = useState<string | null>(null);

  const {
    data: notesData,
    isLoading,
    isError,
    refetch,
  } = useNotesList({
    document_id: documentId || undefined,
    tag: searchTag.trim() || undefined,
  });

  const createMutation = useCreateNoteMutation();
  const updateMutation = useUpdateNoteMutation();
  const deleteMutation = useDeleteNoteMutation();
  const synthesizeMutation = useSynthesizeNotesMutation();

  const setActiveCitation = useReaderStore((s) => s.setActiveCitation);
  const notes = useMemo(() => notesData?.data || [], [notesData]);

  const handleJumpToPage = (page: number, noteId: string) => {
    const note = notes.find((n) => n.id === noteId);
    const bboxes = (note as unknown as { bounding_boxes?: BoundingBox[] })?.bounding_boxes;
    const bbox = bboxes && bboxes.length > 0 ? bboxes[0] : null;
    setActiveCitation(noteId, bbox, page);
  };

  const handleJumpToBadge = (badge: InteractiveBadgeResponse) => {
    const bbox = badge.bounding_boxes[0] ?? null;
    setActiveCitation(badge.badge_id, bbox, badge.page_number);
  };

  const handleUpdateNote = async (
    noteId: string,
    updatedNote: string,
    tags: string[],
    version: number
  ) => {
    await updateMutation.mutateAsync({
      noteId,
      data: { user_note: updatedNote, tags },
      etag: `v${version}`,
    });
  };

  const handleDeleteNote = async (noteId: string) => {
    await deleteMutation.mutateAsync(noteId);
  };

  return (
    <div
      role="region"
      aria-label="Sổ tay nghiên cứu cá nhân"
      className="flex-1 flex flex-col h-full bg-canvas dark:bg-[#181715] overflow-hidden text-xs"
    >
      {/* Top Action Bar */}
      <div className="h-11 px-4 border-b border-hairline dark:border-[#2b2824] flex items-center justify-between gap-2 shrink-0 bg-surface-soft/40 dark:bg-[#1a1917]">
        {/* Search by tag */}
        <div className="flex-1 relative max-w-xs">
          <Search className="w-3.5 h-3.5 text-muted absolute left-2.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTag}
            onChange={(e) => setSearchTag(e.target.value)}
            placeholder="Lọc theo nhãn tag..."
            className="w-full pl-8 pr-3 py-1 rounded-md bg-canvas dark:bg-[#141311] border border-hairline focus:border-primary outline-none font-mono text-[11px]"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => setIsSynthesisOpen(true)}
            disabled={notes.length === 0}
            className="flex items-center gap-1 px-2.5 py-1 rounded-md bg-surface-cream-strong hover:bg-surface-card dark:bg-[#282622] text-primary font-medium border border-hairline transition-colors disabled:opacity-40"
            title="AI Tổng hợp ghi chú thành bài học đúc kết"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Tổng hợp AI</span>
          </button>

          <button
            type="button"
            onClick={() => setIsCreateOpen(true)}
            className="flex items-center gap-1 px-2.5 py-1 rounded-md bg-primary hover:bg-primary/90 text-white font-medium shadow-2xs transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Thêm</span>
          </button>
        </div>
      </div>

      {/* Main Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Active Synthesized Lesson Display if present */}
        {activeSynthesis && (
          <SynthesizedLessonCard
            synthesis={activeSynthesis}
            onJumpToBadge={handleJumpToBadge}
            onClose={() => setActiveSynthesis(null)}
          />
        )}

        {/* 5 UI States for Notes */}
        {isLoading ? (
          <div className="space-y-3 py-6">
            <div className="h-20 bg-surface-soft/60 dark:bg-[#201e1b] rounded-lg animate-pulse" />
            <div className="h-20 bg-surface-soft/60 dark:bg-[#201e1b] rounded-lg animate-pulse" />
          </div>
        ) : isError ? (
          <div className="text-center py-12 space-y-2">
            <AlertCircle className="w-6 h-6 text-amber-500 mx-auto" />
            <p className="text-muted">Không thể tải danh sách ghi chú.</p>
            <button
              type="button"
              onClick={() => refetch()}
              className="inline-flex items-center gap-1 px-3 py-1 rounded bg-surface-soft text-primary border border-hairline text-xs"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Thử lại</span>
            </button>
          </div>
        ) : notes.length === 0 ? (
          <div className="text-center py-16 space-y-3">
            <BookOpen className="w-8 h-8 text-muted/40 mx-auto" />
            <div className="space-y-1">
              <h4 className="font-serif font-medium text-sm text-ink dark:text-zinc-200">
                Sổ tay chưa có ghi chú nào
              </h4>
              <p className="text-muted max-w-xs mx-auto text-xs">
                Bôi đen đoạn văn bản trên bài báo bên trái và bấm &ldquo;Thêm vào sổ tay&rdquo; để lưu trích dẫn.
              </p>
            </div>
            <button
              type="button"
              onClick={() => setIsCreateOpen(true)}
              className="px-3.5 py-1.5 rounded-md bg-surface-cream-strong hover:bg-surface-card text-ink font-medium border border-hairline"
            >
              Tạo ghi chú thủ công
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {notes.map((note) => (
              <NoteCard
                key={note.id}
                note={note}
                onJumpToPage={handleJumpToPage}
                onUpdateNote={handleUpdateNote}
                onDeleteNote={handleDeleteNote}
                onInspectNote={(id) => setInspectNoteId(id)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Create Note Dialog */}
      <CreateNoteDialog
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        documentId={documentId}
        selectedText=""
        pageNumber={1}
        onSubmit={async (payload) => {
          await createMutation.mutateAsync({
            document_id: payload.document_id,
            selected_text: payload.selected_text || "Trích dẫn thủ công",
            page_number: payload.page_number,
            user_note: payload.user_note,
            tags: payload.tags,
          });
        }}
      />

      {/* Note Synthesis Modal */}
      <NoteSynthesisModal
        isOpen={isSynthesisOpen}
        onClose={() => setIsSynthesisOpen(false)}
        selectedNoteIds={notes.map((n) => n.id)}
        totalNotesCount={notes.length}
        isLoading={synthesizeMutation.isPending}
        onSynthesize={async (request) => {
          const result = await synthesizeMutation.mutateAsync({
            ...request,
            note_ids: notes.map((n) => n.id),
          });
          setActiveSynthesis(result);
        }}
      />

      {/* Note Detail Modal (Frozen Evidence Snapshot Inspection) */}
      <NoteDetailModal
        isOpen={Boolean(inspectNoteId)}
        onClose={() => setInspectNoteId(null)}
        noteId={inspectNoteId}
        onJumpToPage={handleJumpToPage}
      />
    </div>
  );
}
