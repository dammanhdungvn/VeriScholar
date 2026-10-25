import { useState, useMemo, useRef } from "react";
import {
  Library,
  Search,
  LayoutGrid,
  List as ListIcon,
  Plus,
  Star,
  MoreVertical,
  FileText,
  CheckCircle2,
  Clock,
  Folder,
  Sparkles,
  Trash2,
  Sliders,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  BookOpen
} from "lucide-react";
import {
  useDocumentsList,
  useStarDocumentMutation,
  useDeleteDocumentMutation
} from "@/features/documents/hooks/useDocumentQueries";
import type { DocumentListItem } from "@/types/document";
import { FolderTreeView } from "./FolderTreeView";
import { ParseConfigModal } from "@/features/documents/components/ParseConfigModal";
import { StarDocumentModal } from "@/features/documents/components/StarDocumentModal";
import { useDocumentIngestion } from "@/features/dashboard/hooks/useDocumentIngestion";
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

  // Modals state
  const [selectedParseDoc, setSelectedParseDoc] = useState<DocumentListItem | null>(null);
  const [selectedStarDoc, setSelectedStarDoc] = useState<DocumentListItem | null>(null);
  const [activeMenuDocId, setActiveMenuDocId] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const { ingest } = useDocumentIngestion();

  const {
    data: paginatedData,
    refetch
  } = useDocumentsList({
    page: currentPage,
    per_page: 24,
  });

  const starMutation = useStarDocumentMutation();
  const deleteMutation = useDeleteDocumentMutation();

  const rawDocuments = useMemo(() => paginatedData?.data || [], [paginatedData]);
  const meta = paginatedData?.meta;
  const totalPages = meta?.total_pages ?? Math.max(1, Math.ceil((meta?.total ?? rawDocuments.length) / 24));

  // Filter based on active tab and search query
  const documents = useMemo(() => {
    let result = rawDocuments;

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
        setActiveMenuDocId(null);
      } catch (err) {
        console.warn("Failed to delete document:", err);
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
      </div>

      {/* 3. Main Body */}
      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === "folders" ? (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 max-w-7xl mx-auto">
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
                activeMenuDocId={activeMenuDocId}
                setActiveMenuDocId={setActiveMenuDocId}
                onToggleStar={handleToggleStar}
                onSelectDocument={onSelectDocument}
                onOpenParseConfig={(doc) => setSelectedParseDoc(doc)}
                onDelete={handleDelete}
              />
            </div>
          </div>
        ) : (
          <div className="max-w-7xl mx-auto space-y-6">
            <DocumentGrid
              documents={documents}
              viewLayout={viewLayout}
              activeMenuDocId={activeMenuDocId}
              setActiveMenuDocId={setActiveMenuDocId}
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
  activeMenuDocId: string | null;
  setActiveMenuDocId: (id: string | null) => void;
  onToggleStar: (doc: DocumentListItem, e: React.MouseEvent) => void;
  onSelectDocument?: (doc: DocumentListItem) => void;
  onOpenParseConfig: (doc: DocumentListItem) => void;
  onDelete: (docId: string, e: React.MouseEvent) => void;
}

function DocumentGrid({
  documents,
  viewLayout,
  activeMenuDocId,
  setActiveMenuDocId,
  onToggleStar,
  onSelectDocument,
  onOpenParseConfig,
  onDelete
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
                <td className="py-3 px-4 font-semibold text-ink dark:text-zinc-100 group-hover:text-[#c15f3e] dark:group-hover:text-[#c15f3e]">
                  <div className="line-clamp-1">{doc.title || doc.filename}</div>
                </td>
                <td className="py-3 px-4 text-muted dark:text-zinc-400">
                  <div className="line-clamp-1">
                    {doc.authors && doc.authors.length > 0 ? doc.authors.join(", ") : "—"}
                  </div>
                </td>
                <td className="py-3 px-4 text-muted dark:text-zinc-400 font-mono">
                  {doc.year || "2024"}
                </td>
                <td className="py-3 px-4">
                  {doc.status === "completed" ? (
                    <span className="inline-flex items-center gap-1 text-[11px] font-mono text-emerald-700 dark:text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full">
                      <CheckCircle2 className="w-3 h-3" /> Ready
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-[11px] font-mono text-amber-700 dark:text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full">
                      <Clock className="w-3 h-3" /> {doc.status}
                    </span>
                  )}
                </td>
                <td className="py-3 px-4 text-right">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onOpenParseConfig(doc);
                    }}
                    className="p-1 rounded hover:bg-[#ece8df] dark:hover:bg-[#2e2b26] text-muted hover:text-ink mr-1 cursor-pointer"
                    title="Configure Parser"
                  >
                    <Sliders className="w-3.5 h-3.5" />
                  </button>
                  <button
                    type="button"
                    onClick={(e) => onDelete(doc.id, e)}
                    className="p-1 rounded hover:bg-rose-500/10 text-muted hover:text-rose-600 cursor-pointer"
                    title="Delete Document"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  // Grid Layout
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {documents.map((doc) => {
        const isMenuOpen = activeMenuDocId === doc.id;
        return (
          <div
            key={doc.id}
            onClick={() => onSelectDocument && onSelectDocument(doc)}
            className="group relative bg-white dark:bg-[#1f1d1a] rounded-2xl border border-[#e8e4dc] dark:border-[#2a2824] hover:border-coral-500/40 dark:hover:border-coral-500/40 hover:shadow-sm transition-all duration-200 overflow-hidden flex flex-col justify-between cursor-pointer"
          >
            {/* Thumbnail Header Area */}
            <div className="relative h-36 bg-[#f4eee5] dark:bg-[#252320] flex items-center justify-center p-4 border-b border-[#ece8df] dark:border-[#2a2824] overflow-hidden">
              <FileText className="w-14 h-14 text-coral-500/30 group-hover:scale-110 transition-transform duration-300 stroke-[1.2]" />

              {/* Star toggle top-left */}
              <button
                type="button"
                onClick={(e) => onToggleStar(doc, e)}
                className="absolute top-2.5 left-2.5 w-8 h-8 rounded-lg bg-white/90 dark:bg-[#1a1916]/90 backdrop-blur-xs flex items-center justify-center shadow-xs cursor-pointer hover:scale-105 transition-transform"
                title={doc.starred_at ? "Unfavorite" : "Favorite"}
              >
                <Star
                  className={cn(
                    "w-4 h-4 transition-colors",
                    doc.starred_at
                      ? "fill-amber-400 text-amber-500"
                      : "text-zinc-400 hover:text-amber-500"
                  )}
                />
              </button>

              {/* Context menu toggle top-right */}
              <div className="absolute top-2.5 right-2.5">
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setActiveMenuDocId(isMenuOpen ? null : doc.id);
                  }}
                  className="w-8 h-8 rounded-lg bg-white/90 dark:bg-[#1a1916]/90 backdrop-blur-xs flex items-center justify-center shadow-xs text-muted hover:text-ink cursor-pointer"
                >
                  <MoreVertical className="w-4 h-4" />
                </button>

                {isMenuOpen && (
                  <div
                    onClick={(e) => e.stopPropagation()}
                    className="absolute right-0 top-9 w-44 bg-white dark:bg-[#24221e] border border-[#e2dcd2] dark:border-[#33302b] rounded-xl shadow-xl z-20 p-1 text-xs space-y-0.5 animate-in fade-in zoom-in-95 duration-100"
                  >
                    <button
                      type="button"
                      onClick={() => {
                        setActiveMenuDocId(null);
                        if (onSelectDocument) onSelectDocument(doc);
                      }}
                      className="w-full px-2.5 py-1.5 rounded-lg text-left flex items-center gap-2 hover:bg-[#f2ece1] dark:hover:bg-[#2e2b26] text-ink dark:text-zinc-200 cursor-pointer"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                      <span>Open Reader</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setActiveMenuDocId(null);
                        onOpenParseConfig(doc);
                      }}
                      className="w-full px-2.5 py-1.5 rounded-lg text-left flex items-center gap-2 hover:bg-[#f2ece1] dark:hover:bg-[#2e2b26] text-ink dark:text-zinc-200 cursor-pointer"
                    >
                      <Sliders className="w-3.5 h-3.5" />
                      <span>Configure Parser</span>
                    </button>
                    <div className="border-t border-[#ece8df] dark:border-[#2e2b26] my-1" />
                    <button
                      type="button"
                      onClick={(e) => onDelete(doc.id, e)}
                      className="w-full px-2.5 py-1.5 rounded-lg text-left flex items-center gap-2 text-rose-600 dark:text-rose-400 hover:bg-rose-500/10 cursor-pointer"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      <span>Delete Document</span>
                    </button>
                  </div>
                )}
              </div>

              {/* Status Badge bottom-left */}
              <div className="absolute bottom-2 left-2">
                {doc.status === "completed" ? (
                  <span className="inline-flex items-center gap-1 text-[10px] font-mono font-medium text-emerald-700 dark:text-emerald-300 bg-white/95 dark:bg-[#1a1916]/95 px-2 py-0.5 rounded-md shadow-xs">
                    <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Ready
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 text-[10px] font-mono font-medium text-amber-700 dark:text-amber-300 bg-white/95 dark:bg-[#1a1916]/95 px-2 py-0.5 rounded-md shadow-xs">
                    <Clock className="w-3 h-3 text-amber-600" /> {doc.status}
                  </span>
                )}
              </div>
            </div>

            {/* Card Content Area */}
            <div className="p-4 flex-1 flex flex-col justify-between">
              <div>
                <h3 className="text-sm font-semibold font-anthropic-serif text-ink dark:text-zinc-100 group-hover:text-[#c15f3e] dark:group-hover:text-[#c15f3e] transition-colors line-clamp-2 leading-snug">
                  {doc.title || doc.filename}
                </h3>
                <p className="text-xs text-muted dark:text-zinc-400 mt-1 line-clamp-1">
                  {doc.authors && doc.authors.length > 0 ? doc.authors.join(", ") : "Unknown Author"}
                </p>
              </div>

              {/* Card Footer Metadata */}
              <div className="mt-4 pt-3 border-t border-[#f0eae1] dark:border-[#282622] flex items-center justify-between text-[11px] font-mono text-muted dark:text-zinc-500">
                <span>{doc.year || "2024"}</span>
                {doc.page_count && <span>{doc.page_count} pages</span>}
                {doc.file_size_bytes ? (
                  <span>{(doc.file_size_bytes / (1024 * 1024)).toFixed(1)} MB</span>
                ) : (
                  <span>PDF</span>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
