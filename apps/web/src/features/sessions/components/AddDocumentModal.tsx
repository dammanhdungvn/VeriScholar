import { useState } from "react";
import { X, Plus, Link, Library, FileText } from "lucide-react";
import type { DocumentListItem } from "@/types/document";
import { cn } from "@/lib/utils";

interface AddDocumentModalProps {
  isOpen: boolean;
  onClose: () => void;
  availableLibraryDocs: DocumentListItem[];
  currentDocumentIds: string[];
  onAddByDocumentId: (documentId: string) => Promise<void>;
  onAddByUrl: (url: string, title?: string) => Promise<void>;
}

export function AddDocumentModal({
  isOpen,
  onClose,
  availableLibraryDocs,
  currentDocumentIds,
  onAddByDocumentId,
  onAddByUrl,
}: AddDocumentModalProps) {
  const [tab, setTab] = useState<"library" | "url">("library");
  const [url, setUrl] = useState("");
  const [urlTitle, setUrlTitle] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const selectableDocs = availableLibraryDocs.filter(
    (doc) => !currentDocumentIds.includes(doc.id)
  );

  const handleSelectDoc = async (docId: string) => {
    setIsSubmitting(true);
    try {
      await onAddByDocumentId(docId);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    setIsSubmitting(true);
    try {
      await onAddByUrl(url.trim(), urlTitle.trim() || undefined);
      setUrl("");
      setUrlTitle("");
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Nạp bài báo vào phiên nghiên cứu"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in duration-150"
    >
      <div className="w-full max-w-lg bg-canvas dark:bg-[#1a1917] rounded-lg shadow-2xl border border-hairline dark:border-[#2f2b26] flex flex-col overflow-hidden text-xs">
        {/* Header */}
        <div className="h-12 px-4 border-b border-hairline dark:border-[#2f2b26] flex items-center justify-between">
          <div className="flex items-center gap-2 font-serif font-semibold text-xs text-ink dark:text-zinc-100">
            <Plus className="w-4 h-4 text-primary" />
            <span>Nạp bài báo vào phiên ({currentDocumentIds.length} / 5)</span>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Đóng hộp thoại"
            className="p-1 rounded hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tab switch */}
        <div className="flex border-b border-hairline dark:border-[#2f2b26] bg-surface-soft/40 dark:bg-[#1d1b18]">
          <button
            type="button"
            onClick={() => setTab("library")}
            className={cn(
              "flex-1 py-2.5 flex items-center justify-center gap-1.5 font-medium border-b-2 transition-colors",
              tab === "library"
                ? "border-primary text-primary bg-canvas dark:bg-[#1a1917]"
                : "border-transparent text-muted hover:text-ink"
            )}
          >
            <Library className="w-3.5 h-3.5" />
            <span>Từ Thư viện cá nhân</span>
          </button>

          <button
            type="button"
            onClick={() => setTab("url")}
            className={cn(
              "flex-1 py-2.5 flex items-center justify-center gap-1.5 font-medium border-b-2 transition-colors",
              tab === "url"
                ? "border-primary text-primary bg-canvas dark:bg-[#1a1917]"
                : "border-transparent text-muted hover:text-ink"
            )}
          >
            <Link className="w-3.5 h-3.5" />
            <span>Nhập link trực tuyến</span>
          </button>
        </div>

        {/* Body */}
        <div className="p-4 max-h-80 overflow-y-auto">
          {tab === "library" ? (
            selectableDocs.length === 0 ? (
              <div className="text-center py-10 text-muted space-y-2">
                <FileText className="w-6 h-6 mx-auto text-muted/50" />
                <p>Không có bài báo nào khả dụng trong thư viện để nạp thêm.</p>
              </div>
            ) : (
              <div className="space-y-1.5">
                {selectableDocs.map((doc) => (
                  <div
                    key={doc.id}
                    onClick={() => !isSubmitting && handleSelectDoc(doc.id)}
                    className="p-2.5 rounded-md border border-hairline dark:border-[#2e2a25] hover:bg-surface-soft dark:hover:bg-[#252320] flex items-center justify-between cursor-pointer transition-colors group"
                  >
                    <div className="truncate pr-2">
                      <h5 className="font-serif font-medium text-ink dark:text-zinc-200 group-hover:text-primary transition-colors truncate">
                        {doc.title || doc.filename}
                      </h5>
                      <span className="text-[10px] font-mono text-muted">
                        Trạng thái: {doc.status}
                      </span>
                    </div>
                    <button
                      type="button"
                      disabled={isSubmitting}
                      className="px-2 py-1 rounded bg-primary text-white font-medium text-[11px] shrink-0"
                    >
                      Chọn
                    </button>
                  </div>
                ))}
              </div>
            )
          ) : (
            <form onSubmit={handleUrlSubmit} className="space-y-3">
              <div className="space-y-1">
                <label className="block text-[11px] font-medium text-ink dark:text-zinc-200">
                  Đường dẫn tệp PDF bài báo (arXiv, PubMed, ACM, IEEE...)
                </label>
                <input
                  type="url"
                  required
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://arxiv.org/pdf/1706.03762.pdf"
                  className="w-full px-3 py-2 rounded-md bg-canvas dark:bg-[#141311] border border-hairline focus:border-primary outline-none font-mono text-xs"
                />
              </div>

              <div className="space-y-1">
                <label className="block text-[11px] font-medium text-ink dark:text-zinc-200">
                  Tiêu đề bài báo (Tùy chọn)
                </label>
                <input
                  type="text"
                  value={urlTitle}
                  onChange={(e) => setUrlTitle(e.target.value)}
                  placeholder="ví dụ: Attention Is All You Need"
                  className="w-full px-3 py-2 rounded-md bg-canvas dark:bg-[#141311] border border-hairline focus:border-primary outline-none font-sans text-xs"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-3 py-1.5 rounded-md hover:bg-black/5 text-muted"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || !url.trim()}
                  className="px-3.5 py-1.5 rounded-md bg-primary hover:bg-primary/90 text-white font-medium disabled:opacity-50"
                >
                  {isSubmitting ? "Đang nạp..." : "Nạp bài báo"}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
