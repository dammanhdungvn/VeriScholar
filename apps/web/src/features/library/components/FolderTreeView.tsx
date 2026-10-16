import { useState } from "react";
import {
  Folder,
  FolderOpen,
  ChevronRight,
  ChevronDown,
  Plus,
  Trash2,
  Library,
  Loader2,
  FolderPlus,
} from "lucide-react";
import {
  useFolderTreeQuery,
  useCreateFolderMutation,
  useDeleteFolderMutation,
} from "../hooks/useFolderQueries";
import type { FolderTreeItem } from "../types";

export interface FolderTreeViewProps {
  selectedFolderId: string | null;
  onSelectFolder: (folderId: string | null) => void;
  className?: string;
}

const PRESET_COLORS = [
  "#6366f1", // Indigo
  "#cc785c", // Terracotta / Anthropic Coral
  "#10b981", // Emerald
  "#f59e0b", // Amber
  "#3b82f6", // Blue
  "#ec4899", // Pink
];

interface TreeNodeProps {
  item: FolderTreeItem;
  level: number;
  selectedFolderId: string | null;
  onSelectFolder: (id: string | null) => void;
  onDeleteFolder: (id: string) => void;
}

function TreeNode({
  item,
  level,
  selectedFolderId,
  onSelectFolder,
  onDeleteFolder,
}: TreeNodeProps) {
  const [isOpen, setIsOpen] = useState(true);
  const isSelected = selectedFolderId === item.id;
  const hasChildren = item.subfolders && item.subfolders.length > 0;

  return (
    <div className="select-none">
      <div
        style={{ paddingLeft: `${Math.min(level * 14 + 8, 48)}px` }}
        className={`group flex items-center justify-between pr-2 py-1.5 rounded-lg text-xs transition-colors cursor-pointer ${
          isSelected
            ? "bg-coral-500/15 text-coral-700 dark:text-coral-300 font-semibold"
            : "text-ink-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200 hover:bg-black/5 dark:hover:bg-white/5"
        }`}
        onClick={() => onSelectFolder(item.id)}
      >
        <div className="flex items-center gap-1.5 min-w-0 flex-1">
          {hasChildren ? (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                setIsOpen(!isOpen);
              }}
              className="p-0.5 hover:bg-black/10 dark:hover:bg-white/10 rounded transition-colors text-muted"
            >
              {isOpen ? (
                <ChevronDown className="w-3.5 h-3.5" />
              ) : (
                <ChevronRight className="w-3.5 h-3.5" />
              )}
            </button>
          ) : (
            <span className="w-3.5 h-3.5 shrink-0" />
          )}

          <div
            className="w-2 h-2 rounded-full shrink-0"
            style={{ backgroundColor: item.color || "#6366f1" }}
          />

          {isOpen && hasChildren ? (
            <FolderOpen className="w-3.5 h-3.5 shrink-0 text-amber-500" />
          ) : (
            <Folder className="w-3.5 h-3.5 shrink-0 text-amber-500" />
          )}

          <span className="truncate flex-1 font-sans">{item.name}</span>
        </div>

        <div className="flex items-center gap-1 shrink-0">
          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-black/5 dark:bg-white/10 text-muted">
            {item.document_count}
          </span>

          <button
            type="button"
            title="Xóa thư mục"
            onClick={(e) => {
              e.stopPropagation();
              onDeleteFolder(item.id);
            }}
            className="opacity-0 group-hover:opacity-100 p-1 hover:text-rose-600 rounded transition-opacity"
          >
            <Trash2 className="w-3 h-3" />
          </button>
        </div>
      </div>

      {hasChildren && isOpen && (
        <div className="space-y-0.5">
          {item.subfolders.map((sub) => (
            <TreeNode
              key={sub.id}
              item={sub}
              level={level + 1}
              selectedFolderId={selectedFolderId}
              onSelectFolder={onSelectFolder}
              onDeleteFolder={onDeleteFolder}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function FolderTreeView({
  selectedFolderId,
  onSelectFolder,
  className = "",
}: FolderTreeViewProps) {
  const { data: tree = [], isLoading } = useFolderTreeQuery();
  const createMutation = useCreateFolderMutation();
  const deleteMutation = useDeleteFolderMutation();

  const [isCreating, setIsCreating] = useState(false);
  const [newFolderName, setNewFolderName] = useState("");
  const [newFolderColor, setNewFolderColor] = useState(PRESET_COLORS[0]);

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFolderName.trim()) return;

    try {
      await createMutation.mutateAsync({
        name: newFolderName.trim(),
        parent_id: selectedFolderId,
        color: newFolderColor,
      });
      setNewFolderName("");
      setIsCreating(false);
    } catch (err) {
      console.warn("Failed to create folder:", err);
    }
  };

  const handleDeleteFolder = async (id: string) => {
    if (confirm("Bạn có chắc chắn muốn xóa thư mục này? Các bài báo sẽ được đưa về thư viện gốc.")) {
      try {
        await deleteMutation.mutateAsync(id);
        if (selectedFolderId === id) {
          onSelectFolder(null);
        }
      } catch (err) {
        console.warn("Failed to delete folder:", err);
      }
    }
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Folder Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-hairline dark:border-[#2f2b26]">
        <div className="flex items-center gap-1.5 font-medium text-xs text-ink dark:text-zinc-200">
          <Library className="w-3.5 h-3.5 text-coral-600 dark:text-coral-400" />
          <span>Thư mục đề tài</span>
        </div>

        <button
          type="button"
          onClick={() => setIsCreating(true)}
          title="Tạo thư mục mới"
          className="inline-flex items-center gap-1 px-2 py-1 rounded-md text-[11px] font-sans font-medium text-coral-600 dark:text-coral-400 hover:bg-coral-500/10 transition-colors cursor-pointer"
        >
          <Plus className="w-3 h-3" />
          <span>Mới</span>
        </button>
      </div>

      {/* Inline Create Folder Form */}
      {isCreating && (
        <form onSubmit={handleCreateSubmit} className="p-3 border-b border-hairline dark:border-[#2f2b26] space-y-2 bg-surface-soft/40 dark:bg-[#1a1917]">
          <div className="text-[11px] font-medium text-ink dark:text-zinc-200 flex items-center justify-between">
            <span className="flex items-center gap-1">
              <FolderPlus className="w-3.5 h-3.5 text-coral-600" />
              <span>Tạo thư mục {selectedFolderId ? "con" : "gốc"}</span>
            </span>
            <button
              type="button"
              onClick={() => setIsCreating(false)}
              className="text-muted hover:text-ink text-xs cursor-pointer"
            >
              ✕
            </button>
          </div>

          <input
            type="text"
            value={newFolderName}
            onChange={(e) => setNewFolderName(e.target.value)}
            placeholder="Tên đề tài / thư mục..."
            autoFocus
            className="w-full px-2.5 py-1 text-xs rounded border border-hairline focus:border-coral-500 outline-none bg-canvas dark:bg-[#201e1b]"
          />

          {/* Color Swatches */}
          <div className="flex items-center gap-1.5 pt-1">
            <span className="text-[10px] text-muted">Màu:</span>
            {PRESET_COLORS.map((c) => (
              <button
                key={c}
                type="button"
                onClick={() => setNewFolderColor(c)}
                style={{ backgroundColor: c }}
                className={`w-3.5 h-3.5 rounded-full transition-transform ${
                  newFolderColor === c ? "ring-2 ring-coral-500 scale-110" : ""
                }`}
              />
            ))}
          </div>

          <div className="flex items-center justify-end gap-1.5 pt-1">
            <button
              type="button"
              onClick={() => setIsCreating(false)}
              className="px-2 py-0.5 text-xs text-muted hover:text-ink cursor-pointer"
            >
              Hủy
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending || !newFolderName.trim()}
              className="px-2.5 py-1 text-xs font-medium bg-coral-500 hover:bg-coral-600 text-white rounded transition-colors disabled:opacity-50 cursor-pointer"
            >
              {createMutation.isPending ? "Đang tạo..." : "Tạo"}
            </button>
          </div>
        </form>
      )}

      {/* Tree View List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-0.5">
        {/* Root All Documents item */}
        <div
          onClick={() => onSelectFolder(null)}
          className={`flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs transition-colors cursor-pointer ${
            selectedFolderId === null
              ? "bg-coral-500/15 text-coral-700 dark:text-coral-300 font-semibold"
              : "text-ink-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200 hover:bg-black/5 dark:hover:bg-white/5"
          }`}
        >
          <div className="flex items-center gap-2">
            <Library className="w-3.5 h-3.5 text-coral-600 dark:text-coral-400" />
            <span>Tất cả bài báo (Root)</span>
          </div>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-8 text-muted">
            <Loader2 className="w-4 h-4 animate-spin mr-1.5" />
            <span className="text-xs">Đang nạp cây thư mục...</span>
          </div>
        ) : tree.length === 0 ? (
          <div className="text-center py-6 px-2 text-muted text-[11px]">
            <span>Chưa có thư mục nào. Nhấp "+ Mới" để tạo đề tài nghiên cứu đầu tiên.</span>
          </div>
        ) : (
          tree.map((node) => (
            <TreeNode
              key={node.id}
              item={node}
              level={0}
              selectedFolderId={selectedFolderId}
              onSelectFolder={onSelectFolder}
              onDeleteFolder={handleDeleteFolder}
            />
          ))
        )}
      </div>
    </div>
  );
}
