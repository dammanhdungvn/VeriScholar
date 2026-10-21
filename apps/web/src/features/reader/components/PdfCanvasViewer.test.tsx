import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, act, fireEvent } from "@testing-library/react";
import { PdfCanvasViewer } from "./PdfCanvasViewer";
import * as pdfRenderQueue from "../lib/pdfRenderQueue";
import { useReaderStore } from "../stores/useReaderStore";

vi.mock("./PdfPageCanvas", () => ({
  PdfPageCanvas: ({ pageNumber, zoomRatio }: { pageNumber: number; zoomRatio: number }) => (
    <div id={`pdf-page-${pageNumber}`} data-testid="pdf-page-canvas" data-zoom-ratio={zoomRatio}>
      Page {pageNumber}
      <div data-testid="grounded-bbox-overlay">Bounding Box</div>
    </div>
  ),
}));

vi.mock("./PdfThumbnailSidebar", () => ({
  PdfThumbnailSidebar: () => <div data-testid="pdf-thumbnail-sidebar">Thumbnails</div>,
}));

vi.mock("./ScholarSelectionMenu", () => ({
  ScholarSelectionMenu: () => <div data-testid="scholar-selection-menu">Menu</div>,
}));

describe("PdfCanvasViewer", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    useReaderStore.getState().resetReader();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  it("renders loading skeleton initially while document is being fetched", () => {
    vi.spyOn(pdfRenderQueue, "getCachedPdfDocument").mockReturnValue(
      new Promise(() => {}) // never resolves
    );

    render(
      <PdfCanvasViewer
        documentId="doc-1"
        fileUrl="https://example.com/test.pdf"
        currentPage={1}
        zoomRatio={1}
        rotationDeg={0}
        activeBbox={null}
      />
    );

    expect(screen.getByText("Đang nạp bài báo khoa học...")).toBeInTheDocument();
    expect(
      screen.getByText(/Phân giải cao & trích xuất tầng văn bản/i)
    ).toBeInTheDocument();
  });

  it("triggers 12s timeout error guard when document load hangs", async () => {
    vi.spyOn(pdfRenderQueue, "getCachedPdfDocument").mockReturnValue(
      new Promise(() => {}) // hangs forever
    );

    render(
      <PdfCanvasViewer
        documentId="doc-1"
        fileUrl="https://example.com/test.pdf"
        currentPage={1}
        zoomRatio={1}
        rotationDeg={0}
        activeBbox={null}
      />
    );

    // Fast-forward by 12 seconds
    act(() => {
      vi.advanceTimersByTime(12000);
    });

    expect(screen.getByText("Không thể kết xuất tài liệu PDF")).toBeInTheDocument();
    expect(
      screen.getByText(/Đã quá thời gian nạp tài liệu PDF \(12s\)/i)
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Thử tải lại/i })).toBeInTheDocument();
  });

  it("retries loading when clicking Thử tải lại button", async () => {
    const clearSpy = vi.spyOn(pdfRenderQueue, "clearCachedPdfDocument").mockImplementation(() => {});
    const getCachedSpy = vi
      .spyOn(pdfRenderQueue, "getCachedPdfDocument")
      .mockReturnValue(new Promise(() => {}));

    render(
      <PdfCanvasViewer
        documentId="doc-1"
        fileUrl="https://example.com/test.pdf"
        currentPage={1}
        zoomRatio={1}
        rotationDeg={0}
        activeBbox={null}
      />
    );

    // Trigger timeout
    act(() => {
      vi.advanceTimersByTime(12000);
    });

    const retryBtn = screen.getByRole("button", { name: /Thử tải lại/i });
    expect(retryBtn).toBeInTheDocument();

    // Click retry
    act(() => {
      fireEvent.click(retryBtn);
    });

    expect(clearSpy).toHaveBeenCalledWith("https://example.com/test.pdf");
    expect(getCachedSpy).toHaveBeenCalledTimes(2);
  });

  it("renders page canvases when document loads successfully in responsive mode", async () => {
    const mockDoc = {
      numPages: 2,
    };
    vi.spyOn(pdfRenderQueue, "getCachedPdfDocument").mockResolvedValue(
      mockDoc as unknown as Awaited<ReturnType<typeof pdfRenderQueue.getCachedPdfDocument>>
    );

    const onPageCount = vi.fn();
    render(
      <PdfCanvasViewer
        documentId="doc-1"
        fileUrl="https://example.com/test.pdf"
        currentPage={1}
        zoomRatio={1}
        rotationDeg={0}
        activeBbox={null}
        onPageCountDetected={onPageCount}
      />
    );

    await act(async () => {
      await Promise.resolve();
    });

    expect(onPageCount).toHaveBeenCalledWith(2);
    const canvases = screen.getAllByTestId("pdf-page-canvas");
    expect(canvases).toHaveLength(2);
  });

  it("smooth-scrolls into view and centers on bounding box when activeBbox is selected", async () => {
    const mockDoc = {
      numPages: 3,
    };
    vi.spyOn(pdfRenderQueue, "getCachedPdfDocument").mockResolvedValue(
      mockDoc as unknown as Awaited<ReturnType<typeof pdfRenderQueue.getCachedPdfDocument>>
    );

    const scrollIntoViewMock = vi.fn();
    window.HTMLElement.prototype.scrollIntoView = scrollIntoViewMock;

    render(
      <PdfCanvasViewer
        documentId="doc-1"
        fileUrl="https://example.com/test.pdf"
        currentPage={1}
        zoomRatio={1}
        rotationDeg={0}
        activeBbox={[0.1, 0.2, 0.8, 0.5, 2]}
      />
    );

    await act(async () => {
      await Promise.resolve();
    });

    expect(scrollIntoViewMock).toHaveBeenCalled();
  });

  it("attaches ResizeObserver to scrollContainer and auto-fits Edge-to-Edge without small scale fallback", async () => {
    const mockDoc = {
      numPages: 1,
    };
    vi.spyOn(pdfRenderQueue, "getCachedPdfDocument").mockResolvedValue(
      mockDoc as unknown as Awaited<ReturnType<typeof pdfRenderQueue.getCachedPdfDocument>>
    );

    let observedElement: Element | null = null;
    let observerCallback: ResizeObserverCallback | null = null;

    class MockResizeObserver {
      constructor(callback: ResizeObserverCallback) {
        observerCallback = callback;
      }
      observe(el: Element) {
        observedElement = el;
      }
      unobserve() {}
      disconnect() {}
    }
    window.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver;

    // Simulate 1090px wide desktop container
    const originalClientWidth = Object.getOwnPropertyDescriptor(
      HTMLElement.prototype,
      "clientWidth"
    );
    Object.defineProperty(HTMLElement.prototype, "clientWidth", {
      configurable: true,
      get() {
        return 1090;
      },
    });

    render(
      <PdfCanvasViewer
        documentId="doc-1"
        fileUrl="https://example.com/test.pdf"
        currentPage={1}
        zoomRatio={1}
        rotationDeg={0}
        activeBbox={null}
      />
    );

    await act(async () => {
      await Promise.resolve();
    });

    // Verify ResizeObserver is attached to the scroll container
    expect(observedElement).not.toBeNull();
    expect(observedElement).toHaveClass("overflow-y-auto");

    // Check rendered canvas zoom ratio:
    // available = 1090 - 20 = 1070
    // standard = 595.32
    // scale = (1070 / 595.32) = ~1.797
    const canvas = screen.getByTestId("pdf-page-canvas");
    const zoomRatioAttr = canvas.getAttribute("data-zoom-ratio");
    expect(Number(zoomRatioAttr)).toBeCloseTo(1.797, 2);

    // Now simulate window resize or split-pane drag to 800px:
    act(() => {
      if (observerCallback && observedElement) {
        observerCallback(
          [
            {
              target: observedElement,
              contentRect: { width: 800 } as DOMRectReadOnly,
            } as ResizeObserverEntry,
          ],
          {} as ResizeObserver
        );
      }
      vi.runAllTimers();
    });

    // available = 800 - 20 = 780
    // scale = 780 / 595.32 = ~1.310
    const updatedZoom = screen.getByTestId("pdf-page-canvas").getAttribute("data-zoom-ratio");
    expect(Number(updatedZoom)).toBeCloseTo(1.31, 2);

    if (originalClientWidth) {
      Object.defineProperty(HTMLElement.prototype, "clientWidth", originalClientWidth);
    }
  });

  it("auto-hides floating pagination HUD after 5s and reveals on hover or mousemove in single page mode", async () => {
    useReaderStore.getState().setReadingMode("single");
    const mockDoc = {
      numPages: 5,
    };
    vi.spyOn(pdfRenderQueue, "getCachedPdfDocument").mockResolvedValue(
      mockDoc as unknown as Awaited<ReturnType<typeof pdfRenderQueue.getCachedPdfDocument>>
    );

    const { container } = render(
      <PdfCanvasViewer
        documentId="doc-1"
        fileUrl="https://example.com/test.pdf"
        currentPage={1}
        zoomRatio={1}
        rotationDeg={0}
        activeBbox={null}
      />
    );

    await act(async () => {
      await Promise.resolve();
    });

    const hud = screen.getByTestId("floating-pagination-hud");
    expect(hud).toBeInTheDocument();
    expect(hud).toHaveTextContent("Trang 1 / 5");
    expect(hud).toHaveClass("opacity-100");
    expect(hud).toHaveClass("pointer-events-auto");

    // Advance 5 seconds: HUD should transition to hidden
    act(() => {
      vi.advanceTimersByTime(5000);
    });

    expect(hud).toHaveClass("opacity-0");
    expect(hud).toHaveClass("pointer-events-none");

    // Moving mouse in scroll container wakes HUD up
    const scrollContainer = container.querySelector(".overflow-y-auto");
    expect(scrollContainer).not.toBeNull();
    act(() => {
      fireEvent.mouseMove(scrollContainer!);
    });

    expect(hud).toHaveClass("opacity-100");
    expect(hud).toHaveClass("pointer-events-auto");

    // Hover directly on HUD keeps it permanently visible (does not hide after 5s)
    act(() => {
      fireEvent.mouseEnter(hud);
    });
    act(() => {
      vi.advanceTimersByTime(10000);
    });
    expect(hud).toHaveClass("opacity-100");

    // Leave HUD: starts 5s countdown
    act(() => {
      fireEvent.mouseLeave(hud);
    });
    act(() => {
      vi.advanceTimersByTime(5000);
    });
    expect(hud).toHaveClass("opacity-0");
  });

  it("manages floating pagination HUD auto-hide in two-page spread mode", async () => {
    useReaderStore.getState().setReadingMode("two-page");
    const mockDoc = {
      numPages: 10,
    };
    vi.spyOn(pdfRenderQueue, "getCachedPdfDocument").mockResolvedValue(
      mockDoc as unknown as Awaited<ReturnType<typeof pdfRenderQueue.getCachedPdfDocument>>
    );

    render(
      <PdfCanvasViewer
        documentId="doc-1"
        fileUrl="https://example.com/test.pdf"
        currentPage={1}
        zoomRatio={1}
        rotationDeg={0}
        activeBbox={null}
      />
    );

    await act(async () => {
      await Promise.resolve();
    });

    const hud = screen.getByTestId("floating-pagination-hud");
    expect(hud).toBeInTheDocument();
    expect(hud).toHaveTextContent("Trang 1 - 2 / 10");
    expect(hud).toHaveClass("opacity-100");

    // Auto-hide after 5s
    act(() => {
      vi.advanceTimersByTime(5000);
    });
    expect(hud).toHaveClass("opacity-0");
  });
});
