import {
  BookMarked,
  GitBranch,
  Link2,
  ArrowUpRight,
  Sparkles,
} from "lucide-react";
import type { BibliometricsResponseData } from "../types";
import { cn } from "@/lib/utils";

export interface BibliometricsPriorWorksCardProps {
  data: BibliometricsResponseData | null;
  loading?: boolean;
  onSelectPaper?: (paperId: string) => void;
  className?: string;
}

export function BibliometricsPriorWorksCard({
  data,
  loading = false,
  onSelectPaper,
  className,
}: BibliometricsPriorWorksCardProps) {
  if (loading) {
    return (
      <div
        className={cn(
          "p-6 rounded-2xl border border-[#e8e4dc] dark:border-[#2a2824] bg-white dark:bg-[#1c1b18] animate-pulse space-y-4",
          className
        )}
      >
        <div className="h-4 bg-stone-200 dark:bg-stone-800 rounded w-1/3" />
        <div className="h-20 bg-stone-100 dark:bg-stone-900 rounded-xl" />
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const { prior_works = [], derivative_works = [], coupling_edges = [] } = data;

  const totalCouplingCount = coupling_edges.reduce(
    (sum, edge) => sum + edge.shared_reference_count,
    0
  );

  return (
    <div
      className={cn(
        "rounded-2xl border border-[#e8e4dc] dark:border-[#2a2824] bg-white dark:bg-[#1c1b18] overflow-hidden",
        className
      )}
    >
      {/* Header */}
      <div className="px-5 py-3.5 border-b border-[#ece8df] dark:border-[#282622] bg-[#fdfcf9] dark:bg-[#1f1e1a] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-[#c15f3e]" />
          <h3 className="text-xs font-semibold text-ink dark:text-zinc-100 uppercase tracking-wider font-mono">
            Phân Tích Thư Mục Học
          </h3>
        </div>
        {coupling_edges.length > 0 && (
          <span className="text-[11px] font-mono text-muted dark:text-zinc-400 flex items-center gap-1">
            <Link2 className="w-3 h-3 text-[#c15f3e]" />
            <span>
              {totalCouplingCount} tài liệu tham khảo chung ({coupling_edges.length} cặp bài báo)
            </span>
          </span>
        )}
      </div>

      <div className="p-5 grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 1. Prior Works (Tác phẩm Cội nguồn - In-Degree) */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <BookMarked className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
              <span className="text-xs font-medium text-ink dark:text-zinc-200">
                Tác phẩm Cội nguồn
              </span>
            </div>
            <span className="text-[10px] font-mono text-muted dark:text-zinc-500 uppercase">
              Bậc vào (In-Degree)
            </span>
          </div>

          {prior_works.length === 0 ? (
            <p className="text-[11px] text-muted dark:text-zinc-500 italic py-2">
              Chưa có tác phẩm cội nguồn được xác định
            </p>
          ) : (
            <div className="space-y-2">
              {prior_works.map((paper) => (
                <div
                  key={paper.id}
                  onClick={() => onSelectPaper?.(paper.id)}
                  className="group p-2.5 rounded-xl border border-[#ece8df] dark:border-[#2a2824] hover:border-indigo-500/40 bg-[#fdfcf9] dark:bg-[#1a1916] flex items-center justify-between gap-3 transition-colors cursor-pointer"
                >
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-medium text-ink dark:text-zinc-200 truncate group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                      {paper.title}
                    </p>
                    <div className="flex items-center gap-2 mt-0.5 text-[10px] text-muted dark:text-zinc-500 font-mono">
                      {paper.year && <span>{paper.year}</span>}
                      {paper.citation_key && (
                        <span>&bull; {paper.citation_key}</span>
                      )}
                    </div>
                  </div>

                  <div
                    data-testid="prior-work-in-degree"
                    className="flex items-center gap-1 shrink-0 px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 font-mono text-[11px] font-semibold"
                  >
                    <span>{paper.in_degree}</span>
                    <ArrowUpRight className="w-3 h-3 opacity-60" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 2. Derivative Works (Tác phẩm Phái sinh - Out-Degree) */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <GitBranch className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
              <span className="text-xs font-medium text-ink dark:text-zinc-200">
                Tác phẩm Phái sinh
              </span>
            </div>
            <span className="text-[10px] font-mono text-muted dark:text-zinc-500 uppercase">
              Bậc ra (Out-Degree)
            </span>
          </div>

          {derivative_works.length === 0 ? (
            <p className="text-[11px] text-muted dark:text-zinc-500 italic py-2">
              Chưa có tác phẩm phái sinh được xác định
            </p>
          ) : (
            <div className="space-y-2">
              {derivative_works.map((paper) => (
                <div
                  key={paper.id}
                  onClick={() => onSelectPaper?.(paper.id)}
                  className="group p-2.5 rounded-xl border border-[#ece8df] dark:border-[#2a2824] hover:border-emerald-500/40 bg-[#fdfcf9] dark:bg-[#1a1916] flex items-center justify-between gap-3 transition-colors cursor-pointer"
                >
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-medium text-ink dark:text-zinc-200 truncate group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">
                      {paper.title}
                    </p>
                    <div className="flex items-center gap-2 mt-0.5 text-[10px] text-muted dark:text-zinc-500 font-mono">
                      {paper.year && <span>{paper.year}</span>}
                      {paper.citation_key && (
                        <span>&bull; {paper.citation_key}</span>
                      )}
                    </div>
                  </div>

                  <div
                    data-testid="derivative-work-out-degree"
                    className="flex items-center gap-1 shrink-0 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 font-mono text-[11px] font-semibold"
                  >
                    <span>{paper.out_degree}</span>
                    <ArrowUpRight className="w-3 h-3 opacity-60" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
