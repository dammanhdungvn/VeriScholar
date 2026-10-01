import { X, BookOpen, ChevronRight } from "lucide-react";
import type { DocumentStructureData } from "@/types/document";

interface DocumentStructureSheetProps {
  structure?: DocumentStructureData | null;
  isOpen: boolean;
  onClose: () => void;
  onNavigatePage: (page: number) => void;
}

export function DocumentStructureSheet({
  structure,
  isOpen,
  onClose,
  onNavigatePage,
}: DocumentStructureSheetProps) {
  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-label="Cấu trúc và mục lục bài báo"
      className="absolute inset-y-0 right-0 w-80 max-w-full bg-surface-card dark:bg-[#1e1d1a] border-l border-hairline dark:border-[#2f2b26] shadow-xl z-20 flex flex-col animate-in slide-in-from-right duration-200"
    >
      <div className="h-11 px-4 border-b border-hairline dark:border-[#2f2b26] flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs font-serif font-semibold text-ink dark:text-zinc-100">
          <BookOpen className="w-4 h-4 text-primary" />
          <span>Mục lục bài báo</span>
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label="Đóng mục lục"
          className="p-1 rounded hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
        {structure?.abstract && (
          <div className="p-3 rounded-md bg-surface-soft dark:bg-[#252320] border border-hairline dark:border-[#332f29]">
            <h4 className="font-sans font-semibold text-ink dark:text-zinc-200 mb-1 uppercase text-[10px] tracking-wider text-primary">
              Tóm tắt (Abstract)
            </h4>
            <p className="text-muted leading-relaxed font-serif text-[11px] line-clamp-6">
              {structure.abstract}
            </p>
          </div>
        )}

        <div>
          <h4 className="text-[10px] uppercase font-mono tracking-wider text-muted font-semibold mb-2">
            Các phần mục (Sections)
          </h4>

          {(!structure?.sections || structure.sections.length === 0) ? (
            <p className="text-muted text-center py-4">Chưa phát hiện phân mục</p>
          ) : (
            <ul className="space-y-1">
              {structure.sections.map((section, idx) => (
                <li key={idx}>
                  <button
                    type="button"
                    onClick={() => {
                      onNavigatePage(section.page_number);
                      onClose();
                    }}
                    className="w-full text-left px-2.5 py-2 rounded hover:bg-surface-cream-strong/70 dark:hover:bg-[#282622] flex items-center justify-between group transition-colors"
                  >
                    <span className="font-sans text-body-strong dark:text-zinc-200 group-hover:text-primary transition-colors truncate pr-2">
                      {section.title}
                    </span>
                    <span className="text-[10px] font-mono text-muted shrink-0 flex items-center gap-1">
                      Tr. {section.page_number}
                      <ChevronRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
