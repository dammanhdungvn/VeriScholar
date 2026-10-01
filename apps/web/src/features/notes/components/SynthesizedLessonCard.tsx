import { BookOpen, Calendar, ArrowUpRight } from "lucide-react";
import type { NoteSynthesisResponse, InteractiveBadgeResponse } from "@/types/note";
import { MathRenderer } from "@/components/shared/MathRenderer";

interface SynthesizedLessonCardProps {
  synthesis: NoteSynthesisResponse;
  onJumpToBadge?: (badge: InteractiveBadgeResponse) => void;
  onClose?: () => void;
}

export function SynthesizedLessonCard({
  synthesis,
  onJumpToBadge,
  onClose,
}: SynthesizedLessonCardProps) {
  // Simple markdown renderer with KaTeX math formula separation
  const renderContent = () => {
    const raw = synthesis.markdown_content || "";
    const blocks = raw.split("$$");

    return blocks.map((block, idx) => {
      if (idx % 2 === 1) {
        return (
          <div
            key={idx}
            className="my-3 p-3 rounded bg-surface-soft dark:bg-[#252320] border border-hairline dark:border-[#332f29] text-center overflow-x-auto text-primary"
          >
            <MathRenderer math={block.trim()} block />
          </div>
        );
      }

      const paragraphs = block.split("\n\n").filter(Boolean);
      return (
        <div key={idx} className="space-y-2">
          {paragraphs.map((para, pIdx) => {
            if (para.startsWith("# ")) {
              return (
                <h2 key={pIdx} className="text-base font-serif font-semibold text-ink dark:text-zinc-100 pt-2 pb-1 border-b border-hairline/60">
                  {para.replace("# ", "")}
                </h2>
              );
            }
            if (para.startsWith("## ")) {
              return (
                <h3 key={pIdx} className="text-sm font-serif font-semibold text-ink dark:text-zinc-100 pt-2 pb-1">
                  {para.replace("## ", "")}
                </h3>
              );
            }
            if (para.startsWith("- ") || para.startsWith("* ")) {
              const items = para.split("\n").filter(Boolean);
              return (
                <ul key={pIdx} className="list-disc pl-5 space-y-1 text-xs text-body dark:text-zinc-300">
                  {items.map((item, iIdx) => (
                    <li key={iIdx}>{item.replace(/^[-*]\s*/, "")}</li>
                  ))}
                </ul>
              );
            }

            return (
              <p key={pIdx} className="text-xs leading-relaxed text-body dark:text-zinc-300">
                {para}
              </p>
            );
          })}
        </div>
      );
    });
  };

  return (
    <div
      role="article"
      aria-label="Bài học đúc kết tri thức AI"
      className="p-5 rounded-lg bg-canvas dark:bg-[#1c1b18] border border-hairline dark:border-[#2f2b26] shadow-sm space-y-4 text-xs"
    >
      {/* Header */}
      <div className="flex items-start justify-between border-b border-hairline dark:border-[#2f2b26] pb-3">
        <div>
          <div className="flex items-center gap-1.5 text-[10px] font-mono text-primary uppercase tracking-wider mb-1">
            <BookOpen className="w-3.5 h-3.5" />
            <span>Bài học đúc kết tri thức ({synthesis.mode})</span>
          </div>
          <h2 className="text-base font-serif font-semibold text-ink dark:text-zinc-100 tracking-tight">
            {synthesis.title}
          </h2>
          <div className="flex items-center gap-3 text-[11px] text-muted mt-1 font-mono">
            <span className="flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              {new Date(synthesis.created_at).toLocaleDateString()}
            </span>
            <span>•</span>
            <span>{synthesis.source_note_ids.length} trích dẫn nguồn</span>
          </div>
        </div>

        {onClose && (
          <button
            type="button"
            onClick={onClose}
            aria-label="Đóng bài học"
            className="text-xs text-muted hover:text-ink px-2 py-1 rounded hover:bg-black/5"
          >
            Đóng
          </button>
        )}
      </div>

      {/* Markdown Content */}
      <div className="prose-xs space-y-3 font-sans leading-relaxed">
        {renderContent()}
      </div>

      {/* Interactive Citation Badges */}
      {synthesis.interactive_badges && synthesis.interactive_badges.length > 0 && (
        <div className="pt-3 border-t border-hairline dark:border-[#2f2b26] space-y-2">
          <h4 className="text-[11px] font-mono uppercase text-muted tracking-wider font-semibold">
            Dẫn chứng vi mô liên kết (Interactive Citations)
          </h4>
          <div className="flex flex-wrap gap-2">
            {synthesis.interactive_badges.map((badge) => (
              <button
                key={badge.badge_id}
                type="button"
                onClick={() => onJumpToBadge?.(badge)}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-mono font-medium bg-surface-soft hover:bg-surface-cream-strong dark:bg-[#262420] text-primary border border-hairline transition-colors shadow-2xs group"
                title={badge.quote_text || badge.citation_label}
              >
                <span>{badge.citation_label}</span>
                <ArrowUpRight className="w-3 h-3 text-muted group-hover:text-primary transition-colors" />
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
