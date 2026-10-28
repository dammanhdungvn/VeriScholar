import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { BboxHighlightLayer } from "../components/BboxHighlightLayer";
import type { BoundingBox } from "@/types/api";

describe("PdfCanvasViewer Scroll Trap & Dismiss Controls", () => {
  const mockBbox: BoundingBox = [0.1, 0.2, 0.5, 0.4, 1];

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
});
