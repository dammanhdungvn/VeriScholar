import * as React from "react";
import { Check } from "lucide-react";
import { cn } from "@/lib/utils";

export interface CheckboxProps {
  id?: string;
  checked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
  disabled?: boolean;
  className?: string;
  "aria-label"?: string;
  "aria-describedby"?: string;
}

export const Checkbox = React.forwardRef<HTMLButtonElement, CheckboxProps>(
  ({ id, checked = false, onCheckedChange, disabled = false, className, ...props }, ref) => {
    return (
      <button
        type="button"
        role="checkbox"
        id={id}
        ref={ref}
        aria-checked={checked}
        disabled={disabled}
        onClick={() => !disabled && onCheckedChange?.(!checked)}
        onKeyDown={(e) => {
          if (e.key === " " || e.key === "Enter") {
            e.preventDefault();
            if (!disabled) onCheckedChange?.(!checked);
          }
        }}
        className={cn(
          "w-4.5 h-4.5 rounded-sm border flex items-center justify-center transition-all cursor-pointer select-none",
          "focus:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2",
          checked
            ? "bg-primary border-primary text-on-primary shadow-xs"
            : "bg-canvas dark:bg-[#201e1b] border-hairline dark:border-[#38332c] hover:border-muted-soft text-transparent",
          disabled && "opacity-50 cursor-not-allowed",
          className
        )}
        {...props}
      >
        <Check className={cn("w-3.5 h-3.5 stroke-[2.5]", checked ? "opacity-100" : "opacity-0")} />
      </button>
    );
  }
);
Checkbox.displayName = "Checkbox";
