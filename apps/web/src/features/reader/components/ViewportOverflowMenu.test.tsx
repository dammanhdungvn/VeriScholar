import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ViewportOverflowMenu } from "./ViewportOverflowMenu";

describe("ViewportOverflowMenu Component", () => {
  it("renders nothing when isOpen is false", () => {
    const { container } = render(
      <ViewportOverflowMenu
        isOpen={false}
        onClose={vi.fn()}
        activeReadingMode="continuous"
        onReadingModeChange={vi.fn()}
      />
    );
    expect(container.firstChild).toBeNull();
  });

  it("renders menu items when isOpen is true", () => {
    render(
      <ViewportOverflowMenu
        isOpen={true}
        onClose={vi.fn()}
        activeReadingMode="continuous"
        onReadingModeChange={vi.fn()}
      />
    );

    expect(screen.getByRole("menu")).toBeInTheDocument();
    expect(screen.getByTestId("overflow-reading-mode-continuous")).toBeInTheDocument();
    expect(screen.getByTestId("overflow-reading-mode-single")).toBeInTheDocument();
    expect(screen.getByTestId("overflow-reading-mode-two-page")).toBeInTheDocument();
  });

  it("handles reading mode selection", () => {
    const onReadingModeChange = vi.fn();
    render(
      <ViewportOverflowMenu
        isOpen={true}
        onClose={vi.fn()}
        activeReadingMode="continuous"
        onReadingModeChange={onReadingModeChange}
      />
    );

    fireEvent.click(screen.getByTestId("overflow-reading-mode-single"));
    expect(onReadingModeChange).toHaveBeenCalledWith("single");
  });

  it("renders zoom and rotation controls when showZoomControls is true", () => {
    const onZoomIn = vi.fn();
    const onZoomOut = vi.fn();
    const onResetZoom = vi.fn();
    const onRotate = vi.fn();

    render(
      <ViewportOverflowMenu
        isOpen={true}
        onClose={vi.fn()}
        activeReadingMode="continuous"
        onReadingModeChange={vi.fn()}
        showZoomControls={true}
        zoomRatio={1.5}
        onZoomIn={onZoomIn}
        onZoomOut={onZoomOut}
        onResetZoom={onResetZoom}
        onRotate={onRotate}
      />
    );

    expect(screen.getByText("150%")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Phóng to" }));
    expect(onZoomIn).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByRole("button", { name: "Thu nhỏ" }));
    expect(onZoomOut).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByRole("button", { name: "Đặt lại kích thước 100%" }));
    expect(onResetZoom).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByRole("button", { name: "Xoay 90 độ" }));
    expect(onRotate).toHaveBeenCalledTimes(1);
  });

  it("handles supplementary actions: references, export, zen mode", () => {
    const onClose = vi.fn();
    const onOpenReferences = vi.fn();
    const onExportPdf = vi.fn();
    const onToggleZenPdf = vi.fn();

    render(
      <ViewportOverflowMenu
        isOpen={true}
        onClose={onClose}
        activeReadingMode="continuous"
        onReadingModeChange={vi.fn()}
        onOpenReferences={onOpenReferences}
        onExportPdf={onExportPdf}
        onToggleZenPdf={onToggleZenPdf}
        isZenPdf={false}
      />
    );

    fireEvent.click(screen.getByTestId("overflow-open-references-btn"));
    expect(onClose).toHaveBeenCalled();
    expect(onOpenReferences).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByTestId("overflow-export-pdf-btn"));
    expect(onExportPdf).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByTestId("overflow-zen-pdf-btn"));
    expect(onToggleZenPdf).toHaveBeenCalledTimes(1);
  });

  it("does not render zoom or reading modes on mobile phone when showReadingModes is false", () => {
    render(
      <ViewportOverflowMenu
        isOpen={true}
        onClose={vi.fn()}
        activeReadingMode="continuous"
        onReadingModeChange={vi.fn()}
        showZoomControls={false}
        showReadingModes={false}
        onOpenReferences={vi.fn()}
        onExportPdf={vi.fn()}
      />
    );

    // Header has short title
    expect(screen.getByText("Tùy chọn")).toBeInTheDocument();
    expect(screen.queryByText("Tùy chọn hiển thị & Công cụ")).toBeNull();

    // No zoom or reload controls
    expect(screen.queryByText(/Thu phóng & Xoay/i)).toBeNull();
    expect(screen.queryByRole("button", { name: "Phóng to" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Xoay 90 độ" })).toBeNull();

    // No reading/view modes
    expect(screen.queryByText("Chế độ đọc")).toBeNull();
    expect(screen.queryByTestId("overflow-reading-mode-continuous")).toBeNull();

    // Still renders essential tools
    expect(screen.getByText("Công cụ")).toBeInTheDocument();
    expect(screen.getByTestId("overflow-open-references-btn")).toBeInTheDocument();
    expect(screen.getByTestId("overflow-export-pdf-btn")).toBeInTheDocument();
  });
});
