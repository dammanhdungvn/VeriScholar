import { useState, useRef, useEffect } from "react";
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Sparkles,
  Send,
  Loader2,
  BookOpen,
} from "lucide-react";
import { useWritingStore } from "../stores/useWritingStore";
import type { AtomicClaim } from "../types";
import { cn } from "@/lib/utils";

interface WritingAssistantPaneProps {
  onVerifyFacts?: () => Promise<void>;
  onSendAssistantPrompt?: (prompt: string) => Promise<void>;
  onOpenEvidence?: (claim: AtomicClaim) => void;
  externalPrompt?: string;
}

export function WritingAssistantPane({
  onVerifyFacts,
  onSendAssistantPrompt,
  onOpenEvidence,
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

  const claims = lastVerifyResult?.claims || [];

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
    <div className="w-80 xl:w-96 flex flex-col h-full bg-[#fbf9f5] dark:bg-[#181715] overflow-hidden select-none shrink-0">
      {/* 1. Header */}
      <div className="h-9 px-4 border-b border-[#ece8df] dark:border-[#2a2824] bg-[#f5f1e8] dark:bg-[#1e1c19] flex items-center justify-between text-xs font-semibold text-ink dark:text-zinc-200">
        <div className="flex items-center gap-1.5 font-anthropic-serif">
          <ShieldCheck className="w-4 h-4 text-coral-600 dark:text-coral-400" />
          <span>SAFE Fact-Checking</span>
        </div>

        <button
          type="button"
          onClick={onVerifyFacts}
          disabled={isVerifying}
          className="px-2 py-0.5 rounded text-[11px] font-medium bg-coral-500 hover:bg-coral-600 text-white disabled:opacity-50 transition-colors flex items-center gap-1 cursor-pointer"
          title="Kích hoạt kiểm chứng 4 giai đoạn SAFE"
        >
          {isVerifying ? (
            <>
              <Loader2 className="w-3 h-3 animate-spin" />
              <span>Đang kiểm chứng...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-3 h-3" />
              <span>Kiểm chứng sự thật</span>
            </>
          )}
        </button>
      </div>

      {/* 2. Fact-Checking Summary & Claims List */}
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

            {/* Stats badges */}
            <div className="grid grid-cols-3 gap-1.5 text-center text-[10px] font-mono">
              <div className="p-1 rounded bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20">
                <span className="font-bold block">{lastVerifyResult.supported_claims}</span>
                <span>Supported</span>
              </div>
              <div className="p-1 rounded bg-rose-500/10 text-rose-700 dark:text-rose-400 border border-rose-500/20">
                <span className="font-bold block">{lastVerifyResult.contradicted_claims}</span>
                <span>Contradicted</span>
              </div>
              <div className="p-1 rounded bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-500/20">
                <span className="font-bold block">{lastVerifyResult.unverified_claims}</span>
                <span>Unverified</span>
              </div>
            </div>
          </div>
        )}

        {/* Claims Cards */}
        {claims.length > 0 ? (
          <div className="space-y-2">
            <div className="text-[11px] font-semibold text-muted dark:text-zinc-400 uppercase tracking-wider">
              Danh sách mệnh đề nguyên tử ({claims.length})
            </div>

            {claims.map((claim) => {
              const isSelected = selectedClaimId === claim.id;
              const isSupported = claim.status === "supported";
              const isContradicted = claim.status === "contradicted";

              return (
                <div
                  key={claim.id}
                  onClick={() => handleClaimClick(claim)}
                  className={cn(
                    "p-2.5 rounded-xl border text-xs transition-all cursor-pointer",
                    isSelected
                      ? "ring-2 ring-coral-500 shadow-xs"
                      : "hover:border-zinc-400 dark:hover:border-zinc-600",
                    isSupported && "bg-emerald-500/5 border-emerald-500/30",
                    isContradicted && "bg-rose-500/5 border-rose-500/30",
                    !isSupported && !isContradicted && "bg-amber-500/5 border-amber-500/30"
                  )}
                >
                  {/* Status header */}
                  <div className="flex items-center justify-between mb-1.5">
                    <span
                      className={cn(
                        "px-1.5 py-0.5 rounded text-[10px] font-semibold flex items-center gap-1",
                        isSupported && "bg-emerald-500/20 text-emerald-800 dark:text-emerald-300",
                        isContradicted && "bg-rose-500/20 text-rose-800 dark:text-rose-300",
                        !isSupported && !isContradicted && "bg-amber-500/20 text-amber-800 dark:text-amber-300"
                      )}
                    >
                      {isSupported && <CheckCircle2 className="w-3 h-3 text-emerald-600" />}
                      {isContradicted && <XCircle className="w-3 h-3 text-rose-600" />}
                      {!isSupported && !isContradicted && <HelpCircle className="w-3 h-3 text-amber-600" />}
                      <span>{claim.status.toUpperCase()}</span>
                    </span>

                    <span className="text-[10px] font-mono text-muted dark:text-zinc-400">
                      {Math.round(claim.confidence_score * 100)}% tin cậy
                    </span>
                  </div>

                  {/* Claim Text */}
                  <p className="font-medium text-ink dark:text-zinc-100 mb-1 leading-snug">
                    "{claim.claim_text}"
                  </p>

                  {/* Evidence Text & Citation */}
                  {claim.evidence_text && (
                    <div className="mt-1.5 p-1.5 rounded bg-white/70 dark:bg-[#1a1917]/70 text-[11px] text-zinc-600 dark:text-zinc-300 border border-black/5 dark:border-white/5">
                      <div className="font-semibold text-[10px] text-muted dark:text-zinc-400 flex items-center gap-1 mb-0.5">
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
                    <div className="mt-1.5 flex items-center justify-between text-[10px] text-muted dark:text-zinc-400 font-mono">
                      <span>Trang {claim.evidence_page}</span>
                      {claim.evidence_bounding_boxes && claim.evidence_bounding_boxes.length > 0 && (
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleClaimClick(claim);
                          }}
                          className="text-coral-600 dark:text-coral-400 font-semibold hover:underline cursor-pointer"
                        >
                          [Xem Bounding Box ↗]
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
            <Sparkles className="w-6 h-6 text-coral-500 mx-auto mb-1.5" />
            <p className="font-medium">Chưa có báo cáo kiểm chứng</p>
            <p className="text-[11px] mt-1">
              Bấm nút "Kiểm chứng sự thật" ở trên để phân rã và đối chiếu mệnh đề trong bài viết.
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

        {/* Prompt Input */}
        <div className="flex items-center gap-1.5 bg-white dark:bg-[#201e1a] p-1.5 rounded-xl border border-[#e2dcd2] dark:border-[#2e2b26]">
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
            className="flex-1 text-xs px-1.5 py-1 bg-transparent text-ink dark:text-zinc-100 outline-none placeholder:text-zinc-400 disabled:opacity-50"
          />
          <button
            type="button"
            onClick={handleSendPrompt}
            disabled={!promptInput.trim() || isAssisting}
            className="p-1.5 rounded-lg bg-coral-500 hover:bg-coral-600 text-white disabled:opacity-40 transition-colors cursor-pointer flex items-center justify-center"
            title="Gửi prompt"
          >
            {isAssisting ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Send className="w-3.5 h-3.5" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
