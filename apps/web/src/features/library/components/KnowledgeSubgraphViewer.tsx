import { useState, useMemo, useRef } from "react";
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  BookOpen,
  FileText,
  Target,
  BarChart2,
  ExternalLink,
} from "lucide-react";
import type {
  GraphSubgraph,
  GraphNode,
  GraphEdge,
  EvidenceChunk,
} from "../types";
import { cn } from "@/lib/utils";

export interface KnowledgeSubgraphViewerProps {
  subgraph: GraphSubgraph;
  onEdgeSelect?: (edge: GraphEdge, evidence?: EvidenceChunk) => void;
  onNodeSelect?: (node: GraphNode) => void;
  className?: string;
  height?: number | string;
}

const TYPE_CONFIG: Record<
  string,
  { label: string; color: string; bg: string; border: string; icon: typeof FileText }
> = {
  Paper: {
    label: "Paper",
    color: "#4f46e5",
    bg: "rgba(79, 70, 229, 0.12)",
    border: "#4f46e5",
    icon: BookOpen,
  },
  Method: {
    label: "Method",
    color: "#059669",
    bg: "rgba(5, 150, 105, 0.12)",
    border: "#059669",
    icon: Target,
  },
  Dataset: {
    label: "Dataset",
    color: "#d97706",
    bg: "rgba(217, 119, 6, 0.12)",
    border: "#d97706",
    icon: FileText,
  },
  MetricResult: {
    label: "Metric",
    color: "#c15f3e",
    bg: "rgba(193, 95, 62, 0.12)",
    border: "#c15f3e",
    icon: BarChart2,
  },
};

function getNodeColor(node: GraphNode): string {
  if (node.role === "prior_work") return "#4338ca";
  if (node.role === "derivative_work") return "#6366f1";
  if (node.role === "method_hub") return "#059669";
  return TYPE_CONFIG[node.type]?.color || "#6b7280";
}

export function KnowledgeSubgraphViewer({
  subgraph,
  onEdgeSelect,
  onNodeSelect,
  className,
  height = 480,
}: KnowledgeSubgraphViewerProps) {
  const [zoom, setZoom] = useState(1);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedEdgeKey, setSelectedEdgeKey] = useState<string | null>(null);
  const [activeEvidence, setActiveEvidence] = useState<{
    edge: GraphEdge;
    evidence?: EvidenceChunk;
  } | null>(null);

  const svgRef = useRef<SVGSVGElement | null>(null);

  const { nodes, edges, evidence = [] } = subgraph;

  // Calculate coordinates deterministically
  const nodePositions = useMemo(() => {
    const map = new Map<string, { x: number; y: number }>();
    const total = nodes.length;
    if (total === 0) return map;

    const cx = 400;
    const cy = 230;

    // Categorize nodes for concentric layout
    const hubs = nodes.filter(
      (n) => n.type === "Method" || n.role === "method_hub"
    );
    const papers = nodes.filter(
      (n) => n.type === "Paper" && n.role !== "method_hub"
    );
    const datasets = nodes.filter((n) => n.type === "Dataset");
    const metrics = nodes.filter((n) => n.type === "MetricResult");

    // 1. Hubs at center
    if (hubs.length === 1) {
      map.set(hubs[0].id, { x: cx, y: cy });
    } else {
      hubs.forEach((h, i) => {
        const angle = (2 * Math.PI * i) / Math.max(hubs.length, 1);
        map.set(h.id, {
          x: cx + 75 * Math.cos(angle),
          y: cy + 75 * Math.sin(angle),
        });
      });
    }

    // 2. Papers on middle ring (r ~ 160)
    papers.forEach((p, i) => {
      const angle = (2 * Math.PI * i) / Math.max(papers.length, 1) - Math.PI / 4;
      map.set(p.id, {
        x: cx + 165 * Math.cos(angle),
        y: cy + 130 * Math.sin(angle),
      });
    });

    // 3. Datasets on left/outer orbit
    datasets.forEach((d, i) => {
      const angle = (2 * Math.PI * i) / Math.max(datasets.length, 1) + Math.PI / 3;
      map.set(d.id, {
        x: cx + 270 * Math.cos(angle),
        y: cy + 180 * Math.sin(angle),
      });
    });

    // 4. Metrics on right/outer orbit
    metrics.forEach((m, i) => {
      const angle = (2 * Math.PI * i) / Math.max(metrics.length, 1) - Math.PI / 6;
      map.set(m.id, {
        x: cx + 280 * Math.cos(angle),
        y: cy + 185 * Math.sin(angle),
      });
    });

    // Fallback for any unmapped node
    nodes.forEach((n, i) => {
      if (!map.has(n.id)) {
        const angle = (2 * Math.PI * i) / total;
        map.set(n.id, {
          x: cx + 200 * Math.cos(angle),
          y: cy + 150 * Math.sin(angle),
        });
      }
    });

    return map;
  }, [nodes]);

  const handleEdgeClick = (edge: GraphEdge) => {
    const edgeKey = `${edge.source}->${edge.target}`;
    setSelectedEdgeKey(edgeKey);

    const matchedEvidence = evidence.find(
      (ev) =>
        ev.chunk_id === edge.evidence_chunk_id ||
        (ev.document_id === edge.document_id &&
          ev.page_number === edge.page_number)
    );

    setActiveEvidence({ edge, evidence: matchedEvidence });
    onEdgeSelect?.(edge, matchedEvidence);
  };

  const handleNodeClick = (node: GraphNode) => {
    setSelectedNodeId(node.id === selectedNodeId ? null : node.id);
    onNodeSelect?.(node);
  };

  if (!nodes || nodes.length === 0) {
    return (
      <div
        style={{ height }}
        className={cn(
          "flex flex-col items-center justify-center rounded-2xl border border-dashed border-[#e2dcd2] dark:border-[#2e2b26] bg-[#fbf9f5]/50 dark:bg-[#181715]/50 text-muted p-8",
          className
        )}
      >
        <BookOpen className="w-8 h-8 opacity-40 mb-2" />
        <p className="text-xs font-medium">Chưa có dữ liệu đồ thị tri thức</p>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "relative flex flex-col rounded-2xl border border-[#e8e4dc] dark:border-[#2a2824] bg-white dark:bg-[#1c1b18] overflow-hidden select-none",
        className
      )}
      style={{ height }}
    >
      {/* 1. Header Toolbar */}
      <div className="h-10 px-4 border-b border-[#e8e4dc] dark:border-[#2a2824] bg-[#fdfcf9] dark:bg-[#1e1d1a] flex items-center justify-between shrink-0 text-xs">
        {/* Entity Legend */}
        <div className="flex items-center gap-3">
          {Object.entries(TYPE_CONFIG).map(([type, cfg]) => (
            <div key={type} className="flex items-center gap-1.5">
              <span
                className="w-2.5 h-2.5 rounded-full"
                style={{ backgroundColor: cfg.color }}
              />
              <span className="text-[11px] font-medium text-ink-muted dark:text-zinc-400">
                {cfg.label}
              </span>
            </div>
          ))}
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={() => setZoom((z) => Math.min(z + 0.15, 2.0))}
            className="p-1 rounded-md hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink dark:hover:text-zinc-200 transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <span className="text-[10px] font-mono w-9 text-center text-muted">
            {Math.round(zoom * 100)}%
          </span>
          <button
            type="button"
            onClick={() => setZoom((z) => Math.max(z - 0.15, 0.5))}
            className="p-1 rounded-md hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink dark:hover:text-zinc-200 transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={() => {
              setZoom(1);
              setSelectedNodeId(null);
              setSelectedEdgeKey(null);
            }}
            className="p-1 rounded-md hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink dark:hover:text-zinc-200 transition-colors ml-1"
            title="Reset"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* 2. Interactive SVG Canvas */}
      <div className="flex-1 w-full h-full overflow-hidden bg-[#faf8f4] dark:bg-[#181715]">
        <svg
          ref={svgRef}
          viewBox="0 0 800 460"
          className="w-full h-full cursor-grab active:cursor-grabbing"
          style={{ transform: `scale(${zoom})`, transformOrigin: "center center" }}
        >
          <defs>
            <marker
              id="arrowhead"
              markerWidth="7"
              markerHeight="6"
              refX="14"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 7 3, 0 6" fill="#9ca3af" />
            </marker>
            <marker
              id="arrowhead-active"
              markerWidth="7"
              markerHeight="6"
              refX="14"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 7 3, 0 6" fill="#c15f3e" />
            </marker>
          </defs>

          {/* Edges */}
          <g className="edges-layer">
            {edges.map((edge, idx) => {
              const src = nodePositions.get(edge.source);
              const tgt = nodePositions.get(edge.target);
              if (!src || !tgt) return null;

              const edgeKey = `${edge.source}->${edge.target}`;
              const isSelected = selectedEdgeKey === edgeKey;
              const hasEvidence = Boolean(
                edge.evidence_chunk_id || edge.page_number
              );

              // Calculate midpoint for label
              const midX = (src.x + tgt.x) / 2;
              const midY = (src.y + tgt.y) / 2;

              return (
                <g
                  key={`${edgeKey}-${idx}`}
                  data-testid="graph-edge"
                  data-edge-key={edgeKey}
                  className="cursor-pointer group"
                  onClick={() => handleEdgeClick(edge)}
                  onDoubleClick={() => handleEdgeClick(edge)}
                >
                  {/* Invisible wide line for easy click */}
                  <line
                    x1={src.x}
                    y1={src.y}
                    x2={tgt.x}
                    y2={tgt.y}
                    stroke="transparent"
                    strokeWidth={18}
                  />

                  {/* Visible Edge Line */}
                  <line
                    x1={src.x}
                    y1={src.y}
                    x2={tgt.x}
                    y2={tgt.y}
                    stroke={isSelected ? "#c15f3e" : "#cbd5e1"}
                    strokeWidth={isSelected ? 2.5 : 1.5}
                    strokeDasharray={hasEvidence ? undefined : "3 3"}
                    markerEnd={
                      isSelected
                        ? "url(#arrowhead-active)"
                        : "url(#arrowhead)"
                    }
                    className="transition-colors group-hover:stroke-[#c15f3e]"
                  />

                  {/* Edge Type Pill */}
                  <g transform={`translate(${midX}, ${midY})`}>
                    <rect
                      x={-28}
                      y={-8}
                      width={56}
                      height={16}
                      rx={4}
                      fill={isSelected ? "#c15f3e" : "#f1ede6"}
                      className="dark:fill-[#2d2a25] transition-colors"
                    />
                    <text
                      textAnchor="middle"
                      y={3}
                      fontSize={8}
                      fontFamily="monospace"
                      fontWeight="600"
                      fill={isSelected ? "#ffffff" : "#64748b"}
                      className="select-none pointer-events-none"
                    >
                      {edge.type}
                    </text>
                  </g>
                </g>
              );
            })}
          </g>

          {/* Nodes */}
          <g className="nodes-layer">
            {nodes.map((node) => {
              const pos = nodePositions.get(node.id) || { x: 400, y: 230 };
              const color = getNodeColor(node);

              // Radius proportional to degree_centrality
              // Degree centrality usually ranges from 1 to 20
              const centrality = node.degree_centrality ?? 2;
              const radius = Math.max(14, Math.min(36, 14 + centrality * 1.5));

              const isSelected = selectedNodeId === node.id;

              return (
                <g
                  key={node.id}
                  data-node-id={node.id}
                  data-node-type={node.type}
                  transform={`translate(${pos.x}, ${pos.y})`}
                  className="cursor-pointer group"
                  onClick={() => handleNodeClick(node)}
                >
                  {/* Selection Ring */}
                  {isSelected && (
                    <circle
                      r={radius + 5}
                      fill="none"
                      stroke={color}
                      strokeWidth={2}
                      strokeDasharray="4 2"
                      opacity={0.8}
                    />
                  )}

                  {/* Node Circle */}
                  <circle
                    r={radius}
                    fill={color}
                    opacity={isSelected ? 0.95 : 0.85}
                    stroke="#ffffff"
                    strokeWidth={2}
                    className="transition-all duration-200 group-hover:opacity-100 group-hover:scale-105"
                  />

                  {/* Centrality Badge in node center */}
                  {centrality > 1 && (
                    <text
                      textAnchor="middle"
                      y={4}
                      fontSize={radius > 22 ? 10 : 8}
                      fill="#ffffff"
                      fontWeight="bold"
                      className="pointer-events-none select-none font-mono"
                    >
                      {centrality}
                    </text>
                  )}

                  {/* Label Text below node */}
                  <g transform={`translate(0, ${radius + 12})`}>
                    <rect
                      x={-Math.min(node.name.length * 3.5, 120)}
                      y={-9}
                      width={Math.min(node.name.length * 7, 240)}
                      height={15}
                      rx={3}
                      fill="#ffffff"
                      className="dark:fill-[#201e1a] opacity-80"
                    />
                    <text
                      textAnchor="middle"
                      fontSize={10}
                      fontWeight="500"
                      fill="#1f2937"
                      className="dark:fill-zinc-200 select-none pointer-events-none font-sans"
                    >
                      {node.name}
                    </text>
                  </g>
                </g>
              );
            })}
          </g>
        </svg>
      </div>

      {/* 3. Evidence Bounding Box Toast / Dock */}
      {activeEvidence && (
        <div className="absolute bottom-3 left-3 right-3 p-3 bg-white/95 dark:bg-[#201e1a]/95 backdrop-blur-md rounded-xl border border-[#c15f3e]/40 shadow-lg flex items-center justify-between text-xs animate-in fade-in duration-200">
          <div className="flex items-start gap-2.5 min-w-0 flex-1 pr-3">
            <span className="w-2 h-2 rounded-full bg-[#c15f3e] shrink-0 mt-1" />
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-ink dark:text-zinc-100 font-mono">
                  {activeEvidence.edge.type}
                </span>
                {activeEvidence.edge.page_number && (
                  <span className="px-1.5 py-0.5 rounded bg-black/5 dark:bg-white/10 text-[10px] font-mono text-muted">
                    Trang {activeEvidence.edge.page_number}
                  </span>
                )}
                {activeEvidence.evidence?.bbox && (
                  <span className="px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-700 dark:text-amber-400 text-[10px] font-medium">
                    Bounding Box viền vàng
                  </span>
                )}
              </div>
              {activeEvidence.evidence?.chunk_text && (
                <p className="text-[11px] text-muted dark:text-zinc-400 truncate mt-0.5 max-w-xl">
                  &ldquo;{activeEvidence.evidence.chunk_text}&rdquo;
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {activeEvidence.edge.document_id && (
              <button
                type="button"
                onClick={() =>
                  onEdgeSelect?.(
                    activeEvidence.edge,
                    activeEvidence.evidence
                  )
                }
                className="px-2.5 py-1 rounded-lg bg-[#c15f3e] hover:bg-[#a84f32] text-white text-[11px] font-medium flex items-center gap-1 transition-colors"
              >
                <span>Mở PDF</span>
                <ExternalLink className="w-3 h-3" />
              </button>
            )}
            <button
              type="button"
              onClick={() => setActiveEvidence(null)}
              className="p-1 rounded-lg hover:bg-black/5 dark:hover:bg-white/5 text-muted"
            >
              &times;
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
