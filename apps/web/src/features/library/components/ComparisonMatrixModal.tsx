import { useState, useMemo } from "react";
import {
  X,
  TableProperties,
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  Copy,
  Check,
  BookOpen,
  ArrowRight,
  Loader2,
  Search,
  Download,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { useComparisonMatrixMutation } from "../hooks/useFolderQueries";
import type { ComparisonMatrixResponse } from "../types";

export interface ComparisonMatrixModalProps {
  isOpen: boolean;
  onClose: () => void;
  folderId?: string | null;
  folderName?: string | null;
  documentIds?: string[] | null;
}

export function ComparisonMatrixModal({
  isOpen,
  onClose,
  folderId,
  folderName,
  documentIds,
}: ComparisonMatrixModalProps) {
  const [topic, setTopic] = useState("");
  const [matrixData, setMatrixData] = useState<ComparisonMatrixResponse | null>(null);
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<"table" | "synthesis" | "markdown">("table");
  const [searchFilter, setSearchFilter] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState<number>(10);

  const matrixMutation = useComparisonMatrixMutation();

  const matrixRows = matrixData?.rows;
  const filteredRows = useMemo(() => {
    if (!matrixRows) return [];
    if (!searchFilter.trim()) return matrixRows;
    const q = searchFilter.toLowerCase().trim();
    return matrixRows.filter((row) => {
      const matchTitle = row.title?.toLowerCase().includes(q);
      const matchMethod = row.core_methodology?.toLowerCase().includes(q);
      const matchDatasets = row.datasets_used?.some((d) => d.toLowerCase().includes(q));
      const matchMetrics = Object.entries(row.key_metrics || {}).some(
        ([k, v]) => k.toLowerCase().includes(q) || String(v).toLowerCase().includes(q)
      );
      const matchStrengths = (Array.isArray(row.strengths) ? row.strengths : [row.strengths]).some(
        (s) => typeof s === "string" && s.toLowerCase().includes(q)
      );
      const matchLimitations = (Array.isArray(row.limitations) ? row.limitations : [row.limitations]).some(
        (l) => typeof l === "string" && l.toLowerCase().includes(q)
      );
      const matchAuthors = row.authors?.some((a) => a.toLowerCase().includes(q));
      return (
        Boolean(matchTitle) ||
        Boolean(matchMethod) ||
        Boolean(matchDatasets) ||
        Boolean(matchMetrics) ||
        Boolean(matchStrengths) ||
        Boolean(matchLimitations) ||
        Boolean(matchAuthors)
      );
    });
  }, [matrixRows, searchFilter]);

  const totalPages = Math.max(1, Math.ceil(filteredRows.length / pageSize));

  const paginatedRows = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredRows.slice(start, start + pageSize);
  }, [filteredRows, currentPage, pageSize]);

  if (!isOpen) return null;

  const handleGenerate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!topic.trim()) return;

    try {
      const res = await matrixMutation.mutateAsync({
        topic: topic.trim(),
        folder_id: folderId || undefined,
        document_ids: documentIds || undefined,
        limit: 200,
      });
      setMatrixData(res);
      setSearchFilter("");
      setCurrentPage(1);
    } catch (err) {
      console.warn("Failed to generate comparison matrix:", err);
    }
  };

  const handleCopyMarkdown = () => {
    if (!matrixData?.markdown_table) return;
    navigator.clipboard.writeText(matrixData.markdown_table);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExportCsv = () => {
    if (!matrixData) return;
    const rowsToExport = filteredRows.length > 0 ? filteredRows : matrixData.rows;
    const headers = [
      "Tài liệu / Tiêu đề",
      "Tác giả",
      "Năm",
      "Phương pháp cốt lõi",
      "Bộ dữ liệu",
      "Chỉ số thực nghiệm",
      "Điểm mạnh",
      "Hạn chế",
    ];

    const escapeCsv = (val: unknown): string => {
      if (val === null || val === undefined) return '""';
      const str = String(val).replace(/"/g, '""');
      return `"${str}"`;
    };

    const csvLines: string[] = [
      headers.map(escapeCsv).join(","),
      ...rowsToExport.map((row) => {
        const authors = row.authors?.join("; ") || "";
        const year = row.year ? String(row.year) : "";
        const datasets = row.datasets_used?.join("; ") || "";
        const metrics = Object.entries(row.key_metrics || {})
          .map(([k, v]) => `${k}: ${v}`)
          .join("; ");
        const strengths = (Array.isArray(row.strengths) ? row.strengths : [row.strengths])
          .filter(Boolean)
          .join("; ");
        const limitations = (Array.isArray(row.limitations) ? row.limitations : [row.limitations])
          .filter(Boolean)
          .join("; ");

        return [
          escapeCsv(row.title),
          escapeCsv(authors),
          escapeCsv(year),
          escapeCsv(row.core_methodology),
          escapeCsv(datasets),
          escapeCsv(metrics),
          escapeCsv(strengths),
          escapeCsv(limitations),
        ].join(",");
      }),
    ];

    const csvContent = "\uFEFF" + csvLines.join("\r\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const cleanTopic = (matrixData.topic || "literature_matrix")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .slice(0, 30);
    link.setAttribute("href", url);
    link.setAttribute("download", `verischolar_matrix_${cleanTopic}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Ma trận so sánh đối chiếu học thuật"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/60 backdrop-blur-xs animate-in fade-in duration-150 text-xs"
    >
      <div className="w-full max-w-5xl max-h-[90vh] bg-canvas dark:bg-[#181715] rounded-xl shadow-2xl border border-hairline dark:border-[#2f2b26] flex flex-col overflow-hidden text-ink dark:text-zinc-100">
        {/* Header */}
        <div className="h-14 px-5 border-b border-hairline dark:border-[#2f2b26] flex items-center justify-between shrink-0 bg-surface-cream/50 dark:bg-[#1d1b18]">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-coral-500/10 text-coral-600 dark:text-coral-400">
              <TableProperties className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-serif font-bold text-sm leading-tight text-ink dark:text-zinc-100">
                <span aria-hidden="true">Ma trận so sánh</span>
                <span className="sr-only">Ma Trận So Sánh Đối Chiếu Học Thuật (Literature Matrix)</span>
              </h3>
              <p className="text-[11px] text-muted dark:text-zinc-400">
                {folderName
                  ? `Thư mục: ${folderName}`
                  : "Toàn bộ tài liệu"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {matrixData && (
              <button
                type="button"
                onClick={() => setMatrixData(null)}
                className="px-2.5 py-1 text-xs rounded-md border border-hairline hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink cursor-pointer"
              >
                Tạo ma trận mới
              </button>
            )}
            <button
              type="button"
              onClick={onClose}
              aria-label="Đóng ma trận đối chiếu"
              className="p-1.5 rounded-md hover:bg-black/5 dark:hover:bg-white/5 text-muted hover:text-ink cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Body Content */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {!matrixData && (
            <div className="max-w-2xl mx-auto py-8 space-y-6">
              <div className="text-center space-y-2">
                <div className="w-12 h-12 mx-auto rounded-2xl bg-coral-500/10 flex items-center justify-center text-coral-600 dark:text-coral-400">
                  <Sparkles className="w-6 h-6" />
                </div>
                <h4 className="font-serif font-bold text-base text-ink dark:text-zinc-100">
                  <span aria-hidden="true">So sánh đa bài báo</span>
                  <span className="sr-only">Tổng hợp & So sánh Đa Bài báo Tự động</span>
                </h4>
                <p className="text-xs text-muted max-w-md mx-auto">
                  Trích xuất và đối chiếu phương pháp, dữ liệu, chỉ số và hạn chế của các bài báo.
                </p>
              </div>

              <form onSubmit={handleGenerate} className="space-y-4">
                <div className="space-y-1.5">
                  <label className="font-medium text-xs text-ink dark:text-zinc-300">
                    Chủ đề nghiên cứu đối chiếu:
                  </label>
                  <input
                    type="text"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    placeholder="Ví dụ: Cơ chế Attention và cải tiến giảm độ phức tạp tính toán..."
                    autoFocus
                    className="w-full px-3.5 py-2.5 rounded-xl border border-hairline focus:border-coral-500 outline-none bg-surface-card dark:bg-[#201e1b] text-sm shadow-2xs"
                  />
                </div>

                {/* Suggested Topics Pills */}
                <div className="space-y-1.5">
                  <span className="text-2xs text-muted font-medium">Gợi ý chủ đề:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {[
                      "So sánh phương pháp và kiến trúc mô hình chính",
                      "Đánh giá bộ dữ liệu thử nghiệm và chỉ số thực nghiệm",
                      "Tổng kết các hạn chế và hướng nghiên cứu mở rộng",
                    ].map((sug, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => setTopic(sug)}
                        className="px-2.5 py-1 rounded-full text-2xs bg-surface-soft dark:bg-[#282622] hover:bg-surface-cream-strong text-muted hover:text-ink border border-hairline transition-colors cursor-pointer"
                      >
                        {sug}
                      </button>
                    ))}
                  </div>
                </div>

                {matrixMutation.isError && (
                  <div
                    role="alert"
                    className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2"
                  >
                    <AlertTriangle className="w-4 h-4 shrink-0 text-rose-600 dark:text-rose-400" />
                    <span>
                      {matrixMutation.error instanceof Error
                        ? matrixMutation.error.message
                        : "Không thể khởi tạo ma trận đối chiếu. Vui lòng thử lại sau."}
                    </span>
                  </div>
                )}

                <div className="pt-2 flex justify-end">
                  <button
                    type="submit"
                    disabled={matrixMutation.isPending || !topic.trim()}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-coral-500 hover:bg-coral-600 text-white font-medium text-xs transition-colors shadow-sm disabled:opacity-50 cursor-pointer"
                  >
                    {matrixMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Đang phân tích...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        <span aria-hidden="true">Tạo ma trận</span>
                        <span className="sr-only">Sinh Ma Trận Đối Chiếu</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          )}

          {matrixData && (
            <div className="space-y-4">
              {/* Sufficiency Gate Banner */}
              <div
                className={`p-4 rounded-xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 ${
                  matrixData.sufficiency.is_sufficient
                    ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-900 dark:text-emerald-200"
                    : "bg-amber-500/10 border-amber-500/30 text-amber-900 dark:text-amber-200"
                }`}
              >
                <div className="space-y-1 flex-1">
                  <div className="flex items-center gap-2">
                    {matrixData.sufficiency.is_sufficient ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-600 text-white">
                        <ShieldCheck className="w-3 h-3" />
                        <span>ĐỦ DẪN CHỨNG ({(matrixData.sufficiency.sufficiency_score * 100).toFixed(0)}%)</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-600 text-white">
                        <AlertTriangle className="w-3 h-3" />
                        <span>THIẾU KHÍA CẠNH ({(matrixData.sufficiency.sufficiency_score * 100).toFixed(0)}%)</span>
                      </span>
                    )}
                    <span className="font-semibold text-xs">
                      Đã đối chiếu {matrixData.documents_compared} bài báo cho chủ đề "{matrixData.topic}"
                    </span>
                  </div>
                  <p className="text-2xs opacity-90 leading-relaxed font-sans">
                    {matrixData.sufficiency.reasoning}
                  </p>

                  {matrixData.sufficiency.missing_aspects?.length > 0 && (
                    <div className="flex items-center gap-1.5 pt-1 text-2xs">
                      <span className="font-semibold">Khía cạnh còn khuyết:</span>
                      {matrixData.sufficiency.missing_aspects.map((aspect, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 rounded bg-black/10 dark:bg-white/10 font-mono text-[10px]"
                        >
                          {aspect}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="shrink-0 flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleExportCsv}
                    data-testid="export-csv-btn"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-hairline bg-surface-card hover:bg-surface-cream dark:bg-[#201e1b] dark:hover:bg-[#282622] text-xs font-medium cursor-pointer shadow-2xs transition-colors"
                  >
                    <Download className="w-3.5 h-3.5 text-coral-600 dark:text-coral-400" />
                    <span aria-hidden="true">Xuất CSV</span>
                    <span className="sr-only">Xuất CSV / Excel</span>
                  </button>
                  <button
                    type="button"
                    onClick={handleCopyMarkdown}
                    className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-hairline bg-surface-card hover:bg-surface-cream dark:bg-[#201e1b] dark:hover:bg-[#282622] text-xs font-medium cursor-pointer shadow-2xs transition-colors"
                  >
                    {copied ? (
                      <>
                        <Check className="w-3 h-3 text-emerald-500" />
                        <span>Đã chép!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3" />
                        <span>Sao chép bảng</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* View Tabs */}
              <div className="flex items-center justify-between border-b border-hairline dark:border-[#2f2b26] pb-2">
                <div className="flex items-center gap-1 p-0.5 rounded-lg bg-surface-soft dark:bg-[#201e1b] border border-hairline">
                  <button
                    type="button"
                    onClick={() => setActiveTab("table")}
                    className={`px-3 py-1 rounded text-xs font-medium transition-colors cursor-pointer ${
                      activeTab === "table"
                        ? "bg-canvas dark:bg-[#2c2925] text-ink dark:text-zinc-100 shadow-2xs"
                        : "text-muted hover:text-ink"
                    }`}
                  >
                    Bảng đối chiếu
                  </button>
                  <button
                    type="button"
                    onClick={() => setActiveTab("synthesis")}
                    className={`px-3 py-1 rounded text-xs font-medium transition-colors cursor-pointer ${
                      activeTab === "synthesis"
                        ? "bg-canvas dark:bg-[#2c2925] text-ink dark:text-zinc-100 shadow-2xs"
                        : "text-muted hover:text-ink"
                    }`}
                  >
                    Tổng quan luận giải
                  </button>
                  <button
                    type="button"
                    onClick={() => setActiveTab("markdown")}
                    className={`px-3 py-1 rounded text-xs font-medium transition-colors cursor-pointer ${
                      activeTab === "markdown"
                        ? "bg-canvas dark:bg-[#2c2925] text-ink dark:text-zinc-100 shadow-2xs"
                        : "text-muted hover:text-ink"
                    }`}
                  >
                    <span aria-hidden="true">Markdown</span>
                    <span className="sr-only">Mã nguồn Markdown</span>
                  </button>
                </div>
              </div>

              {/* Tab 1: Interactive Comparison Matrix Table */}
              {activeTab === "table" && (
                <div className="space-y-3">
                  {/* Search / Filter & Page Size Bar */}
                  <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
                    <div className="relative flex-1 max-w-md">
                      <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
                      <input
                        type="text"
                        value={searchFilter}
                        onChange={(e) => {
                          setSearchFilter(e.target.value);
                          setCurrentPage(1);
                        }}
                        placeholder="Lọc theo phương pháp, dữ liệu, chỉ số, hạn chế..."
                        data-testid="search-matrix-input"
                        className="w-full pl-8 pr-8 py-1.5 rounded-lg border border-hairline bg-surface-card dark:bg-[#201e1b] text-xs focus:border-coral-500 outline-none text-ink dark:text-zinc-100 shadow-2xs"
                      />
                      {searchFilter && (
                        <button
                          type="button"
                          onClick={() => {
                            setSearchFilter("");
                            setCurrentPage(1);
                          }}
                          className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted hover:text-ink text-xs cursor-pointer"
                          aria-label="Xóa bộ lọc"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      )}
                    </div>

                    <div className="flex items-center gap-3 justify-between sm:justify-end text-2xs text-muted">
                      <span>
                        {filteredRows.length === matrixData.rows.length ? (
                          <span>Tổng cộng: <strong className="text-ink dark:text-zinc-100">{matrixData.rows.length}</strong> bài báo</span>
                        ) : (
                          <span>
                            Kết quả lọc: <strong className="text-ink dark:text-zinc-100">{filteredRows.length}</strong> / {matrixData.rows.length} bài báo
                          </span>
                        )}
                      </span>

                      <div className="flex items-center gap-1.5">
                        <span>Mỗi trang:</span>
                        <select
                          value={pageSize}
                          onChange={(e) => {
                            setPageSize(Number(e.target.value));
                            setCurrentPage(1);
                          }}
                          aria-label="Số dòng mỗi trang"
                          className="px-2 py-1 rounded border border-hairline bg-surface-card dark:bg-[#201e1b] text-2xs text-ink dark:text-zinc-200 outline-none cursor-pointer"
                        >
                          <option value={10}>10</option>
                          <option value={25}>25</option>
                          <option value={50}>50</option>
                          <option value={100}>100</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Table with smooth horizontal & vertical scroll */}
                  <div className="border border-hairline dark:border-[#2f2b26] rounded-xl overflow-x-auto max-h-[60vh] overflow-y-auto shadow-sm">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead className="sticky top-0 z-10 bg-surface-soft dark:bg-[#22201d] shadow-2xs">
                        <tr className="border-b border-hairline dark:border-[#2f2b26] text-muted font-serif">
                          <th className="p-3 w-48 font-semibold">Tài liệu / Tác giả</th>
                          <th className="p-3 w-60 font-semibold">Phương pháp cốt lõi</th>
                          <th className="p-3 w-36 font-semibold">Bộ dữ liệu</th>
                          <th className="p-3 w-40 font-semibold">Chỉ số thực nghiệm</th>
                          <th className="p-3 w-48 font-semibold">Điểm mạnh</th>
                          <th className="p-3 w-48 font-semibold">Hạn chế / Điểm nghẽn</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-hairline dark:divide-[#2f2b26]">
                        {paginatedRows.map((row, idx) => (
                          <tr
                            key={row.document_id || idx}
                            className="hover:bg-surface-soft/40 dark:hover:bg-[#1f1d1a] transition-colors align-top"
                          >
                            <td className="p-3 space-y-1">
                              <span className="font-serif font-medium text-ink dark:text-zinc-100 leading-snug block">
                                {row.title}
                              </span>
                              <div className="text-[10px] text-muted font-mono">
                                {row.authors?.slice(0, 2).join(", ")}
                                {row.authors?.length && row.authors.length > 2 && " et al."}
                                {row.year && ` (${row.year})`}
                              </div>
                            </td>
                            <td className="p-3 text-ink-muted dark:text-zinc-300 leading-relaxed font-sans">
                              {row.core_methodology}
                            </td>
                            <td className="p-3">
                              <div className="flex flex-wrap gap-1">
                                {row.datasets_used?.map((ds, i) => (
                                  <span
                                    key={i}
                                    className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-blue-500/10 text-blue-700 dark:text-blue-300"
                                  >
                                    {ds}
                                  </span>
                                ))}
                              </div>
                            </td>
                            <td className="p-3 font-mono text-[11px] text-coral-600 dark:text-amber-400">
                              {Object.entries(row.key_metrics || {}).map(([k, v], i) => (
                                <div key={i}>
                                  <span className="text-muted">{k}: </span>
                                  <span className="font-semibold">{v}</span>
                                </div>
                              ))}
                            </td>
                            <td className="p-3">
                              <ul className="list-disc list-inside space-y-1 text-emerald-700 dark:text-emerald-300 text-2xs">
                                {(Array.isArray(row.strengths) ? row.strengths : row.strengths ? [row.strengths] : []).map((s, i) => (
                                  <li key={i}>{s}</li>
                                ))}
                              </ul>
                            </td>
                            <td className="p-3">
                              <ul className="list-disc list-inside space-y-1 text-rose-700 dark:text-rose-300 text-2xs">
                                {(Array.isArray(row.limitations) ? row.limitations : row.limitations ? [row.limitations] : []).map((l, i) => (
                                  <li key={i}>{l}</li>
                                ))}
                              </ul>
                            </td>
                          </tr>
                        ))}
                        {filteredRows.length === 0 && (
                          <tr>
                            <td colSpan={6} className="py-12 text-center text-muted">
                              <AlertTriangle className="w-6 h-6 mx-auto mb-2 text-amber-500 opacity-60" />
                              <p className="text-xs">Không tìm thấy bài báo nào khớp với từ khóa "{searchFilter}".</p>
                              <button
                                type="button"
                                onClick={() => {
                                  setSearchFilter("");
                                  setCurrentPage(1);
                                }}
                                className="mt-2 text-coral-600 dark:text-coral-400 hover:underline text-2xs cursor-pointer font-medium"
                              >
                                Xóa bộ lọc để hiển thị toàn bộ {matrixData.rows.length} bài báo
                              </button>
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>

                  {/* Pagination Bar */}
                  {filteredRows.length > 0 && (
                    <div className="flex items-center justify-between px-2 py-1 text-2xs text-muted">
                      <div>
                        Hiển thị{" "}
                        <strong className="text-ink dark:text-zinc-200">
                          {(currentPage - 1) * pageSize + 1} -{" "}
                          {Math.min(currentPage * pageSize, filteredRows.length)}
                        </strong>{" "}
                        trong số <strong className="text-ink dark:text-zinc-200">{filteredRows.length}</strong> bài báo
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          disabled={currentPage <= 1}
                          onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                          data-testid="matrix-prev-page"
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded border border-hairline bg-surface-card hover:bg-surface-cream dark:bg-[#201e1b] dark:hover:bg-[#282622] disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-colors"
                        >
                          <ChevronLeft className="w-3 h-3" />
                          <span>Trước</span>
                        </button>

                        <span className="font-mono px-1">
                          Trang {currentPage} / {totalPages}
                        </span>

                        <button
                          type="button"
                          disabled={currentPage >= totalPages}
                          onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                          data-testid="matrix-next-page"
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded border border-hairline bg-surface-card hover:bg-surface-cream dark:bg-[#201e1b] dark:hover:bg-[#282622] disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-colors"
                        >
                          <span>Sau</span>
                          <ChevronRight className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Tab 2: Narrative Synthesis */}
              {activeTab === "synthesis" && (
                <div className="p-5 rounded-xl border border-hairline dark:border-[#2f2b26] bg-surface-card dark:bg-[#1a1917] space-y-3 leading-relaxed text-xs">
                  <div className="flex items-center gap-2 text-coral-600 dark:text-coral-400 font-serif font-bold text-sm">
                    <BookOpen className="w-4 h-4" />
                    <span>Luận giải Tổng quan & Nhận định Khoa học</span>
                  </div>
                  <div className="font-sans text-ink dark:text-zinc-200 whitespace-pre-wrap leading-relaxed">
                    {matrixData.summary_synthesis}
                  </div>
                </div>
              )}

              {/* Tab 3: Markdown View */}
              {activeTab === "markdown" && (
                <div className="relative">
                  <pre className="p-4 rounded-xl border border-hairline dark:border-[#2f2b26] bg-[#f7f5ee] dark:bg-[#141311] font-mono text-2xs overflow-x-auto whitespace-pre-wrap">
                    {matrixData.markdown_table}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
