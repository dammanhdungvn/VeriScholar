import * as React from "react";
import { cn } from "@/lib/utils";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "canvas" | "card" | "dark" | "coral";
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = "card", ...props }, ref) => {
    const variantStyles = {
      canvas: "bg-canvas border border-hairline text-ink",
      card: "bg-surface-card border border-hairline text-ink",
      dark: "bg-surface-dark border border-[#2a2926] text-on-dark",
      coral: "bg-primary text-on-primary",
    };

    return (
      <div
        ref={ref}
        className={cn("rounded-lg p-6 transition-all", variantStyles[variant], className)}
        {...props}
      />
    );
  }
);
Card.displayName = "Card";

export function CardHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("flex flex-col gap-1.5 mb-4", className)} {...props} />;
}

export function CardTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={cn("font-display text-xl font-normal tracking-tight text-ink", className)} {...props} />;
}

export function CardDescription({ className, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn("text-sm text-muted font-sans leading-relaxed", className)} {...props} />;
}

export function CardContent({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("", className)} {...props} />;
}

export function CardFooter({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("flex items-center pt-4", className)} {...props} />;
}
