import { useState, useRef, type DragEvent, type ChangeEvent } from "react";
import { Search, MessageSquare, FileUp, Sparkles, X, Loader2 } from "lucide-react";
import { AcademicLogo } from "@/components/shared/AcademicLogo";
import { useAuthStore } from "@/features/auth/stores/useAuthStore";
import { useTheme } from "@/hooks/useTheme";
import { DashboardChatInputBox } from "./DashboardChatInputBox";
import { ScholarlyResultCard } from "@/features/discovery/components/ScholarlyResultCard";
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
  const [searchError, setSearchError] = useState<string | null>(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const [openingPaperTitle, setOpeningPaperTitle] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const userGreetingName = user?.full_name
    ? user.full_name.split(" ").slice(-2).join(" ")
    : user?.email?.split("@")[0] || "Học giả";

  const executeSearch = async (query: string) => {
    if (!query.trim()) return;
    setIsSearching(true);
    setSearchError(null);
    try {
      const results = await discoveryApi.search(query.trim(), 8);
      setSearchResults(results);
    } catch {
      setSearchError("Không thể tìm kiếm bài báo lúc này. Vui lòng thử lại sau.");
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
      {/* 1. Header & Greeting */}
      <div className="flex flex-col items-center text-center mb-6">
        <div className="w-12 h-12 rounded-2xl bg-white dark:bg-[#24221f] border border-[#e5dfd4] dark:border-[#38332c] p-2.5 shadow-xs flex items-center justify-center mb-3">
          <AcademicLogo size="sm" inverted={isDark} showWordmark={false} />
        </div>
        <h1 className="font-sans text-2xl sm:text-3xl md:text-4xl tracking-tight text-ink dark:text-[#f7f5ef] font-semibold">
          Không gian nghiên cứu, {userGreetingName}
        </h1>
        <p className="text-xs sm:text-sm text-muted dark:text-zinc-400 mt-1 max-w-md font-sans">
          Tìm kiếm bài báo học thuật, phân tích PDF hoặc đối thoại suy luận cùng AI.
        </p>
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
          placeholder={
            mode === "search"
              ? "Nhập tên bài báo, tác giả hoặc từ khóa (ví dụ: Attention, Transformer)..."
              : "Đặt câu hỏi hoặc yêu cầu phân tích học thuật (chọn độ sâu suy luận ở nút trên)..."
          }
        />
      </div>

      {/* 4. Dynamic Content: Search Results OR Starting Actions */}
      {isSearching && (
        <div className="flex items-center justify-center gap-2 py-8 text-sm text-muted dark:text-zinc-400">
          <Loader2 className="w-4 h-4 animate-spin text-[#cc785c]" />
          <span>Đang tìm kiếm bài báo trên các kho học thuật mở...</span>
        </div>
      )}

      {searchError && (
        <div className="text-xs text-rose-500 py-3 text-center">{searchError}</div>
      )}

      {searchResults.length > 0 && !isSearching && (
        <div className="w-full mt-6 space-y-4">
          <div className="flex items-center justify-between text-xs text-muted dark:text-zinc-400 px-1">
            <span>Tìm thấy {searchResults.length} bài báo khoa học phù hợp:</span>
            <button
              type="button"
              onClick={() => setSearchResults([])}
              className="flex items-center gap-1 hover:text-ink dark:hover:text-zinc-200 transition-colors cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
              <span>Đóng kết quả</span>
            </button>
          </div>

          <div className="grid grid-cols-1 gap-3 max-h-[50vh] overflow-y-auto pr-1">
            {searchResults.map((paper, idx) => (
              <ScholarlyResultCard
                key={`${paper.title}-${idx}`}
                paper={paper}
                onOpenReading={handlePaperClick}
                isLoading={openingPaperTitle === paper.title}
              />
            ))}
          </div>
        </div>
      )}

      {/* 5. Two Primary Starting Actions (Shown when no search results) */}
      {searchResults.length === 0 && !isSearching && (
        <div className="w-full max-w-2xl mt-6 flex flex-col gap-4">
          {/* Action A: Compact PDF Upload Dropzone */}
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
            className={`w-full py-4 px-6 rounded-2xl border border-dashed transition-all duration-200 flex items-center justify-center gap-3 cursor-pointer select-none ${
              isDragActive
                ? "border-[#cc785c] bg-[#cc785c]/10 text-[#cc785c]"
                : "border-[#e0d9cd] dark:border-[#33302b] bg-white/50 dark:bg-[#1f1d1a]/50 hover:border-[#cc785c]/50 text-muted dark:text-zinc-400"
            }`}
          >
            <div className="w-8 h-8 rounded-xl bg-[#cc785c]/10 text-[#cc785c] flex items-center justify-center shrink-0">
              <FileUp className="w-4 h-4" />
            </div>
            <div className="flex flex-col text-left">
              <span className="text-xs font-semibold text-ink dark:text-zinc-200">
                Kéo thả tệp PDF bài báo vào đây hoặc duyệt tệp
              </span>
              <span className="text-[11px] text-muted dark:text-zinc-400">
                Hỗ trợ tệp PDF học thuật tới 50 MB, tự động bóc tách 2 cột và lưu trữ CAS
              </span>
            </div>
          </div>

          {/* Action B: Topic Chips Grid */}
          <div className="flex flex-wrap items-center justify-center gap-2 pt-1">
            <span className="text-[11px] font-medium text-muted dark:text-zinc-400 flex items-center gap-1 mr-1">
              <Sparkles className="w-3 h-3 text-[#cc785c]" />
              <span>Gợi ý chủ đề:</span>
            </span>
            {TOPIC_CHIPS.map((chip) => (
              <button
                key={chip.label}
                type="button"
                onClick={() => handleChipClick(chip.query)}
                className="px-3 py-1 rounded-full text-xs font-medium border border-[#ded8cd] dark:border-[#35322d] bg-white dark:bg-[#201e1a] text-ink dark:text-zinc-300 hover:border-[#cc785c] hover:text-[#cc785c] transition-all cursor-pointer shadow-2xs"
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
