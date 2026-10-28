import { render } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { PdfPageCanvas } from "../components/PdfPageCanvas";

// Mock IntersectionObserver in jsdom
class MockIntersectionObserver {
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
}
window.IntersectionObserver = MockIntersectionObserver as any;

describe("PdfPageCanvas Zoom Bounding Box Scale", () => {
  it("does NOT clamp container or page to maxWidth: 100% when zoom > 1.0", () => {
    const { container } = render(
      <PdfPageCanvas
        pageNumber={1}
        zoomRatio={1.5}
        rotationDeg={0}
        fallbackDimensions={[600, 800]}
      />
    );

    const pageWrapper = container.querySelector("#pdf-page-1") as HTMLElement;
    const pageDiv = container.querySelector(".page") as HTMLElement;

    // Zoom 1.5 of 600px width = 900px
    expect(pageWrapper.style.width).toBe("900px");
    expect(pageWrapper.style.maxWidth).toBeFalsy();
    expect(pageDiv.style.width).toBe("900px");
    expect(pageDiv.style.maxWidth).toBeFalsy();
  });
});
