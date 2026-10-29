import { useState, useRef, useEffect } from "react";
import { BookmarkPlus, Copy, Check, MessageSquarePlus } from "lucide-react";
import type { BoundingBox } from "@/types/api";

export interface ScholarSelectionMenuProps {
  selectedText: string;
  coord: { x: number; y: number } | null;
  pageNumber: number;
  bbox?: BoundingBox | null;
  documentTitle?: string;
  onAddToNote: (selectedText: string, pageNumber: number, bbox?: BoundingBox | null) => void;
  onAddToChat?: (selectedText: string, pageNumber: number, bbox?: BoundingBox | null) => void;
  onAskChat?: (prompt: string) => void;
  onClearSelection: () => void;
}

export function ScholarSelectionMenu({
  selectedText,
  coord,
  pageNumber,
  bbox,
  documentTitle,
  onAddToNote,
  onAddToChat,
  onAskChat,
  onClearSelection,
}: ScholarSelectionMenuProps) {
  const [copied, setCopied] = useState(false);
  const [copiedRaw, setCopiedRaw] = useState(false);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  if (!selectedText || !coord) return null;

  const copyToClipboard = async (text: string): Promise<boolean> => {
    try {
      if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
        await navigator.clipboard.writeText(text);
        return true;
      }
      throw new Error("Clipboard API unavailable");
    } catch {
      try {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.left = "-9999px";
        textArea.style.top = "-9999px";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        const success = document.execCommand("copy");
        document.body.removeChild(textArea);
        return success;
      } catch (fallbackErr) {
        console.warn("Clipboard copy failed:", fallbackErr);
        return false;
      }
    }
  };

  const handleCopyRaw = async () => {
    const success = await copyToClipboard(selectedText);
    if (success) {
      setCopiedRaw(true);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      timeoutRef.current = setTimeout(() => {
        setCopiedRaw(false);
        onClearSelection();
      }, 1500);
    }
  };

  const handleCopyCitation = async () => {
    const citation = `"${selectedText}"\n— [${documentTitle || "Tài liệu khoa học"}, Trang ${pageNumber}]`;
    const success = await copyToClipboard(citation);
    if (success) {
      setCopied(true);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      timeoutRef.current = setTimeout(() => {
        setCopied(false);
        onClearSelection();
      }, 1500);
    }
  };

  const handleAddToChatAction = () => {
    if (onAddToChat) {
      onAddToChat(selectedText, pageNumber, bbox ?? null);
      onClearSelection();
    } else if (onAskChat) {
      const prompt = `Hãy giải thích chi tiết ý nghĩa và luận điểm trong đoạn trích sau (Trang ${pageNumber}):\n\n"${selectedText}"`;
      onAskChat(prompt);
      onClearSelection();
    }
  };

  const handleSaveToNote = () => {
    onAddToNote(selectedText, pageNumber, bbox ?? null);
    onClearSelection();
  };

  return (
    <div
      data-testid="scholar-selection-menu"
      style={{ left: coord.x, top: coord.y }}
      className="absolute z-40 -translate-x-1/2 -translate-y-full mb-2 flex items-center shadow-xl rounded-lg bg-[#1a1917] text-zinc-100 p-1 gap-1 text-xs border border-white/10 backdrop-blur-md animate-in fade-in zoom-in-95 duration-150 select-none"
    >
      {/* 1. Add to Chat (Zero-Click Context Chip) */}
      {(onAddToChat || onAskChat) && (
        <button
          type="button"
          data-testid="selection-add-chat-btn"
          onClick={handleAddToChatAction}
          title="Đưa đoạn trích vào khung chat với Context Chip (Zero-Click Focus)"
          className="flex items-center gap-1.5 px-2.5 py-1 rounded hover:bg-white/15 text-zinc-200 hover:text-white transition-colors cursor-pointer"
        >
          <MessageSquarePlus className="w-3.5 h-3.5 text-coral-400" />
          <span className="font-medium">Đưa vào Chat</span>
        </button>
      )}

      {(onAddToChat || onAskChat) && <div className="w-[1px] h-3.5 bg-white/15 my-auto" />}

      {/* 2. Add to Note */}
      <button
        type="button"
        data-testid="selection-add-note-btn"
        onClick={handleSaveToNote}
        title="Lưu đoạn trích này vào Sổ tay nghiên cứu kèm số trang và tọa độ Bounding Box"
        className="flex items-center gap-1.5 px-2.5 py-1 rounded hover:bg-white/15 text-zinc-200 hover:text-white transition-colors cursor-pointer"
      >
        <BookmarkPlus className="w-3.5 h-3.5 text-amber-400" />
        <span className="font-medium">Vào sổ tay</span>
      </button>

      <div className="w-[1px] h-3.5 bg-white/15 my-auto" />

      {/* 3. Direct clean raw copy */}
      <button
        type="button"
        data-testid="selection-copy-raw-btn"
        onClick={handleCopyRaw}
        title="Sao chép nguyên bản đoạn trích"
        className="flex items-center gap-1.5 px-2 py-1 rounded hover:bg-white/15 text-zinc-200 hover:text-white transition-colors cursor-pointer"
      >
        {copiedRaw ? (
          <>
            <Check className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-emerald-400 font-medium">Đã chép</span>
          </>
        ) : (
          <>
            <Copy className="w-3.5 h-3.5 text-zinc-400" />
            <span className="font-medium">Sao chép</span>
          </>
        )}
      </button>

      <div className="w-[1px] h-3.5 bg-white/15 my-auto" />

      {/* 4. Copy with citation */}
      <button
        type="button"
        data-testid="selection-copy-citation-btn"
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
