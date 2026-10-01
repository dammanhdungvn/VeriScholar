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
  onClear,
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
      style={style}
      className={cn(
        "absolute rounded-xs pointer-events-none transition-all duration-300 z-10",
        "border-[1.5px] border-accent-amber/90 bg-accent-amber/15 shadow-2xs",
        isActive && "border-primary bg-primary/20 animate-pulse ring-1 ring-primary/40"
      )}
    >
      {/* Visual Badge for Citation Position */}
      <div className="absolute -top-5 left-0 flex items-center gap-1 pointer-events-auto">
        <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-[10px] font-mono font-medium tracking-tight bg-primary text-white shadow-xs">
          Tr. {page}
        </span>
        {onClear && (
          <button
            type="button"
            onClick={onClear}
            className="w-4 h-4 rounded-full bg-black/60 hover:bg-black text-white flex items-center justify-center text-[10px]"
            aria-label="Xóa viền highlight"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
}
