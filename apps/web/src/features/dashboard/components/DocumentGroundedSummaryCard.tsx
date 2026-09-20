import { AlertTriangle, Award, Compass, FileText, ArrowUpRight } from "lucide-react";
import type { DocumentSummaryResponse } from "@/features/documents/api/documentsApi";
import { MathRenderer } from "@/components/shared/MathRenderer";
import { useDashboardStore } from "../stores/useDashboardStore";
import type { BoundingBox } from "@/types/dashboard";

interface DocumentGroundedSummaryCardProps {
  summary: DocumentSummaryResponse;
  paperTitle?: string;
}

export function DocumentGroundedSummaryCard({
  summary,
  paperTitle = "Tài liệu",
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

  const sections = [
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
  ];

  return (
    <div className="w-full space-y-4 font-anthropic-sans">
      <div className="flex items-center justify-between pb-2 border-b border-[#e6dfd8] dark:border-[#2a2824]">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-[#cc785c] animate-pulse" />
          <h3 className="font-serif font-bold text-base sm:text-lg text-ink dark:text-[#f3f2ef]">
            3 Luận Điểm Cốt Lõi {paperTitle ? `• ${paperTitle}` : "(Grounded Summary)"}
          </h3>
        </div>
        <span className="text-xs text-ink-muted dark:text-[#a09e99] font-mono">
          Visual Evidence Grounding
        </span>
      </div>

      <div className="grid grid-cols-1 gap-3.5">
        {sections.map((sec) => {
          const Icon = sec.icon;
          const bbox = sec.data.bounding_boxes?.[0];
          const pageNum = bbox ? bbox[4] : null;
          const isSelected = bbox ? isBboxActive(bbox) : false;

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
                {sec.data.text.split("$$").map((chunk, bIdx) => {
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
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
