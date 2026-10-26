import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Search,
  Compass,
  Upload,
  Loader2,
  Sparkles,
  AlertCircle,
  FileSearch,
} from "lucide-react";
import { DashboardTaskbar } from "@/features/dashboard/components/DashboardTaskbar";
import { MobileDashboardHeader } from "@/features/dashboard/components/MobileDashboardHeader";
import { useDashboardStore } from "@/features/dashboard/stores/useDashboardStore";
import { useDashboardSessions } from "@/features/dashboard/hooks/useDashboardSessions";
import { discoveryApi, type ScholarlyPaper } from "../api/discoveryApi";
import { ScholarlyResultCard } from "./ScholarlyResultCard";
import { DocumentUploadModal } from "@/features/documents/components/DocumentUploadModal";

const SUGGESTED_TOPICS = [
  "Direct Preference Optimization",
  "Transformer language models",
  "Retrieval Augmented Generation",
  "Deep Learning in Bioinformatics",
];

export function DiscoveryPage() {
  const navigate = useNavigate();
  const toggleSidebar = useDashboardStore((s) => s.toggleSidebar);
  const { sessions } = useDashboardSessions();

  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<ScholarlyPaper[]>([]);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [openingPaperTitle, setOpeningPaperTitle] = useState<string | null>(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  const handleSearch = async (queryToSearch?: string) => {
    const q = (queryToSearch ?? searchQuery).trim();
    if (!q) return;

    if (queryToSearch) {
      setSearchQuery(queryToSearch);
    }

    setIsSearching(true);
    setSearchError(null);

    try {
      const results = await discoveryApi.search(q, 10);
      setSearchResults(results);
    } catch (err) {
      setSearchResults([]);
      setSearchError(
        err instanceof Error ? err.message : "Không thể tải kết quả tìm kiếm. Vui lòng thử lại."
      );
    } finally {
      setIsSearching(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSearch();
  };

  const handleOpenReading = async (paper: ScholarlyPaper) => {
    try {
      setOpeningPaperTitle(paper.title);
      setSearchError(null);
      const res = await discoveryApi.openReading({
        title: paper.title,
        authors: paper.authors,
        publication_year: paper.publication_year,
        doi: paper.doi,
        arxiv_id: paper.arxiv_id,
        abstract: paper.abstract,
        pdf_url: paper.pdf_url,
      });

      if (res?.session_id) {
        navigate(`/dashboard/${res.session_id}`);
      }
    } catch (err) {
      setSearchError(
        err instanceof Error
          ? err.message
          : "Không thể khởi tạo phiên đọc từ bài báo này. Vui lòng thử lại."
      );
    } finally {
      setOpeningPaperTitle(null);
    }
  };

  return (
    <div className="h-screen w-screen flex bg-[#fdfcf9] dark:bg-[#181715] text-ink dark:text-[#f3f2ef] overflow-hidden select-none">
      {/* 1. Left Navigation Taskbar */}
      <DashboardTaskbar
        sessions={sessions}
        onSelectSession={(id) => navigate(`/dashboard/${id}`)}
        onNewSession={() => navigate("/dashboard")}
      />

      {/* 2. Main Content Area */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative">
        <MobileDashboardHeader
          onToggleSidebar={toggleSidebar}
          onNewSession={() => navigate("/dashboard")}
        />

        {/* Top Header */}
        <header className="h-14 px-6 border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#fdfcf9] dark:bg-[#1c1b18] flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-coral-500/10 text-coral-600 dark:text-coral-400 flex items-center justify-center">
              <Compass className="w-4 h-4 stroke-[2]" />
            </div>
            <div>
              <h1 className="text-sm font-semibold font-anthropic-serif text-ink dark:text-zinc-100 flex items-center gap-2">
                Khám phá Đề tài & Bài báo
                {searchResults.length > 0 && (
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-zinc-100 dark:bg-zinc-800 text-muted dark:text-zinc-400 font-normal">
                    {searchResults.length} kết quả
                  </span>
                )}
              </h1>
              <p className="text-[11px] text-muted dark:text-zinc-400 font-sans">
                Tìm kiếm bài báo mở và bắt đầu phiên nghiên cứu chỉ với một cú nhấp
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setIsUploadModalOpen(true)}
              className="h-8 px-3 rounded-lg text-xs font-medium border border-hairline bg-white dark:bg-[#252320] text-ink dark:text-zinc-200 hover:border-zinc-400 flex items-center gap-1.5 transition-colors cursor-pointer"
            >
              <Upload className="w-3.5 h-3.5 text-muted" />
              <span>Tải lên PDF</span>
            </button>
          </div>
        </header>

        {/* Search Bar Area */}
        <div className="px-6 py-4 border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#f8f6f0] dark:bg-[#1a1916] shrink-0">
          <form onSubmit={handleSubmit} className="max-w-3xl mx-auto flex items-center gap-2">
            <div className="flex-1 relative">
              <Search className="w-4 h-4 text-muted absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleSearch();
                  }
                }}
                placeholder="Tìm kiếm bài báo học thuật theo chủ đề, tiêu đề, DOI hoặc arXiv ID..."
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white dark:bg-[#22201c] border border-hairline text-xs outline-none focus:border-coral-500 text-ink dark:text-zinc-100 font-sans shadow-xs transition-all"
              />
            </div>
            <button
              type="submit"
              disabled={isSearching || !searchQuery.trim()}
              className="h-10 px-5 rounded-xl text-xs font-medium flex items-center gap-2 bg-ink dark:bg-white text-white dark:text-black hover:opacity-90 disabled:opacity-50 transition-colors cursor-pointer shrink-0 shadow-xs"
            >
              {isSearching ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Đang tìm...</span>
                </>
              ) : (
                <>
                  <Search className="w-3.5 h-3.5" />
                  <span>Tìm kiếm</span>
                </>
              )}
            </button>
          </form>

          {/* Quick Topics */}
          <div className="max-w-3xl mx-auto flex items-center gap-2 pt-3 flex-wrap text-[11px] text-muted">
            <span className="flex items-center gap-1 font-medium">
              <Sparkles className="w-3 h-3 text-coral-600" /> Gợi ý:
            </span>
            {SUGGESTED_TOPICS.map((topic) => (
              <button
                key={topic}
                type="button"
                onClick={() => handleSearch(topic)}
                className="px-2.5 py-1 rounded-md bg-white dark:bg-[#24221e] border border-hairline hover:border-zinc-400 text-zinc-700 dark:text-zinc-300 transition-colors cursor-pointer font-sans"
              >
                {topic}
              </button>
            ))}
          </div>
        </div>

        {/* Results Container */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-4xl mx-auto space-y-4">
            {searchError && (
              <div
                role="alert"
                className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-xs flex items-center gap-2 font-sans"
              >
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{searchError}</span>
              </div>
            )}

            {isSearching ? (
              <div className="py-20 flex flex-col items-center justify-center text-muted space-y-3">
                <Loader2 className="w-8 h-8 animate-spin text-coral-600" />
                <p className="text-xs font-sans">
                  Đang truy vấn các cơ sở dữ liệu học thuật mở...
                </p>
              </div>
            ) : searchResults.length === 0 ? (
              <div className="py-20 text-center text-xs text-muted space-y-3">
                <FileSearch className="w-10 h-10 mx-auto text-zinc-400 stroke-[1.5]" />
                <p className="font-sans">
                  Nhập từ khóa nghiên cứu, tiêu đề hoặc mã định danh DOI/arXiv để khám phá bài báo.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {searchResults.map((paper, idx) => (
                  <ScholarlyResultCard
                    key={paper.doi || paper.arxiv_id || `${paper.title}-${idx}`}
                    paper={paper}
                    onOpenReading={handleOpenReading}
                    isLoading={openingPaperTitle === paper.title}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* PDF Upload Modal */}
      <DocumentUploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onUploadSuccess={() => {
          navigate("/dashboard");
        }}
      />
    </div>
  );
}
