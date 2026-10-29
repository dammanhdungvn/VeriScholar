import { useState, useMemo, useRef, useEffect } from "react";
import {
  Library,
  Search,
  LayoutGrid,
  List as ListIcon,
  Share2,
  Plus,
  Star,
  FileText,
  Folder,
  FolderPlus,
  FolderInput,
  ArrowLeft,
  Pencil,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  BookOpen,
  Trash2,
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { documentsApi } from "@/features/documents/api/documentsApi";
import {
  useDocumentsList,
  useDeleteDocumentMutation,
} from "@/features/documents/hooks/useDocumentQueries";
import type { DocumentListItem } from "@/types/document";
import { FolderCard } from "./FolderCard";
import { CreateFolderModal } from "./CreateFolderModal";
import { RenameFolderModal } from "./RenameFolderModal";
import { MoveToFolderModal } from "./MoveToFolderModal";
import {
  useFoldersListQuery,
  useDeleteFolderMutation,
} from "../hooks/useFolderQueries";
import type { FolderItem } from "../types";
import { useDocumentIngestion } from "@/features/dashboard/hooks/useDocumentIngestion";
import { LibraryGraphSidebar } from "./LibraryGraphSidebar";
import { GraphRagAssistantFab } from "./GraphRagAssistantFab";
import { BibliometricsPriorWorksCard } from "./BibliometricsPriorWorksCard";
import { libraryApi } from "../api/libraryApi";
import type {
  BibliometricsResponseData,
} from "../types";
import { cn } from "@/lib/utils";

interface LibraryWorkspaceViewProps {
  onSelectDocument?: (doc: DocumentListItem) => void;
}

export type LibraryFilterTab = "all" | "folders" | "graph";
type ViewLayout = "grid" | "list";

export function LibraryWorkspaceView({ onSelectDocument }: LibraryWorkspaceViewProps) {
  const [activeTab, setActiveTab] = useState<LibraryFilterTab>("all");
  const [viewLayout, setViewLayout] = useState<ViewLayout>("grid");
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedFolderId, setSelectedFolderId] = useState<string | null>(null);

  // Bibliometrics States
  const [folderBibliometrics, setFolderBibliometrics] = useState<BibliometricsResponseData | null>(null);
  const [isLoadingBibliometrics, setIsLoadingBibliometrics] = useState(false);
  const [showBibliometrics, setShowBibliometrics] = useState(false);

  // Modals state
  const [isCreateFolderOpen, setIsCreateFolderOpen] = useState(false);
  const [renameFolderTarget, setRenameFolderTarget] = useState<FolderItem | null>(null);
  const [moveDocTarget, setMoveDocTarget] = useState<DocumentListItem | null>(null);

  // Wiki Graph Sidebar state
  const [isGraphSidebarOpen, setIsGraphSidebarOpen] = useState(false);
  const [focusedNodeId, setFocusedNodeId] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const { ingest } = useDocumentIngestion();

  // Folders list query
  const { data: folders = [], refetch: refetchFolders } = useFoldersListQuery();
  const deleteFolderMutation = useDeleteFolderMutation();

  // Knowledge Graph query (LLM Wiki)
  const {
    data: libraryGraphData,
    isLoading: isLoadingLibraryGraph,
    refetch: refetchGraph,
  } = useQuery({
    queryKey: ["library", "graph", selectedFolderId],
    queryFn: () => libraryApi.getLibraryGraph(selectedFolderId),
  });

  const {
    data: paginatedData,
    refetch,
  } = useDocumentsList({
    star: true,
    page: currentPage,
    per_page: 24,
  });

  const deleteMutation = useDeleteDocumentMutation();

  const rawDocuments = useMemo(() => paginatedData?.data || [], [paginatedData]);
  const meta = paginatedData?.meta;
  const totalPages = meta?.total_pages ?? Math.max(1, Math.ceil((meta?.total ?? rawDocuments.length) / 24));

  const selectedFolder = useMemo(
    () => folders.find((f) => f.id === selectedFolderId) || null,
    [folders, selectedFolderId]
  );

  // Filter based on active tab and search query - strict persistence for My Library
  const documents = useMemo(() => {
    let result = rawDocuments.filter((d) => Boolean(d.is_persistent || d.starred_at || d.folder_id));

    if (activeTab === "folders" && selectedFolderId) {
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

  const handleToggleStar = async (doc: DocumentListItem, e: React.MouseEvent) => {
    e.stopPropagation();
    setMoveDocTarget(doc);
  };

  const handleDeleteFolder = async (folder: FolderItem) => {
    if (
      window.confirm(
        `Are you sure you want to delete folder "${folder.name}"? Papers inside will remain in All Papers.`
      )
    ) {
      try {
        await deleteFolderMutation.mutateAsync(folder.id);
        if (selectedFolderId === folder.id) {
          setSelectedFolderId(null);
        }
      } catch (err) {
        console.warn("Failed to delete folder:", err);
      }
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      try {
        await documentsApi.uploadDocument(
          file,
          undefined,
          true,
          undefined,
          undefined,
          selectedFolderId || undefined
        );
        refetch();
        refetchGraph();
      } catch (err) {
        console.warn("Direct library upload failed, falling back to ingestion:", err);
        await ingest(file);
        refetch();
        refetchGraph();
      }
    }
  };

  const handleDelete = async (docId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm("Are you sure you want to delete this document from your library?")) {
      try {
        await deleteMutation.mutateAsync(docId);
      } catch (err) {
        console.warn("Failed to delete document:", err);
      }
    }
  };

  return (
    <div className="flex-1 flex h-full bg-[#fbf9f5] dark:bg-[#181715] overflow-hidden select-none">
      {/* Main Workspace Area */}
      <div className="flex-1 flex flex-col h-full min-w-0 overflow-hidden">
        {/* 1. Header Bar */}
        <header className="h-14 px-6 border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#fdfcf9] dark:bg-[#1c1b18] flex items-center justify-between shrink-0 gap-4">
        {/* Title & Stats */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="w-8 h-8 rounded-lg bg-stone-500/10 dark:bg-stone-500/20 flex items-center justify-center text-stone-700 dark:text-stone-300">
            <Library className="w-4 h-4 stroke-[2]" />
          </div>
          <div>
            <h1 className="text-sm font-semibold font-anthropic-serif text-ink dark:text-zinc-100">
              My Library
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

          {/* Wiki Graph Sidebar Toggle */}
          <button
            type="button"
            onClick={() => setIsGraphSidebarOpen(!isGraphSidebarOpen)}
            className={cn(
              "h-8 px-2.5 rounded-lg text-xs font-medium flex items-center gap-1.5 border transition-colors cursor-pointer",
              isGraphSidebarOpen
                ? "bg-[#c15f3e]/10 border-[#c15f3e]/30 text-[#c15f3e]"
                : "bg-white dark:bg-[#201e1a] border-[#e2dcd2] dark:border-[#322f2a] text-ink dark:text-zinc-200 hover:bg-[#f5f2eb] dark:hover:bg-[#282622]"
            )}
            title="Toggle Wiki Graph Sidebar"
          >
            <Share2 className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Wiki Graph</span>
          </button>

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
            { id: "all" as const, label: "All Papers", icon: Library },
            { id: "folders" as const, label: "Folders", icon: Folder },
            { id: "graph" as const, label: "Knowledge Graph", icon: Share2 },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              onClick={() => {
                setActiveTab(id);
                if (id === "graph") {
                  setIsGraphSidebarOpen(true);
                }
              }}
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
            className="px-2.5 py-1 rounded-lg border border-[#e2dcd2] dark:border-[#33302b] bg-white dark:bg-[#201e1a] text-xs font-medium text-ink-muted hover:text-ink dark:text-zinc-300 flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <Sparkles className="w-3.5 h-3.5 text-[#c15f3e]" />
            <span>{showBibliometrics ? "Hide Bibliometrics" : "View Bibliometrics"}</span>
          </button>
        )}
      </div>

      {/* 3. Main Body */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* A. Bibliometrics Card (when toggled or available in folder) */}
          {activeTab === "folders" && (showBibliometrics || folderBibliometrics) && (
            <BibliometricsPriorWorksCard
              data={folderBibliometrics}
              loading={isLoadingBibliometrics}
            />
          )}

          {/* C. Knowledge Graph (LLM Wiki) in Sidebar + Documents Hierarchy */}
          {activeTab === "graph" ? (
            <div className="space-y-4">
              <div className="p-3 bg-[#c15f3e]/5 border border-[#c15f3e]/20 rounded-xl flex items-center justify-between text-xs text-[#c15f3e]">
                <div className="flex items-center gap-2">
                  <Share2 className="w-4 h-4 shrink-0" />
                  <span>
                    Interactive Wiki Knowledge Graph is active in the right sidebar. Click any paper to center its local subgraph.
                  </span>
                </div>
                {!isGraphSidebarOpen && (
                  <button
                    type="button"
                    onClick={() => setIsGraphSidebarOpen(true)}
                    className="font-medium hover:underline cursor-pointer text-xs"
                  >
                    Open Sidebar →
                  </button>
                )}
              </div>

              <DocumentGrid
                documents={documents}
                viewLayout={viewLayout}
                onToggleStar={handleToggleStar}
                onSelectDocument={onSelectDocument}
                onMoveFolder={(doc) => setMoveDocTarget(doc)}
                onDelete={handleDelete}
                onFocusGraph={(doc) => {
                  setFocusedNodeId(doc.id);
                  setIsGraphSidebarOpen(true);
                }}
                focusedDocId={focusedNodeId}
              />
            </div>
          ) : activeTab === "folders" ? (
            !selectedFolderId ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between pb-2">
                  <div>
                    <h2 className="text-sm font-semibold font-anthropic-serif text-ink dark:text-zinc-100">
                      Folders
                    </h2>
                    <p className="text-xs text-muted dark:text-zinc-400">
                      Organize your research papers by project and topic.
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setIsCreateFolderOpen(true)}
                    className="h-8 px-3 rounded-lg text-xs font-medium flex items-center gap-1.5 bg-[#c15f3e] hover:bg-[#a84f32] text-white shadow-xs transition-colors cursor-pointer"
                  >
                    <FolderPlus className="w-3.5 h-3.5" />
                    <span>New Folder</span>
                  </button>
                </div>

                {folders.length === 0 ? (
                  <div className="p-12 text-center rounded-2xl border border-dashed border-[#e2dcd2] dark:border-[#2e2b26] bg-[#f8f6f0]/50 dark:bg-[#1a1916]/50">
                    <Folder className="w-8 h-8 text-muted dark:text-zinc-600 mx-auto mb-2" />
                    <p className="text-sm font-anthropic-serif font-semibold text-ink dark:text-zinc-200">
                      No folders yet
                    </p>
                    <p className="text-xs text-muted dark:text-zinc-400 mt-1 mb-4">
                      Create your first folder to organize your library.
                    </p>
                    <button
                      type="button"
                      onClick={() => setIsCreateFolderOpen(true)}
                      className="h-8 px-3 rounded-lg text-xs font-medium inline-flex items-center gap-1.5 bg-[#c15f3e] hover:bg-[#a84f32] text-white transition-colors cursor-pointer"
                    >
                      <FolderPlus className="w-3.5 h-3.5" />
                      <span>New Folder</span>
                    </button>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {folders.map((folder) => {
                      const count = rawDocuments.filter((d) => d.folder_id === folder.id).length;
                      return (
                        <FolderCard
                          key={folder.id}
                          folder={folder}
                          paperCount={count}
                          onClick={() => setSelectedFolderId(folder.id)}
                          onRename={(f) => setRenameFolderTarget(f)}
                          onDelete={(f) => handleDeleteFolder(f)}
                        />
                      );
                    })}
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {/* Drill-down Header with Breadcrumb */}
                <div className="flex items-center justify-between pb-2 border-b border-[#ece8df] dark:border-[#282622]">
                  <div className="flex items-center gap-3">
                    <button
                      type="button"
                      onClick={() => setSelectedFolderId(null)}
                      className="h-8 px-2.5 rounded-lg border border-[#e2dcd2] dark:border-[#322f2a] bg-white dark:bg-[#201e1a] text-xs font-medium text-ink dark:text-zinc-200 hover:bg-[#f5f2eb] dark:hover:bg-[#282622] flex items-center gap-1.5 transition-colors cursor-pointer"
                    >
                      <ArrowLeft className="w-3.5 h-3.5" />
                      <span>Back to Folders</span>
                    </button>
                    <div>
                      <h2 className="text-sm font-semibold font-anthropic-serif text-ink dark:text-zinc-100 flex items-center gap-2">
                        <Folder className="w-4 h-4 text-[#c15f3e]" />
                        <span>{selectedFolder?.name || "Folder"}</span>
                        <span className="text-xs font-normal text-muted dark:text-zinc-400 font-mono">
                          ({documents.length} {documents.length === 1 ? "paper" : "papers"})
                        </span>
                      </h2>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {selectedFolder && (
                      <button
                        type="button"
                        onClick={() => setRenameFolderTarget(selectedFolder)}
                        className="p-1.5 rounded-lg border border-[#e2dcd2] dark:border-[#322f2a] text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200 hover:bg-black/5 transition-colors cursor-pointer"
                        title="Rename Folder"
                      >
                        <Pencil className="w-3.5 h-3.5" />
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={handleUploadClick}
                      className="h-8 px-3 rounded-lg text-xs font-medium flex items-center gap-1.5 bg-[#c15f3e] hover:bg-[#a84f32] text-white shadow-xs transition-colors cursor-pointer"
                    >
                      <Plus className="w-3.5 h-3.5 stroke-[2.5]" />
                      <span>Upload PDF</span>
                    </button>
                  </div>
                </div>

                {/* Folder Papers Grid */}
                <DocumentGrid
                  documents={documents}
                  viewLayout={viewLayout}
                  onToggleStar={handleToggleStar}
                  onSelectDocument={onSelectDocument}
                  onMoveFolder={(doc) => setMoveDocTarget(doc)}
                  onDelete={handleDelete}
                  onFocusGraph={(doc) => {
                    setFocusedNodeId(doc.id);
                    setIsGraphSidebarOpen(true);
                  }}
                  focusedDocId={focusedNodeId}
                />
              </div>
            )
          ) : (
            <div className="space-y-6">
              <DocumentGrid
                documents={documents}
                viewLayout={viewLayout}
                onToggleStar={handleToggleStar}
                onSelectDocument={onSelectDocument}
                onMoveFolder={(doc) => setMoveDocTarget(doc)}
                onDelete={handleDelete}
                onFocusGraph={(doc) => {
                  setFocusedNodeId(doc.id);
                  setIsGraphSidebarOpen(true);
                }}
                focusedDocId={focusedNodeId}
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
    </div>

    {/* Right Sidebar: Wiki Knowledge Graph & Local Focus */}
    <LibraryGraphSidebar
      isOpen={isGraphSidebarOpen}
      onClose={() => setIsGraphSidebarOpen(false)}
      graphData={libraryGraphData || null}
      isLoading={isLoadingLibraryGraph}
      focusedNodeId={focusedNodeId}
      onClearFocus={() => setFocusedNodeId(null)}
      onSelectDocument={onSelectDocument}
    />

    {/* Floating GraphRAG Assistant Bubble */}
      <GraphRagAssistantFab folderId={selectedFolderId} />

      {/* Create Folder Modal */}
      <CreateFolderModal
        isOpen={isCreateFolderOpen}
        onClose={() => setIsCreateFolderOpen(false)}
        onSuccess={(id) => {
          refetchFolders();
          setSelectedFolderId(id);
        }}
      />

      {/* Rename Folder Modal */}
      <RenameFolderModal
        isOpen={Boolean(renameFolderTarget)}
        folder={renameFolderTarget}
        onClose={() => setRenameFolderTarget(null)}
        onSuccess={() => {
          refetchFolders();
        }}
      />

      {/* Move Document to Folder Modal */}
      {moveDocTarget && (
        <MoveToFolderModal
          isOpen={Boolean(moveDocTarget)}
          documentId={moveDocTarget.id}
          documentTitle={moveDocTarget.title || moveDocTarget.filename}
          currentFolderId={moveDocTarget.folder_id}
          onClose={() => setMoveDocTarget(null)}
          onSuccess={() => {
            refetch();
            refetchFolders();
          }}
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
  onMoveFolder: (doc: DocumentListItem) => void;
  onDelete: (docId: string, e: React.MouseEvent) => void;
  onFocusGraph?: (doc: DocumentListItem) => void;
  focusedDocId?: string | null;
}

function DocumentGrid({
  documents,
  viewLayout,
  onToggleStar,
  onSelectDocument,
  onMoveFolder,
  onDelete,
  onFocusGraph,
  focusedDocId,
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
                      data-testid={`doc-graph-btn-${doc.id}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        onFocusGraph?.(doc);
                      }}
                      className={cn(
                        "p-1.5 rounded-lg text-muted hover:text-[#c15f3e] hover:bg-[#c15f3e]/10 cursor-pointer transition-colors",
                        focusedDocId === doc.id && "text-[#c15f3e] bg-[#c15f3e]/10"
                      )}
                      title="Focus in Wiki Graph"
                    >
                      <Share2 className="w-3.5 h-3.5" />
                    </button>
                    <button
                      type="button"
                      data-testid={`doc-move-btn-${doc.id}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        onMoveFolder(doc);
                      }}
                      className="p-1.5 rounded-lg hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink cursor-pointer transition-colors"
                      title="Move to Folder"
                    >
                      <FolderInput className="w-3.5 h-3.5" />
                    </button>
                    <button
                      type="button"
                      data-testid={`doc-delete-btn-${doc.id}`}
                      onClick={(e) => onDelete(doc.id, e)}
                      className="p-1.5 rounded-lg hover:bg-rose-500/10 text-muted hover:text-rose-600 cursor-pointer transition-colors"
                      title="Delete document"
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
          className={cn(
            "group relative bg-white dark:bg-[#1f1d1a] p-4 rounded-2xl border border-[#e8e4dc] dark:border-[#2a2824] hover:border-[#c15f3e]/40 transition-all cursor-pointer shadow-2xs hover:shadow-xs flex flex-col justify-between",
            focusedDocId === doc.id && "ring-2 ring-[#c15f3e] border-[#c15f3e]"
          )}
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
                data-testid={`doc-graph-btn-${doc.id}`}
                onClick={(e) => {
                  e.stopPropagation();
                  onFocusGraph?.(doc);
                }}
                className={cn(
                  "p-1 rounded-lg text-muted hover:text-[#c15f3e] hover:bg-[#c15f3e]/10 cursor-pointer transition-colors",
                  focusedDocId === doc.id && "text-[#c15f3e] bg-[#c15f3e]/10"
                )}
                title="Focus in Wiki Graph"
              >
                <Share2 className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                data-testid={`doc-move-btn-${doc.id}`}
                onClick={(e) => {
                  e.stopPropagation();
                  onMoveFolder(doc);
                }}
                className="p-1 rounded-lg hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink cursor-pointer transition-colors"
                title="Move to Folder"
              >
                <FolderInput className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                data-testid={`doc-delete-btn-${doc.id}`}
                onClick={(e) => onDelete(doc.id, e)}
                className="p-1 rounded-lg hover:bg-rose-500/10 text-muted hover:text-rose-600 cursor-pointer transition-colors"
                title="Delete document"
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
