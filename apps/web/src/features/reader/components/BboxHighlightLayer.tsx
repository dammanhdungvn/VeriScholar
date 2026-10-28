import { computeBoundingBoxStyle } from "@/lib/bounding-box-scaler";
import type { BoundingBox } from "@/types/api";
import { cn } from "@/lib/utils";

interface BboxHighlightLayerProps {
  bbox?: BoundingBox | null;
  bboxes?: BoundingBox[] | null;
  currentPage: number;
  isActive?: boolean;
  label?: string;
  onClear?: () => void;
}

export function BboxHighlightLayer({
  bbox,
  bboxes,
  currentPage,
  isActive = true,
  label,
  onClear: _onClear,
}: BboxHighlightLayerProps) {
  // Collect all boxes that apply to the current page
  const resolvedBoxes: BoundingBox[] = [];

  if (bboxes && bboxes.length > 0) {
    for (const b of bboxes) {
      if (b && b[4] === currentPage) {
        resolvedBoxes.push(b);
      }
    }
  } else if (bbox && bbox[4] === currentPage) {
    resolvedBoxes.push(bbox);
  }

  if (resolvedBoxes.length === 0) return null;

  return (
    <>
      {resolvedBoxes.map((box, index) => {
        const style = computeBoundingBoxStyle(box);
        return (
          <div
            key={`${box[0]}-${box[1]}-${box[2]}-${box[3]}-${index}`}
            role="region"
            data-testid="grounded-bbox-overlay"
            aria-label={label || `Đoạn trích dẫn bằng chứng tại trang ${box[4]}`}
            style={{
              ...style,
              border: "2px dashed #f59e0b",
              backgroundColor: "rgba(245, 158, 11, 0.12)",
              borderRadius: "6px",
            }}
            className={cn(
              "absolute pointer-events-none transition-all duration-300 z-20",
              "border-2 border-dashed border-amber-500 bg-amber-500/15 rounded-md",
              isActive &&
                "border-2 border-dashed border-amber-500 bg-amber-500/20 ring-2 ring-amber-400/50 shadow-md animate-pulse"
            )}
          />
        );
      })}
    </>
  );
}
