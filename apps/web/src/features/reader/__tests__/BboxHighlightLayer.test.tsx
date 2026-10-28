import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { BboxHighlightLayer } from "../components/BboxHighlightLayer";
import type { BoundingBox } from "@/types/api";

describe("BboxHighlightLayer Component", () => {
  const mockBbox: BoundingBox = [0.1, 0.2, 0.5, 0.4, 1];

  it("renders with gold dashed border and amber styling on matching page", () => {
    render(<BboxHighlightLayer bbox={mockBbox} currentPage={1} isActive={true} />);
    const overlay = screen.getByTestId("grounded-bbox-overlay");
    expect(overlay).toBeInTheDocument();
    expect(overlay).toHaveClass("border-dashed");
    expect(overlay).toHaveClass("border-amber-500");
    expect(overlay.style.border).toContain("dashed");
    // jsdom normalizes hex #f59e0b to rgb(245, 158, 11)
    expect(
      overlay.style.border.includes("#f59e0b") ||
        overlay.style.border.includes("rgb(245, 158, 11)")
    ).toBe(true);
    expect(overlay.style.borderRadius).toBe("6px");
  });

  it("returns null when bbox is null or page does not match", () => {
    const { container: container1 } = render(
      <BboxHighlightLayer bbox={null} currentPage={1} />
    );
    expect(container1.firstChild).toBeNull();

    const { container: container2 } = render(
      <BboxHighlightLayer bbox={mockBbox} currentPage={2} />
    );
    expect(container2.firstChild).toBeNull();
  });

  it("renders multiple bounding boxes when bboxes array is provided on current page", () => {
    const multiBboxes: BoundingBox[] = [
      [0.1, 0.2, 0.4, 0.3, 1],
      [0.1, 0.32, 0.45, 0.42, 1],
      [0.1, 0.5, 0.4, 0.6, 2], // page 2, should not render on page 1
    ];

    render(<BboxHighlightLayer bboxes={multiBboxes} currentPage={1} isActive={true} />);
    const overlays = screen.getAllByTestId("grounded-bbox-overlay");
    expect(overlays).toHaveLength(2);
    expect(overlays[0]).toHaveClass("border-amber-500");
    expect(overlays[1]).toHaveClass("border-amber-500");
  });
});
