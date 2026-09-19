import * as React from "react";
import { cn } from "@/lib/utils";

export interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  required?: boolean;
}

export const Label = React.forwardRef<HTMLLabelElement, LabelProps>(
  ({ className, required, children, ...props }, ref) => {
    return (
      <label
        ref={ref}
        className={cn(
          "block text-xs font-medium font-sans text-body-strong dark:text-[#d1ccc2] select-none mb-1.5",
          className
        )}
        {...props}
      >
        {children}
        {required && <span className="ml-1 text-primary font-medium">*</span>}
      </label>
    );
  }
);
Label.displayName = "Label";
