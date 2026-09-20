import { useState, useMemo } from "react";
import {
  ArrowLeft,
  Briefcase,
  CheckCircle2,
  Clock,
  Plus,
  Check,
  Download,
  Copy,
  Layers,
  FileText,
  FileCode,
  ShieldCheck,
  Sparkles,
  Eye,
  Code2,
  FileSpreadsheet
} from "lucide-react";
import type { CoworkTask } from "@/types/dashboard";
import { COWORK_SAMPLE_TASKS } from "../data/mockDashboardData";
import { MathRenderer } from "@/components/shared/MathRenderer";
import { CitationBadge } from "./CitationBadge";
import { useDashboardStore } from "../stores/useDashboardStore";

type ArtifactViewMode = "preview" | "latex" | "markdown";

export function DashboardCoworkView() {
  const setAppMode = useDashboardStore((s) => s.setAppMode);
  const [tasks, setTasks] = useState<CoworkTask[]>(COWORK_SAMPLE_TASKS);
  const [activeTaskId, setActiveTaskId] = useState<string>(COWORK_SAMPLE_TASKS[0].id);
  const [copied, setCopied] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [newGoalInput, setNewGoalInput] = useState("");
  const [viewMode, setViewMode] = useState<ArtifactViewMode>("preview");

  const currentTask = tasks.find((t) => t.id === activeTaskId) ?? tasks[0];

  const handleApprove = () => {
    setTasks((prev) =>
      prev.map((t) => {
        if (t.id === currentTask.id) {
          const updatedSteps = t.steps.map((s) =>
            s.status === "waiting_approval" ? { ...s, status: "completed" as const } : s
          );
          return {
            ...t,
            status: "completed" as const,
            progress: 100,
            steps: updatedSteps
          };
        }
        return t;
      })
    );
  };

  const handleReject = () => {
    setTasks((prev) =>
      prev.map((t) => {
        if (t.id === currentTask.id) {
          const updatedSteps = t.steps.map((s) =>
            s.status === "waiting_approval" ? { ...s, status: "pending" as const } : s
          );
          return {
            ...t,
            status: "running" as const,
            progress: 50,
            steps: updatedSteps
          };
        }
        return t;
      })
    );
  };

  const latexCode = useMemo(() => {
    return `% VeriScholar LaTeX
\\begin{table}[htbp]
  \\centering
  \\caption{Đối Chiếu Định Lượng: Self-Attention vs Recurrent Layers}
  \\label{tab:complexity_comparison}
  \\begin{tabular}{lll}
    \\hline
    \\textbf{Tiêu Chí} & \\textbf{Self-Attention} & \\textbf{Recurrent} \\\\
    \\hline
    Độ phức tạp mỗi lớp & $\\mathcal{O}(n^2 \\cdot d)$ & $\\mathcal{O}(n \\cdot d^2)$ \\\\
    Thao tác tuần tự tối thiểu & $\\mathcal{O}(1)$ & $\\mathcal{O}(n)$ \\\\
    Độ dài đường đi tối đa & $\\mathcal{O}(1)$ & $\\mathcal{O}(n)$ \\\\
    Huấn luyện song song & Hoàn toàn song song & Tuần tự theo thời gian \\\\
    \\hline
  \\end{tabular}
\\end{table}`;
  }, []);

  const handleCopyArtifact = () => {
    if (!currentTask.artifact) return;
    const textToCopy = viewMode === "latex" ? latexCode : currentTask.artifact.content;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!currentTask.artifact) return;
    const content = viewMode === "latex" ? latexCode : currentTask.artifact.content;
    const filename =
      viewMode === "latex"
        ? `${currentTask.artifact.title.replace(/\s+/g, "_")}.tex`
        : `${currentTask.artifact.title.replace(/\s+/g, "_")}.md`;
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleCreateTask = () => {
    if (!newGoalInput.trim()) return;
    const newTask: CoworkTask = {
      id: `task-${Date.now()}`,
      title: newGoalInput.trim().slice(0, 45),
      goal: newGoalInput.trim(),
      status: "running",
      progress: 25,
      context_sources: [
        { id: "src-new-1", name: "Attention_Is_All_You_Need.pdf", type: "pdf", size: "2.1 MB" },
        { id: "src-new-2", name: "ResearchNotes.md", type: "docx", size: "8 KB" }
      ],
      steps: [
        { id: "step-1", name: "Bóc tách cấu trúc tài liệu", status: "completed", details: "" },
        { id: "step-2", name: "Lập bảng đối chiếu học thuật", status: "running", details: "" },
        { id: "step-3", name: "Phê duyệt đưa vào bản thảo", status: "pending", details: "" },
        { id: "step-4", name: "Xuất file LaTeX hoàn chỉnh", status: "pending", details: "" }
      ],
      artifact: {
        id: `art-${Date.now()}`,
        title: newGoalInput.trim().slice(0, 30),
        type: "markdown",
        version: "v0.1",
        updated_at: new Date().toISOString(),
        content: `# ${newGoalInput.trim()}`
      }
    };

    setTasks((prev) => [newTask, ...prev]);
    setActiveTaskId(newTask.id);
    setNewGoalInput("");
    setIsCreating(false);
  };

  return (
    <div className="flex-1 flex flex-col md:flex-row h-full overflow-hidden bg-[#faf8f5] dark:bg-[#141311] text-ink dark:text-[#f3f2ef]">
      {/* 1. Left Column: Work Intake & Steps (40% width, max 420px) */}
      <div className="w-full md:w-[360px] lg:w-[400px] border-r border-[#e8e4dc] dark:border-[#282622] flex flex-col justify-between h-full bg-[#fdfcf9] dark:bg-[#191815] shrink-0">
        {/* Header Bar */}
        <div className="h-12 px-3 sm:px-4 border-b border-[#e8e4dc] dark:border-[#282622] flex items-center justify-between shrink-0">
          <div className="flex items-center gap-1.5 sm:gap-2">
            <button
              type="button"
              onClick={() => setAppMode("chat")}
              title="Quay lại hội thoại"
              className="p-1 -ml-1 rounded-lg text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#eae4d9] dark:hover:bg-[#282622] transition-colors cursor-pointer"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
            </button>
            <Briefcase className="w-4 h-4 text-coral-600 dark:text-coral-400" />
            <span className="font-semibold text-xs text-ink dark:text-zinc-100 tracking-tight">
              Kế Hoạch Thực Thi
            </span>
            <span
              className={`text-3xs font-mono px-1.5 py-0.5 rounded-full font-medium ${
                currentTask.status === "waiting_approval"
                  ? "bg-amber-500/15 text-amber-700 dark:text-amber-400 border border-amber-500/30"
                  : currentTask.status === "completed"
                  ? "bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border border-emerald-500/30"
                  : "bg-coral-500/15 text-coral-700 dark:text-coral-400 border border-coral-500/30"
              }`}
            >
              {currentTask.status === "waiting_approval"
                ? "Chờ duyệt"
                : currentTask.status === "completed"
                ? "Hoàn thành"
                : "Đang chạy"}
            </span>
          </div>

          <button
            type="button"
            onClick={() => setIsCreating(!isCreating)}
            className="flex items-center gap-1 text-2xs px-2 py-1 bg-[#f2eee6] dark:bg-[#252320] hover:bg-[#eae4d9] dark:hover:bg-[#2f2b26] text-ink dark:text-zinc-200 rounded-lg border border-[#ded8cc] dark:border-[#38332c] transition-colors cursor-pointer font-medium"
          >
            <Plus className="w-3 h-3 text-coral-600 dark:text-coral-400" />
            <span>Tác vụ</span>
          </button>
        </div>

        {/* Task Creator Form if expanded */}
        {isCreating && (
          <div className="p-3 border-b border-[#e8e4dc] dark:border-[#282622] bg-[#f7f4ee] dark:bg-[#1e1d1a] space-y-2">
            <textarea
              value={newGoalInput}
              onChange={(e) => setNewGoalInput(e.target.value)}
              placeholder="Nhập mục tiêu tác vụ..."
              rows={2}
              className="w-full text-xs p-2 bg-canvas dark:bg-[#141311] border border-[#e5dfd4] dark:border-[#38332c] rounded-lg text-ink dark:text-zinc-100 placeholder-muted dark:placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-coral-500/30 resize-none font-sans"
            />
            <div className="flex justify-end gap-1.5">
              <button
                type="button"
                onClick={() => setIsCreating(false)}
                className="px-2 py-1 text-2xs text-muted hover:text-ink transition-colors"
              >
                Hủy
              </button>
              <button
                type="button"
                onClick={handleCreateTask}
                className="px-2.5 py-1 bg-coral-600 hover:bg-coral-700 text-white text-2xs font-medium rounded-md shadow-2xs transition-colors"
              >
                Tạo
              </button>
            </div>
          </div>
        )}

        {/* Task Progress & Step Timeline */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {/* Active Task Card */}
          <div className="p-3 rounded-xl bg-white dark:bg-[#1c1b18] border border-[#e8e4dc] dark:border-[#2d2b27] shadow-2xs space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-ink dark:text-zinc-100 font-sans truncate max-w-[280px]">
                {currentTask.title}
              </span>
              <span className="text-2xs font-mono font-semibold text-coral-600 dark:text-coral-400">
                {currentTask.progress}%
              </span>
            </div>

            {/* Progress Bar */}
            <div className="w-full h-1 bg-[#eae5dc] dark:bg-[#282622] rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  currentTask.status === "completed"
                    ? "bg-emerald-500"
                    : "bg-gradient-to-r from-coral-500 to-amber-500"
                }`}
                style={{ width: `${currentTask.progress}%` }}
              />
            </div>
          </div>

          {/* Steps List */}
          <div className="space-y-1.5">
            {currentTask.steps.map((step, idx) => {
              const isDone = step.status === "completed";
              const isWaiting = step.status === "waiting_approval";
              const isRunning = step.status === "running";

              return (
                <div
                  key={step.id}
                  className={`px-3 py-2 rounded-xl border transition-all flex items-center justify-between text-xs font-sans ${
                    isWaiting
                      ? "border-amber-500/50 bg-amber-500/8 dark:bg-amber-950/20"
                      : isDone
                      ? "border-emerald-500/30 bg-emerald-500/5 dark:bg-emerald-950/10"
                      : isRunning
                      ? "border-coral-500/40 bg-coral-500/5 dark:bg-coral-950/10"
                      : "border-[#ece7de] dark:border-[#282622] bg-white/60 dark:bg-[#1a1916]/60"
                  }`}
                >
                  <div className="flex items-center gap-2 min-w-0">
                    {isDone ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
                    ) : isWaiting ? (
                      <Clock className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0 animate-pulse" />
                    ) : isRunning ? (
                      <Sparkles className="w-4 h-4 text-coral-600 dark:text-coral-400 shrink-0 animate-spin" />
                    ) : (
                      <span className="w-4 h-4 rounded-full border border-[#d8d2c6] dark:border-zinc-700 flex items-center justify-center text-3xs font-mono text-muted shrink-0">
                        {idx + 1}
                      </span>
                    )}
                    <span className="font-medium text-ink dark:text-zinc-200 truncate">{step.name}</span>
                  </div>

                  {isWaiting && (
                    <span className="text-3xs font-mono font-medium text-amber-700 dark:text-amber-400 bg-amber-500/15 px-1.5 py-0.5 rounded border border-amber-500/30 shrink-0">
                      Chờ duyệt
                    </span>
                  )}
                  {isRunning && (
                    <span className="text-3xs font-mono font-medium text-coral-600 dark:text-coral-400 bg-coral-500/15 px-1.5 py-0.5 rounded animate-pulse border border-coral-500/30 shrink-0">
                      Đang chạy
                    </span>
                  )}
                </div>
              );
            })}
          </div>

          {/* Minimal Human Approval Gate Banner */}
          {currentTask.status === "waiting_approval" && (
            <div className="p-3 rounded-xl bg-amber-500/10 dark:bg-amber-950/20 border border-amber-500/30 flex items-center justify-between gap-2 shadow-2xs">
              <div className="flex items-center gap-2 text-xs font-medium text-amber-900 dark:text-amber-200">
                <ShieldCheck className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0" />
                <span>Xác nhận bản thảo</span>
              </div>
              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={handleReject}
                  className="px-2 py-1 rounded-lg border border-amber-500/30 text-amber-900 dark:text-amber-200 text-2xs font-medium hover:bg-amber-500/10 transition-colors cursor-pointer"
                >
                  Sửa
                </button>
                <button
                  type="button"
                  onClick={handleApprove}
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-2xs font-medium shadow-2xs transition-colors cursor-pointer"
                >
                  <Check className="w-3 h-3" />
                  <span>Phê duyệt</span>
                </button>
              </div>
            </div>
          )}

          {/* Context Sources Chips */}
          {currentTask.context_sources && currentTask.context_sources.length > 0 && (
            <div className="space-y-1 pt-1">
              <div className="flex flex-wrap gap-1.5">
                {currentTask.context_sources.map((src) => (
                  <div
                    key={src.id}
                    className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-white dark:bg-[#1c1b18] border border-[#e8e4dc] dark:border-[#2d2b27] text-3xs font-mono text-ink dark:text-zinc-300"
                  >
                    {src.type === "pdf" ? (
                      <FileText className="w-3 h-3 text-coral-600 dark:text-coral-400 shrink-0" />
                    ) : (
                      <FileCode className="w-3 h-3 text-emerald-500 shrink-0" />
                    )}
                    <span className="truncate max-w-[140px]">{src.name}</span>
                    <span className="text-muted dark:text-zinc-500">({src.size})</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 2. Right Column: Artifact Viewer (60% width) */}
      <div className="flex-1 flex flex-col h-full overflow-hidden bg-canvas dark:bg-[#141311] select-text">
        {/* Artifact Top Bar */}
        <div className="h-12 px-4 border-b border-[#e8e4dc] dark:border-[#282622] flex items-center justify-between shrink-0 bg-white/60 dark:bg-[#191815]/60 backdrop-blur-xs">
          <div className="flex items-center gap-2 min-w-0">
            <Layers className="w-4 h-4 text-coral-600 dark:text-coral-400 shrink-0" />
            <span className="font-semibold text-xs sm:text-sm text-ink dark:text-zinc-100 truncate">
              {currentTask.artifact?.title ?? "Bản thảo"}
            </span>
          </div>

          <div className="flex items-center gap-2">
            {/* Mode Switcher Tabs */}
            <div className="flex items-center p-0.5 rounded-lg bg-[#f0ecdc] dark:bg-[#252320] border border-[#e2dcd0] dark:border-[#332f29]">
              <button
                type="button"
                onClick={() => setViewMode("preview")}
                className={`flex items-center gap-1 px-2 py-0.5 text-2xs font-medium rounded-md transition-colors cursor-pointer ${
                  viewMode === "preview"
                    ? "bg-white dark:bg-[#1c1b18] text-ink dark:text-zinc-100 shadow-2xs font-semibold"
                    : "text-muted dark:text-zinc-400 hover:text-ink"
                }`}
              >
                <Eye className="w-3 h-3" />
                <span>Xem</span>
              </button>
              <button
                type="button"
                onClick={() => setViewMode("latex")}
                className={`flex items-center gap-1 px-2 py-0.5 text-2xs font-medium rounded-md transition-colors cursor-pointer ${
                  viewMode === "latex"
                    ? "bg-white dark:bg-[#1c1b18] text-ink dark:text-zinc-100 shadow-2xs font-semibold"
                    : "text-muted dark:text-zinc-400 hover:text-ink"
                }`}
              >
                <FileSpreadsheet className="w-3 h-3" />
                <span>LaTeX</span>
              </button>
              <button
                type="button"
                onClick={() => setViewMode("markdown")}
                className={`flex items-center gap-1 px-2 py-0.5 text-2xs font-medium rounded-md transition-colors cursor-pointer ${
                  viewMode === "markdown"
                    ? "bg-white dark:bg-[#1c1b18] text-ink dark:text-zinc-100 shadow-2xs font-semibold"
                    : "text-muted dark:text-zinc-400 hover:text-ink"
                }`}
              >
                <Code2 className="w-3 h-3" />
                <span>MD</span>
              </button>
            </div>

            {/* Actions */}
            <button
              type="button"
              onClick={handleCopyArtifact}
              title="Sao chép nội dung"
              className="inline-flex items-center gap-1 px-2 py-1 text-2xs font-sans font-medium rounded-lg bg-white dark:bg-[#252320] hover:bg-[#f5f1e8] dark:hover:bg-[#2e2b26] text-ink dark:text-zinc-200 border border-[#ded8cc] dark:border-[#38332c] transition-colors cursor-pointer shadow-2xs"
            >
              {copied ? <Check className="w-3 h-3 text-emerald-500" /> : <Copy className="w-3 h-3" />}
              <span>{copied ? "Đã chép" : "Chép"}</span>
            </button>
            <button
              type="button"
              onClick={handleDownload}
              title="Tải về"
              className="inline-flex items-center gap-1 px-2 py-1 text-2xs font-sans font-medium rounded-lg bg-white dark:bg-[#252320] hover:bg-[#f5f1e8] dark:hover:bg-[#2e2b26] text-ink dark:text-zinc-200 border border-[#ded8cc] dark:border-[#38332c] transition-colors cursor-pointer shadow-2xs"
            >
              <Download className="w-3 h-3" />
              <span>Tải</span>
            </button>
          </div>
        </div>

        {/* Artifact Content Area */}
        <div className="flex-1 overflow-y-auto p-5 max-w-3xl w-full mx-auto space-y-4">
          {currentTask.artifact ? (
            viewMode === "preview" ? (
              <div className="p-6 rounded-2xl bg-white dark:bg-[#191815] border border-[#e8e4dc] dark:border-[#282622] shadow-sm space-y-4">
                <h1 className="font-serif text-lg sm:text-xl font-bold tracking-tight text-ink dark:text-zinc-100 pb-2 border-b border-[#eeeae2] dark:border-[#282622]">
                  {currentTask.artifact.title}
                </h1>

                {/* Formatted Academic Table */}
                <div className="overflow-x-auto rounded-xl border border-[#e8e4dc] dark:border-[#2d2b27]">
                  <table className="w-full text-xs sm:text-sm border-collapse text-left">
                    <thead>
                      <tr className="bg-[#f7f4ee] dark:bg-[#201e1a] border-b border-[#e8e4dc] dark:border-[#2d2b27] text-ink dark:text-zinc-200">
                        <th className="p-3 font-semibold text-xs tracking-tight">Tiêu chí</th>
                        <th className="p-3 font-semibold text-xs tracking-tight text-coral-700 dark:text-coral-300">
                          Self-Attention
                        </th>
                        <th className="p-3 font-semibold text-xs tracking-tight text-muted dark:text-zinc-400">
                          Recurrent (RNN)
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#ece7de] dark:divide-[#262420] text-ink dark:text-zinc-300 font-sans">
                      <tr className="hover:bg-[#faf8f5] dark:hover:bg-[#1e1d1a] transition-colors">
                        <td className="p-3 font-medium">Độ phức tạp mỗi lớp</td>
                        <td className="p-3 font-mono text-coral-600 dark:text-amber-400">
                          <MathRenderer math="\mathcal{O}(n^2 \cdot d)" />
                        </td>
                        <td className="p-3 font-mono text-muted dark:text-zinc-400">
                          <MathRenderer math="\mathcal{O}(n \cdot d^2)" />
                        </td>
                      </tr>
                      <tr className="hover:bg-[#faf8f5] dark:hover:bg-[#1e1d1a] transition-colors">
                        <td className="p-3 font-medium">Thao tác tuần tự</td>
                        <td className="p-3 font-mono text-coral-600 dark:text-amber-400">
                          <MathRenderer math="\mathcal{O}(1)" />
                        </td>
                        <td className="p-3 font-mono text-muted dark:text-zinc-400">
                          <MathRenderer math="\mathcal{O}(n)" />
                        </td>
                      </tr>
                      <tr className="hover:bg-[#faf8f5] dark:hover:bg-[#1e1d1a] transition-colors">
                        <td className="p-3 font-medium">Độ dài đường đi tối đa</td>
                        <td className="p-3 font-mono text-coral-600 dark:text-amber-400">
                          <MathRenderer math="\mathcal{O}(1)" />
                        </td>
                        <td className="p-3 font-mono text-muted dark:text-zinc-400">
                          <MathRenderer math="\mathcal{O}(n)" />
                        </td>
                      </tr>
                      <tr className="hover:bg-[#faf8f5] dark:hover:bg-[#1e1d1a] transition-colors">
                        <td className="p-3 font-medium">Huấn luyện song song</td>
                        <td className="p-3 font-medium text-emerald-600 dark:text-emerald-400">
                          Có
                        </td>
                        <td className="p-3 text-muted dark:text-zinc-400">
                          Không (tuần tự)
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                {/* Minimal Citation Footer */}
                <div className="flex items-center justify-between pt-2 border-t border-[#eeeae2] dark:border-[#282622] text-2xs text-muted dark:text-zinc-400">
                  <span className="font-mono">Nguồn chứng cứ</span>
                  <CitationBadge
                    citation={{
                      paper_id: "doc-vaswani-2017",
                      paper_title: "Attention Is All You Need",
                      page: 6,
                      bbox: [0.12, 0.45, 0.88, 0.72, 6]
                    }}
                  />
                </div>
              </div>
            ) : viewMode === "latex" ? (
              <div className="p-4 rounded-2xl bg-white dark:bg-[#191815] border border-[#e8e4dc] dark:border-[#282622] shadow-sm space-y-2">
                <div className="flex items-center justify-between text-2xs font-mono text-muted dark:text-zinc-400 pb-1.5 border-b border-[#eeeae2] dark:border-[#282622]">
                  <span>LaTeX</span>
                  <span>table.tex</span>
                </div>
                <pre className="whitespace-pre-wrap font-mono text-xs leading-relaxed bg-[#f7f4ee] dark:bg-[#12110f] p-3 rounded-xl border border-[#e5dfd4] dark:border-[#2d2b27] text-ink dark:text-zinc-200 overflow-x-auto">
                  {latexCode}
                </pre>
              </div>
            ) : (
              <div className="p-4 rounded-2xl bg-white dark:bg-[#191815] border border-[#e8e4dc] dark:border-[#282622] shadow-sm space-y-2">
                <div className="flex items-center justify-between text-2xs font-mono text-muted dark:text-zinc-400 pb-1.5 border-b border-[#eeeae2] dark:border-[#282622]">
                  <span>Markdown</span>
                  <span>artifact.md</span>
                </div>
                <pre className="whitespace-pre-wrap font-mono text-xs leading-relaxed bg-[#f7f4ee] dark:bg-[#12110f] p-3 rounded-xl border border-[#e5dfd4] dark:border-[#2d2b27] text-ink dark:text-zinc-200 overflow-x-auto">
                  {currentTask.artifact.content}
                </pre>
              </div>
            )
          ) : (
            <div className="text-center py-20 text-muted dark:text-zinc-500 text-xs">
              Chưa có bản thảo.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
