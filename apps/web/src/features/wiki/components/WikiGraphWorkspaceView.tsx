import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Network,
  BookOpen,
  Sparkles,
  Search,
  Folder,
  ArrowRight,
  RefreshCw,
} from "lucide-react";
import { KnowledgeGraphCanvas } from "@/features/library/components/KnowledgeGraphCanvas";
import { PaperInspectionDrawer } from "@/features/library/components/PaperInspectionDrawer";
import { AcademicMarkdownRenderer } from "@/components/shared/AcademicMarkdownRenderer";
import { libraryApi } from "@/features/library/api/libraryApi";
import { useFoldersListQuery } from "@/features/library/hooks/useFolderQueries";
import type {
  LibraryGraphNode,
  WikiPageItem,
  ResearchGapsResponseData,
} from "@/features/library/types";
import { cn } from "@/lib/utils";

export interface WikiGraphWorkspaceViewProps {
  onSelectDocument?: (doc: { id: string; title?: string; filename: string }) => void;
}

type ViewMode = "graph" | "wiki" | "gaps";

export function WikiGraphWorkspaceView({
  onSelectDocument,
}: WikiGraphWorkspaceViewProps) {
  const [mode, setMode] = useState<ViewMode>("graph");
  const [selectedFolderId, setSelectedFolderId] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<LibraryGraphNode | null>(null);
  const [selectedWikiSlug, setSelectedWikiSlug] = useState<string | null>(null);
  const [wikiSearch, setWikiSearch] = useState("");

  // Folders list
  const { data: folders = [] } = useFoldersListQuery();

  // Knowledge Graph Data
  const {
    data: graphData,
    isLoading: isLoadingGraph,
    refetch: refetchGraph,
  } = useQuery({
    queryKey: ["wiki-graph", "library-graph", selectedFolderId],
    queryFn: () => libraryApi.getLibraryGraph(selectedFolderId),
  });

  // Compiled Wiki Pages
  const {
    data: wikiPages = [],
    isLoading: isLoadingWiki,
    refetch: refetchWiki,
  } = useQuery<WikiPageItem[]>({
    queryKey: ["wiki-graph", "pages"],
    queryFn: () => libraryApi.listWikiPages(),
  });

  // Research Gaps Matrix
  const {
    data: gapsData,
    isLoading: isLoadingGaps,
    refetch: refetchGaps,
  } = useQuery<ResearchGapsResponseData>({
    queryKey: ["wiki-graph", "research-gaps", selectedFolderId],
    queryFn: () => libraryApi.getResearchGaps(selectedFolderId, 5),
  });

  // Active selected wiki page
  const activeWikiPage = useMemo(() => {
    if (!wikiPages || wikiPages.length === 0) return null;
    if (selectedWikiSlug) {
      return wikiPages.find((p) => p.slug === selectedWikiSlug) || wikiPages[0];
    }
    return wikiPages[0];
  }, [wikiPages, selectedWikiSlug]);

  // Filtered wiki pages
  const filteredWikiPages = useMemo(() => {
    if (!wikiSearch.trim()) return wikiPages;
    const q = wikiSearch.toLowerCase().trim();
    return wikiPages.filter(
      (p) =>
        p.title.toLowerCase().includes(q) ||
        p.slug.toLowerCase().includes(q) ||
        p.page_type.toLowerCase().includes(q)
    );
  }, [wikiPages, wikiSearch]);

  const rawNodes = graphData?.nodes || [];
  const rawEdges = graphData?.edges || [];

  return (
    <div
      data-testid="wiki-graph-workspace"
      className="flex-1 flex flex-col h-screen w-full bg-[#fbf9f5] dark:bg-[#181715] text-ink dark:text-[#f3f2ef] overflow-hidden"
    >
      {/* 1. Header Toolbar */}
      <header className="h-13 px-4 border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#fdfcf9] dark:bg-[#1c1b18] flex items-center justify-between gap-3 shrink-0 z-20">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Network className="w-5 h-5 text-[#c15f3e] stroke-[2.2]" />
            <h1 className="font-serif font-bold text-sm tracking-tight text-[#1a1918] dark:text-[#f4f1ea]">
              Wiki Graph
            </h1>
          </div>

          {/* Mode Switcher Tabs */}
          <nav
            aria-label="Chế độ xem Wiki Graph"
            className="flex items-center gap-1 bg-[#ede8df]/70 dark:bg-[#252320] p-0.5 rounded-lg border border-[#e2dcd2]/70 dark:border-[#322f2a]"
          >
            <button
              type="button"
              onClick={() => setMode("graph")}
              className={cn(
                "px-2.5 py-1 rounded-md text-xs font-medium transition-colors cursor-pointer flex items-center gap-1.5",
                mode === "graph"
                  ? "bg-white dark:bg-[#1e1c19] text-[#c15f3e] font-semibold shadow-2xs"
                  : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200"
              )}
            >
              <Network className="w-3.5 h-3.5" />
              <span>Đồ thị tri thức</span>
            </button>
            <button
              type="button"
              onClick={() => setMode("wiki")}
              className={cn(
                "px-2.5 py-1 rounded-md text-xs font-medium transition-colors cursor-pointer flex items-center gap-1.5",
                mode === "wiki"
                  ? "bg-white dark:bg-[#1e1c19] text-[#c15f3e] font-semibold shadow-2xs"
                  : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200"
              )}
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>Trang Wiki</span>
              {wikiPages.length > 0 && (
                <span className="text-[10px] opacity-75 font-mono">
                  ({wikiPages.length})
                </span>
              )}
            </button>
            <button
              type="button"
              onClick={() => setMode("gaps")}
              className={cn(
                "px-2.5 py-1 rounded-md text-xs font-medium transition-colors cursor-pointer flex items-center gap-1.5",
                mode === "gaps"
                  ? "bg-white dark:bg-[#1e1c19] text-[#c15f3e] font-semibold shadow-2xs"
                  : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200"
              )}
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Khoảng trống</span>
            </button>
          </nav>
        </div>

        {/* Right Section: Folder filter & Refresh */}
        <div className="flex items-center gap-2">
          {folders.length > 0 && (
            <div className="flex items-center gap-1 bg-white dark:bg-[#22201d] px-2 py-1 rounded-lg border border-[#e2dcd2] dark:border-[#322f2a] text-xs">
              <Folder className="w-3 h-3 text-muted" />
              <select
                aria-label="Lọc theo thư mục"
                value={selectedFolderId || ""}
                onChange={(e) => setSelectedFolderId(e.target.value || null)}
                className="bg-transparent text-xs text-ink dark:text-zinc-100 outline-none cursor-pointer"
              >
                <option value="">Tất cả thư mục</option>
                {folders.map((f) => (
                  <option key={f.id} value={f.id}>
                    {f.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          <button
            type="button"
            onClick={() => {
              if (mode === "graph") refetchGraph();
              if (mode === "wiki") refetchWiki();
              if (mode === "gaps") refetchGaps();
            }}
            className="p-1.5 rounded-lg border border-[#e2dcd2] dark:border-[#322f2a] bg-white dark:bg-[#201e1a] hover:bg-[#f5f2eb] dark:hover:bg-[#282622] text-muted hover:text-ink transition-colors cursor-pointer"
            title="Làm mới dữ liệu"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </header>

      {/* 2. Workspace Body */}
      <div className="flex-1 relative overflow-hidden">
        {/* MODE 1: KNOWLEDGE GRAPH CANVAS */}
        {mode === "graph" && (
          <div className="h-full w-full relative">
            <KnowledgeGraphCanvas
              graphData={graphData || null}
              isLoading={isLoadingGraph}
              focusNodeId={selectedNode?.id || null}
              onSelectNode={(node) => setSelectedNode(node)}
              onSelectDocument={onSelectDocument}
            />

            {/* Paper / Entity Inspection Drawer */}
            <div
              className={cn(
                "absolute top-0 right-0 bottom-0 w-80 md:w-96 transition-transform duration-300 ease-[cubic-bezier(0.2,0,0,1)] z-30 shadow-2xl",
                selectedNode ? "translate-x-0" : "translate-x-full pointer-events-none"
              )}
            >
              <PaperInspectionDrawer
                isOpen={!!selectedNode}
                node={selectedNode}
                allNodes={rawNodes}
                allEdges={rawEdges}
                onClose={() => setSelectedNode(null)}
                onSelectNode={(id) => {
                  const target = rawNodes.find((n) => n.id === id);
                  if (target) setSelectedNode(target);
                }}
                onOpenReader={(docId) => {
                  if (onSelectDocument && selectedNode) {
                    onSelectDocument({
                      id: docId,
                      title: selectedNode.label,
                      filename:
                        (selectedNode.metadata?.filename as string) || "document.pdf",
                    });
                  }
                }}
              />
            </div>
          </div>
        )}

        {/* MODE 2: COMPILED WIKI PAGES EXPLORER */}
        {mode === "wiki" && (
          <div className="h-full w-full flex overflow-hidden">
            {/* Left: Wiki Pages Sidebar List */}
            <aside
              aria-label="Danh sách trang wiki"
              className="w-72 border-r border-[#e8e4dc] dark:border-[#2e2b26] bg-[#fcfbf7] dark:bg-[#1a1916] flex flex-col shrink-0"
            >
              <div className="p-2.5 border-b border-[#ece8df] dark:border-[#2a2824]">
                <div className="relative">
                  <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-muted pointer-events-none" />
                  <input
                    type="text"
                    value={wikiSearch}
                    onChange={(e) => setWikiSearch(e.target.value)}
                    placeholder="Tìm kiếm trang wiki..."
                    className="w-full h-7 pl-8 pr-2 rounded-md bg-white dark:bg-[#22201d] border border-[#e2dcd2] dark:border-[#322f2a] text-xs text-ink dark:text-zinc-100 placeholder:text-muted outline-none focus:border-[#c15f3e]"
                  />
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-2 space-y-1 scrollbar-none">
                {isLoadingWiki ? (
                  <div className="p-4 text-center text-xs text-muted">
                    Đang tải danh sách wiki...
                  </div>
                ) : filteredWikiPages.length === 0 ? (
                  <div className="p-4 text-center text-xs text-muted">
                    Chưa có trang wiki nào được biên soạn.
                  </div>
                ) : (
                  filteredWikiPages.map((page) => {
                    const isSelected = activeWikiPage?.slug === page.slug;
                    return (
                      <button
                        key={page.id}
                        type="button"
                        onClick={() => setSelectedWikiSlug(page.slug)}
                        className={cn(
                          "w-full text-left p-2 rounded-lg text-xs transition-colors cursor-pointer flex flex-col gap-1 border",
                          isSelected
                            ? "bg-[#c15f3e]/10 border-[#c15f3e]/30 text-[#c15f3e] font-semibold"
                            : "bg-white/70 dark:bg-[#201e1a] border-transparent hover:border-[#e2dcd2] dark:hover:border-[#322f2a] text-ink dark:text-zinc-200"
                        )}
                      >
                        <div className="flex items-center justify-between gap-1">
                          <span className="truncate font-serif">{page.title}</span>
                          <span className="px-1.5 py-0.2 rounded text-[9px] font-mono uppercase bg-black/5 dark:bg-white/10 text-muted shrink-0">
                            {page.page_type}
                          </span>
                        </div>
                        <span className="text-[10px] text-muted font-mono truncate">
                          [[{page.slug}]]
                        </span>
                      </button>
                    );
                  })
                )}
              </div>
            </aside>

            {/* Right: Wiki Page Markdown Preview */}
            <main className="flex-1 overflow-y-auto p-6 bg-white dark:bg-[#161513]">
              {activeWikiPage ? (
                <article className="max-w-3xl mx-auto space-y-4">
                  <header className="pb-3 border-b border-[#ece8df] dark:border-[#2a2824] flex items-center justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-[#c15f3e]/10 text-[#c15f3e] font-semibold">
                          {activeWikiPage.page_type}
                        </span>
                        <span className="text-xs text-muted font-mono">
                          [[{activeWikiPage.slug}]]
                        </span>
                      </div>
                      <h2 className="font-serif font-bold text-xl text-[#1a1918] dark:text-[#f4f1ea]">
                        {activeWikiPage.title}
                      </h2>
                    </div>

                    <button
                      type="button"
                      onClick={() => {
                        // Switch to graph and select node if matched
                        setMode("graph");
                        const matched = rawNodes.find(
                          (n) =>
                            n.label.toLowerCase() === activeWikiPage.title.toLowerCase() ||
                            n.id === activeWikiPage.slug
                        );
                        if (matched) setSelectedNode(matched);
                      }}
                      className="px-2.5 py-1.5 rounded-lg border border-[#e2dcd2] dark:border-[#322f2a] hover:bg-[#f5f2eb] dark:hover:bg-[#282622] text-xs font-medium text-ink dark:text-zinc-200 flex items-center gap-1.5 cursor-pointer"
                      title="Xem trên đồ thị"
                    >
                      <Network className="w-3.5 h-3.5 text-[#c15f3e]" />
                      <span>Xem đồ thị</span>
                    </button>
                  </header>

                  {/* Wikilinks references */}
                  {activeWikiPage.wikilinks.length > 0 && (
                    <div className="flex items-center gap-1.5 flex-wrap text-xs text-muted">
                      <span className="font-medium">Liên kết wiki:</span>
                      {activeWikiPage.wikilinks.map((link) => (
                        <button
                          key={link}
                          type="button"
                          onClick={() => setSelectedWikiSlug(link)}
                          className="px-2 py-0.5 rounded bg-surface dark:bg-[#22201d] border border-[#e2dcd2] dark:border-[#322f2a] text-[#c15f3e] hover:underline cursor-pointer font-mono text-[11px]"
                        >
                          [[{link}]]
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Markdown Content */}
                  <div className="pt-2 text-ink dark:text-zinc-100 text-sm leading-relaxed">
                    <AcademicMarkdownRenderer
                      content={activeWikiPage.markdown_content}
                    />
                  </div>
                </article>
              ) : (
                <div className="h-full flex items-center justify-center text-xs text-muted">
                  Chọn một trang wiki để xem nội dung chi tiết.
                </div>
              )}
            </main>
          </div>
        )}

        {/* MODE 3: RESEARCH GAPS SYNTHESIS MATRIX */}
        {mode === "gaps" && (
          <div className="h-full w-full overflow-y-auto p-6 bg-white dark:bg-[#161513]">
            <div className="max-w-4xl mx-auto space-y-6">
              <header className="pb-3 border-b border-[#ece8df] dark:border-[#2a2824] flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <Sparkles className="w-4 h-4 text-[#c15f3e]" />
                    <span className="text-xs font-semibold text-[#c15f3e] uppercase tracking-wider">
                      Ma trận khoảng trống nghiên cứu
                    </span>
                  </div>
                  <h2 className="font-serif font-bold text-xl text-[#1a1918] dark:text-[#f4f1ea]">
                    Tổng hợp rào cản & Hướng đi tiềm năng
                  </h2>
                </div>

                <span className="text-xs text-muted font-mono">
                  {gapsData?.total_papers_analyzed || 0} bài báo phân tích
                </span>
              </header>

              {isLoadingGaps ? (
                <div className="py-12 text-center text-xs text-muted">
                  Đang phân tích khoảng trống nghiên cứu từ thư viện...
                </div>
              ) : gapsData ? (
                <div className="space-y-6">
                  {/* Recommended Directions */}
                  {gapsData.recommended_directions.length > 0 && (
                    <div className="p-4 rounded-xl bg-[#c15f3e]/5 border border-[#c15f3e]/20 space-y-2">
                      <h3 className="font-serif font-semibold text-xs text-[#c15f3e] uppercase tracking-wider flex items-center gap-1.5">
                        <ArrowRight className="w-3.5 h-3.5" />
                        Hướng phát triển khuyến nghị
                      </h3>
                      <ul className="space-y-1.5 text-xs text-ink dark:text-zinc-200">
                        {gapsData.recommended_directions.map((dir, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <span className="text-[#c15f3e] font-bold">•</span>
                            <span>{dir}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Synthesized Matrix Markdown */}
                  {gapsData.synthesized_matrix_markdown && (
                    <div className="p-5 rounded-xl bg-[#fbf9f5] dark:bg-[#1a1916] border border-[#ece8df] dark:border-[#2a2824]">
                      <AcademicMarkdownRenderer
                        content={gapsData.synthesized_matrix_markdown}
                      />
                    </div>
                  )}
                </div>
              ) : (
                <div className="py-12 text-center text-xs text-muted">
                  Chưa có dữ liệu khoảng trống nghiên cứu. Hãy đánh dấu sao ⭐ bài báo để kích hoạt bóc tách.
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
