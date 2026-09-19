import type { BoundingBox, PageDimensions } from "@/types/api";

export interface ComputedBoxStyle {
  left: string;
  top: string;
  width: string;
  height: string;
}

/**
 * Dynamic Viewport Matrix Scaling:
 * Converts normalized coordinate [x0, y0, x1, y1, page] into percentage CSS styles.
 * Ensures 100% invariant alignment under zoom, split-pane resize, and responsive layouts.
 */
export function computeBoundingBoxStyle(
  bbox: BoundingBox,
  _dimensions?: PageDimensions
): ComputedBoxStyle {
  const [x0, y0, x1, y1] = bbox;

  // Spatial Bounds Guard
  const clampedX0 = Math.max(0, Math.min(x0, 1));
  const clampedY0 = Math.max(0, Math.min(y0, 1));
  const clampedX1 = Math.max(clampedX0, Math.min(x1, 1));
  const clampedY1 = Math.max(clampedY0, Math.min(y1, 1));

  return {
    left: `${(clampedX0 * 100).toFixed(2)}%`,
    top: `${(clampedY0 * 100).toFixed(2)}%`,
    width: `${((clampedX1 - clampedX0) * 100).toFixed(2)}%`,
    height: `${((clampedY1 - clampedY0) * 100).toFixed(2)}%`,
  };
}
