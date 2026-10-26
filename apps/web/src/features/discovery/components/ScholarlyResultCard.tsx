import { useState } from "react";
import {
  BookOpen,
  FileText,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Loader2,
  CheckCircle2,
} from "lucide-react";
import type { ScholarlyPaper } from "../api/discoveryApi";

export function formatScholarlyAuthors(authors?: string[]): string {
  if (!authors || authors.length === 0) {
    return "Chưa rõ tác giả";
  }
  if (authors.length <= 2) {
    return authors.join(", ");
  }
  return `${authors[0]}, ${authors[1]} và cộng sự`;
}

export function sanitizeAcademicTitle(title: string): string {
  if (!title) return "";
  let clean = title;

  // Replace common LaTeX math symbols and arrows
  clean = clean.replace(/\\to\b|\\rightarrow\b/g, " -> ");
  clean = clean.replace(/\\leftarrow\b/g, " <- ");
  clean = clean.replace(/\\leftrightarrow\b/g, " <-> ");
  clean = clean.replace(/\\pm\b/g, " ± ");
  clean = clean.replace(/\\times\b/g, " × ");
  clean = clean.replace(/\\cdot\b/g, " · ");
  clean = clean.replace(/\\leq\b/g, " <= ");
  clean = clean.replace(/\\geq\b/g, " >= ");
  clean = clean.replace(/\\neq\b/g, " != ");
  clean = clean.replace(/\\approx\b/g, " ≈ ");
  clean = clean.replace(/\\infty\b/g, " ∞ ");

  // Greek letters
  clean = clean.replace(/\\mu\b/g, "mu");
  clean = clean.replace(/\\alpha\b/g, "alpha");
  clean = clean.replace(/\\beta\b/g, "beta");
  clean = clean.replace(/\\gamma\b/g, "gamma");
  clean = clean.replace(/\\theta\b/g, "theta");
  clean = clean.replace(/\\lambda\b/g, "lambda");
  clean = clean.replace(/\\pi\b/g, "pi");
  clean = clean.replace(/\\sigma\b/g, "sigma");

  // LaTeX text formatting commands: \text{abc}, \mathbf{abc}, etc.
  clean = clean.replace(/\\(?:text|mathbf|mathit|mathrm|mathcal|mathbb)\{([^}]*)\}/g, "$1");

  // Remove remaining curly braces
  clean = clean.replace(/[{}]/g, "");

  // Remove stray backslashes before words
  clean = clean.replace(/\\([a-zA-Z]+)/g, "$1");
  clean = clean.replace(/\\/g, "");

  // Remove all $ delimiters
  clean = clean.replace(/\$/g, "");

  // Collapse whitespace
  clean = clean.replace(/\s+/g, " ").trim();

  return clean;
}

interface ScholarlyResultCardProps {
  paper: ScholarlyPaper;
  onOpenReading: (paper: ScholarlyPaper) => void;
  isLoading?: boolean;
}

export function ScholarlyResultCard({
  paper,
  onOpenReading,
  isLoading = false,
}: ScholarlyResultCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const isOpenAccess = paper.access_status === "open_access_pdf";

  return (
    <div className="p-5 rounded-xl border border-hairline bg-white dark:bg-[#1c1b18] hover:border-zinc-300 dark:hover:border-zinc-700 transition-all duration-200 shadow-xs flex flex-col justify-between gap-4">
      <div className="space-y-2">
        {/* Header row: Access badge, Peer-Reviewed tag & Year */}
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-1.5 flex-wrap">
            {isOpenAccess ? (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                <span>Open Access PDF</span>
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-zinc-500/10 text-zinc-700 dark:text-zinc-400 border border-zinc-500/20">
                <span className="w-1.5 h-1.5 rounded-full bg-zinc-400" />
                <span>Tóm tắt</span>
              </span>
            )}

            {paper.is_peer_reviewed && (
              <span
                data-testid="peer-reviewed-badge"
                title="Bài báo đã qua hội đồng chuyên gia phản biện và công bố chính thức (Peer-Reviewed)"
                className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-purple-500/10 text-purple-700 dark:text-purple-400 border border-purple-500/20"
              >
                <CheckCircle2 className="w-3 h-3 text-purple-600 dark:text-purple-400" />
                <span>Đã bình duyệt</span>
              </span>
            )}
          </div>

          {paper.publication_year && (
            <span className="text-[11px] font-mono text-muted dark:text-zinc-400">
              {paper.publication_year}
            </span>
          )}
        </div>

        {/* Paper Title (Sanitized of raw LaTeX) */}
        <h3 className="text-base font-semibold font-anthropic-serif text-ink dark:text-zinc-100 leading-snug">
          {sanitizeAcademicTitle(paper.title)}
        </h3>

        {/* Authors (Clamped to 2 authors + 'và cộng sự') and Venue */}
        <div className="text-xs text-muted dark:text-zinc-400">
          <span>{formatScholarlyAuthors(paper.authors)}</span>
          {paper.venue && (
            <>
              <span className="mx-1.5 text-zinc-300 dark:text-zinc-700">•</span>
              <span className="italic">{paper.venue}</span>
            </>
          )}
        </div>

        {/* Abstract (Clamped to line-clamp-2) */}
        {paper.abstract && (
          <div className="pt-1">
            <p
              className={`text-xs text-zinc-600 dark:text-zinc-300 leading-relaxed font-sans ${
                !isExpanded ? "line-clamp-2" : ""
              }`}
            >
              {paper.abstract}
            </p>
            {paper.abstract.length > 120 && (
              <button
                type="button"
                onClick={() => setIsExpanded(!isExpanded)}
                className="mt-1 text-[11px] font-medium text-[#cc785c] dark:text-[#e08b6f] hover:underline flex items-center gap-1 cursor-pointer"
              >
                {isExpanded ? (
                  <>
                    <span>Thu gọn</span>
                    <ChevronUp className="w-3 h-3" />
                  </>
                ) : (
                  <>
                    <span>Xem thêm tóm tắt</span>
                    <ChevronDown className="w-3 h-3" />
                  </>
                )}
              </button>
            )}
          </div>
        )}

        {/* Direct Identifiers */}
        <div className="flex flex-wrap items-center gap-3 pt-1 text-[10px] font-mono text-muted dark:text-zinc-400">
          {paper.doi && (
            <a
              href={`https://doi.org/${paper.doi}`}
              target="_blank"
              rel="noreferrer"
              className="hover:text-coral-600 hover:underline flex items-center gap-0.5"
            >
              <span>DOI: {paper.doi}</span>
              <ExternalLink className="w-2.5 h-2.5 ml-0.5 opacity-60" />
            </a>
          )}
          {paper.arxiv_id && (
            <a
              href={`https://arxiv.org/abs/${paper.arxiv_id}`}
              target="_blank"
              rel="noreferrer"
              className="hover:text-coral-600 hover:underline flex items-center gap-0.5"
            >
              <span>arXiv: {paper.arxiv_id}</span>
              <ExternalLink className="w-2.5 h-2.5 ml-0.5 opacity-60" />
            </a>
          )}
        </div>
      </div>

      {/* Action footer */}
      <div className="pt-3 border-t border-hairline flex items-center justify-end gap-2">
        <button
          type="button"
          onClick={() => onOpenReading(paper)}
          disabled={isLoading}
          className={`h-8 px-4 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors cursor-pointer disabled:opacity-50 ${
            isOpenAccess
              ? "bg-ink dark:bg-white text-white dark:text-black hover:opacity-90"
              : "bg-zinc-100 dark:bg-zinc-800 text-zinc-800 dark:text-zinc-200 hover:bg-zinc-200 dark:hover:bg-zinc-700"
          }`}
        >
          {isLoading ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>Đang mở...</span>
            </>
          ) : isOpenAccess ? (
            <>
              <BookOpen className="w-3.5 h-3.5" />
              <span>Mở Đọc Sâu</span>
            </>
          ) : (
            <>
              <FileText className="w-3.5 h-3.5" />
              <span>Xem Tóm Tắt</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
