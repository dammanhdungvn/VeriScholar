import { useState } from "react";
import { X, Star, Folder, CheckCircle2, AlertCircle, Plus } from "lucide-react";
import { documentsApi } from "../api/documentsApi";
import { useQueryClient } from "@tanstack/react-query";
import { DOCUMENT_QUERY_KEYS } from "../hooks/useDocumentQueries";
import {
  useFoldersListQuery,
  useCreateFolderMutation,
  FOLDER_QUERY_KEYS,
} from "@/features/library/hooks/useFolderQueries";

interface StarDocumentModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentId: string;
  documentTitle?: string;
  isStarred?: boolean;
  onStarSuccess?: () => void;
}

export function StarDocumentModal({
  isOpen,
  onClose,
  documentId,
  documentTitle,
  isStarred = false,
  onStarSuccess,
}: StarDocumentModalProps) {
  const queryClient = useQueryClient();
  const [folderId, setFolderId] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // New folder creation state
  const [isCreatingFolder, setIsCreatingFolder] = useState(false);
  const [newFolderName, setNewFolderName] = useState("");

  const { data: folders = [] } = useFoldersListQuery();
  const createFolderMutation = useCreateFolderMutation();

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!documentId) return;

    setIsSubmitting(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      await documentsApi.starDocument(documentId, folderId.trim() || null);

      // Invalidate documents lists and details
      queryClient.invalidateQueries({ queryKey: DOCUMENT_QUERY_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: DOCUMENT_QUERY_KEYS.detail(documentId) });

      setSuccessMsg(
        isStarred
          ? "Đã cập nhật thư mục lưu trữ thành công!"
          : "Đã lưu vĩnh viễn bài báo vào thư viện cá nhân (Atomic Promotion)!"
      );
      onStarSuccess?.();
      setTimeout(() => {
        onClose();
      }, 700);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Thao tác lưu bài báo thất bại.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Lưu bài báo vào thư viện cá nhân"
      onClick={(e) => {
        if (e.target === e.currentTarget && !isSubmitting) onClose();
      }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in duration-150 text-xs"
    >
      <div className="w-full max-w-md bg-canvas dark:bg-[#1a1917] rounded-xl shadow-2xl border border-hairline dark:border-[#2f2b26] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="h-12 px-5 border-b border-hairline dark:border-[#2f2b26] flex items-center justify-between shrink-0 bg-surface-soft/40 dark:bg-[#1f1d1a]">
          <div className="flex items-center gap-2 font-serif font-semibold text-sm text-ink dark:text-zinc-100">
            <Star className="w-4 h-4 text-amber-500 fill-amber-500" />
            <span>Lưu vĩnh viễn vào Thư viện (Star Document)</span>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            aria-label="Đóng hộp thoại"
            className="p-1 rounded-md hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink disabled:opacity-40"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          {documentTitle && (
            <div className="p-2.5 rounded-lg bg-surface-soft/60 dark:bg-[#22201d] border border-hairline dark:border-[#302c26]">
              <span className="text-[11px] text-muted block mb-0.5">Tài liệu:</span>
              <p className="font-serif font-medium text-ink dark:text-zinc-200 line-clamp-2">
                {documentTitle}
              </p>
            </div>
          )}

          <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-800 dark:text-amber-300 leading-relaxed text-[11px]">
            Khi gắn sao, bài báo sẽ được lưu trữ vĩnh viễn trong thư viện nghiên cứu cá nhân của bạn.
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label htmlFor="folder-select" className="text-xs font-medium text-ink dark:text-zinc-200 flex items-center gap-1.5">
                <Folder className="w-3.5 h-3.5 text-muted" />
                <span>Thư mục lưu trữ:</span>
              </label>
              {!isCreatingFolder && (
                <button
                  type="button"
                  onClick={() => setIsCreatingFolder(true)}
                  className="text-[11px] text-amber-600 hover:text-amber-700 dark:text-amber-400 font-medium flex items-center gap-1 cursor-pointer"
                >
                  <Plus className="w-3 h-3" />
                  <span>Tạo thư mục mới</span>
                </button>
              )}
            </div>

            {isCreatingFolder ? (
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={newFolderName}
                  onChange={(e) => setNewFolderName(e.target.value)}
                  placeholder="Nhập tên thư mục mới..."
                  className="flex-1 px-3 py-1.5 rounded-lg bg-canvas dark:bg-[#151412] border border-amber-500 outline-none font-sans text-xs"
                />
                <button
                  type="button"
                  disabled={!newFolderName.trim()}
                  onClick={async () => {
                    if (!newFolderName.trim()) return;
                    try {
                      const created = await createFolderMutation.mutateAsync({
                        name: newFolderName.trim(),
                      });
                      queryClient.invalidateQueries({ queryKey: FOLDER_QUERY_KEYS.all });
                      setFolderId(created.id);
                      setIsCreatingFolder(false);
                      setNewFolderName("");
                    } catch (err) {
                      setErrorMsg("Không thể tạo thư mục mới.");
                    }
                  }}
                  className="px-2.5 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-600 text-white text-xs font-medium transition-colors disabled:opacity-50 cursor-pointer"
                >
                  Tạo
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setIsCreatingFolder(false);
                    setNewFolderName("");
                  }}
                  className="px-2 py-1.5 rounded-lg hover:bg-black/5 dark:hover:bg-white/5 text-muted text-xs cursor-pointer"
                >
                  Hủy
                </button>
              </div>
            ) : (
              <select
                id="folder-select"
                value={folderId}
                onChange={(e) => setFolderId(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-canvas dark:bg-[#151412] border border-hairline focus:border-amber-500 outline-none font-sans text-xs cursor-pointer"
              >
                <option value="">Thư viện chung (Không gán thư mục)</option>
                {folders.map((f) => (
                  <option key={f.id} value={f.id}>
                    📁 {f.name} ({f.document_count || 0} bài báo)
                  </option>
                ))}
              </select>
            )}
            <p className="text-[10px] text-muted">
              Chọn thư mục đề tài nghiên cứu để phân loại khoa học.
            </p>
          </div>

          {errorMsg && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {successMsg && (
            <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-hairline dark:border-[#2f2b26]">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 rounded-lg border border-hairline hover:bg-black/5 dark:hover:bg-white/5 font-medium text-muted hover:text-ink transition-colors disabled:opacity-40"
            >
              Hủy
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-600 text-white font-medium shadow-xs transition-colors disabled:opacity-50 cursor-pointer"
            >
              <Star className="w-3.5 h-3.5 fill-white" />
              <span>{isSubmitting ? "Đang lưu..." : isStarred ? "Cập nhật" : "Lưu vào Thư viện"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
