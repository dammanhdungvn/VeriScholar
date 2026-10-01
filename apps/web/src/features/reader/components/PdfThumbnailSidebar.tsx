import { useState, useEffect, useRef, memo } from "react";
import { X, FileText, Bookmark } from "lucide-react";
import { cn } from "@/lib/utils";
import type { PDFDocumentProxy } from "pdfjs-dist";

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
          <span className="truncate font-serif font-bold text-xs" title={documentTitle || `Thu nhỏ (${totalPages} trang)`}>
            {documentTitle ? `${documentTitle.slice(0, 22)}...` : `Thu nhỏ (${totalPages} trang)`}
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

      {/* Pages List */}
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
    </aside>
  );
}
