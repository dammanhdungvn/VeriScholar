import { describe, it, expect } from "vitest";
import { calculateSelectionBoundingBox } from "../lib/selection-bbox";
import type { BoundingBox } from "@/types/api";

describe("calculateSelectionBoundingBox", () => {
  it("calculates tight normalized bounding box from client rects without bleeding across column gutter", () => {
    // Mock page element (width: 800, height: 1000)
    const mockPageEl = {
      getBoundingClientRect: () => ({
        left: 100,
        top: 50,
        right: 900,
        bottom: 1050,
        width: 800,
        height: 1000,
      }),
      querySelector: () => null,
    } as unknown as HTMLElement;

    // Mock Range with 3 lines selected in left column (x: 150 to 450, within page left=100)
    const mockRects = [
      { left: 164, top: 250, right: 480, bottom: 270, width: 316, height: 20 },
      { left: 164, top: 275, right: 480, bottom: 295, width: 316, height: 20 },
      { left: 164, top: 300, right: 400, bottom: 320, width: 236, height: 20 },
    ];

    const mockRange = {
      getClientRects: () => mockRects as unknown as DOMRectList,
      getBoundingClientRect: () => ({
        left: 164,
        top: 250,
        right: 480,
        bottom: 320,
        width: 316,
        height: 70,
      }),
    } as unknown as Range;

    const bbox: BoundingBox | null = calculateSelectionBoundingBox(mockRange, mockPageEl, 1);

    expect(bbox).not.toBeNull();
    if (bbox) {
      // Normalized to page:
      // x0 = (164 - 100) / 800 = 64 / 800 = 0.08
      // x1 = (480 - 100) / 800 = 380 / 800 = 0.475
      // y0 = (250 - 50) / 1000 = 200 / 1000 = 0.20
      // y1 = (320 - 50) / 1000 = 270 / 1000 = 0.27
      // page = 1
      expect(bbox[0]).toBeCloseTo(0.08, 2);
      expect(bbox[1]).toBeCloseTo(0.20, 2);
      expect(bbox[2]).toBeCloseTo(0.475, 2);
      expect(bbox[3]).toBeCloseTo(0.27, 2);
      expect(bbox[4]).toBe(1);
      // Ensure it stays strictly inside the left half of the page (< 0.50)
      expect(bbox[2]).toBeLessThanOrEqual(0.50);
    }
  });

  it("handles zero client rects gracefully by falling back to getBoundingClientRect", () => {
    const mockPageEl = {
      getBoundingClientRect: () => ({
        left: 0,
        top: 0,
        right: 1000,
        bottom: 1000,
        width: 1000,
        height: 1000,
      }),
      querySelector: () => null,
    } as unknown as HTMLElement;

    const mockRange = {
      getClientRects: () => [] as unknown as DOMRectList,
      getBoundingClientRect: () => ({
        left: 100,
        top: 200,
        right: 400,
        bottom: 500,
        width: 300,
        height: 300,
      }),
    } as unknown as Range;

    const bbox = calculateSelectionBoundingBox(mockRange, mockPageEl, 2);
    expect(bbox).toEqual([0.1, 0.2, 0.4, 0.5, 2]);
  });
});
