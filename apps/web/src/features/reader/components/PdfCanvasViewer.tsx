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
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [scrollContainer, setScrollContainer] = useState<HTMLDivElement | null>(null);

  const setContainerRefs = useCallback((el: HTMLDivElement | null) => {
    containerRef.current = el;
    setScrollContainer(el);
  }, []);

  const [pdfDoc, setPdfDoc] = useState<PDFDocumentProxy | null>(null);
  const [loadedUrl, setLoadedUrl] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [retryKey, setRetryKey] = useState<number>(0);
  const isLoadingPdf = loadedUrl !== fileUrl && !loadError;

  // Track whether currentPage was updated by IntersectionObserver scroll or programmatic click
  const lastScrolledByObserverRef = useRef<number | null>(currentPage);

  // Track active user scrolling to prevent any programmatic auto-scroll hijacking
  const isUserScrollingRef = useRef(false);
  const userScrollTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const scrollRafRef = useRef<number | null>(null);

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

  // Floating Pagination HUD Auto-hide states (5s inactive timer)
  const [isHudVisible, setIsHudVisible] = useState(true);
  const hudTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isHudHoveredRef = useRef(false);

  const resetHudTimer = useCallback(() => {
    setIsHudVisible(true);
    if (hudTimerRef.current) {
      clearTimeout(hudTimerRef.current);
      hudTimerRef.current = null;
    }
    if (!isHudHoveredRef.current) {
      hudTimerRef.current = setTimeout(() => {
        setIsHudVisible(false);
      }, 5000);
    }
  }, []);

  // Automatic reset when currentPage or readingMode changes
  useEffect(() => {
    resetHudTimer();
    return () => {
      if (hudTimerRef.current) {
        clearTimeout(hudTimerRef.current);
        hudTimerRef.current = null;
      }
    };
  }, [currentPage, readingMode, resetHudTimer]);

  const handleHudMouseEnter = useCallback(() => {
    isHudHoveredRef.current = true;
    if (hudTimerRef.current) {
      clearTimeout(hudTimerRef.current);
      hudTimerRef.current = null;
    }
    setIsHudVisible(true);
  }, []);

  const handleHudMouseLeave = useCallback(() => {
    isHudHoveredRef.current = false;
    resetHudTimer();
  }, [resetHudTimer]);

  // 1. Load PDF Document via cached PDF.js loader with 12s timeout guard
  useEffect(() => {
    let isCancelled = false;

    // 12s timeout guard to eliminate infinite hanging loading skeleton
    const timeoutId = window.setTimeout(() => {
      if (isCancelled) return;
      console.warn("[PDF.js] Load timeout exceeded (12s) for:", fileUrl);
      setLoadError(
        "Đã quá thời gian nạp tài liệu PDF (12s). Vui lòng thử tải lại hoặc kiểm tra kết nối mạng."
      );
      setLoadedUrl(fileUrl);
    }, 12000);

    getCachedPdfDocument(fileUrl)
      .then((doc) => {
        if (isCancelled) return;
        window.clearTimeout(timeoutId);
        setPdfDoc(doc);
        setLoadedUrl(fileUrl);
        setLoadError(null);
        if (onPageCountDetected) {
          onPageCountDetected(doc.numPages);
        }
      })
      .catch((err: unknown) => {
        if (isCancelled) return;
        window.clearTimeout(timeoutId);
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
      window.clearTimeout(timeoutId);
    };
  }, [fileUrl, onPageCountDetected, retryKey]);

  // Total pages from PDF document or metadata fallback
  const totalPages = pdfDoc?.numPages || documentDetail?.page_count || 1;

  // Active scroll tracking: identify the page occupying the reading viewport
  const updateCurrentPageFromScroll = useCallback(() => {
    if (!scrollContainer || readingMode !== "continuous" || totalPages <= 1) {
      return;
    }

    const containerRect = scrollContainer.getBoundingClientRect();
    if (containerRect.height <= 0) return;

    // Reading anchor: 30% from the top of the container
    const readingAnchorY = containerRect.top + Math.min(200, containerRect.height * 0.3);

    let bestPage = 1;
    let maxVisibleHeight = -1;

    for (let p = 1; p <= totalPages; p++) {
      const pageEl = document.getElementById(`pdf-page-${p}`);
      if (!pageEl) continue;
      const r = pageEl.getBoundingClientRect();

      // Check if page covers the reading anchor
      if (r.top <= readingAnchorY && r.bottom >= readingAnchorY) {
        bestPage = p;
        break;
      }

      // Fallback: page with the largest visible overlap
      const vTop = Math.max(r.top, containerRect.top);
      const vBottom = Math.min(r.bottom, containerRect.bottom);
      const vHeight = Math.max(0, vBottom - vTop);
      if (vHeight > maxVisibleHeight) {
        maxVisibleHeight = vHeight;
        bestPage = p;
      }
    }

    if (bestPage > 0 && bestPage !== lastScrolledByObserverRef.current) {
      lastScrolledByObserverRef.current = bestPage;
      setCurrentPage(bestPage);
    }
  }, [scrollContainer, readingMode, totalPages, setCurrentPage]);

  const handleContainerScroll = useCallback(() => {
    isUserScrollingRef.current = true;
    if (userScrollTimeoutRef.current) {
      clearTimeout(userScrollTimeoutRef.current);
    }
    userScrollTimeoutRef.current = setTimeout(() => {
      isUserScrollingRef.current = false;
      updateCurrentPageFromScroll();
    }, 400);

    if (scrollRafRef.current === null) {
      scrollRafRef.current = requestAnimationFrame(() => {
        scrollRafRef.current = null;
        updateCurrentPageFromScroll();
      });
    }
  }, [updateCurrentPageFromScroll]);

  useEffect(() => {
    return () => {
      if (scrollRafRef.current !== null) {
        cancelAnimationFrame(scrollRafRef.current);
      }
      if (userScrollTimeoutRef.current) {
        clearTimeout(userScrollTimeoutRef.current);
      }
    };
  }, []);

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

  // Track last scrolled bbox key to prevent continuous jumping when user scrolls
  const lastScrolledBboxKeyRef = useRef<string | null>(null);

  // 3. Scroll to Target Page ONLY on programmatic jumps or citation clicks
  // (Never interrupt natural user scrolling velocity)
  useEffect(() => {
    // A. Citation Highlight Clicked: Scroll into view and center on bounding box ONCE
    if (activeBbox && activeBbox[4]) {
      const bboxKey = `${activeBbox[0]}-${activeBbox[1]}-${activeBbox[2]}-${activeBbox[3]}-${activeBbox[4]}`;
      if (lastScrolledBboxKeyRef.current === bboxKey) {
        return;
      }

      const pageNum = activeBbox[4];
      const pageEl = document.getElementById(`pdf-page-${pageNum}`);
      if (pageEl && scrollContainer) {
        lastScrolledBboxKeyRef.current = bboxKey;
        const bboxOverlay = pageEl.querySelector<HTMLElement>('[data-testid="grounded-bbox-overlay"]');
        const target = bboxOverlay || pageEl;
        if (typeof target.scrollIntoView === "function") {
          try {
            target.scrollIntoView({ behavior: "smooth", block: "center" });
          } catch {
            // Safe fallback
          }
        }

        const containerRect = scrollContainer.getBoundingClientRect();
        const targetRect = target.getBoundingClientRect();
        if (containerRect.height > 0 && targetRect.height > 0) {
          const relativeTop = targetRect.top - containerRect.top + scrollContainer.scrollTop;
          const centeredTop = Math.max(
            0,
            relativeTop - containerRect.height / 2 + targetRect.height / 2
          );

          if (typeof scrollContainer.scrollTo === "function") {
            scrollContainer.scrollTo({ top: centeredTop, behavior: "smooth" });
          } else {
            scrollContainer.scrollTop = centeredTop;
          }
        }
      }
      return;
    } else {
      lastScrolledBboxKeyRef.current = null;
    }

    // B. User is actively scrolling: DO NOT hijack scroll!
    if (isUserScrollingRef.current) {
      lastScrolledByObserverRef.current = currentPage;
      return;
    }

    // C. Page updated naturally by scroll observer: DO NOT hijack scroll
    if (lastScrolledByObserverRef.current === currentPage) {
      return;
    }

    // D. In continuous reading mode: If page is already substantially visible in viewport, do NOT scroll!
    if (readingMode === "continuous") {
      const pageEl = document.getElementById(`pdf-page-${currentPage}`);
      if (pageEl && scrollContainer) {
        const containerRect = scrollContainer.getBoundingClientRect();
        const pageRect = pageEl.getBoundingClientRect();
        const visibleTop = Math.max(pageRect.top, containerRect.top);
        const visibleBottom = Math.min(pageRect.bottom, containerRect.bottom);
        const visibleHeight = visibleBottom - visibleTop;
        if (visibleHeight > 100) {
          lastScrolledByObserverRef.current = currentPage;
          return;
        }
      }
    }

    // E. Explicit programmatic jump (e.g. clicked thumbnail, pagination controls, or single/two-page switch)
    const pageEl = document.getElementById(`pdf-page-${currentPage}`);
    if (pageEl && scrollContainer) {
      lastScrolledByObserverRef.current = currentPage;
      const containerRect = scrollContainer.getBoundingClientRect();
      const pageRect = pageEl.getBoundingClientRect();
      const relativeTop = pageRect.top - containerRect.top + scrollContainer.scrollTop;
      const targetTop = relativeTop - 16;
      if (typeof scrollContainer.scrollTo === "function") {
        scrollContainer.scrollTo({ top: targetTop, behavior: "smooth" });
      } else {
        scrollContainer.scrollTop = targetTop;
      }
    }
  }, [currentPage, activeBbox, readingMode, pdfDoc, scrollContainer]);

  // Metadata dimensions lookup map
  const pageDimensionsMap = useMemo(() => {
    const map = new Map<number, [number, number]>();
    documentDetail?.pages_metadata?.forEach((pm) => {
      map.set(pm.page_number, pm.dimensions);
    });
    return map;
  }, [documentDetail?.pages_metadata]);

  // Track container width for responsive scaling (measured purely from PDF container, never window.innerWidth)
  const [containerWidth, setContainerWidth] = useState<number>(0);

  useEffect(() => {
    if (!scrollContainer) return;

    const measureWidth = () => {
      const clientW = scrollContainer.clientWidth;
      if (clientW > 0) {
        setContainerWidth((prev) => (Math.abs(prev - clientW) >= 1 ? clientW : prev));
      }
    };

    // Immediate initial measurement of container clientWidth when mounted
    measureWidth();

    if (typeof ResizeObserver === "undefined") {
      return;
    }

    let rafId: number | null = null;
    let debounceTimer: ReturnType<typeof setTimeout> | null = null;

    const ro = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (!entry) return;
      const newWidth = Math.round(entry.contentRect.width || scrollContainer.clientWidth);
      if (newWidth <= 0) return;

      if (debounceTimer) clearTimeout(debounceTimer);
      if (rafId) cancelAnimationFrame(rafId);

      // Debounce slightly (16ms) combined with requestAnimationFrame for smooth 60fps responsive scaling
      debounceTimer = setTimeout(() => {
        rafId = requestAnimationFrame(() => {
          setContainerWidth((prev) => (Math.abs(prev - newWidth) >= 1 ? newWidth : prev));
        });
      }, 16);
    });

    ro.observe(scrollContainer);
    return () => {
      ro.disconnect();
      if (debounceTimer) clearTimeout(debounceTimer);
      if (rafId) cancelAnimationFrame(rafId);
    };
  }, [scrollContainer, pdfDoc]);

  // Dynamic Fit-to-Width Base Scale:
  // Dynamically computes the exact scale ensuring the PDF page fills available panel width
  // Edge-to-Edge without huge empty bars on sides, and without right-edge clipping.
  const fitWidthBaseScale = useMemo(() => {
    const standardWidth = pageDimensionsMap.get(currentPage)?.[0] || 595.32;
    // Measured width of the PDF container; fallback to scrollContainer clientWidth or standard fallback
    const effectiveWidth =
      containerWidth > 0
        ? containerWidth
        : (scrollContainer?.clientWidth || (typeof window !== "undefined" ? (window.innerWidth < 768 ? window.innerWidth : window.innerWidth * 0.5) : 595.32));

    // Full screen edge-to-edge on mobile (< 640px) with 0 padding; 20px on desktop (>= 640px)
    // Edge-to-Edge display eliminates huge black bars
    const padding = effectiveWidth < 640 ? 0 : 20;
    const available = Math.max(220, effectiveWidth - padding);
    return Number((available / standardWidth).toFixed(3));
  }, [containerWidth, currentPage, pageDimensionsMap, scrollContainer]);

  // Responsive Effective Zoom:
  // - Default is always fitWidthBaseScale (page auto-scales 100% to fit container width)
  // - When user clicks Zoom (+/-), zoomRatio scales proportionally relative to fit width
  const effectiveZoom = useMemo(() => {
    return Number((zoomRatio * fitWidthBaseScale).toFixed(3));
  }, [fitWidthBaseScale, zoomRatio]);

  // Two-page spread zoom: fits both pages comfortably side by side without clipping
  const twoPageZoom = useMemo(() => {
    return Number((zoomRatio * fitWidthBaseScale * 0.49).toFixed(3));
  }, [fitWidthBaseScale, zoomRatio]);

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
            setPdfDoc(null);
            setRetryKey((prev) => prev + 1);
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
        ref={setContainerRefs}
        onScroll={handleContainerScroll}
        onMouseUp={handleMouseUp}
        onMouseMove={resetHudTimer}
        className={cn(
          "flex-1 relative overflow-y-auto overflow-x-hidden px-0 sm:px-2.5 py-0 sm:py-4 transition-colors duration-200 [contain:layout_style] scrollbar-none [scrollbar-width:none] [&::-webkit-scrollbar]:hidden",
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
            "w-full mx-auto pb-16 flex flex-col items-center",
            readingMode === "continuous" && "gap-2 sm:gap-3",
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
                  currentPageNumber={currentPage}
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
                currentPageNumber={currentPage}
                onPageVisible={handlePageVisible}
                fallbackDimensions={pageDimensionsMap.get(pageNum)}
                readingMode={readingMode}
                positionInSpread="single"
              />
            ))
          )}

          {/* Floating Navigation HUD for Single Page Mode */}
          {readingMode === "single" && totalPages > 1 && (
            <div
              data-testid="floating-pagination-hud"
              onMouseEnter={handleHudMouseEnter}
              onMouseLeave={handleHudMouseLeave}
              className={cn(
                "sticky bottom-4 z-20 mt-6 inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/95 dark:bg-[#201e1b]/95 backdrop-blur-md border border-[#e2ded6] dark:border-[#38332c] shadow-lg select-none text-xs transition-all duration-300 ease-out",
                isHudVisible
                  ? "opacity-100 translate-y-0 pointer-events-auto"
                  : "opacity-0 translate-y-2 pointer-events-none"
              )}
            >
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
            <div
              data-testid="floating-pagination-hud"
              onMouseEnter={handleHudMouseEnter}
              onMouseLeave={handleHudMouseLeave}
              className={cn(
                "sticky bottom-4 z-20 mt-6 inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/95 dark:bg-[#201e1b]/95 backdrop-blur-md border border-[#e2ded6] dark:border-[#38332c] shadow-lg select-none text-xs transition-all duration-300 ease-out",
                isHudVisible
                  ? "opacity-100 translate-y-0 pointer-events-auto"
                  : "opacity-0 translate-y-2 pointer-events-none"
              )}
            >
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
