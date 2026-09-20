import { useState, useRef, useEffect, useMemo } from "react";
import {
  FileText,
  RotateCcw,
  Sparkles,
  ZoomIn,
  ZoomOut,
  ChevronLeft,
  ChevronRight,
  User,
  BrainCircuit,
  Copy,
  Check,
  ThumbsUp,
  ThumbsDown,
  Square,
} from "lucide-react";
import type { ChatMessage } from "@/types/dashboard";
import { useDashboardStore } from "../stores/useDashboardStore";
import { useWorkspaceStore } from "../stores/useWorkspaceStore";
import { computeBoundingBoxStyle } from "@/lib/bounding-box-scaler";
import { MathRenderer } from "@/components/shared/MathRenderer";
import { DocumentGroundedSummaryCard } from "./DocumentGroundedSummaryCard";
import { CitationBadge } from "./CitationBadge";
import { PresuppositionBanner } from "./PresuppositionBanner";
import { DashboardChatInputBox } from "./DashboardChatInputBox";
import type { DocumentSummaryResponse } from "@/features/documents/api/documentsApi";

interface DashboardWorkspaceProps {
  messages: ChatMessage[];
  inputText: string;
  onChangeText: (text: string) => void;
  onSend: (text?: string) => void;
  isGenerating: boolean;
  onStopGeneration: () => void;
  onUploadFile?: (file: File) => void;
  onResetChat: () => void;
  summary?: DocumentSummaryResponse | null;
}

const DEFAULT_GROUNDED_SUMMARY: DocumentSummaryResponse = {
  document_id: "doc-vaswani-2017",
  problem_statement: {
    text: "Các mô hình chuỗi tuần tự trước đây (RNN, LSTM, GRU) phụ thuộc chặt chẽ vào tính toán tuần tự dọc theo trục thời gian, cản trở việc song song hóa trong huấn luyện và gặp khó khăn khi mô hình hóa các phụ thuộc xa giữa các từ trong văn bản.",
    bounding_boxes: [[0.1, 0.15, 0.9, 0.35, 1]],
  },
  contributions: {
    text: "Đề xuất kiến trúc Transformer loại bỏ hoàn toàn mạng đệ quy, chỉ dựa trên cơ chế Self-Attention đa đầu (Multi-Head Attention) và hàm mã hóa vị trí Positional Encoding:\n$$PE_{(pos, 2i)} = \\sin\\left(\\frac{pos}{10000^{2i/d_{\\text{model}}}}\\right)$$\n$$PE_{(pos, 2i+1)} = \\cos\\left(\\frac{pos}{10000^{2i/d_{\\text{model}}}}\\right)$$\nĐạt BLEU score kỷ lục 28.4 trên tập dịch máy WMT 2014 English-to-German.",
    bounding_boxes: [[0.15, 0.62, 0.85, 0.88, 6]],
  },
  limitations: {
    text: "Độ phức tạp tính toán và tiêu thụ bộ nhớ của ma trận chú ý Self-Attention là $O(n^2)$ theo độ dài chuỗi $n$, khiến việc mở rộng sang các tài liệu cực dài đòi hỏi tài nguyên tính toán phần cứng lớn.",
    bounding_boxes: [[0.1, 0.7, 0.9, 0.95, 7]],
  },
};

/**
 * Formats assistant message markdown into paragraphs with KaTeX support
 */
function FormattedAssistantMessage({ content }: { content: string }) {
  const renderedContent = useMemo(() => {
    const blocks = content.split("$$");

    return blocks.map((chunk, idx) => {
      if (idx % 2 === 1) {
        return (
          <div
            key={idx}
            className="my-3 p-3.5 rounded-2xl bg-[#f7f4ee] dark:bg-[#21201d] border border-[#e5dfd4] dark:border-[#38332c] text-center overflow-x-auto text-coral-600 dark:text-amber-400 shadow-2xs"
          >
            <MathRenderer math={chunk.trim()} block />
          </div>
        );
      }

      const lines = chunk.split("\n").filter((l) => l.length > 0);
      return (
        <div key={idx} className="space-y-2.5">
          {lines.map((line, lIdx) => {
            const tokens = line.split(/(\*\*[^*]+\*\*|\$[^$]+\$)/g);

            return (
              <p key={lIdx} className="leading-relaxed text-xs sm:text-sm text-ink dark:text-zinc-200">
                {tokens.map((token, tIdx) => {
                  if (token.startsWith("**") && token.endsWith("**")) {
                    return (
                      <strong key={tIdx} className="font-semibold text-ink dark:text-zinc-100">
                        {token.slice(2, -2)}
                      </strong>
                    );
                  }
                  if (token.startsWith("$") && token.endsWith("$") && token.length > 2) {
                    return (
                      <MathRenderer
                        key={tIdx}
                        math={token.slice(1, -1)}
                        className="text-coral-600 dark:text-amber-400 px-0.5"
                      />
                    );
                  }
                  return token;
                })}
              </p>
            );
          })}
        </div>
      );
    });
  }, [content]);

  return <div className="space-y-3 font-anthropic-sans leading-relaxed">{renderedContent}</div>;
}

export function DashboardWorkspace({
  messages,
  inputText,
  onChangeText,
  onSend,
  isGenerating,
  onStopGeneration,
  onUploadFile,
  onResetChat,
  summary = DEFAULT_GROUNDED_SUMMARY,
}: DashboardWorkspaceProps) {
  const activeBbox = useDashboardStore((s) => s.activeBbox);
  const documentTitle = useWorkspaceStore((s) => s.documentTitle);

  const [zoomLevel, setZoomLevel] = useState<number>(100);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const totalPages = 8;
  const [copiedMsgId, setCopiedMsgId] = useState<string | null>(null);

  const bboxRef = useRef<HTMLDivElement | null>(null);
  const chatScrollRef = useRef<HTMLDivElement | null>(null);

  const [prevBbox, setPrevBbox] = useState(activeBbox);
  if (activeBbox !== prevBbox) {
    setPrevBbox(activeBbox);
    if (activeBbox && activeBbox[4]) {
      setCurrentPage(activeBbox[4]);
    }
  }

  // Scroll into view when activeBbox changes
  useEffect(() => {
    if (activeBbox && activeBbox[4] && bboxRef.current && typeof bboxRef.current.scrollIntoView === "function") {
      bboxRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [activeBbox]);

  // Auto-scroll chat stream
  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [messages, isGenerating]);

  const handleCopy = (msgId: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedMsgId(msgId);
    setTimeout(() => setCopiedMsgId(null), 2000);
  };

  const handleZoomIn = () => setZoomLevel((z) => Math.min(200, z + 15));
  const handleZoomOut = () => setZoomLevel((z) => Math.max(70, z - 15));
  const handleZoomReset = () => setZoomLevel(100);

  const displayTitle = documentTitle || "Attention Is All You Need";

  // Compute percentage box styling for active bounding box
  const bboxStyle = useMemo(() => {
    if (!activeBbox) return null;
    return computeBoundingBoxStyle(activeBbox);
  }, [activeBbox]);

  return (
    <div className="flex-1 flex flex-col lg:flex-row h-full overflow-hidden bg-[#faf9f5] dark:bg-[#181715] select-text">
      {/* ========================================================================= */}
      {/* 1. LEFT PANE: DYNAMIC PDF / DOCUMENT CANVAS                              */}
      {/* ========================================================================= */}
      <section className="w-full lg:w-1/2 flex flex-col h-1/2 lg:h-full border-b lg:border-b-0 lg:border-r border-[#e6dfd8] dark:border-[#2a2824] bg-[#faf8f4] dark:bg-[#1c1b18] overflow-hidden">
        {/* Document Header & Page Navigation Toolbar */}
        <header className="h-11 px-3.5 bg-[#f0ece3] dark:bg-[#201e1a] border-b border-[#e6dfd8] dark:border-[#2a2824] flex items-center justify-between select-none shrink-0">
          <div className="flex items-center gap-2 max-w-[60%]">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white dark:bg-[#252320] border border-[#d8d3c7] dark:border-[#38332c] text-xs font-sans font-medium text-ink dark:text-[#f3f2ef] shadow-2xs truncate">
              <FileText className="w-3.5 h-3.5 text-[#cc785c] shrink-0" />
              <span className="truncate" title={displayTitle}>
                {displayTitle}.pdf
              </span>
            </div>
            <span className="text-3xs font-mono text-ink-muted dark:text-zinc-400 hidden sm:inline">
              • Trang {currentPage} / {totalPages}
            </span>
          </div>

          {/* Zoom & Page Stepper */}
          <div className="flex items-center gap-1">
            <div className="flex items-center bg-white dark:bg-[#252320] border border-[#d8d3c7] dark:border-[#38332c] rounded-lg p-0.5 shadow-2xs">
              <button
                type="button"
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage <= 1}
                title="Trang trước"
                className="p-1 rounded hover:bg-[#f0ece3] dark:hover:bg-[#302c26] text-ink-muted dark:text-zinc-400 disabled:opacity-40 cursor-pointer"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
              </button>
              <span className="text-3xs font-mono px-1.5 text-ink dark:text-zinc-200">
                {currentPage}
              </span>
              <button
                type="button"
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage >= totalPages}
                title="Trang sau"
                className="p-1 rounded hover:bg-[#f0ece3] dark:hover:bg-[#302c26] text-ink-muted dark:text-zinc-400 disabled:opacity-40 cursor-pointer"
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="flex items-center bg-white dark:bg-[#252320] border border-[#d8d3c7] dark:border-[#38332c] rounded-lg p-0.5 shadow-2xs">
              <button
                type="button"
                onClick={handleZoomOut}
                title="Thu nhỏ"
                className="p-1 rounded hover:bg-[#f0ece3] dark:hover:bg-[#302c26] text-ink-muted dark:text-zinc-400 cursor-pointer"
              >
                <ZoomOut className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={handleZoomReset}
                title="Đặt lại 100%"
                className="text-3xs font-mono px-1.5 text-ink dark:text-zinc-200 hover:text-[#cc785c]"
              >
                {zoomLevel}%
              </button>
              <button
                type="button"
                onClick={handleZoomIn}
                title="Phóng to"
                className="p-1 rounded hover:bg-[#f0ece3] dark:hover:bg-[#302c26] text-ink-muted dark:text-zinc-400 cursor-pointer"
              >
                <ZoomIn className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </header>

        {/* Paper Canvas Scroll Area */}
        <div className="flex-1 overflow-auto p-4 sm:p-6 custom-scrollbar flex justify-center bg-[#eae5db]/60 dark:bg-[#141311]">
          <div
            style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: "top center" }}
            className="w-full max-w-2xl min-h-[780px] bg-white dark:bg-[#201e1a] rounded-xl border border-[#d8d3c7] dark:border-[#332e26] p-6 sm:p-8 shadow-sm transition-transform duration-150 relative text-[#141413] dark:text-[#ded8cc]"
          >
            {/* Dynamic Grounded Bounding Box Overlay */}
            {bboxStyle && activeBbox && (
              <div
                ref={bboxRef}
                data-testid="grounded-bbox-overlay"
                style={{
                  left: bboxStyle.left,
                  top: bboxStyle.top,
                  width: bboxStyle.width,
                  height: bboxStyle.height,
                }}
                className="absolute z-20 pointer-events-none rounded-md border-2 border-[#cc785c] bg-[#cc785c]/10 shadow-[0_0_12px_rgba(204,120,92,0.35)] animate-in fade-in zoom-in-95 duration-250"
              >
                <div className="absolute -top-3.5 left-2 px-1.5 py-0.5 rounded bg-[#cc785c] text-white text-[10px] font-mono font-medium tracking-wide flex items-center gap-1 shadow-xs">
                  <span>⚑</span>
                  <span>Dẫn chứng • Tr. {activeBbox[4]}</span>
                </div>
              </div>
            )}

            {/* Paper Sheet Content */}
            <article className="space-y-5 font-anthropic-sans leading-relaxed text-xs sm:text-sm">
              <header className="text-center pb-4 border-b border-[#e5e1d8] dark:border-[#353027]">
                <h2 className="font-serif font-bold text-lg sm:text-xl text-[#11100f] dark:text-[#fbf9f5] leading-snug">
                  {displayTitle}
                </h2>
                <p className="mt-1 text-2xs font-mono text-ink-muted dark:text-zinc-400">
                  Phân tích học thuật bảo chứng tọa độ Bounding Box
                </p>

                <div className="mt-3.5 p-3 rounded-lg bg-[#faf8f4] dark:bg-[#181715] border border-[#e5dfd4] dark:border-[#332e26] text-justify text-2xs leading-relaxed italic text-ink-muted dark:text-zinc-300">
                  <strong className="not-italic font-semibold text-ink dark:text-[#f3f2ef]">
                    Tóm tắt nghiên cứu (Abstract) —{" "}
                  </strong>
                  Các mô hình chuỗi tuần tự trước đây chủ yếu dựa vào mạng nơ-ron hồi quy RNN hoặc tích
                  chập trong cấu trúc encoder-decoder. Chúng tôi đề xuất mô hình Transformer chỉ dựa vào
                  cơ chế tự chú ý (Self-Attention) để nắm bắt quan hệ toàn cục giữa đầu vào và đầu ra,
                  cho phép song song hóa vượt trội trong quá trình huấn luyện và đạt đỉnh cao mới về độ
                  chính xác dịch máy.
                </div>
              </header>

              {/* 2-Column Scholarly Layout */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-justify text-2xs leading-relaxed">
                <section className="space-y-3">
                  <h3 className="font-serif font-bold text-xs text-ink dark:text-[#f3f2ef]">
                    1. Giới thiệu (Introduction)
                  </h3>
                  <p>
                    Mô hình hồi quy thường phân rã tính toán theo chuỗi thời gian của các ký hiệu đầu
                    vào và đầu ra. Việc căn chỉnh vị trí theo các bước tính toán tạo ra chuỗi trạng
                    thái ẩn $h_t$, vốn ngăn cản việc song song hóa trên các ví dụ huấn luyện.
                  </p>
                  <p>
                    Hạn chế này đặc biệt nghiêm trọng ở các độ dài chuỗi lớn, khi việc quản lý bộ nhớ
                    giới hạn khả năng xử lý song song các mẫu huấn luyện.
                  </p>
                </section>

                <section className="space-y-3">
                  <h3 className="font-serif font-bold text-xs text-ink dark:text-[#f3f2ef]">
                    2. Mã hóa vị trí (Positional Encoding)
                  </h3>
                  <p>
                    Do mô hình không chứa tính tuần tự hay tích chập, để mô hình sử dụng được thứ tự
                    của chuỗi, chúng ta phải đưa thông tin về vị trí tương đối hoặc tuyệt đối của các
                    từ trong chuỗi.
                  </p>
                  <div className="p-2.5 rounded-lg bg-[#f7f4ee] dark:bg-[#161513] border border-[#e5dfd4] dark:border-[#38332c] text-center my-1.5 overflow-x-auto text-[#cc785c]">
                    <MathRenderer
                      math="PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d_{\text{model}}}}\right)"
                      block
                    />
                  </div>
                  <p>
                    Trong đó $pos$ là vị trí và $i$ là chiều không gian biểu diễn vector.
                  </p>
                </section>
              </div>
            </article>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 2. RIGHT PANE: SOCRATIC COPILOT CHAT & GROUNDED SUMMARY                  */}
      {/* ========================================================================= */}
      <section className="w-full lg:w-1/2 flex flex-col h-1/2 lg:h-full bg-[#faf9f5] dark:bg-[#181715] overflow-hidden relative">
        {/* Right Pane Header */}
        <header className="h-11 px-4 bg-white/70 dark:bg-[#1c1b18]/70 backdrop-blur-sm border-b border-[#e6dfd8] dark:border-[#2a2824] flex items-center justify-between select-none shrink-0 z-10">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-[#cc785c]/15 text-[#cc785c] flex items-center justify-center">
              <Sparkles className="w-3.5 h-3.5" />
            </div>
            <div>
              <h2 className="font-serif font-bold text-xs sm:text-sm text-ink dark:text-[#f3f2ef] leading-tight">
                Socratic Copilot
              </h2>
              <span className="text-[10px] text-ink-muted dark:text-zinc-400 font-mono">
                Trợ lý phản biện &amp; bảo chứng
              </span>
            </div>
          </div>

          <button
            type="button"
            onClick={onResetChat}
            title="Làm mới hội thoại"
            className="p-1.5 rounded-lg hover:bg-[#f0ece3] dark:hover:bg-[#282622] text-ink-muted dark:text-zinc-400 hover:text-ink dark:hover:text-zinc-100 transition-colors cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </header>

        {/* Scrollable Stream (Summary Card + Messages) */}
        <div
          ref={chatScrollRef}
          className="flex-1 overflow-y-auto px-4 sm:px-6 py-5 space-y-6 custom-scrollbar"
        >
          {/* Auto-Triggered Grounded 3-Point Summary Card */}
          {summary && (
            <div className="animate-in fade-in slide-in-from-top-3 duration-300">
              <DocumentGroundedSummaryCard summary={summary} paperTitle={displayTitle} />
            </div>
          )}

          {/* Chat Messages */}
          {messages.map((message) => {
            const isUser = message.role === "user";

            if (isUser) {
              return (
                <div key={message.id} className="flex justify-end">
                  <div className="max-w-xl px-4 py-3 rounded-2xl rounded-tr-xs bg-white dark:bg-[#252320] border border-[#e8e4dc] dark:border-[#38332c] text-ink dark:text-zinc-100 text-xs sm:text-sm font-anthropic-sans shadow-xs">
                    <div className="flex items-center gap-1.5 text-3xs font-mono text-ink-muted dark:text-zinc-400 mb-1">
                      <User className="w-3 h-3 text-[#cc785c]" />
                      <span className="font-medium">Học giả</span>
                    </div>
                    <div className="leading-relaxed whitespace-pre-wrap">{message.content}</div>
                  </div>
                </div>
              );
            }

            return (
              <div key={message.id} className="flex gap-3 max-w-2xl">
                {/* Socratic Avatar Emblem */}
                <div className="w-7 h-7 rounded-xl bg-[#cc785c]/10 border border-[#cc785c]/20 text-[#cc785c] flex items-center justify-center shrink-0 mt-1 shadow-2xs">
                  <Sparkles className="w-3.5 h-3.5" />
                </div>

                {/* Assistant Message Body */}
                <div className="flex-1 space-y-2.5 min-w-0">
                  <div className="text-3xs font-mono font-medium text-ink-muted dark:text-zinc-500 flex items-center gap-2">
                    <span className="font-semibold text-ink dark:text-zinc-300 font-anthropic-sans">
                      Socratic
                    </span>
                    {message.is_streaming && (
                      <span className="inline-flex items-center gap-1 text-[#cc785c] animate-pulse">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#cc785c]" />
                        <span>Đang suy luận...</span>
                      </span>
                    )}
                  </div>

                  {/* Collapsible Reasoning */}
                  {message.thought && (
                    <details className="group p-2 rounded-xl bg-[#f4efe6]/80 dark:bg-[#211f1c] border border-[#e5dfd4] dark:border-[#332f28] text-2xs font-mono text-ink-muted dark:text-zinc-400">
                      <summary className="cursor-pointer font-medium select-none flex items-center gap-1.5 text-ink dark:text-zinc-300 hover:text-[#cc785c] transition-colors">
                        <BrainCircuit className="w-3.5 h-3.5 text-[#cc785c]" />
                        <span>Suy luận bảo chứng</span>
                      </summary>
                      <div className="mt-2 pt-2 border-t border-hairline/60 dark:border-zinc-800 text-3xs font-mono leading-relaxed whitespace-pre-wrap">
                        {message.thought}
                      </div>
                    </details>
                  )}

                  {/* Socratic Presupposition Alert */}
                  {message.presupposition_alert && (
                    <PresuppositionBanner alert={message.presupposition_alert} />
                  )}

                  {/* Formatted Markdown & KaTeX */}
                  <FormattedAssistantMessage content={message.content} />

                  {/* Interactive Citations */}
                  {message.citations && message.citations.length > 0 && (
                    <div className="pt-1.5 flex flex-wrap items-center gap-1.5">
                      {message.citations.map((cite, cIdx) => (
                        <CitationBadge key={cIdx} citation={cite} />
                      ))}
                    </div>
                  )}

                  {/* Feedback Toolbar */}
                  {!message.is_streaming && (
                    <div className="flex items-center gap-1 pt-1 text-ink-muted dark:text-zinc-500 text-xs">
                      <button
                        type="button"
                        onClick={() => handleCopy(message.id, message.content)}
                        title="Sao chép câu trả lời"
                        className="p-1 rounded-lg hover:bg-white dark:hover:bg-[#252320] border border-transparent hover:border-[#e5dfd4] dark:hover:border-[#38332c] hover:text-ink dark:hover:text-zinc-200 transition-all cursor-pointer"
                      >
                        {copiedMsgId === message.id ? (
                          <Check className="w-3 h-3 text-emerald-500" />
                        ) : (
                          <Copy className="w-3 h-3" />
                        )}
                      </button>
                      <button
                        type="button"
                        title="Hữu ích"
                        className="p-1 rounded-lg hover:bg-white dark:hover:bg-[#252320] border border-transparent hover:border-[#e5dfd4] dark:hover:border-[#38332c] hover:text-ink dark:hover:text-zinc-200 transition-all cursor-pointer"
                      >
                        <ThumbsUp className="w-3 h-3" />
                      </button>
                      <button
                        type="button"
                        title="Chưa chính xác"
                        className="p-1 rounded-lg hover:bg-white dark:hover:bg-[#252320] border border-transparent hover:border-[#e5dfd4] dark:hover:border-[#38332c] hover:text-ink dark:hover:text-zinc-200 transition-all cursor-pointer"
                      >
                        <ThumbsDown className="w-3 h-3" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Bottom-Docked Input Bar */}
        <div className="shrink-0 pb-4 pt-2 px-3 bg-gradient-to-t from-[#faf9f5] via-[#faf9f5]/90 to-transparent dark:from-[#181715] dark:via-[#181715]/90 z-10">
          {isGenerating && (
            <div className="flex justify-center mb-2">
              <button
                type="button"
                onClick={onStopGeneration}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white dark:bg-[#252320] border border-[#e5dfd4] dark:border-zinc-700/60 text-ink dark:text-zinc-200 text-xs font-sans shadow-xs hover:bg-[#f4efe6] dark:hover:bg-[#2e2a25] transition-colors cursor-pointer"
              >
                <Square className="w-3 h-3 fill-current text-[#cc785c]" />
                <span>Dừng suy luận</span>
              </button>
            </div>
          )}

          <DashboardChatInputBox
            inputText={inputText}
            onChangeText={onChangeText}
            onSend={onSend}
            isGenerating={isGenerating}
            onUploadFile={onUploadFile}
          />
        </div>
      </section>
    </div>
  );
}
