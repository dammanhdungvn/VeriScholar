import { useState, useRef, type DragEvent, type ChangeEvent } from "react";
import { Search, MessageSquare, FileUp, X } from "lucide-react";
import { AcademicLogo } from "@/components/shared/AcademicLogo";
import { useAuthStore } from "@/features/auth/stores/useAuthStore";
import { useTheme } from "@/hooks/useTheme";
import { DashboardChatInputBox } from "./DashboardChatInputBox";
import { ScholarlyResultCard } from "@/features/discovery/components/ScholarlyResultCard";
import { ScholarlySkeletonList } from "@/features/discovery/components/ScholarlySkeletonList";
import { discoveryApi, type ScholarlyPaper } from "@/features/discovery/api/discoveryApi";
import type { ReasoningEffortLevel } from "@/features/dashboard/stores/useDashboardStore";

interface UnifiedHeroWorkspaceProps {
  inputText: string;
  onChangeText: (text: string) => void;
  onSendChat: (text: string, reasoningEffort?: ReasoningEffortLevel) => void;
  onIngestFile: (file: File) => void | Promise<void>;
  onOpenPaper: (paper: ScholarlyPaper) => void | Promise<void>;
  isGenerating?: boolean;
}

const TOPIC_CHIPS = [
  { label: "Attention Mechanism", query: "Attention Is All You Need Transformer" },
  { label: "Graph Neural Networks", query: "Graph Neural Networks Review" },
  { label: "Deep Residual Learning", query: "Deep Residual Learning for Image Recognition ResNet" },
  { label: "Diffusion Models", query: "Denoising Diffusion Probabilistic Models" },
];

export function UnifiedHeroWorkspace({
  inputText,
  onChangeText,
  onSendChat,
  onIngestFile,
  onOpenPaper,
  isGenerating = false,
}: UnifiedHeroWorkspaceProps) {
  const { theme } = useTheme();
  const isDark = theme === "dark";
  const { user } = useAuthStore();

  const [mode, setMode] = useState<"search" | "chat">("search");
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<ScholarlyPaper[]>([]);
  const [filterMode, setFilterMode] = useState<"all" | "peer_reviewed">("all");
  const [searchError, setSearchError] = useState<string | null>(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const [openingPaperTitle, setOpeningPaperTitle] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const userGreetingName = user?.full_name
    ? user.full_name.split(" ").slice(-2).join(" ")
    : user?.email?.split("@")[0] || "Học giả";

  const totalCount = searchResults.length;
  const peerReviewedCount = searchResults.filter((p) => Boolean(p.is_peer_reviewed)).length;
  const displayedResults =
    filterMode === "peer_reviewed"
      ? searchResults.filter((p) => Boolean(p.is_peer_reviewed))
      : searchResults;

  const executeSearch = async (query: string) => {
    if (!query.trim()) return;
    setIsSearching(true);
    setSearchError(null);
    setFilterMode("all");
    try {
      const results = await discoveryApi.search(query.trim(), 8);
      setSearchResults(results);
    } catch {
      setSearchError("Không thể kết nối máy chủ tìm kiếm. Vui lòng thử lại sau.");
    } finally {
      setIsSearching(false);
    }
  };

  const handleSend = (textToSend?: string) => {
    const text = textToSend || inputText;
    if (!text.trim()) return;

    if (mode === "search") {
      executeSearch(text);
    } else {
      onSendChat(text);
    }
  };

  const handleChipClick = (query: string) => {
    onChangeText(query);
    setMode("search");
    executeSearch(query);
  };

  const handlePaperClick = async (paper: ScholarlyPaper) => {
    setOpeningPaperTitle(paper.title);
    try {
      await onOpenPaper(paper);
    } finally {
      setOpeningPaperTitle(null);
    }
  };

  const handleDrag = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onIngestFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onIngestFile(e.target.files[0]);
    }
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-4 sm:p-6 md:p-8 w-full max-w-4xl mx-auto my-auto relative z-10 select-none overflow-y-auto">
      {/* 1. Academic Header & Greeting (Radical Minimalism, no verbose slogans) */}
      <div className="flex flex-col items-center text-center mb-6">
        <div className="w-11 h-11 rounded-2xl bg-white dark:bg-[#24221f] border border-[#e5dfd4] dark:border-[#38332c] p-2 shadow-xs flex items-center justify-center mb-3">
          <AcademicLogo size="sm" inverted={isDark} showWordmark={false} />
        </div>
        <h1 className="font-sans text-2xl sm:text-3xl md:text-4xl tracking-tight text-ink dark:text-[#f7f5ef] font-semibold">
          Không gian nghiên cứu, {userGreetingName}
        </h1>
      </div>

      {/* 2. Mode Selector Pill Tabs */}
      <div className="flex items-center gap-1.5 p-1 rounded-full bg-[#ede8df] dark:bg-[#252320] border border-[#ded8cd] dark:border-[#35322d] mb-4">
        <button
          type="button"
          onClick={() => {
            setMode("search");
            setSearchResults([]);
          }}
          className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-medium transition-all cursor-pointer ${
            mode === "search"
              ? "bg-white dark:bg-[#1a1916] text-ink dark:text-[#f3f2ef] shadow-xs"
              : "text-muted dark:text-zinc-400 hover:text-ink dark:hover:text-zinc-200"
          }`}
        >
          <Search className="w-3.5 h-3.5" />
          <span>Tìm bài báo</span>
        </button>

        <button
          type="button"
          onClick={() => {
            setMode("chat");
            setSearchResults([]);
          }}
          className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-medium transition-all cursor-pointer ${
            mode === "chat"
              ? "bg-white dark:bg-[#1a1916] text-ink dark:text-[#f3f2ef] shadow-xs"
              : "text-muted dark:text-zinc-400 hover:text-ink dark:hover:text-zinc-200"
          }`}
        >
          <MessageSquare className="w-3.5 h-3.5" />
          <span>Đối thoại AI</span>
        </button>
      </div>

      {/* 3. Central Multi-purpose Chat / Search Input Box */}
      <div className="w-full max-w-2xl">
        <DashboardChatInputBox
          inputText={inputText}
          onChangeText={onChangeText}
          onSend={handleSend}
          isGenerating={isGenerating || isSearching}
          onUploadFile={onIngestFile}
          showReasoning={mode === "chat"}
          placeholder={
            mode === "search"
              ? "Nhập tên bài báo hoặc tác giả (ví dụ: Attention, Transformer)..."
              : "Đặt câu hỏi hoặc yêu cầu phân tích học thuật..."
          }
        />
      </div>

      {/* 4. Dynamic Content: Search Results & Skeleton Loading */}
      {isSearching && <ScholarlySkeletonList />}

      {searchError && (
        <div className="text-xs text-rose-500 py-3 text-center">{searchError}</div>
      )}

      {searchResults.length > 0 && !isSearching && (
        <div className="w-full mt-6 space-y-4">
          <div className="flex items-center justify-between text-xs text-muted dark:text-zinc-400 px-1 flex-wrap gap-2">
            {/* Pill filter toggle */}
            <div className="flex items-center gap-1 p-0.5 rounded-full bg-[#ede8df] dark:bg-[#252320] border border-[#ded8cd] dark:border-[#35322d]">
              <button
                type="button"
                onClick={() => setFilterMode("all")}
                data-testid="filter-all-btn"
                className={`px-3 py-1 rounded-full text-xs font-medium transition-all cursor-pointer ${
                  filterMode === "all"
                    ? "bg-white dark:bg-[#1a1916] text-ink dark:text-[#f3f2ef] shadow-xs"
                    : "text-muted dark:text-zinc-400 hover:text-ink dark:hover:text-zinc-200"
                }`}
              >
                Tất cả ({totalCount})
              </button>
              <button
                type="button"
                onClick={() => setFilterMode("peer_reviewed")}
                data-testid="filter-peer-reviewed-btn"
                className={`px-3 py-1 rounded-full text-xs font-medium transition-all cursor-pointer ${
                  filterMode === "peer_reviewed"
                    ? "bg-white dark:bg-[#1a1916] text-ink dark:text-[#f3f2ef] shadow-xs"
                    : "text-muted dark:text-zinc-400 hover:text-ink dark:hover:text-zinc-200"
                }`}
              >
                Đã bình duyệt ({peerReviewedCount})
              </button>
            </div>

            <button
              type="button"
              onClick={() => {
                setSearchResults([]);
                setFilterMode("all");
              }}
              className="flex items-center gap-1 hover:text-ink dark:hover:text-zinc-200 transition-colors cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
              <span>Đóng kết quả</span>
            </button>
          </div>

          {displayedResults.length === 0 ? (
            <div className="py-8 text-center text-xs text-muted dark:text-zinc-400">
              Không có bài báo đã bình duyệt trong kết quả tìm kiếm này.
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-3 max-h-[50vh] overflow-y-auto pr-1">
              {displayedResults.map((paper, idx) => (
                <ScholarlyResultCard
                  key={`${paper.title}-${idx}`}
                  paper={paper}
                  onOpenReading={handlePaperClick}
                  isLoading={openingPaperTitle === paper.title}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* 5. Two Primary Starting Actions (Shown when no search results) */}
      {searchResults.length === 0 && !isSearching && (
        <div className="w-full max-w-2xl mt-5 flex flex-col gap-3.5">
          {/* Action A: Compact PDF Upload Dropzone (Minimal, zero internal jargon) */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileInputChange}
            accept=".pdf,application/pdf"
            className="hidden"
          />

          <div
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`w-full py-3.5 px-5 rounded-2xl border border-dashed transition-all duration-200 flex items-center justify-center gap-3 cursor-pointer select-none ${
              isDragActive
                ? "border-[#cc785c] bg-[#cc785c]/10 text-[#cc785c]"
                : "border-[#ded8cd] dark:border-[#33302b] bg-white/40 dark:bg-[#1f1d1a]/40 hover:border-[#cc785c]/60 text-muted dark:text-zinc-400"
            }`}
          >
            <div className="w-7 h-7 rounded-lg bg-[#cc785c]/10 text-[#cc785c] flex items-center justify-center shrink-0">
              <FileUp className="w-3.5 h-3.5" />
            </div>
            <span className="text-xs font-medium text-ink dark:text-zinc-300">
              Kéo thả tệp PDF bài báo vào đây hoặc duyệt tệp (tối đa 50 MB)
            </span>
          </div>

          {/* Action B: Balanced Topic Chips */}
          <div className="flex flex-wrap items-center justify-center gap-2 pt-1">
            {TOPIC_CHIPS.map((chip) => (
              <button
                key={chip.label}
                type="button"
                onClick={() => handleChipClick(chip.query)}
                className="px-3.5 py-1.5 rounded-full text-xs font-medium border border-[#ded8cd] dark:border-[#35322d] bg-white dark:bg-[#201e1a] text-ink dark:text-zinc-300 hover:border-[#cc785c] hover:text-[#cc785c] transition-all cursor-pointer shadow-2xs"
              >
                {chip.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
