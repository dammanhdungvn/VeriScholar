import { useState } from "react";
import { BookmarkPlus, Copy, Check, Sparkles } from "lucide-react";

interface ScholarSelectionMenuProps {
  selectedText: string;
  coord: { x: number; y: number } | null;
  pageNumber: number;
  documentTitle?: string;
  onAddToNote: (selectedText: string, pageNumber: number) => void;
  onAskChat?: (prompt: string) => void;
  onClearSelection: () => void;
}

export function ScholarSelectionMenu({
  selectedText,
  coord,
  pageNumber,
  documentTitle,
  onAddToNote,
  onAskChat,
  onClearSelection,
}: ScholarSelectionMenuProps) {
  const [copied, setCopied] = useState(false);

  if (!selectedText || !coord) return null;

  const handleCopyCitation = async () => {
    const citation = `"${selectedText}"\n— [${documentTitle || "Tài liệu khoa học"}, Trang ${pageNumber}]`;
    await navigator.clipboard.writeText(citation);
    setCopied(true);
    setTimeout(() => {
      setCopied(false);
      onClearSelection();
    }, 1500);
  };

  const handleAskSocratic = () => {
    if (onAskChat) {
      const prompt = `Hãy giải thích chi tiết ý nghĩa và luận điểm trong đoạn trích sau (Trang ${pageNumber}):\n\n"${selectedText}"`;
      onAskChat(prompt);
      onClearSelection();
    }
  };

  const handleSaveToNote = () => {
    onAddToNote(selectedText, pageNumber);
    onClearSelection();
  };

  return (
    <div
      style={{ left: coord.x, top: coord.y }}
      className="absolute z-40 -translate-x-1/2 -translate-y-full mb-2 flex items-center shadow-xl rounded-lg bg-[#1a1917] text-zinc-100 p-1 gap-1 text-xs border border-white/10 backdrop-blur-md animate-in fade-in zoom-in-95 duration-150 select-none"
    >
      {/* 1. Add to Note */}
      <button
        type="button"
        onClick={handleSaveToNote}
        title="Thêm đoạn trích này vào Sổ tay nghiên cứu"
        className="flex items-center gap-1.5 px-2.5 py-1 rounded hover:bg-white/15 text-zinc-200 hover:text-white transition-colors cursor-pointer"
      >
        <BookmarkPlus className="w-3.5 h-3.5 text-coral-400" />
        <span className="font-medium">Vào sổ tay</span>
      </button>

      <div className="w-[1px] h-3.5 bg-white/15 my-auto" />

      {/* 2. Ask Socratic Copilot */}
      {onAskChat && (
        <button
          type="button"
          onClick={handleAskSocratic}
          title="Hỏi trợ lý Socratic về đoạn văn này"
          className="flex items-center gap-1.5 px-2.5 py-1 rounded hover:bg-white/15 text-zinc-200 hover:text-white transition-colors cursor-pointer"
        >
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          <span className="font-medium">Hỏi Socratic</span>
        </button>
      )}

      <div className="w-[1px] h-3.5 bg-white/15 my-auto" />

      {/* 3. Copy with citation */}
      <button
        type="button"
        onClick={handleCopyCitation}
        title="Sao chép kèm trích dẫn chuẩn học thuật"
        className="flex items-center gap-1.5 px-2 py-1 rounded hover:bg-white/15 text-zinc-200 hover:text-white transition-colors cursor-pointer"
      >
        {copied ? (
          <>
            <Check className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-emerald-400 font-medium">Đã chép</span>
          </>
        ) : (
          <>
            <Copy className="w-3.5 h-3.5 text-zinc-400" />
            <span className="font-medium">Trích dẫn</span>
          </>
        )}
      </button>
    </div>
  );
}
