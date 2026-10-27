import { render } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { PdfPageCanvas } from "../components/PdfPageCanvas";
import type { PDFDocumentProxy, PDFPageProxy } from "pdfjs-dist";

// Mock pdfRenderQueue
vi.mock("../lib/pdfRenderQueue", () => ({
  pdfRenderQueue: {
    enqueue: vi.fn((_id, _priority, execute) => execute(vi.fn())),
    cancel: vi.fn(),
  },
  runWhenIdle: vi.fn((cb) => {
    cb();
    return vi.fn();
  }),
}));

// Mock pdfjs-init
vi.mock("../lib/pdfjs-init", () => ({
  pdfjsLib: {
    TextLayer: class {
      render = vi.fn().mockResolvedValue(undefined);
    },
  },
}));

// Mock IntersectionObserver in jsdom
class MockIntersectionObserver {
  callback: any;
  observe = vi.fn((_el) => {
    this.callback([{ isIntersecting: true, intersectionRatio: 1.0 }], this);
  });
  unobserve = vi.fn();
  disconnect = vi.fn();
  constructor(callback: any) {
    this.callback = callback;
  }
}
window.IntersectionObserver = MockIntersectionObserver as any;

// Mock Canvas getContext in jsdom
HTMLCanvasElement.prototype.getContext = vi.fn().mockReturnValue({
  setTransform: vi.fn(),
}) as any;

describe("PdfPageCanvas anti-flicker stability", () => {
  it("does not re-render or cancel canvas when currentPageNumber changes while scrolling", async () => {
    const { pdfRenderQueue } = await import("../lib/pdfRenderQueue");

    const mockRenderTask = {
      promise: Promise.resolve(),
      cancel: vi.fn(),
    };

    const mockPage: Partial<PDFPageProxy> = {
      getViewport: vi.fn().mockReturnValue({ width: 600, height: 800, scale: 1.0 }),
      render: vi.fn().mockReturnValue(mockRenderTask),
      getTextContent: vi.fn().mockResolvedValue({ items: [], styles: {} }),
    };

    const mockPdfDoc: Partial<PDFDocumentProxy> = {
      getPage: vi.fn().mockResolvedValue(mockPage as PDFPageProxy),
      numPages: 5,
    };

    // Initial render at page 1 with viewport at page 1
    const { rerender } = render(
      <PdfPageCanvas
        pdfDoc={mockPdfDoc as PDFDocumentProxy}
        pageNumber={1}
        zoomRatio={1.0}
        rotationDeg={0}
        activeBbox={null}
        isCurrentPage={true}
        currentPageNumber={1}
      />
    );

    // Clear mock after initial mount
    vi.mocked(pdfRenderQueue.cancel).mockClear();

    // Simulate page scrolling: currentPageNumber changes from 1 to 2
    rerender(
      <PdfPageCanvas
        pdfDoc={mockPdfDoc as PDFDocumentProxy}
        pageNumber={1}
        zoomRatio={1.0}
        rotationDeg={0}
        activeBbox={null}
        isCurrentPage={false}
        currentPageNumber={2}
      />
    );

    // Cancel must NOT have been called on page 1 when user scrolled to page 2
    expect(pdfRenderQueue.cancel).not.toHaveBeenCalledWith(expect.stringContaining("page-1"));
  });
});
