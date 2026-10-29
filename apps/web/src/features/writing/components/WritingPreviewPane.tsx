import { useState, useEffect, useRef } from "react";
import type { PDFDocumentProxy } from "pdfjs-dist";
import {
  ZoomIn,
  ZoomOut,
  RefreshCw,
  AlertCircle,
  Download,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  Sparkles,
  Play,
} from "lucide-react";
import { useWritingStore } from "../stores/useWritingStore";
import { draftsApi } from "../api/draftsApi";
import { getCachedPdfDocument } from "@/features/reader/lib/pdfRenderQueue";
import { pdfjsLib } from "@/features/reader/lib/pdfjs-init";
import { cn } from "@/lib/utils";

interface WritingPreviewPaneProps {
  onSelectionAddToChat?: (selectedText: string) => void;
  onRecompile?: () => void;
  onRecompileClearCache?: () => void;
  onDownloadPdf?: () => void;
  onDoAnything?: () => void;
  onNavigateToLine?: (line: number) => void;
  showDoAnything?: boolean;
}

interface PaperPageCanvasProps {
  pdfDoc: PDFDocumentProxy;
  pageNumber: number;
  zoomLevel: number;
  containerWidth?: number;
  onInView?: (pageNum: number) => void;
  onDoublePageClick?: (pageNumber: number, x: number, y: number) => void;
}

function PaperPageCanvas({
  pdfDoc,
  pageNumber,
  zoomLevel,
  containerWidth,
  onInView,
  onDoublePageClick,
}: PaperPageCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [dimensions, setDimensions] = useState<{ width: number; height: number } | null>(null);
  const { activeHighlightBox } = useWritingStore();

  const scaleRatio = dimensions ? dimensions.width / 595.32 : 1;

  const handleDoubleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!onDoublePageClick) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickY = e.clientY - rect.top;
    const r = rect.width > 0 ? rect.width / 595.32 : 1;
    const ptX = clickX / r;
    const ptY = clickY / r;
    onDoublePageClick(pageNumber, ptX, ptY);
  };

  // Intersection observer to track current visible page
  useEffect(() => {
    const el = containerRef.current;
    if (!el || !onInView) return;

    if (typeof IntersectionObserver === "undefined") return;

    const observer = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        if (entry.isIntersecting && entry.intersectionRatio > 0.4) {
          onInView(pageNumber);
        }
      },
      { threshold: [0.4] }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [pageNumber, onInView]);

  // Render PDF page to HTML5 canvas with dynamic autofit scaling
  useEffect(() => {
    let isCancelled = false;
    let renderTask: ReturnType<typeof page.render> | null = null;
    let page: any = null;

    async function renderPage() {
      try {
        page = await pdfDoc.getPage(pageNumber);
        if (isCancelled) return;

        // Get unscaled page size (standard A4 is 595.32 x 841.92 pt)
        const unscaledViewport = page.getViewport({ scale: 1.0 });
        const standardWidth = unscaledViewport.width || 595.32;

        // Calculate dynamic Autofit baseScale:
        // On mobile (< 640px), 4px padding ensures full-screen edge-to-edge without horizontal overflow
        // On desktop (>= 640px), 24px padding and capped to 880px for optimal reading
        let baseScale = 1.0;
        if (containerWidth && containerWidth > 0) {
          const padding = containerWidth < 640 ? 4 : 24;
          const availableWidth = Math.max(220, containerWidth - padding);
          const targetWidth = containerWidth >= 640 ? Math.min(availableWidth, 880) : availableWidth;
          baseScale = targetWidth / standardWidth;
        } else if (typeof window !== "undefined") {
          const winW = window.innerWidth;
          const isMobile = winW < 640;
          const available = isMobile ? winW - 4 : Math.min(winW * 0.5 - 24, 880);
          baseScale = Math.max(0.4, available / standardWidth);
        }

        const scale = baseScale * (zoomLevel / 100);
        const viewport = page.getViewport({ scale });
        setDimensions({ width: viewport.width, height: viewport.height });

        const canvas = canvasRef.current;
        if (!canvas) return;

        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = Math.floor(viewport.width * dpr);
        canvas.height = Math.floor(viewport.height * dpr);
        canvas.style.width = `${viewport.width}px`;
        canvas.style.height = `${viewport.height}px`;

        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.scale(dpr, dpr);

        renderTask = page.render({
          canvasContext: ctx,
          viewport: viewport,
        });
        await renderTask.promise;
      } catch (err: unknown) {
        if ((err as { name?: string })?.name !== "RenderingCancelledException") {
          // Handled cancellation cleanly
        }
      }
    }

    renderPage();

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
  }, [pdfDoc, pageNumber, zoomLevel, containerWidth]);

  return (
    <div
      ref={containerRef}
      data-testid={`preview-page-${pageNumber}`}
      onDoubleClick={handleDoubleClick}
      className="relative bg-white shadow-[0_2px_8px_rgba(0,0,0,0.16)] border border-[#ded8cc] dark:border-[#38332c] rounded-xs select-text overflow-hidden transition-all duration-150 cursor-pointer"
      style={{
        width: dimensions ? `${dimensions.width}px` : "auto",
        height: dimensions ? `${dimensions.height}px` : "auto",
        maxWidth: zoomLevel <= 100 ? "100%" : undefined,
        minWidth: dimensions ? undefined : "220px",
        minHeight: dimensions ? undefined : "320px",
      }}
    >
      <canvas ref={canvasRef} className="block max-w-full h-auto" />
      {activeHighlightBox && activeHighlightBox.page === pageNumber && (
        <div
          data-testid="synctex-highlight-box"
          className="absolute bg-yellow-400/40 border-2 border-yellow-500 rounded pointer-events-none transition-all z-10"
          style={{
            left: `${(activeHighlightBox.x || 0) * scaleRatio}px`,
            top: `${(activeHighlightBox.y || 0) * scaleRatio}px`,
            width: `${Math.max(20, (activeHighlightBox.width || 100) * scaleRatio)}px`,
            height: `${Math.max(12, (activeHighlightBox.height || 16) * scaleRatio)}px`,
          }}
        />
      )}
    </div>
  );
}

export function WritingPreviewPane({
  onSelectionAddToChat: _onSelectionAddToChat,
  onRecompile,
  onRecompileClearCache,
  onDownloadPdf,
  onDoAnything,
  onNavigateToLine,
  showDoAnything = true,
}: WritingPreviewPaneProps) {
  const {
    activeDraftId,
    previewPdfBlobUrl,
    setPreviewPdfBlobUrl,
    isCompiling,
    setCompiling,
    setCompileResult,
    setWorkspaceMode,
    setAssistantPrompt,
    activeHighlightBox,
    setActiveFile,
  } = useWritingStore();

  const [zoomLevel, setZoomLevel] = useState(100);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(3);
  const [pdfDoc, setPdfDoc] = useState<PDFDocumentProxy | null>(null);
  const [pdfJsError, setPdfJsError] = useState(false);
  const [isRecompileMenuOpen, setIsRecompileMenuOpen] = useState(false);
  const recompileMenuRef = useRef<HTMLDivElement | null>(null);

  // Close recompile dropdown on click outside
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (recompileMenuRef.current && !recompileMenuRef.current.contains(e.target as Node)) {
        setIsRecompileMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const pageRefs = useRef<Record<number, HTMLDivElement | null>>({});
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState<number>(() => {
    if (typeof window !== "undefined") {
      return window.innerWidth < 768 ? window.innerWidth : Math.round(window.innerWidth * 0.5);
    }
    return 595.32;
  });

  // Automatically scroll to highlight box page if SyncTeX forward triggered
  useEffect(() => {
    if (activeHighlightBox?.page) {
      handlePageChange(activeHighlightBox.page);
    }
  }, [activeHighlightBox]);

  const handleClearCacheRecompile = async () => {
    if (!activeDraftId) return;
    if (onRecompileClearCache) {
      onRecompileClearCache();
      return;
    }
    try {
      setCompiling(true);
      const res = await draftsApi.recompileClearCache(activeDraftId);
      setCompileResult(res);
      if (res.success) {
        const blob = await draftsApi.getPreviewPdfBlob(activeDraftId);
        const url = URL.createObjectURL(blob);
        setPreviewPdfBlobUrl(url);
      }
    } catch (err) {
      console.error("Recompile clear cache error:", err);
    } finally {
      setCompiling(false);
    }
  };

  const handleInverseSearch = async (pageNum: number, x: number, y: number) => {
    if (!activeDraftId) return;
    try {
      const loc = await draftsApi.synctexInverse(activeDraftId, pageNum, x, y);
      if (loc?.file && (loc.file === "main.tex" || loc.file === "references.bib")) {
        setActiveFile(loc.file as "main.tex" | "references.bib");
      }
      if (loc?.line && onNavigateToLine) {
        onNavigateToLine(loc.line);
      }
    } catch (err) {
      console.error("Inverse SyncTeX failed:", err);
    }
  };

  // Track preview container width to dynamically autofit PDF full screen
  useEffect(() => {
    const el = scrollContainerRef.current;
    if (!el) return;

    let timer: any = null;
    const updateWidth = () => {
      if (el.clientWidth > 0) {
        setContainerWidth(el.clientWidth);
      }
    };

    updateWidth();

    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const width = entry.contentRect.width;
        if (width > 0) {
          if (timer) clearTimeout(timer);
          timer = setTimeout(() => {
            setContainerWidth(width);
          }, 80);
        }
      }
    });

    observer.observe(el);
    window.addEventListener("resize", updateWidth);

    return () => {
      if (timer) clearTimeout(timer);
      observer.disconnect();
      window.removeEventListener("resize", updateWidth);
    };
  }, []);

  // Load preview PDF when activeDraftId changes or after compile
  useEffect(() => {
    let active = true;
    if (!activeDraftId) return;

    async function loadPdf() {
      try {
        setLoadError(null);
        const blob = await draftsApi.getPreviewPdfBlob(activeDraftId!);
        if (active) {
          const url = URL.createObjectURL(blob);
          setPreviewPdfBlobUrl(url);
        }
      } catch (err) {
        if (active) {
          setLoadError(err instanceof Error ? err.message : "Chưa có bản xem trước. Hãy bấm 'Biên dịch' để tạo PDF.");
        }
      }
    }

    loadPdf();

    return () => {
      active = false;
    };
  }, [activeDraftId, setPreviewPdfBlobUrl]);

  const effectivePdfUrl =
    previewPdfBlobUrl ||
    (activeDraftId ? draftsApi.getPreviewPdfUrl(activeDraftId) : null);

  // Load PDF with PDF.js when effectivePdfUrl is available
  useEffect(() => {
    let isCancelled = false;
    if (!effectivePdfUrl) {
      setPdfDoc(null);
      return;
    }

    async function loadPdfDoc() {
      try {
        setPdfJsError(false);
        const doc = await getCachedPdfDocument(effectivePdfUrl!);
        if (!isCancelled) {
          setPdfDoc(doc);
          setTotalPages(doc.numPages);
          setCurrentPage(1);
        }
      } catch (err) {
        if (!isCancelled) {
          setPdfJsError(true);
          setLoadError(err instanceof Error ? err.message : "Không thể hiển thị bản xem trước PDF.");
        }
      }
    }

    loadPdfDoc();

    return () => {
      isCancelled = true;
    };
  }, [effectivePdfUrl]);

  const handleZoomIn = () => setZoomLevel((z) => Math.min(z + 15, 200));
  const handleZoomOut = () => setZoomLevel((z) => Math.max(z - 15, 50));
  const handleResetZoom = () => setZoomLevel(100);

  const handlePageChange = (newPage: number) => {
    const clamped = Math.max(1, Math.min(totalPages, newPage));
    setCurrentPage(clamped);
    const targetEl = pageRefs.current[clamped];
    if (targetEl) {
      targetEl.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  const handleDownload = () => {
    if (onDownloadPdf) {
      onDownloadPdf();
      return;
    }
    if (previewPdfBlobUrl) {
      const link = document.createElement("a");
      link.href = previewPdfBlobUrl;
      link.download = `preview_${activeDraftId || "draft"}.pdf`;
      link.click();
    }
  };

  const handleDoAnythingClick = () => {
    if (onDoAnything) {
      onDoAnything();
    } else {
      // Default: ensure tri-pane is active and focus assistant prompt
      setWorkspaceMode("tri-pane");
      setAssistantPrompt("Hỗ trợ tôi hoàn thiện bản thảo này:");
    }
  };

  return (
    <div
      data-testid="writing-preview-pane"
      className="flex-1 flex flex-col h-full bg-[#ebe7df] dark:bg-[#121110] border-r border-[#e8e4dc] dark:border-[#2e2b26] overflow-hidden relative"
    >
      {/* 1. Sub-header Controls with Overleaf-style green [Recompile] button, Download, Page Nav, Zoom */}
      <div className="h-10 px-3 border-b border-[#ece8df] dark:border-[#2a2824] bg-[#fbf9f5] dark:bg-[#1e1c19] flex items-center justify-between text-xs text-muted dark:text-zinc-400 select-none shrink-0 gap-2">
        {/* Left: Prominent Green [Recompile] button & Download */}
        <div className="flex items-center gap-2">
          {/* Smart Green Recompile Split Button with Dropdown */}
          <div className="relative inline-flex items-center rounded-lg shadow-xs" ref={recompileMenuRef}>
            <button
              type="button"
              data-testid="recompile-btn"
              onClick={onRecompile}
              disabled={isCompiling}
              className="h-7 px-3 rounded-l-lg text-xs font-semibold flex items-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white disabled:opacity-50 transition-colors cursor-pointer"
              title="Biên dịch lại bản thảo LaTeX (Recompile)"
            >
              {isCompiling ? (
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Play className="w-3.5 h-3.5 fill-current" />
              )}
              <span>Recompile</span>
            </button>
            <button
              type="button"
              data-testid="recompile-dropdown-trigger"
              onClick={() => setIsRecompileMenuOpen((prev) => !prev)}
              disabled={isCompiling}
              className="h-7 px-1.5 rounded-r-lg border-l border-emerald-700 bg-emerald-600 hover:bg-emerald-700 text-white disabled:opacity-50 transition-colors cursor-pointer flex items-center justify-center"
              title="Tùy chọn biên dịch"
            >
              <ChevronDown className="w-3 h-3" />
            </button>

            {isRecompileMenuOpen && (
              <div
                data-testid="recompile-menu-dropdown"
                className="absolute left-0 top-8 w-52 bg-white dark:bg-[#24221e] border border-[#e2dcd2] dark:border-[#33302b] rounded-xl shadow-xl z-50 p-1 text-xs space-y-0.5 animate-in fade-in zoom-in-95 duration-100"
              >
                <button
                  type="button"
                  onClick={() => {
                    setIsRecompileMenuOpen(false);
                    onRecompile?.();
                  }}
                  className="w-full px-2.5 py-1.5 rounded-lg text-left flex items-center gap-2 hover:bg-[#f2ece1] dark:hover:bg-[#2e2b26] text-ink dark:text-zinc-200 cursor-pointer"
                >
                  <Play className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Recompile</span>
                </button>
                <button
                  type="button"
                  data-testid="recompile-clear-cache-btn"
                  onClick={() => {
                    setIsRecompileMenuOpen(false);
                    handleClearCacheRecompile();
                  }}
                  className="w-full px-2.5 py-1.5 rounded-lg text-left flex items-center gap-2 hover:bg-[#f2ece1] dark:hover:bg-[#2e2b26] text-ink dark:text-zinc-200 cursor-pointer"
                >
                  <Sparkles className="w-3.5 h-3.5 text-amber-600" />
                  <span>Xóa bộ đệm & Dựng lại</span>
                </button>
              </div>
            )}
          </div>

          {/* Download PDF button */}
          <button
            type="button"
            data-testid="preview-download-btn"
            onClick={handleDownload}
            className="h-7 w-7 rounded-lg flex items-center justify-center hover:bg-[#ece8df] dark:hover:bg-[#282623] text-ink dark:text-zinc-200 transition-colors cursor-pointer"
            title="Tải xuống tệp PDF"
          >
            <Download className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Center: Page Navigation < 1 / 3 > */}
        <div
          data-testid="preview-page-nav"
          className="flex items-center bg-[#eae5db] dark:bg-[#262420] px-1.5 py-0.5 rounded-lg border border-[#ded8cc] dark:border-[#302d28] gap-1 text-[11px] font-mono"
        >
          <button
            type="button"
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage <= 1}
            className="p-1 rounded hover:bg-white dark:hover:bg-[#1a1916] disabled:opacity-30 transition-colors cursor-pointer"
            title="Trang trước"
          >
            <ChevronLeft className="w-3 h-3" />
          </button>

          <span className="px-1 text-ink dark:text-zinc-200 font-semibold">
            {currentPage} / {totalPages}
          </span>

          <button
            type="button"
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage >= totalPages}
            className="p-1 rounded hover:bg-white dark:hover:bg-[#1a1916] disabled:opacity-30 transition-colors cursor-pointer"
            title="Trang tiếp"
          >
            <ChevronRight className="w-3 h-3" />
          </button>
        </div>

        {/* Right: Zoom Controls - 100% + */}
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={handleZoomOut}
            className="p-1 rounded hover:bg-[#ece8df] dark:hover:bg-[#282623] transition-colors cursor-pointer"
            title="Thu nhỏ"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={handleResetZoom}
            className="text-[11px] font-mono px-1.5 py-0.5 rounded hover:bg-[#ece8df] dark:hover:bg-[#282623] transition-colors cursor-pointer"
            title="Đặt lại 100%"
          >
            {zoomLevel}%
          </button>
          <button
            type="button"
            onClick={handleZoomIn}
            className="p-1 rounded hover:bg-[#ece8df] dark:hover:bg-[#282623] transition-colors cursor-pointer"
            title="Phóng to"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* 2. Main Preview Container */}
      <div
        ref={scrollContainerRef}
        className="flex-1 overflow-auto flex items-center justify-center relative bg-[#ebe7df] dark:bg-[#121110]"
      >
        {isCompiling ? (
          <div className="flex flex-col items-center gap-2 text-muted dark:text-zinc-400">
            <RefreshCw className="w-6 h-6 animate-spin text-coral-500" />
            <span className="text-xs font-anthropic-serif">Đang biên dịch bản thảo trong sandbox...</span>
          </div>
        ) : loadError ? (
          <div className="flex flex-col items-center gap-2 text-center max-w-sm p-6 rounded-xl bg-white/60 dark:bg-[#1a1917]/60 border border-[#e2dcd2] dark:border-[#2e2b26]">
            <AlertCircle className="w-8 h-8 text-amber-500 mb-1" />
            <span className="text-xs font-medium text-ink dark:text-zinc-200">{loadError}</span>
            <span className="text-[11px] text-muted dark:text-zinc-400">
              Biên dịch mã nguồn LaTeX để xem trước PDF.
            </span>
          </div>
        ) : pdfDoc && !pdfJsError ? (
          <div
            className={cn(
              "w-full h-full overflow-y-auto flex flex-col items-center px-0 sm:px-3 pt-2 sm:pt-3 pb-16 gap-2 scroll-smooth",
              zoomLevel > 100 ? "overflow-x-auto" : "overflow-x-hidden"
            )}
          >
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNum) => (
              <div
                key={pageNum}
                ref={(el) => {
                  pageRefs.current[pageNum] = el;
                }}
                className="w-full flex justify-center shrink-0 px-0.5 sm:px-0"
              >
                <PaperPageCanvas
                  pdfDoc={pdfDoc}
                  pageNumber={pageNum}
                  zoomLevel={zoomLevel}
                  containerWidth={containerWidth}
                  onInView={(p) => setCurrentPage(p)}
                  onDoublePageClick={handleInverseSearch}
                />
              </div>
            ))}
          </div>
        ) : effectivePdfUrl ? (
          <div
            className="w-full h-full relative flex items-center justify-center transition-all duration-200 p-4"
            style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: "top center" }}
          >
            <iframe
              src={`${effectivePdfUrl}#toolbar=0&navpanes=0`}
              title="Draft PDF Preview"
              className="w-full h-full rounded shadow-md border border-[#e2dcd2] dark:border-[#2e2b26]"
            />
          </div>
        ) : (
          <div className="text-xs text-muted dark:text-zinc-500">
            Chưa có tài liệu được chọn.
          </div>
        )}
      </div>

      {/* 3. Floating Bottom-Right [ + Do anything ] Action Pill */}
      {showDoAnything && (
        <div className="absolute bottom-5 right-5 z-20 pointer-events-auto">
          <button
            type="button"
            data-testid="preview-do-anything-btn"
            onClick={handleDoAnythingClick}
            className="h-10 px-4 rounded-full bg-white dark:bg-[#201e1a] border border-[#e2dcd2] dark:border-[#38332c] hover:border-coral-500/50 hover:bg-coral-500/10 text-ink dark:text-zinc-100 shadow-lg flex items-center gap-2 text-xs font-semibold font-anthropic-serif transition-all hover:scale-105 active:scale-95 cursor-pointer group"
            title="Hỏi AI bất cứ điều gì về bản thảo hoặc bổ sung nội dung (+ Do anything)"
          >
            <Sparkles className="w-4 h-4 text-coral-500 group-hover:rotate-12 transition-transform" />
            <span>+ Do anything</span>
          </button>
        </div>
      )}
    </div>
  );
}
