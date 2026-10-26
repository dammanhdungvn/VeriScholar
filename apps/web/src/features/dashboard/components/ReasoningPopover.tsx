import { useEffect, useRef, useState, useCallback } from "react";
import { RotateCcw, ChevronRight } from "lucide-react";
import {
  useDashboardStore,
  type ReasoningEffortLevel,
} from "../stores/useDashboardStore";

interface ReasoningPopoverProps {
  isOpen: boolean;
  onClose: () => void;
}

const EFFORT_LEVELS: Array<{
  id: ReasoningEffortLevel;
  label: string;
  percent: number;
}> = [
  { id: "light", label: "Light", percent: 0 },
  { id: "medium", label: "Medium", percent: 33.33 },
  { id: "high", label: "High", percent: 66.66 },
  { id: "extra_high", label: "Extra High", percent: 100 },
];

export function ReasoningPopover({ isOpen, onClose }: ReasoningPopoverProps) {
  const popoverRef = useRef<HTMLDivElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const reasoningEffort = useDashboardStore((s) => s.reasoningEffort);
  const selectedModel = useDashboardStore((s) => s.selectedModel);
  const setReasoningEffort = useDashboardStore((s) => s.setReasoningEffort);
  const resetReasoningEffort = useDashboardStore((s) => s.resetReasoningEffort);

  // Close on Escape or click outside
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };

    const handleClickOutside = (e: MouseEvent) => {
      if (
        popoverRef.current &&
        !popoverRef.current.contains(e.target as Node)
      ) {
        onClose();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen, onClose]);

  const updateLevelFromPointer = useCallback(
    (clientX: number) => {
      if (!trackRef.current) return;
      const rect = trackRef.current.getBoundingClientRect();
      const width = rect.width > 0 ? rect.width : 240;
      const relativeX = clientX - rect.left;
      const ratio = Math.max(0, Math.min(1, relativeX / width));
      const stepIndex = Math.round(ratio * 3);
      const clampedIndex = isNaN(stepIndex) ? 0 : Math.max(0, Math.min(3, stepIndex));
      if (EFFORT_LEVELS[clampedIndex]) {
        setReasoningEffort(EFFORT_LEVELS[clampedIndex].id);
      }
    },
    [setReasoningEffort]
  );

  const handlePointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    setIsDragging(true);
    try {
      e.currentTarget.setPointerCapture(e.pointerId);
    } catch {
      // Ignore if unsupported in jsdom
    }
    updateLevelFromPointer(e.clientX);
  };

  const handlePointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!isDragging) return;
    updateLevelFromPointer(e.clientX);
  };

  const handlePointerUp = (e: React.PointerEvent<HTMLDivElement>) => {
    if (isDragging) {
      setIsDragging(false);
      try {
        e.currentTarget.releasePointerCapture(e.pointerId);
      } catch {
        // Ignore if already released
      }
    }
  };

  if (!isOpen) return null;

  const currentLevelConfig =
    EFFORT_LEVELS.find((l) => l.id === reasoningEffort) || EFFORT_LEVELS[0];
  const activePercent = currentLevelConfig.percent;

  const getDisplayLabel = (effort: ReasoningEffortLevel) => {
    switch (effort) {
      case "light":
      case "off":
        return "Light";
      case "low":
      case "medium":
        return "Medium";
      case "high":
        return "High";
      case "extra_high":
        return "Extra High";
      default:
        return "Light";
    }
  };

  return (
    <div
      ref={popoverRef}
      role="dialog"
      aria-label="Cài đặt mức độ suy luận 5.6 Luna"
      className="absolute bottom-full mb-3 right-0 z-40 w-64 p-4 rounded-2xl bg-[#212120] text-white border border-[#38342e] shadow-[0_12px_36px_rgba(0,0,0,0.5)] select-none animate-in fade-in zoom-in-95 duration-150"
    >
      {/* Header: Level Label + Reset Button */}
      <div className="flex items-center justify-between mb-0.5">
        <div className="w-4" /> {/* Spacer */}
        <span
          data-testid="reasoning-effort-label"
          className={`text-sm font-medium tracking-wide ${
            reasoningEffort === "light" || reasoningEffort === "off"
              ? "text-zinc-400"
              : "text-sky-400"
          }`}
        >
          {getDisplayLabel(reasoningEffort)}
        </span>
        <button
          type="button"
          onClick={resetReasoningEffort}
          data-testid="reasoning-reset-btn"
          title="Khôi phục mặc định (Light)"
          aria-label="Khôi phục mặc định"
          className="text-zinc-400 hover:text-white p-1 rounded-full hover:bg-white/10 transition-colors cursor-pointer"
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Model Name Subtitle */}
      <div className="flex items-center justify-center gap-0.5 text-xs text-zinc-400 mb-4 cursor-default">
        <span>{selectedModel}</span>
        <ChevronRight className="w-3 h-3 opacity-70" />
      </div>

      {/* Stepped Interactive Slider Track with Mouse Drag Support (Rule Item 7) */}
      <div
        ref={trackRef}
        data-testid="reasoning-slider"
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerCancel={handlePointerUp}
        onMouseDown={handlePointerDown as unknown as React.MouseEventHandler<HTMLDivElement>}
        onMouseMove={handlePointerMove as unknown as React.MouseEventHandler<HTMLDivElement>}
        onMouseUp={handlePointerUp as unknown as React.MouseEventHandler<HTMLDivElement>}
        className="relative px-2 py-3 cursor-ew-resize touch-none select-none"
      >
        {/* Inactive Track */}
        <div className="relative w-full h-2 rounded-full bg-zinc-700/80 overflow-hidden">
          {/* Active Highlight Track */}
          <div
            className="h-full bg-sky-500 transition-all duration-150"
            style={{ width: `${activePercent}%` }}
          />
        </div>

        {/* 4 Clickable Step Dots */}
        <div className="absolute inset-x-2 top-1/2 -translate-y-1/2 flex justify-between pointer-events-none">
          {EFFORT_LEVELS.map((step) => {
            const isPassed = step.percent <= activePercent;
            return (
              <span
                key={step.id}
                className={`w-1.5 h-1.5 rounded-full transition-colors ${
                  isPassed ? "bg-white" : "bg-zinc-400/80"
                }`}
              />
            );
          })}
        </div>

        {/* Draggable/Animated Thumb */}
        <div
          className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-4.5 h-4.5 rounded-full bg-white shadow-md pointer-events-none transition-all duration-150"
          style={{ left: `calc(8px + (100% - 16px) * ${activePercent / 100})` }}
        />

        {/* Click targets for the 4 steps */}
        <div className="absolute inset-0 flex">
          {EFFORT_LEVELS.map((step) => (
            <button
              key={step.id}
              type="button"
              data-testid={`reasoning-step-${step.id}`}
              onClick={(e) => {
                e.stopPropagation();
                setReasoningEffort(step.id);
              }}
              aria-label={`Đặt mức suy luận: ${step.label}`}
              className="flex-1 h-full cursor-pointer focus:outline-none"
            />
          ))}
        </div>
      </div>
    </div>
  );
}
