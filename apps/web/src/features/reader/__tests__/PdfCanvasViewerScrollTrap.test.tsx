import { render, screen, fireEvent, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { BboxHighlightLayer } from "../components/BboxHighlightLayer";
import { PdfCanvasViewer } from "../components/PdfCanvasViewer";
import { useDashboardStore } from "@/features/dashboard/stores/useDashboardStore";
import type { BoundingBox } from "@/types/api";

// Mock pdfRenderQueue and getCachedPdfDocument
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

vi.mock("../lib/pdfjs-init", () => ({
  pdfjsLib: {
    TextLayer: class {
      render = vi.fn().mockResolvedValue(undefined);
    },
  },
}));

describe("PdfCanvasViewer Scroll Trap & Dismiss Controls", () => {
  const mockBbox: BoundingBox = [0.1, 0.2, 0.5, 0.4, 1];

  beforeEach(() => {
    vi.clearAllMocks();
    useDashboardStore.getState().setActiveBbox(null);
  });

  it("renders a dismiss button when onClear is passed and calls onClear on click", () => {
    const handleClear = vi.fn();
    render(
      <BboxHighlightLayer
        bbox={mockBbox}
        currentPage={1}
        isActive={true}
        onClear={handleClear}
      />
    );

    const dismissButton = screen.getByRole("button", { name: /đóng khung trích dẫn/i });
    expect(dismissButton).toBeInTheDocument();

    fireEvent.click(dismissButton);
    expect(handleClear).toHaveBeenCalledTimes(1);
  });

  it("does not render a dismiss button when onClear is not provided", () => {
    render(<BboxHighlightLayer bbox={mockBbox} currentPage={1} isActive={true} />);
    const dismissButton = screen.queryByRole("button", { name: /đóng khung trích dẫn/i });
    expect(dismissButton).not.toBeInTheDocument();
  });

  it("clears active bbox when pressing Escape key in PdfCanvasViewer", () => {
    const handleClearHighlight = vi.fn();
    useDashboardStore.getState().setActiveBbox(mockBbox);

    const { unmount } = render(
      <PdfCanvasViewer
        documentId="doc-test-1"
        fileUrl="/test.pdf"
        currentPage={1}
        zoomRatio={1.0}
        rotationDeg={0}
        activeBbox={mockBbox}
        onClearHighlight={handleClearHighlight}
      />
    );

    expect(useDashboardStore.getState().activeBbox).toEqual(mockBbox);

    // Fire Escape key event on window
    act(() => {
      window.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));
    });

    expect(handleClearHighlight).toHaveBeenCalledTimes(1);
    expect(useDashboardStore.getState().activeBbox).toBeNull();

    unmount();
  });

  it("does not snap scroll back to active bbox when user navigates/scrolls to subsequent pages", async () => {
    // Set up mock DOM elements for scroll container and target page
    const pageEl = document.createElement("div");
    pageEl.id = "pdf-page-1";
    document.body.appendChild(pageEl);

    const scrollToMock = vi.fn();
    Element.prototype.scrollTo = scrollToMock;

    useDashboardStore.getState().setActiveBbox(mockBbox);

    const { rerender, unmount } = render(
      <PdfCanvasViewer
        documentId="doc-test-1"
        fileUrl="/test.pdf"
        currentPage={1}
        zoomRatio={1.0}
        rotationDeg={0}
        activeBbox={mockBbox}
      />
    );

    // Initial render may schedule scroll to active bbox
    const initialCallCount = scrollToMock.mock.calls.length;

    // Simulate user scrolling down to page 2 and page 3 with the same activeBbox still present
    rerender(
      <PdfCanvasViewer
        documentId="doc-test-1"
        fileUrl="/test.pdf"
        currentPage={2}
        zoomRatio={1.0}
        rotationDeg={0}
        activeBbox={mockBbox}
      />
    );

    rerender(
      <PdfCanvasViewer
        documentId="doc-test-1"
        fileUrl="/test.pdf"
        currentPage={3}
        zoomRatio={1.0}
        rotationDeg={0}
        activeBbox={mockBbox}
      />
    );

    // scrollTo should NOT be invoked again because lastScrolledBboxKeyRef holds the active key
    expect(scrollToMock.mock.calls.length).toBe(initialCallCount);

    unmount();
    document.body.removeChild(pageEl);
  });
});
