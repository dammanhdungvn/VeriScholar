import { useState, useMemo, useRef } from "react";
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  BookOpen,
  Target,
  FileText,
  BarChart2,
  X,
  Search,
  ExternalLink,
  Share2,
} from "lucide-react";
import type { LibraryGraphResponseData, LibraryGraphNode } from "../types";
import { cn } from "@/lib/utils";

export interface KnowledgeGraphCanvasProps {
  graphData: LibraryGraphResponseData | null;
  isLoading?: boolean;
  onSelectDocument?: (doc: { id: string; title?: string; filename: string }) => void;
  className?: string;
}

const NODE_TYPE_CONFIG: Record<
  string,
  { label: string; color: string; bg: string; border: string; icon: typeof FileText }
> = {
  Paper: {
    label: "Bài báo",
    color: "#4f46e5",
    bg: "rgba(79, 70, 229, 0.15)",
    border: "#4f46e5",
    icon: BookOpen,
  },
  Method: {
    label: "Phương pháp",
    color: "#059669",
    bg: "rgba(5, 150, 105, 0.15)",
    border: "#059669",
    icon: Target,
  },
  Dataset: {
    label: "Tập dữ liệu",
    color: "#d97706",
    bg: "rgba(217, 119, 6, 0.15)",
    border: "#d97706",
    icon: FileText,
  },
  MetricResult: {
    label: "Chỉ số",
    color: "#c15f3e",
    bg: "rgba(193, 95, 62, 0.15)",
    border: "#c15f3e",
    icon: BarChart2,
  },
};

export function KnowledgeGraphCanvas({
  graphData,
  isLoading = false,
  onSelectDocument,
  className,
}: KnowledgeGraphCanvasProps) {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [startPan, setStartPan] = useState({ x: 0, y: 0 });
  const [selectedNode, setSelectedNode] = useState<LibraryGraphNode | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState<string>("all");

  const svgRef = useRef<SVGSVGElement | null>(null);

  const nodes = useMemo(() => graphData?.nodes || [], [graphData]);
  const edges = useMemo(() => graphData?.edges || [], [graphData]);

  // Filter nodes by query and type
  const filteredNodes = useMemo(() => {
    return nodes.filter((node) => {
      const matchesSearch = searchQuery.trim()
        ? node.label.toLowerCase().includes(searchQuery.toLowerCase())
        : true;
      const matchesType = filterType === "all" ? true : node.type.toLowerCase() === filterType.toLowerCase();
      return matchesSearch && matchesType;
    });
  }, [nodes, searchQuery, filterType]);

  // Compute node 2D positions deterministically
  const nodePositions = useMemo(() => {
    const map = new Map<string, { x: number; y: number }>();
    const total = nodes.length;
    if (total === 0) return map;

    const cx = 500;
    const cy = 350;

    // Separate papers from concept/method nodes
    const papers = nodes.filter((n) => n.type === "Paper");
    const otherNodes = nodes.filter((n) => n.type !== "Paper");

    // Layout papers in an inner elliptical ring
    const pCount = Math.max(papers.length, 1);
    const rX = Math.min(260 + pCount * 15, 420);
    const rY = Math.min(180 + pCount * 12, 280);

    papers.forEach((p, i) => {
      const angle = (2 * Math.PI * i) / pCount - Math.PI / 2;
      map.set(p.id, {
        x: cx + rX * Math.cos(angle),
        y: cy + rY * Math.sin(angle),
      });
    });

    // Layout other entities (Methods, Datasets) in an outer ring or around hubs
    const oCount = Math.max(otherNodes.length, 1);
    const outRx = rX + 140;
    const outRy = rY + 110;

    otherNodes.forEach((o, i) => {
      const angle = (2 * Math.PI * i) / oCount + Math.PI / 6;
      map.set(o.id, {
        x: cx + outRx * Math.cos(angle),
        y: cy + outRy * Math.sin(angle),
      });
    });

    return map;
  }, [nodes]);

  // Find edges connected to selected node
  const connectedEdges = useMemo(() => {
    if (!selectedNode) return [];
    return edges.filter(
      (e) => e.source === selectedNode.id || e.target === selectedNode.id
    );
  }, [selectedNode, edges]);

  // Find neighbor nodes
  const neighborNodes = useMemo(() => {
    if (!selectedNode) return [];
    const neighborIds = new Set<string>();
    connectedEdges.forEach((e) => {
      if (e.source === selectedNode.id) neighborIds.add(e.target);
      if (e.target === selectedNode.id) neighborIds.add(e.source);
    });
    return nodes.filter((n) => neighborIds.has(n.id));
  }, [selectedNode, connectedEdges, nodes]);

  // Pan interaction
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.target === svgRef.current || (e.target as HTMLElement).tagName === "svg") {
      setIsPanning(true);
      setStartPan({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isPanning) {
      setPan({
        x: e.clientX - startPan.x,
        y: e.clientY - startPan.y,
      });
    }
  };

  const handleMouseUp = () => {
    setIsPanning(false);
  };

  if (isLoading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-muted">
        <div className="w-8 h-8 rounded-full border-2 border-primary border-t-transparent animate-spin mb-3" />
        <p className="text-xs">Đang nạp đồ thị tri thức LLM Wiki...</p>
      </div>
    );
  }

  if (nodes.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center bg-[#fbf9f5] dark:bg-[#181715]">
        <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center text-primary mb-4 shadow-xs">
          <Share2 className="w-8 h-8 stroke-[1.5]" />
        </div>
        <h3 className="font-serif font-semibold text-base text-ink dark:text-zinc-100 mb-1">
          Chưa có bài báo trong Đồ thị Tri thức
        </h3>
        <p className="text-xs text-muted max-w-md leading-relaxed mb-4">
          Tải lên các tài liệu PDF nghiên cứu hoặc gắn sao các bài báo yêu thích để hệ thống tự động
          kết nối tri thức theo mô hình LLM Wiki của Andrej Karpathy.
        </p>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "relative flex-1 flex flex-col h-full bg-[#fbf9f5] dark:bg-[#181715] overflow-hidden select-none",
        className
      )}
    >
      {/* Top Filter and Controls Bar */}
      <div className="h-12 px-6 border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#fdfcf9] dark:bg-[#1c1b18] flex items-center justify-between shrink-0 gap-4 z-10">
        <div className="flex items-center gap-3">
          {/* Search bar */}
          <div className="relative w-64">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-muted pointer-events-none" />
            <input
              type="text"
              placeholder="Lọc thực thể theo tên..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full h-7 pl-8 pr-3 rounded-md bg-white dark:bg-[#22201d] border border-[#e2dcd2] dark:border-[#322f2a] text-xs text-ink dark:text-zinc-100 placeholder:text-muted outline-none focus:border-primary transition-colors"
            />
          </div>

          {/* Type filters */}
          <div className="flex items-center gap-1">
            {["all", "Paper", "Method", "Dataset"].map((type) => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={cn(
                  "px-2.5 py-1 rounded text-[11px] font-medium transition-colors cursor-pointer",
                  filterType === type
                    ? "bg-primary text-white"
                    : "bg-surface dark:bg-[#252320] text-muted hover:text-ink hover:bg-black/5"
                )}
              >
                {type === "all" ? "Tất cả" : NODE_TYPE_CONFIG[type]?.label || type}
              </button>
            ))}
          </div>
        </div>

        {/* Stats & Zoom controls */}
        <div className="flex items-center gap-2">
          <span className="text-[11px] text-muted font-mono hidden sm:inline">
            {nodes.length} đỉnh • {edges.length} liên kết
          </span>
          <div className="h-4 w-px bg-border/60 mx-1 hidden sm:block" />
          <div className="flex items-center gap-1 bg-surface dark:bg-[#201e1b] rounded-lg border border-border/80 p-0.5">
            <button
              type="button"
              onClick={() => setZoom((z) => Math.min(z + 0.15, 2.5))}
              className="p-1 rounded hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink cursor-pointer"
              title="Phóng to"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => setZoom((z) => Math.max(z - 0.15, 0.4))}
              className="p-1 rounded hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink cursor-pointer"
              title="Thu nhỏ"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => {
                setZoom(1);
                setPan({ x: 0, y: 0 });
              }}
              className="p-1 rounded hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink cursor-pointer"
              title="Đặt lại góc nhìn"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* SVG Interactive Canvas */}
      <div
        className="flex-1 relative overflow-hidden cursor-grab active:cursor-grabbing"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      >
        <svg
          ref={svgRef}
          className="w-full h-full"
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transformOrigin: "center center",
            transition: isPanning ? "none" : "transform 0.15s ease-out",
          }}
        >
          {/* Arrow markers definition */}
          <defs>
            <marker
              id="graph-arrow"
              viewBox="0 0 10 10"
              refX="18"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#9ca3af" />
            </marker>
            <marker
              id="graph-arrow-active"
              viewBox="0 0 10 10"
              refX="18"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#c15f3e" />
            </marker>
          </defs>

          {/* Edges */}
          <g className="edges">
            {edges.map((edge, idx) => {
              const srcPos = nodePositions.get(edge.source);
              const tgtPos = nodePositions.get(edge.target);
              if (!srcPos || !tgtPos) return null;

              const isEdgeConnected =
                selectedNode &&
                (edge.source === selectedNode.id || edge.target === selectedNode.id);

              return (
                <g key={`edge-${idx}`}>
                  <line
                    x1={srcPos.x}
                    y1={srcPos.y}
                    x2={tgtPos.x}
                    y2={tgtPos.y}
                    stroke={isEdgeConnected ? "#c15f3e" : "#d1d5db"}
                    strokeWidth={isEdgeConnected ? 2 : 1.2}
                    strokeDasharray={edge.relation === "RELATED" ? "4,4" : undefined}
                    markerEnd={
                      isEdgeConnected ? "url(#graph-arrow-active)" : "url(#graph-arrow)"
                    }
                    className="transition-colors duration-200"
                  />
                  {edge.label && (
                    <text
                      x={(srcPos.x + tgtPos.x) / 2}
                      y={(srcPos.y + tgtPos.y) / 2 - 4}
                      fill={isEdgeConnected ? "#c15f3e" : "#9ca3af"}
                      fontSize="9"
                      textAnchor="middle"
                      className="select-none font-mono pointer-events-none"
                    >
                      {edge.label}
                    </text>
                  )}
                </g>
              );
            })}
          </g>

          {/* Nodes */}
          <g className="nodes">
            {filteredNodes.map((node) => {
              const pos = nodePositions.get(node.id);
              if (!pos) return null;

              const isSelected = selectedNode?.id === node.id;
              const isNeighbor = neighborNodes.some((n) => n.id === node.id);
              const config = NODE_TYPE_CONFIG[node.type] || NODE_TYPE_CONFIG.Paper;
              const radius = node.type === "Paper" ? 22 : 17;

              return (
                <g
                  key={node.id}
                  transform={`translate(${pos.x}, ${pos.y})`}
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedNode(isSelected ? null : node);
                  }}
                  className="cursor-pointer group"
                >
                  {/* Outer glow ring when selected or neighbor */}
                  {(isSelected || isNeighbor) && (
                    <circle
                      r={radius + 6}
                      fill="none"
                      stroke={isSelected ? "#c15f3e" : config.color}
                      strokeWidth={isSelected ? 2.5 : 1.5}
                      strokeDasharray={isSelected ? undefined : "3,3"}
                      className="animate-pulse"
                    />
                  )}

                  {/* Main Node Circle */}
                  <circle
                    r={radius}
                    fill={config.bg}
                    stroke={isSelected ? "#c15f3e" : config.border}
                    strokeWidth={isSelected ? 2.5 : 1.5}
                    className="transition-all duration-200 group-hover:scale-110 drop-shadow-xs"
                  />

                  {/* Node Label */}
                  <text
                    y={radius + 14}
                    textAnchor="middle"
                    fill="currentColor"
                    fontSize={node.type === "Paper" ? "11" : "10"}
                    fontWeight={isSelected || node.type === "Paper" ? "600" : "500"}
                    className={cn(
                      "text-ink dark:text-zinc-200 pointer-events-none font-sans drop-shadow-xs",
                      isSelected && "text-primary dark:text-primary font-bold"
                    )}
                  >
                    {node.label.length > 28
                      ? `${node.label.slice(0, 26)}...`
                      : node.label}
                  </text>
                </g>
              );
            })}
          </g>
        </svg>

        {/* Selected Node Inspector Drawer / Card */}
        {selectedNode && (
          <div className="absolute right-4 top-4 bottom-4 w-80 bg-white/95 dark:bg-[#1c1b18]/95 backdrop-blur-md rounded-xl border border-border shadow-xl flex flex-col overflow-hidden z-20 animate-in slide-in-from-right duration-200">
            <div className="h-12 px-4 border-b border-border flex items-center justify-between shrink-0 bg-surface/50">
              <div className="flex items-center gap-2">
                <span
                  className="w-2.5 h-2.5 rounded-full"
                  style={{
                    backgroundColor:
                      NODE_TYPE_CONFIG[selectedNode.type]?.color || "#4f46e5",
                  }}
                />
                <span className="font-serif font-semibold text-xs text-ink dark:text-zinc-100">
                  Chi tiết thực thể
                </span>
              </div>
              <button
                type="button"
                onClick={() => setSelectedNode(null)}
                className="p-1 rounded-md hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink cursor-pointer"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
              <div>
                <span className="text-[10px] text-muted block mb-1">Tên thực thể:</span>
                <h4 className="font-serif font-semibold text-sm text-ink dark:text-zinc-100 leading-snug">
                  {selectedNode.label}
                </h4>
              </div>

              <div className="flex items-center gap-2 text-[11px]">
                <span className="px-2 py-0.5 rounded-full bg-black/5 dark:bg-white/10 text-muted font-medium">
                  Loại: {NODE_TYPE_CONFIG[selectedNode.type]?.label || selectedNode.type}
                </span>
                <span className="px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium">
                  Bậc liên kết: {selectedNode.degree}
                </span>
              </div>

              {/* Connected Papers / Entities */}
              <div>
                <span className="text-[10px] text-muted block mb-1.5 font-medium">
                  Các liên kết ({connectedEdges.length}):
                </span>
                {connectedEdges.length === 0 ? (
                  <p className="text-[11px] text-muted italic">Chưa có liên kết phụ thuộc.</p>
                ) : (
                  <div className="space-y-1.5">
                    {connectedEdges.map((edge, idx) => {
                      const otherId =
                        edge.source === selectedNode.id ? edge.target : edge.source;
                      const otherNode = nodes.find((n) => n.id === otherId);
                      return (
                        <div
                          key={idx}
                          onClick={() => {
                            if (otherNode) setSelectedNode(otherNode);
                          }}
                          className="p-2 rounded-lg bg-surface/70 dark:bg-[#252320] border border-border/60 hover:border-primary/50 transition-colors cursor-pointer text-[11px] flex items-center justify-between"
                        >
                          <span className="truncate flex-1 font-medium text-ink dark:text-zinc-200">
                            {otherNode?.label || otherId}
                          </span>
                          <span className="ml-2 px-1.5 py-0.5 rounded bg-black/5 dark:bg-white/10 text-[9px] font-mono text-muted shrink-0">
                            {edge.label || edge.relation}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Document Action if Paper */}
              {selectedNode.type === "Paper" && onSelectDocument && (
                <div className="pt-2">
                  <button
                    type="button"
                    onClick={() => {
                      onSelectDocument({
                        id: selectedNode.id,
                        title: selectedNode.label,
                        filename: (selectedNode.metadata?.filename as string) || "document.pdf",
                      });
                    }}
                    className="w-full py-2 px-3 rounded-lg bg-primary hover:bg-primary/90 text-white font-medium flex items-center justify-center gap-1.5 transition-colors cursor-pointer shadow-xs"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                    <span>Mở đọc sâu bài báo</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
