import type { BoundingBox } from "@/types/api";

/**
 * Calculates a normalized BoundingBox [x0, y0, x1, y1, page] for a text selection
 * relative to the target PDF page element.
 *
 * Uses `range.getClientRects()` to inspect individual line fragments rather than
 * relying solely on `range.getBoundingClientRect()`, ensuring accurate bounding
 * that respects multi-line column text boundaries without extraneous gutter bleeding.
 */
export function calculateSelectionBoundingBox(
  range: Range,
  targetPageEl: HTMLElement,
  detectedPage: number
): BoundingBox | null {
  if (!range || !targetPageEl) {
    return null;
  }

  const innerPage =
    targetPageEl.querySelector<HTMLElement>(".textLayer")?.parentElement ||
    targetPageEl.querySelector<HTMLElement>("canvas")?.parentElement ||
    targetPageEl;

  const pageRect = innerPage.getBoundingClientRect();
  if (pageRect.width <= 0 || pageRect.height <= 0) {
    return null;
  }

  // Extract individual line rects from range
  const clientRects = Array.from(range.getClientRects?.() ?? []).filter(
    (r) => r.width > 0 && r.height > 0
  );

  let minLeft: number;
  let minTop: number;
  let maxRight: number;
  let maxBottom: number;

  if (clientRects.length > 0) {
    minLeft = Math.min(...clientRects.map((r) => r.left));
    minTop = Math.min(...clientRects.map((r) => r.top));
    maxRight = Math.max(...clientRects.map((r) => r.right));
    maxBottom = Math.max(...clientRects.map((r) => r.bottom));
  } else {
    // Fallback to bounding client rect if getClientRects is empty
    const bounding = range.getBoundingClientRect();
    if (!bounding || (bounding.width === 0 && bounding.height === 0)) {
      return null;
    }
    minLeft = bounding.left;
    minTop = bounding.top;
    maxRight = bounding.right;
    maxBottom = bounding.bottom;
  }

  // Normalize coordinates relative to inner page dimensions [0..1]
  const rawX0 = (minLeft - pageRect.left) / pageRect.width;
  const rawY0 = (minTop - pageRect.top) / pageRect.height;
  const rawX1 = (maxRight - pageRect.left) / pageRect.width;
  const rawY1 = (maxBottom - pageRect.top) / pageRect.height;

  const x0 = Number(Math.max(0, Math.min(1, rawX0)).toFixed(4));
  const y0 = Number(Math.max(0, Math.min(1, rawY0)).toFixed(4));
  const x1 = Number(Math.max(x0, Math.min(1, rawX1)).toFixed(4));
  const y1 = Number(Math.max(y0, Math.min(1, rawY1)).toFixed(4));
  const normalizedPage = Math.max(1, detectedPage);

  return [x0, y0, x1, y1, normalizedPage];
}
