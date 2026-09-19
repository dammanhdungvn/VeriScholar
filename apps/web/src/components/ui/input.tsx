import * as React from "react";
import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  startIcon?: React.ReactNode;
  endIcon?: React.ReactNode;
  error?: boolean;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, startIcon, endIcon, error, ...props }, ref) => {
    return (
      <div className="relative flex items-center w-full">
        {startIcon && (
          <div className="absolute left-3.5 flex items-center justify-center pointer-events-none text-muted dark:text-[#9c988f]">
            {startIcon}
          </div>
        )}
        <input
          type={type}
          className={cn(
            "w-full h-10.5 px-3.5 text-sm font-sans rounded-lg transition-all duration-150",
            "bg-surface-soft/40 dark:bg-[#181613] text-ink dark:text-[#f5f3ed]",
            "border border-hairline dark:border-[#38332c] hover:border-zinc-300 dark:hover:border-[#484237]",
            "placeholder:text-muted/60 dark:placeholder:text-[#787369]",
            "focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 focus:bg-canvas dark:focus:bg-[#1c1a17]",
            "disabled:cursor-not-allowed disabled:opacity-60 disabled:bg-surface-soft dark:disabled:bg-[#1c1a17]",
            startIcon && "pl-10",
            endIcon && "pr-10",
            error && "border-error focus:border-error focus:ring-error/20 dark:border-error",
            className
          )}
          ref={ref}
          {...props}
        />
        {endIcon && (
          <div className="absolute right-3.5 flex items-center justify-center text-muted dark:text-[#9c988f]">
            {endIcon}
          </div>
        )}
      </div>
    );
  }
);
Input.displayName = "Input";
