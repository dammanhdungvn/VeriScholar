import { describe, it, expect } from "vitest";
import { computeBoundingBoxStyle } from "./bounding-box-scaler";
import type { BoundingBox } from "@/types/api";

describe("computeBoundingBoxStyle", () => {
  it("computes percentage styles accurately for normalized valid coordinates", () => {
    const bbox: BoundingBox = [0.1, 0.2, 0.8, 0.5, 1];
    const style = computeBoundingBoxStyle(bbox);

    expect(style.left).toBe("10.00%");
    expect(style.top).toBe("20.00%");
    expect(style.width).toBe("70.00%");
    expect(style.height).toBe("30.00%");
  });

  it("clamps out-of-bound negative coordinates to 0%", () => {
    const bbox: BoundingBox = [-0.1, -0.05, 0.5, 0.6, 1];
    const style = computeBoundingBoxStyle(bbox);

    expect(style.left).toBe("0.00%");
    expect(style.top).toBe("0.00%");
    expect(style.width).toBe("50.00%");
    expect(style.height).toBe("60.00%");
  });

  it("clamps coordinates exceeding 1.0 safely", () => {
    const bbox: BoundingBox = [0.5, 0.6, 1.5, 1.2, 2];
    const style = computeBoundingBoxStyle(bbox);

    expect(style.left).toBe("50.00%");
    expect(style.top).toBe("60.00%");
    expect(style.width).toBe("50.00%");
    expect(style.height).toBe("40.00%");
  });

  it("handles reversed coordinates safely without negative dimensions", () => {
    const bbox: BoundingBox = [0.8, 0.5, 0.2, 0.1, 1];
    const style = computeBoundingBoxStyle(bbox);

    // Clamped x1 is at least clamped x0
    expect(parseFloat(style.width)).toBeGreaterThanOrEqual(0);
    expect(parseFloat(style.height)).toBeGreaterThanOrEqual(0);
  });
});
