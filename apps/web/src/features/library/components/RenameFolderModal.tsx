import { useState, useEffect } from "react";
import { Pencil, X } from "lucide-react";
import { useUpdateFolderMutation } from "../hooks/useFolderQueries";
import type { FolderItem } from "../types";

interface RenameFolderModalProps {
  isOpen: boolean;
  onClose: () => void;
  folder: FolderItem | null;
  onSuccess?: () => void;
}

export function RenameFolderModal({
  isOpen,
  onClose,
  folder,
  onSuccess,
}: RenameFolderModalProps) {
  const [folderName, setFolderName] = useState("");
  const updateFolderMutation = useUpdateFolderMutation();

  useEffect(() => {
    if (folder) {
      setFolderName(folder.name);
    }
  }, [folder]);

  if (!isOpen || !folder) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = folderName.trim();
    if (!trimmed || trimmed === folder.name) {
      onClose();
      return;
    }

    try {
      await updateFolderMutation.mutateAsync({
        id: folder.id,
        payload: { name: trimmed },
      });
      onSuccess?.();
      onClose();
    } catch (err) {
      console.warn("Failed to rename folder:", err);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Rename Folder"
      onClick={(e) => {
        if (e.target === e.currentTarget && !updateFolderMutation.isPending) onClose();
      }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in duration-150 text-xs"
    >
      <div className="w-full max-w-sm bg-white dark:bg-[#1c1b18] rounded-2xl shadow-xl border border-[#e8e4dc] dark:border-[#2e2b26] p-5 space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-[#f0eae1] dark:border-[#2a2824]">
          <div className="flex items-center gap-2 text-sm font-semibold font-anthropic-serif text-ink dark:text-zinc-100">
            <Pencil className="w-4 h-4 text-[#c15f3e]" />
            <span>Rename Folder</span>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={updateFolderMutation.isPending}
            className="p-1 rounded-lg text-muted hover:text-ink dark:hover:text-zinc-200 hover:bg-black/5 dark:hover:bg-white/5 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-[11px] font-medium text-muted dark:text-zinc-400 mb-1.5">
              Folder Name
            </label>
            <input
              type="text"
              autoFocus
              required
              value={folderName}
              onChange={(e) => setFolderName(e.target.value)}
              className="w-full h-9 px-3 rounded-lg bg-[#fbf9f5] dark:bg-[#201e1a] border border-[#e2dcd2] dark:border-[#322f2a] text-xs text-ink dark:text-zinc-100 placeholder:text-muted dark:placeholder:text-zinc-500 outline-none focus:border-[#c15f3e] transition-colors"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={updateFolderMutation.isPending}
              className="px-3 py-1.5 rounded-lg border border-[#e2dcd2] dark:border-[#322f2a] text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200 hover:bg-black/5 transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!folderName.trim() || updateFolderMutation.isPending}
              className="px-3.5 py-1.5 rounded-lg bg-[#c15f3e] hover:bg-[#a84f32] text-white font-medium shadow-xs disabled:opacity-50 transition-colors cursor-pointer"
            >
              {updateFolderMutation.isPending ? "Saving..." : "Save"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
