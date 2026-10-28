import { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";
import { Check, Copy, Download, Image as ImageIcon, Network } from "lucide-react";

interface MermaidRendererProps {
  chart: string;
  className?: string;
}

export function MermaidRenderer({ chart, className }: MermaidRendererProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svgContent, setSvgContent] = useState<string>("");
  const [renderError, setRenderError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let isMounted = true;
    const isDark = document.documentElement.classList.contains("dark");
    const cleanChart = chart ? chart.trim() : "";

    if (!cleanChart || cleanChart === "undefined" || cleanChart.length < 5) {
      return;
    }

    const uniqueId = `mermaid-svg-${Math.random().toString(36).substring(2, 10)}`;

    try {
      mermaid.initialize({
        startOnLoad: false,
        suppressErrorRendering: true,
        theme: isDark ? "dark" : "neutral",
        securityLevel: "loose",
        fontFamily: "var(--font-sans, system-ui, sans-serif)",
        themeVariables: isDark
          ? {
              darkMode: true,
              background: "#181816",
              primaryColor: "#cc785c",
              primaryTextColor: "#f5f3ed",
              primaryBorderColor: "#8c442e",
              lineColor: "#b87058",
              secondaryColor: "#292723",
              tertiaryColor: "#201e1b",
            }
          : {
              background: "#fcfbf7",
              primaryColor: "#cc785c",
              primaryTextColor: "#141413",
              primaryBorderColor: "#d99079",
              lineColor: "#cc785c",
              secondaryColor: "#f4efe6",
              tertiaryColor: "#ebe4d5",
            },
      });

      mermaid
        .render(uniqueId, cleanChart)
        .then(({ svg }) => {
          if (isMounted) {
            setSvgContent(svg);
            setRenderError(null);
          }
        })
        .catch((err) => {
          if (isMounted) {
            setRenderError(err?.message || "Không thể vẽ sơ đồ Mermaid");
          }
          const strayEl = document.getElementById(`d${uniqueId}`);
          if (strayEl) strayEl.remove();
        });
    } catch (err: unknown) {
      if (isMounted) {
        setRenderError(err instanceof Error ? err.message : "Lỗi khởi tạo sơ đồ");
      }
      const strayEl = document.getElementById(`d${uniqueId}`);
      if (strayEl) strayEl.remove();
    }

    return () => {
      isMounted = false;
      const strayEl = document.getElementById(`d${uniqueId}`);
      if (strayEl) strayEl.remove();
    };
  }, [chart]);

  const handleCopy = () => {
    navigator.clipboard.writeText(chart.trim());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadSvg = () => {
    let svgSource = svgContent;
    const svgEl = containerRef.current?.querySelector("svg");
    if (svgEl) {
      svgSource = new XMLSerializer().serializeToString(svgEl);
    }
    if (!svgSource) return;

    if (!svgSource.match(/^<svg[^>]+xmlns="http:\/\/www\.w3\.org\/2000\/svg"/)) {
      svgSource = svgSource.replace(
        /^<svg/,
        '<svg xmlns="http://www.w3.org/2000/svg"'
      );
    }

    const blob = new Blob([svgSource], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "diagram.svg";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleDownloadPng = () => {
    let svgSource = svgContent;
    const svgEl = containerRef.current?.querySelector("svg");
    if (svgEl) {
      svgSource = new XMLSerializer().serializeToString(svgEl);
    }
    if (!svgSource) return;

    if (!svgSource.match(/^<svg[^>]+xmlns="http:\/\/www\.w3\.org\/2000\/svg"/)) {
      svgSource = svgSource.replace(
        /^<svg/,
        '<svg xmlns="http://www.w3.org/2000/svg"'
      );
    }

    const svgBlob = new Blob([svgSource], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(svgBlob);

    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      try {
        const bbox = svgEl?.getBoundingClientRect();
        const svgWidth =
          bbox && bbox.width > 0
            ? bbox.width
            : parseFloat(svgEl?.getAttribute("width") || "0") || img.naturalWidth || 800;
        const svgHeight =
          bbox && bbox.height > 0
            ? bbox.height
            : parseFloat(svgEl?.getAttribute("height") || "0") || img.naturalHeight || 600;

        const scale = 2; // 2x vector scale
        const canvas = document.createElement("canvas");
        canvas.width = Math.max(Math.round(svgWidth * scale), 200);
        canvas.height = Math.max(Math.round(svgHeight * scale), 150);

        const ctx = canvas.getContext("2d");
        if (ctx) {
          const isDark = document.documentElement.classList.contains("dark");
          ctx.fillStyle = isDark ? "#181816" : "#ffffff";
          ctx.fillRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

          const pngUrl = canvas.toDataURL("image/png");
          const a = document.createElement("a");
          a.href = pngUrl;
          a.download = "diagram.png";
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
        }
      } catch (err) {
        console.error("Failed to export Mermaid PNG:", err);
      } finally {
        URL.revokeObjectURL(url);
      }
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
    };
    img.src = url;
  };

  if (renderError) {
    return (
      <div className="my-3 rounded-xl border border-rose-300 dark:border-rose-900/60 bg-rose-50/50 dark:bg-rose-950/20 p-3 text-xs font-mono text-rose-700 dark:text-rose-300">
        <div className="flex items-center justify-between mb-1.5 font-sans font-semibold">
          <span>Lỗi kết xuất sơ đồ Mermaid</span>
          <button
            type="button"
            data-testid="copy-mermaid-btn"
            onClick={handleCopy}
            className="inline-flex items-center gap-1 text-2xs hover:underline cursor-pointer"
          >
            {copied ? <Check className="w-3 h-3 text-emerald-500" /> : <Copy className="w-3 h-3" />}
            <span>{copied ? "Đã chép" : "Sao chép mã"}</span>
          </button>
        </div>
        <pre className="overflow-x-auto text-2xs whitespace-pre-wrap">{chart}</pre>
      </div>
    );
  }

  return (
    <div
      className={`my-4 rounded-xl border border-[#e5dfd4] dark:border-[#38332c] bg-[#fcfbf7] dark:bg-[#1a1917] overflow-hidden shadow-2xs ${
        className || ""
      }`}
      data-testid="mermaid-diagram-container"
    >
      <div className="flex items-center justify-between px-3.5 py-2 border-b border-[#eee8dc] dark:border-[#2d2924] bg-[#f7f3ea]/70 dark:bg-[#201e1b]/70 text-xs text-muted dark:text-zinc-400">
        <div className="inline-flex items-center gap-1.5 font-medium text-ink dark:text-zinc-200">
          <Network className="w-3.5 h-3.5 text-primary dark:text-coral-400" />
          <span>Sơ đồ kiến trúc & Mindmap</span>
        </div>
        <div className="flex items-center gap-1">
          <button
            type="button"
            data-testid="download-svg-btn"
            onClick={handleDownloadSvg}
            disabled={!svgContent}
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-2xs font-sans text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-surface-soft dark:hover:bg-[#2b2722] transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            title="Tải ảnh vector SVG"
          >
            <Download className="w-3 h-3" />
            <span>Tải SVG</span>
          </button>
          <button
            type="button"
            data-testid="download-png-btn"
            onClick={handleDownloadPng}
            disabled={!svgContent}
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-2xs font-sans text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-surface-soft dark:hover:bg-[#2b2722] transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            title="Tải ảnh PNG độ phân giải cao"
          >
            <ImageIcon className="w-3 h-3" />
            <span>Tải PNG</span>
          </button>
          <button
            type="button"
            data-testid="copy-mermaid-btn"
            onClick={handleCopy}
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-2xs font-sans text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-surface-soft dark:hover:bg-[#2b2722] transition-colors cursor-pointer"
            title="Sao chép cú pháp Mermaid"
          >
            {copied ? (
              <>
                <Check className="w-3 h-3 text-emerald-500" />
                <span>Đã chép</span>
              </>
            ) : (
              <>
                <Copy className="w-3 h-3" />
                <span>Sao chép mã</span>
              </>
            )}
          </button>
        </div>
      </div>

      <div
        ref={containerRef}
        className="p-4 flex items-center justify-center overflow-x-auto min-h-[140px] [&_svg]:max-w-full [&_svg]:h-auto"
        dangerouslySetInnerHTML={{ __html: svgContent }}
      />
    </div>
  );
}
