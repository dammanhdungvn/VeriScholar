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

  it("handles onExportPdf button click", () => {
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

    const exportBtn = screen.getByRole("button", { name: /Xuất PDF/i });
    expect(exportBtn).toBeInTheDocument();
    fireEvent.click(exportBtn);
    expect(onExport).toHaveBeenCalledTimes(1);
  });

  it("handles onToggleZenPdf button click for Zen reading mode", () => {
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
});
