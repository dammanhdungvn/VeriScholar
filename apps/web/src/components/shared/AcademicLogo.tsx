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
    xl: { icon: 52, text: "text-3xl", gap: "gap-3.5" },
  };

  const { icon, text, gap } = sizeMap[size];
  const uniqueId = React.useId().replace(/:/g, "");

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
      {/* VeriScholar Brand Mark: Book + V Spine + Corner Bounding Box + AI Spark */}
      <svg
        width={icon}
        height={icon}
        viewBox="0 0 1024 1024"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="shrink-0 transition-transform duration-300 group-hover:scale-105 drop-shadow-xs"
        aria-hidden="true"
      >
        <defs>
          <linearGradient id={`coral-${uniqueId}`} x1="320" y1="300" x2="620" y2="820" gradientUnits="userSpaceOnUse">
            <stop stopColor="#D98A6B" />
            <stop offset="1" stopColor="#B96549" />
          </linearGradient>
          <linearGradient id={`paper-${uniqueId}`} x1="270" y1="600" x2="520" y2="900" gradientUnits="userSpaceOnUse">
            <stop stopColor={inverted ? "#FAF8F4" : "#FFFDF8"} />
            <stop offset="1" stopColor={inverted ? "#DCD4C5" : "#E8E0D2"} />
          </linearGradient>
        </defs>

        {/* Verification frame / 4-corner bounding box */}
        <g stroke="#CC785C" strokeWidth="28" strokeLinecap="round" strokeLinejoin="round">
          <path d="M250 180H365" />
          <path d="M250 180V295" />
          <path d="M774 180H659" />
          <path d="M774 180V295" />
          <path d="M250 700V585" />
          <path d="M250 700H365" />
          <path d="M774 700V585" />
          <path d="M774 700H659" />
        </g>

        {/* AI / discovery sparkle */}
        <path
          d="M512 245 C520 285 535 300 575 308 C535 316 520 331 512 371 C504 331 489 316 449 308 C489 300 504 285 512 245Z"
          fill="#CC785C"
        />

        {/* Open scholarly book */}
        <path
          d="M512 780 C450 716 382 660 282 625 C263 619 245 629 238 650 L198 812 C303 778 408 793 512 875Z"
          fill={`url(#paper-${uniqueId})`}
        />
        <path
          d="M512 780 C574 716 642 660 742 625 C761 619 779 629 786 650 L826 812 C721 778 616 793 512 875Z"
          fill={`url(#paper-${uniqueId})`}
        />

        {/* Page layers */}
        <path
          d="M203 825 C310 792 411 810 512 890 C613 810 714 792 821 825 L812 855 C705 824 608 838 512 913 C416 838 319 824 212 855Z"
          fill={inverted ? "#252320" : "#141413"}
        />
        <path
          d="M222 790 C323 764 419 781 512 851 C605 781 701 764 802 790 L792 819 C691 795 603 810 512 880 C421 810 333 795 232 819Z"
          fill="#E8E0D2"
        />

        {/* Central verification V emerging from the book */}
        <path
          d="M306 335 L423 360 L512 650 L602 360 L719 335 L590 718 C574 765 552 800 512 827 C472 800 450 765 434 718Z"
          fill={`url(#coral-${uniqueId})`}
        />

        {/* Dark verification arm */}
        <path
          d="M512 650 L602 360 L719 335 L590 718 C574 765 552 800 512 827 C545 786 558 744 550 704Z"
          fill={inverted ? "#181715" : "#252320"}
        />

        {/* Small inner highlight to reinforce V/book fusion */}
        <path
          d="M512 827 C536 799 550 770 557 735 L542 700 C533 747 522 780 512 827Z"
          fill="#E8E0D2"
        />
      </svg>

      {showWordmark && (
        <span className={cn("tracking-tight font-display font-medium", text)}>
          Veri<span className="text-primary font-normal">Scholar</span>
        </span>
      )}
    </div>
  );
}

