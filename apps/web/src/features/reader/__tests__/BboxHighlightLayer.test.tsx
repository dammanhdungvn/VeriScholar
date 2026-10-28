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
});
