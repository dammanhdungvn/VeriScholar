import { useState, useRef, useEffect } from "react";
import { MoreHorizontal, Archive, Settings, Sun, Moon } from "lucide-react";
import { cn } from "@/lib/utils";

interface WorkspaceToolsMenuProps {
  onExport: () => void;
  onOpenSettings: () => void;
  isDark: boolean;
  onToggleTheme: () => void;
}

export function WorkspaceToolsMenu({
  onExport,
  onOpenSettings,
  isDark,
  onToggleTheme,
}: WorkspaceToolsMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;

    const handlePointerDown = (e: PointerEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsOpen(false);
      }
    };

    const timer = window.setTimeout(() => {
      window.addEventListener("pointerdown", handlePointerDown);
    }, 10);
    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.clearTimeout(timer);
      window.removeEventListener("pointerdown", handlePointerDown);
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen]);

  return (
    <div ref={menuRef} className="relative inline-block">
      <button
        type="button"
        data-testid="workspace-tools-menu-btn"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-label="Công cụ bổ sung"
        aria-expanded={isOpen}
        aria-haspopup="menu"
        title="Công cụ bổ sung (Xuất ZIP, Cài đặt, Giao diện)"
        className={cn(
          "inline-flex items-center justify-center w-7 h-7 rounded-lg border text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 transition-colors cursor-pointer shadow-2xs",
          isOpen
            ? "bg-primary text-white border-primary hover:bg-primary/90"
            : "border-[#e5dfd4] dark:border-[#38332c] bg-white/80 dark:bg-[#252320] hover:bg-[#f5f1ea] dark:hover:bg-[#2e2b26]"
        )}
      >
        <MoreHorizontal className="w-3.5 h-3.5" />
      </button>

      {isOpen && (
        <div
          role="menu"
          aria-label="Tùy chọn công cụ phiên làm việc"
          data-testid="workspace-tools-popover"
          className="absolute right-0 top-full mt-1.5 z-50 w-52 p-1.5 rounded-xl bg-white dark:bg-[#1c1a17] border border-hairline dark:border-[#38332c] shadow-xl backdrop-blur-md animate-in fade-in zoom-in-95 duration-150 select-none text-ink dark:text-zinc-100"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="space-y-0.5">
            <button
              type="button"
              role="menuitem"
              onClick={() => {
                setIsOpen(false);
                onExport();
              }}
              className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs font-medium text-ink dark:text-zinc-200 hover:bg-surface-soft dark:hover:bg-[#282521] hover:text-primary transition-colors cursor-pointer text-left"
            >
              <Archive className="w-3.5 h-3.5 text-primary shrink-0" />
              <span>Xuất ZIP</span>
            </button>

            <button
              type="button"
              role="menuitem"
              onClick={() => {
                setIsOpen(false);
                onOpenSettings();
              }}
              className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs font-medium text-ink dark:text-zinc-200 hover:bg-surface-soft dark:hover:bg-[#282521] hover:text-primary transition-colors cursor-pointer text-left"
            >
              <Settings className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
              <span>Cài đặt</span>
            </button>

            <button
              type="button"
              role="menuitem"
              onClick={() => {
                setIsOpen(false);
                onToggleTheme();
              }}
              className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs font-medium text-ink dark:text-zinc-200 hover:bg-surface-soft dark:hover:bg-[#282521] hover:text-primary transition-colors cursor-pointer text-left"
            >
              {isDark ? (
                <Sun className="w-3.5 h-3.5 text-amber-400 shrink-0" />
              ) : (
                <Moon className="w-3.5 h-3.5 text-zinc-600 shrink-0" />
              )}
              <span>{isDark ? "Giao diện sáng" : "Giao diện tối"}</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
