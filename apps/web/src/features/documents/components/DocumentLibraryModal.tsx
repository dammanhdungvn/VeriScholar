import { useState, useMemo } from "react";
import {
  X,
  Library,
  Search,
  FileText,
  Star,
  Trash2,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
  CheckCircle2,
  Clock,
  AlertCircle,
} from "lucide-react";
import { useDocumentsList, useDeleteDocumentMutation } from "../hooks/useDocumentQueries";
import type { DocumentListItem } from "@/types/document";
import { StarDocumentModal } from "./StarDocumentModal";
import { FolderTreeView } from "@/features/library/components/FolderTreeView";

interface DocumentLibraryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectDocument: (doc: DocumentListItem) => void;
  activeDocumentId?: string | null;
}

type StatusFilter = "all" | "completed" | "processing" | "uploaded" | "failed";

export function DocumentLibraryModal({
  isOpen,
  onClose,
  onSelectDocument,
  activeDocumentId,
}: DocumentLibraryModalProps) {
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedFolderId, setSelectedFolderId] = useState<string | null>(null);

  // Sub-modal states
  const [selectedStarDoc, setSelectedStarDoc] = useState<DocumentListItem | null>(null);
  const [deleteConfirmDoc, setDeleteConfirmDoc] = useState<DocumentListItem | null>(null);

  const {
    data: paginatedData,
    isLoading,
    isError,
    refetch,
  } = useDocumentsList({
    page: currentPage,
    per_page: 10,
    status: statusFilter === "all" ? undefined : statusFilter,
  });

  const deleteMutation = useDeleteDocumentMutation();

  const documents = useMemo(() => paginatedData?.data || [], [paginatedData]);
  const meta = paginatedData?.meta;
  const totalItems = meta?.total ?? documents.length;
  const totalPages = meta?.total_pages ?? Math.max(1, Math.ceil(totalItems / 10));

  // Client-side quick search by title or filename
  const filteredDocuments = useMemo(() => {
    if (!searchQuery.trim()) return documents;
    const q = searchQuery.toLowerCase();
    return documents.filter(
      (d) =>
        (d.title && d.title.toLowerCase().includes(q)) ||
        (d.filename && d.filename.toLowerCase().includes(q))
    );
  }, [documents, searchQuery]);

  if (!isOpen) return null;

  const handleDelete = async (doc: DocumentListItem) => {
    try {
      await deleteMutation.mutateAsync(doc.id);
      setDeleteConfirmDoc(null);
    } catch (err) {
      console.warn("Failed to delete document:", err);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-medium bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3 h-3" />
            <span>Hoàn thành</span>
          </span>
        );
      case "processing":
      case "pending":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-medium bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-500/20">
            <RefreshCw className="w-3 h-3 animate-spin" />
            <span>Đang xử lý</span>
          </span>
        );
      case "failed":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-medium bg-rose-500/10 text-rose-700 dark:text-rose-400 border border-rose-500/20">
            <AlertCircle className="w-3 h-3" />
            <span>Lỗi</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-medium bg-blue-500/10 text-blue-700 dark:text-blue-400 border border-blue-500/20">
            <Clock className="w-3 h-3" />
            <span>Mới tải lên</span>
          </span>
        );
    }
  };

  return (
    <>
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Thư viện tài liệu nghiên cứu"
        onClick={(e) => {
          if (e.target === e.currentTarget) onClose();
        }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/50 backdrop-blur-xs animate-in fade-in duration-150 text-xs"
      >
        <div className="w-full max-w-5xl lg:max-w-6xl max-h-[85vh] h-[85vh] bg-canvas dark:bg-[#1a1917] rounded-xl shadow-2xl border border-hairline dark:border-[#2f2b26] flex flex-col overflow-hidden">
          {/* Header */}
          <div className="h-13 px-5 border-b border-hairline dark:border-[#2f2b26] flex items-center justify-between shrink-0 bg-surface-soft/40 dark:bg-[#1f1d1a]">
            <div className="flex items-center gap-2.5 font-serif font-semibold text-sm text-ink dark:text-zinc-100">
              <Library className="w-4.5 h-4.5 text-coral-600 dark:text-coral-400" />
              <span>Thư viện tài liệu nghiên cứu (Document Library)</span>
              {totalItems > 0 && (
                <span className="font-mono text-[11px] px-2 py-0.5 rounded-full bg-coral-500/10 text-coral-700 dark:text-coral-300">
                  {totalItems} bài báo
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onClose}
                aria-label="Đóng thư viện"
                className="p-1 rounded-md hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink cursor-pointer"
              >
                <X className="w-4.5 h-4.5" />
              </button>
            </div>
          </div>

          {/* Main Dual-Pane Body */}
          <div className="flex flex-1 min-h-0 overflow-hidden">
            {/* Left Pane: Folder Tree */}
            <FolderTreeView
              selectedFolderId={selectedFolderId}
              onSelectFolder={setSelectedFolderId}
              className="w-56 sm:w-64 border-r border-hairline dark:border-[#2f2b26] shrink-0"
            />

            {/* Right Pane: Controls Bar, Documents List, Pagination */}
            <div className="flex-1 flex flex-col min-w-0 overflow-hidden">

          {/* Controls Bar: Filter tabs & Search Input */}
          <div className="p-4 border-b border-hairline dark:border-[#2f2b26] flex flex-wrap items-center justify-between gap-3 bg-surface-card/40 dark:bg-[#171614] shrink-0">
            {/* Status Tabs */}
            <div className="flex items-center gap-1 p-1 rounded-lg bg-surface-soft dark:bg-[#201e1b] border border-hairline dark:border-[#302c26]">
              {(
                [
                  { id: "all", label: "Tất cả" },
                  { id: "completed", label: "Đã bóc tách" },
                  { id: "processing", label: "Đang xử lý" },
                  { id: "uploaded", label: "Mới tải" },
                  { id: "failed", label: "Lỗi" },
                ] as const
              ).map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => {
                    setStatusFilter(tab.id);
                    setCurrentPage(1);
                  }}
                  className={`px-3 py-1 rounded-md text-[11px] font-sans font-medium transition-colors cursor-pointer ${
                    statusFilter === tab.id
                      ? "bg-canvas dark:bg-[#2b2824] text-ink dark:text-zinc-100 shadow-2xs font-semibold"
                      : "text-muted hover:text-ink dark:hover:text-zinc-200"
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Search Input */}
            <div className="relative w-64 max-w-full">
              <Search className="w-3.5 h-3.5 text-muted absolute left-2.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Tìm theo tiêu đề hoặc tên tệp..."
                className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-canvas dark:bg-[#141311] border border-hairline focus:border-coral-500 outline-none font-sans text-xs"
              />
            </div>
          </div>

          {/* Documents Table / List Area */}
          <div className="flex-1 overflow-y-auto p-4">
            {isLoading ? (
              <div className="space-y-3 py-8">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="h-16 rounded-lg bg-surface-soft/60 dark:bg-[#201e1b] animate-pulse" />
                ))}
              </div>
            ) : isError ? (
              <div className="text-center py-16 space-y-2">
                <AlertCircle className="w-6 h-6 text-amber-500 mx-auto" />
                <p className="text-muted">Không thể tải danh sách tài liệu từ hệ thống.</p>
                <button
                  type="button"
                  onClick={() => refetch()}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-surface-soft text-ink border border-hairline hover:bg-surface-cream-strong"
                >
                  <RefreshCw className="w-3 h-3" />
                  <span>Tải lại</span>
                </button>
              </div>
            ) : filteredDocuments.length === 0 ? (
              <div className="text-center py-16 space-y-2">
                <FileText className="w-8 h-8 text-muted/40 mx-auto" />
                <h4 className="font-serif font-medium text-ink dark:text-zinc-200 text-sm">
                  Không tìm thấy tài liệu phù hợp
                </h4>
                <p className="text-muted text-[11px] max-w-sm mx-auto">
                  Tải lên tệp PDF bài báo mới hoặc thay đổi bộ lọc trạng thái để xem các tài liệu khác.
                </p>
              </div>
            ) : (
              <div className="space-y-2.5">
                {filteredDocuments.map((doc) => {
                  const isActive = doc.id === activeDocumentId;
                  const dateStr = doc.created_at
                    ? new Date(doc.created_at).toLocaleDateString("vi-VN", {
                        year: "numeric",
                        month: "short",
                        day: "numeric",
                      })
                    : "";

                  return (
                    <div
                      key={doc.id}
                      className={`p-3.5 rounded-xl border transition-all duration-150 flex items-center justify-between gap-3 ${
                        isActive
                          ? "bg-coral-500/5 dark:bg-coral-500/10 border-coral-500/30"
                          : "bg-surface-card dark:bg-[#1f1d1a] border-hairline dark:border-[#2f2b26] hover:border-hairline-strong"
                      }`}
                    >
                      {/* Left: Document Info */}
                      <div className="flex items-start gap-3 min-w-0 flex-1">
                        <div className="w-8 h-8 rounded-lg bg-surface-soft dark:bg-[#282622] flex items-center justify-center shrink-0 mt-0.5 border border-hairline">
                          <FileText className="w-4 h-4 text-coral-600 dark:text-coral-400" />
                        </div>

                        <div className="min-w-0 flex-1 space-y-1">
                          <div className="flex items-center gap-2">
                            <h5 className="font-serif font-medium text-ink dark:text-zinc-100 text-xs sm:text-sm truncate">
                              {doc.title || doc.filename}
                            </h5>
                            {doc.is_persistent && (
                              <span title="Tài liệu đã lưu">
                                <Star className="w-3.5 h-3.5 text-amber-500 fill-amber-500 shrink-0" />
                              </span>
                            )}
                          </div>

                          <div className="flex items-center gap-3 text-[11px] text-muted font-sans">
                            <span className="font-mono truncate max-w-[200px]">{doc.filename}</span>
                            <span>•</span>
                            <span>{getStatusBadge(doc.status)}</span>
                            {dateStr && (
                              <>
                                <span>•</span>
                                <span>{dateStr}</span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Right: Actions */}
                      <div className="flex items-center gap-1.5 shrink-0">
                        {/* Star Button */}
                        <button
                          type="button"
                          onClick={() => setSelectedStarDoc(doc)}
                          title={doc.is_persistent ? "Quản lý thư mục lưu trữ" : "Lưu vĩnh viễn vào Thư viện (Star)"}
                          className="p-1.5 rounded-lg border border-hairline dark:border-zinc-700 hover:bg-surface-soft dark:hover:bg-[#282622] text-muted hover:text-amber-500 cursor-pointer transition-colors"
                        >
                          <Star className={`w-3.5 h-3.5 ${doc.is_persistent ? "text-amber-500 fill-amber-500" : ""}`} />
                        </button>

                        {/* Open in Workspace Button */}
                        <button
                          type="button"
                          onClick={() => {
                            onSelectDocument(doc);
                            onClose();
                          }}
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-coral-500 hover:bg-coral-600 text-white font-medium shadow-2xs transition-colors cursor-pointer text-xs"
                        >
                          <span>Mở đọc</span>
                          <ExternalLink className="w-3 h-3" />
                        </button>

                        {/* Delete Button */}
                        <button
                          type="button"
                          onClick={() => setDeleteConfirmDoc(doc)}
                          title="Xóa tài liệu khỏi hệ thống"
                          className="p-1.5 rounded-lg border border-hairline dark:border-zinc-700 hover:bg-rose-500/10 text-muted hover:text-rose-500 cursor-pointer transition-colors"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Footer: Pagination */}
          <div className="h-12 px-5 border-t border-hairline dark:border-[#2f2b26] flex items-center justify-between shrink-0 bg-surface-soft/40 dark:bg-[#1f1d1a]">
            <div className="text-[11px] text-muted font-sans">
              Trang {currentPage} / {totalPages} (Tổng cộng {totalItems} bài báo)
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage <= 1 || isLoading}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md border border-hairline hover:bg-black/5 dark:hover:bg-white/5 text-ink disabled:opacity-40 transition-colors"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
                <span>Trước</span>
              </button>
              <button
                type="button"
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage >= totalPages || isLoading}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md border border-hairline hover:bg-black/5 dark:hover:bg-white/5 text-ink disabled:opacity-40 transition-colors"
              >
                <span>Sau</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

      {/* Submodal 2: Star Document Modal */}
      {selectedStarDoc && (
        <StarDocumentModal
          isOpen={Boolean(selectedStarDoc)}
          onClose={() => setSelectedStarDoc(null)}
          documentId={selectedStarDoc.id}
          documentTitle={selectedStarDoc.title || selectedStarDoc.filename}
          isStarred={selectedStarDoc.is_persistent}
          onStarSuccess={() => refetch()}
        />
      )}

      {/* Submodal 3: Delete Confirmation Dialog */}
      {deleteConfirmDoc && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Xác nhận xóa tài liệu"
          className="fixed inset-0 z-60 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in duration-150 text-xs"
        >
          <div className="w-full max-w-sm bg-canvas dark:bg-[#1a1917] rounded-xl shadow-2xl border border-hairline dark:border-[#2f2b26] p-5 space-y-4">
            <div className="flex items-center gap-2 text-rose-600 dark:text-rose-400 font-serif font-semibold text-sm">
              <Trash2 className="w-4 h-4" />
              <span>Xác nhận xóa tài liệu</span>
            </div>
            <p className="text-muted leading-relaxed">
              Bạn có chắc chắn muốn xóa bài báo &ldquo;{deleteConfirmDoc.title || deleteConfirmDoc.filename}&rdquo;? Thao tác này sẽ xóa vĩnh viễn tệp cùng các trích dẫn liên quan và không thể hoàn tác.
            </p>
            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setDeleteConfirmDoc(null)}
                className="px-3 py-1.5 rounded-lg border border-hairline hover:bg-black/5 text-muted hover:text-ink"
              >
                Hủy
              </button>
              <button
                type="button"
                onClick={() => handleDelete(deleteConfirmDoc)}
                disabled={deleteMutation.isPending}
                className="px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-medium"
              >
                {deleteMutation.isPending ? "Đang xóa..." : "Xác nhận xóa"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
