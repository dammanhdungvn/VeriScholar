import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cn } from "@/lib/utils";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean;
  variant?: "primary" | "secondary" | "secondary-dark" | "ghost" | "icon" | "coral-inverted";
  size?: "sm" | "md" | "lg" | "icon";
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";

    const variantStyles = {
      primary:
        "bg-primary hover:bg-primary-active active:bg-primary-active text-on-primary font-medium transition-colors shadow-xs disabled:bg-primary-disabled disabled:text-muted disabled:cursor-not-allowed",
      secondary:
        "bg-canvas hover:bg-surface-soft active:bg-surface-card text-ink border border-hairline font-medium transition-colors disabled:opacity-50",
      "secondary-dark":
        "bg-surface-dark-elevated hover:bg-[#2e2c28] text-on-dark font-medium border border-[#383632] transition-colors disabled:opacity-50",
      ghost:
        "bg-transparent hover:bg-surface-soft active:bg-surface-card text-ink font-medium transition-colors",
      icon:
        "w-9 h-9 p-0 rounded-full flex items-center justify-center border border-hairline bg-canvas hover:bg-surface-soft text-ink transition-colors",
      "coral-inverted":
        "bg-canvas hover:bg-surface-soft text-ink font-medium shadow-xs transition-colors",
    };

    const sizeStyles = {
      sm: "h-8 px-3 text-xs rounded-md",
      md: "h-10 px-5 text-sm rounded-md",
      lg: "h-12 px-7 text-base rounded-md",
      icon: "h-9 w-9 p-0 rounded-full",
    };

    return (
      <Comp
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center gap-2 font-sans select-none outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 cursor-pointer transition-all",
          variantStyles[variant],
          size !== "icon" && sizeStyles[size],
          className
        )}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";
