import * as React from "react";
import { cn } from "@/lib/utils";

export interface AcademicLogoProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: "sm" | "md" | "lg" | "xl";
  inverted?: boolean;
  showWordmark?: boolean;
}

export function AcademicLogo({
  size = "md",
  inverted = false,
  showWordmark = true,
  className,
  ...props
}: AcademicLogoProps) {
  const sizeMap = {
    sm: { icon: 26, text: "text-lg", gap: "gap-2" },
    md: { icon: 32, text: "text-xl", gap: "gap-2.5" },
    lg: { icon: 40, text: "text-2xl", gap: "gap-3" },
    xl: { icon: 48, text: "text-xl sm:text-3xl tracking-normal", gap: "gap-2.5 sm:gap-3.5" },
  };

  const { icon, text, gap } = sizeMap[size];
  const logoSrc = inverted
    ? "/images/VeriScholar_logo_dark.svg"
    : "/images/VeriScholar_logo_light.svg";

  return (
    <div
      className={cn(
        "inline-flex items-center font-display select-none group",
        gap,
        inverted ? "text-on-dark" : "text-ink",
        className
      )}
      {...props}
    >
      <img
        src={logoSrc}
        alt="VeriScholar"
        width={icon}
        height={icon}
        className={cn(
          "shrink-0 transition-transform duration-300 group-hover:scale-105 drop-shadow-xs object-contain",
          size === "sm" && "w-[26px] h-[26px]",
          size === "md" && "w-8 h-8",
          size === "lg" && "w-10 h-10",
          size === "xl" && "w-9 h-9 sm:w-12 sm:h-12"
        )}
      />

      {showWordmark && (
        <span className={cn("tracking-tight font-display font-medium", text)}>
          Veri<span className="text-primary font-normal">Scholar</span>
        </span>
      )}
    </div>
  );
}

