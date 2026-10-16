import {
  ZoomIn,
  ZoomOut,
  RotateCw,
  ChevronLeft,
  ChevronRight,
  Download,
  LayoutGrid,
  Scroll,
  File,
  Columns2,
  Maximize2,
  Minimize2,
  BookMarked,
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
  useReaderStore,
  type ReadingMode,
} from "../stores/useReaderStore";

interface ViewportControlsProps {
  currentPage: number;
  totalPages: number;
  zoomRatio: number;
  onPageChange: (page: number) => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onResetZoom: () => void;
  onRotate: () => void;
  onExportPdf?: () => void;
  isExportingPdf?: boolean;
  readingMode?: ReadingMode;
  onReadingModeChange?: (mode: ReadingMode) => void;
  isThumbnailsOpen?: boolean;
  onToggleThumbnails?: () => void;
  isZenPdf?: boolean;
  onToggleZenPdf?: () => void;
  onOpenReferences?: () => void;
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
  onExportPdf,
  isExportingPdf,
  readingMode: propReadingMode,
  onReadingModeChange: propOnReadingModeChange,
  isThumbnailsOpen: propIsThumbnailsOpen,
  onToggleThumbnails: propOnToggleThumbnails,
  isZenPdf,
  onToggleZenPdf,
  onOpenReferences,
}: ViewportControlsProps) {
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
      role="toolbar"
      aria-label="Thanh điều khiển khung nhìn tài liệu"
      className="h-11 px-3.5 border-b border-hairline/80 dark:border-[#282622] bg-[#faf8f5]/90 dark:bg-[#161513]/90 backdrop-blur-md flex items-center justify-between gap-2 select-none text-xs overflow-x-auto scrollbar-none"
    >
      {/* 1. Left Cluster: Thumbnails, Page Navigation */}
      <div className="flex items-center gap-1 shrink-0">
        <button
          type="button"
          onClick={toggleThumbnails}
          aria-label="Xem trước trang (Thumbnails)"
          title="Xem trước trang (Thumbnails)"
          className={cn(
            "p-1.5 rounded transition-colors cursor-pointer",
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
          className="p-1 rounded hover:bg-surface-soft dark:hover:bg-[#252320] disabled:opacity-30 disabled:pointer-events-none transition-colors cursor-pointer"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-1 font-mono text-muted dark:text-zinc-400 px-1">
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
          className="p-1 rounded hover:bg-surface-soft dark:hover:bg-[#252320] disabled:opacity-30 disabled:pointer-events-none transition-colors cursor-pointer"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* 2. Middle Cluster: Zoom & Smart Fit & Rotation */}
      <div className="flex items-center gap-1 shrink-0">
        <button
          type="button"
          onClick={onZoomOut}
          disabled={zoomRatio <= 0.5}
          aria-label="Thu nhỏ"
          title="Thu nhỏ (Ctrl -)"
          className="p-1 rounded hover:bg-surface-soft dark:hover:bg-[#252320] disabled:opacity-30 transition-colors cursor-pointer"
        >
          <ZoomOut className="w-3.5 h-3.5" />
        </button>

        <button
          type="button"
          onClick={onResetZoom}
          aria-label="Đặt lại kích thước 100%"
          title="Đặt lại 100%"
          className="px-1.5 py-0.5 rounded font-mono font-medium hover:bg-surface-soft dark:hover:bg-[#252320] transition-colors cursor-pointer"
        >
          {zoomPercent}%
        </button>

        <button
          type="button"
          onClick={onZoomIn}
          disabled={zoomRatio >= 3.0}
          aria-label="Phóng to"
          title="Phóng to (Ctrl +)"
          className="p-1 rounded hover:bg-surface-soft dark:hover:bg-[#252320] disabled:opacity-30 transition-colors cursor-pointer"
        >
          <ZoomIn className="w-3.5 h-3.5" />
        </button>

        <div className="w-[1px] h-4 bg-hairline dark:bg-[#332f29] mx-0.5" />

        <button
          type="button"
          onClick={onRotate}
          aria-label="Xoay trang 90 độ"
          title="Xoay trang 90 độ"
          className="p-1 rounded hover:bg-surface-soft dark:hover:bg-[#252320] transition-colors text-muted hover:text-ink cursor-pointer"
        >
          <RotateCw className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* 3. Reading Modes Segmented Control & Document Export */}
      <div className="flex items-center gap-2 shrink-0 border-l border-hairline dark:border-[#332f29] pl-2">
        <div
          role="radiogroup"
          aria-label="Chế độ xem tài liệu"
          className="inline-flex items-center p-0.5 rounded-lg bg-[#f0ece3] dark:bg-[#23211e] border border-[#e5dfd4] dark:border-[#332f2a]"
        >
          {/* Continuous Scroll */}
          <button
            type="button"
            role="radio"
            aria-checked={activeReadingMode === "continuous"}
            onClick={() => setReadingMode("continuous")}
            title="Chế độ cuộn liên tục (Continuous Scroll)"
            aria-label="Cuộn liên tục"
            className={cn(
              "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium transition-all cursor-pointer",
              activeReadingMode === "continuous"
                ? "bg-white dark:bg-[#1a1917] text-primary shadow-xs font-semibold"
                : "text-muted dark:text-zinc-400 hover:text-ink dark:hover:text-zinc-200"
            )}
          >
            <Scroll className="w-3.5 h-3.5" />
            <span className="hidden xl:inline">Cuộn</span>
          </button>

          {/* Single Page */}
          <button
            type="button"
            role="radio"
            aria-checked={activeReadingMode === "single"}
            onClick={() => setReadingMode("single")}
            title="Chế độ từng trang (Single Page)"
            aria-label="Trang đơn"
            className={cn(
              "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium transition-all cursor-pointer",
              activeReadingMode === "single"
                ? "bg-white dark:bg-[#1a1917] text-primary shadow-xs font-semibold"
                : "text-muted dark:text-zinc-400 hover:text-ink dark:hover:text-zinc-200"
            )}
          >
            <File className="w-3.5 h-3.5" />
            <span className="hidden xl:inline">Trang đơn</span>
          </button>

          {/* Two-Page Spread */}
          <button
            type="button"
            role="radio"
            aria-checked={activeReadingMode === "two-page"}
            onClick={() => setReadingMode("two-page")}
            title="Chế độ 2 trang song song (Two-Page Spread)"
            aria-label="Hai trang"
            className={cn(
              "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium transition-all cursor-pointer",
              activeReadingMode === "two-page"
                ? "bg-white dark:bg-[#1a1917] text-primary shadow-xs font-semibold"
                : "text-muted dark:text-zinc-400 hover:text-ink dark:hover:text-zinc-200"
            )}
          >
            <Columns2 className="w-3.5 h-3.5" />
            <span className="hidden xl:inline">Hai trang</span>
          </button>
        </div>

        {onOpenReferences && (
          <>
            <div className="w-[1px] h-4 bg-hairline dark:bg-[#332f29]" />
            <button
              type="button"
              data-testid="open-references-btn"
              onClick={onOpenReferences}
              aria-label="Trích xuất Tài liệu Tham khảo"
              title="Trích xuất & Mở rộng Tài liệu Tham khảo (Module 3)"
              className="flex items-center gap-1 px-2.5 py-1 rounded-md border border-[#e5dfd4] dark:border-[#38332c] text-muted hover:text-ink hover:bg-white dark:hover:bg-[#252320] transition-colors font-sans cursor-pointer text-[11px] shadow-2xs"
            >
              <BookMarked className="w-3.5 h-3.5 text-primary" />
              <span className="hidden sm:inline font-medium">Trích xuất Tài liệu Tham khảo</span>
            </button>
          </>
        )}

        {onExportPdf && (
          <>
            <div className="w-[1px] h-4 bg-hairline dark:bg-[#332f29]" />
            <button
              type="button"
              onClick={onExportPdf}
              disabled={isExportingPdf}
              aria-label="Xuất PDF kèm ghi chú"
              title="Tải xuống tệp PDF có Native ISO Highlights & Bounding Boxes"
              className="flex items-center gap-1 px-2.5 py-1 rounded-md border border-[#e5dfd4] dark:border-[#38332c] text-muted hover:text-ink hover:bg-white dark:hover:bg-[#252320] transition-colors font-sans cursor-pointer disabled:opacity-50 text-[11px] shadow-2xs"
            >
              <Download className="w-3.5 h-3.5 text-primary" />
              <span className="hidden sm:inline font-medium">
                {isExportingPdf ? "Đang xuất..." : "Xuất PDF"}
              </span>
            </button>
          </>
        )}

        {onToggleZenPdf && (
          <>
            <div className="w-[1px] h-4 bg-hairline dark:bg-[#332f29]" />
            <button
              type="button"
              data-testid="zen-pdf-btn"
              onClick={onToggleZenPdf}
              aria-label={isZenPdf ? "Khôi phục chia đôi màn hình" : "Ẩn Chatbot / Chế độ đọc tập trung (Zen PDF)"}
              title={isZenPdf ? "Khôi phục chia đôi màn hình (Esc)" : "Ẩn Chatbot / Chế độ đọc tập trung (Zen PDF)"}
              className={cn(
                "flex items-center gap-1 px-2.5 py-1 rounded-md border text-[11px] transition-colors font-sans cursor-pointer shadow-2xs",
                isZenPdf
                  ? "bg-primary text-white border-primary font-semibold"
                  : "border-[#e5dfd4] dark:border-[#38332c] text-muted hover:text-ink hover:bg-white dark:hover:bg-[#252320]"
              )}
            >
              {isZenPdf ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5 text-primary" />}
              <span className="hidden sm:inline">
                {isZenPdf ? "Thu nhỏ PDF" : "Zen PDF"}
              </span>
            </button>
          </>
        )}
      </div>
    </div>
  );
}
