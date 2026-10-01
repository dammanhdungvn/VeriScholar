import { useState } from "react";
import { X, Sliders, Table, RefreshCw, CheckCircle2, AlertCircle } from "lucide-react";
import { documentsApi } from "../api/documentsApi";
import { useQueryClient } from "@tanstack/react-query";
import { DOCUMENT_QUERY_KEYS } from "../hooks/useDocumentQueries";

interface ParseConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentId: string;
  documentTitle?: string;
  onParseSuccess?: () => void;
}

interface PresetOption {
  name: string;
  chunkSize: number;
  chunkOverlap: number;
  description: string;
}

const PRESETS: PresetOption[] = [
  {
    name: "Chuẩn RAG",
    chunkSize: 512,
    chunkOverlap: 50,
    description: "Cân bằng tối ưu giữa độ chính xác và ngữ cảnh học thuật.",
  },
  {
    name: "Chi tiết (Fine-grained)",
    chunkSize: 256,
    chunkOverlap: 25,
    description: "Phù hợp bài báo công thức toán dày đặc và trích dẫn vi mô.",
  },
  {
    name: "Ngữ cảnh rộng (Dense)",
    chunkSize: 1024,
    chunkOverlap: 100,
    description: "Tối ưu cho tổng quan tài liệu và phân tích liên chương.",
  },
];

export function ParseConfigModal({
  isOpen,
  onClose,
  documentId,
  documentTitle,
  onParseSuccess,
}: ParseConfigModalProps) {
  const queryClient = useQueryClient();
  const [chunkSize, setChunkSize] = useState<number>(512);
  const [chunkOverlap, setChunkOverlap] = useState<number>(50);
  const [extractTables, setExtractTables] = useState<boolean>(true);
  const [forceReparse, setForceReparse] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleApplyPreset = (preset: PresetOption) => {
    setChunkSize(preset.chunkSize);
    setChunkOverlap(preset.chunkOverlap);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!documentId) return;

    if (chunkSize < 100 || chunkSize > 2048) {
      setErrorMsg("Kích thước phân đoạn (chunk_size) phải nằm trong khoảng 100 - 2048 tokens.");
      return;
    }
    if (chunkOverlap < 0 || chunkOverlap > 200) {
      setErrorMsg("Độ gối chồng (chunk_overlap) phải nằm trong khoảng 0 - 200 tokens.");
      return;
    }
    if (chunkOverlap >= chunkSize) {
      setErrorMsg("Độ gối chồng phải nhỏ hơn kích thước phân đoạn.");
      return;
    }

    setIsSubmitting(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      await documentsApi.parseDocument(documentId, {
        chunk_size: chunkSize,
        chunk_overlap: chunkOverlap,
        extract_tables: extractTables,
        force_reparse: forceReparse,
      });

      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: DOCUMENT_QUERY_KEYS.structure(documentId) });
      queryClient.invalidateQueries({ queryKey: DOCUMENT_QUERY_KEYS.chunks(documentId) });
      queryClient.invalidateQueries({ queryKey: DOCUMENT_QUERY_KEYS.references(documentId) });
      queryClient.invalidateQueries({ queryKey: DOCUMENT_QUERY_KEYS.detail(documentId) });
      queryClient.invalidateQueries({ queryKey: DOCUMENT_QUERY_KEYS.status(documentId) });

      setSuccessMsg("Đã kích hoạt bóc tách tài liệu thành công!");
      onParseSuccess?.();
      setTimeout(() => {
        onClose();
      }, 800);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Kích hoạt bóc tách tài liệu thất bại.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Cấu hình bóc tách tài liệu"
      onClick={(e) => {
        if (e.target === e.currentTarget && !isSubmitting) onClose();
      }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in duration-150 text-xs"
    >
      <div className="w-full max-w-lg bg-canvas dark:bg-[#1a1917] rounded-xl shadow-2xl border border-hairline dark:border-[#2f2b26] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="h-12 px-5 border-b border-hairline dark:border-[#2f2b26] flex items-center justify-between shrink-0 bg-surface-soft/40 dark:bg-[#1f1d1a]">
          <div className="flex items-center gap-2 font-serif font-semibold text-sm text-ink dark:text-zinc-100">
            <Sliders className="w-4 h-4 text-coral-600 dark:text-coral-400" />
            <span>Cấu hình bóc tách tài liệu (Parse Document)</span>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            aria-label="Đóng hộp thoại"
            className="p-1 rounded-md hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink disabled:opacity-40"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4 overflow-y-auto max-h-[80vh]">
          {documentTitle && (
            <div className="p-2.5 rounded-lg bg-surface-soft/60 dark:bg-[#22201d] border border-hairline dark:border-[#302c26]">
              <span className="text-[11px] text-muted block mb-0.5">Tài liệu mục tiêu:</span>
              <p className="font-serif font-medium text-ink dark:text-zinc-200 line-clamp-1">
                {documentTitle}
              </p>
            </div>
          )}

          {/* Quick Presets */}
          <div className="space-y-1.5">
            <label className="text-[11px] font-semibold text-ink dark:text-zinc-300 block">
              Mẫu cấu hình khuyến nghị (Presets):
            </label>
            <div className="grid grid-cols-3 gap-2">
              {PRESETS.map((preset) => {
                const isSelected = chunkSize === preset.chunkSize && chunkOverlap === preset.chunkOverlap;
                return (
                  <button
                    key={preset.name}
                    type="button"
                    onClick={() => handleApplyPreset(preset)}
                    className={`p-2.5 rounded-lg text-left border transition-all cursor-pointer ${
                      isSelected
                        ? "border-coral-500 bg-coral-500/10 text-coral-700 dark:text-coral-300 font-semibold"
                        : "border-hairline dark:border-[#332f29] bg-surface-card dark:bg-[#201e1b] text-ink dark:text-zinc-300 hover:border-hairline-strong"
                    }`}
                  >
                    <span className="text-xs block font-serif font-medium">{preset.name}</span>
                    <span className="text-[10px] font-mono text-muted block mt-0.5">
                      {preset.chunkSize} / {preset.chunkOverlap}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Chunk Size Slider & Number Input */}
          <div className="space-y-1.5 p-3 rounded-lg bg-surface-card dark:bg-[#201e1b] border border-hairline dark:border-[#302c26]">
            <div className="flex items-center justify-between">
              <label htmlFor="chunk-size-input" className="text-xs font-medium text-ink dark:text-zinc-200">
                Kích thước phân đoạn (Chunk Size)
              </label>
              <div className="flex items-center gap-1 font-mono text-xs">
                <input
                  id="chunk-size-input"
                  type="number"
                  min={100}
                  max={2048}
                  step={16}
                  value={chunkSize}
                  onChange={(e) => setChunkSize(Number(e.target.value))}
                  className="w-16 px-1.5 py-0.5 rounded text-right bg-canvas dark:bg-[#151412] border border-hairline focus:border-coral-500 outline-none"
                />
                <span className="text-muted text-[11px]">tokens</span>
              </div>
            </div>
            <input
              type="range"
              min={100}
              max={2048}
              step={16}
              value={chunkSize}
              onChange={(e) => setChunkSize(Number(e.target.value))}
              className="w-full accent-coral-500 cursor-pointer"
            />
            <p className="text-[10px] text-muted">
              Độ dài tối đa mỗi đoạn văn bản được nhúng vector (khuyến nghị 256 - 512 tokens).
            </p>
          </div>

          {/* Chunk Overlap Slider & Number Input */}
          <div className="space-y-1.5 p-3 rounded-lg bg-surface-card dark:bg-[#201e1b] border border-hairline dark:border-[#302c26]">
            <div className="flex items-center justify-between">
              <label htmlFor="chunk-overlap-input" className="text-xs font-medium text-ink dark:text-zinc-200">
                Độ gối chồng (Chunk Overlap)
              </label>
              <div className="flex items-center gap-1 font-mono text-xs">
                <input
                  id="chunk-overlap-input"
                  type="number"
                  min={0}
                  max={200}
                  step={5}
                  value={chunkOverlap}
                  onChange={(e) => setChunkOverlap(Number(e.target.value))}
                  className="w-16 px-1.5 py-0.5 rounded text-right bg-canvas dark:bg-[#151412] border border-hairline focus:border-coral-500 outline-none"
                />
                <span className="text-muted text-[11px]">tokens</span>
              </div>
            </div>
            <input
              type="range"
              min={0}
              max={200}
              step={5}
              value={chunkOverlap}
              onChange={(e) => setChunkOverlap(Number(e.target.value))}
              className="w-full accent-coral-500 cursor-pointer"
            />
            <p className="text-[10px] text-muted">
              Số lượng tokens lặp lại giữa các đoạn liền kề nhằm tránh mất ngữ cảnh biên (0 - 200).
            </p>
          </div>

          {/* Feature Toggles */}
          <div className="space-y-2 pt-1">
            <label className="flex items-center justify-between p-2.5 rounded-lg bg-surface-card dark:bg-[#201e1b] border border-hairline dark:border-[#302c26] cursor-pointer">
              <div className="flex items-center gap-2">
                <Table className="w-4 h-4 text-coral-600 dark:text-coral-400" />
                <div>
                  <span className="font-medium text-ink dark:text-zinc-200 block">
                    Trích xuất bảng biểu khoa học (Extract Tables)
                  </span>
                  <span className="text-[10px] text-muted block">
                    Tự động nhận diện cấu trúc dòng, cột và chuyển đổi sang bảng Markdown.
                  </span>
                </div>
              </div>
              <input
                type="checkbox"
                checked={extractTables}
                onChange={(e) => setExtractTables(e.target.checked)}
                className="w-4 h-4 accent-coral-500 rounded cursor-pointer"
              />
            </label>

            <label className="flex items-center justify-between p-2.5 rounded-lg bg-surface-card dark:bg-[#201e1b] border border-hairline dark:border-[#302c26] cursor-pointer">
              <div className="flex items-center gap-2">
                <RefreshCw className="w-4 h-4 text-coral-600 dark:text-coral-400" />
                <div>
                  <span className="font-medium text-ink dark:text-zinc-200 block">
                    Bắt buộc bóc tách lại (Force Reparse)
                  </span>
                  <span className="text-[10px] text-muted block">
                    Ghi đè chỉ mục vector và tái tạo lại toàn bộ chunks từ tệp gốc.
                  </span>
                </div>
              </div>
              <input
                type="checkbox"
                checked={forceReparse}
                onChange={(e) => setForceReparse(e.target.checked)}
                className="w-4 h-4 accent-coral-500 rounded cursor-pointer"
              />
            </label>
          </div>

          {/* Feedback messages */}
          {errorMsg && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {successMsg && (
            <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          {/* Footer Actions */}
          <div className="flex items-center justify-end gap-2 pt-2 border-t border-hairline dark:border-[#2f2b26]">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 rounded-lg border border-hairline hover:bg-black/5 dark:hover:bg-white/5 font-medium text-muted hover:text-ink transition-colors disabled:opacity-40"
            >
              Hủy
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-coral-500 hover:bg-coral-600 text-white font-medium shadow-xs transition-colors disabled:opacity-50 cursor-pointer"
            >
              {isSubmitting && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
              <span>{isSubmitting ? "Đang xử lý..." : "Kích hoạt bóc tách"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
