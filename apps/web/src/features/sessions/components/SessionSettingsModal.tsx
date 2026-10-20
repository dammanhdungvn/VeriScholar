import { useState } from "react";
import { X, Settings, Trash2, Check } from "lucide-react";

interface SessionSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  sessionId: string;
  currentTitle: string;
  version: number;
  documentCount: number;
  createdAt: string;
  onUpdateTitle: (newTitle: string, version: number) => Promise<void>;
  onDeleteSession: () => Promise<void>;
}

export function SessionSettingsModal({
  isOpen,
  onClose,
  sessionId,
  currentTitle,
  version,
  documentCount,
  createdAt,
  onUpdateTitle,
  onDeleteSession,
}: SessionSettingsModalProps) {
  const [title, setTitle] = useState(currentTitle);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  if (!isOpen) return null;

  const handleSaveTitle = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || title === currentTitle) return;
    setIsSaving(true);
    try {
      await onUpdateTitle(title.trim(), version);
      onClose();
    } catch (err) {
      console.warn("Failed to update session title:", err);
      onClose();
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm("Bạn có chắc chắn muốn xóa phiên nghiên cứu này? Thao tác này không thể hoàn tác.")) {
      return;
    }
    setIsDeleting(true);
    try {
      await onDeleteSession();
      onClose();
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Cấu hình phiên nghiên cứu"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in duration-150"
    >
      <div className="w-full max-w-md bg-canvas dark:bg-[#1a1917] rounded-lg shadow-2xl border border-hairline dark:border-[#2f2b26] flex flex-col overflow-hidden text-xs">
        <div className="h-11 px-4 border-b border-hairline dark:border-[#2f2b26] flex items-center justify-between">
          <div className="flex items-center gap-2 font-serif font-semibold text-xs text-ink dark:text-zinc-100">
            <Settings className="w-4 h-4 text-primary" />
            <span>Cài đặt phiên nghiên cứu</span>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Đóng cài đặt"
            className="p-1 rounded hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSaveTitle} className="p-4 space-y-4">
          <div className="space-y-1">
            <label className="block text-[11px] font-medium text-ink dark:text-zinc-200">
              Tiêu đề phiên nghiên cứu
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Nhập tên phiên..."
              className="w-full px-3 py-2 rounded-md bg-canvas dark:bg-[#141311] border border-hairline focus:border-primary outline-none font-sans text-xs"
            />
          </div>

          <div className="p-3 rounded-md bg-surface-soft dark:bg-[#201e1b] border border-hairline dark:border-[#2d2924] space-y-1.5 font-mono text-[11px] text-muted">
            <div className="flex justify-between">
              <span>Mã phiên:</span>
              <span className="text-ink dark:text-zinc-300">{sessionId.slice(0, 8)}...</span>
            </div>
            <div className="flex justify-between">
              <span>Phiên bản:</span>
              <span className="text-ink dark:text-zinc-300">v{version}</span>
            </div>
            <div className="flex justify-between">
              <span>Tài liệu:</span>
              <span className="text-ink dark:text-zinc-300">{documentCount} / 5</span>
            </div>
            <div className="flex justify-between">
              <span>Khởi tạo:</span>
              <span className="text-ink dark:text-zinc-300">
                {new Date(createdAt).toLocaleDateString()}
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-hairline dark:border-[#2f2b26]">
            <button
              type="button"
              onClick={handleDelete}
              disabled={isDeleting}
              className="flex items-center gap-1 text-rose-500 hover:text-rose-600 font-medium disabled:opacity-50"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Xóa phiên</span>
            </button>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onClose}
                className="px-3 py-1.5 rounded-md hover:bg-black/5 text-muted"
              >
                Hủy
              </button>
              <button
                type="submit"
                disabled={isSaving || !title.trim() || title === currentTitle}
                className="px-3.5 py-1.5 rounded-md bg-primary hover:bg-primary/90 text-white font-medium flex items-center gap-1 disabled:opacity-50"
              >
                <Check className="w-3 h-3" />
                <span>Lưu thay đổi</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
