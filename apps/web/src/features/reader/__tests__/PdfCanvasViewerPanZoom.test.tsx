import { render, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeAll } from "vitest";
import { PdfCanvasViewer } from "../components/PdfCanvasViewer";

// Mock IntersectionObserver in jsdom
class MockIntersectionObserver {
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
}
beforeAll(() => {
  window.IntersectionObserver = MockIntersectionObserver as unknown as typeof IntersectionObserver;
  globalThis.IntersectionObserver = MockIntersectionObserver as unknown as typeof IntersectionObserver;
});

vi.mock("@/features/reader/lib/pdfjs-init", () => ({}));
vi.mock("../lib/pdfRenderQueue", () => ({
  pdfRenderQueue: {
    enqueue: vi.fn((_id, _priority, execute) => execute(vi.fn())),
    cancel: vi.fn(),
  },
  getCachedPdfDocument: vi.fn().mockResolvedValue({
    numPages: 5,
    getPage: vi.fn().mockResolvedValue({
      getViewport: vi.fn().mockReturnValue({ width: 600, height: 800 }),
      render: vi.fn().mockReturnValue({ promise: Promise.resolve() }),
      getTextContent: vi.fn().mockResolvedValue({ items: [] }),
    }),
  }),
  clearCachedPdfDocument: vi.fn(),
  runWhenIdle: vi.fn((cb) => {
    cb();
    return vi.fn();
  }),
}));

describe("PdfCanvasViewer Pan & Zoom Container", () => {
  it("uses min-w-fit w-fit mx-auto to prevent flex horizontal clipping", async () => {
    const { container } = render(
      <PdfCanvasViewer
        documentId="doc-test"
        fileUrl="https://example.com/test.pdf"
        currentPage={1}
        zoomRatio={1.5}
        rotationDeg={0}
        activeBbox={null}
      />
    );

    await waitFor(() => {
      const pagesContainer = container.querySelector(".min-w-fit.w-fit.mx-auto");
      expect(pagesContainer).toBeInTheDocument();
    });
  });

  it("applies paper-scrollbar on scroll container when effectiveZoom > 1.0", async () => {
    const { container } = render(
      <PdfCanvasViewer
        documentId="doc-test"
        fileUrl="https://example.com/test.pdf"
        currentPage={1}
        zoomRatio={1.5}
        rotationDeg={0}
        activeBbox={null}
      />
    );

    await waitFor(() => {
      const scrollContainer = container.querySelector(".paper-scrollbar");
      expect(scrollContainer).toBeInTheDocument();
    });
  });

  it("applies scrollbar-none when effectiveZoom <= 1.0", async () => {
    const { container } = render(
      <PdfCanvasViewer
        documentId="doc-test"
        fileUrl="https://example.com/test.pdf"
        currentPage={1}
        zoomRatio={1.0}
        rotationDeg={0}
        activeBbox={null}
      />
    );

    await waitFor(() => {
      const scrollContainer = container.querySelector(".scrollbar-none");
      expect(scrollContainer).toBeInTheDocument();
    });
  });
});
