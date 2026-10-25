import * as React from "react";
import katex from "katex";

export interface MathRendererProps {
  math: string;
  block?: boolean;
  className?: string;
}

export function MathRenderer({ math, block = false, className }: MathRendererProps) {
  const html = React.useMemo(() => {
    const cleanMath = math ? math.trim() : "";
    if (!cleanMath || cleanMath === "undefined") {
      return "";
    }
    try {
      return katex.renderToString(cleanMath, {
        displayMode: block,
        throwOnError: false,
      });
    } catch {
      return cleanMath;
    }
  }, [math, block]);

  if (!html) return null;

  if (block) {
    return (
      <div
        className={className}
        dangerouslySetInnerHTML={{ __html: html }}
      />
    );
  }

  return (
    <span
      className={className}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
