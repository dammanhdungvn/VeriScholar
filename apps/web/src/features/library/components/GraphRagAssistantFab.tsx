import { useState } from "react";
import {
  Sparkles,
  X,
  Send,
  Loader2,
  ChevronDown,
} from "lucide-react";
import { libraryApi } from "../api/libraryApi";
import type { GraphQueryMode, GraphQueryResponseData } from "../types";
import { cn } from "@/lib/utils";

export interface GraphRagAssistantFabProps {
  folderId?: string | null;
  className?: string;
}

const SUGGESTIONS = [
  "So sánh các phương pháp và mô hình trong thư viện",
  "Tổng hợp các kết quả thực nghiệm và chỉ số",
  "Những đóng góp khoa học chính của các tài liệu",
];

export function GraphRagAssistantFab({ folderId, className }: GraphRagAssistantFabProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<GraphQueryMode>("auto");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<GraphQueryResponseData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e?: React.FormEvent, customQuery?: string) => {
    if (e) e.preventDefault();
    const effectiveQuery = (customQuery || query).trim();
    if (!effectiveQuery || isLoading) return;

    setIsLoading(true);
    setError(null);
    try {
      const res = await libraryApi.queryGraph({
        query: effectiveQuery,
        mode,
        folder_id: folderId || null,
        top_k: 5,
      });
      setResult(res);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Truy vấn GraphRAG thất bại. Vui lòng thử lại.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Floating Action Bubble (FAB) */}
      {!isOpen && (
        <button
          type="button"
          onClick={() => setIsOpen(true)}
          aria-label="Trợ lý GraphRAG"
          className={cn(
            "fixed bottom-6 right-6 z-40 flex items-center gap-2 px-4 py-3 rounded-full bg-[#c15f3e] hover:bg-[#b05334] text-white shadow-xl hover:shadow-2xl transition-all duration-200 cursor-pointer group hover:scale-105 active:scale-95",
            className
          )}
        >
          <Sparkles className="w-4 h-4 fill-white/20 animate-pulse" />
          <span className="text-xs font-semibold tracking-wide">Trợ lý GraphRAG</span>
        </button>
      )}

      {/* Slide-over Drawer / Modal Chat Window */}
      {isOpen && (
        <div
          role="dialog"
          aria-label="Khung chat trợ lý GraphRAG"
          className="fixed bottom-6 right-6 z-50 w-full max-w-md sm:w-[440px] h-[580px] bg-white/95 dark:bg-[#1c1b18]/95 backdrop-blur-md rounded-2xl border border-[#e8e4dc] dark:border-[#2e2b26] shadow-2xl flex flex-col overflow-hidden animate-in slide-in-from-bottom-5 duration-200"
        >
          {/* Header */}
          <div className="h-14 px-5 border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#fdfcf9] dark:bg-[#1e1d1a] flex items-center justify-between shrink-0">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <h3 className="font-serif font-semibold text-xs text-ink dark:text-zinc-100">
                  Hỏi đáp Đồ thị Tri thức GraphRAG
                </h3>
                <p className="text-[10px] text-muted">
                  {folderId ? "Phạm vi: Thư mục hiện tại" : "Phạm vi: Toàn bộ thư viện"}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {/* Mode Selector */}
              <div className="relative">
                <select
                  value={mode}
                  onChange={(e) => setMode(e.target.value as GraphQueryMode)}
                  className="h-7 text-[10px] pl-2 pr-6 rounded-md bg-surface dark:bg-[#252320] border border-border text-ink dark:text-zinc-200 outline-none cursor-pointer appearance-none"
                >
                  <option value="auto">Tự động (Auto)</option>
                  <option value="hybrid">Hỗn hợp (Hybrid)</option>
                  <option value="local">Cục bộ (Local CTE)</option>
                  <option value="global">Toàn cục (Global)</option>
                </select>
                <ChevronDown className="w-3 h-3 absolute right-1.5 top-1/2 -translate-y-1/2 text-muted pointer-events-none" />
              </div>

              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="p-1 rounded-md hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Chat Messages Body */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
            {/* Introductory guide */}
            {!result && !isLoading && (
              <div className="p-3.5 rounded-xl bg-surface/80 dark:bg-[#252320]/80 border border-border/60 space-y-2">
                <p className="text-[11px] text-muted leading-relaxed">
                  Trợ lý GraphRAG tra cứu qua đồ thị tri thức cá nhân, tổng hợp đối chiếu từ nhiều bài báo khoa học đã lưu trữ trong thư viện.
                </p>
                <span className="text-[10px] font-medium text-ink dark:text-zinc-300 block">
                  Gợi ý câu hỏi nhanh:
                </span>
                <div className="flex flex-col gap-1.5">
                  {SUGGESTIONS.map((s, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => {
                        setQuery(s);
                        handleSubmit(undefined, s);
                      }}
                      className="text-left text-[11px] p-2 rounded-lg bg-white dark:bg-[#1a1917] border border-border/80 hover:border-primary/50 text-ink-muted hover:text-ink transition-colors cursor-pointer"
                    >
                      • {s}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Loading state */}
            {isLoading && (
              <div className="p-6 flex flex-col items-center justify-center text-center text-muted space-y-2">
                <Loader2 className="w-6 h-6 animate-spin text-primary" />
                <p className="text-xs font-medium">Đang đối chiếu đồ thị và tổng hợp tri thức...</p>
                <span className="text-[10px] text-muted/80">Quét CTE mỏ neo và tóm tắt cộng đồng</span>
              </div>
            )}

            {/* Error display */}
            {error && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-xs">
                {error}
              </div>
            )}

            {/* Result display */}
            {result && !isLoading && (
              <div className="space-y-3">
                <div className="p-3.5 rounded-xl bg-surface/90 dark:bg-[#252320]/90 border border-border/80 space-y-2">
                  <div className="flex items-center justify-between text-[10px] text-muted">
                    <span className="font-mono uppercase tracking-wider font-semibold text-primary">
                      Chế độ: {result.mode_used}
                    </span>
                    {result.meta?.matched_entities && (
                      <span>{result.meta.matched_entities} thực thể khớp</span>
                    )}
                  </div>
                  <div className="text-xs text-ink dark:text-zinc-100 leading-relaxed whitespace-pre-wrap font-sans">
                    {result.answer}
                  </div>
                </div>

                {/* Evidence Chunks Grounding */}
                {result.evidence_chunks && result.evidence_chunks.length > 0 && (
                  <div className="space-y-1.5">
                    <span className="text-[10px] font-semibold text-muted uppercase tracking-wider block">
                      Căn cứ trích xuất ({result.evidence_chunks.length}):
                    </span>
                    {result.evidence_chunks.slice(0, 3).map((chunk, idx) => (
                      <div
                        key={idx}
                        className="p-2 rounded-lg bg-black/5 dark:bg-white/5 border border-border/40 text-[10px] text-muted leading-relaxed"
                      >
                        <span className="font-mono text-primary mr-1">Trang {chunk.page_number}:</span>
                        {chunk.chunk_text.slice(0, 160)}...
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Query Input Footer */}
          <form
            onSubmit={(e) => handleSubmit(e)}
            className="p-3 border-t border-[#e8e4dc] dark:border-[#2e2b26] bg-[#fdfcf9] dark:bg-[#1e1d1a] flex items-center gap-2 shrink-0"
          >
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Đặt câu hỏi đối chiếu, tổng hợp tri thức..."
              disabled={isLoading}
              className="flex-1 h-9 px-3 rounded-lg bg-white dark:bg-[#252320] border border-[#e2dcd2] dark:border-[#322f2a] text-xs text-ink dark:text-zinc-100 placeholder:text-muted outline-none focus:border-primary transition-colors disabled:opacity-50"
            />
            <button
              type="submit"
              data-testid="graphrag-submit-btn"
              disabled={!query.trim() || isLoading}
              className="w-9 h-9 rounded-lg bg-[#c15f3e] hover:bg-[#b05334] text-white flex items-center justify-center shrink-0 disabled:opacity-40 transition-colors cursor-pointer"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </form>
        </div>
      )}
    </>
  );
}
