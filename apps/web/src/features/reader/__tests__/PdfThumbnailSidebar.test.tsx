import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { PdfThumbnailSidebar } from "../components/PdfThumbnailSidebar";

describe("PdfThumbnailSidebar Dual-Mode (Thumbnails & Outline)", () => {
  it("toggles between thumbnail and outline view modes in PDF sidebar", async () => {
    const mockGetOutline = vi.fn().mockResolvedValue([
      { title: "1. Introduction", dest: 1, items: [] },
      { title: "2. Methodology", dest: 5, items: [] },
    ]);
    const mockPdfDoc = {
      getOutline: mockGetOutline,
      getPage: vi.fn().mockResolvedValue({
        getViewport: vi.fn().mockReturnValue({ width: 100, height: 140 }),
        render: vi.fn().mockReturnValue({ promise: Promise.resolve(), cancel: vi.fn() }),
      }),
      getDestination: vi.fn(),
      getPageIndex: vi.fn(),
    } as any;

    const onSelectPage = vi.fn();

    render(
      <PdfThumbnailSidebar
        isOpen={true}
        onClose={vi.fn()}
        totalPages={10}
        currentPage={1}
        onSelectPage={onSelectPage}
        pdfDoc={mockPdfDoc}
      />
    );

    // Initial view is thumbnails
    expect(screen.getByText("Trang 1")).toBeInTheDocument();

    // Toggle to Outline mode
    const outlineTab = screen.getByRole("tab", { name: /Mục lục/i });
    fireEvent.click(outlineTab);

    // Should fetch and display outline items
    expect(await screen.findByText("1. Introduction")).toBeInTheDocument();
    expect(screen.getByText("2. Methodology")).toBeInTheDocument();

    // Click an outline item
    fireEvent.click(screen.getByText("2. Methodology"));
    expect(onSelectPage).toHaveBeenCalledWith(5);
  });

  it("displays fallback message when PDF has no embedded outline", async () => {
    const mockGetOutline = vi.fn().mockResolvedValue(null);
    const mockPdfDoc = {
      getOutline: mockGetOutline,
      getPage: vi.fn().mockResolvedValue({
        getViewport: vi.fn().mockReturnValue({ width: 100, height: 140 }),
        render: vi.fn().mockReturnValue({ promise: Promise.resolve(), cancel: vi.fn() }),
      }),
    } as any;

    render(
      <PdfThumbnailSidebar
        isOpen={true}
        onClose={vi.fn()}
        totalPages={10}
        currentPage={1}
        onSelectPage={vi.fn()}
        pdfDoc={mockPdfDoc}
      />
    );

    const outlineTab = screen.getByRole("tab", { name: /Mục lục/i });
    fireEvent.click(outlineTab);

    expect(
      await screen.findByText(/Tài liệu này không có mục lục nhúng/i)
    ).toBeInTheDocument();
  });
});
