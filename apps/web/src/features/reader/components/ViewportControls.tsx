import { useState, useRef, useEffect } from "react";
import {
  ZoomIn,
  ZoomOut,
  RotateCw,
  ChevronLeft,
  ChevronRight,
  LayoutGrid,
  SlidersHorizontal,
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
  useReaderStore,
  type ReadingMode,
} from "../stores/useReaderStore";
import { ViewportOverflowMenu } from "./ViewportOverflowMenu";

interface ViewportControlsProps {
  currentPage: number;
  totalPages: number;
  zoomRatio: number;
  onPageChange: (page: number) => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onResetZoom: () => void;
  onRotate: () => void;
  readingMode?: ReadingMode;
  onReadingModeChange?: (mode: ReadingMode) => void;
  isThumbnailsOpen?: boolean;
  onToggleThumbnails?: () => void;
  isZenPdf?: boolean;
  onToggleZenPdf?: () => void;
  onOpenReferences?: () => void;
  onOpenNotes?: () => void;
}

export function ViewportControls({
  currentPage,
  totalPages,
  zoomRatio,
  onPageChange,
  onZoomIn,
  onZoomOut,
  onResetZoom,
  onRotate,
  readingMode: propReadingMode,
  onReadingModeChange: propOnReadingModeChange,
  isThumbnailsOpen: propIsThumbnailsOpen,
  onToggleThumbnails: propOnToggleThumbnails,
  isZenPdf: _isZenPdf,
  onToggleZenPdf: _onToggleZenPdf,
  onOpenReferences,
  onOpenNotes,
}: ViewportControlsProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState<number>(() => {
    return typeof window !== "undefined" ? window.innerWidth : 1024;
  });
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    if (el.clientWidth > 0) {
      setContainerWidth(el.clientWidth);
    }

    if (typeof ResizeObserver === "undefined") {
      return;
    }

    const ro = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (entry && entry.contentRect.width > 0) {
        setContainerWidth(entry.contentRect.width);
      }
    });

    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // Mobile threshold: < 480px moves zoom & rotate into overflow menu
  const isMobile = containerWidth < 480;

  // Store fallback hooks
  const storeReadingMode = useReaderStore((s) => s.readingMode);
  const storeSetReadingMode = useReaderStore((s) => s.setReadingMode);
  const storeIsThumbnailsOpen = useReaderStore((s) => s.isThumbnailsOpen);
  const storeToggleThumbnails = useReaderStore((s) => s.toggleThumbnails);

  const activeReadingMode = propReadingMode ?? storeReadingMode;
  const setReadingMode = propOnReadingModeChange ?? storeSetReadingMode;

  const activeIsThumbnailsOpen = propIsThumbnailsOpen ?? storeIsThumbnailsOpen;
  const toggleThumbnails = propOnToggleThumbnails ?? storeToggleThumbnails;

  const zoomPercent = Math.round(zoomRatio * 100);

  return (
    <div
      ref={containerRef}
      role="toolbar"
      aria-label="Thanh điều khiển khung nhìn tài liệu"
      className="relative z-10 h-11 px-2.5 sm:px-3.5 border-b border-hairline/80 dark:border-[#282622] bg-[#faf8f5]/90 dark:bg-[#161513]/90 backdrop-blur-md flex items-center justify-between gap-1 sm:gap-2 select-none text-xs overflow-visible"
    >
      {/* 1. Left Cluster: Thumbnails Grid | Page Navigation */}
      <div className="flex items-center gap-0.5 sm:gap-1 shrink-0">
        <button
          type="button"
          onClick={toggleThumbnails}
          aria-label="Xem trước trang (Thumbnails)"
          title="Xem trước trang (Thumbnails)"
          className={cn(
            "p-1.5 min-w-[32px] min-h-[32px] flex items-center justify-center rounded-md transition-colors cursor-pointer",
            activeIsThumbnailsOpen
              ? "bg-primary text-white"
              : "text-muted hover:text-ink hover:bg-surface-soft dark:hover:bg-[#252320]"
          )}
        >
          <LayoutGrid className="w-3.5 h-3.5" />
        </button>

        <div className="w-[1px] h-4 bg-hairline dark:bg-[#332f29] mx-0.5" />

        <button
          type="button"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage <= 1}
          aria-label="Trang trước"
          title="Trang trước (Page Up)"
          className="p-1.5 min-w-[32px] min-h-[32px] flex items-center justify-center rounded-md hover:bg-surface-soft dark:hover:bg-[#252320] disabled:opacity-30 disabled:pointer-events-none transition-colors cursor-pointer text-ink dark:text-zinc-200"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-1 font-mono text-muted dark:text-zinc-400 px-1 text-xs">
          <span className="font-semibold text-ink dark:text-zinc-100">{currentPage}</span>
          <span>/</span>
          <span>{totalPages || 1}</span>
        </div>

        <button
          type="button"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage >= totalPages}
          aria-label="Trang tiếp theo"
          title="Trang tiếp theo (Page Down)"
          className="p-1.5 min-w-[32px] min-h-[32px] flex items-center justify-center rounded-md hover:bg-surface-soft dark:hover:bg-[#252320] disabled:opacity-30 disabled:pointer-events-none transition-colors cursor-pointer text-ink dark:text-zinc-200"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* 2. Middle Cluster: - 100% + | Xoay 90° */}
      {!isMobile && (
        <div className="flex items-center gap-1 sm:gap-1.5 shrink-0">
          <button
            type="button"
            onClick={onZoomOut}
            disabled={zoomRatio <= 0.5}
            aria-label="Thu nhỏ"
            title="Thu nhỏ (Ctrl -)"
            className="p-1.5 min-w-[28px] min-h-[28px] flex items-center justify-center rounded-md hover:bg-surface-soft dark:hover:bg-[#252320] disabled:opacity-30 transition-colors cursor-pointer text-ink dark:text-zinc-200"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>

          <button
            type="button"
            onClick={onResetZoom}
            aria-label="Đặt lại kích thước 100%"
            title="Đặt lại 100%"
            className="px-1.5 py-0.5 rounded-md font-mono font-medium hover:bg-surface-soft dark:hover:bg-[#252320] transition-colors cursor-pointer text-xs text-ink dark:text-zinc-200"
          >
            {zoomPercent}%
          </button>

          <button
            type="button"
            onClick={onZoomIn}
            disabled={zoomRatio >= 3.0}
            aria-label="Phóng to"
            title="Phóng to (Ctrl +)"
            className="p-1.5 min-w-[28px] min-h-[28px] flex items-center justify-center rounded-md hover:bg-surface-soft dark:hover:bg-[#252320] disabled:opacity-30 transition-colors cursor-pointer text-ink dark:text-zinc-200"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>

          <div className="w-[1px] h-4 bg-hairline dark:bg-[#332f29] mx-0.5" />

          <button
            type="button"
            onClick={onRotate}
            aria-label="Xoay trang 90 độ"
            title="Xoay trang 90 độ"
            className="p-1.5 min-w-[28px] min-h-[28px] flex items-center justify-center rounded-md hover:bg-surface-soft dark:hover:bg-[#252320] transition-colors text-muted hover:text-ink cursor-pointer"
          >
            <RotateCw className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* 3. Right Cluster: [Tùy chọn] */}
      <div className="relative z-30 shrink-0 flex items-center gap-1.5">
        <button
          type="button"
          data-testid="viewport-overflow-menu-btn"
          onClick={(e) => {
            e.stopPropagation();
            setIsMenuOpen((prev) => !prev);
          }}
          aria-label="Tùy chọn đọc và công cụ"
          aria-expanded={isMenuOpen}
          aria-haspopup="menu"
          className={cn(
            "flex items-center gap-1.5 px-2 sm:px-2.5 py-1.5 rounded-md border text-xs font-medium transition-colors cursor-pointer shadow-2xs min-h-[32px]",
            isMenuOpen
              ? "bg-primary text-white border-primary font-semibold"
              : "border-[#e5dfd4] dark:border-[#38332c] text-ink dark:text-zinc-200 hover:bg-surface-soft dark:hover:bg-[#252320]"
          )}
        >
          <SlidersHorizontal
            className={cn(
              "w-3.5 h-3.5",
              isMenuOpen ? "text-white" : "text-primary dark:text-coral-400"
            )}
          />
          <span className="hidden sm:inline font-sans font-medium">Tùy chọn</span>
        </button>

        <ViewportOverflowMenu
          isOpen={isMenuOpen}
          onClose={() => setIsMenuOpen(false)}
          activeReadingMode={activeReadingMode}
          onReadingModeChange={setReadingMode}
          onOpenReferences={onOpenReferences}
          onOpenNotes={onOpenNotes}
          isZenPdf={false}
          zoomRatio={zoomRatio}
          onZoomIn={onZoomIn}
          onZoomOut={onZoomOut}
          onResetZoom={onResetZoom}
          onRotate={onRotate}
          showZoomControls={false}
          showReadingModes={false}
          isMobile={isMobile}
        />
      </div>
    </div>
  );
}
