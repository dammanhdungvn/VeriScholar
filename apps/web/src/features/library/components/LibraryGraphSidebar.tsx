import { useState, useMemo } from "react";
import {
  Share2,
  X,
  ChevronRight,
  Focus,
} from "lucide-react";
import type {
  LibraryGraphResponseData,
  LibraryGraphNode,
} from "../types";
import type { DocumentListItem } from "@/types/document";
import { KnowledgeGraphCanvas } from "./KnowledgeGraphCanvas";
import { PaperInspectionDrawer } from "./PaperInspectionDrawer";

export interface LibraryGraphSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  graphData: LibraryGraphResponseData | null;
  isLoading?: boolean;
  focusedNodeId?: string | null;
  onClearFocus?: () => void;
  onSelectDocument?: (doc: DocumentListItem) => void;
  onAskAI?: (prompt: string) => void;
}

export function LibraryGraphSidebar({
  isOpen,
  onClose,
  graphData,
  isLoading = false,
  focusedNodeId = null,
  onClearFocus,
  onSelectDocument,
  onAskAI,
}: LibraryGraphSidebarProps) {
  const [inspectedNode, setInspectedNode] = useState<LibraryGraphNode | null>(null);

  const nodes = useMemo(() => graphData?.nodes || [], [graphData]);
  const edges = useMemo(() => graphData?.edges || [], [graphData]);

  const focusedNode = useMemo(() => {
    if (!focusedNodeId) return null;
    return nodes.find((n) => n.id === focusedNodeId) || null;
  }, [nodes, focusedNodeId]);

  if (!isOpen) {
    return null;
  }

  const handleOpenReader = (docId: string) => {
    const doc = nodes.find((n) => n.id === docId);
    if (doc && onSelectDocument) {
      onSelectDocument({
        id: doc.id,
        filename: (doc.metadata?.filename as string) || `${doc.label}.pdf`,
        title: doc.label,
        status: "completed",
        is_persistent: true,
        created_at: new Date().toISOString(),
      });
    }
  };

  return (
    <aside
      data-testid="library-graph-sidebar"
      className="w-[380px] sm:w-[420px] shrink-0 border-l border-[#e8e4dc] dark:border-[#2e2b26] flex flex-col h-full bg-[#fdfcf9] dark:bg-[#1c1b18] overflow-hidden relative z-20 shadow-lg"
    >
      {/* 1. Sidebar Header */}
      <div className="h-14 px-4 border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#f8f6f0] dark:bg-[#1a1916] flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-[#c15f3e]/10 flex items-center justify-center text-[#c15f3e]">
            <Share2 className="w-4 h-4 stroke-[2]" />
          </div>
          <div>
            <h2 className="text-xs font-semibold font-anthropic-serif text-ink dark:text-zinc-100">
              Wiki Graph
            </h2>
            <p className="text-[10px] text-muted dark:text-zinc-400 font-mono">
              {nodes.length} nodes · {edges.length} {edges.length === 1 ? "edge" : "edges"}
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={onClose}
          aria-label="Close sidebar"
          className="p-1.5 rounded-lg text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200 hover:bg-black/5 dark:hover:bg-white/5 transition-colors cursor-pointer"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* 2. Focus Indicator Banner */}
      {focusedNode && (
        <div className="px-3 py-1.5 bg-[#f5f0e6] dark:bg-[#24201a] border-b border-[#e5decb] dark:border-[#332b20] flex items-center justify-between text-xs shrink-0">
          <div className="flex items-center gap-1.5 min-w-0 pr-2">
            <Focus className="w-3.5 h-3.5 text-[#c15f3e] shrink-0" />
            <span className="truncate text-ink dark:text-zinc-200 font-medium">
              Focused: {focusedNode.label}
            </span>
          </div>
          {onClearFocus && (
            <button
              type="button"
              onClick={onClearFocus}
              aria-label="Clear focus"
              className="text-[11px] text-[#c15f3e] hover:underline flex items-center gap-0.5 shrink-0 cursor-pointer font-medium"
            >
              <X className="w-3 h-3" />
              <span>Clear</span>
            </button>
          )}
        </div>
      )}

      {/* 3. Interactive Force-Directed Canvas */}
      <div className="flex-1 relative overflow-hidden">
        <KnowledgeGraphCanvas
          graphData={graphData}
          isLoading={isLoading}
          focusNodeId={focusedNodeId}
          onSelectDocument={(doc) => {
            onSelectDocument?.({
              id: doc.id,
              filename: doc.filename,
              title: doc.title,
              status: "completed",
              is_persistent: true,
              created_at: new Date().toISOString(),
            });
          }}
          onSelectNode={(node) => {
            setInspectedNode(node);
          }}
          className="h-full border-none rounded-none"
        />

        {/* 4. Sliding Wiki Peek Sheet Drawer */}
        <PaperInspectionDrawer
          isOpen={Boolean(inspectedNode)}
          node={inspectedNode}
          allNodes={nodes}
          allEdges={edges}
          onClose={() => setInspectedNode(null)}
          onOpenReader={handleOpenReader}
          onAskAI={onAskAI}
          onSelectNode={(nodeId) => {
            const next = nodes.find((n) => n.id === nodeId);
            if (next) setInspectedNode(next);
          }}
        />
      </div>
    </aside>
  );
}
