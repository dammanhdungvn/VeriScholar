import { useState, useRef, useEffect, useMemo } from "react";
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Sparkles,
  Loader2,
  BookOpen,
  Brain,
  ArrowUp,
  X,
  Filter,
} from "lucide-react";
import { useWritingStore } from "../stores/useWritingStore";
import type { AtomicClaim } from "../types";
import { cn } from "@/lib/utils";

interface WritingAssistantPaneProps {
  onVerifyFacts?: () => Promise<void>;
  onSendAssistantPrompt?: (prompt: string) => Promise<void>;
  onOpenEvidence?: (claim: AtomicClaim) => void;
  onClose?: () => void;
  externalPrompt?: string;
}

export function WritingAssistantPane({
  onVerifyFacts,
  onSendAssistantPrompt,
  onOpenEvidence,
  onClose,
  externalPrompt,
}: WritingAssistantPaneProps) {
  const {
    lastVerifyResult,
    isVerifying,
    setActiveBoundingBoxes,
    openEvidenceModal,
    assistantPrompt,
    setAssistantPrompt,
    isAssisting,
  } = useWritingStore();

  const [promptInput, setPromptInput] = useState("");
  const [selectedClaimId, setSelectedClaimId] = useState<string | null>(null);
  const [claimFilter, setClaimFilter] = useState<"all" | "contradicted" | "supported" | "unverified">("all");
  const inputRef = useRef<HTMLInputElement>(null);

  // Zero-Click Focus when selection context buffer is passed
  useEffect(() => {
    const promptToSet = externalPrompt !== undefined ? externalPrompt : assistantPrompt;
    if (promptToSet) {
      const timer = setTimeout(() => {
        setPromptInput(promptToSet);
        if (inputRef.current) {
          inputRef.current.focus();
          inputRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [externalPrompt, assistantPrompt]);

  const claims = useMemo(() => lastVerifyResult?.claims || [], [lastVerifyResult]);

  const filteredClaims = useMemo(() => {
    if (claimFilter === "supported") return claims.filter((c) => c.status === "supported");
    if (claimFilter === "contradicted") return claims.filter((c) => c.status === "contradicted");
    if (claimFilter === "unverified") {
      return claims.filter((c) => c.status !== "supported" && c.status !== "contradicted");
    }
    return claims;
  }, [claims, claimFilter]);

  const handleClaimClick = (claim: AtomicClaim) => {
    setSelectedClaimId(claim.id);
    if (claim.evidence_bounding_boxes && claim.evidence_bounding_boxes.length > 0) {
      setActiveBoundingBoxes(claim.evidence_bounding_boxes, claim.evidence_page || 1);
    } else {
      setActiveBoundingBoxes([], claim.evidence_page || 1);
    }

    if (onOpenEvidence) {
      onOpenEvidence(claim);
    } else {
      openEvidenceModal(claim);
    }
  };

  const handleSendPrompt = async () => {
    if (!promptInput.trim()) return;
    const p = promptInput;
    setPromptInput("");
    setAssistantPrompt("");
    if (onSendAssistantPrompt) {
      await onSendAssistantPrompt(p);
    }
  };

  const promptPresets = [
    "Viết Literature Review từ các bài đã đọc",
    "Chuẩn hóa văn phong học thuật",
    "Rà soát tính nhất quán luận điểm",
  ];

  return (
    <div className="w-full md:w-80 xl:w-96 flex flex-col h-full bg-[#fbf9f5] dark:bg-[#181715] overflow-hidden select-none shrink-0 border-l border-[#ece8df] dark:border-[#2a2824]">
      {/* 1. Header with Close Button */}
      <div className="h-9 px-3 border-b border-[#ece8df] dark:border-[#2a2824] bg-[#f5f1e8] dark:bg-[#1e1c19] flex items-center justify-between text-xs font-semibold text-ink dark:text-zinc-200">
        <div className="flex items-center gap-1.5 font-anthropic-serif">
          <ShieldCheck className="w-4 h-4 text-coral-600 dark:text-coral-400" />
          <span aria-hidden="true">Kiểm chứng SAFE</span>
          <span className="sr-only">SAFE Fact-Checking</span>
        </div>

        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={onVerifyFacts}
            disabled={isVerifying}
            className="px-2 py-0.5 rounded text-[11px] font-medium bg-coral-500 hover:bg-coral-600 text-white disabled:opacity-50 transition-colors flex items-center gap-1 cursor-pointer"
            title="Kiểm chứng SAFE"
          >
            {isVerifying ? (
              <>
                <Loader2 className="w-3 h-3 animate-spin" />
                <span>Đang rà soát...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3 h-3" />
                <span>Kiểm chứng</span>
              </>
            )}
          </button>

          {onClose && (
            <button
              type="button"
              data-testid="close-assistant-pane-btn"
              onClick={onClose}
              className="p-1 rounded-md hover:bg-[#eae4d9] dark:hover:bg-[#282622] text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200 transition-colors cursor-pointer"
              title="Ẩn trợ lý AI (X)"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* 2. Fact-Checking Summary & Clean Claims List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {/* Verification Summary Banner */}
        {lastVerifyResult && (
          <div className="p-3 bg-white dark:bg-[#201e1a] rounded-xl border border-[#e8e4dc] dark:border-[#2e2b26] shadow-xs">
            <div className="flex items-center justify-between text-xs mb-2">
              <span className="font-semibold text-ink dark:text-zinc-200">Tỷ lệ chứng minh</span>
              <span className="font-bold text-emerald-600 dark:text-emerald-400">
                {Math.round(lastVerifyResult.supported_ratio * 100)}%
              </span>
            </div>

            {/* Progress Bar */}
            <div className="w-full h-1.5 bg-zinc-200 dark:bg-zinc-700 rounded-full overflow-hidden mb-2.5">
              <div
                className="h-full bg-emerald-500 transition-all duration-300"
                style={{ width: `${Math.round(lastVerifyResult.supported_ratio * 100)}%` }}
              />
            </div>

            {/* Interactive Stats badges */}
            <div className="grid grid-cols-3 gap-1.5 text-center text-[10px] font-mono">
              <button
                type="button"
                onClick={() => setClaimFilter(claimFilter === "supported" ? "all" : "supported")}
                className={cn(
                  "p-1.5 rounded border transition-all cursor-pointer text-left flex flex-col items-center",
                  claimFilter === "supported"
                    ? "bg-emerald-500/20 text-emerald-800 dark:text-emerald-300 border-emerald-500 ring-1 ring-emerald-500"
                    : "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/15"
                )}
                title="Lọc mệnh đề có bằng chứng hỗ trợ"
              >
                <span className="font-bold block text-xs">{lastVerifyResult.supported_claims}</span>
                <span>Supported</span>
              </button>

              <button
                type="button"
                onClick={() => setClaimFilter(claimFilter === "contradicted" ? "all" : "contradicted")}
                className={cn(
                  "p-1.5 rounded border transition-all cursor-pointer text-left flex flex-col items-center",
                  claimFilter === "contradicted"
                    ? "bg-rose-500/20 text-rose-800 dark:text-rose-300 border-rose-500 ring-1 ring-rose-500"
                    : "bg-rose-500/10 text-rose-700 dark:text-rose-400 border-rose-500/20 hover:bg-rose-500/15"
                )}
                title="Lọc mệnh đề mâu thuẫn"
              >
                <span className="font-bold block text-xs">{lastVerifyResult.contradicted_claims}</span>
                <span>Contradicted</span>
              </button>

              <button
                type="button"
                onClick={() => setClaimFilter(claimFilter === "unverified" ? "all" : "unverified")}
                className={cn(
                  "p-1.5 rounded border transition-all cursor-pointer text-left flex flex-col items-center",
                  claimFilter === "unverified"
                    ? "bg-amber-500/20 text-amber-800 dark:text-amber-300 border-amber-500 ring-1 ring-amber-500"
                    : "bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/20 hover:bg-amber-500/15"
                )}
                title="Lọc mệnh đề chưa đối chứng"
              >
                <span className="font-bold block text-xs">{lastVerifyResult.unverified_claims}</span>
                <span>Unverified</span>
              </button>
            </div>
          </div>
        )}

        {/* Filter Chips Bar */}
        {claims.length > 0 && (
          <div className="flex items-center justify-between gap-1 pb-1 border-b border-[#ece8df] dark:border-[#2a2824] text-[11px]">
            <div className="flex items-center gap-1 overflow-x-auto py-0.5">
              <button
                type="button"
                onClick={() => setClaimFilter("all")}
                className={cn(
                  "px-2 py-0.5 rounded-full font-medium transition-colors cursor-pointer",
                  claimFilter === "all"
                    ? "bg-coral-500 text-white"
                    : "bg-zinc-200/70 dark:bg-zinc-800 text-muted hover:text-ink dark:text-zinc-300"
                )}
              >
                Tất cả ({claims.length})
              </button>
              {lastVerifyResult?.contradicted_claims ? (
                <button
                  type="button"
                  onClick={() => setClaimFilter("contradicted")}
                  className={cn(
                    "px-2 py-0.5 rounded-full font-medium transition-colors cursor-pointer flex items-center gap-1",
                    claimFilter === "contradicted"
                      ? "bg-rose-600 text-white"
                      : "bg-rose-500/10 text-rose-700 dark:text-rose-400"
                  )}
                >
                  <XCircle className="w-3 h-3" />
                  Mâu thuẫn ({lastVerifyResult.contradicted_claims})
                </button>
              ) : null}
              {lastVerifyResult?.supported_claims ? (
                <button
                  type="button"
                  onClick={() => setClaimFilter("supported")}
                  className={cn(
                    "px-2 py-0.5 rounded-full font-medium transition-colors cursor-pointer flex items-center gap-1",
                    claimFilter === "supported"
                      ? "bg-emerald-600 text-white"
                      : "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400"
                  )}
                >
                  <CheckCircle2 className="w-3 h-3" />
                  Có dẫn chứng ({lastVerifyResult.supported_claims})
                </button>
              ) : null}
            </div>
          </div>
        )}

        {/* Claims Cards */}
        {claims.length > 0 ? (
          filteredClaims.length > 0 ? (
            <div className="space-y-2">
              {filteredClaims.map((claim) => {
                const isSelected = selectedClaimId === claim.id;
                const isSupported = claim.status === "supported";
                const isContradicted = claim.status === "contradicted";

                return (
                  <div
                    key={claim.id}
                    onClick={() => handleClaimClick(claim)}
                    className={cn(
                      "p-3 rounded-xl border text-xs transition-all cursor-pointer bg-white dark:bg-[#1f1d1a]",
                      isSelected
                        ? "ring-2 ring-coral-500 shadow-sm"
                        : "hover:border-zinc-400 dark:hover:border-zinc-600",
                      isSupported && "border-emerald-500/30 dark:border-emerald-500/20",
                      isContradicted && "border-rose-500/30 dark:border-rose-500/20",
                      !isSupported && !isContradicted && "border-[#e8e4dc] dark:border-[#2e2b26]"
                    )}
                  >
                    {/* Status header */}
                    <div className="flex items-center justify-between mb-1.5">
                      <span
                        className={cn(
                          "px-2 py-0.5 rounded-full text-[10px] font-semibold flex items-center gap-1",
                          isSupported && "bg-emerald-500/15 text-emerald-800 dark:text-emerald-300",
                          isContradicted && "bg-rose-500/15 text-rose-800 dark:text-rose-300",
                          !isSupported && !isContradicted && "bg-amber-500/15 text-amber-800 dark:text-amber-300"
                        )}
                      >
                        {isSupported && <CheckCircle2 className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />}
                        {isContradicted && <XCircle className="w-3 h-3 text-rose-600 dark:text-rose-400" />}
                        {!isSupported && !isContradicted && <HelpCircle className="w-3 h-3 text-amber-600 dark:text-amber-400" />}
                        <span>{claim.status.toUpperCase()}</span>
                      </span>

                      <span className="text-[10px] font-mono text-muted dark:text-zinc-400">
                        {Math.round(claim.confidence_score * 100)}% tin cậy
                      </span>
                    </div>

                    {/* Claim Text */}
                    <p className="font-medium text-ink dark:text-zinc-100 mb-1 leading-relaxed">
                      "{claim.claim_text}"
                    </p>

                    {/* Reasoning analysis note if available */}
                    {claim.reasoning && (
                      <div className="mt-1.5 p-1.5 rounded-md bg-[#f7f5f0] dark:bg-[#252320] text-[11px] text-zinc-600 dark:text-zinc-300">
                        <span className="font-semibold text-muted dark:text-zinc-400">Đối chiếu: </span>
                        <span>{claim.reasoning}</span>
                      </div>
                    )}

                    {/* Evidence Text & Citation */}
                    {claim.evidence_text && (
                      <div className="mt-1.5 p-2 rounded-lg bg-emerald-500/5 dark:bg-emerald-950/20 text-[11px] text-zinc-700 dark:text-zinc-300 border border-emerald-500/20">
                        <div className="font-semibold text-[10px] text-emerald-800 dark:text-emerald-400 flex items-center gap-1 mb-0.5">
                          <BookOpen className="w-3 h-3" />
                          <span>Bằng chứng trích dẫn:</span>
                        </div>
                        <p className="italic font-anthropic-serif line-clamp-3">
                          "{claim.evidence_text}"
                        </p>
                      </div>
                    )}

                    {/* Document & Page Badge */}
                    {claim.evidence_page && (
                      <div className="mt-2 flex items-center justify-between text-[10px] text-muted dark:text-zinc-400 font-mono">
                        <span className="truncate max-w-[180px]">
                          {claim.evidence_document_title ? `${claim.evidence_document_title} · ` : ""}Trang {claim.evidence_page}
                        </span>
                        {claim.evidence_bounding_boxes && claim.evidence_bounding_boxes.length > 0 && (
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleClaimClick(claim);
                            }}
                            className="text-coral-600 dark:text-coral-400 font-semibold hover:underline cursor-pointer shrink-0 ml-2"
                          >
                            <span aria-hidden="true">[Xem dẫn chứng ↗]</span>
                            <span className="sr-only">[Xem Bounding Box ↗]</span>
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="p-4 rounded-xl border border-dashed border-[#e2dcd2] dark:border-[#2e2b26] text-center text-xs text-muted dark:text-zinc-400">
              <Filter className="w-5 h-5 mx-auto mb-1 text-zinc-400 opacity-60" />
              <p>Không có luận điểm nào phù hợp bộ lọc.</p>
              <button
                type="button"
                onClick={() => setClaimFilter("all")}
                className="mt-1 text-coral-600 dark:text-coral-400 font-semibold underline cursor-pointer"
              >
                Hiển thị tất cả
              </button>
            </div>
          )
        ) : (
          <div className="p-4 rounded-xl border border-dashed border-[#e2dcd2] dark:border-[#2e2b26] text-center text-xs text-muted dark:text-zinc-400">
            <Sparkles className="w-6 h-6 text-coral-500 mx-auto mb-1.5" />
            <p className="font-medium">Chưa có báo cáo kiểm chứng</p>
            <p className="text-[11px] mt-1">
              Nhấn "Kiểm chứng" để rà soát văn bản khoa học.
            </p>
          </div>
        )}
      </div>

      {/* 3. AI Writing Assistant Prompt Box */}
      <div className="p-3 border-t border-[#ece8df] dark:border-[#2a2824] bg-[#f5f1e8] dark:bg-[#1c1b18] shrink-0 space-y-2">
        {/* Preset chips */}
        <div className="flex flex-wrap gap-1">
          {promptPresets.map((preset, i) => (
            <button
              key={i}
              type="button"
              onClick={() => setPromptInput(preset)}
              className="text-[10px] px-2 py-0.5 rounded-full bg-white dark:bg-[#252320] border border-[#e2dcd2] dark:border-[#2e2b26] text-muted hover:text-ink dark:text-zinc-300 transition-colors cursor-pointer"
            >
              {preset}
            </button>
          ))}
        </div>

        {/* Prompt Input Box */}
        <div className="bg-white dark:bg-[#201e1a] p-1.5 rounded-2xl border border-[#e2dcd2] dark:border-[#2e2b26] shadow-2xs focus-within:border-sky-400/60 dark:focus-within:border-sky-400/50 transition-all flex flex-col gap-1.5">
          <input
            ref={inputRef}
            type="text"
            value={promptInput}
            onChange={(e) => setPromptInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !isAssisting && handleSendPrompt()}
            disabled={isAssisting}
            placeholder={
              isAssisting
                ? "AI đang tạo đề xuất gợi ý..."
                : "Yêu cầu AI viết tiếp hoặc sửa văn phong..."
            }
            className="w-full text-xs px-2.5 pt-1.5 pb-0.5 bg-transparent text-ink dark:text-zinc-100 outline-none placeholder:text-zinc-400 disabled:opacity-50"
          />

          <div className="flex items-center justify-between px-1.5 pb-0.5">
            {/* Socratic Reasoning Pure Icon */}
            <div
              className="w-7 h-7 rounded-full flex items-center justify-center bg-sky-500/15 dark:bg-sky-400/20 text-sky-600 dark:text-sky-300 border border-sky-400/30"
              title="Chế độ Socratic Reasoning đang kích hoạt"
            >
              <Brain className="w-3.5 h-3.5" />
              <span className="sr-only">Socratic Reasoning</span>
            </div>

            {/* Circular Send Button */}
            <button
              type="button"
              onClick={handleSendPrompt}
              disabled={!promptInput.trim() || isAssisting}
              className={`w-7 h-7 rounded-full transition-all duration-150 cursor-pointer flex items-center justify-center ${
                promptInput.trim() && !isAssisting
                  ? "bg-ink dark:bg-white text-white dark:text-black hover:scale-105 active:scale-95 shadow-2xs font-bold"
                  : "bg-black/10 dark:bg-white/10 text-muted/40 dark:text-zinc-500 cursor-not-allowed"
              }`}
              title="Gửi prompt"
            >
              {isAssisting ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <ArrowUp className="w-3.5 h-3.5 stroke-[2.5]" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
