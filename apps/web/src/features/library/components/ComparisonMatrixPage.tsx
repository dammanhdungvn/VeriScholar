import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  TableProperties,
  Sparkles,
  Download,
  Search,
  ChevronLeft,
  ChevronRight,
  Loader2,
  Copy,
  Check,
  Folder,
} from "lucide-react";
import { DashboardTaskbar } from "@/features/dashboard/components/DashboardTaskbar";
import { MobileDashboardHeader } from "@/features/dashboard/components/MobileDashboardHeader";
import { useDashboardStore } from "@/features/dashboard/stores/useDashboardStore";
import { useDashboardSessions } from "@/features/dashboard/hooks/useDashboardSessions";
import { useComparisonMatrixMutation, useFolderTreeQuery } from "../hooks/useFolderQueries";
import type { ComparisonMatrixResponse, FolderTreeItem } from "../types";
import { cn } from "@/lib/utils";

export function ComparisonMatrixPage() {
  const navigate = useNavigate();
  const toggleSidebar = useDashboardStore((s) => s.toggleSidebar);
  const { sessions } = useDashboardSessions();

  const [topic, setTopic] = useState("So sánh phương pháp luận, tập dữ liệu thực nghiệm và kết quả benchmark");
  const [selectedFolderId, setSelectedFolderId] = useState<string | "all">("all");
  const [matrixData, setMatrixData] = useState<ComparisonMatrixResponse | null>(null);
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<"table" | "synthesis" | "markdown">("table");
  const [searchFilter, setSearchFilter] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  const { data: folderTree } = useFolderTreeQuery();
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
      const matchAuthors = row.authors?.some((a) => a.toLowerCase().includes(q));
      return Boolean(matchTitle) || Boolean(matchMethod) || Boolean(matchDatasets) || Boolean(matchMetrics) || Boolean(matchAuthors);
    });
  }, [matrixRows, searchFilter]);

  const totalPages = Math.max(1, Math.ceil(filteredRows.length / pageSize));
  const paginatedRows = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredRows.slice(start, start + pageSize);
  }, [filteredRows, currentPage, pageSize]);

  const handleGenerate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!topic.trim()) return;

    try {
      const res = await matrixMutation.mutateAsync({
        topic: topic.trim(),
        folder_id: selectedFolderId === "all" ? undefined : selectedFolderId,
        limit: 200,
      });
      setMatrixData(res);
      setSearchFilter("");
      setCurrentPage(1);
    } catch {
      // handled by mutation
    }
  };

  const handleCopyMarkdown = () => {
    if (!matrixData) return;
    const content = activeTab === "markdown" ? matrixData.markdown_table : matrixData.summary_synthesis;
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleExportCsv = () => {
    if (!matrixRows || matrixRows.length === 0) return;
    const headers = ["Tiêu đề", "Năm", "Tác giả", "Phương pháp", "Tập dữ liệu", "Chỉ số", "Điểm mạnh", "Hạn chế"];
    const csvRows = matrixRows.map((r) => [
      `"${(r.title || "").replace(/"/g, '""')}"`,
      r.year ?? "",
      `"${(r.authors || []).join(", ").replace(/"/g, '""')}"`,
      `"${(r.core_methodology || "").replace(/"/g, '""')}"`,
      `"${(r.datasets_used || []).join("; ").replace(/"/g, '""')}"`,
      `"${Object.entries(r.key_metrics || {}).map(([k, v]) => `${k}: ${v}`).join("; ").replace(/"/g, '""')}"`,
      `"${(Array.isArray(r.strengths) ? r.strengths.join("; ") : r.strengths || "").replace(/"/g, '""')}"`,
      `"${(Array.isArray(r.limitations) ? r.limitations.join("; ") : r.limitations || "").replace(/"/g, '""')}"`,
    ]);

    const csvContent = "\uFEFF" + [headers.join(","), ...csvRows.map((e) => e.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `VeriScholar_Comparison_Matrix_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="h-screen w-screen flex bg-canvas dark:bg-[#181715] text-ink dark:text-[#f3f2ef] overflow-hidden">
      {/* 1. Left Navigation Taskbar */}
      <DashboardTaskbar
        sessions={sessions}
        onSelectSession={(id) => navigate(`/dashboard/${id}`)}
        onNewSession={() => navigate("/dashboard")}
      />

      {/* 2. Center Content Area */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative">
        <MobileDashboardHeader
          onToggleSidebar={toggleSidebar}
          onNewSession={() => navigate("/dashboard")}
        />

        {/* Top Header Bar */}
        <header className="h-14 px-6 border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#fdfcf9] dark:bg-[#1c1b18] flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-stone-500/10 dark:bg-stone-500/20 flex items-center justify-center text-stone-700 dark:text-stone-300">
              <TableProperties className="w-4 h-4 stroke-[2]" />
            </div>
            <div>
              <h1 className="text-sm font-semibold font-anthropic-serif text-ink dark:text-zinc-100">
                Comparison Matrix
              </h1>
              <p className="text-[11px] text-muted dark:text-zinc-400 font-sans">
                Cross-Paper Benchmark & Analysis
              </p>
            </div>
          </div>

          {matrixData && (
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleExportCsv}
                className="h-7 px-2.5 rounded-lg text-xs font-medium flex items-center gap-1.5 bg-[#c15f3e] hover:bg-[#a84f32] text-white transition-colors cursor-pointer"
                title="Export CSV"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Export CSV</span>
              </button>
              <button
                type="button"
                onClick={handleCopyMarkdown}
                className="h-7 px-2.5 rounded-lg text-xs font-medium border border-hairline hover:bg-surface-cream dark:hover:bg-[#262420] text-ink dark:text-zinc-200 transition-colors cursor-pointer flex items-center gap-1.5"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? "Copied" : "Copy Markdown"}</span>
              </button>
            </div>
          )}
        </header>

        {/* Query & Scope Bar */}
        <div className="p-3 border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#f8f6f0] dark:bg-[#1a1916] shrink-0">
          <form onSubmit={handleGenerate} className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 max-w-6xl mx-auto">
            {/* Scope select */}
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white dark:bg-[#22201c] border border-hairline text-xs">
              <Folder className="w-3.5 h-3.5 text-muted" />
              <select
                value={selectedFolderId}
                onChange={(e) => setSelectedFolderId(e.target.value)}
                className="bg-transparent border-none outline-none text-xs text-ink dark:text-zinc-200 font-medium cursor-pointer"
              >
                <option value="all">All Documents</option>
                {folderTree?.map((f: FolderTreeItem) => (
                  <option key={f.id} value={f.id}>
                    {f.name} ({f.document_count || 0})
                  </option>
                ))}
              </select>
            </div>

            {/* Prompt input */}
            <div className="flex-1 relative">
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Topic (e.g. Attention mechanisms, Reasoning benchmarks)..."
                className="w-full px-3 py-1.5 rounded-xl bg-white dark:bg-[#22201c] border border-hairline focus:border-[#c15f3e] outline-none text-xs text-ink dark:text-zinc-100 font-sans shadow-xs"
              >
              </input>
            </div>

            {/* Submit button */}
            <button
              type="submit"
              disabled={matrixMutation.isPending || !topic.trim()}
              className="h-8 px-3 rounded-xl text-xs font-medium flex items-center justify-center gap-1.5 bg-[#c15f3e] hover:bg-[#a84f32] disabled:opacity-50 text-white shadow-xs transition-colors cursor-pointer shrink-0"
            >
              {matrixMutation.isPending ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Analyze Matrix</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* View Tabs Ribbon & Search */}
        {matrixData && (
          <div className="px-6 py-2 border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-white dark:bg-[#1a1916] flex flex-col sm:flex-row items-center justify-between gap-2 shrink-0">
            <div className="flex items-center gap-1 text-xs font-medium">
              <button
                type="button"
                onClick={() => setActiveTab("table")}
                className={cn(
                  "px-2.5 py-1 rounded-lg transition-colors cursor-pointer",
                  activeTab === "table"
                    ? "bg-stone-500/10 text-ink dark:text-zinc-100 font-semibold"
                    : "text-muted hover:text-ink"
                )}
              >
                Matrix ({filteredRows.length})
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("synthesis")}
                className={cn(
                  "px-2.5 py-1 rounded-lg transition-colors cursor-pointer",
                  activeTab === "synthesis"
                    ? "bg-stone-500/10 text-ink dark:text-zinc-100 font-semibold"
                    : "text-muted hover:text-ink"
                )}
              >
                Synthesis
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("markdown")}
                className={cn(
                  "px-2.5 py-1 rounded-lg transition-colors cursor-pointer",
                  activeTab === "markdown"
                    ? "bg-stone-500/10 text-ink dark:text-zinc-100 font-semibold"
                    : "text-muted hover:text-ink"
                )}
              >
                Markdown
              </button>
            </div>

            {activeTab === "table" && (
              <div className="relative w-full sm:w-60">
                <Search className="w-3.5 h-3.5 text-muted absolute left-2.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={searchFilter}
                  onChange={(e) => {
                    setSearchFilter(e.target.value);
                    setCurrentPage(1);
                  }}
                  placeholder="Filter rows..."
                  className="w-full pl-8 pr-3 py-1 rounded-lg bg-[#fbf9f5] dark:bg-[#141311] border border-hairline text-xs outline-none focus:border-[#c15f3e]"
                />
              </div>
            )}
          </div>
        )}

        {/* Main Content Workspace */}
        <div className="flex-1 overflow-y-auto p-6">
          {!matrixData && !matrixMutation.isPending && (
            <div className="max-w-md mx-auto py-16 text-center space-y-3">
              <div className="w-12 h-12 rounded-xl bg-stone-500/10 text-stone-600 dark:text-stone-300 flex items-center justify-center mx-auto">
                <TableProperties className="w-6 h-6 stroke-[1.8]" />
              </div>
              <h2 className="text-base font-semibold font-anthropic-serif text-ink dark:text-zinc-100">
                Comparison Matrix
              </h2>
              <p className="text-xs text-muted dark:text-zinc-400 leading-relaxed">
                Extract and compare methodologies, datasets, and benchmark metrics across papers.
              </p>
              <button
                type="button"
                onClick={() => handleGenerate()}
                className="h-9 px-4 rounded-xl text-xs font-medium bg-[#c15f3e] hover:bg-[#a84f32] text-white transition-colors cursor-pointer shadow-xs inline-flex items-center gap-2"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Run Matrix Analysis</span>
              </button>
            </div>
          )}

          {matrixMutation.isPending && (
            <div className="max-w-md mx-auto py-20 text-center space-y-3">
              <Loader2 className="w-7 h-7 text-[#c15f3e] animate-spin mx-auto" />
              <p className="text-xs font-semibold text-ink dark:text-zinc-200">
                Generating comparison matrix...
              </p>
              <p className="text-[11px] text-muted dark:text-zinc-400">
                Extracting evidence notes, metadata, and document chunks.
              </p>
            </div>
          )}

          {matrixData && activeTab === "table" && (
            <div className="max-w-7xl mx-auto space-y-4">
              <div className="rounded-2xl border border-[#e8e4dc] dark:border-[#2e2b26] bg-white dark:bg-[#1a1916] overflow-x-auto shadow-xs">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#f8f6f0] dark:bg-[#1f1d1a] text-muted dark:text-zinc-400 font-mono text-[11px]">
                      <th className="py-3 px-4 font-medium">Paper & Authors</th>
                      <th className="py-3 px-4 font-medium">Year</th>
                      <th className="py-3 px-4 font-medium">Methodology</th>
                      <th className="py-3 px-4 font-medium">Datasets</th>
                      <th className="py-3 px-4 font-medium">Metrics</th>
                      <th className="py-3 px-4 font-medium">Strengths / Limitations</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#ece8df] dark:divide-[#282622]">
                    {paginatedRows.map((row) => (
                      <tr key={row.document_id} className="hover:bg-[#faf8f4] dark:hover:bg-[#22201c] transition-colors">
                        <td className="py-3 px-4 max-w-xs">
                          <div className="font-semibold text-ink dark:text-zinc-100 font-anthropic-serif">
                            {row.title}
                          </div>
                          <div className="text-[11px] text-muted dark:text-zinc-400 truncate mt-0.5">
                            {row.authors?.join(", ") || "Unknown"}
                          </div>
                        </td>
                        <td className="py-3 px-4 font-mono text-muted dark:text-zinc-400">
                          {row.year ?? "—"}
                        </td>
                        <td className="py-3 px-4 text-xs font-sans text-ink dark:text-zinc-200 max-w-sm">
                          {row.core_methodology || "—"}
                        </td>
                        <td className="py-3 px-4 max-w-xs">
                          <div className="flex flex-wrap gap-1">
                            {row.datasets_used?.map((d, i) => (
                              <span key={i} className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-stone-500/10 text-stone-700 dark:text-stone-300">
                                {d}
                              </span>
                            )) || "—"}
                          </div>
                        </td>
                        <td className="py-3 px-4 max-w-xs font-mono text-[11px]">
                          {Object.entries(row.key_metrics || {}).map(([k, v]) => (
                            <div key={k} className="text-ink dark:text-zinc-200">
                              <span className="text-muted dark:text-zinc-400">{k}:</span> {v}
                            </div>
                          ))}
                        </td>
                        <td className="py-3 px-4 text-[11px] max-w-xs space-y-1">
                          {row.strengths && (
                            <div className="text-emerald-700 dark:text-emerald-400">
                              + {Array.isArray(row.strengths) ? row.strengths[0] : row.strengths}
                            </div>
                          )}
                          {row.limitations && (
                            <div className="text-amber-700 dark:text-amber-400">
                              - {Array.isArray(row.limitations) ? row.limitations[0] : row.limitations}
                            </div>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between pt-2">
                  <span className="text-xs text-muted dark:text-zinc-400 font-mono">
                    Page {currentPage} / {totalPages} ({filteredRows.length} papers)
                  </span>
                  <div className="flex items-center gap-1">
                    <button
                      type="button"
                      disabled={currentPage <= 1}
                      onClick={() => setCurrentPage((p) => p - 1)}
                      className="p-1 rounded-lg border border-hairline disabled:opacity-40 hover:bg-surface-cream dark:hover:bg-[#252320] cursor-pointer"
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </button>
                    <button
                      type="button"
                      disabled={currentPage >= totalPages}
                      onClick={() => setCurrentPage((p) => p + 1)}
                      className="p-1 rounded-lg border border-hairline disabled:opacity-40 hover:bg-surface-cream dark:hover:bg-[#252320] cursor-pointer"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {matrixData && activeTab === "synthesis" && (
            <div className="max-w-4xl mx-auto p-8 rounded-2xl border border-[#e8e4dc] dark:border-[#2e2b26] bg-white dark:bg-[#1a1916] prose dark:prose-invert text-xs leading-relaxed">
              <h2 className="text-sm font-semibold font-anthropic-serif mb-4">
                Synthesis Summary
              </h2>
              <div className="whitespace-pre-wrap font-sans text-ink dark:text-zinc-200">
                {matrixData.summary_synthesis}
              </div>
            </div>
          )}

          {matrixData && activeTab === "markdown" && (
            <div className="max-w-4xl mx-auto p-6 rounded-2xl border border-[#e8e4dc] dark:border-[#2e2b26] bg-[#1a1916] text-zinc-100 font-mono text-xs overflow-x-auto">
              <pre className="whitespace-pre">{matrixData.markdown_table}</pre>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
