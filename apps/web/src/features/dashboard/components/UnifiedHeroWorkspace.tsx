import { useState, useRef, useMemo, useCallback, useEffect } from "react";
import { Search, Sparkles, X, ChevronLeft, ChevronRight } from "lucide-react";
import { AcademicLogo } from "@/components/shared/AcademicLogo";
import { useTheme } from "@/hooks/useTheme";
import { DashboardChatInputBox } from "./DashboardChatInputBox";
import { ScholarlyResultCard } from "@/features/discovery/components/ScholarlyResultCard";
import { ScholarlySkeletonList } from "@/features/discovery/components/ScholarlySkeletonList";
import { discoveryApi, type ScholarlyPaper } from "@/features/discovery/api/discoveryApi";
import { parseScholarlyInput } from "@/features/discovery/lib/urlGuardrail";
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

  const [mode, setMode] = useState<"search" | "chat">("search");
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<ScholarlyPaper[]>([]);
  const [filterMode, setFilterMode] = useState<"all" | "peer_reviewed">("all");
  const [searchError, setSearchError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [openingPaperTitle, setOpeningPaperTitle] = useState<string | null>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);
  const carouselRef = useRef<HTMLDivElement>(null);

  const updateScrollButtons = useCallback(() => {
    const el = carouselRef.current;
    if (!el) return;
    const { scrollLeft, scrollWidth, clientWidth } = el;
    setCanScrollLeft(scrollLeft > 5);
    setCanScrollRight(scrollLeft + clientWidth < scrollWidth - 5);
  }, []);

  const scrollCarousel = (direction: "left" | "right") => {
    carouselRef.current?.scrollBy?.({
      left: direction === "left" ? -380 : 380,
      behavior: "smooth",
    });
  };

  const totalCount = searchResults.length;
  const peerReviewedCount = searchResults.filter((p) => Boolean(p.is_peer_reviewed)).length;
  const displayedResults = useMemo(() => {
    const list =
      filterMode === "peer_reviewed"
        ? searchResults.filter((p) => Boolean(p.is_peer_reviewed))
        : searchResults;
    // Academic Priority Re-ranking: Prioritize peer-reviewed papers at top
    return [...list].sort((a, b) => {
      if (a.is_peer_reviewed && !b.is_peer_reviewed) return -1;
      if (!a.is_peer_reviewed && b.is_peer_reviewed) return 1;
      return (b.publication_year || 0) - (a.publication_year || 0);
    });
  }, [searchResults, filterMode]);

  useEffect(() => {
    updateScrollButtons();
    const el = carouselRef.current;
    if (!el) return;

    const frameId = requestAnimationFrame(updateScrollButtons);
    el.addEventListener("scroll", updateScrollButtons, { passive: true });
    window.addEventListener("resize", updateScrollButtons);

    return () => {
      cancelAnimationFrame(frameId);
      el.removeEventListener("scroll", updateScrollButtons);
      window.removeEventListener("resize", updateScrollButtons);
    };
  }, [displayedResults, updateScrollButtons]);

  const handleResetSearch = () => {
    setSearchResults([]);
    setHasSearched(false);
    setSearchError(null);
    setFilterMode("all");
    setCanScrollLeft(false);
    setCanScrollRight(false);
    onChangeText("");
  };

  const executeSearch = async (query: string) => {
    const raw = query.trim();
    if (!raw) return;

    const parsed = parseScholarlyInput(raw);
    if (parsed.type === "invalid_url") {
      setSearchError(parsed.message);
      setSearchResults([]);
      setHasSearched(false);
      return;
    }

    setIsSearching(true);
    setSearchError(null);
    setFilterMode("all");

    const searchQuery =
      parsed.type === "scholarly_url" ? parsed.identifier : parsed.query;

    try {
      const results = await discoveryApi.search(searchQuery, 8);
      setSearchResults(results);
      setHasSearched(true);
    } catch {
      setSearchError("Không thể kết nối máy chủ tìm kiếm. Vui lòng thử lại sau.");
      setHasSearched(true);
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

  const hasActiveContent =
    isSearching ||
    searchResults.length > 0 ||
    (hasSearched && searchResults.length === 0 && !searchError);

  return (
    <div
      className={`flex-1 flex flex-col items-center p-4 sm:p-6 md:p-8 w-full ${
        searchResults.length > 0 ? "max-w-5xl" : "max-w-4xl"
      } mx-auto relative z-10 select-none overflow-y-auto scrollbar-none transition-all duration-300 ${
        hasActiveContent
          ? "justify-start pt-6 sm:pt-10 my-0"
          : "justify-center my-auto"
      }`}
    >
      {/* 1. Academic Header & Workspace (Radical Minimalism, Rule Item 4) */}
      <div className="flex flex-col items-center text-center mb-6">
        <div className="w-11 h-11 rounded-2xl bg-white dark:bg-[#24221f] border border-[#e5dfd4] dark:border-[#38332c] p-2 shadow-xs flex items-center justify-center mb-3">
          <AcademicLogo size="sm" inverted={isDark} showWordmark={false} />
        </div>
        <h1 className="font-sans text-2xl sm:text-3xl md:text-4xl tracking-tight text-ink dark:text-[#f7f5ef] font-semibold">
          Workspace
        </h1>
      </div>

      {/* 2. Mode Selector Pill Tabs (Rule Item 6: "Nghiên cứu") */}
      <div className="flex items-center gap-1.5 p-1 rounded-full bg-[#ede8df] dark:bg-[#252320] border border-[#ded8cd] dark:border-[#35322d] mb-4">
        <button
          type="button"
          onClick={() => {
            setMode("search");
            handleResetSearch();
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
            handleResetSearch();
          }}
          className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-medium transition-all cursor-pointer ${
            mode === "chat"
              ? "bg-white dark:bg-[#1a1916] text-ink dark:text-[#f3f2ef] shadow-xs"
              : "text-muted dark:text-zinc-400 hover:text-ink dark:hover:text-zinc-200"
          }`}
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Nghiên cứu</span>
        </button>
      </div>

      {/* 3. Central Multi-purpose Chat / Search Input Box */}
      <div className="w-full max-w-2xl">
        <DashboardChatInputBox
          mode={mode}
          inputText={inputText}
          onChangeText={onChangeText}
          onSend={handleSend}
          isGenerating={isGenerating || isSearching}
          onUploadFile={onIngestFile}
          showReasoning={mode === "chat"}
          placeholder={
            mode === "search"
              ? "Tìm kiếm bài báo khoa học theo tiêu đề, tác giả, DOI hoặc arXiv ID..."
              : "Đặt câu hỏi nghiên cứu, kéo thả PDF hoặc yêu cầu tóm tắt..."
          }
        />
      </div>

      {/* 4. Dynamic Content: Search Results & Skeleton Loading */}
      {isSearching && <ScholarlySkeletonList />}

      {searchError && (
        <div className="text-xs text-rose-500 py-3 text-center">{searchError}</div>
      )}

      {/* 4b. Empty State Feedback */}
      {hasSearched && searchResults.length === 0 && !isSearching && !searchError && (
        <div className="w-full max-w-md my-8 flex flex-col items-center justify-center text-center p-6 rounded-2xl border border-[#ded8cd] dark:border-[#35322d] bg-white/60 dark:bg-[#201e1a]/60">
          <p className="text-sm text-muted dark:text-zinc-400 mb-4">
            Không tìm thấy bài báo phù hợp với yêu cầu này.
          </p>
          <button
            type="button"
            onClick={handleResetSearch}
            className="px-4 py-1.5 rounded-full text-xs font-medium bg-[#cc785c] hover:bg-[#b8684e] text-white transition-all cursor-pointer shadow-xs"
          >
            Làm mới
          </button>
        </div>
      )}

      {searchResults.length > 0 && !isSearching && (
        <div className="w-full mt-6 space-y-3 pb-8">
          <div className="flex items-center justify-between text-xs text-muted dark:text-zinc-400 px-1 flex-wrap gap-2 mb-2">
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
              onClick={handleResetSearch}
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
            <div className="relative w-full mt-2">
              {/* Left Navigation Arrow */}
              {canScrollLeft && (
                <button
                  type="button"
                  onClick={() => scrollCarousel("left")}
                  data-testid="carousel-prev-btn"
                  aria-label="Cuộn sang trái"
                  className="absolute -left-3 top-1/2 -translate-y-1/2 z-20 w-8 h-8 rounded-full bg-white/90 dark:bg-[#201e1a]/90 backdrop-blur-xs border border-[#ded8cd] dark:border-[#35322d] shadow-md flex items-center justify-center text-ink dark:text-zinc-200 hover:bg-zinc-50 dark:hover:bg-[#2a2723] transition-all cursor-pointer"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
              )}

              {/* Horizontal Snap Rail */}
              <div
                ref={carouselRef}
                onScroll={updateScrollButtons}
                data-testid="scholarly-carousel-track"
                className="flex gap-4 overflow-x-auto scrollbar-none snap-x snap-mandatory py-2 px-1"
              >
                {displayedResults.map((paper, idx) => (
                  <div
                    key={`${paper.title}-${idx}`}
                    data-testid="scholarly-carousel-item"
                    className="w-[320px] sm:w-[380px] shrink-0 snap-start flex flex-col"
                  >
                    <ScholarlyResultCard
                      paper={paper}
                      onOpenReading={handlePaperClick}
                      isLoading={openingPaperTitle === paper.title}
                    />
                  </div>
                ))}
              </div>

              {/* Right Navigation Arrow */}
              {canScrollRight && (
                <button
                  type="button"
                  onClick={() => scrollCarousel("right")}
                  data-testid="carousel-next-btn"
                  aria-label="Cuộn sang phải"
                  className="absolute -right-3 top-1/2 -translate-y-1/2 z-20 w-8 h-8 rounded-full bg-white/90 dark:bg-[#201e1a]/90 backdrop-blur-xs border border-[#ded8cd] dark:border-[#35322d] shadow-md flex items-center justify-center text-ink dark:text-zinc-200 hover:bg-zinc-50 dark:hover:bg-[#2a2723] transition-all cursor-pointer"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              )}
            </div>
          )}
        </div>
      )}

      {/* 5. Scholarly Topic Exploration Chips (Rule Item 9: standalone dropzone removed) */}
      {searchResults.length === 0 && !isSearching && !hasSearched && (
        <div className="w-full max-w-2xl mt-4 flex flex-wrap items-center justify-center gap-2">
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
      )}
    </div>
  );
}
