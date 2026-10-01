import {
  AlertTriangle,
  Award,
  Compass,
  FileText,
  ArrowUpRight,
  Sparkles,
  Radio,
  RefreshCw,
  Loader2,
} from "lucide-react";
import type { DocumentSummaryResponse } from "@/features/documents/api/documentsApi";
import { MathRenderer } from "@/components/shared/MathRenderer";
import { useDashboardStore } from "../stores/useDashboardStore";
import type { BoundingBox } from "@/types/dashboard";
import { Button } from "@/components/ui/button";

interface DocumentGroundedSummaryCardProps {
  summary?: DocumentSummaryResponse | null;
  paperTitle?: string;
  isGenerating?: boolean;
  isStreaming?: boolean;
  onGenerateSummary?: () => void;
  onStreamSummary?: () => void;
}

export function DocumentGroundedSummaryCard({
  summary,
  paperTitle = "Tài liệu",
  isGenerating = false,
  isStreaming = false,
  onGenerateSummary,
  onStreamSummary,
}: DocumentGroundedSummaryCardProps) {
  const setActiveBbox = useDashboardStore((s) => s.setActiveBbox);
  const activeBbox = useDashboardStore((s) => s.activeBbox);

  const isBboxActive = (bbox: BoundingBox) =>
    activeBbox &&
    activeBbox[0] === bbox[0] &&
    activeBbox[1] === bbox[1] &&
    activeBbox[4] === bbox[4];

  const handleCitationClick = (bbox: BoundingBox) => {
    setActiveBbox(bbox);
  };

  const hasSummaryContent = Boolean(
    summary &&
      (summary.problem_statement?.text ||
        summary.contributions?.text ||
        summary.limitations?.text)
  );

  const sections = summary
    ? [
        {
          id: "problem",
          title: "Vấn đề nghiên cứu (Problem Statement)",
          icon: AlertTriangle,
          colorClass: "text-amber-600 dark:text-amber-400",
          bgClass: "bg-amber-500/10 border-amber-500/20",
          badgeClass: "bg-amber-500/20 text-amber-700 dark:text-amber-300 border-amber-500/30",
          data: summary.problem_statement,
        },
        {
          id: "contributions",
          title: "Đóng góp chính (Contributions)",
          icon: Award,
          colorClass: "text-emerald-600 dark:text-emerald-400",
          bgClass: "bg-emerald-500/10 border-emerald-500/20",
          badgeClass: "bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border-emerald-500/30",
          data: summary.contributions,
        },
        {
          id: "limitations",
          title: "Hạn chế & Hướng phát triển (Limitations)",
          icon: Compass,
          colorClass: "text-purple-600 dark:text-purple-400",
          bgClass: "bg-purple-500/10 border-purple-500/20",
          badgeClass: "bg-purple-500/20 text-purple-700 dark:text-purple-300 border-purple-500/30",
          data: summary.limitations,
        },
      ]
    : [];

  return (
    <div className="w-full space-y-4 font-anthropic-sans">
      {/* Header bar */}
      <div className="flex flex-wrap items-center justify-between pb-2 border-b border-[#e6dfd8] dark:border-[#2a2824] gap-2">
        <div className="flex items-center gap-2">
          <span
            className={`w-2.5 h-2.5 rounded-full ${
              isStreaming || isGenerating
                ? "bg-amber-500 animate-ping"
                : hasSummaryContent
                ? "bg-[#cc785c]"
                : "bg-zinc-400"
            }`}
          />
          <h3 className="font-serif font-bold text-base sm:text-lg text-ink dark:text-[#f3f2ef]">
            3 Luận Điểm Cốt Lõi {paperTitle ? `• ${paperTitle}` : "(Grounded Summary)"}
          </h3>
        </div>

        <div className="flex items-center gap-2">
          {hasSummaryContent && !isStreaming && !isGenerating && (
            <div className="flex items-center gap-1.5">
              {onStreamSummary && (
                <button
                  type="button"
                  onClick={onStreamSummary}
                  title="Stream lại tóm tắt qua Server-Sent Events"
                  className="inline-flex items-center gap-1 px-2.5 py-1 text-xs rounded-md bg-surface-soft dark:bg-[#252320] border border-hairline hover:bg-surface-cream-strong text-ink dark:text-zinc-200 transition-colors cursor-pointer"
                >
                  <Radio className="w-3 h-3 text-[#cc785c]" />
                  <span>Stream lại (SSE)</span>
                </button>
              )}
              {onGenerateSummary && (
                <button
                  type="button"
                  onClick={onGenerateSummary}
                  title="Tái tạo tóm tắt qua REST API"
                  className="inline-flex items-center gap-1 px-2 py-1 text-xs rounded-md bg-surface-soft dark:bg-[#252320] border border-hairline hover:bg-surface-cream-strong text-muted hover:text-ink transition-colors cursor-pointer"
                >
                  <RefreshCw className="w-3 h-3" />
                  <span>Sinh mới</span>
                </button>
              )}
            </div>
          )}
          <span className="text-xs text-ink-muted dark:text-[#a09e99] font-mono">
            Visual Evidence Grounding
          </span>
        </div>
      </div>

      {/* Streaming / Generating active banner */}
      {(isStreaming || isGenerating) && (
        <div className="p-3 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-between text-xs text-primary font-medium animate-pulse">
          <div className="flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin shrink-0" />
            <span>
              {isStreaming
                ? "Đang nhận luồng tóm tắt SSE kèm toạ độ Bounding Box thời gian thực..."
                : "Mô hình AI đang phân tích toàn văn tài liệu..."}
            </span>
          </div>
          <span className="font-mono text-[11px] uppercase tracking-wider">Luồng trực tiếp</span>
        </div>
      )}

      {/* Empty State */}
      {!hasSummaryContent && !isStreaming && !isGenerating ? (
        <div className="p-8 rounded-2xl border border-dashed border-[#e6dfd8] dark:border-[#2a2824] bg-surface-card/60 dark:bg-[#1a1917]/50 text-center space-y-3">
          <div className="w-10 h-10 rounded-full bg-primary/10 text-primary flex items-center justify-center mx-auto">
            <Sparkles className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <h4 className="font-serif font-bold text-sm text-ink dark:text-zinc-100">
              Chưa có bản tóm tắt 3 luận điểm cốt lõi
            </h4>
            <p className="text-xs text-muted max-w-md mx-auto leading-relaxed">
              Trích xuất tự động Vấn đề nghiên cứu, Đóng góp chính và Các hạn chế cốt lõi. Mọi câu khẳng định đều được gắn nhãn toạ độ Bounding Box kiểm chứng trực tiếp trên bản PDF.
            </p>
          </div>
          <div className="flex items-center justify-center gap-2 pt-2">
            {onStreamSummary && (
              <Button
                variant="primary"
                size="sm"
                onClick={onStreamSummary}
                className="gap-1.5 text-xs cursor-pointer"
              >
                <Radio className="w-3.5 h-3.5 text-white" />
                <span>Stream tóm tắt (SSE)</span>
              </Button>
            )}
            {onGenerateSummary && (
              <Button
                variant="secondary"
                size="sm"
                onClick={onGenerateSummary}
                className="gap-1.5 text-xs cursor-pointer"
              >
                <Sparkles className="w-3.5 h-3.5 text-primary" />
                <span>Sinh tóm tắt (REST)</span>
              </Button>
            )}
          </div>
        </div>
      ) : (
        /* Summary Points Grid */
        <div className="grid grid-cols-1 gap-3.5">
          {sections.map((sec) => {
            const Icon = sec.icon;
            const bbox = sec.data?.bounding_boxes?.[0];
            const pageNum = bbox ? bbox[4] : null;
            const isSelected = bbox ? isBboxActive(bbox) : false;
            const textContent = sec.data?.text || "";

            return (
              <div
                key={sec.id}
                className={`p-4 rounded-xl border transition-all duration-200 bg-white dark:bg-[#1c1b18] ${
                  isSelected
                    ? "border-[#cc785c] ring-2 ring-[#cc785c]/30 shadow-sm"
                    : "border-[#e6dfd8] dark:border-[#2a2824] hover:border-[#cc785c]/50"
                }`}
              >
                {/* Header */}
                <div className="flex items-center justify-between gap-2 mb-2.5">
                  <div className="flex items-center gap-2">
                    <div className={`p-1.5 rounded-lg ${sec.bgClass}`}>
                      <Icon className={`w-4 h-4 ${sec.colorClass}`} />
                    </div>
                    <h4 className="text-sm font-semibold text-ink dark:text-[#f3f2ef]">
                      {sec.title}
                    </h4>
                  </div>

                  {/* Evidence Citation Badge */}
                  {bbox && pageNum && (
                    <button
                      type="button"
                      onClick={() => handleCitationClick(bbox)}
                      title={`Nhảy tới trang ${pageNum} trên PDF Canvas`}
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-mono font-medium border cursor-pointer transition-all ${
                        isSelected
                          ? "bg-[#cc785c] text-white border-[#cc785c]"
                          : sec.badgeClass
                      }`}
                    >
                      <FileText className="w-3 h-3 shrink-0" />
                      <span>Tr.{pageNum}</span>
                      <ArrowUpRight className="w-2.5 h-2.5 opacity-70" />
                    </button>
                  )}
                </div>

                {/* Body */}
                <div className="text-xs sm:text-sm text-ink dark:text-[#d6d4ce] leading-relaxed pl-8">
                  {textContent ? (
                    textContent.split("$$").map((chunk, bIdx) => {
                      if (bIdx % 2 === 1) {
                        return (
                          <div
                            key={bIdx}
                            className="my-2 p-2.5 rounded-xl bg-[#f7f4ee] dark:bg-[#21201d] border border-[#e5dfd4] dark:border-[#38332c] text-center overflow-x-auto text-[#cc785c] dark:text-amber-400 shadow-2xs"
                          >
                            <MathRenderer math={chunk.trim()} block />
                          </div>
                        );
                      }

                      const lines = chunk.split("\n").filter((l) => l.length > 0);
                      return (
                        <div key={bIdx} className="space-y-1.5">
                          {lines.map((line, lIdx) => {
                            const tokens = line.split(/(\*\*[^*]+\*\*|\$[^$]+\$)/g);
                            return (
                              <p key={lIdx} className="leading-relaxed">
                                {tokens.map((token, tIdx) => {
                                  if (token.startsWith("**") && token.endsWith("**")) {
                                    return (
                                      <strong key={tIdx} className="font-semibold text-ink dark:text-zinc-100">
                                        {token.slice(2, -2)}
                                      </strong>
                                    );
                                  }
                                  if (token.startsWith("$") && token.endsWith("$") && token.length > 2) {
                                    return (
                                      <MathRenderer
                                        key={tIdx}
                                        math={token.slice(1, -1)}
                                        className="text-[#cc785c] dark:text-amber-400 px-0.5"
                                      />
                                    );
                                  }
                                  return token;
                                })}
                              </p>
                            );
                          })}
                        </div>
                      );
                    })
                  ) : (
                    <span className="text-muted italic">Đang chờ luận điểm...</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
