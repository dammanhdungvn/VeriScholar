import { useState, useEffect } from "react";
import { Folder, FolderInput, X, Check } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { documentsApi } from "@/features/documents/api/documentsApi";
import { DOCUMENT_QUERY_KEYS } from "@/features/documents/hooks/useDocumentQueries";
import { useFoldersListQuery, FOLDER_QUERY_KEYS } from "../hooks/useFolderQueries";
import { cn } from "@/lib/utils";

interface MoveToFolderModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentId: string;
  documentTitle?: string;
  currentFolderId?: string | null;
  onSuccess?: () => void;
}

export function MoveToFolderModal({
  isOpen,
  onClose,
  documentId,
  documentTitle,
  currentFolderId,
  onSuccess,
}: MoveToFolderModalProps) {
  const queryClient = useQueryClient();
  const [selectedFolderId, setSelectedFolderId] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const { data: folders = [] } = useFoldersListQuery();

  useEffect(() => {
    setSelectedFolderId(currentFolderId || "");
  }, [currentFolderId, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!documentId) return;

    setIsSubmitting(true);
    setErrorMsg(null);

    try {
      await documentsApi.starDocument(
        documentId,
        selectedFolderId ? selectedFolderId : null
      );

      queryClient.invalidateQueries({ queryKey: DOCUMENT_QUERY_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: DOCUMENT_QUERY_KEYS.detail(documentId) });
      queryClient.invalidateQueries({ queryKey: FOLDER_QUERY_KEYS.all });
      queryClient.invalidateQueries({ queryKey: FOLDER_QUERY_KEYS.tree });

      onSuccess?.();
      onClose();
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to move document.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Move Document to Folder"
      onClick={(e) => {
        if (e.target === e.currentTarget && !isSubmitting) onClose();
      }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in duration-150 text-xs"
    >
      <div className="w-full max-w-md bg-white dark:bg-[#1c1b18] rounded-2xl shadow-xl border border-[#e8e4dc] dark:border-[#2e2b26] p-5 space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-[#f0eae1] dark:border-[#2a2824]">
          <div className="flex items-center gap-2 text-sm font-semibold font-anthropic-serif text-ink dark:text-zinc-100">
            <FolderInput className="w-4 h-4 text-[#c15f3e]" />
            <span>Move to Folder</span>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            className="p-1 rounded-lg text-muted hover:text-ink dark:hover:text-zinc-200 hover:bg-black/5 dark:hover:bg-white/5 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Paper title info */}
        {documentTitle && (
          <div className="px-3 py-2 rounded-xl bg-[#fbf9f5] dark:bg-[#201e1a] border border-[#f0eae1] dark:border-[#2e2b26]">
            <p className="text-[11px] text-muted dark:text-zinc-400 font-mono">Selected Paper:</p>
            <p className="text-xs font-medium text-ink dark:text-zinc-100 line-clamp-2 mt-0.5 font-anthropic-serif">
              {documentTitle}
            </p>
          </div>
        )}

        {errorMsg && (
          <div className="p-2.5 rounded-lg bg-rose-500/10 text-rose-700 dark:text-rose-400 text-xs">
            {errorMsg}
          </div>
        )}

        {/* Folder Selection List */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-[11px] font-medium text-muted dark:text-zinc-400 mb-2">
              Select Destination Folder
            </label>
            <div className="max-h-48 overflow-y-auto space-y-1.5 pr-1">
              {/* Root / Unassigned Option */}
              <button
                type="button"
                onClick={() => setSelectedFolderId("")}
                className={cn(
                  "w-full px-3 py-2 rounded-xl border text-left flex items-center justify-between transition-colors cursor-pointer",
                  selectedFolderId === ""
                    ? "bg-[#c15f3e]/10 border-[#c15f3e] text-[#c15f3e] font-semibold"
                    : "border-[#e8e4dc] dark:border-[#2a2824] bg-white dark:bg-[#1f1d1a] text-ink dark:text-zinc-200 hover:border-[#c15f3e]/40"
                )}
              >
                <div className="flex items-center gap-2">
                  <Folder className="w-4 h-4 text-muted" />
                  <span>Unassigned (All Papers)</span>
                </div>
                {selectedFolderId === "" && <Check className="w-4 h-4 text-[#c15f3e]" />}
              </button>

              {/* Folders List */}
              {folders.map((folder) => {
                const isSelected = selectedFolderId === folder.id;
                return (
                  <button
                    key={folder.id}
                    type="button"
                    onClick={() => setSelectedFolderId(folder.id)}
                    className={cn(
                      "w-full px-3 py-2 rounded-xl border text-left flex items-center justify-between transition-colors cursor-pointer",
                      isSelected
                        ? "bg-[#c15f3e]/10 border-[#c15f3e] text-[#c15f3e] font-semibold"
                        : "border-[#e8e4dc] dark:border-[#2a2824] bg-white dark:bg-[#1f1d1a] text-ink dark:text-zinc-200 hover:border-[#c15f3e]/40"
                    )}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <Folder className="w-4 h-4 text-[#c15f3e]/70 shrink-0" />
                      <span className="truncate">{folder.name}</span>
                    </div>
                    {isSelected && <Check className="w-4 h-4 text-[#c15f3e] shrink-0" />}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-[#f0eae1] dark:border-[#2a2824]">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-3 py-1.5 rounded-lg border border-[#e2dcd2] dark:border-[#322f2a] text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200 hover:bg-black/5 transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-3.5 py-1.5 rounded-lg bg-[#c15f3e] hover:bg-[#a84f32] text-white font-medium shadow-xs disabled:opacity-50 transition-colors cursor-pointer"
            >
              {isSubmitting ? "Moving..." : "Move Document"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
