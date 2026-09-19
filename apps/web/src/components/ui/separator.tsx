import * as React from "react";
import { cn } from "@/lib/utils";

export interface SeparatorProps extends React.HTMLAttributes<HTMLDivElement> {
  label?: string;
  orientation?: "horizontal" | "vertical";
}

export const Separator = React.forwardRef<HTMLDivElement, SeparatorProps>(
  ({ className, label, orientation = "horizontal", ...props }, ref) => {
    if (label && orientation === "horizontal") {
      return (
        <div ref={ref} className={cn("relative flex items-center justify-center my-5 w-full", className)} {...props}>
          <div className="grow border-t border-hairline dark:border-[#332f28]" />
          <span className="px-3 text-xs font-sans text-muted-soft dark:text-[#807b71] uppercase tracking-wider select-none">
            {label}
          </span>
          <div className="grow border-t border-hairline dark:border-[#332f28]" />
        </div>
      );
    }

    return (
      <div
        ref={ref}
        role="separator"
        aria-orientation={orientation}
        className={cn(
          orientation === "horizontal"
            ? "w-full border-t border-hairline dark:border-[#332f28] my-4"
            : "h-full border-l border-hairline dark:border-[#332f28] mx-4",
          className
        )}
        {...props}
      />
    );
  }
);
Separator.displayName = "Separator";
