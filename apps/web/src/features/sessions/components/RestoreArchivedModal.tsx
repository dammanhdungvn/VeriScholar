import { useState } from "react";
import { X, UploadCloud, FileText, AlertCircle } from "lucide-react";

interface RestoreArchivedModalProps {
  isOpen: boolean;
  onClose: () => void;
  sessionId: string;
  onRestore: (file: File) => Promise<void>;
}

export function RestoreArchivedModal({
  isOpen,
  onClose,
  sessionId,
  onRestore,
}: RestoreArchivedModalProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.toLowerCase().endsWith(".pdf")) {
        setErrorMsg("Chỉ chấp nhận tệp định dạng .pdf");
        return;
      }
      setSelectedFile(file);
      setErrorMsg(null);
    }
  };

  const handleRestoreSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setIsUploading(true);
    setErrorMsg(null);
    try {
      await onRestore(selectedFile);
      onClose();
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Khôi phục phiên thất bại");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Khôi phục phiên nghiên cứu đã hết hạn TTL"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in duration-150 text-xs"
    >
      <div className="w-full max-w-md bg-canvas dark:bg-[#1a1917] rounded-lg shadow-2xl border border-hairline dark:border-[#2f2b26] flex flex-col overflow-hidden">
        <div className="h-11 px-4 border-b border-hairline dark:border-[#2f2b26] flex items-center justify-between">
          <div className="flex items-center gap-2 font-serif font-semibold text-xs text-ink dark:text-zinc-100">
            <UploadCloud className="w-4 h-4 text-primary" />
            <span>Kích hoạt lại phiên nghiên cứu quá hạn</span>
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

        <form onSubmit={handleRestoreSubmit} className="p-5 space-y-4">
          <p className="text-muted leading-relaxed">
            Phiên nghiên cứu ({sessionId.slice(0, 8)}...) này đã quá hạn lưu trữ 30 ngày. Vui lòng tải lại tệp PDF gốc để khôi phục phiên làm việc.
          </p>

          <label className="border-2 border-dashed border-hairline dark:border-[#332f29] hover:border-primary rounded-lg p-6 flex flex-col items-center justify-center cursor-pointer transition-colors bg-surface-soft/40 dark:bg-[#1f1d1a]">
            <input
              type="file"
              accept="application/pdf,.pdf"
              onChange={handleFileChange}
              className="hidden"
            />
            {selectedFile ? (
              <div className="flex items-center gap-2 text-ink dark:text-zinc-200 font-medium">
                <FileText className="w-5 h-5 text-primary" />
                <span className="truncate max-w-[240px]">{selectedFile.name}</span>
              </div>
            ) : (
              <div className="text-center space-y-1">
                <UploadCloud className="w-6 h-6 text-muted mx-auto" />
                <span className="font-medium text-ink dark:text-zinc-200">Chọn tệp PDF gốc</span>
                <p className="text-[10px] text-muted">Tối đa 50MB</p>
              </div>
            )}
          </label>

          {errorMsg && (
            <div className="flex items-center gap-1.5 p-2 rounded bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400">
              <AlertCircle className="w-3.5 h-3.5 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-hairline dark:border-[#2f2b26]">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 rounded-md hover:bg-black/5 text-muted"
            >
              Hủy
            </button>
            <button
              type="submit"
              disabled={isUploading || !selectedFile}
              className="px-4 py-1.5 rounded-md bg-primary hover:bg-primary/90 text-white font-medium disabled:opacity-50"
            >
              {isUploading ? "Đang phục hồi..." : "Bắt đầu khôi phục"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
