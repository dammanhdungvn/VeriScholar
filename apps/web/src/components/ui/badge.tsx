import * as React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "coral" | "amber" | "outline" | "dark";
}

export function Badge({
  className,
  variant = "default",
  ...props
}: BadgeProps) {
  const variantStyles = {
    default: "bg-surface-card text-ink border border-hairline",
    coral: "bg-primary text-on-primary font-medium tracking-wide uppercase",
    amber: "bg-[#fcf3e6] text-[#b36b1e] border border-[#f0d5b2] font-medium",
    outline: "bg-transparent text-muted border border-hairline font-medium",
    dark: "bg-surface-dark-elevated text-on-dark border border-[#383632]",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-sans select-none transition-colors",
        variantStyles[variant],
        className
      )}
      {...props}
    />
  );
}
