import { useState, useMemo, useRef } from "react";
import { X, Plus, Link, Library, FileText, UploadCloud, Loader2, AlertCircle } from "lucide-react";
import type { DocumentListItem } from "@/types/document";
import { cn } from "@/lib/utils";

interface AddDocumentModalProps {
  isOpen: boolean;
  onClose: () => void;
  availableLibraryDocs: DocumentListItem[];
  currentDocumentIds: string[];
  onAddByDocumentId: (documentId: string) => Promise<void>;
  onAddByUrl: (url: string, title?: string) => Promise<void>;
  onAddByFile?: (file: File) => Promise<void>;
}

export function AddDocumentModal({
  isOpen,
  onClose,
  availableLibraryDocs,
  currentDocumentIds,
  onAddByDocumentId,
  onAddByUrl,
  onAddByFile,
}: AddDocumentModalProps) {
  const [tab, setTab] = useState<"library" | "upload" | "url">("library");
  const [url, setUrl] = useState("");
  const [urlTitle, setUrlTitle] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const selectableDocs = useMemo(() => {
    const raw = availableLibraryDocs || [];
    const notOpened = raw.filter(
      (doc) => !currentDocumentIds.includes(doc.id) && (doc as any).is_persistent !== false
    );
    const seen = new Set<string>();
    const deduplicated: DocumentListItem[] = [];
    for (const doc of notOpened) {
      const norm = (doc.title || doc.filename || "")
        .trim()
        .toLowerCase()
        .replace(/\.pdf$/i, "");
      if (norm && !seen.has(norm)) {
        seen.add(norm);
        deduplicated.push(doc);
      }
    }
    return deduplicated;
  }, [availableLibraryDocs, currentDocumentIds]);

  if (!isOpen) return null;

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

  const handleFileUpload = async (file: File) => {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setUploadError("Vui lòng chọn tệp định dạng PDF (.pdf).");
      return;
    }
    setIsSubmitting(true);
    setUploadError(null);
    try {
      if (onAddByFile) {
        await onAddByFile(file);
      }
      onClose();
    } catch (err) {
      console.error("Failed to upload document to session:", err);
      setUploadError(err instanceof Error ? err.message : "Tải lên bài báo thất bại.");
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
            <span aria-hidden="true">Thêm tài liệu ({currentDocumentIds.length}/5)</span>
            <span className="sr-only">Nạp bài báo vào phiên ({currentDocumentIds.length} / 5)</span>
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
            <span>Thư viện</span>
          </button>

          <button
            type="button"
            onClick={() => setTab("upload")}
            className={cn(
              "flex-1 py-2.5 flex items-center justify-center gap-1.5 font-medium border-b-2 transition-colors",
              tab === "upload"
                ? "border-primary text-primary bg-canvas dark:bg-[#1a1917]"
                : "border-transparent text-muted hover:text-ink"
            )}
          >
            <UploadCloud className="w-3.5 h-3.5" />
            <span>Tải lên PDF</span>
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
            <span>Đường dẫn (URL)</span>
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
          ) : tab === "upload" ? (
            <div className="space-y-3">
              {uploadError && (
                <div className="p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-700 dark:text-rose-300 flex items-center gap-2 text-xs">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{uploadError}</span>
                </div>
              )}

              <div
                onDragOver={(e) => {
                  e.preventDefault();
                  setIsDragging(true);
                }}
                onDragLeave={(e) => {
                  e.preventDefault();
                  setIsDragging(false);
                }}
                onDrop={(e) => {
                  e.preventDefault();
                  setIsDragging(false);
                  if (e.dataTransfer.files?.[0]) {
                    handleFileUpload(e.dataTransfer.files[0]);
                  }
                }}
                onClick={() => fileInputRef.current?.click()}
                className={cn(
                  "p-8 rounded-xl border-2 border-dashed transition-all flex flex-col items-center justify-center text-center cursor-pointer select-none",
                  isDragging
                    ? "border-primary bg-primary/10"
                    : "border-hairline dark:border-[#2f2b26] hover:border-primary/50 bg-surface-soft/30 dark:bg-[#141311]"
                )}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,application/pdf"
                  data-testid="session-pdf-file-input"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files?.[0]) {
                      handleFileUpload(e.target.files[0]);
                      e.target.value = "";
                    }
                  }}
                />
                {isSubmitting ? (
                  <div className="flex flex-col items-center space-y-2 py-2">
                    <Loader2 className="w-8 h-8 text-primary animate-spin" />
                    <span className="font-medium text-ink dark:text-zinc-200">
                      Đang tải và nạp bài báo vào phiên...
                    </span>
                  </div>
                ) : (
                  <div className="flex flex-col items-center space-y-1.5">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary mb-1">
                      <UploadCloud className="w-5 h-5" />
                    </div>
                    <div className="font-medium text-ink dark:text-zinc-200">
                      Kéo thả tệp PDF vào đây, hoặc{" "}
                      <span className="text-primary underline">chọn từ máy tính</span>
                    </div>
                    <p className="text-[11px] text-muted dark:text-zinc-400">
                      Chỉ hỗ trợ tệp định dạng .pdf (tối đa 50MB)
                    </p>
                  </div>
                )}
              </div>
            </div>
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
