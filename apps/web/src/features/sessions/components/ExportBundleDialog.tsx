import { useState } from "react";
import { X, Archive, Download, FileCheck } from "lucide-react";

interface ExportBundleDialogProps {
  isOpen: boolean;
  onClose: () => void;
  sessionId: string;
  sessionTitle: string;
  onExport: () => Promise<Blob>;
}

export function ExportBundleDialog({
  isOpen,
  onClose,
  sessionId,
  sessionTitle,
  onExport,
}: ExportBundleDialogProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  if (!isOpen) return null;

  const handleDownload = async () => {
    setIsExporting(true);
    try {
      const blob = await onExport();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = `verischolar_session_${sessionId.slice(0, 8)}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
      setIsSuccess(true);
    } catch {
      // Error handled by parent
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Xuất gói nghiên cứu ngoại tuyến"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in duration-150 text-xs"
    >
      <div className="w-full max-w-md bg-canvas dark:bg-[#1a1917] rounded-lg shadow-2xl border border-hairline dark:border-[#2f2b26] flex flex-col overflow-hidden">
        <div className="h-11 px-4 border-b border-hairline dark:border-[#2f2b26] flex items-center justify-between">
          <div className="flex items-center gap-2 font-serif font-semibold text-xs text-ink dark:text-zinc-100">
            <Archive className="w-4 h-4 text-primary" />
            <span>Xuất Gói Nghiên Cứu Ngoại Tuyến (.zip)</span>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Đóng hộp thoại"
            className="p-1 rounded hover:bg-black/5 text-muted hover:text-ink"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-5 space-y-4">
          <div className="space-y-2">
            <p className="text-body dark:text-zinc-300 leading-relaxed">
              Gói tài liệu ngoại tuyến trọn gói (.zip) bao gồm đầy đủ dữ liệu phiên làm việc{" "}
              <strong>&ldquo;{sessionTitle}&rdquo;</strong>:
            </p>
            <ul className="space-y-1.5 p-3 rounded-md bg-surface-soft dark:bg-[#201e1b] border border-hairline dark:border-[#2c2823] font-mono text-[11px] text-muted">
              <li className="flex items-center gap-2">
                <FileCheck className="w-3.5 h-3.5 text-primary" />
                <span>documents/ — Tệp PDF gốc có Native ISO Highlights</span>
              </li>
              <li className="flex items-center gap-2">
                <FileCheck className="w-3.5 h-3.5 text-primary" />
                <span>master_lesson.md — Bài học Markdown chuẩn AST & KaTeX</span>
              </li>
              <li className="flex items-center gap-2">
                <FileCheck className="w-3.5 h-3.5 text-primary" />
                <span>chat_transcript.html — Lịch sử hội thoại tự chứa CSS/JS</span>
              </li>
            </ul>
          </div>

          {isSuccess && (
            <div className="p-3 rounded-md bg-teal-500/10 border border-teal-500/30 text-teal-700 dark:text-teal-300 font-medium">
              Đã tạo và tải gói ngoại tuyến thành công!
            </div>
          )}

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-hairline dark:border-[#2f2b26]">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 rounded-md hover:bg-black/5 text-muted"
            >
              Đóng
            </button>
            <button
              type="button"
              onClick={handleDownload}
              disabled={isExporting}
              className="px-4 py-1.5 rounded-md bg-primary hover:bg-primary/90 text-white font-medium flex items-center gap-1.5 shadow-xs disabled:opacity-50"
            >
              <Download className="w-3.5 h-3.5" />
              <span>{isExporting ? "Đang nén dữ liệu..." : "Tải gói ZIP"}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
