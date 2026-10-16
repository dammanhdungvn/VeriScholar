import { useState, useRef, useEffect, useMemo, useCallback } from "react";
import type { PDFDocumentProxy } from "pdfjs-dist";
import { AlertCircle, RefreshCw, Eye, ChevronLeft, ChevronRight } from "lucide-react";
import { getCachedPdfDocument, clearCachedPdfDocument } from "../lib/pdfRenderQueue";
import { PdfPageCanvas } from "./PdfPageCanvas";
import { PdfThumbnailSidebar } from "./PdfThumbnailSidebar";
import { ScholarSelectionMenu } from "./ScholarSelectionMenu";
import { useReaderStore } from "../stores/useReaderStore";
import { useTheme } from "@/hooks/useTheme";
import type { BoundingBox } from "@/types/api";
import type { DocumentDetailResponseData } from "@/types/document";
import { cn } from "@/lib/utils";

interface PdfCanvasViewerProps {
  documentId: string;
  documentDetail?: DocumentDetailResponseData | null;
  fileUrl: string;
  currentPage: number;
  zoomRatio: number;
  rotationDeg: 0 | 90 | 180 | 270;
  activeBbox: BoundingBox | null;
  isLoading?: boolean;
  onPageCountDetected?: (count: number) => void;
  onClearHighlight?: () => void;
  onAddToNote?: (selectedText: string, pageNumber: number, bbox?: BoundingBox | null) => void;
  onAddToChat?: (selectedText: string, pageNumber: number, bbox?: BoundingBox | null) => void;
  onAskChat?: (prompt: string) => void;
}

export const BASE_PDF_RENDER_SCALE = 1.44;

export function PdfCanvasViewer({
  documentId,
  documentDetail,
  fileUrl,
  currentPage,
  zoomRatio,
  rotationDeg,
  activeBbox,
  isLoading: isExternalLoading = false,
  onPageCountDetected,
  onClearHighlight,
  onAddToNote,
  onAddToChat,
  onAskChat,
}: PdfCanvasViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [pdfDoc, setPdfDoc] = useState<PDFDocumentProxy | null>(null);
  const [loadedUrl, setLoadedUrl] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const isLoadingPdf = loadedUrl !== fileUrl && !loadError;

  // Track whether currentPage was updated by IntersectionObserver scroll or programmatic click
  const lastScrolledByObserverRef = useRef<number | null>(null);

  // Store & Theme States
  const { theme } = useTheme();
  const isDark = theme === "dark";
  const readingMode = useReaderStore((s) => s.readingMode);
  const colorTheme = isDark ? "dark" : "default";
  const isThumbnailsOpen = useReaderStore((s) => s.isThumbnailsOpen);
  const setIsThumbnailsOpen = useReaderStore((s) => s.setIsThumbnailsOpen);
  const setCurrentPage = useReaderStore((s) => s.setCurrentPage);

  // Text selection state
  const [selectedText, setSelectedText] = useState("");
  const [selectionCoord, setSelectionCoord] = useState<{ x: number; y: number } | null>(null);
  const [selectionPage, setSelectionPage] = useState<number>(currentPage);
  const [selectionBbox, setSelectionBbox] = useState<BoundingBox | null>(null);

  // 1. Load PDF Document via cached PDF.js loader
  useEffect(() => {
    let isCancelled = false;

    getCachedPdfDocument(fileUrl)
      .then((doc) => {
        if (isCancelled) return;
        setPdfDoc(doc);
        setLoadedUrl(fileUrl);
        setLoadError(null);
        if (onPageCountDetected) {
          onPageCountDetected(doc.numPages);
        }
      })
      .catch((err: unknown) => {
        if (isCancelled) return;
        console.error("[PDF.js] Failed to load document:", err);
        setLoadError(
          err instanceof Error
            ? err.message
            : "Không thể tải tệp PDF bài báo. Vui lòng kiểm tra lại kết nối mạng hoặc thử lại."
        );
        setLoadedUrl(fileUrl);
      });

    return () => {
      isCancelled = true;
    };
  }, [fileUrl, onPageCountDetected]);

  // Total pages from PDF document or metadata fallback
  const totalPages = pdfDoc?.numPages || documentDetail?.page_count || 1;

  // 2. Handle Text Selection in PDF Text Layer with Normalized BoundingBox Calculation
  const handleMouseUp = () => {
    const selection = window.getSelection();
    const text = selection?.toString().trim();

    if (text && text.length > 2) {
      const range = selection?.getRangeAt(0);
      const rect = range?.getBoundingClientRect();
      const containerRect = containerRef.current?.getBoundingClientRect();

      if (rect && containerRect) {
        // Find which page the selection is on by traversing up
        let node: Node | null = range?.startContainer ?? null;
        let detectedPage = currentPage;
        let matchedPageEl: HTMLElement | null = null;

        while (node && node !== containerRef.current) {
          if (node instanceof HTMLElement && node.dataset?.pageNumber) {
            detectedPage = Number(node.dataset.pageNumber);
            matchedPageEl = node;
            break;
          }
          node = node.parentNode;
        }

        const targetPageEl =
          matchedPageEl || document.getElementById(`pdf-page-${detectedPage}`);

        // Calculate normalized BoundingBox: [x0, y0, x1, y1, page]
        let calculatedBbox: BoundingBox | null = null;
        if (targetPageEl) {
          const innerPage =
            targetPageEl.querySelector<HTMLElement>(".textLayer")?.parentElement ||
            targetPageEl.querySelector<HTMLElement>("canvas")?.parentElement ||
            targetPageEl;
          const pageRect = innerPage.getBoundingClientRect();

          if (pageRect.width > 0 && pageRect.height > 0) {
            const rawX0 = (rect.left - pageRect.left) / pageRect.width;
            const rawY0 = (rect.top - pageRect.top) / pageRect.height;
            const rawX1 = (rect.right - pageRect.left) / pageRect.width;
            const rawY1 = (rect.bottom - pageRect.top) / pageRect.height;

            const x0 = Number(Math.max(0, Math.min(1, rawX0)).toFixed(4));
            const y0 = Number(Math.max(0, Math.min(1, rawY0)).toFixed(4));
            const x1 = Number(Math.max(x0, Math.min(1, rawX1)).toFixed(4));
            const y1 = Number(Math.max(y0, Math.min(1, rawY1)).toFixed(4));
            const normalizedPage = Math.max(1, detectedPage);

            calculatedBbox = [x0, y0, x1, y1, normalizedPage];
          }
        }

        setSelectedText(text);
        setSelectionPage(detectedPage);
        setSelectionBbox(calculatedBbox);
        setSelectionCoord({
          x: rect.left - containerRect.left + rect.width / 2,
          y: rect.top - containerRect.top - 8,
        });
        return;
      }
    }

    setSelectedText("");
    setSelectionCoord(null);
    setSelectionBbox(null);
  };

  const handleClearSelection = () => {
    setSelectedText("");
    setSelectionCoord(null);
    setSelectionBbox(null);
    window.getSelection()?.removeAllRanges();
  };

  // 3. Scroll to Target Page ONLY on programmatic jumps or citation clicks
  // (Never interrupt natural user scrolling velocity)
  useEffect(() => {
    if (readingMode !== "continuous") return;

    // A. Citation Highlight Clicked: Always scroll into view
    if (activeBbox && activeBbox[4]) {
      const pageEl = document.getElementById(`pdf-page-${activeBbox[4]}`);
      if (pageEl && containerRef.current) {
        pageEl.scrollIntoView({ behavior: "smooth", block: "start" });
      }
      return;
    }

    // B. Page updated naturally by scroll observer: DO NOT hijack scroll
    if (lastScrolledByObserverRef.current === currentPage) {
      return;
    }

    // C. User explicitly jumped via controls or sidebar
    const pageEl = document.getElementById(`pdf-page-${currentPage}`);
    if (pageEl && containerRef.current) {
      pageEl.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [currentPage, activeBbox, readingMode]);

  // Metadata dimensions lookup map
  const pageDimensionsMap = useMemo(() => {
    const map = new Map<number, [number, number]>();
    documentDetail?.pages_metadata?.forEach((pm) => {
      map.set(pm.page_number, pm.dimensions);
    });
    return map;
  }, [documentDetail?.pages_metadata]);

  // Track container width for responsive scaling
  const [containerWidth, setContainerWidth] = useState<number>(() => {
    return typeof window !== "undefined" ? window.innerWidth : 1024;
  });

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    if (el.clientWidth > 0) {
      setContainerWidth(el.clientWidth);
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

  // Responsive base scale:
  // - On desktop & tablet (container >= 650px): fixed at developer baseline 1.44 (100% UI = 144% width)
  // - On mobile (< 650px): smoothly fits mobile screen width so paper is never cut off
  const responsiveBaseScale = useMemo(() => {
    if (containerWidth >= 650) {
      return BASE_PDF_RENDER_SCALE;
    }
    const standardWidth = pageDimensionsMap.get(currentPage)?.[0] || 595.32;
    const available = Math.max(260, containerWidth - 20);
    return Number((available / standardWidth).toFixed(3));
  }, [containerWidth, currentPage, pageDimensionsMap]);

  // The UI displays 100% when zoomRatio = 1.0.
  // Every +5% increments zoomRatio by +0.05, and -5% decrements by -0.05.
  const effectiveZoom = useMemo(() => {
    return Number((zoomRatio * responsiveBaseScale).toFixed(3));
  }, [zoomRatio, responsiveBaseScale]);

  // Two-page spread zoom to ensure both pages fit comfortably side by side
  const twoPageZoom = useMemo(() => {
    return Number((zoomRatio * responsiveBaseScale * 0.52).toFixed(3));
  }, [zoomRatio, responsiveBaseScale]);

  // Pages array for rendering
  const pagesToRender = useMemo(() => {
    if (readingMode === "continuous") {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }
    if (readingMode === "two-page") {
      const first = currentPage % 2 === 0 ? currentPage - 1 : currentPage;
      const second = first + 1;
      return second <= totalPages ? [first, second] : [first];
    }
    // Single page mode
    return [currentPage];
  }, [readingMode, totalPages, currentPage]);

  const handlePageVisible = useCallback(
    (pageNum: number) => {
      if (readingMode === "continuous") {
        lastScrolledByObserverRef.current = pageNum;
        setCurrentPage(pageNum);
      }
    },
    [readingMode, setCurrentPage]
  );

  // Loading Screen
  if (isExternalLoading || (isLoadingPdf && !pdfDoc)) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 bg-[#faf8f4] dark:bg-[#161513] select-none">
        <div className="w-16 h-20 bg-surface-cream-strong/70 dark:bg-[#252320] rounded-lg shadow-sm border border-hairline animate-pulse mb-4 flex items-center justify-center">
          <Eye className="w-6 h-6 text-primary/40 animate-bounce" />
        </div>
        <h4 className="text-xs font-serif font-semibold text-ink dark:text-zinc-200 mb-1">
          Đang nạp bài báo khoa học...
        </h4>
        <p className="text-[11px] text-muted font-mono animate-pulse">
          Trang {currentPage} • Phân giải cao & trích xuất tầng văn bản (PDF.js Engine)
        </p>
      </div>
    );
  }

  // Error Screen with Retry
  if (loadError) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center bg-[#faf8f4] dark:bg-[#161513]">
        <AlertCircle className="w-10 h-10 text-amber-600 dark:text-amber-500 mb-3" />
        <h4 className="text-sm font-serif font-semibold text-ink dark:text-zinc-100 mb-1">
          Không thể kết xuất tài liệu PDF
        </h4>
        <p className="text-xs text-muted max-w-sm mb-4 leading-relaxed font-sans">
          {loadError}
        </p>
        <button
          type="button"
          onClick={() => {
            clearCachedPdfDocument(fileUrl);
            setLoadError(null);
            setLoadedUrl(null);
          }}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium bg-primary text-white hover:bg-primary/90 transition-colors shadow-xs cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Thử tải lại</span>
        </button>
      </div>
    );
  }

  const containerThemeBg = {
    default: "bg-[#f2efe9] dark:bg-[#121110]",
    dark: "bg-[#0b0a0a]",
    sepia: "bg-[#ece2d0] dark:bg-[#1a1714]",
    contrast: "bg-[#ded8cc] dark:bg-[#080808]",
  }[colorTheme];

  return (
    <div className="flex-1 flex w-full h-full overflow-hidden relative select-text">
      {/* 1. Left Thumbnail Sidebar Drawer */}
      <PdfThumbnailSidebar
        isOpen={isThumbnailsOpen}
        onClose={() => setIsThumbnailsOpen(false)}
        totalPages={totalPages}
        currentPage={currentPage}
        onSelectPage={(pageNum) => {
          lastScrolledByObserverRef.current = null; // Programmatic jump
          setCurrentPage(pageNum);
          if (readingMode === "continuous") {
            const el = document.getElementById(`pdf-page-${pageNum}`);
            el?.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        }}
        activeCitationPage={activeBbox ? activeBbox[4] : null}
        documentTitle={documentDetail?.title || documentDetail?.filename}
        pdfDoc={pdfDoc}
      />

      {/* 2. Main PDF Scroll Canvas Area */}
      <div
        ref={containerRef}
        onMouseUp={handleMouseUp}
        className={cn(
          "flex-1 relative overflow-y-auto overflow-x-auto px-2 sm:px-3 py-4 flex justify-center scrollbar-none transition-colors duration-200 [contain:layout_style]",
          containerThemeBg
        )}
      >
        {/* Scholar Floating Selection Menu */}
        {selectedText && selectionCoord && (
          <ScholarSelectionMenu
            selectedText={selectedText}
            coord={selectionCoord}
            pageNumber={selectionPage}
            bbox={selectionBbox}
            documentTitle={documentDetail?.title || documentDetail?.filename}
            onAddToNote={(text, page, bbox) => {
              if (onAddToNote) onAddToNote(text, page, bbox);
            }}
            onAddToChat={onAddToChat}
            onAskChat={onAskChat}
            onClearSelection={handleClearSelection}
          />
        )}

        {/* Pages Container: Stack for Continuous, Side-by-Side Book for Two-Page, Centered for Single */}
        <div
          className={cn(
            "w-full max-w-full pb-20 flex flex-col items-center",
            readingMode === "continuous" && "gap-4",
            readingMode === "single" && "justify-center min-h-[calc(100vh-140px)]",
            readingMode === "two-page" && "gap-2"
          )}
        >
          {readingMode === "two-page" ? (
            <div className="flex flex-row items-start justify-center gap-0 max-w-full overflow-x-auto shadow-md rounded-xs">
              {pagesToRender.map((pageNum, idx) => (
                <PdfPageCanvas
                  key={`${documentId}-page-${pageNum}`}
                  pdfDoc={pdfDoc}
                  pageNumber={pageNum}
                  zoomRatio={twoPageZoom}
                  rotationDeg={rotationDeg}
                  activeBbox={activeBbox}
                  onClearHighlight={onClearHighlight}
                  colorTheme={colorTheme}
                  isCurrentPage={pageNum === currentPage}
                  onPageVisible={handlePageVisible}
                  fallbackDimensions={pageDimensionsMap.get(pageNum)}
                  readingMode="two-page"
                  positionInSpread={idx === 0 ? "left" : "right"}
                />
              ))}
            </div>
          ) : (
            pagesToRender.map((pageNum) => (
              <PdfPageCanvas
                key={`${documentId}-page-${pageNum}`}
                pdfDoc={pdfDoc}
                pageNumber={pageNum}
                zoomRatio={effectiveZoom}
                rotationDeg={rotationDeg}
                activeBbox={activeBbox}
                onClearHighlight={onClearHighlight}
                colorTheme={colorTheme}
                isCurrentPage={pageNum === currentPage}
                onPageVisible={handlePageVisible}
                fallbackDimensions={pageDimensionsMap.get(pageNum)}
                readingMode={readingMode}
                positionInSpread="single"
              />
            ))
          )}

          {/* Floating Navigation HUD for Single Page Mode */}
          {readingMode === "single" && totalPages > 1 && (
            <div className="sticky bottom-4 z-20 mt-6 inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/95 dark:bg-[#201e1b]/95 backdrop-blur-md border border-[#e2ded6] dark:border-[#38332c] shadow-lg select-none text-xs">
              <button
                type="button"
                onClick={() => setCurrentPage(currentPage - 1)}
                disabled={currentPage <= 1}
                title="Trang trước (Page Up)"
                className="p-1 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-800 disabled:opacity-30 disabled:pointer-events-none transition-colors cursor-pointer text-ink dark:text-zinc-200"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="font-mono font-medium text-ink dark:text-zinc-200 text-xs px-1">
                Trang {currentPage} / {totalPages}
              </span>
              <button
                type="button"
                onClick={() => setCurrentPage(currentPage + 1)}
                disabled={currentPage >= totalPages}
                title="Trang tiếp theo (Page Down)"
                className="p-1 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-800 disabled:opacity-30 disabled:pointer-events-none transition-colors cursor-pointer text-ink dark:text-zinc-200"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}

          {/* Floating Navigation HUD for Two-Page Spread Mode */}
          {readingMode === "two-page" && totalPages > 1 && (
            <div className="sticky bottom-4 z-20 mt-6 inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/95 dark:bg-[#201e1b]/95 backdrop-blur-md border border-[#e2ded6] dark:border-[#38332c] shadow-lg select-none text-xs">
              <button
                type="button"
                onClick={() => setCurrentPage(Math.max(1, currentPage - 2))}
                disabled={currentPage <= 1}
                title="Hai trang trước"
                className="p-1 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-800 disabled:opacity-30 disabled:pointer-events-none transition-colors cursor-pointer text-ink dark:text-zinc-200"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="font-mono font-medium text-ink dark:text-zinc-200 text-xs px-1">
                Trang {pagesToRender[0]}{pagesToRender[1] ? ` - ${pagesToRender[1]}` : ""} / {totalPages}
              </span>
              <button
                type="button"
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 2))}
                disabled={currentPage >= totalPages - 1}
                title="Hai trang tiếp theo"
                className="p-1 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-800 disabled:opacity-30 disabled:pointer-events-none transition-colors cursor-pointer text-ink dark:text-zinc-200"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
