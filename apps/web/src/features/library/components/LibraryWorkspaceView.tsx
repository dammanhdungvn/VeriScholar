import { useState, useMemo, useRef, useEffect } from "react";
import {
  Library,
  Search,
  LayoutGrid,
  List as ListIcon,
  Plus,
  Star,
  FileText,
  Folder,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  BookOpen,
  Send,
  Loader2,
  X,
  ChevronDown,
  ChevronUp,
  SlidersHorizontal,
  Trash2,
} from "lucide-react";
import {
  useDocumentsList,
  useStarDocumentMutation,
  useDeleteDocumentMutation,
} from "@/features/documents/hooks/useDocumentQueries";
import type { DocumentListItem } from "@/types/document";
import { FolderTreeView } from "./FolderTreeView";
import { ParseConfigModal } from "@/features/documents/components/ParseConfigModal";
import { StarDocumentModal } from "@/features/documents/components/StarDocumentModal";
import { useDocumentIngestion } from "@/features/dashboard/hooks/useDocumentIngestion";
import { KnowledgeSubgraphViewer } from "./KnowledgeSubgraphViewer";
import { BibliometricsPriorWorksCard } from "./BibliometricsPriorWorksCard";
import { libraryApi } from "../api/libraryApi";
import type {
  GraphQueryMode,
  GraphQueryResponseData,
  BibliometricsResponseData,
  GraphEdge,
} from "../types";
import { cn } from "@/lib/utils";

interface LibraryWorkspaceViewProps {
  onSelectDocument?: (doc: DocumentListItem) => void;
}

type LibraryFilterTab = "all" | "suggestions" | "favorites" | "folders";
type ViewLayout = "grid" | "list";

export function LibraryWorkspaceView({ onSelectDocument }: LibraryWorkspaceViewProps) {
  const [activeTab, setActiveTab] = useState<LibraryFilterTab>("all");
  const [viewLayout, setViewLayout] = useState<ViewLayout>("grid");
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedFolderId, setSelectedFolderId] = useState<string | null>(null);

  // GraphRAG States
  const [graphQuery, setGraphQuery] = useState("");
  const [graphMode, setGraphMode] = useState<GraphQueryMode>("hybrid");
  const [isQueryingGraph, setIsQueryingGraph] = useState(false);
  const [graphResult, setGraphResult] = useState<GraphQueryResponseData | null>(null);
  const [graphError, setGraphError] = useState<string | null>(null);
  const [showSubgraph, setShowSubgraph] = useState(true);

  // Bibliometrics States
  const [folderBibliometrics, setFolderBibliometrics] = useState<BibliometricsResponseData | null>(null);
  const [isLoadingBibliometrics, setIsLoadingBibliometrics] = useState(false);
  const [showBibliometrics, setShowBibliometrics] = useState(false);

  // Modals state
  const [selectedParseDoc, setSelectedParseDoc] = useState<DocumentListItem | null>(null);
  const [selectedStarDoc, setSelectedStarDoc] = useState<DocumentListItem | null>(null);

  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const { ingest } = useDocumentIngestion();

  const {
    data: paginatedData,
    refetch,
  } = useDocumentsList({
    page: currentPage,
    per_page: 24,
  });

  const starMutation = useStarDocumentMutation();
  const deleteMutation = useDeleteDocumentMutation();

  const rawDocuments = useMemo(() => paginatedData?.data || [], [paginatedData]);
  const meta = paginatedData?.meta;
  const totalPages = meta?.total_pages ?? Math.max(1, Math.ceil((meta?.total ?? rawDocuments.length) / 24));

  // Filter based on active tab and search query - strict persistence for My Library
  const documents = useMemo(() => {
    let result = rawDocuments.filter((d) => Boolean(d.is_persistent || d.starred_at || d.folder_id));

    if (activeTab === "favorites") {
      result = result.filter((d) => Boolean(d.starred_at || d.folder_id));
    } else if (activeTab === "suggestions") {
      result = result.slice(0, 6);
    } else if (activeTab === "folders" && selectedFolderId) {
      result = result.filter((d) => d.folder_id === selectedFolderId);
    }

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (d) =>
          (d.title ? d.title.toLowerCase().includes(q) : false) ||
          d.filename.toLowerCase().includes(q) ||
          (d.authors ? d.authors.some((a) => a.toLowerCase().includes(q)) : false)
      );
    }

    return result;
  }, [rawDocuments, activeTab, selectedFolderId, searchQuery]);

  // Fetch Bibliometrics when folder changes and tab is folders
  useEffect(() => {
    if (selectedFolderId && activeTab === "folders") {
      let isSubscribed = true;
      setIsLoadingBibliometrics(true);
      libraryApi
        .getFolderBibliometrics(selectedFolderId)
        .then((res) => {
          if (isSubscribed) {
            setFolderBibliometrics(res);
            setIsLoadingBibliometrics(false);
          }
        })
        .catch(() => {
          if (isSubscribed) {
            setFolderBibliometrics(null);
            setIsLoadingBibliometrics(false);
          }
        });

      return () => {
        isSubscribed = false;
      };
    } else {
      setFolderBibliometrics(null);
    }
  }, [selectedFolderId, activeTab]);

  const handleGraphSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const query = graphQuery.trim();
    if (!query) return;

    setIsQueryingGraph(true);
    setGraphError(null);
    try {
      const res = await libraryApi.queryGraph({
        query,
        mode: graphMode,
        folder_id: selectedFolderId || null,
      });
      setGraphResult(res);
      setShowSubgraph(true);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Truy vấn GraphRAG thất bại. Vui lòng thử lại.";
      setGraphError(message);
    } finally {
      setIsQueryingGraph(false);
    }
  };

  const handleToggleStar = async (doc: DocumentListItem, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      if (doc.starred_at) {
        // Unstar
        await starMutation.mutateAsync({ documentId: doc.id, folderId: null });
      } else {
        // Open star modal to pick folder or star directly
        setSelectedStarDoc(doc);
      }
    } catch (err) {
      console.warn("Failed to toggle star:", err);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      await ingest(file);
      refetch();
    }
  };

  const handleDelete = async (docId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm("Bạn có chắc chắn muốn xóa tài liệu này khỏi thư viện?")) {
      try {
        await deleteMutation.mutateAsync(docId);
      } catch (err) {
        console.warn("Failed to delete document:", err);
      }
    }
  };

  const handleEdgeSelect = (edge: GraphEdge) => {
    if (edge.document_id && onSelectDocument) {
      const matched = rawDocuments.find((d) => d.id === edge.document_id);
      if (matched) {
        onSelectDocument(matched);
      }
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#fbf9f5] dark:bg-[#181715] overflow-hidden select-none">
      {/* 1. Header Bar */}
      <header className="h-14 px-6 border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#fdfcf9] dark:bg-[#1c1b18] flex items-center justify-between shrink-0 gap-4">
        {/* Title & Stats */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="w-8 h-8 rounded-lg bg-stone-500/10 dark:bg-stone-500/20 flex items-center justify-center text-stone-700 dark:text-stone-300">
            <Library className="w-4 h-4 stroke-[2]" />
          </div>
          <div>
            <h1 className="text-sm font-semibold font-anthropic-serif text-ink dark:text-zinc-100">
              Library
            </h1>
            <p className="text-[11px] text-muted dark:text-zinc-400">
              {meta?.total ?? rawDocuments.length} documents
            </p>
          </div>
        </div>

        {/* Search Bar */}
        <div className="relative flex-1 max-w-md hidden md:block">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-muted dark:text-zinc-500 pointer-events-none" />
          <input
            type="text"
            placeholder="Search title, author, DOI..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full h-8 pl-8 pr-3 rounded-lg bg-white dark:bg-[#201e1a] border border-[#e2dcd2] dark:border-[#322f2a] text-xs text-ink dark:text-zinc-100 placeholder:text-muted dark:placeholder:text-zinc-500 outline-none focus:border-[#c15f3e] transition-colors"
          />
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 shrink-0">
          {/* View Toggle */}
          <div className="flex items-center bg-[#eae5db] dark:bg-[#24221e] p-0.5 rounded-lg border border-[#ded8cc] dark:border-[#302d28]">
            <button
              type="button"
              onClick={() => setViewLayout("grid")}
              className={cn(
                "p-1 rounded-md transition-colors cursor-pointer",
                viewLayout === "grid"
                  ? "bg-white dark:bg-[#1a1916] text-[#c15f3e] shadow-xs"
                  : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200"
              )}
              title="Grid"
            >
              <LayoutGrid className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => setViewLayout("list")}
              className={cn(
                "p-1 rounded-md transition-colors cursor-pointer",
                viewLayout === "list"
                  ? "bg-white dark:bg-[#1a1916] text-[#c15f3e] shadow-xs"
                  : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200"
              )}
              title="List"
            >
              <ListIcon className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* + Upload PDF Button */}
          <button
            type="button"
            onClick={handleUploadClick}
            className="h-8 px-3 rounded-lg text-xs font-medium flex items-center gap-1.5 bg-[#c15f3e] hover:bg-[#a84f32] text-white shadow-xs transition-colors cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5 stroke-[2.5]" />
            <span>Upload PDF</span>
          </button>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf"
            className="hidden"
          />
        </div>
      </header>

      {/* 2. Filter Tabs Ribbon */}
      <div className="px-6 py-2 border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#f8f6f0] dark:bg-[#1a1916] flex items-center justify-between shrink-0 overflow-x-auto">
        <div className="flex items-center gap-1 text-xs font-medium">
          {[
            { id: "all" as const, label: "All", icon: Library },
            { id: "suggestions" as const, label: "Suggested", icon: Sparkles },
            { id: "favorites" as const, label: "Starred", icon: Star },
            { id: "folders" as const, label: "Folders", icon: Folder },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              onClick={() => setActiveTab(id)}
              className={cn(
                "px-2.5 py-1 rounded-lg flex items-center gap-1.5 transition-all cursor-pointer whitespace-nowrap",
                activeTab === id
                  ? "bg-white dark:bg-[#24221e] text-ink dark:text-zinc-100 font-semibold shadow-xs border border-[#e2dcd2] dark:border-[#33302b]"
                  : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200"
              )}
            >
              <Icon className="w-3.5 h-3.5 stroke-[2]" />
              <span>{label}</span>
            </button>
          ))}
        </div>

        {activeTab === "folders" && selectedFolderId && (
          <button
            type="button"
            onClick={() => setShowBibliometrics(!showBibliometrics)}
            className="px-2.5 py-1 rounded-lg border border-[#e2dcd2] dark:border-[#33302b] bg-white dark:bg-[#201e1a] text-xs font-medium text-ink-muted hover:text-ink dark:text-zinc-300 flex items-center gap-1.5 transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5 text-[#c15f3e]" />
            <span>{showBibliometrics ? "Ẩn Thư mục học" : "Xem Thư mục học"}</span>
          </button>
        )}
      </div>

      {/* 3. Main Body */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* A. GraphRAG Smart Dual-Level Search Box */}
          <div className="rounded-2xl border border-[#e8e4dc] dark:border-[#2a2824] bg-white dark:bg-[#1c1b18] p-4 shadow-xs">
            <form onSubmit={handleGraphSearch} className="space-y-3">
              <div className="flex items-center justify-between gap-3 flex-wrap">
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-muted font-mono">
                    Chế độ Tra Cứu Tri Thức:
                  </span>
                  <div className="flex items-center bg-[#f4f0e8] dark:bg-[#262420] p-0.5 rounded-lg border border-[#e5dfd5] dark:border-[#302d28]">
                    {(
                      [
                        { id: "hybrid" as const, label: "Hybrid" },
                        { id: "local" as const, label: "Local" },
                        { id: "global" as const, label: "Global" },
                      ] as const
                    ).map((m) => (
                      <button
                        key={m.id}
                        type="button"
                        onClick={() => setGraphMode(m.id)}
                        className={cn(
                          "px-2.5 py-1 rounded-md text-xs font-medium transition-all cursor-pointer",
                          graphMode === m.id
                            ? "bg-white dark:bg-[#1c1b18] text-[#c15f3e] font-semibold shadow-xs"
                            : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200"
                        )}
                      >
                        {m.label}
                      </button>
                    ))}
                  </div>
                </div>

                {selectedFolderId && (
                  <span className="text-[11px] font-mono text-muted dark:text-zinc-400">
                    Lọc theo thư mục đang chọn
                  </span>
                )}
              </div>

              <div className="relative flex items-center gap-2">
                <div className="relative flex-1">
                  <input
                    type="text"
                    value={graphQuery}
                    onChange={(e) => setGraphQuery(e.target.value)}
                    placeholder="Hỏi đáp SOTA, đối chiếu mô hình hoặc tra cứu đồ thị..."
                    className="w-full h-10 pl-3.5 pr-10 rounded-xl bg-[#faf8f4] dark:bg-[#201e1a] border border-[#e2dcd2] dark:border-[#322f2a] text-xs text-ink dark:text-zinc-100 placeholder:text-muted dark:placeholder:text-zinc-500 outline-none focus:border-[#c15f3e] transition-colors"
                  />
                  {graphQuery && (
                    <button
                      type="button"
                      onClick={() => setGraphQuery("")}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-ink"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                <button
                  type="submit"
                  data-testid="graphrag-search-submit"
                  disabled={isQueryingGraph || !graphQuery.trim()}
                  className="h-10 px-4 rounded-xl bg-[#c15f3e] hover:bg-[#a84f32] disabled:opacity-50 text-white text-xs font-medium flex items-center gap-1.5 transition-colors cursor-pointer shrink-0"
                >
                  {isQueryingGraph ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Send className="w-3.5 h-3.5" />
                  )}
                  <span>Tra cứu</span>
                </button>
              </div>
            </form>

            {graphError && (
              <div className="mt-3 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-700 dark:text-rose-400 text-xs">
                {graphError}
              </div>
            )}

            {/* Synthesized Answer & Subgraph */}
            {graphResult && (
              <div className="mt-4 pt-4 border-t border-[#ece8df] dark:border-[#282622] space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-500" />
                    <h3 className="text-xs font-semibold text-ink dark:text-zinc-100 uppercase tracking-wider font-mono">
                      Câu Trả Lời Tổng Hợp ({graphResult.mode_used})
                    </h3>
                  </div>

                  <button
                    type="button"
                    onClick={() => setShowSubgraph(!showSubgraph)}
                    className="text-xs text-muted hover:text-ink dark:text-zinc-400 flex items-center gap-1"
                  >
                    <span>{showSubgraph ? "Thu gọn đồ thị" : "Xem đồ thị tri thức"}</span>
                    {showSubgraph ? (
                      <ChevronUp className="w-3.5 h-3.5" />
                    ) : (
                      <ChevronDown className="w-3.5 h-3.5" />
                    )}
                  </button>
                </div>

                <div className="p-4 rounded-xl bg-[#faf8f4] dark:bg-[#1a1916] border border-[#ece8df] dark:border-[#2a2824] text-xs leading-relaxed text-ink dark:text-zinc-200 whitespace-pre-wrap">
                  {graphResult.answer}
                </div>

                {showSubgraph && graphResult.subgraph && (
                  <KnowledgeSubgraphViewer
                    subgraph={graphResult.subgraph}
                    onEdgeSelect={handleEdgeSelect}
                    height={440}
                  />
                )}
              </div>
            )}
          </div>

          {/* B. Bibliometrics Card (when toggled or available in folder) */}
          {activeTab === "folders" && (showBibliometrics || folderBibliometrics) && (
            <BibliometricsPriorWorksCard
              data={folderBibliometrics}
              loading={isLoadingBibliometrics}
            />
          )}

          {/* C. Documents and Folders Hierarchy */}
          {activeTab === "folders" ? (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="md:col-span-1 bg-white dark:bg-[#1f1d1a] p-4 rounded-2xl border border-[#e8e4dc] dark:border-[#2a2824]">
                <FolderTreeView
                  selectedFolderId={selectedFolderId}
                  onSelectFolder={(folderId) => setSelectedFolderId(folderId)}
                />
              </div>
              <div className="md:col-span-3">
                <DocumentGrid
                  documents={documents}
                  viewLayout={viewLayout}
                  onToggleStar={handleToggleStar}
                  onSelectDocument={onSelectDocument}
                  onOpenParseConfig={(doc) => setSelectedParseDoc(doc)}
                  onDelete={handleDelete}
                />
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              <DocumentGrid
                documents={documents}
                viewLayout={viewLayout}
                onToggleStar={handleToggleStar}
                onSelectDocument={onSelectDocument}
                onOpenParseConfig={(doc) => setSelectedParseDoc(doc)}
                onDelete={handleDelete}
              />

              {/* Pagination Controls */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between pt-4 border-t border-[#ece8df] dark:border-[#282622]">
                  <span className="text-xs text-muted dark:text-zinc-400 font-mono">
                    Page {currentPage} / {totalPages}
                  </span>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      disabled={currentPage <= 1}
                      onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                      className="p-1.5 rounded-lg border border-[#e2dcd2] dark:border-[#302d28] disabled:opacity-40 hover:bg-[#ece8df] dark:hover:bg-[#282622] transition-colors cursor-pointer"
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </button>
                    <button
                      type="button"
                      disabled={currentPage >= totalPages}
                      onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                      className="p-1.5 rounded-lg border border-[#e2dcd2] dark:border-[#302d28] disabled:opacity-40 hover:bg-[#ece8df] dark:hover:bg-[#282622] transition-colors cursor-pointer"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Parse Config Modal */}
      {selectedParseDoc && (
        <ParseConfigModal
          documentId={selectedParseDoc.id}
          documentTitle={selectedParseDoc.title || selectedParseDoc.filename}
          isOpen={Boolean(selectedParseDoc)}
          onClose={() => setSelectedParseDoc(null)}
        />
      )}

      {/* Star Document Modal */}
      {selectedStarDoc && (
        <StarDocumentModal
          documentId={selectedStarDoc.id}
          documentTitle={selectedStarDoc.title || selectedStarDoc.filename}
          isStarred={Boolean(selectedStarDoc.starred_at)}
          isOpen={Boolean(selectedStarDoc)}
          onClose={() => setSelectedStarDoc(null)}
          onStarSuccess={() => refetch()}
        />
      )}
    </div>
  );
}

interface DocumentGridProps {
  documents: DocumentListItem[];
  viewLayout: ViewLayout;
  onToggleStar: (doc: DocumentListItem, e: React.MouseEvent) => void;
  onSelectDocument?: (doc: DocumentListItem) => void;
  onOpenParseConfig: (doc: DocumentListItem) => void;
  onDelete: (docId: string, e: React.MouseEvent) => void;
}

function DocumentGrid({
  documents,
  viewLayout,
  onToggleStar,
  onSelectDocument,
  onOpenParseConfig,
  onDelete,
}: DocumentGridProps) {
  if (documents.length === 0) {
    return (
      <div className="p-12 text-center rounded-2xl border border-dashed border-[#e2dcd2] dark:border-[#2e2b26] bg-[#f8f6f0]/50 dark:bg-[#1a1916]/50">
        <BookOpen className="w-8 h-8 text-muted dark:text-zinc-600 mx-auto mb-2" />
        <p className="text-sm font-anthropic-serif font-semibold text-ink dark:text-zinc-200">
          No documents found
        </p>
        <p className="text-xs text-muted dark:text-zinc-400 mt-1">
          Upload a PDF or refine your search query.
        </p>
      </div>
    );
  }

  if (viewLayout === "list") {
    return (
      <div className="bg-white dark:bg-[#1f1d1a] rounded-2xl border border-[#e8e4dc] dark:border-[#2a2824] overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-[#ece8df] dark:border-[#2a2824] bg-[#f8f6f0] dark:bg-[#181715] text-muted dark:text-zinc-400 font-medium">
              <th className="py-3 px-4 w-10 text-center">★</th>
              <th className="py-3 px-4">Document</th>
              <th className="py-3 px-4">Authors</th>
              <th className="py-3 px-4">Year</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#f0eae1] dark:divide-[#282622]">
            {documents.map((doc) => (
              <tr
                key={doc.id}
                onClick={() => onSelectDocument && onSelectDocument(doc)}
                className="hover:bg-[#fbf9f5] dark:hover:bg-[#252320] transition-colors cursor-pointer group"
              >
                <td className="py-3 px-4 text-center">
                  <button
                    type="button"
                    onClick={(e) => onToggleStar(doc, e)}
                    className="p-1 rounded hover:bg-black/5 dark:hover:bg-white/5 cursor-pointer"
                  >
                    <Star
                      className={cn(
                        "w-4 h-4",
                        doc.starred_at
                          ? "fill-amber-400 text-amber-500"
                          : "text-muted hover:text-amber-500"
                      )}
                    />
                  </button>
                </td>
                <td className="py-3 px-4 font-medium text-ink dark:text-zinc-200">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-muted shrink-0" />
                    <span className="truncate max-w-xs">{doc.title || doc.filename}</span>
                  </div>
                </td>
                <td className="py-3 px-4 text-muted dark:text-zinc-400">
                  {doc.authors && doc.authors.length > 0 ? doc.authors.join(", ") : "—"}
                </td>
                <td className="py-3 px-4 text-muted dark:text-zinc-400 font-mono">
                  {doc.publication_year ?? "—"}
                </td>
                <td className="py-3 px-4">
                  {doc.status !== "completed" && (
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-amber-500/10 text-amber-700 dark:text-amber-400">
                      {doc.status}
                    </span>
                  )}
                </td>
                <td className="py-3 px-4 text-right">
                  <div className="flex items-center justify-end gap-1">
                    <button
                      type="button"
                      data-testid={`doc-config-btn-${doc.id}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        onOpenParseConfig(doc);
                      }}
                      className="p-1.5 rounded-lg hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink cursor-pointer transition-colors"
                      title="Tùy chọn phân tích"
                    >
                      <SlidersHorizontal className="w-3.5 h-3.5" />
                    </button>
                    <button
                      type="button"
                      data-testid={`doc-delete-btn-${doc.id}`}
                      onClick={(e) => onDelete(doc.id, e)}
                      className="p-1.5 rounded-lg hover:bg-rose-500/10 text-muted hover:text-rose-600 cursor-pointer transition-colors"
                      title="Xóa tài liệu"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  // Grid layout
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {documents.map((doc) => (
        <div
          key={doc.id}
          onClick={() => onSelectDocument && onSelectDocument(doc)}
          className="group relative bg-white dark:bg-[#1f1d1a] p-4 rounded-2xl border border-[#e8e4dc] dark:border-[#2a2824] hover:border-[#c15f3e]/40 transition-all cursor-pointer shadow-2xs hover:shadow-xs flex flex-col justify-between"
        >
          <div>
            <div className="flex items-start justify-between gap-2 mb-2">
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-black/5 dark:bg-white/5 text-muted">
                {doc.publication_year || "Paper"}
              </span>
              <button
                type="button"
                onClick={(e) => onToggleStar(doc, e)}
                className="p-1 rounded hover:bg-black/5 dark:hover:bg-white/5 cursor-pointer"
              >
                <Star
                  className={cn(
                    "w-4 h-4",
                    doc.starred_at
                      ? "fill-amber-400 text-amber-500"
                      : "text-muted hover:text-amber-500"
                  )}
                />
              </button>
            </div>

            <h4 className="text-xs font-semibold text-ink dark:text-zinc-100 line-clamp-2 mb-1.5 font-anthropic-serif group-hover:text-[#c15f3e] transition-colors">
              {doc.title || doc.filename}
            </h4>

            {doc.authors && doc.authors.length > 0 && (
              <p className="text-[11px] text-muted dark:text-zinc-400 line-clamp-1 mb-2">
                {doc.authors.join(", ")}
              </p>
            )}
          </div>

          <div className="flex items-center justify-between pt-3 border-t border-[#f0eae1] dark:border-[#262420] text-[10px] text-muted dark:text-zinc-500">
            <span className="font-mono">
              {doc.status !== "completed" ? doc.status : ""}
            </span>
            <div className="flex items-center gap-1">
              <button
                type="button"
                data-testid={`doc-config-btn-${doc.id}`}
                onClick={(e) => {
                  e.stopPropagation();
                  onOpenParseConfig(doc);
                }}
                className="p-1 rounded-lg hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink cursor-pointer transition-colors"
                title="Tùy chọn phân tích"
              >
                <SlidersHorizontal className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                data-testid={`doc-delete-btn-${doc.id}`}
                onClick={(e) => onDelete(doc.id, e)}
                className="p-1 rounded-lg hover:bg-rose-500/10 text-muted hover:text-rose-600 cursor-pointer transition-colors"
                title="Xóa tài liệu"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
