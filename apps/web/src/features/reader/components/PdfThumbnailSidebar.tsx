import { useState, useEffect, useRef, memo } from "react";
import { X, FileText, Bookmark, ListTree, ChevronRight, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import type { PDFDocumentProxy } from "pdfjs-dist";

interface OutlineItem {
  title: string;
  dest: any;
  items?: OutlineItem[];
}

interface PdfThumbnailSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  totalPages: number;
  currentPage: number;
  onSelectPage: (page: number) => void;
  activeCitationPage?: number | null;
  documentTitle?: string;
  pdfDoc?: PDFDocumentProxy | null;
}

const MiniThumbnailCanvas = memo(function MiniThumbnailCanvas({
  pdfDoc,
  pageNum,
  hasCitation,
}: {
  pdfDoc?: PDFDocumentProxy | null;
  pageNum: number;
  hasCitation?: boolean;
}) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [isRendered, setIsRendered] = useState(false);

  useEffect(() => {
    let isCancelled = false;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let renderTask: any = null;

    if (!pdfDoc || !canvasRef.current) return;

    pdfDoc
      .getPage(pageNum)
      .then((page) => {
        if (isCancelled || !canvasRef.current) return;
        const unscaledViewport = page.getViewport({ scale: 1 });
        const targetWidth = 140;
        const scale = targetWidth / unscaledViewport.width;
        const viewport = page.getViewport({ scale });
        const canvas = canvasRef.current;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        canvas.width = Math.floor(viewport.width);
        canvas.height = Math.floor(viewport.height);

        renderTask = page.render({
          canvasContext: ctx,
          viewport,
          canvas,
        });

        return renderTask.promise;
      })
      .then(() => {
        if (!isCancelled) setIsRendered(true);
      })
      .catch(() => {
        // Ignored on cancel or unmount
      });

    return () => {
      isCancelled = true;
      if (renderTask) {
        try {
          renderTask.cancel();
        } catch {
          // ignore
        }
      }
    };
  }, [pdfDoc, pageNum]);

  return (
    <div className="relative w-full aspect-[1/1.414] bg-white dark:bg-[#1a1917] border border-black/10 dark:border-white/10 rounded-xs shadow-2xs overflow-hidden flex items-center justify-center">
      <canvas
        ref={canvasRef}
        className={cn(
          "w-full h-full object-contain pointer-events-none transition-opacity duration-200",
          isRendered ? "opacity-100" : "opacity-0"
        )}
      />

      {/* Wireframe skeleton placeholder while loading or in test environments */}
      {!isRendered && (
        <div className="absolute inset-0 p-2 flex flex-col justify-between bg-zinc-50 dark:bg-[#171614] select-none">
          <div className="space-y-1 opacity-20">
            <div className="h-1 bg-current rounded-full w-2/3" />
            <div className="h-0.5 bg-current rounded-full w-full" />
            <div className="h-0.5 bg-current rounded-full w-4/5" />
          </div>
          <div className="text-[9px] font-mono text-center text-muted font-semibold">
            {pageNum}
          </div>
        </div>
      )}

      {hasCitation && (
        <div className="absolute top-1.5 right-1.5 w-2.5 h-2.5 rounded-full bg-amber-500 shadow-xs ring-2 ring-white dark:ring-zinc-900 animate-pulse" />
      )}
    </div>
  );
});

function PdfOutlineNode({
  item,
  depth = 0,
  onSelect,
}: {
  item: OutlineItem;
  depth?: number;
  onSelect: (dest: any) => void;
}) {
  const [isExpanded, setIsExpanded] = useState(true);
  const hasChildren = item.items && item.items.length > 0;

  return (
    <div className="flex flex-col">
      <div
        className={cn(
          "flex items-center gap-1.5 py-1 px-1.5 rounded-md hover:bg-black/5 dark:hover:bg-white/5 transition-colors cursor-pointer group text-xs text-ink dark:text-zinc-200",
          depth > 0 && "ml-3 text-[11px]"
        )}
        onClick={() => onSelect(item.dest)}
      >
        {hasChildren ? (
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              setIsExpanded(!isExpanded);
            }}
            className="p-0.5 rounded hover:bg-black/10 dark:hover:bg-white/10 text-muted"
          >
            <ChevronRight className={cn("w-3 h-3 transition-transform", isExpanded && "rotate-90")} />
          </button>
        ) : (
          <span className="w-3 shrink-0" />
        )}
        <span className="truncate flex-1 font-serif group-hover:text-primary transition-colors text-left">
          {item.title}
        </span>
      </div>

      {hasChildren && isExpanded && (
        <div className="space-y-0.5 border-l border-hairline dark:border-[#2b2824] ml-2 pl-1">
          {item.items!.map((child, idx) => (
            <PdfOutlineNode
              key={`${child.title}-${idx}`}
              item={child}
              depth={depth + 1}
              onSelect={onSelect}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function PdfThumbnailSidebar({
  isOpen,
  onClose,
  totalPages,
  currentPage,
  onSelectPage,
  activeCitationPage,
  documentTitle,
  pdfDoc,
}: PdfThumbnailSidebarProps) {
  const [viewMode, setViewMode] = useState<"thumbnails" | "outline">("thumbnails");
  const [outline, setOutline] = useState<OutlineItem[] | null>(null);
  const [isLoadingOutline, setIsLoadingOutline] = useState(false);

  useEffect(() => {
    if (!pdfDoc || viewMode !== "outline") return;
    let isCancelled = false;
    setIsLoadingOutline(true);

    pdfDoc
      .getOutline()
      .then((data) => {
        if (!isCancelled) {
          setOutline(data || []);
        }
      })
      .catch((err) => {
        console.warn("Failed to get PDF outline:", err);
        if (!isCancelled) setOutline([]);
      })
      .finally(() => {
        if (!isCancelled) setIsLoadingOutline(false);
      });

    return () => {
      isCancelled = true;
    };
  }, [pdfDoc, viewMode]);

  const handleSelectOutlineDest = async (dest: any) => {
    if (dest === undefined || dest === null) return;
    if (typeof dest === "number") {
      onSelectPage(dest);
      return;
    }
    if (!pdfDoc) return;
    try {
      let explicitDest = dest;
      if (typeof dest === "string") {
        explicitDest = await pdfDoc.getDestination(dest);
      }
      if (Array.isArray(explicitDest) && explicitDest.length > 0) {
        const targetRef = explicitDest[0];
        if (typeof targetRef === "number") {
          onSelectPage(targetRef + 1);
        } else if (targetRef && typeof pdfDoc.getPageIndex === "function") {
          const pageIndex = await pdfDoc.getPageIndex(targetRef);
          onSelectPage(pageIndex + 1);
        }
      }
    } catch (err) {
      console.warn("Could not resolve outline destination:", err);
    }
  };

  if (!isOpen) return null;

  const pages = Array.from({ length: totalPages }, (_, i) => i + 1);

  return (
    <aside
      role="complementary"
      aria-label="Thanh điều hướng thu nhỏ các trang (Thumbnails)"
      className="w-56 h-full border-r border-hairline dark:border-[#2b2824] bg-surface-soft/80 dark:bg-[#161513] backdrop-blur-md flex flex-col shrink-0 select-none z-20 animate-in slide-in-from-left duration-200"
    >
      {/* Header */}
      <div className="h-11 px-3.5 border-b border-hairline dark:border-[#2b2824] flex items-center justify-between">
        <div className="flex items-center gap-2 font-medium text-xs text-ink dark:text-zinc-200 truncate">
          <FileText className="w-3.5 h-3.5 text-primary shrink-0" />
          <span className="truncate font-serif font-bold text-xs" title={documentTitle || `Tài liệu (${totalPages} trang)`}>
            {documentTitle ? `${documentTitle.slice(0, 22)}...` : `Tài liệu (${totalPages} trang)`}
          </span>
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label="Đóng thanh thu nhỏ"
          className="p-1 rounded-md hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink cursor-pointer transition-colors"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Segmented View Mode Tabs: [ Trang ] [ Mục lục ] */}
      <div className="px-3 py-2 border-b border-hairline dark:border-[#2b2824]">
        <div className="grid grid-cols-2 p-0.5 rounded-lg bg-surface-cream dark:bg-[#1f1d1a] text-xs font-medium border border-hairline dark:border-[#2e2a24]" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={viewMode === "thumbnails"}
            onClick={() => setViewMode("thumbnails")}
            className={cn(
              "py-1 px-2 rounded-md transition-all text-center flex items-center justify-center gap-1.5 cursor-pointer text-xs",
              viewMode === "thumbnails"
                ? "bg-white dark:bg-[#2a2722] text-ink dark:text-zinc-100 font-semibold shadow-2xs"
                : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200"
            )}
          >
            <FileText className="w-3 h-3 text-primary" />
            <span>Trang</span>
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={viewMode === "outline"}
            onClick={() => setViewMode("outline")}
            className={cn(
              "py-1 px-2 rounded-md transition-all text-center flex items-center justify-center gap-1.5 cursor-pointer text-xs",
              viewMode === "outline"
                ? "bg-white dark:bg-[#2a2722] text-ink dark:text-zinc-100 font-semibold shadow-2xs"
                : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200"
            )}
          >
            <ListTree className="w-3 h-3 text-primary" />
            <span>Mục lục</span>
          </button>
        </div>
      </div>

      {/* Tab Content: Thumbnails Mode */}
      {viewMode === "thumbnails" && (
        <div className="flex-1 overflow-y-auto p-3 space-y-3 custom-scrollbar">
          {pages.map((pageNum) => {
            const isSelected = pageNum === currentPage;
            const hasCitation = activeCitationPage === pageNum;

            return (
              <button
                key={pageNum}
                type="button"
                onClick={() => onSelectPage(pageNum)}
                className={cn(
                  "w-full flex flex-col items-center p-2 rounded-lg border transition-all text-left group cursor-pointer",
                  isSelected
                    ? "bg-primary/10 border-primary ring-2 ring-primary/30 shadow-xs"
                    : "bg-canvas dark:bg-[#1d1b18] border-hairline dark:border-[#2e2a24] hover:border-primary/40 hover:bg-surface-cream-strong/50"
                )}
              >
                {/* Thumbnail Mini-Canvas Render */}
                <MiniThumbnailCanvas
                  pdfDoc={pdfDoc}
                  pageNum={pageNum}
                  hasCitation={hasCitation}
                />

                {/* Page Number Label */}
                <div className="mt-1.5 flex items-center justify-between w-full px-1 text-[11px] font-mono">
                  <span
                    className={cn(
                      "font-medium transition-colors",
                      isSelected ? "text-primary font-bold" : "text-muted group-hover:text-ink"
                    )}
                  >
                    Trang {pageNum}
                  </span>
                  {hasCitation && (
                    <span className="flex items-center gap-0.5 text-[10px] text-amber-600 dark:text-amber-400 font-sans font-medium">
                      <Bookmark className="w-2.5 h-2.5 fill-current" />
                      <span>Dẫn chứng</span>
                    </span>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      )}

      {/* Tab Content: Outline Mode */}
      {viewMode === "outline" && (
        <div className="flex-1 overflow-y-auto p-3 space-y-1 custom-scrollbar">
          {isLoadingOutline && (
            <div className="p-4 flex items-center justify-center gap-2 text-xs text-muted">
              <Loader2 className="w-4 h-4 animate-spin text-primary" />
              <span>Đang đọc mục lục...</span>
            </div>
          )}

          {!isLoadingOutline && outline && outline.length > 0 && (
            <div className="space-y-1">
              {outline.map((item, idx) => (
                <PdfOutlineNode
                  key={`${item.title}-${idx}`}
                  item={item}
                  onSelect={handleSelectOutlineDest}
                />
              ))}
            </div>
          )}

          {!isLoadingOutline && (!outline || outline.length === 0) && (
            <div className="p-4 text-center text-xs text-muted font-serif">
              Tài liệu này không có mục lục nhúng.
            </div>
          )}
        </div>
      )}
    </aside>
  );
}
