import { computeBoundingBoxStyle } from "@/lib/bounding-box-scaler";
import type { BoundingBox } from "@/types/api";
import { cn } from "@/lib/utils";

interface BboxHighlightLayerProps {
  bbox: BoundingBox | null;
  currentPage: number;
  isActive?: boolean;
  label?: string;
  onClear?: () => void;
}

export function BboxHighlightLayer({
  bbox,
  currentPage,
  isActive = true,
  label,
  onClear: _onClear,
}: BboxHighlightLayerProps) {
  if (!bbox) return null;

  const page = bbox[4];
  if (page !== currentPage) return null;

  const style = computeBoundingBoxStyle(bbox);

  return (
    <div
      role="region"
      data-testid="grounded-bbox-overlay"
      aria-label={label || `Đoạn trích dẫn bằng chứng tại trang ${page}`}
      style={{
        ...style,
        border: "2px dashed #f59e0b",
        backgroundColor: "rgba(245, 158, 11, 0.12)",
        borderRadius: "6px",
      }}
      className={cn(
        "absolute pointer-events-none transition-all duration-300 z-20",
        "border-2 border-dashed border-amber-500 bg-amber-500/15 rounded-md",
        isActive && "border-2 border-dashed border-amber-500 bg-amber-500/20 ring-2 ring-amber-400/50 shadow-md animate-pulse"
      )}
    />
  );
}
