import { useState, useMemo, useRef, useEffect, useCallback } from "react";
import {
  forceSimulation,
  forceLink,
  forceManyBody,
  forceCenter,
  forceCollide,
  type SimulationNodeDatum,
  type SimulationLinkDatum,
} from "d3-force";
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Search,
  Filter,
} from "lucide-react";
import type {
  LibraryGraphResponseData,
  LibraryGraphNode,
  LibraryCommunity,
} from "../types";
import { cn } from "@/lib/utils";

export interface KnowledgeGraphCanvasProps {
  graphData: LibraryGraphResponseData | null;
  isLoading?: boolean;
  focusNodeId?: string | null;
  onSelectDocument?: (doc: { id: string; title?: string; filename: string }) => void;
  onSelectNode?: (node: LibraryGraphNode) => void;
  onSelectCommunity?: (community: LibraryCommunity) => void;
  className?: string;
}

interface SimNode extends SimulationNodeDatum {
  id: string;
  label: string;
  type: string;
  degree: number;
  citation_count: number;
  community_id?: number | null;
  community_label?: string | null;
  metadata?: Record<string, unknown>;
  radius: number;
  color: string;
}

interface SimLink extends SimulationLinkDatum<SimNode> {
  source: string | SimNode;
  target: string | SimNode;
  relation: string;
  label: string;
  weight: number;
}

const COMMUNITY_PALETTE = [
  "#c15f3e", // Coral
  "#4f46e5", // Indigo
  "#059669", // Emerald
  "#d97706", // Amber
  "#e11d48", // Rose
  "#0891b2", // Cyan
  "#7c3aed", // Purple
  "#2563eb", // Blue
];

const NODE_TYPE_COLORS: Record<string, string> = {
  Paper: "#4f46e5",
  Method: "#059669",
  Dataset: "#d97706",
  MetricResult: "#c15f3e",
};

const ENTITY_TYPE_FILTERS = [
  { id: "all", label: "Tất cả" },
  { id: "Paper", label: "Bài báo" },
  { id: "Method", label: "Phương pháp" },
  { id: "Dataset", label: "Tập dữ liệu" },
  { id: "MetricResult", label: "Chỉ số" },
];

export function KnowledgeGraphCanvas({
  graphData,
  isLoading = false,
  focusNodeId = null,
  onSelectDocument,
  onSelectNode,
  onSelectCommunity,
  className,
}: KnowledgeGraphCanvasProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedEntityType, setSelectedEntityType] = useState<string>("all");
  const [selectedCommunityId, setSelectedCommunityId] = useState<number | null>(null);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);

  // References for mutable simulation state
  const simNodesRef = useRef<SimNode[]>([]);
  const simLinksRef = useRef<SimLink[]>([]);
  const simulationRef = useRef<ReturnType<typeof forceSimulation<SimNode>> | null>(null);
  const isDraggingNodeRef = useRef<SimNode | null>(null);
  const isPanningRef = useRef(false);
  const dragStartPosRef = useRef({ x: 0, y: 0, panX: 0, panY: 0 });
  const hasMovedSignificantlyRef = useRef(false);
  const zoomRef = useRef(zoom);
  const panRef = useRef(pan);
  zoomRef.current = zoom;
  panRef.current = pan;

  const rawNodes = useMemo(() => graphData?.nodes || [], [graphData]);
  const rawEdges = useMemo(() => graphData?.edges || [], [graphData]);
  const communities = useMemo(() => graphData?.communities || [], [graphData]);

  // Compute 1-hop adjacency for spotlight highlighting
  const adjacencyMap = useMemo(() => {
    const map = new Map<string, Set<string>>();
    rawNodes.forEach((n) => map.set(n.id, new Set()));
    rawEdges.forEach((e) => {
      map.get(e.source)?.add(e.target);
      map.get(e.target)?.add(e.source);
    });
    return map;
  }, [rawNodes, rawEdges]);

  // Initialize or re-create simulation when graphData changes
  useEffect(() => {
    if (!containerRef.current || rawNodes.length === 0) {
      simNodesRef.current = [];
      simLinksRef.current = [];
      if (simulationRef.current) simulationRef.current.stop();
      return;
    }

    const rect = containerRef.current.getBoundingClientRect();
    const width = rect.width || 600;
    const height = rect.height || 500;

    // Build SimNodes
    const nodesMap = new Map<string, SimNode>();
    const simNodes: SimNode[] = rawNodes.map((n) => {
      const citationCount = n.citation_count || 0;
      const radius = Math.max(12, Math.min(28, 12 + citationCount * 1.2));
      const color =
        n.community_id !== undefined && n.community_id !== null
          ? COMMUNITY_PALETTE[Math.abs(n.community_id) % COMMUNITY_PALETTE.length]
          : NODE_TYPE_COLORS[n.type] || "#4f46e5";

      const node: SimNode = {
        id: n.id,
        label: n.label,
        type: n.type,
        degree: n.degree,
        citation_count: citationCount,
        community_id: n.community_id,
        community_label: n.community_label,
        metadata: n.metadata,
        radius,
        color,
        x: width / 2 + (Math.random() - 0.5) * 150,
        y: height / 2 + (Math.random() - 0.5) * 150,
      };
      nodesMap.set(n.id, node);
      return node;
    });

    // Build SimLinks (filter out invalid targets)
    const simLinks: SimLink[] = rawEdges
      .filter((e) => nodesMap.has(e.source) && nodesMap.has(e.target))
      .map((e) => ({
        source: e.source,
        target: e.target,
        relation: e.relation,
        label: e.label,
        weight: e.weight || 1.0,
      }));

    simNodesRef.current = simNodes;
    simLinksRef.current = simLinks;

    if (simulationRef.current) {
      simulationRef.current.stop();
    }

    const sim = forceSimulation<SimNode>(simNodes)
      .force(
        "link",
        forceLink<SimNode, SimLink>(simLinks)
          .id((d) => d.id)
          .distance(90)
          .strength(0.35)
      )
      .force("charge", forceManyBody().strength(-280))
      .force("center", forceCenter(width / 2, height / 2).strength(0.08))
      .force(
        "collision",
        forceCollide<SimNode>()
          .radius((d) => d.radius + 14)
          .iterations(3)
      )
      .alphaDecay(0.024);

    simulationRef.current = sim;

    return () => {
      sim.stop();
    };
  }, [rawNodes, rawEdges]);

  // Center on focusNodeId when changed
  useEffect(() => {
    if (!focusNodeId || simNodesRef.current.length === 0 || !containerRef.current) return;
    const target = simNodesRef.current.find((n) => n.id === focusNodeId);
    if (target && target.x !== undefined && target.y !== undefined) {
      const rect = containerRef.current.getBoundingClientRect();
      const targetPanX = rect.width / 2 - target.x * zoomRef.current;
      const targetPanY = rect.height / 2 - target.y * zoomRef.current;
      setPan({ x: targetPanX, y: targetPanY });
    }
  }, [focusNodeId]);

  // 60fps HTML5 Canvas Render Loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    let ctx: CanvasRenderingContext2D | null = null;
    try {
      ctx = canvas.getContext("2d");
    } catch {
      ctx = null;
    }
    if (!ctx) return;

    let animationFrameId: number;

    const renderFrame = () => {
      const rect = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      const displayWidth = rect.width;
      const displayHeight = rect.height;

      if (canvas.width !== displayWidth * dpr || canvas.height !== displayHeight * dpr) {
        canvas.width = displayWidth * dpr;
        canvas.height = displayHeight * dpr;
      }

      ctx.save();
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.scale(dpr, dpr);

      // Apply zoom & pan transform
      ctx.translate(panRef.current.x, panRef.current.y);
      ctx.scale(zoomRef.current, zoomRef.current);

      const activeHoverId = hoveredNodeId || focusNodeId;
      const spotlightNeighbors = activeHoverId ? adjacencyMap.get(activeHoverId) : null;

      // 1. Render Community Soft Halos
      const nodes = simNodesRef.current;
      nodes.forEach((n) => {
        if (n.x === undefined || n.y === undefined) return;
        const isDimmed =
          (selectedCommunityId !== null && n.community_id !== selectedCommunityId) ||
          (activeHoverId && activeHoverId !== n.id && !spotlightNeighbors?.has(n.id));

        if (!isDimmed) {
          ctx.beginPath();
          ctx.arc(n.x, n.y, n.radius * 1.8, 0, 2 * Math.PI);
          ctx.fillStyle = `${n.color}15`; // Translucent halo
          ctx.fill();
        }
      });

      // 2. Render Edges with directional arrows
      const links = simLinksRef.current;
      links.forEach((link) => {
        const s = link.source as SimNode;
        const t = link.target as SimNode;
        if (s.x === undefined || s.y === undefined || t.x === undefined || t.y === undefined)
          return;

        const isLinkActive =
          activeHoverId && (s.id === activeHoverId || t.id === activeHoverId);
        const isDimmed =
          activeHoverId && !isLinkActive;

        ctx.save();
        ctx.beginPath();
        ctx.moveTo(s.x, s.y);
        ctx.lineTo(t.x, t.y);
        ctx.strokeStyle = isLinkActive
          ? "#4f46e5"
          : isDimmed
          ? "#e5e7eb40"
          : "#d1d5db80";
        ctx.lineWidth = isLinkActive ? 2.0 : 1.2;
        ctx.stroke();

        // Edge relation label for active links
        if (isLinkActive) {
          const midX = (s.x + t.x) / 2;
          const midY = (s.y + t.y) / 2;
          ctx.font = "9px 'Anthropic Mono', ui-monospace, monospace";
          ctx.fillStyle = "#6b7280";
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillText(link.label || link.relation, midX, midY - 6);
        }
        ctx.restore();
      });

      // 3. Render Nodes
      nodes.forEach((n) => {
        if (n.x === undefined || n.y === undefined) return;

        const isFocus = n.id === focusNodeId;
        const isHovered = n.id === hoveredNodeId;
        const isNeighbor = activeHoverId ? spotlightNeighbors?.has(n.id) : false;
        const matchesEntity =
          selectedEntityType === "all" || n.type === selectedEntityType;
        const isDimmed =
          !matchesEntity ||
          (selectedCommunityId !== null && n.community_id !== selectedCommunityId) ||
          (activeHoverId && !isHovered && !isFocus && !isNeighbor);

        const alpha = isDimmed ? 0.2 : 1.0;
        ctx.save();
        ctx.globalAlpha = alpha;

        // Outer stroke ring
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius, 0, 2 * Math.PI);
        ctx.fillStyle = isHovered || isFocus ? n.color : `${n.color}22`;
        ctx.fill();
        ctx.lineWidth = isHovered || isFocus ? 2.5 : 1.5;
        ctx.strokeStyle = n.color;
        ctx.stroke();

        // Node Label
        const query = searchQuery.trim().toLowerCase();
        const matchesSearch = query && n.label.toLowerCase().includes(query);

        ctx.font = `${
          isHovered || isFocus ? "bold 11px" : "10px"
        } 'Anthropic Sans', system-ui, sans-serif`;

        const truncatedLabel =
          n.label.length > 24 ? `${n.label.slice(0, 22)}…` : n.label;
        const textMetrics = ctx.measureText(truncatedLabel);
        const textWidth = textMetrics.width;

        // Subtle background pill for crystal clear text readability over edges
        ctx.fillStyle = "rgba(253, 252, 249, 0.88)";
        ctx.fillRect(
          n.x - textWidth / 2 - 3,
          n.y + n.radius + 3,
          textWidth + 6,
          13
        );

        ctx.fillStyle = matchesSearch
          ? "#c15f3e"
          : isHovered || isFocus
          ? "#111827"
          : "#374151";
        ctx.textAlign = "center";
        ctx.textBaseline = "top";
        ctx.fillText(truncatedLabel, n.x, n.y + n.radius + 4);

        ctx.restore();
      });

      ctx.restore();

      animationFrameId = requestAnimationFrame(renderFrame);
    };

    animationFrameId = requestAnimationFrame(renderFrame);

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [hoveredNodeId, focusNodeId, selectedCommunityId, searchQuery, adjacencyMap]);

  // Coordinate conversion helper: client pos -> simulation graph pos
  const clientToGraphPos = useCallback(
    (clientX: number, clientY: number) => {
      const canvas = canvasRef.current;
      if (!canvas) return { x: 0, y: 0 };
      const rect = canvas.getBoundingClientRect();
      const xOnCanvas = clientX - rect.left;
      const yOnCanvas = clientY - rect.top;
      const graphX = (xOnCanvas - panRef.current.x) / zoomRef.current;
      const graphY = (yOnCanvas - panRef.current.y) / zoomRef.current;
      return { x: graphX, y: graphY };
    },
    []
  );

  // Find node under pointer
  const findNodeAtPos = useCallback(
    (graphX: number, graphY: number): SimNode | null => {
      for (const node of simNodesRef.current) {
        if (node.x === undefined || node.y === undefined) continue;
        const dx = graphX - node.x;
        const dy = graphY - node.y;
        if (Math.hypot(dx, dy) <= node.radius + 4) {
          return node;
        }
      }
      return null;
    },
    []
  );

  // Pointer event handlers
  const handlePointerDown = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const { x, y } = clientToGraphPos(e.clientX, e.clientY);
    const hitNode = findNodeAtPos(x, y);

    hasMovedSignificantlyRef.current = false;
    dragStartPosRef.current = {
      x: e.clientX,
      y: e.clientY,
      panX: pan.x,
      panY: pan.y,
    };

    if (hitNode) {
      isDraggingNodeRef.current = hitNode;
      hitNode.fx = hitNode.x;
      hitNode.fy = hitNode.y;
      if (simulationRef.current) {
        simulationRef.current.alphaTarget(0.3).restart();
      }
    } else {
      isPanningRef.current = true;
    }

    (e.target as HTMLElement).setPointerCapture(e.pointerId);
  };

  const handlePointerMove = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const dist = Math.hypot(
      e.clientX - dragStartPosRef.current.x,
      e.clientY - dragStartPosRef.current.y
    );
    if (dist > 5) {
      hasMovedSignificantlyRef.current = true;
    }

    if (isDraggingNodeRef.current) {
      const { x, y } = clientToGraphPos(e.clientX, e.clientY);
      isDraggingNodeRef.current.fx = x;
      isDraggingNodeRef.current.fy = y;
    } else if (isPanningRef.current) {
      const dx = e.clientX - dragStartPosRef.current.x;
      const dy = e.clientY - dragStartPosRef.current.y;
      setPan({
        x: dragStartPosRef.current.panX + dx,
        y: dragStartPosRef.current.panY + dy,
      });
    } else {
      // Hover detection
      const { x, y } = clientToGraphPos(e.clientX, e.clientY);
      const hit = findNodeAtPos(x, y);
      setHoveredNodeId(hit ? hit.id : null);
    }
  };

  const handlePointerUp = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (isDraggingNodeRef.current) {
      const dragged = isDraggingNodeRef.current;
      dragged.fx = null;
      dragged.fy = null;
      isDraggingNodeRef.current = null;
      if (simulationRef.current) {
        simulationRef.current.alphaTarget(0);
      }

      // If user simply clicked the node without significant drag
      if (!hasMovedSignificantlyRef.current) {
        const fullNode = rawNodes.find((n) => n.id === dragged.id);
        if (fullNode) {
          onSelectNode?.(fullNode);
          if (fullNode.type === "Paper") {
            const filename =
              (fullNode.metadata?.filename as string) || `${fullNode.label}.pdf`;
            onSelectDocument?.({
              id: fullNode.id,
              title: fullNode.label,
              filename,
            });
          }
        }
      }
    }

    isPanningRef.current = false;
    try {
      (e.target as HTMLElement).releasePointerCapture(e.pointerId);
    } catch {
      // benign
    }
  };

  // Zoom via wheel
  const handleWheel = (e: React.WheelEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
    setZoom((prev) => Math.max(0.3, Math.min(3.5, prev * zoomFactor)));
  };

  // Toolbar Actions
  const handleZoomIn = () => setZoom((z) => Math.min(3.5, z * 1.25));
  const handleZoomOut = () => setZoom((z) => Math.max(0.3, z * 0.8));
  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
    setSelectedCommunityId(null);
    setSearchQuery("");
  };

  return (
    <div
      ref={containerRef}
      className={cn(
        "relative flex flex-col h-full w-full bg-[#fbf9f5] dark:bg-[#181715] overflow-hidden select-none",
        className
      )}
    >
      {/* Top Bar: Search, Entity Filter Tabs, and Controls */}
      <div className="px-3 py-2 border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#fdfcf9] dark:bg-[#1c1b18] flex flex-wrap items-center justify-between gap-2 shrink-0 z-10">
        <div className="flex flex-wrap items-center gap-2 flex-1 min-w-[200px]">
          <div className="relative flex-1 max-w-xs min-w-[140px]">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-muted pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Lọc thực thể theo tên..."
              className="w-full h-7 pl-8 pr-3 rounded-md bg-white dark:bg-[#22201d] border border-[#e2dcd2] dark:border-[#322f2a] text-xs text-ink dark:text-zinc-100 placeholder:text-muted outline-none focus:border-primary transition-colors"
            />
          </div>

          {/* Entity Type Filter Tabs */}
          <div className="flex items-center gap-0.5 bg-[#ede8df]/60 dark:bg-[#252320] p-0.5 rounded-lg border border-[#e2dcd2]/70 dark:border-[#322f2a]">
            {ENTITY_TYPE_FILTERS.map((f) => (
              <button
                key={f.id}
                type="button"
                onClick={() => setSelectedEntityType(f.id)}
                className={cn(
                  "px-2 py-0.5 rounded-md text-[11px] font-medium transition-colors cursor-pointer",
                  selectedEntityType === f.id
                    ? "bg-[#c15f3e] text-white shadow-2xs"
                    : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200"
                )}
              >
                {f.label}
              </button>
            ))}
          </div>

          <span className="text-[11px] text-muted font-mono whitespace-nowrap">
            {rawNodes.length} đỉnh • {rawEdges.length} liên kết
          </span>
        </div>

        {/* Zoom & Reset Controls */}
        <div className="flex items-center gap-1 bg-surface dark:bg-[#201e1b] rounded-md border border-border/80 p-0.5">
          <button
            type="button"
            onClick={handleZoomIn}
            className="p-1 rounded hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink cursor-pointer"
            title="Phóng to"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={handleZoomOut}
            className="p-1 rounded hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink cursor-pointer"
            title="Thu nhỏ"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={handleReset}
            className="p-1 rounded hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink cursor-pointer"
            title="Đặt lại khung nhìn"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Community Ribbon Filter */}
      {communities.length > 0 && (
        <div className="px-3 py-1.5 border-b border-[#e8e4dc]/70 dark:border-[#2e2b26]/70 bg-[#fbf9f5] dark:bg-[#181715] flex items-center gap-1.5 overflow-x-auto text-[11px] scrollbar-none shrink-0 z-10">
          <Filter className="w-3 h-3 text-muted shrink-0" />
          <button
            type="button"
            onClick={() => setSelectedCommunityId(null)}
            className={cn(
              "px-2 py-0.5 rounded-full text-[10px] font-medium transition-colors cursor-pointer shrink-0",
              selectedCommunityId === null
                ? "bg-primary text-white"
                : "bg-surface dark:bg-[#252320] text-muted hover:text-ink"
            )}
          >
            Tất cả cộng đồng
          </button>
          {communities.map((c) => {
            const isSelected = selectedCommunityId === c.id;
            const dotColor =
              COMMUNITY_PALETTE[Math.abs(c.id) % COMMUNITY_PALETTE.length];
            return (
              <button
                key={c.id}
                type="button"
                onClick={() => {
                  setSelectedCommunityId(isSelected ? null : c.id);
                  onSelectCommunity?.(c);
                }}
                className={cn(
                  "flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-medium transition-colors cursor-pointer shrink-0 border",
                  isSelected
                    ? "bg-primary/10 border-primary text-primary dark:text-zinc-100"
                    : "border-border/60 bg-white/60 dark:bg-[#201e1b] text-muted hover:text-ink"
                )}
              >
                <span
                  className="w-1.5 h-1.5 rounded-full shrink-0"
                  style={{ backgroundColor: dotColor }}
                />
                <span className="truncate max-w-[120px]">{c.label}</span>
                <span className="text-[9px] opacity-70 font-mono">({c.paper_count})</span>
              </button>
            );
          })}
        </div>
      )}

      {/* Simulation HTML5 Canvas */}
      <div className="relative flex-1 w-full h-full min-h-[300px]">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white/60 dark:bg-black/60 z-20 backdrop-blur-xs">
            <span className="text-xs text-muted animate-pulse">
              Đang tải đồ thị tri thức...
            </span>
          </div>
        )}
        <canvas
          ref={canvasRef}
          data-testid="knowledge-graph-canvas"
          onPointerDown={handlePointerDown}
          onPointerMove={handlePointerMove}
          onPointerUp={handlePointerUp}
          onWheel={handleWheel}
          className="w-full h-full cursor-grab active:cursor-grabbing block"
        />
      </div>
    </div>
  );
}
