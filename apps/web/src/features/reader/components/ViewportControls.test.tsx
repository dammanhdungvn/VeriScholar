import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ViewportControls } from "./ViewportControls";

describe("ViewportControls Component", () => {
  it("renders page info and zoom percentage", () => {
    render(
      <ViewportControls
        currentPage={4}
        totalPages={12}
        zoomRatio={1.25}
        onPageChange={vi.fn()}
        onZoomIn={vi.fn()}
        onZoomOut={vi.fn()}
        onResetZoom={vi.fn()}
        onRotate={vi.fn()}
      />
    );

    expect(screen.getByText("4")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
    expect(screen.getByText("125%")).toBeInTheDocument();
  });

  it("handles page forward and backward clicks", () => {
    const onPage = vi.fn();
    render(
      <ViewportControls
        currentPage={4}
        totalPages={12}
        zoomRatio={1.0}
        onPageChange={onPage}
        onZoomIn={vi.fn()}
        onZoomOut={vi.fn()}
        onResetZoom={vi.fn()}
        onRotate={vi.fn()}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: /trang trước/i }));
    expect(onPage).toHaveBeenCalledWith(3);

    fireEvent.click(screen.getByRole("button", { name: /trang tiếp theo/i }));
    expect(onPage).toHaveBeenCalledWith(5);
  });

  it("handles zoom controls", () => {
    const onZoomIn = vi.fn();
    const onZoomOut = vi.fn();
    const onReset = vi.fn();

    render(
      <ViewportControls
        currentPage={1}
        totalPages={10}
        zoomRatio={1.0}
        onPageChange={vi.fn()}
        onZoomIn={onZoomIn}
        onZoomOut={onZoomOut}
        onResetZoom={onReset}
        onRotate={vi.fn()}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: /phóng to/i }));
    expect(onZoomIn).toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: /thu nhỏ/i }));
    expect(onZoomOut).toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: /đặt lại kích thước/i }));
    expect(onReset).toHaveBeenCalled();
  });

  it("handles onExportPdf action through options menu", () => {
    const onExport = vi.fn();
    render(
      <ViewportControls
        currentPage={1}
        totalPages={10}
        zoomRatio={1.0}
        onPageChange={vi.fn()}
        onZoomIn={vi.fn()}
        onZoomOut={vi.fn()}
        onResetZoom={vi.fn()}
        onRotate={vi.fn()}
        onExportPdf={onExport}
      />
    );

    // Open options menu
    const overflowBtn = screen.getByTestId("viewport-overflow-menu-btn");
    fireEvent.click(overflowBtn);

    const exportBtn = screen.getByTestId("overflow-export-pdf-btn");
    expect(exportBtn).toBeInTheDocument();
    fireEvent.click(exportBtn);
    expect(onExport).toHaveBeenCalledTimes(1);
  });

  it("handles onToggleZenPdf button click for Zen reading mode directly on toolbar", () => {
    const onToggleZen = vi.fn();
    render(
      <ViewportControls
        currentPage={1}
        totalPages={10}
        zoomRatio={1.0}
        onPageChange={vi.fn()}
        onZoomIn={vi.fn()}
        onZoomOut={vi.fn()}
        onResetZoom={vi.fn()}
        onRotate={vi.fn()}
        isZenPdf={false}
        onToggleZenPdf={onToggleZen}
      />
    );

    const zenBtn = screen.getByTestId("zen-pdf-btn");
    expect(zenBtn).toBeInTheDocument();
    expect(zenBtn).toHaveTextContent(/Zen PDF/i);
    fireEvent.click(zenBtn);
    expect(onToggleZen).toHaveBeenCalledTimes(1);
  });

  it("handles onOpenReferences action through options menu", () => {
    const onOpenRefs = vi.fn();
    render(
      <ViewportControls
        currentPage={1}
        totalPages={10}
        zoomRatio={1.0}
        onPageChange={vi.fn()}
        onZoomIn={vi.fn()}
        onZoomOut={vi.fn()}
        onResetZoom={vi.fn()}
        onRotate={vi.fn()}
        onOpenReferences={onOpenRefs}
      />
    );

    const overflowBtn = screen.getByTestId("viewport-overflow-menu-btn");
    fireEvent.click(overflowBtn);

    const openRefsBtn = screen.getByTestId("overflow-open-references-btn");
    expect(openRefsBtn).toBeInTheDocument();
    expect(openRefsBtn).toHaveTextContent(/Trích xuất Tài liệu Tham khảo/i);
    fireEvent.click(openRefsBtn);
    expect(onOpenRefs).toHaveBeenCalledTimes(1);
  });

  it("renders overflow menu button when in compact/overflow mode", () => {
    render(
      <ViewportControls
        currentPage={1}
        totalPages={10}
        zoomRatio={1.0}
        onPageChange={vi.fn()}
        onZoomIn={vi.fn()}
        onZoomOut={vi.fn()}
        onResetZoom={vi.fn()}
        onRotate={vi.fn()}
      />
    );

    const overflowBtn = screen.getByTestId("viewport-overflow-menu-btn");
    expect(overflowBtn).toBeInTheDocument();
    expect(overflowBtn).toHaveTextContent(/Tùy chọn/i);
    expect(screen.queryByTestId("viewport-overflow-popover")).not.toBeInTheDocument();
  });

  it("opens popover menu on click and handles reading mode selection", () => {
    const onReadingModeChange = vi.fn();
    render(
      <ViewportControls
        currentPage={1}
        totalPages={10}
        zoomRatio={1.0}
        onPageChange={vi.fn()}
        onZoomIn={vi.fn()}
        onZoomOut={vi.fn()}
        onResetZoom={vi.fn()}
        onRotate={vi.fn()}
        readingMode="continuous"
        onReadingModeChange={onReadingModeChange}
      />
    );

    const overflowBtn = screen.getByTestId("viewport-overflow-menu-btn");
    fireEvent.click(overflowBtn);

    const popover = screen.getByTestId("viewport-overflow-popover");
    expect(popover).toBeInTheDocument();

    const singleBtn = screen.getByTestId("overflow-reading-mode-single");
    fireEvent.click(singleBtn);
    expect(onReadingModeChange).toHaveBeenCalledWith("single");
  });

  it("handles action items in overflow popover menu", () => {
    const onOpenRefs = vi.fn();
    const onExport = vi.fn();
    const onToggleZen = vi.fn();

    render(
      <ViewportControls
        currentPage={1}
        totalPages={10}
        zoomRatio={1.0}
        onPageChange={vi.fn()}
        onZoomIn={vi.fn()}
        onZoomOut={vi.fn()}
        onResetZoom={vi.fn()}
        onRotate={vi.fn()}
        onOpenReferences={onOpenRefs}
        onExportPdf={onExport}
        onToggleZenPdf={onToggleZen}
      />
    );

    const overflowBtn = screen.getByTestId("viewport-overflow-menu-btn");
    fireEvent.click(overflowBtn);

    const refsBtn = screen.getByTestId("overflow-open-references-btn");
    fireEvent.click(refsBtn);
    expect(onOpenRefs).toHaveBeenCalledTimes(1);
    expect(screen.queryByTestId("viewport-overflow-popover")).not.toBeInTheDocument();

    // Reopen and test export
    fireEvent.click(overflowBtn);
    const exportBtn = screen.getByTestId("overflow-export-pdf-btn");
    fireEvent.click(exportBtn);
    expect(onExport).toHaveBeenCalledTimes(1);

    // Reopen and test zen
    fireEvent.click(overflowBtn);
    const zenBtn = screen.getByTestId("overflow-zen-pdf-btn");
    fireEvent.click(zenBtn);
    expect(onToggleZen).toHaveBeenCalledTimes(1);
  });

  it("closes popover on Escape key", () => {
    render(
      <ViewportControls
        currentPage={1}
        totalPages={10}
        zoomRatio={1.0}
        onPageChange={vi.fn()}
        onZoomIn={vi.fn()}
        onZoomOut={vi.fn()}
        onResetZoom={vi.fn()}
        onRotate={vi.fn()}
      />
    );

    const overflowBtn = screen.getByTestId("viewport-overflow-menu-btn");
    fireEvent.click(overflowBtn);
    expect(screen.getByTestId("viewport-overflow-popover")).toBeInTheDocument();

    fireEvent.keyDown(window, { key: "Escape" });
    expect(screen.queryByTestId("viewport-overflow-popover")).not.toBeInTheDocument();
  });

  it("handles reading mode selection from the inline toolbar dropdown", () => {
    const onReadingModeChange = vi.fn();
    render(
      <ViewportControls
        currentPage={1}
        totalPages={10}
        zoomRatio={1.0}
        onPageChange={vi.fn()}
        onZoomIn={vi.fn()}
        onZoomOut={vi.fn()}
        onResetZoom={vi.fn()}
        onRotate={vi.fn()}
        readingMode="continuous"
        onReadingModeChange={onReadingModeChange}
      />
    );

    const modeBtn = screen.getByTestId("reading-mode-dropdown-btn");
    expect(modeBtn).toHaveTextContent("Cuộn");

    fireEvent.click(modeBtn);
    expect(screen.getByTestId("reading-mode-menu-popover")).toBeInTheDocument();

    const twoPageOpt = screen.getByTestId("mode-opt-two-page");
    fireEvent.click(twoPageOpt);

    expect(onReadingModeChange).toHaveBeenCalledWith("two-page");
    expect(screen.queryByTestId("reading-mode-menu-popover")).not.toBeInTheDocument();
  });
});
