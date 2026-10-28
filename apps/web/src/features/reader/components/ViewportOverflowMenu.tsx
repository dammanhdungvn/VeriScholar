import { useRef, useEffect } from "react";
import {
  BookMarked,
  SlidersHorizontal,
  ZoomIn,
  ZoomOut,
  RotateCw,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { ReadingMode } from "../stores/useReaderStore";

export interface ViewportOverflowMenuProps {
  isOpen: boolean;
  onClose: () => void;
  activeReadingMode?: ReadingMode;
  onReadingModeChange?: (mode: ReadingMode) => void;
  onOpenReferences?: () => void;
  onOpenNotes?: () => void;
  isZenPdf?: boolean;
  onToggleZenPdf?: () => void;
  zoomRatio?: number;
  onZoomIn?: () => void;
  onZoomOut?: () => void;
  onResetZoom?: () => void;
  onRotate?: () => void;
  showZoomControls?: boolean;
  showReadingModes?: boolean;
  isMobile?: boolean;
  className?: string;
}

export function ViewportOverflowMenu({
  isOpen,
  onClose,
  activeReadingMode: _activeReadingMode,
  onReadingModeChange: _onReadingModeChange,
  onOpenReferences,
  onOpenNotes,
  isZenPdf: _isZenPdf,
  onToggleZenPdf: _onToggleZenPdf,
  zoomRatio,
  onZoomIn,
  onZoomOut,
  onResetZoom,
  onRotate,
  showZoomControls = false,
  showReadingModes: _showReadingModes = false,
  isMobile: _isMobile,
  className,
}: ViewportOverflowMenuProps) {
  const popoverRef = useRef<HTMLDivElement>(null);

  // Close on Escape or click outside
  useEffect(() => {
    if (!isOpen) return;

    const handlePointerDown = (e: PointerEvent) => {
      const target = e.target as HTMLElement | null;
      if (target?.closest?.('[data-testid="viewport-overflow-menu-btn"]')) {
        return;
      }
      if (popoverRef.current && !popoverRef.current.contains(target as Node)) {
        onClose();
      }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
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
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      ref={popoverRef}
      role="menu"
      aria-label="Tùy chọn đọc và công cụ PDF"
      data-testid="viewport-overflow-popover"
      className={cn(
        "absolute right-0 top-full mt-1.5 z-50 w-72 p-2 rounded-xl bg-white dark:bg-[#1c1a17] border border-hairline dark:border-[#38332c] shadow-xl backdrop-blur-md animate-in fade-in zoom-in-95 duration-150 select-none text-ink dark:text-zinc-100",
        className
      )}
      onClick={(e) => e.stopPropagation()}
    >
      {/* Header */}
      <div className="px-2.5 py-1.5 border-b border-hairline/80 dark:border-[#2b2722] mb-1.5 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <SlidersHorizontal className="w-3.5 h-3.5 text-primary dark:text-primary-light" />
          <span className="text-xs font-serif font-semibold text-ink dark:text-zinc-100">
            Tùy chọn
          </span>
        </div>
        <span className="text-[10px] font-mono text-muted dark:text-zinc-400 bg-surface-soft dark:bg-[#282521] px-1.5 py-0.5 rounded border border-hairline/60 dark:border-[#332f2a]">
          Esc
        </span>
      </div>

      {/* 0. Zoom & Rotation Controls (When mobile/compact hides them from top bar) */}
      {showZoomControls && onZoomIn && onZoomOut && onResetZoom && (
        <div className="mb-2">
          <div className="px-2 py-1 text-[10px] font-mono uppercase tracking-wider text-muted dark:text-zinc-400 font-semibold flex items-center justify-between">
            <span>Thu phóng & Xoay</span>
            <span className="font-mono text-ink dark:text-zinc-200">
              {Math.round((zoomRatio || 1) * 100)}%
            </span>
          </div>
          <div className="grid grid-cols-4 gap-1 p-1 rounded-lg bg-surface-soft/60 dark:bg-[#25221e]/60 border border-hairline/60">
            <button
              type="button"
              onClick={onZoomOut}
              disabled={(zoomRatio || 1) <= 0.5}
              aria-label="Thu nhỏ"
              title="Thu nhỏ"
              className="flex items-center justify-center h-8 rounded bg-white dark:bg-[#1a1917] border border-hairline/80 dark:border-[#38332c] text-ink dark:text-zinc-200 hover:text-primary transition-colors disabled:opacity-30 cursor-pointer shadow-2xs"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={onResetZoom}
              aria-label="Đặt lại kích thước 100%"
              title="Đặt lại 100%"
              className="flex items-center justify-center h-8 rounded bg-white dark:bg-[#1a1917] border border-hairline/80 dark:border-[#38332c] text-xs font-mono font-medium text-ink dark:text-zinc-200 hover:text-primary transition-colors cursor-pointer shadow-2xs"
            >
              100%
            </button>
            <button
              type="button"
              onClick={onZoomIn}
              disabled={(zoomRatio || 1) >= 3.0}
              aria-label="Phóng to"
              title="Phóng to"
              className="flex items-center justify-center h-8 rounded bg-white dark:bg-[#1a1917] border border-hairline/80 dark:border-[#38332c] text-ink dark:text-zinc-200 hover:text-primary transition-colors disabled:opacity-30 cursor-pointer shadow-2xs"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            {onRotate && (
              <button
                type="button"
                onClick={onRotate}
                aria-label="Xoay 90 độ"
                title="Xoay 90 độ"
                className="flex items-center justify-center h-8 rounded bg-white dark:bg-[#1a1917] border border-hairline/80 dark:border-[#38332c] text-ink dark:text-zinc-200 hover:text-primary transition-colors cursor-pointer shadow-2xs"
              >
                <RotateCw className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
          <div className="h-[1px] bg-hairline dark:bg-[#2b2722] my-1.5" />
        </div>
      )}

      {/* 2. Công cụ học thuật & Không gian (Academic Tools & Focus) */}
      <div className="space-y-0.5">
        <div className="px-2 py-1 text-[10px] font-mono uppercase tracking-wider text-muted dark:text-zinc-400 font-semibold">
          Công cụ
        </div>

        {onOpenNotes && (
          <button
            type="button"
            role="menuitem"
            data-testid="overflow-open-notes-btn"
            onClick={() => {
              onClose();
              onOpenNotes();
            }}
            className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs font-medium text-ink dark:text-zinc-200 hover:bg-surface-soft dark:hover:bg-[#282521] hover:text-primary transition-colors cursor-pointer text-left"
          >
            <BookMarked className="w-3.5 h-3.5 text-primary shrink-0" />
            <span className="flex-1 font-medium">Sổ ghi chú</span>
          </button>
        )}

        {onOpenReferences && (
          <button
            type="button"
            role="menuitem"
            data-testid="overflow-open-references-btn"
            onClick={() => {
              onClose();
              onOpenReferences();
            }}
            className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs font-medium text-ink dark:text-zinc-200 hover:bg-surface-soft dark:hover:bg-[#282521] hover:text-primary transition-colors cursor-pointer text-left"
          >
            <BookMarked className="w-3.5 h-3.5 text-primary shrink-0" />
            <span className="flex-1 font-medium">Trích xuất Tài liệu Tham khảo</span>
          </button>
        )}
      </div>
    </div>
  );
}
