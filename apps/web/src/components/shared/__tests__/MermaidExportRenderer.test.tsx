import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { MermaidRenderer } from "../MermaidRenderer";

// Mock mermaid library
vi.mock("mermaid", () => ({
  default: {
    initialize: vi.fn(),
    render: vi.fn().mockImplementation((id: string) =>
      Promise.resolve({
        svg: `<svg id="${id}" width="400" height="300" viewBox="0 0 400 300"><g><text>Test Mermaid Diagram</text></g></svg>`,
      })
    ),
  },
}));

describe("MermaidExportRenderer", () => {
  const sampleChart = `graph TD\n  A[Bắt đầu] --> B[Xử lý]\n  B --> C[Kết quả]`;
  let originalImage: typeof Image;
  let clickedAnchors: { download: string; href: string }[] = [];

  beforeEach(() => {
    clickedAnchors = [];

    // Spy on anchor click
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(function (this: HTMLAnchorElement) {
      clickedAnchors.push({
        download: this.download,
        href: this.href,
      });
    });

    // Mock URL object methods
    if (!window.URL.createObjectURL) {
      window.URL.createObjectURL = vi.fn();
    }
    if (!window.URL.revokeObjectURL) {
      window.URL.revokeObjectURL = vi.fn();
    }
    vi.spyOn(window.URL, "createObjectURL").mockImplementation((blob: Blob | MediaSource) => {
      return `blob:mock-url-${blob instanceof Blob ? blob.type : "source"}`;
    });
    vi.spyOn(window.URL, "revokeObjectURL").mockImplementation(() => {});

    // Mock Canvas 2D Context
    HTMLCanvasElement.prototype.getContext = vi.fn().mockReturnValue({
      fillRect: vi.fn(),
      drawImage: vi.fn(),
    }) as any;
    HTMLCanvasElement.prototype.toDataURL = vi.fn().mockReturnValue("data:image/png;base64,mockPngData");

    // Mock Image to simulate image loading
    originalImage = window.Image;
    class MockImage {
      private _src = "";
      onload: (() => void) | null = null;
      onerror: (() => void) | null = null;
      naturalWidth = 400;
      naturalHeight = 300;

      get src() {
        return this._src;
      }
      set src(value: string) {
        this._src = value;
        setTimeout(() => {
          if (this.onload) {
            this.onload();
          }
        }, 10);
      }
    }
    window.Image = MockImage as any;

    // Mock clipboard
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
    window.Image = originalImage;
  });

  it("renders diagram container and SVG output", async () => {
    render(<MermaidRenderer chart={sampleChart} />);

    const container = screen.getByTestId("mermaid-diagram-container");
    expect(container).toBeInTheDocument();

    await waitFor(() => {
      expect(container.querySelector("svg")).not.toBeNull();
    });
    expect(container.textContent).toContain("Sơ đồ kiến trúc & Mindmap");
  });

  it("renders 'Tải SVG' button (data-testid='download-svg-btn') and clicking it triggers SVG download", async () => {
    render(<MermaidRenderer chart={sampleChart} />);

    // Wait for SVG render
    await waitFor(() => {
      expect(screen.getByTestId("mermaid-diagram-container").querySelector("svg")).not.toBeNull();
    });

    const downloadSvgBtn = screen.getByTestId("download-svg-btn");
    expect(downloadSvgBtn).toBeInTheDocument();
    expect(downloadSvgBtn.textContent).toContain("Tải SVG");

    fireEvent.click(downloadSvgBtn);

    expect(window.URL.createObjectURL).toHaveBeenCalled();
    expect(clickedAnchors.length).toBeGreaterThan(0);
    const lastAnchor = clickedAnchors[clickedAnchors.length - 1];
    expect(lastAnchor.download).toBe("diagram.svg");
    expect(lastAnchor.href).toContain("blob:mock-url-image/svg+xml");
  });

  it("renders 'Tải PNG' button (data-testid='download-png-btn') and clicking it triggers PNG export", async () => {
    render(<MermaidRenderer chart={sampleChart} />);

    await waitFor(() => {
      expect(screen.getByTestId("mermaid-diagram-container").querySelector("svg")).not.toBeNull();
    });

    const downloadPngBtn = screen.getByTestId("download-png-btn");
    expect(downloadPngBtn).toBeInTheDocument();
    expect(downloadPngBtn.textContent).toContain("Tải PNG");

    fireEvent.click(downloadPngBtn);

    await waitFor(() => {
      const pngAnchor = clickedAnchors.find((a) => a.download === "diagram.png");
      expect(pngAnchor).toBeDefined();
      expect(pngAnchor?.href).toBe("data:image/png;base64,mockPngData");
    });
  });

  it("'Sao chép mã' copies Mermaid syntax to clipboard and displays copied feedback", async () => {
    render(<MermaidRenderer chart={sampleChart} />);

    const copyBtn = screen.getByTestId("copy-mermaid-btn");
    expect(copyBtn).toBeInTheDocument();
    expect(copyBtn.textContent).toContain("Sao chép mã");

    fireEvent.click(copyBtn);

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(sampleChart);
    expect(await screen.findByText("Đã chép")).toBeInTheDocument();
  });

  it("instantly serves cached SVG on re-render without blanking", async () => {
    const chartCode = "graph TD\n  A --> B";
    const { unmount } = render(<MermaidRenderer chart={chartCode} />);
    await waitFor(() => {
      expect(screen.getByText("Test Mermaid Diagram")).toBeInTheDocument();
    });
    unmount();

    // Mount again with identical chart code: cached SVG should be rendered synchronously on initial render
    const { container } = render(<MermaidRenderer chart={chartCode} />);
    expect(container.querySelector("svg")).not.toBeNull();
    expect(screen.getByText("Test Mermaid Diagram")).toBeInTheDocument();
  });
});
