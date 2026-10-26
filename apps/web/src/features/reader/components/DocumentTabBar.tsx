import { useState } from "react";
import { Plus, X, Star, FileText, Trash2, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";
import type { DocumentListItem } from "@/types/document";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface DocumentTabBarProps {
  documents: DocumentListItem[];
  openDocumentIds: string[];
  activeDocumentId: string | null;
  onSelectDocument: (documentId: string) => void;
  onCloseDocument: (documentId: string) => void;
  onAddDocument: () => void;
  onToggleStar?: (documentId: string) => void;
  onDeleteDocument?: (documentId: string) => void;
}

export function DocumentTabBar({
  documents,
  openDocumentIds,
  activeDocumentId,
  onSelectDocument,
  onCloseDocument,
  onAddDocument,
  onToggleStar,
  onDeleteDocument,
}: DocumentTabBarProps) {
  const [docToDelete, setDocToDelete] = useState<DocumentListItem | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const docMap = new Map(documents.map((d) => [d.id, d]));

  const handleConfirmDelete = async () => {
    if (!docToDelete || !onDeleteDocument) return;
    try {
      setIsDeleting(true);
      await onDeleteDocument(docToDelete.id);
      setDocToDelete(null);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <>
      <div
        role="tablist"
        aria-label="Danh sách bài báo đang mở"
        className="h-11 border-b border-hairline dark:border-[#2b2824] bg-surface-soft/60 dark:bg-[#1f1e1b] flex items-center px-2 gap-1.5 overflow-x-auto scrollbar-none select-none"
      >
        {openDocumentIds.map((docId) => {
          const doc = docMap.get(docId);
          const isActive = docId === activeDocumentId;
          const displayName = doc?.title || doc?.filename || `Bài báo ${docId.slice(0, 6)}`;
          const isPersistent = doc?.is_persistent ?? false;

          return (
            <div
              key={docId}
              role="tab"
              aria-selected={isActive}
              tabIndex={0}
              onClick={() => onSelectDocument(docId)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  onSelectDocument(docId);
                }
              }}
              className={cn(
                "group relative flex items-center h-8 px-3 gap-2 rounded-md text-xs font-medium cursor-pointer transition-all duration-150 border",
                isActive
                  ? "bg-surface-cream-strong dark:bg-[#2c2925] border-hairline dark:border-[#3d3832] text-ink dark:text-zinc-100 shadow-2xs font-semibold"
                  : "bg-transparent border-transparent text-muted hover:bg-surface-cream-strong/50 dark:hover:bg-[#252320] hover:text-ink dark:hover:text-zinc-200"
              )}
              title={displayName}
            >
              <FileText
                className={cn(
                  "w-3.5 h-3.5 shrink-0",
                  isActive ? "text-primary" : "text-muted/70"
                )}
              />

              <span className="max-w-[100px] sm:max-w-[160px] truncate text-left">{displayName}</span>

              {/* Star toggle button */}
              {onToggleStar && (
                <button
                  type="button"
                  aria-label={isPersistent ? "Đã lưu vào thư viện" : "Lưu bài báo vào thư viện"}
                  onClick={(e) => {
                    e.stopPropagation();
                    onToggleStar(docId);
                  }}
                  className={cn(
                    "p-0.5 rounded hover:bg-black/5 dark:hover:bg-white/10 transition-colors cursor-pointer",
                    isPersistent ? "text-amber-500" : "text-muted/40 hover:text-amber-500"
                  )}
                >
                  <Star
                    className={cn("w-3 h-3", isPersistent && "fill-amber-500")}
                  />
                </button>
              )}

              {/* Delete document button (Cascade Purge) */}
              {onDeleteDocument && (
                <button
                  type="button"
                  aria-label={`Xóa bài báo ${displayName}`}
                  title="Xóa vĩnh viễn tài liệu khỏi hệ thống"
                  onClick={(e) => {
                    e.stopPropagation();
                    setDocToDelete(doc || { id: docId, filename: displayName, is_persistent: false, status: "completed", created_at: "" });
                  }}
                  className="opacity-0 group-hover:opacity-100 p-0.5 rounded hover:bg-red-500/10 dark:hover:bg-red-500/20 text-muted hover:text-red-600 transition-opacity cursor-pointer"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              )}

              {/* Close tab button */}
              {openDocumentIds.length > 1 && (
                <button
                  type="button"
                  aria-label={`Đóng tab ${displayName}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    onCloseDocument(docId);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-0.5 rounded hover:bg-black/10 dark:hover:bg-white/10 transition-opacity text-muted hover:text-ink cursor-pointer"
                >
                  <X className="w-3 h-3" />
                </button>
              )}
            </div>
          );
        })}

        {/* Add new document to session (Max 5) */}
        {openDocumentIds.length < 5 && (
          <button
            type="button"
            onClick={onAddDocument}
            aria-label="Nạp thêm bài báo vào phiên (Tối đa 5 bài)"
            className="flex items-center justify-center w-7 h-7 rounded-md text-muted hover:text-ink dark:hover:text-zinc-100 hover:bg-surface-cream-strong/60 dark:hover:bg-[#2a2723] transition-colors border border-dashed border-hairline dark:border-[#3a352f] cursor-pointer"
            title="Nạp thêm bài báo vào phiên (Tối đa 5 bài)"
          >
            <Plus className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Confirmation Dialog for Permanent Document Deletion */}
      <Dialog open={Boolean(docToDelete)} onOpenChange={(open) => !open && setDocToDelete(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <div className="flex items-center gap-2 text-red-600 mb-1">
              <AlertTriangle className="w-5 h-5 shrink-0" />
              <DialogTitle className="text-base font-serif font-bold text-red-600">
                Xóa vĩnh viễn tài liệu?
              </DialogTitle>
            </div>
            <DialogDescription className="text-xs text-muted leading-relaxed">
              Bạn có chắc chắn muốn xóa tài liệu{" "}
              <strong className="text-ink dark:text-zinc-200">
                "{docToDelete?.title || docToDelete?.filename}"
              </strong>{" "}
              khỏi hệ thống?
              <br /><br />
              Thao tác này sẽ xóa vĩnh viễn tệp cùng toàn bộ phân đoạn và dữ liệu liên quan. Hành động này không thể hoàn tác!
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="mt-4 gap-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setDocToDelete(null)}
              disabled={isDeleting}
            >
              Hủy
            </Button>
            <button
              type="button"
              onClick={handleConfirmDelete}
              disabled={isDeleting}
              className="inline-flex items-center justify-center px-4 py-2 text-xs font-semibold rounded-md bg-red-600 hover:bg-red-700 text-white transition-colors cursor-pointer disabled:opacity-50"
            >
              {isDeleting ? "Đang xóa..." : "Xác nhận xóa"}
            </button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
