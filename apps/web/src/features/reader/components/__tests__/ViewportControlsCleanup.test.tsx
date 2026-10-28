import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ViewportControls } from "../ViewportControls";
import { ViewportOverflowMenu } from "../ViewportOverflowMenu";

describe("Viewport Controls and Overflow Menu Cleanup", () => {
  it("does not render Zen PDF or Mode View buttons in ViewportControls", () => {
    render(
      <ViewportControls
        currentPage={1}
        totalPages={15}
        zoomRatio={1}
        onPageChange={vi.fn()}
        onZoomIn={vi.fn()}
        onZoomOut={vi.fn()}
        onResetZoom={vi.fn()}
        onRotate={vi.fn()}
      />
    );

    // Zen PDF button must be removed from toolbar
    expect(screen.queryByTestId("zen-pdf-btn")).toBeNull();
    expect(screen.queryByText(/Zen PDF/i)).toBeNull();

    // Mode View button must be removed from toolbar
    expect(screen.queryByTestId("reading-mode-dropdown-btn")).toBeNull();
  });

  it("renders Sổ ghi chú in ViewportOverflowMenu and removes mode view and Zen PDF", () => {
    const handleOpenNotes = vi.fn();
    const handleClose = vi.fn();

    render(
      <ViewportOverflowMenu
        isOpen={true}
        onClose={handleClose}
        activeReadingMode="continuous"
        onReadingModeChange={vi.fn()}
        onOpenNotes={handleOpenNotes}
      />
    );

    // Mode view section must NOT be rendered in Tùy chọn menu
    expect(screen.queryByText("Chế độ đọc")).toBeNull();
    expect(screen.queryByTestId("overflow-reading-mode-continuous")).toBeNull();
    expect(screen.queryByTestId("overflow-reading-mode-single")).toBeNull();
    expect(screen.queryByTestId("overflow-reading-mode-two-page")).toBeNull();

    // Zen PDF must NOT be rendered in Tùy chọn menu
    expect(screen.queryByTestId("overflow-zen-pdf-btn")).toBeNull();
    expect(screen.queryByText(/Đọc tập trung \(Zen PDF\)/i)).toBeNull();

    // "Sổ ghi chú" MUST be rendered in Tùy chọn menu
    const notesBtn = screen.getByTestId("overflow-open-notes-btn");
    expect(notesBtn).toBeDefined();
    expect(screen.getByText("Sổ ghi chú")).toBeDefined();

    fireEvent.click(notesBtn);
    expect(handleOpenNotes).toHaveBeenCalledTimes(1);
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it("renders save bookmark option inside Tùy chọn overflow menu", () => {
    const handleToggleBookmark = vi.fn();
    const handleClose = vi.fn();

    render(
      <ViewportOverflowMenu
        isOpen={true}
        onClose={handleClose}
        isBookmarked={false}
        onToggleBookmark={handleToggleBookmark}
      />
    );

    const bookmarkBtn = screen.getByTestId("overflow-toggle-bookmark-btn");
    expect(bookmarkBtn).toBeInTheDocument();
    expect(bookmarkBtn).toHaveTextContent("Lưu vào kho yêu thích");

    fireEvent.click(bookmarkBtn);
    expect(handleToggleBookmark).toHaveBeenCalledTimes(1);
    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});
