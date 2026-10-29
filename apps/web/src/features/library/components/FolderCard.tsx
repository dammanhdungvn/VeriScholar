import { Folder, MoreVertical, Pencil, Trash2 } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import type { FolderItem } from "../types";

interface FolderCardProps {
  folder: FolderItem;
  paperCount: number;
  onClick: () => void;
  onRename: (folder: FolderItem) => void;
  onDelete: (folder: FolderItem) => void;
}

export function FolderCard({
  folder,
  paperCount,
  onClick,
  onRename,
  onDelete,
}: FolderCardProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    }
    if (menuOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [menuOpen]);

  const formattedDate = folder.updated_at || folder.created_at
    ? new Date(folder.updated_at || folder.created_at).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      })
    : null;

  return (
    <div
      data-testid={`folder-card-${folder.id}`}
      onClick={onClick}
      className="group relative bg-white dark:bg-[#1f1d1a] p-5 rounded-2xl border border-[#e8e4dc] dark:border-[#2a2824] hover:border-[#c15f3e]/50 transition-all cursor-pointer shadow-2xs hover:shadow-xs flex flex-col justify-between h-40"
    >
      {/* Top Header: Folder Icon & Actions Menu */}
      <div className="flex items-start justify-between gap-3">
        <div className="w-10 h-10 rounded-xl bg-[#c15f3e]/10 dark:bg-[#c15f3e]/20 flex items-center justify-center text-[#c15f3e] shrink-0 transition-transform group-hover:scale-105">
          <Folder className="w-5 h-5 fill-[#c15f3e]/20 stroke-[2]" />
        </div>

        {/* Action Menu */}
        <div className="relative" ref={menuRef}>
          <button
            type="button"
            data-testid={`folder-menu-btn-${folder.id}`}
            onClick={(e) => {
              e.stopPropagation();
              setMenuOpen((prev) => !prev);
            }}
            aria-label="Folder actions"
            className="p-1 rounded-lg text-muted hover:text-ink dark:hover:text-zinc-200 hover:bg-black/5 dark:hover:bg-white/5 transition-colors cursor-pointer"
          >
            <MoreVertical className="w-4 h-4" />
          </button>

          {menuOpen && (
            <div
              className="absolute right-0 top-full mt-1 w-36 bg-white dark:bg-[#201e1a] border border-[#e2dcd2] dark:border-[#322f2a] rounded-xl shadow-lg py-1 z-30 animate-in fade-in zoom-in-95 duration-100"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                type="button"
                data-testid={`folder-rename-btn-${folder.id}`}
                onClick={() => {
                  setMenuOpen(false);
                  onRename(folder);
                }}
                className="w-full px-3 py-1.5 text-xs text-left text-ink dark:text-zinc-200 hover:bg-[#f5f2eb] dark:hover:bg-[#2a2722] flex items-center gap-2 cursor-pointer transition-colors"
              >
                <Pencil className="w-3.5 h-3.5 text-muted" />
                <span>Rename</span>
              </button>
              <button
                type="button"
                data-testid={`folder-delete-btn-${folder.id}`}
                onClick={() => {
                  setMenuOpen(false);
                  onDelete(folder);
                }}
                className="w-full px-3 py-1.5 text-xs text-left text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/30 flex items-center gap-2 cursor-pointer transition-colors"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Delete</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Middle: Title */}
      <div className="my-2">
        <h3 className="text-sm font-semibold font-anthropic-serif text-ink dark:text-zinc-100 group-hover:text-[#c15f3e] transition-colors line-clamp-1">
          {folder.name}
        </h3>
        {folder.description && (
          <p className="text-[11px] text-muted dark:text-zinc-400 line-clamp-1 mt-0.5">
            {folder.description}
          </p>
        )}
      </div>

      {/* Bottom Footer: Stats */}
      <div className="flex items-center justify-between text-[11px] text-muted dark:text-zinc-500 font-mono pt-2 border-t border-[#f2ede4] dark:border-[#262420]">
        <span>
          {paperCount} {paperCount === 1 ? "paper" : "papers"}
        </span>
        {formattedDate && <span>{formattedDate}</span>}
      </div>
    </div>
  );
}
