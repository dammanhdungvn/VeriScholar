import { useState, useRef, useEffect } from "react";
import {
  ZoomIn,
  ZoomOut,
  RotateCw,
  ChevronLeft,
  ChevronRight,
  LayoutGrid,
  Maximize2,
  Minimize2,
  SlidersHorizontal,
  Scroll,
  File,
  Columns2,
  ChevronDown,
  Check,
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
  isZenPdf,
  onToggleZenPdf,
  onOpenReferences,
}: ViewportControlsProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState<number>(() => {
    return typeof window !== "undefined" ? window.innerWidth : 1024;
  });
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isReadingModeMenuOpen, setIsReadingModeMenuOpen] = useState(false);

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

  // Close reading mode dropdown on click outside
  useEffect(() => {
    if (!isReadingModeMenuOpen) return;
    const handlePointerDown = (e: PointerEvent) => {
      const target = e.target as HTMLElement | null;
      if (target?.closest?.('[data-testid="reading-mode-dropdown-btn"]')) return;
      if (target?.closest?.('[data-testid="reading-mode-menu-popover"]')) return;
      setIsReadingModeMenuOpen(false);
    };
    const timer = setTimeout(() => {
      window.addEventListener("pointerdown", handlePointerDown);
    }, 10);
    return () => {
      clearTimeout(timer);
      window.removeEventListener("pointerdown", handlePointerDown);
    };
  }, [isReadingModeMenuOpen]);

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

  const readingModeConfig = {
    continuous: { label: "Cuộn", fullLabel: "Cuộn liên tục", icon: Scroll },
    single: { label: "Trang đơn", fullLabel: "Trang đơn", icon: File },
    "two-page": { label: "Hai trang", fullLabel: "Hai trang song song", icon: Columns2 },
  };
  const currentMode = readingModeConfig[activeReadingMode] || readingModeConfig.continuous;
  const ModeIcon = currentMode.icon;

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

      {/* 2. Middle Cluster: Reading Mode Dropdown | - 100% + | Xoay 90° */}
      {!isMobile && (
        <div className="flex items-center gap-1 sm:gap-1.5 shrink-0">
          {/* Reading Mode Single Dropdown Button */}
          <div className="relative shrink-0">
            <button
              type="button"
              data-testid="reading-mode-dropdown-btn"
              onClick={(e) => {
                e.stopPropagation();
                setIsReadingModeMenuOpen((prev) => !prev);
              }}
              aria-label="Chọn chế độ đọc"
              aria-expanded={isReadingModeMenuOpen}
              aria-haspopup="menu"
              className={cn(
                "flex items-center gap-1.5 px-2 py-1 rounded-md border text-xs font-medium transition-colors cursor-pointer shadow-2xs min-h-[28px]",
                isReadingModeMenuOpen
                  ? "bg-primary text-white border-primary font-semibold"
                  : "border-[#e5dfd4] dark:border-[#38332c] text-ink dark:text-zinc-200 hover:bg-surface-soft dark:hover:bg-[#252320]"
              )}
            >
              <ModeIcon className={cn("w-3.5 h-3.5", isReadingModeMenuOpen ? "text-white" : "text-primary dark:text-coral-400")} />
              <span className="font-sans font-medium text-[11px]">{currentMode.label}</span>
              <ChevronDown className={cn("w-3 h-3 transition-transform duration-150 opacity-70", isReadingModeMenuOpen && "rotate-180")} />
            </button>

            {/* Reading Mode Dropdown Popover */}
            {isReadingModeMenuOpen && (
              <div
                role="menu"
                aria-label="Lựa chọn chế độ đọc tài liệu"
                data-testid="reading-mode-menu-popover"
                className="absolute left-0 top-full mt-1.5 z-50 w-52 p-1.5 rounded-xl bg-white dark:bg-[#1c1a17] border border-hairline dark:border-[#38332c] shadow-xl backdrop-blur-md animate-in fade-in zoom-in-95 duration-150 select-none text-ink dark:text-zinc-100"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="px-2 py-1 text-[10px] font-mono uppercase tracking-wider text-muted dark:text-zinc-400 font-semibold">
                  Chế độ đọc
                </div>
                {(["continuous", "single", "two-page"] as const).map((mode) => {
                  const item = readingModeConfig[mode];
                  const Icon = item.icon;
                  const isSelected = activeReadingMode === mode;
                  return (
                    <button
                      key={mode}
                      type="button"
                      role="menuitemradio"
                      aria-checked={isSelected}
                      data-testid={`mode-opt-${mode}`}
                      onClick={() => {
                        setReadingMode(mode);
                        setIsReadingModeMenuOpen(false);
                      }}
                      className={cn(
                        "w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-medium transition-colors cursor-pointer text-left",
                        isSelected
                          ? "bg-primary/10 text-primary dark:bg-primary/20 dark:text-coral-400 font-semibold"
                          : "text-ink dark:text-zinc-200 hover:bg-surface-soft dark:hover:bg-[#282521]"
                      )}
                    >
                      <div className="flex items-center gap-2">
                        <Icon className="w-3.5 h-3.5 text-primary dark:text-coral-400" />
                        <span>{item.fullLabel}</span>
                      </div>
                      {isSelected && <Check className="w-3.5 h-3.5 text-primary dark:text-coral-400" />}
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          <div className="w-[1px] h-4 bg-hairline dark:bg-[#332f29] mx-0.5" />

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

      {/* 3. Right Cluster: [Zen PDF] | [Tùy chọn] */}
      <div className="relative z-30 shrink-0 flex items-center gap-1.5">
        {onToggleZenPdf && (
          <button
            type="button"
            data-testid="zen-pdf-btn"
            onClick={onToggleZenPdf}
            aria-label={isZenPdf ? "Khôi phục chia đôi màn hình" : "Ẩn Chatbot / Chế độ đọc tập trung (Zen PDF)"}
            title={isZenPdf ? "Khôi phục chia đôi màn hình (Esc)" : "Chế độ đọc tập trung (Zen PDF)"}
            className={cn(
              "hidden md:flex items-center gap-1 px-2 sm:px-2.5 py-1.5 rounded-md border text-xs font-sans font-medium transition-colors cursor-pointer shadow-2xs min-h-[32px]",
              isZenPdf
                ? "bg-primary text-white border-primary font-semibold"
                : "border-[#e5dfd4] dark:border-[#38332c] text-ink dark:text-zinc-200 hover:bg-surface-soft dark:hover:bg-[#252320]"
            )}
          >
            {isZenPdf ? (
              <Minimize2 className="w-3.5 h-3.5" />
            ) : (
              <Maximize2 className="w-3.5 h-3.5 text-primary dark:text-coral-400" />
            )}
            <span className="hidden sm:inline font-medium">
              {isZenPdf ? "Thu nhỏ PDF" : "Zen PDF"}
            </span>
          </button>
        )}

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
          isZenPdf={isZenPdf}
          onToggleZenPdf={onToggleZenPdf}
          zoomRatio={zoomRatio}
          onZoomIn={onZoomIn}
          onZoomOut={onZoomOut}
          onResetZoom={onResetZoom}
          onRotate={onRotate}
          showZoomControls={false}
          showReadingModes={!isMobile}
          isMobile={isMobile}
        />
      </div>
    </div>
  );
}
