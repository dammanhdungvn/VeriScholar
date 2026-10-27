import { FileText, ArrowUpRight } from "lucide-react";
import type { CitationBadgeData } from "@/types/dashboard";
import { useDashboardStore } from "../stores/useDashboardStore";
import { useReaderStore } from "@/features/reader/stores/useReaderStore";

interface CitationBadgeProps {
  citation: CitationBadgeData;
  onOpenReferences?: () => void;
}

export function CitationBadge({ citation, onOpenReferences: _onOpenReferences }: CitationBadgeProps) {
  const setActiveBbox = useDashboardStore((s) => s.setActiveBbox);
  const activeBbox = useDashboardStore((s) => s.activeBbox);

  const isSelected = Boolean(
    activeBbox &&
    citation.bbox &&
    activeBbox[0] === citation.bbox[0] &&
    activeBbox[1] === citation.bbox[1] &&
    activeBbox[4] === citation.bbox[4]
  );

  const handleClick = () => {
    const docId = citation.paper_id;
    if (docId) {
      useReaderStore.getState().setActiveDocumentId(docId);
    }

    const targetPage = citation.bbox ? citation.bbox[4] || citation.page || 1 : citation.page || 1;

    if (citation.bbox) {
      setActiveBbox(citation.bbox);
      useReaderStore.getState().setCurrentPage(targetPage);
    } else if (citation.page) {
      useReaderStore.getState().setCurrentPage(citation.page);
    }

    if (typeof window !== "undefined") {
      window.dispatchEvent(
        new CustomEvent("scholar:focus-bbox", {
          detail: {
            documentId: docId,
            pageNumber: targetPage,
            boundingBoxes: citation.bbox ? [citation.bbox] : [],
          },
        })
      );
    }
  };

  return (
    <button
      type="button"
      data-testid="citation-badge"
      onClick={handleClick}
      title={`Xem đoạn bằng chứng tại trang ${citation.page}`}
      className={`inline-flex items-center gap-1 px-2 py-0.5 mx-1 rounded-md text-2xs font-mono transition-all cursor-pointer border ${
        isSelected
          ? "bg-amber-500/20 text-amber-600 dark:text-amber-400 border-amber-500/50 ring-2 ring-amber-500/30"
          : "bg-surface-soft dark:bg-[#282623] hover:bg-surface-cream-strong dark:hover:bg-[#322f2b] text-ink dark:text-zinc-200 border-hairline dark:border-zinc-700/60"
      }`}
    >
      <FileText className="w-3 h-3 text-primary shrink-0" />
      <span className="truncate max-w-[130px] font-sans font-medium">
        {citation.paper_title}
      </span>
      <span className="text-muted dark:text-zinc-400">Tr.{citation.page}</span>
      <ArrowUpRight className="w-2.5 h-2.5 opacity-60" />
    </button>
  );
}
