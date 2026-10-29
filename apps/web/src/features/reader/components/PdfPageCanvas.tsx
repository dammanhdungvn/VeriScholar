import { useEffect, useRef, useState, memo } from "react";
import type { PDFDocumentProxy, PDFPageProxy } from "pdfjs-dist";
import { pdfjsLib } from "../lib/pdfjs-init";
import { pdfRenderQueue, runWhenIdle } from "../lib/pdfRenderQueue";
import { BboxHighlightLayer } from "./BboxHighlightLayer";
import type { BoundingBox } from "@/types/api";
import type { ReaderColorTheme, ReadingMode } from "../stores/useReaderStore";
import { cn } from "@/lib/utils";

interface PdfPageCanvasProps {
  pdfDoc?: PDFDocumentProxy | null;
  pageNumber: number;
  zoomRatio: number;
  rotationDeg: 0 | 90 | 180 | 270;
  activeBbox?: BoundingBox | null;
  activeBboxes?: BoundingBox[] | null;
  onClearHighlight?: () => void;
  colorTheme?: ReaderColorTheme;
  isCurrentPage?: boolean;
  onPageVisible?: (pageNumber: number) => void;
  fallbackDimensions?: [number, number];
  readingMode?: ReadingMode;
  positionInSpread?: "left" | "right" | "single";
  currentPageNumber?: number;
}

export const PdfPageCanvas = memo(function PdfPageCanvas({
  pdfDoc = null,
  pageNumber,
  zoomRatio,
  rotationDeg,
  activeBbox = null,
  activeBboxes,
  onClearHighlight,
  colorTheme = "default",
  isCurrentPage = false,
  onPageVisible,
  fallbackDimensions,
  readingMode = "continuous",
  positionInSpread = "single",
  currentPageNumber,
}: PdfPageCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const textLayerRef = useRef<HTMLDivElement>(null);

  const [isRendered, setIsRendered] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const [pageSize, setPageSize] = useState<{ width: number; height: number } | null>(null);

  // Refs for tracking priority dynamically without re-triggering render hook on scroll
  const isCurrentPageRef = useRef(isCurrentPage);
  isCurrentPageRef.current = isCurrentPage;
  const currentPageNumberRef = useRef(currentPageNumber);
  currentPageNumberRef.current = currentPageNumber;

  // 1. Render Lookahead Observer: pre-render canvases within 800px lookahead buffer
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const renderObserver = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        if (entry.isIntersecting) {
          setIsVisible(true);
        } else {
          // If page scrolled out before finishing render, allow cancellation
          if (!isRendered) {
            setIsVisible(false);
          }
        }
      },
      {
        rootMargin: "800px 0px 800px 0px", // High-velocity lookahead buffer for seamless fast scrolling
        threshold: 0,
      }
    );

    renderObserver.observe(el);
    return () => renderObserver.disconnect();
  }, [isRendered]);

  // 2. Active Page Visibility Observer: track the truly active reading page
  useEffect(() => {
    const el = containerRef.current;
    if (!el || !onPageVisible) return;

    const pageObserver = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        if (entry.isIntersecting && entry.intersectionRatio >= 0.2) {
          onPageVisible(pageNumber);
        }
      },
      {
        threshold: [0.1, 0.2, 0.3, 0.5],
      }
    );

    pageObserver.observe(el);
    return () => pageObserver.disconnect();
  }, [pageNumber, onPageVisible]);

  // Unique task id for queue coordination
  const taskId = `page-${pageNumber}-z${zoomRatio}-r${rotationDeg}`;

  // 2. Render PDF Page on HTML5 Canvas via Concurrency-Controlled Render Queue
  useEffect(() => {
    if (!pdfDoc || !isVisible) {
      pdfRenderQueue.cancel(taskId);
      return;
    }

    let isCancelled = false;
    let cancelIdle: (() => void) | null = null;
    const priority = isCurrentPageRef.current
      ? 0
      : Math.abs(pageNumber - (currentPageNumberRef.current || pageNumber));

    const executeRender = async (setCancelHandler: (cancel: () => void) => void) => {
      try {
        const page: PDFPageProxy = await pdfDoc.getPage(pageNumber);
        if (isCancelled) return;

        const viewport = page.getViewport({
          scale: zoomRatio,
          rotation: rotationDeg,
        });

        const scaledWidth = Math.floor(viewport.width);
        const scaledHeight = Math.floor(viewport.height);
        setPageSize({ width: scaledWidth, height: scaledHeight });

        const canvas = canvasRef.current;
        if (!canvas || isCancelled) return;

        const ctx = canvas.getContext("2d", { alpha: false });
        if (!ctx) return;

        // Retina / High-DPI screen sharp scaling (clamped to max 2 for memory efficiency)
        const dpr = typeof window !== "undefined" ? Math.min(window.devicePixelRatio || 1, 2) : 1;
        const targetCanvasWidth = Math.floor(scaledWidth * dpr);
        const targetCanvasHeight = Math.floor(scaledHeight * dpr);

        // Guard against unnecessary canvas clearing: setting width/height wipes HTML5 canvas
        if (canvas.width !== targetCanvasWidth || canvas.height !== targetCanvasHeight) {
          canvas.width = targetCanvasWidth;
          canvas.height = targetCanvasHeight;
        }
        canvas.style.width = `${scaledWidth}px`;
        canvas.style.height = `${scaledHeight}px`;

        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

        const renderContext = {
          canvasContext: ctx,
          viewport: viewport,
          canvas: canvas,
        };

        const renderTask = page.render(renderContext);
        setCancelHandler(() => {
          try {
            renderTask.cancel();
          } catch {
            // ignore
          }
        });

        await renderTask.promise;
        if (isCancelled) return;

        setIsRendered(true);

        // Defer PDF Text Layer rendering to idle time to guarantee 60fps scrolling
        cancelIdle = runWhenIdle(async () => {
          if (isCancelled || !textLayerRef.current) return;
          try {
            textLayerRef.current.innerHTML = "";
            textLayerRef.current.style.width = `${scaledWidth}px`;
            textLayerRef.current.style.height = `${scaledHeight}px`;
            textLayerRef.current.style.setProperty("--scale-factor", `${viewport.scale}`);
            textLayerRef.current.style.setProperty("--total-scale-factor", `${viewport.scale}`);
            textLayerRef.current.style.setProperty("--user-unit", "1");

            const textContent = await page.getTextContent();
            if (!isCancelled && textLayerRef.current) {
              const textLayer = new pdfjsLib.TextLayer({
                textContentSource: textContent,
                container: textLayerRef.current,
                viewport: viewport,
              });
              await textLayer.render();
            }
          } catch {
            // Text layer failure is non-fatal
          }
        }, 120);
      } catch (err: unknown) {
        if ((err as { name?: string })?.name !== "RenderingCancelledException") {
          console.warn(`[PDF.js] Failed to render page ${pageNumber}:`, err);
        }
      }
    };

    pdfRenderQueue.enqueue(taskId, priority, executeRender).catch((err: unknown) => {
      if ((err as { name?: string })?.name !== "RenderingCancelledException") {
        console.warn(`[PDF.js] Queue error page ${pageNumber}:`, err);
      }
    });

    return () => {
      isCancelled = true;
      if (cancelIdle) cancelIdle();
      pdfRenderQueue.cancel(taskId);
    };
  }, [pdfDoc, pageNumber, zoomRatio, rotationDeg, isVisible, taskId]);

  // Estimate aspect ratio from fallback metadata if canvas not yet sized
  const aspectWidth = fallbackDimensions?.[0] || 595;
  const aspectHeight = fallbackDimensions?.[1] || 842;
  const estimatedWidth = Math.floor(aspectWidth * zoomRatio);
  const estimatedHeight = Math.floor(aspectHeight * zoomRatio);

  const containerWidth = pageSize?.width || estimatedWidth;
  const containerHeight = pageSize?.height || estimatedHeight;

  // Filter styles based on colorTheme
  const themeFilterClass = {
    default: "",
    dark: "invert-[0.92] hue-rotate-180 contrast-[1.12] brightness-[0.96]",
    sepia: "sepia-[0.35] contrast-[1.05] brightness-[0.98]",
    contrast: "contrast-[1.28] brightness-[0.96]",
  }[colorTheme];

  return (
    <div
      ref={containerRef}
      id={`pdf-page-${pageNumber}`}
      data-page-number={pageNumber}
      className={cn(
        "relative flex flex-col items-center select-none [contain:layout_paint] [will-change:transform] [transform:translateZ(0)] transition-all duration-150 shrink-0",
        readingMode === "two-page" ? "mx-0 my-0" : "mx-auto my-0",
        positionInSpread === "left" && "shadow-[2px_0_10px_rgba(0,0,0,0.08)]",
        positionInSpread === "right" && "shadow-[-2px_0_10px_rgba(0,0,0,0.08)]"
      )}
      style={{
        width: `${containerWidth}px`,
        minHeight: `${containerHeight}px`,
      }}
    >
      {/* Main Page Container */}
      <div
        className={cn(
          "page relative overflow-hidden select-none bg-white dark:bg-[#1a1917] sm:shadow-[0_2px_14px_rgba(0,0,0,0.06),0_1px_3px_rgba(0,0,0,0.03)] dark:sm:shadow-[0_4px_24px_rgba(0,0,0,0.5)] border-y sm:border border-[#ded8cc] dark:border-[#2f2b26] sm:rounded-xs transition-colors duration-150 shrink-0",
          themeFilterClass,
          positionInSpread === "left" && "rounded-r-none border-r-[#dfd8cc] dark:border-r-[#24211d]",
          positionInSpread === "right" && "rounded-l-none border-l-0"
        )}
        style={{
          width: `${containerWidth}px`,
          height: `${containerHeight}px`,
        }}
      >

        {/* HTML5 PDF.js Canvas */}
        <canvas
          ref={canvasRef}
          className="absolute inset-0 block pointer-events-none"
          style={{
            width: `${containerWidth}px`,
            height: `${containerHeight}px`,
          }}
        />

        {/* PDF.js Text Layer: Transparent selectable text layer on top of canvas */}
        <div
          ref={textLayerRef}
          className="textLayer absolute inset-0 select-text overflow-hidden opacity-100"
          style={{
            width: `${containerWidth}px`,
            height: `${containerHeight}px`,
          }}
        />

        {/* Spatial BoundingBox Highlight Layer for Visual Evidence Grounding */}
        <BboxHighlightLayer
          bbox={activeBbox}
          bboxes={activeBboxes}
          currentPage={pageNumber}
          onClear={onClearHighlight}
        />

        {/* Loading placeholder skeleton: only visible on initial page render, never flickers during scroll */}
        {!isRendered && (
          <div
            className="absolute inset-0 flex flex-col items-center justify-center bg-[#faf8f5]/90 dark:bg-[#1a1917]/90 backdrop-blur-2xs transition-opacity duration-200"
          >
            <div className="w-7 h-7 rounded-full border-2 border-primary/20 border-t-primary animate-spin mb-2" />
            <span className="text-[11px] font-mono text-muted animate-pulse">
              Đang kết xuất Trang {pageNumber}...
            </span>
          </div>
        )}
      </div>
    </div>
  );
});
