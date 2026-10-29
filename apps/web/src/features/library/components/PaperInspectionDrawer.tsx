import { useMemo } from "react";
import {
  X,
  BookOpen,
  Sparkles,
  ExternalLink,
  GitFork,
  ArrowUpRight,
  ArrowDownLeft,
  Calendar,
  Layers,
} from "lucide-react";
import type { LibraryGraphNode, LibraryGraphEdge } from "../types";
import { AcademicMarkdownRenderer } from "@/components/shared/AcademicMarkdownRenderer";

export interface PaperInspectionDrawerProps {
  isOpen: boolean;
  node: LibraryGraphNode | null;
  allNodes?: LibraryGraphNode[];
  allEdges?: LibraryGraphEdge[];
  onClose: () => void;
  onOpenReader?: (docId: string) => void;
  onAskAI?: (prompt: string) => void;
  onSelectNode?: (nodeId: string) => void;
  onViewWiki?: (node: LibraryGraphNode) => void;
}

export function PaperInspectionDrawer({
  isOpen,
  node,
  allNodes = [],
  allEdges = [],
  onClose,
  onOpenReader,
  onAskAI,
  onSelectNode,
  onViewWiki,
}: PaperInspectionDrawerProps) {
  // Derive connected nodes from edges
  const { priorWorks, derivativeWorks, connectedConcepts } = useMemo(() => {
    if (!node) {
      return { priorWorks: [], derivativeWorks: [], connectedConcepts: [] };
    }
    const nodeMap = new Map(allNodes.map((n) => [n.id, n]));
    const prior: LibraryGraphNode[] = [];
    const derivative: LibraryGraphNode[] = [];
    const concepts: LibraryGraphNode[] = [];

    allEdges.forEach((edge) => {
      if (edge.source === node.id) {
        const target = nodeMap.get(edge.target);
        if (target) {
          if (target.type === "Paper") {
            prior.push(target);
          } else {
            concepts.push(target);
          }
        }
      } else if (edge.target === node.id) {
        const source = nodeMap.get(edge.source);
        if (source) {
          if (source.type === "Paper") {
            derivative.push(source);
          } else {
            concepts.push(source);
          }
        }
      }
    });

    return {
      priorWorks: prior,
      derivativeWorks: derivative,
      connectedConcepts: concepts,
    };
  }, [node, allNodes, allEdges]);

  if (!isOpen || !node) {
    return null;
  }

  const year = node.metadata?.publication_year;
  const abstract = node.metadata?.abstract || "No abstract available for this entity.";
  const citations = node.citation_count ?? node.degree ?? 0;

  return (
    <div
      data-testid="paper-inspection-drawer"
      className="absolute inset-0 z-30 flex flex-col bg-[#fdfcf9] dark:bg-[#1a1916] border-l border-[#e8e4dc] dark:border-[#2e2b26] shadow-xl animate-in slide-in-from-right duration-200 overflow-hidden"
    >
      {/* 1. Header Bar */}
      <div className="h-12 px-4 border-b border-[#ece8df] dark:border-[#282622] flex items-center justify-between shrink-0 bg-[#f8f6f0] dark:bg-[#1f1d1a]">
        <div className="flex items-center gap-2 overflow-hidden">
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-medium uppercase tracking-wider bg-[#e8e4dc] dark:bg-[#2e2b26] text-ink dark:text-zinc-300">
            {node.type}
          </span>
          {node.community_label && (
            <span className="text-xs text-[#c15f3e] font-medium truncate max-w-[180px]">
              {node.community_label}
            </span>
          )}
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close inspection drawer"
          className="p-1 rounded-md text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200 hover:bg-black/5 dark:hover:bg-white/5 transition-colors cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* 2. Scrollable Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs select-text">
        {/* Title */}
        <div>
          <h3 className="text-sm font-semibold font-anthropic-serif text-ink dark:text-zinc-100 leading-snug">
            {node.label}
          </h3>
          <div className="flex flex-wrap items-center gap-3 mt-2 text-muted dark:text-zinc-400 text-[11px]">
            {year && (
              <div className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                <span>{year}</span>
              </div>
            )}
            <div className="flex items-center gap-1 font-mono">
              <GitFork className="w-3 h-3" />
              <span>{citations} citations</span>
            </div>
          </div>
        </div>

        {/* Abstract */}
        <div className="space-y-1.5 pt-2 border-t border-[#ece8df] dark:border-[#282622]">
          <span className="text-[11px] font-medium font-anthropic-serif text-ink-muted dark:text-zinc-400">
            Abstract & Summary
          </span>
          <div className="p-3 rounded-xl bg-[#f5f2eb] dark:bg-[#23211d] text-ink dark:text-zinc-200 text-xs leading-relaxed max-h-48 overflow-y-auto">
            <AcademicMarkdownRenderer content={abstract} />
          </div>
        </div>

        {/* Prior Works */}
        {priorWorks.length > 0 && (
          <div className="space-y-1.5 pt-2 border-t border-[#ece8df] dark:border-[#282622]">
            <span className="text-[11px] font-medium text-ink-muted dark:text-zinc-400 flex items-center gap-1">
              <ArrowDownLeft className="w-3 h-3 text-[#059669]" />
              <span>Prior Works Cited ({priorWorks.length})</span>
            </span>
            <div className="space-y-1">
              {priorWorks.map((p) => (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => onSelectNode?.(p.id)}
                  className="w-full text-left p-1.5 rounded-lg bg-white dark:bg-[#201e1a] border border-[#e8e4dc] dark:border-[#2e2b26] hover:border-[#c15f3e] transition-colors flex items-center justify-between group cursor-pointer"
                >
                  <span className="truncate pr-2 font-medium text-ink dark:text-zinc-200">
                    {p.label}
                  </span>
                  <ExternalLink className="w-3 h-3 text-muted group-hover:text-[#c15f3e] shrink-0" />
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Derivative Works (Citing Papers) */}
        {derivativeWorks.length > 0 && (
          <div className="space-y-1.5 pt-2 border-t border-[#ece8df] dark:border-[#282622]">
            <span className="text-[11px] font-medium text-ink-muted dark:text-zinc-400 flex items-center gap-1">
              <ArrowUpRight className="w-3 h-3 text-[#4f46e5]" />
              <span>Derivative Citations ({derivativeWorks.length})</span>
            </span>
            <div className="space-y-1">
              {derivativeWorks.map((d) => (
                <button
                  key={d.id}
                  type="button"
                  onClick={() => onSelectNode?.(d.id)}
                  className="w-full text-left p-1.5 rounded-lg bg-white dark:bg-[#201e1a] border border-[#e8e4dc] dark:border-[#2e2b26] hover:border-[#c15f3e] transition-colors flex items-center justify-between group cursor-pointer"
                >
                  <span className="truncate pr-2 font-medium text-ink dark:text-zinc-200">
                    {d.label}
                  </span>
                  <ExternalLink className="w-3 h-3 text-muted group-hover:text-[#c15f3e] shrink-0" />
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Connected Concepts */}
        {connectedConcepts.length > 0 && (
          <div className="space-y-1.5 pt-2 border-t border-[#ece8df] dark:border-[#282622]">
            <span className="text-[11px] font-medium text-ink-muted dark:text-zinc-400 flex items-center gap-1">
              <Layers className="w-3 h-3 text-[#d97706]" />
              <span>Methods & Datasets ({connectedConcepts.length})</span>
            </span>
            <div className="flex flex-wrap gap-1.5">
              {connectedConcepts.map((c) => (
                <span
                  key={c.id}
                  className="px-2 py-0.5 rounded-md text-[11px] bg-white dark:bg-[#201e1a] border border-[#e8e4dc] dark:border-[#2e2b26] text-ink dark:text-zinc-300"
                >
                  {c.label}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 3. Action Bar */}
      <div className="p-3 border-t border-[#ece8df] dark:border-[#282622] bg-[#f8f6f0] dark:bg-[#1a1916] flex items-center gap-2 shrink-0">
        <button
          type="button"
          onClick={() => onOpenReader?.(node.id)}
          className="flex-1 h-8 px-3 rounded-lg bg-[#c15f3e] hover:bg-[#a84f32] text-white font-medium text-xs flex items-center justify-center gap-1.5 shadow-xs transition-colors cursor-pointer"
        >
          <BookOpen className="w-3.5 h-3.5" />
          <span>Open in Deep Reader</span>
        </button>

        {onViewWiki && (
          <button
            type="button"
            onClick={() => onViewWiki(node)}
            className="h-8 px-2.5 rounded-lg border border-[#e2dcd2] dark:border-[#33302b] bg-white dark:bg-[#201e1a] text-ink dark:text-zinc-200 hover:bg-[#f5f2eb] dark:hover:bg-[#282622] font-medium text-xs flex items-center justify-center gap-1.5 shadow-xs transition-colors cursor-pointer"
            title="Xem bài viết trên Wiki"
          >
            <BookOpen className="w-3.5 h-3.5 text-[#c15f3e]" />
            <span className="hidden sm:inline">Wiki ↗</span>
          </button>
        )}

        <button
          type="button"
          onClick={() =>
            onAskAI?.(
              `Phân tích chi tiết đóng góp, phương pháp luận và các kết quả cốt lõi của bài báo "${node.label}".`
            )
          }
          className="h-8 px-3 rounded-lg border border-[#e2dcd2] dark:border-[#33302b] bg-white dark:bg-[#201e1a] text-ink dark:text-zinc-200 hover:bg-[#f5f2eb] dark:hover:bg-[#282622] font-medium text-xs flex items-center justify-center gap-1.5 shadow-xs transition-colors cursor-pointer"
          title="Ask AI About Paper"
        >
          <Sparkles className="w-3.5 h-3.5 text-[#c15f3e]" />
          <span>Ask AI About Paper</span>
        </button>
      </div>
    </div>
  );
}
