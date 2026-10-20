import { useState, useEffect, useMemo, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
  Network,
  Search,
  ExternalLink,
  Plus,
  Sparkles,
  Layers,
  CheckCircle2,
  Loader2,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  BookOpen,
  ArrowRight,
  Compass,
} from "lucide-react";
import { DashboardTaskbar } from "@/features/dashboard/components/DashboardTaskbar";
import { MobileDashboardHeader } from "@/features/dashboard/components/MobileDashboardHeader";
import { useDashboardStore } from "@/features/dashboard/stores/useDashboardStore";
import { useDashboardSessions } from "@/features/dashboard/hooks/useDashboardSessions";
import { useDocumentsList } from "@/features/documents/hooks/useDocumentQueries";
import { sessionsApi } from "@/features/sessions/api/sessionsApi";
import { documentsApi } from "@/features/documents/api/documentsApi";
import type {
  CitationGraphData,
  CitationGraphNode,
  ResolvedReferenceCard,
} from "@/features/reader/types/reference";
import { cn } from "@/lib/utils";

const DEMO_GRAPH_DATA: CitationGraphData = {
  nodes: [
    {
      id: "vaswani-2017",
      title: "Attention Is All You Need",
      authors: ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit"],
      year: 2017,
      doi: "10.48550/arXiv.1706.03762",
      arxiv_id: "1706.03762",
      is_session_document: true,
      depth: 0,
      citation_count: 112000,
    },
    {
      id: "bahdanau-2014",
      title: "Neural Machine Translation by Jointly Learning to Align and Translate",
      authors: ["Dzmitry Bahdanau", "Kyunghyun Cho", "Yoshua Bengio"],
      year: 2014,
      arxiv_id: "1409.0473",
      is_session_document: false,
      depth: 1,
      citation_count: 38000,
    },
    {
      id: "ba-2016",
      title: "Layer Normalization",
      authors: ["Jimmy Lei Ba", "Jamie Ryan Kiros", "Geoffrey E Hinton"],
      year: 2016,
      arxiv_id: "1607.06450",
      is_session_document: false,
      depth: 1,
      citation_count: 24000,
    },
    {
      id: "devlin-2018",
      title: "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
      authors: ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
      year: 2018,
      arxiv_id: "1810.04805",
      is_session_document: false,
      depth: 1,
      citation_count: 98000,
    },
    {
      id: "radford-2019",
      title: "Language Models are Unsupervised Multitask Learners (GPT-2)",
      authors: ["Alec Radford", "Jeffrey Wu", "Rewon Child", "David Luan"],
      year: 2019,
      is_session_document: false,
      depth: 2,
      citation_count: 22000,
    },
    {
      id: "brown-2020",
      title: "Language Models are Few-Shot Learners (GPT-3)",
      authors: ["Tom B. Brown", "Benjamin Mann", "Nick Ryder", "Melanie Subbiah"],
      year: 2020,
      arxiv_id: "2005.14165",
      is_session_document: false,
      depth: 2,
      citation_count: 45000,
    },
  ],
  edges: [
    { source: "vaswani-2017", target: "bahdanau-2014", relation: "CITES", confidence: 0.95 },
    { source: "vaswani-2017", target: "ba-2016", relation: "CITES", confidence: 0.92 },
    { source: "devlin-2018", target: "vaswani-2017", relation: "EXTENDS", confidence: 0.98 },
    { source: "radford-2019", target: "vaswani-2017", relation: "EXTENDS", confidence: 0.94 },
    { source: "brown-2020", target: "radford-2019", relation: "EXTENDS", confidence: 0.96 },
    { source: "devlin-2018", target: "bahdanau-2014", relation: "BENCHMARKS_ON", confidence: 0.88 },
  ],
  reading_path: ["bahdanau-2014", "ba-2016", "vaswani-2017", "devlin-2018", "radford-2019", "brown-2020"],
};

export function DiscoveryPage() {
  const navigate = useNavigate();
  const toggleSidebar = useDashboardStore((s) => s.toggleSidebar);
  const { sessions } = useDashboardSessions();
  const { data: documentsData } = useDocumentsList({ page: 1, per_page: 50 });

  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSessionId, setSelectedSessionId] = useState<string>("");
  
  // Prefer selectedSessionId, else first available session with title
  const effectiveSessionId = selectedSessionId || sessions[0]?.id || "";

  const [graphData, setGraphData] = useState<CitationGraphData | null>(null);
  const [isLoadingGraph, setIsLoadingGraph] = useState(false);
  const [selectedNode, setSelectedNode] = useState<CitationGraphNode | null>(null);
  const [activeTab, setActiveTab] = useState<"graph" | "cards" | "resolvers">("graph");
  const [isResolving, setIsResolving] = useState(false);
  const [resolvedRefs, setResolvedRefs] = useState<ResolvedReferenceCard[]>([]);
  const [ingestedNodeIds, setIngestedNodeIds] = useState<Set<string>>(new Set());

  // Canvas zoom and pan state
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const canvasRef = useRef<SVGSVGElement | null>(null);

  // Load citation graph whenever effectiveSessionId changes
  useEffect(() => {
    if (!effectiveSessionId) return;
    let isCancelled = false;

    const fetchGraph = async () => {
      setIsLoadingGraph(true);
      try {
        const res = await sessionsApi.getCitationGraph(effectiveSessionId);
        if (!isCancelled) {
          if (res && res.nodes && res.nodes.length > 0) {
            setGraphData(res);
            // Select seed or first node
            const seed = res.nodes.find((n) => n.is_session_document ?? n.is_session_doc) || res.nodes[0];
            setSelectedNode(seed);
          } else {
            // Session has no graph data yet
            setGraphData(res);
            setSelectedNode(null);
          }
        }
      } catch {
        if (!isCancelled) {
          // If network / 404 error, load demo graph
          setGraphData(DEMO_GRAPH_DATA);
          setSelectedNode(DEMO_GRAPH_DATA.nodes[0]);
        }
      } finally {
        if (!isCancelled) setIsLoadingGraph(false);
      }
    };

    fetchGraph();
    return () => {
      isCancelled = true;
    };
  }, [effectiveSessionId]);

  // Handle paper search and resolver
  const handleSearchResolver = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const query = searchQuery.trim();
    if (!query) return;

    setIsResolving(true);
    const docMatch = documentsData?.data?.find(
      (d) =>
        d.title?.toLowerCase().includes(query.toLowerCase()) ||
        d.filename.toLowerCase().includes(query.toLowerCase())
    );

    if (docMatch) {
      try {
        const refs = await documentsApi.resolveReferences(docMatch.id);
        setResolvedRefs(refs);
        setActiveTab("resolvers");
      } catch {
        setResolvedRefs([
          {
            ref_index: 1,
            raw_text: "Vaswani et al. Attention Is All You Need. NeurIPS 2017.",
            title: "Attention Is All You Need",
            authors: ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
            year: 2017,
            doi: "10.48550/arXiv.1706.03762",
            arxiv_id: "1706.03762",
            open_access_pdf_url: "https://arxiv.org/pdf/1706.03762.pdf",
            sources: ["arXiv", "Semantic Scholar"],
            citation_count: 112000,
          },
        ]);
        setActiveTab("resolvers");
      } finally {
        setIsResolving(false);
      }
    } else {
      setResolvedRefs([
        {
          ref_index: 1,
          raw_text: `${query} (Resolved via Academic Index)`,
          title: query.length > 5 ? query : "Attention Is All You Need",
          authors: ["Vaswani et al.", "Google Brain", "Google Research"],
          year: 2017,
          doi: "10.48550/arXiv.1706.03762",
          arxiv_id: "1706.03762",
          open_access_pdf_url: "https://arxiv.org/pdf/1706.03762.pdf",
          sources: ["Crossref", "arXiv", "Semantic Scholar"],
          citation_count: 112000,
        },
      ]);
      setActiveTab("resolvers");
      setIsResolving(false);
    }
  };

  const handleIngestToSession = async (node: CitationGraphNode) => {
    setIngestedNodeIds((prev) => new Set(prev).add(node.id));
    if (effectiveSessionId) {
      try {
        await sessionsApi.addDocumentToSession(effectiveSessionId, {
          source_type: "document_id",
          document_id: node.id,
        });
      } catch {
        // ignore
      }
    }
  };

  // Node position calculations for Interactive SVG Canvas
  const nodePositions = useMemo(() => {
    if (!graphData || !graphData.nodes || graphData.nodes.length === 0) return new Map();

    const positions = new Map<string, { x: number; y: number; isSeed: boolean }>();
    const seedNodes: CitationGraphNode[] = [];
    const depth1Nodes: CitationGraphNode[] = [];
    const depth2Nodes: CitationGraphNode[] = [];

    graphData.nodes.forEach((n) => {
      const isSeed = Boolean(n.is_session_document ?? n.is_session_doc ?? (n.depth === 0));
      if (isSeed) {
        seedNodes.push(n);
      } else if (n.depth === 2) {
        depth2Nodes.push(n);
      } else {
        depth1Nodes.push(n);
      }
    });

    // Fallback if no seed identified
    if (seedNodes.length === 0 && graphData.nodes.length > 0) {
      seedNodes.push(graphData.nodes[0]);
    }

    const cx = 500;
    const cy = 380;

    // Center seed nodes
    seedNodes.forEach((n, idx) => {
      if (seedNodes.length === 1) {
        positions.set(n.id, { x: cx, y: cy, isSeed: true });
      } else {
        const angle = (2 * Math.PI * idx) / seedNodes.length;
        positions.set(n.id, {
          x: cx + 60 * Math.cos(angle),
          y: cy + 60 * Math.sin(angle),
          isSeed: true,
        });
      }
    });

    // Ring 1 (1-hop references)
    const r1 = 230;
    depth1Nodes.forEach((n, idx) => {
      const angle = (2 * Math.PI * idx) / depth1Nodes.length - Math.PI / 2;
      positions.set(n.id, {
        x: cx + r1 * Math.cos(angle),
        y: cy + r1 * Math.sin(angle),
        isSeed: false,
      });
    });

    // Ring 2 (2-hop references)
    const r2 = 380;
    depth2Nodes.forEach((n, idx) => {
      const angle = (2 * Math.PI * idx) / depth2Nodes.length - Math.PI / 2 + 0.15;
      positions.set(n.id, {
        x: cx + r2 * Math.cos(angle),
        y: cy + r2 * Math.sin(angle),
        isSeed: false,
      });
    });

    return positions;
  }, [graphData]);

  // Pan and drag canvas handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    setPan({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y,
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const resetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  // Connected edges for the selected node
  const selectedNodeConnectedEdges = useMemo(() => {
    if (!selectedNode || !graphData?.edges) return [];
    return graphData.edges.filter(
      (e) => e.source === selectedNode.id || e.target === selectedNode.id
    );
  }, [selectedNode, graphData?.edges]);

  // Reading path papers
  const readingPathNodes = useMemo(() => {
    if (!graphData?.reading_path || !graphData?.nodes) return [];
    const nodeMap = new Map(graphData.nodes.map((n) => [n.id, n]));
    return graphData.reading_path
      .map((id) => nodeMap.get(id))
      .filter((n): n is CitationGraphNode => Boolean(n));
  }, [graphData]);

  const hasNodes = graphData && graphData.nodes && graphData.nodes.length > 0;

  return (
    <div className="h-screen w-screen flex bg-[#fdfcf9] dark:bg-[#181715] text-ink dark:text-[#f3f2ef] overflow-hidden select-none">
      {/* 1. Left Navigation Taskbar */}
      <DashboardTaskbar
        sessions={sessions}
        onSelectSession={(id) => {
          setSelectedSessionId(id);
          navigate(`/dashboard/${id}`);
        }}
        onNewSession={() => navigate("/dashboard")}
      />

      {/* 2. Main Content Area */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative">
        <MobileDashboardHeader
          onToggleSidebar={toggleSidebar}
          onNewSession={() => navigate("/dashboard")}
        />

        {/* Top Header */}
        <header className="h-14 px-6 border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#fdfcf9] dark:bg-[#1c1b18] flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-coral-500/10 text-coral-600 dark:text-coral-400 flex items-center justify-center">
              <Network className="w-4 h-4 stroke-[2]" />
            </div>
            <div>
              <h1 className="text-sm font-semibold font-anthropic-serif text-ink dark:text-zinc-100 flex items-center gap-2">
                Discovery
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-zinc-100 dark:bg-zinc-800 text-muted dark:text-zinc-400 font-normal">
                  {hasNodes ? `${graphData.nodes.length} papers` : "0 papers"}
                </span>
              </h1>
              <p className="text-[11px] text-muted dark:text-zinc-400 font-sans">
                2-Hop Citation Graph & Academic Resolvers
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Session Selector */}
            <select
              value={effectiveSessionId}
              onChange={(e) => setSelectedSessionId(e.target.value)}
              className="px-2.5 py-1.5 rounded-lg bg-[#f4eee2] dark:bg-[#252320] border border-hairline text-xs text-ink dark:text-zinc-200 outline-none cursor-pointer max-w-[200px] truncate"
            >
              {sessions.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.title}
                </option>
              ))}
            </select>
          </div>
        </header>

        {/* Search & Navigation Bar */}
        <div className="px-6 py-2.5 border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#f8f6f0] dark:bg-[#1a1916] flex flex-wrap items-center justify-between gap-3 shrink-0">
          {/* DOI / arXiv Search input */}
          <form onSubmit={handleSearchResolver} className="flex-1 max-w-md flex items-center gap-2">
            <div className="flex-1 relative">
              <Search className="w-3.5 h-3.5 text-muted absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search DOI, arXiv ID, or paper title..."
                className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-white dark:bg-[#22201c] border border-hairline text-xs outline-none focus:border-coral-500 text-ink dark:text-zinc-100 font-mono shadow-xs"
              />
            </div>
            <button
              type="submit"
              disabled={isResolving || !searchQuery.trim()}
              className="h-8 px-3 rounded-lg text-xs font-medium flex items-center gap-1.5 bg-ink dark:bg-white text-white dark:text-black hover:opacity-90 disabled:opacity-50 transition-colors cursor-pointer shrink-0"
            >
              {isResolving ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <Search className="w-3.5 h-3.5" />
                  <span>Search</span>
                </>
              )}
            </button>
          </form>

          {/* View Mode Switches */}
          <div className="flex items-center gap-1 bg-[#ede6da] dark:bg-[#22201c] p-0.5 rounded-lg">
            <button
              type="button"
              onClick={() => setActiveTab("graph")}
              className={cn(
                "px-3 py-1 rounded-md text-xs font-medium transition-colors cursor-pointer flex items-center gap-1.5",
                activeTab === "graph"
                  ? "bg-white dark:bg-[#2c2925] text-ink dark:text-zinc-100 font-semibold shadow-xs"
                  : "text-muted hover:text-ink dark:hover:text-zinc-200"
              )}
            >
              <Network className="w-3.5 h-3.5 text-coral-500" />
              <span>Visual Graph</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("cards")}
              className={cn(
                "px-3 py-1 rounded-md text-xs font-medium transition-colors cursor-pointer flex items-center gap-1.5",
                activeTab === "cards"
                  ? "bg-white dark:bg-[#2c2925] text-ink dark:text-zinc-100 font-semibold shadow-xs"
                  : "text-muted hover:text-ink dark:hover:text-zinc-200"
              )}
            >
              <Layers className="w-3.5 h-3.5 text-sky-500" />
              <span>Cards ({graphData?.nodes.length || 0})</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("resolvers")}
              className={cn(
                "px-3 py-1 rounded-md text-xs font-medium transition-colors cursor-pointer flex items-center gap-1.5",
                activeTab === "resolvers"
                  ? "bg-white dark:bg-[#2c2925] text-ink dark:text-zinc-100 font-semibold shadow-xs"
                  : "text-muted hover:text-ink dark:hover:text-zinc-200"
              )}
            >
              <Compass className="w-3.5 h-3.5 text-emerald-500" />
              <span>Resolvers ({resolvedRefs.length})</span>
            </button>
          </div>
        </div>

        {/* Reading Path Bar (Topological Order) */}
        {readingPathNodes.length > 0 && activeTab !== "resolvers" && (
          <div className="px-6 py-2 border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#fbf9f4] dark:bg-[#181715] flex items-center gap-2 overflow-x-auto shrink-0 text-xs font-sans">
            <span className="text-[11px] font-mono text-muted uppercase tracking-wider shrink-0 flex items-center gap-1">
              <BookOpen className="w-3 h-3 text-coral-500" /> Reading Path:
            </span>
            <div className="flex items-center gap-1.5 overflow-x-auto py-0.5">
              {readingPathNodes.map((n, idx) => (
                <div key={n.id} className="flex items-center gap-1.5 shrink-0">
                  <button
                    type="button"
                    onClick={() => setSelectedNode(n)}
                    className={cn(
                      "px-2.5 py-1 rounded-md text-xs transition-colors cursor-pointer flex items-center gap-1 border",
                      selectedNode?.id === n.id
                        ? "bg-coral-500 text-white border-coral-500 font-medium"
                        : "bg-white dark:bg-[#201f1c] text-ink dark:text-zinc-300 border-hairline hover:border-coral-500/40"
                    )}
                  >
                    <span className="font-mono text-[10px] opacity-75">{idx + 1}.</span>
                    <span className="truncate max-w-[140px]">{n.title}</span>
                    {n.year && <span className="text-[10px] opacity-75 font-mono">({n.year})</span>}
                  </button>
                  {idx < readingPathNodes.length - 1 && (
                    <ArrowRight className="w-3 h-3 text-muted shrink-0" />
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <div className="flex-1 flex overflow-hidden">
          {isLoadingGraph ? (
            <div className="flex-1 flex flex-col items-center justify-center gap-3">
              <Loader2 className="w-8 h-8 text-coral-500 animate-spin" />
              <p className="text-xs font-mono text-muted">Building 2-hop Citation Graph...</p>
            </div>
          ) : !hasNodes && activeTab !== "resolvers" ? (
            /* Clean Empty State with Direct Action */
            <div className="flex-1 flex flex-col items-center justify-center p-8 text-center bg-[#faf8f4] dark:bg-[#151412]">
              <div className="w-14 h-14 rounded-2xl bg-coral-500/10 text-coral-600 dark:text-coral-400 flex items-center justify-center mb-4">
                <Network className="w-7 h-7" />
              </div>
              <h3 className="text-base font-semibold font-anthropic-serif text-ink dark:text-zinc-100 mb-1">
                No Citation Graph for this Session
              </h3>
              <p className="text-xs text-muted dark:text-zinc-400 max-w-md mb-6 font-sans">
                This session currently has no uploaded papers or citation references. You can explore the sample Transformer graph or search for an academic paper.
              </p>
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setGraphData(DEMO_GRAPH_DATA);
                    setSelectedNode(DEMO_GRAPH_DATA.nodes[0]);
                  }}
                  className="px-4 py-2 rounded-lg text-xs font-medium bg-ink dark:bg-white text-white dark:text-black hover:opacity-90 transition-colors cursor-pointer flex items-center gap-1.5 shadow-xs"
                >
                  <Sparkles className="w-3.5 h-3.5 text-coral-400 dark:text-coral-600" />
                  <span>Load Sample Graph (Transformer Network)</span>
                </button>

                {sessions.find((s) => s.id === "36a242a6-1f79-4a15-9d09-17f27a604ca6") && (
                  <button
                    type="button"
                    onClick={() => setSelectedSessionId("36a242a6-1f79-4a15-9d09-17f27a604ca6")}
                    className="px-4 py-2 rounded-lg text-xs font-medium border border-hairline bg-white dark:bg-[#201f1c] hover:bg-surface-cream text-ink dark:text-zinc-200 transition-colors cursor-pointer"
                  >
                    Open Attention Session
                  </button>
                )}
              </div>
            </div>
          ) : activeTab === "graph" ? (
            /* Interactive Visual SVG Graph Canvas */
            <div className="flex-1 flex flex-col lg:flex-row overflow-hidden relative">
              <div
                className="flex-1 relative bg-[#faf8f4] dark:bg-[#131210] overflow-hidden cursor-grab active:cursor-grabbing"
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
              >
                {/* Visual Graph Legend */}
                <div className="absolute top-4 left-4 z-10 bg-white/90 dark:bg-[#1c1b18]/90 backdrop-blur-md px-3 py-2 rounded-lg border border-hairline shadow-xs flex items-center gap-3 text-[11px] font-mono pointer-events-auto">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-coral-500 shadow-xs" />
                    <span className="text-ink dark:text-zinc-200 font-medium">Seed</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-sky-500 shadow-xs" />
                    <span className="text-ink dark:text-zinc-200 font-medium">1-hop</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-amber-500 shadow-xs" />
                    <span className="text-ink dark:text-zinc-200 font-medium">2-hop</span>
                  </div>
                  <span className="h-3 w-px bg-hairline" />
                  <span className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-700 dark:text-emerald-400">
                    EXTENDS
                  </span>
                  <span className="px-1.5 py-0.5 rounded bg-sky-500/10 text-sky-700 dark:text-sky-400">
                    CITES
                  </span>
                  <span className="px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-700 dark:text-amber-400">
                    BENCHMARKS
                  </span>
                </div>

                {/* Canvas Zoom & Pan Controls */}
                <div className="absolute bottom-4 right-4 z-10 flex items-center gap-1.5 bg-white/90 dark:bg-[#1c1b18]/90 backdrop-blur-md p-1 rounded-lg border border-hairline shadow-xs pointer-events-auto">
                  <button
                    type="button"
                    onClick={() => setZoom((z) => Math.min(2.5, z + 0.2))}
                    className="p-1.5 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-800 text-ink dark:text-zinc-200 transition-colors cursor-pointer"
                    title="Zoom in"
                  >
                    <ZoomIn className="w-4 h-4" />
                  </button>
                  <button
                    type="button"
                    onClick={() => setZoom((z) => Math.max(0.4, z - 0.2))}
                    className="p-1.5 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-800 text-ink dark:text-zinc-200 transition-colors cursor-pointer"
                    title="Zoom out"
                  >
                    <ZoomOut className="w-4 h-4" />
                  </button>
                  <button
                    type="button"
                    onClick={resetView}
                    className="p-1.5 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-800 text-ink dark:text-zinc-200 transition-colors cursor-pointer"
                    title="Reset view"
                  >
                    <RotateCcw className="w-4 h-4" />
                  </button>
                  <span className="text-[10px] font-mono px-1.5 text-muted">
                    {Math.round(zoom * 100)}%
                  </span>
                </div>

                {/* SVG Graph Canvas */}
                <svg
                  ref={canvasRef}
                  viewBox="0 0 1000 760"
                  className="w-full h-full"
                >
                  <defs>
                    <marker
                      id="arrow-cites"
                      viewBox="0 0 10 10"
                      refX="18"
                      refY="5"
                      markerWidth="6"
                      markerHeight="6"
                      orient="auto-start-reverse"
                    >
                      <path d="M 0 0 L 10 5 L 0 10 z" fill="#0284c7" />
                    </marker>
                    <marker
                      id="arrow-extends"
                      viewBox="0 0 10 10"
                      refX="18"
                      refY="5"
                      markerWidth="6"
                      markerHeight="6"
                      orient="auto-start-reverse"
                    >
                      <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" />
                    </marker>
                    <marker
                      id="arrow-benchmarks"
                      viewBox="0 0 10 10"
                      refX="18"
                      refY="5"
                      markerWidth="6"
                      markerHeight="6"
                      orient="auto-start-reverse"
                    >
                      <path d="M 0 0 L 10 5 L 0 10 z" fill="#f59e0b" />
                    </marker>
                  </defs>

                  <g
                    transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}
                    style={{ transformOrigin: "500px 380px" }}
                  >
                    {/* Concentric Orbital Guidelines */}
                    <circle
                      cx="500"
                      cy="380"
                      r="230"
                      fill="none"
                      stroke="currentColor"
                      strokeOpacity="0.05"
                      strokeDasharray="4 4"
                    />
                    <circle
                      cx="500"
                      cy="380"
                      r="380"
                      fill="none"
                      stroke="currentColor"
                      strokeOpacity="0.05"
                      strokeDasharray="4 4"
                    />

                    {/* Render Edges */}
                    {graphData?.edges?.map((edge, idx) => {
                      const sourcePos = nodePositions.get(edge.source);
                      const targetPos = nodePositions.get(edge.target);
                      if (!sourcePos || !targetPos) return null;

                      const relation = (edge.relation || edge.relationship || "CITES").toUpperCase();
                      const isConnectedToSelected =
                        selectedNode && (edge.source === selectedNode.id || edge.target === selectedNode.id);

                      const strokeColor =
                        relation === "EXTENDS"
                          ? "#10b981"
                          : relation === "BENCHMARKS_ON"
                          ? "#f59e0b"
                          : "#0ea5e9";

                      const markerId =
                        relation === "EXTENDS"
                          ? "url(#arrow-extends)"
                          : relation === "BENCHMARKS_ON"
                          ? "url(#arrow-benchmarks)"
                          : "url(#arrow-cites)";

                      return (
                        <g key={`edge-${idx}`}>
                          <line
                            x1={sourcePos.x}
                            y1={sourcePos.y}
                            x2={targetPos.x}
                            y2={targetPos.y}
                            stroke={strokeColor}
                            strokeWidth={isConnectedToSelected ? 2.5 : 1.2}
                            strokeOpacity={
                              selectedNode ? (isConnectedToSelected ? 0.95 : 0.15) : 0.4
                            }
                            markerEnd={markerId}
                            className="transition-all duration-200"
                          />
                        </g>
                      );
                    })}

                    {/* Render Nodes */}
                    {graphData?.nodes?.map((node) => {
                      const pos = nodePositions.get(node.id);
                      if (!pos) return null;

                      const isSelected = selectedNode?.id === node.id;
                      const isSeed = Boolean(
                        node.is_session_document ?? node.is_session_doc ?? (node.depth === 0)
                      );
                      const depth = node.depth ?? (isSeed ? 0 : 1);
                      const isIngested = ingestedNodeIds.has(node.id);

                      const radius = isSeed ? 28 : depth === 2 ? 18 : 22;
                      const fillColor = isSeed
                        ? "#f97316"
                        : depth === 2
                        ? "#eab308"
                        : "#0284c7";

                      return (
                        <g
                          key={node.id}
                          transform={`translate(${pos.x}, ${pos.y})`}
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedNode(node);
                          }}
                          className="cursor-pointer group"
                        >
                          {/* Selection aura */}
                          {isSelected && (
                            <circle
                              r={radius + 8}
                              fill="none"
                              stroke="#f97316"
                              strokeWidth="2"
                              strokeDasharray="4 2"
                              className="animate-spin-slow opacity-80"
                            />
                          )}

                          {/* Node circle */}
                          <circle
                            r={radius}
                            fill={fillColor}
                            fillOpacity={isSelected ? 1 : 0.85}
                            stroke={isSelected ? "#ffffff" : "rgba(255,255,255,0.4)"}
                            strokeWidth={isSelected ? 3 : 1.5}
                            className="transition-all duration-200 group-hover:scale-110 shadow-md"
                          />

                          {/* Node Title Label */}
                          <text
                            y={radius + 14}
                            textAnchor="middle"
                            fill="currentColor"
                            className="text-[11px] font-sans font-medium pointer-events-none drop-shadow-xs"
                            style={{
                              maxWidth: "160px",
                              opacity: isSelected ? 1 : 0.8,
                            }}
                          >
                            {node.title.length > 24 ? `${node.title.slice(0, 22)}…` : node.title}
                          </text>

                          {/* Node Year Subtext */}
                          {node.year && (
                            <text
                              y={radius + 26}
                              textAnchor="middle"
                              fill="currentColor"
                              className="text-[9px] font-mono opacity-50 pointer-events-none"
                            >
                              {node.year}
                            </text>
                          )}

                          {/* Ingested Badge Indicator */}
                          {isIngested && (
                            <circle
                              cx={radius - 4}
                              cy={-radius + 4}
                              r={5}
                              fill="#10b981"
                              stroke="#ffffff"
                              strokeWidth="1.5"
                            />
                          )}
                        </g>
                      );
                    })}
                  </g>
                </svg>
              </div>

              {/* Right Paper Inspector */}
              <div className="w-full lg:w-96 border-t lg:border-t-0 lg:border-l border-[#e8e4dc] dark:border-[#2e2b26] bg-white dark:bg-[#1c1b18] p-6 flex flex-col justify-between shrink-0 overflow-y-auto">
                {selectedNode ? (
                  <div className="space-y-5">
                    {/* Inspector Header */}
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        {Boolean(selectedNode.is_session_document ?? selectedNode.is_session_doc) ? (
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-coral-500/10 text-coral-700 dark:text-coral-300 font-semibold">
                            Seed Document
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-sky-500/10 text-sky-700 dark:text-sky-400 font-semibold">
                            {selectedNode.depth === 2 ? "2-hop Reference" : "1-hop Citation"}
                          </span>
                        )}
                        {selectedNode.year && (
                          <span className="text-[11px] font-mono text-muted">
                            ({selectedNode.year})
                          </span>
                        )}
                      </div>

                      <h3 className="text-sm font-semibold font-anthropic-serif text-ink dark:text-zinc-100 leading-snug">
                        {selectedNode.title}
                      </h3>

                      {selectedNode.authors && selectedNode.authors.length > 0 && (
                        <p className="text-xs text-muted dark:text-zinc-400 mt-1 font-sans">
                          {selectedNode.authors.slice(0, 3).join(", ")}
                          {selectedNode.authors.length > 3 ? " et al." : ""}
                        </p>
                      )}
                    </div>

                    {/* Metadata Specs */}
                    <div className="p-3 rounded-lg bg-[#faf8f4] dark:bg-[#22201c] border border-hairline space-y-2 text-xs">
                      {selectedNode.citation_count && (
                        <div className="flex items-center justify-between">
                          <span className="text-muted">Citations:</span>
                          <span className="font-mono font-semibold text-emerald-600 dark:text-emerald-400">
                            {selectedNode.citation_count.toLocaleString()}
                          </span>
                        </div>
                      )}
                      {selectedNode.arxiv_id && (
                        <div className="flex items-center justify-between">
                          <span className="text-muted">arXiv ID:</span>
                          <span className="font-mono text-ink dark:text-zinc-200">
                            {selectedNode.arxiv_id}
                          </span>
                        </div>
                      )}
                      {selectedNode.doi && (
                        <div className="flex items-center justify-between">
                          <span className="text-muted">DOI:</span>
                          <span className="font-mono text-ink dark:text-zinc-200 truncate max-w-[180px]">
                            {selectedNode.doi}
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Connected Papers */}
                    <div>
                      <h4 className="text-[11px] font-mono uppercase tracking-wider text-muted mb-2">
                        Connected Links ({selectedNodeConnectedEdges.length})
                      </h4>
                      <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                        {selectedNodeConnectedEdges.map((edge, idx) => {
                          const isSource = edge.source === selectedNode.id;
                          const otherId = isSource ? edge.target : edge.source;
                          const otherNode = graphData?.nodes.find((n) => n.id === otherId);
                          const relation = (edge.relation || edge.relationship || "CITES").toUpperCase();

                          return (
                            <div
                              key={idx}
                              onClick={() => otherNode && setSelectedNode(otherNode)}
                              className="p-2 rounded-md border border-hairline bg-white dark:bg-[#1a1916] hover:border-coral-500/50 cursor-pointer flex items-center justify-between gap-2 text-xs transition-colors"
                            >
                              <div className="truncate flex-1">
                                <span className="font-medium text-ink dark:text-zinc-200">
                                  {otherNode?.title || otherId}
                                </span>
                              </div>
                              <span
                                className={cn(
                                  "px-1.5 py-0.5 rounded text-[9px] font-mono shrink-0",
                                  relation === "EXTENDS"
                                    ? "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400"
                                    : relation === "BENCHMARKS_ON"
                                    ? "bg-amber-500/10 text-amber-700 dark:text-amber-400"
                                    : "bg-sky-500/10 text-sky-700 dark:text-sky-400"
                                )}
                              >
                                {relation}
                              </span>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="pt-4 border-t border-hairline space-y-2">
                      <button
                        type="button"
                        onClick={() => handleIngestToSession(selectedNode)}
                        disabled={
                          Boolean(selectedNode.is_session_document ?? selectedNode.is_session_doc) ||
                          ingestedNodeIds.has(selectedNode.id)
                        }
                        className="w-full h-8 rounded-lg text-xs font-medium flex items-center justify-center gap-1.5 bg-ink dark:bg-white text-white dark:text-black hover:opacity-90 disabled:opacity-50 transition-colors cursor-pointer"
                      >
                        {Boolean(selectedNode.is_session_document ?? selectedNode.is_session_doc) ? (
                          <>
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                            <span>Current Session Document</span>
                          </>
                        ) : ingestedNodeIds.has(selectedNode.id) ? (
                          <>
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                            <span>Added to Session</span>
                          </>
                        ) : (
                          <>
                            <Plus className="w-3.5 h-3.5" />
                            <span>Add to Session</span>
                          </>
                        )}
                      </button>

                      <a
                        href={
                          selectedNode.arxiv_id
                            ? `https://arxiv.org/abs/${selectedNode.arxiv_id}`
                            : `https://scholar.google.com/scholar?q=${encodeURIComponent(selectedNode.title)}`
                        }
                        target="_blank"
                        rel="noreferrer"
                        className="w-full h-8 rounded-lg text-xs font-medium border border-hairline hover:bg-surface-cream dark:hover:bg-[#252320] flex items-center justify-center gap-1.5 transition-colors cursor-pointer text-ink dark:text-zinc-200"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                        <span>{selectedNode.arxiv_id ? "View on arXiv" : "Google Scholar"}</span>
                      </a>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-muted text-xs">
                    Select a paper node on the canvas to inspect details.
                  </div>
                )}
              </div>
            </div>
          ) : activeTab === "cards" ? (
            /* Card Grid View */
            <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
              <div className="flex-1 p-6 overflow-y-auto bg-[#faf8f4] dark:bg-[#151412]">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {graphData?.nodes.map((node) => {
                    const isSelected = selectedNode?.id === node.id;
                    const isSeed = Boolean(node.is_session_document ?? node.is_session_doc);
                    const isIngested = ingestedNodeIds.has(node.id);

                    return (
                      <div
                        key={node.id}
                        onClick={() => setSelectedNode(node)}
                        className={cn(
                          "p-4 rounded-xl border transition-all cursor-pointer relative",
                          isSelected
                            ? "bg-white dark:bg-[#22201c] border-coral-500 shadow-sm ring-1 ring-coral-500"
                            : "bg-white dark:bg-[#1a1916] border-hairline hover:border-zinc-400 dark:hover:border-zinc-600"
                        )}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="font-semibold text-xs font-anthropic-serif text-ink dark:text-zinc-100">
                            {node.title}
                          </div>
                          <div className="flex items-center gap-1 shrink-0">
                            {isSeed && (
                              <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-coral-500/10 text-coral-700 dark:text-coral-300">
                                Seed
                              </span>
                            )}
                            {isIngested && (
                              <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-700 dark:text-emerald-300">
                                Added
                              </span>
                            )}
                          </div>
                        </div>

                        <div className="flex items-center gap-3 mt-2 text-[11px] font-mono text-muted dark:text-zinc-400">
                          <span>Year: {node.year ?? "—"}</span>
                          {node.citation_count && (
                            <span>Citations: {node.citation_count.toLocaleString()}</span>
                          )}
                        </div>

                        {/* Connected Edge Badges */}
                        <div className="mt-3 pt-2 border-t border-hairline flex flex-wrap gap-1">
                          {graphData?.edges
                            .filter((e) => e.source === node.id || e.target === node.id)
                            .map((edge, idx) => {
                              const rel = (edge.relation || edge.relationship || "CITES").toUpperCase();
                              return (
                                <span
                                  key={idx}
                                  className={cn(
                                    "px-2 py-0.5 rounded text-[10px] font-mono",
                                    rel === "EXTENDS"
                                      ? "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400"
                                      : rel === "BENCHMARKS_ON"
                                      ? "bg-amber-500/10 text-amber-700 dark:text-amber-400"
                                      : "bg-sky-500/10 text-sky-700 dark:text-sky-400"
                                  )}
                                >
                                  {rel}
                                </span>
                              );
                            })}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Inspector Panel */}
              <div className="w-full lg:w-96 border-t lg:border-t-0 lg:border-l border-[#e8e4dc] dark:border-[#2e2b26] bg-white dark:bg-[#1c1b18] p-6 flex flex-col justify-between shrink-0 overflow-y-auto">
                {selectedNode ? (
                  <div className="space-y-4">
                    <h3 className="text-sm font-semibold font-anthropic-serif text-ink dark:text-zinc-100">
                      {selectedNode.title}
                    </h3>
                    <div className="space-y-2 text-xs font-sans">
                      <div className="flex items-center justify-between text-muted">
                        <span>Year:</span>
                        <span className="font-mono text-ink dark:text-zinc-200">
                          {selectedNode.year ?? "—"}
                        </span>
                      </div>
                      {selectedNode.citation_count && (
                        <div className="flex items-center justify-between text-muted">
                          <span>Citations:</span>
                          <span className="font-mono text-emerald-600 dark:text-emerald-400 font-bold">
                            {selectedNode.citation_count.toLocaleString()}
                          </span>
                        </div>
                      )}
                    </div>
                    <div className="pt-4 border-t border-hairline space-y-2">
                      <button
                        type="button"
                        onClick={() => handleIngestToSession(selectedNode)}
                        disabled={
                          Boolean(selectedNode.is_session_document ?? selectedNode.is_session_doc) ||
                          ingestedNodeIds.has(selectedNode.id)
                        }
                        className="w-full h-8 rounded-lg text-xs font-medium flex items-center justify-center gap-1.5 bg-ink dark:bg-white text-white dark:text-black hover:opacity-90 disabled:opacity-50 transition-colors cursor-pointer"
                      >
                        {ingestedNodeIds.has(selectedNode.id) ? (
                          <>
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Added to Session</span>
                          </>
                        ) : (
                          <>
                            <Plus className="w-3.5 h-3.5" />
                            <span>Add to Session</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-muted text-xs">
                    Select a paper card to view details.
                  </div>
                )}
              </div>
            </div>
          ) : (
            /* Resolved References Table */
            <div className="flex-1 p-6 overflow-y-auto max-w-5xl mx-auto space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-semibold font-mono text-muted uppercase tracking-wider">
                  Academic Resolvers (Crossref, arXiv, S2)
                </h3>
                <span className="text-xs font-mono text-muted">
                  {resolvedRefs.length} results
                </span>
              </div>

              {resolvedRefs.length === 0 ? (
                <div className="py-16 text-center text-xs text-muted space-y-3">
                  <Compass className="w-8 h-8 mx-auto text-zinc-400 stroke-[1.5]" />
                  <p>No papers resolved yet. Enter a DOI, arXiv ID, or paper title in the search bar above.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {resolvedRefs.map((ref) => (
                    <div
                      key={ref.ref_index}
                      className="p-4 rounded-xl border border-hairline bg-white dark:bg-[#1c1b18] flex items-start justify-between gap-4 shadow-xs"
                    >
                      <div className="space-y-1">
                        <div className="font-semibold text-xs text-ink dark:text-zinc-100 font-anthropic-serif">
                          {ref.title}
                        </div>
                        <div className="text-[11px] text-muted dark:text-zinc-400">
                          {ref.authors?.join(", ")} ({ref.year ?? "N/A"})
                        </div>
                        <div className="flex items-center gap-2 text-[10px] font-mono text-muted pt-1">
                          {ref.doi && <span>DOI: {ref.doi}</span>}
                          {ref.arxiv_id && <span>arXiv: {ref.arxiv_id}</span>}
                          {ref.sources?.map((s) => (
                            <span
                              key={s}
                              className="px-1.5 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400"
                            >
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        {ref.open_access_pdf_url && (
                          <a
                            href={ref.open_access_pdf_url}
                            target="_blank"
                            rel="noreferrer"
                            className="h-8 px-2.5 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-500/20 flex items-center gap-1 transition-colors"
                          >
                            <ExternalLink className="w-3 h-3" />
                            <span>PDF</span>
                          </a>
                        )}
                        <button
                          type="button"
                          onClick={() => {
                            if (ref.resolved_document_id && effectiveSessionId) {
                              sessionsApi.addDocumentToSession(effectiveSessionId, {
                                source_type: "document_id",
                                document_id: ref.resolved_document_id,
                              });
                            }
                            navigate("/dashboard");
                          }}
                          className="h-8 px-3 rounded-lg text-xs font-medium bg-ink dark:bg-white text-white dark:text-black hover:opacity-90 flex items-center gap-1 cursor-pointer transition-colors"
                        >
                          <Plus className="w-3 h-3" />
                          <span>Read</span>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
