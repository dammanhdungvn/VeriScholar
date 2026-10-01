import { useState } from "react";
import { X, Sparkles, BookOpen, Layers, Target, HelpCircle } from "lucide-react";
import type { NoteSynthesisMode, SynthesizeNotesRequest } from "@/types/note";
import { cn } from "@/lib/utils";

interface NoteSynthesisModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedNoteIds: string[];
  totalNotesCount: number;
  onSynthesize: (request: SynthesizeNotesRequest) => Promise<void>;
  isLoading?: boolean;
}

const MODES: {
  id: NoteSynthesisMode;
  label: string;
  desc: string;
  icon: typeof BookOpen;
}[] = [
  {
    id: "concept_lesson",
    label: "Bài học khái niệm",
    desc: "Đúc kết các định nghĩa, công thức toán và giải thích cơ chế hoạt động cốt lõi.",
    icon: BookOpen,
  },
  {
    id: "literature_review",
    label: "Tổng quan tài liệu",
    desc: "Xâu chuỗi các luận điểm thành một bức tranh tổng thể so sánh các phương pháp.",
    icon: Layers,
  },
  {
    id: "research_gap",
    label: "Khoảng trống nghiên cứu",
    desc: "Phân tích các giới hạn, giả định chưa kiểm chứng và gợi mở hướng đi mới.",
    icon: Target,
  },
  {
    id: "active_recall_quiz",
    label: "Tự vấn & Flashcard",
    desc: "Tạo bộ câu hỏi phản biện Socratic và thẻ ghi nhớ để củng cố kiến thức sâu.",
    icon: HelpCircle,
  },
];

export function NoteSynthesisModal({
  isOpen,
  onClose,
  selectedNoteIds,
  totalNotesCount,
  onSynthesize,
  isLoading = false,
}: NoteSynthesisModalProps) {
  const [selectedMode, setSelectedMode] = useState<NoteSynthesisMode>("concept_lesson");
  const [targetTitle, setTargetTitle] = useState("");
  const [language, setLanguage] = useState("vi");

  if (!isOpen) return null;

  const notesToUseCount = selectedNoteIds.length > 0 ? selectedNoteIds.length : totalNotesCount;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSynthesize({
      note_ids: selectedNoteIds,
      mode: selectedMode,
      language,
      target_title: targetTitle.trim() || undefined,
    });
    onClose();
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="AI Tổng hợp ghi chú thành bài học"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in duration-150"
    >
      <div className="w-full max-w-lg bg-canvas dark:bg-[#1a1917] rounded-lg shadow-2xl border border-hairline dark:border-[#2f2b26] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="h-12 px-5 border-b border-hairline dark:border-[#2f2b26] flex items-center justify-between">
          <div className="flex items-center gap-2 font-serif font-semibold text-sm text-ink dark:text-zinc-100">
            <Sparkles className="w-4 h-4 text-primary" />
            <span>AI Tổng Hợp Tri Thức ({notesToUseCount} ghi chú)</span>
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

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4 text-xs">
          {/* Mode Selector */}
          <div className="space-y-2">
            <label className="block text-[11px] font-sans font-medium text-ink dark:text-zinc-200">
              Mục tiêu đúc kết tri thức
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {MODES.map((mode) => {
                const Icon = mode.icon;
                const isSelected = selectedMode === mode.id;

                return (
                  <div
                    key={mode.id}
                    onClick={() => setSelectedMode(mode.id)}
                    className={cn(
                      "p-3 rounded-md border cursor-pointer transition-all duration-150 flex flex-col justify-between",
                      isSelected
                        ? "bg-surface-cream-strong dark:bg-[#282521] border-primary text-ink dark:text-zinc-100 shadow-2xs"
                        : "bg-surface-soft/60 dark:bg-[#1f1d1a] border-hairline dark:border-[#2e2b26] hover:bg-surface-cream-strong/50 text-muted hover:text-ink"
                    )}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <Icon className={cn("w-4 h-4", isSelected ? "text-primary" : "text-muted")} />
                      <span className="font-sans font-semibold text-xs">{mode.label}</span>
                    </div>
                    <p className="text-[11px] leading-relaxed text-muted line-clamp-2">
                      {mode.desc}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Title Input */}
          <div className="space-y-1">
            <label className="block text-[11px] font-sans font-medium text-ink dark:text-zinc-200">
              Tiêu đề bài đúc kết (Tùy chọn)
            </label>
            <input
              type="text"
              value={targetTitle}
              onChange={(e) => setTargetTitle(e.target.value)}
              placeholder="ví dụ: Bản Đúc Kết Cơ Chế Self-Attention..."
              className="w-full px-3 py-2 rounded-md bg-canvas dark:bg-[#141311] border border-hairline focus:border-primary outline-none font-sans text-xs"
            />
          </div>

          {/* Language Selector */}
          <div className="space-y-1">
            <label className="block text-[11px] font-sans font-medium text-ink dark:text-zinc-200">
              Ngôn ngữ xuất bản
            </label>
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-1.5 cursor-pointer">
                <input
                  type="radio"
                  name="language"
                  value="vi"
                  checked={language === "vi"}
                  onChange={() => setLanguage("vi")}
                  className="accent-primary"
                />
                <span className="font-sans">Tiếng Việt</span>
              </label>
              <label className="flex items-center gap-1.5 cursor-pointer">
                <input
                  type="radio"
                  name="language"
                  value="en"
                  checked={language === "en"}
                  onChange={() => setLanguage("en")}
                  className="accent-primary"
                />
                <span className="font-sans">English</span>
              </label>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-2 pt-3 border-t border-hairline dark:border-[#2f2b26]">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-1.5 rounded-md hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink font-medium"
            >
              Hủy
            </button>
            <button
              type="submit"
              disabled={isLoading || notesToUseCount === 0}
              className="px-4 py-2 rounded-md bg-primary hover:bg-primary/90 text-white font-medium flex items-center gap-1.5 shadow-xs disabled:opacity-50"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{isLoading ? "Đang tổng hợp..." : "Bắt đầu tổng hợp"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
