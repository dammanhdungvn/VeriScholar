import { useState, useEffect, useRef, useCallback } from "react";
import { Link, useParams } from "react-router-dom";
import {
  FileCode,
  Play,
  ShieldCheck,
  MessageSquare,
  Download,
  Save,
  CheckCircle2,
  AlertCircle,
  ArrowLeft,
  Loader2,
  Plus,
  Terminal,
} from "lucide-react";
import { AcademicLogo } from "@/components/shared/AcademicLogo";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { draftsApi } from "../api/draftsApi";
import type { DraftItem, VerifyClaimsResponse, DraftCommentItem } from "@/types/draft";

export function DraftingWorkspace() {
  const { draftId: routeDraftId } = useParams<{ draftId?: string }>();

  const [draftsList, setDraftsList] = useState<DraftItem[]>([]);
  const [activeDraft, setActiveDraft] = useState<DraftItem | null>(null);
  const [currentEtag, setCurrentEtag] = useState<string>("");
  const [content, setContent] = useState<string>("");
  const [title, setTitle] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [saveSuccess, setSaveSuccess] = useState<boolean>(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Tab state: "compile" | "factcheck" | "comments"
  const [activeTab, setActiveTab] = useState<"compile" | "factcheck" | "comments">("compile");

  // SSE Compilation State
  const [compileLogs, setCompileLogs] = useState<string[]>([]);
  const [isCompiling, setIsCompiling] = useState<boolean>(false);
  const [compileStatus, setCompileStatus] = useState<string | null>(null);
  const compileAbortRef = useRef<AbortController | null>(null);

  // SAFE Fact Checking State
  const [isVerifying, setIsVerifying] = useState<boolean>(false);
  const [factCheckResult, setFactCheckResult] = useState<VerifyClaimsResponse | null>(null);

  // Comments State
  const [comments, setComments] = useState<DraftCommentItem[]>([]);
  const [newCommentText, setNewCommentText] = useState<string>("");
  const [selectedLine, setSelectedLine] = useState<number>(1);

  // Load drafts list on mount
  const refreshDrafts = useCallback(async () => {
    try {
      setIsLoading(true);
      const res = await draftsApi.listDrafts({ per_page: 50 });
      setDraftsList(res.data);

      const targetId = routeDraftId || (res.data.length > 0 ? res.data[0].id : null);
      if (targetId) {
        const detailRes = await draftsApi.getDraft(targetId);
        setActiveDraft(detailRes.data);
        setTitle(detailRes.data.title);
        setContent(detailRes.data.content);
        setCurrentEtag(detailRes.headers.get("etag") || "");
      } else {
        setActiveDraft(null);
      }
    } catch (err) {
      console.error("Failed to load drafts:", err);
    } finally {
      setIsLoading(false);
    }
  }, [routeDraftId]);

  useEffect(() => {
    refreshDrafts();
  }, [refreshDrafts]);

  // Handle Create Draft
  const handleCreateDraft = async () => {
    try {
      setIsLoading(true);
      const res = await draftsApi.createDraft({
        title: "Bản thảo nghiên cứu mới",
        initial_content: `\\documentclass[11pt,a4paper]{article}
\\usepackage[utf8]{inputenc}
\\usepackage{amsmath,amssymb}
\\usepackage{cite}

\\title{Nghiên cứu về Kiến trúc Retrieval-Augmented Generation Grounded}
\\author{Nhà nghiên cứu VeriScholar}
\\date{\\today}

\\begin{document}
\\maketitle

\\begin{abstract}
Bản tóm tắt nghiên cứu khoa học với độ tin cậy trích dẫn cao.
\\end{abstract}

\\section{Giới thiệu}
Hệ thống VeriScholar cho phép xác thực phát biểu dựa trên bằng chứng chuẩn tọa độ BoundingBox.

\\end{document}`,
      });
      setActiveDraft(res.data);
      setTitle(res.data.title);
      setContent(res.data.content);
      setCurrentEtag(res.headers.get("etag") || "");
      await refreshDrafts();
    } catch (err) {
      console.error("Failed to create draft:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Save with OCC If-Match header
  const handleSave = async () => {
    if (!activeDraft) return;
    try {
      setIsSaving(true);
      setSaveError(null);
      setSaveSuccess(false);

      if (title !== activeDraft.title) {
        await draftsApi.patchDraft(activeDraft.id, { title }, currentEtag);
      }

      const res = await draftsApi.updateDraftContent(
        activeDraft.id,
        { content },
        currentEtag
      );

      setActiveDraft(res.data);
      setCurrentEtag(res.headers.get("etag") || "");
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      if (err.status === 412 || err.message?.includes("412")) {
        setSaveError("Xung đột phiên bản (OCC Conflict). Bản thảo đã được chỉnh sửa ở nơi khác!");
      } else {
        setSaveError(err.message || "Lỗi lưu bản thảo.");
      }
    } finally {
      setIsSaving(false);
    }
  };

  // Handle Compile LaTeX via SSE Stream
  const handleCompile = () => {
    if (!activeDraft) return;
    setIsCompiling(true);
    setCompileLogs([]);
    setCompileStatus("running");
    setActiveTab("compile");

    if (compileAbortRef.current) {
      compileAbortRef.current.abort();
    }

    compileAbortRef.current = draftsApi.compileDraftStream(
      activeDraft.id,
      { compiler_engine: "pdflatex" },
      {
        onMessage: (event, data: any) => {
          const logMsg = typeof data === "object" ? JSON.stringify(data) : String(data);
          setCompileLogs((prev) => [...prev, `[${event}] ${logMsg}`]);
        },
        onError: (err) => {
          setCompileLogs((prev) => [...prev, `[ERROR] ${err.message}`]);
          setIsCompiling(false);
          setCompileStatus("failed");
        },
        onComplete: () => {
          setCompileLogs((prev) => [...prev, "[SUCCESS] Biên dịch hoàn tất thành công!"]);
          setIsCompiling(false);
          setCompileStatus("success");
        },
      }
    );
  };

  // Handle SAFE Fact-Checking
  const handleFactCheck = async () => {
    if (!activeDraft || !content.trim()) return;
    try {
      setIsVerifying(true);
      setActiveTab("factcheck");
      const res = await draftsApi.verifyClaims(activeDraft.id, {
        selected_text: content.slice(0, 3000), // First 3000 chars for check
      });
      setFactCheckResult(res);
    } catch (err) {
      console.error("SAFE verification failed:", err);
    } finally {
      setIsVerifying(false);
    }
  };

  // Handle Export Bundle (.zip)
  const handleExportBundle = async (format: "zip" | "pdf" = "zip") => {
    if (!activeDraft) return;
    try {
      const blob = await draftsApi.exportBundle(activeDraft.id, format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${activeDraft.title.replace(/\s+/g, "_")}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Export bundle failed:", err);
    }
  };

  // Handle Add Comment
  const handleAddComment = async () => {
    if (!activeDraft || !newCommentText.trim()) return;
    try {
      const lines = content.split("\n");
      const res = await draftsApi.createComment(activeDraft.id, {
        line_number: selectedLine,
        selected_text: lines[selectedLine - 1] || "toàn dòng",
        comment: newCommentText.trim(),
      });
      setComments((prev) => [...prev, res]);
      setNewCommentText("");
    } catch (err) {
      console.error("Failed to add comment:", err);
    }
  };

  // Word count & Char count stats
  const wordCount = content.trim() ? content.trim().split(/\s+/).length : 0;
  const charCount = content.length;

  return (
    <div className="h-screen bg-[#faf8f4] dark:bg-[#161513] text-ink dark:text-zinc-100 flex flex-col overflow-hidden">
      {/* 1. Header Toolbar */}
      <header className="h-14 border-b border-[#e8e4dc] dark:border-[#2a2824] bg-white dark:bg-[#1c1b18] px-4 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <Link
            to="/dashboard"
            className="w-8 h-8 rounded-lg flex items-center justify-center text-muted hover:text-ink hover:bg-[#f2ece1] dark:hover:bg-[#282522] transition-colors"
            title="Quay lại Dashboard"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <AcademicLogo size="sm" showWordmark={false} />
          <div className="h-4 w-px bg-[#e8e4dc] dark:border-[#2a2824]" />
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Tiêu đề bản thảo..."
            className="h-8 w-64 md:w-80 text-sm font-semibold bg-transparent border-transparent hover:border-[#e8e4dc] focus:border-coral-500 rounded-lg"
          />
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          {saveError && (
            <span className="text-xs text-rose-500 font-medium flex items-center gap-1">
              <AlertCircle className="w-3.5 h-3.5" />
              {saveError}
            </span>
          )}
          {saveSuccess && (
            <span className="text-xs text-emerald-600 font-medium flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Đã lưu
            </span>
          )}

          <Button
            onClick={handleSave}
            disabled={isSaving || !activeDraft}
            size="sm"
            variant="secondary"
            className="h-8 text-xs gap-1.5"
          >
            {isSaving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
            <span>Lưu</span>
          </Button>

          <Button
            onClick={handleCompile}
            disabled={isCompiling || !activeDraft}
            size="sm"
            className="h-8 text-xs bg-coral-500 hover:bg-coral-600 text-white gap-1.5"
          >
            {isCompiling ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
            <span>Biên dịch LaTeX</span>
          </Button>

          <Button
            onClick={handleFactCheck}
            disabled={isVerifying || !activeDraft}
            size="sm"
            variant="secondary"
            className="h-8 text-xs gap-1.5"
          >
            {isVerifying ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5 text-coral-600" />}
            <span>Kiểm chứng SAFE</span>
          </Button>

          <Button
            onClick={() => handleExportBundle("zip")}
            disabled={!activeDraft}
            size="sm"
            variant="ghost"
            className="h-8 text-xs gap-1.5"
            title="Tải gói submission camera-ready (.zip)"
          >
            <Download className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Camera-Ready Bundle</span>
          </Button>
        </div>
      </header>

      {/* 2. Workspace Body: Left Sidebar (Drafts list) + Center Editor + Right Panels */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Drawer: Drafts List */}
        <aside className="w-56 border-r border-[#e8e4dc] dark:border-[#2a2824] bg-[#fbf9f5] dark:bg-[#1a1917] flex flex-col shrink-0">
          <div className="p-3 border-b border-[#ece8df] dark:border-[#2a2824] flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted font-mono">
              Bản thảo
            </span>
            <button
              onClick={handleCreateDraft}
              className="p-1 rounded-md text-coral-600 hover:bg-coral-500/10 cursor-pointer"
              title="Tạo bản thảo mới"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {isLoading && draftsList.length === 0 ? (
              <div className="py-8 text-center text-xs text-muted">
                <Loader2 className="w-4 h-4 animate-spin mx-auto mb-1" />
                Đang tải...
              </div>
            ) : draftsList.length === 0 ? (
              <div className="py-8 text-center text-xs text-muted px-2">
                Chưa có bản thảo nào. Nhấn dấu + để tạo mới.
              </div>
            ) : (
              draftsList.map((d) => (
                <button
                  key={d.id}
                  onClick={() => {
                    setActiveDraft(d);
                    setTitle(d.title);
                    setContent(d.content);
                  }}
                  className={`w-full text-left p-2 rounded-lg text-xs font-medium transition-colors flex items-center gap-2 ${
                    activeDraft?.id === d.id
                      ? "bg-white dark:bg-[#282522] shadow-2xs text-coral-600 font-semibold"
                      : "text-muted hover:text-ink hover:bg-[#f2ece1] dark:hover:bg-[#22201d]"
                  }`}
                >
                  <FileCode className="w-3.5 h-3.5 shrink-0" />
                  <span className="truncate flex-1">{d.title}</span>
                </button>
              ))
            )}
          </div>
        </aside>

        {/* Center: Editor Canvas */}
        <div className="flex-1 flex flex-col bg-white dark:bg-[#1e1d1a] border-r border-[#e8e4dc] dark:border-[#2a2824] overflow-hidden">
          {activeDraft ? (
            <>
              <div className="flex-1 p-4 overflow-hidden flex flex-col">
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Nhập nội dung LaTeX hoặc Markdown nghiên cứu khoa học tại đây..."
                  className="flex-1 w-full p-4 font-mono text-xs sm:text-sm leading-relaxed resize-none bg-[#fdfbf7] dark:bg-[#181715] border border-[#ece8df] dark:border-[#2a2824] rounded-xl focus:outline-none focus:ring-1 focus:ring-coral-500/40 select-text"
                  spellCheck={false}
                />
              </div>

              {/* Status Bar */}
              <div className="h-8 border-t border-[#ece8df] dark:border-[#2a2824] bg-[#fbf9f5] dark:bg-[#1a1917] px-4 flex items-center justify-between text-[11px] font-mono text-muted shrink-0">
                <div className="flex items-center gap-4">
                  <span>{wordCount} từ</span>
                  <span>{charCount} ký tự</span>
                  <span>ETag: {currentEtag ? currentEtag.slice(0, 10) : "mới"}</span>
                </div>
                <div>Format: LaTeX (pdflatex)</div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-muted p-8">
              <FileCode className="w-12 h-12 mb-3 stroke-[1.5]" />
              <p className="text-sm font-semibold mb-2">Chưa chọn bản thảo nào</p>
              <Button onClick={handleCreateDraft} size="sm" className="bg-coral-500 hover:bg-coral-600 text-white text-xs">
                Tạo bản thảo nghiên cứu đầu tiên
              </Button>
            </div>
          )}
        </div>

        {/* Right Drawer: Diagnostic Panel (Compile / Fact Check / Peer Comments) */}
        <div className="w-80 md:w-96 bg-[#fbf9f5] dark:bg-[#1c1b18] flex flex-col shrink-0 overflow-hidden">
          {/* Tabs Navigation */}
          <div className="h-10 border-b border-[#ece8df] dark:border-[#2a2824] flex items-center px-2 shrink-0">
            <button
              onClick={() => setActiveTab("compile")}
              className={`flex-1 h-8 text-xs font-medium rounded-md transition-colors flex items-center justify-center gap-1.5 ${
                activeTab === "compile"
                  ? "bg-white dark:bg-[#282522] text-coral-600 font-semibold shadow-2xs"
                  : "text-muted hover:text-ink"
              }`}
            >
              <Terminal className="w-3.5 h-3.5" />
              <span>Biên dịch</span>
            </button>
            <button
              onClick={() => setActiveTab("factcheck")}
              className={`flex-1 h-8 text-xs font-medium rounded-md transition-colors flex items-center justify-center gap-1.5 ${
                activeTab === "factcheck"
                  ? "bg-white dark:bg-[#282522] text-coral-600 font-semibold shadow-2xs"
                  : "text-muted hover:text-ink"
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Kiểm chứng</span>
            </button>
            <button
              onClick={() => setActiveTab("comments")}
              className={`flex-1 h-8 text-xs font-medium rounded-md transition-colors flex items-center justify-center gap-1.5 ${
                activeTab === "comments"
                  ? "bg-white dark:bg-[#282522] text-coral-600 font-semibold shadow-2xs"
                  : "text-muted hover:text-ink"
              }`}
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>Ghi chú ({comments.length})</span>
            </button>
          </div>

          {/* Tab 1: Live LaTeX Compile Logs */}
          {activeTab === "compile" && (
            <div className="flex-1 p-3 flex flex-col overflow-hidden">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono font-medium text-muted">Trạng thái:</span>
                <span
                  className={`text-[11px] font-mono px-2 py-0.5 rounded-full font-medium ${
                    compileStatus === "success"
                      ? "bg-emerald-500/10 text-emerald-600"
                      : compileStatus === "failed"
                      ? "bg-rose-500/10 text-rose-600"
                      : compileStatus === "running"
                      ? "bg-amber-500/10 text-amber-600"
                      : "bg-surface-cream text-muted"
                  }`}
                >
                  {compileStatus || "Sẵn sàng"}
                </span>
              </div>
              <div className="flex-1 bg-[#121212] text-emerald-400 p-3 rounded-xl font-mono text-[11px] overflow-y-auto space-y-1 select-text">
                {compileLogs.length === 0 ? (
                  <p className="text-zinc-500">Nhấn &quot;Biên dịch LaTeX&quot; để chạy SSE pipeline...</p>
                ) : (
                  compileLogs.map((log, i) => <div key={i}>{log}</div>)
                )}
              </div>
            </div>
          )}

          {/* Tab 2: SAFE Fact Checking Panel */}
          {activeTab === "factcheck" && (
            <div className="flex-1 p-3 overflow-y-auto space-y-3">
              <p className="text-xs text-muted">
                Quy trình SAFE 4 bước kiểm chứng các phát biểu khoa học đối chiếu với cơ sở dữ liệu học thuật.
              </p>
              {isVerifying ? (
                <div className="py-12 text-center text-xs text-muted">
                  <Loader2 className="w-5 h-5 animate-spin mx-auto mb-2 text-coral-500" />
                  Đang phân rã câu và kiểm chứng bằng chứng...
                </div>
              ) : factCheckResult ? (
                <div className="space-y-3">
                  <div className="p-3 rounded-xl bg-white dark:bg-[#22201d] border border-[#ece8df] dark:border-[#2a2824] shadow-2xs">
                    <span className="text-xs text-muted block mb-1 font-mono">Độ chuẩn xác (Factuality Score):</span>
                    <span className="text-2xl font-bold font-serif text-coral-600">
                      {factCheckResult.total_claims > 0
                        ? Math.round((factCheckResult.supported_count / factCheckResult.total_claims) * 100)
                        : 100}%
                    </span>
                    <p className="text-[11px] text-muted mt-1">
                      {factCheckResult.supported_count}/{factCheckResult.total_claims} phát biểu được bảo chứng đầy đủ.
                    </p>
                  </div>

                  {factCheckResult.claims?.map((claim, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-white dark:bg-[#22201d] border border-[#ece8df] dark:border-[#2a2824] text-xs space-y-1.5"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-ink dark:text-zinc-200">
                          Phát biểu #{idx + 1}
                        </span>
                        <span
                          className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                            claim.verdict === "supported"
                              ? "bg-emerald-500/10 text-emerald-600"
                              : "bg-rose-500/10 text-rose-600"
                          }`}
                        >
                          {claim.verdict.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-muted italic">&quot;{claim.claim_text}&quot;</p>
                      {claim.citation?.quote && (
                        <p className="text-[11px] text-zinc-600 dark:text-zinc-400 bg-surface-cream dark:bg-[#1a1917] p-2 rounded">
                          Bằng chứng: {claim.citation.quote}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="py-12 text-center text-xs text-muted">
                  Chưa có kết quả. Nhấn &quot;Kiểm chứng SAFE&quot; để rà soát bản thảo.
                </div>
              )}
            </div>
          )}

          {/* Tab 3: Peer Review Comments */}
          {activeTab === "comments" && (
            <div className="flex-1 p-3 flex flex-col overflow-hidden">
              <div className="flex-1 overflow-y-auto space-y-2 mb-3">
                {comments.length === 0 ? (
                  <p className="text-xs text-muted text-center py-8">Chưa có nhận xét dòng nào.</p>
                ) : (
                  comments.map((c) => (
                    <div
                      key={c.id}
                      className="p-2.5 rounded-xl bg-white dark:bg-[#22201d] border border-[#ece8df] dark:border-[#2a2824] text-xs space-y-1 shadow-2xs"
                    >
                      <div className="flex items-center justify-between text-[10px] text-muted font-mono">
                        <span>Dòng #{c.line_number}</span>
                        <span>{c.author_name}</span>
                      </div>
                      <p className="text-ink dark:text-zinc-200">{c.comment}</p>
                    </div>
                  ))
                )}
              </div>

              {/* Add Comment Input */}
              <div className="pt-2 border-t border-[#ece8df] dark:border-[#2a2824] space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted font-mono shrink-0">Dòng:</span>
                  <Input
                    type="number"
                    min={1}
                    value={selectedLine}
                    onChange={(e) => setSelectedLine(parseInt(e.target.value) || 1)}
                    className="h-7 w-20 text-xs font-mono"
                  />
                </div>
                <div className="flex gap-2">
                  <Input
                    value={newCommentText}
                    onChange={(e) => setNewCommentText(e.target.value)}
                    placeholder="Viết nhận xét..."
                    className="h-8 text-xs"
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleAddComment();
                      }
                    }}
                  />
                  <Button onClick={handleAddComment} size="sm" className="h-8 text-xs bg-coral-500 hover:bg-coral-600 text-white">
                    Gửi
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
