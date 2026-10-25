import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Search,
  ExternalLink,
  Plus,
  Loader2,
  Compass,
} from "lucide-react";
import { DashboardTaskbar } from "@/features/dashboard/components/DashboardTaskbar";
import { MobileDashboardHeader } from "@/features/dashboard/components/MobileDashboardHeader";
import { useDashboardStore } from "@/features/dashboard/stores/useDashboardStore";
import { useDashboardSessions } from "@/features/dashboard/hooks/useDashboardSessions";
import { useDocumentsList } from "@/features/documents/hooks/useDocumentQueries";
import { sessionsApi } from "@/features/sessions/api/sessionsApi";
import { documentsApi } from "@/features/documents/api/documentsApi";
import type { ResolvedReferenceCard } from "@/features/reader/types/reference";

export function DiscoveryPage() {
  const navigate = useNavigate();
  const toggleSidebar = useDashboardStore((s) => s.toggleSidebar);
  const { sessions } = useDashboardSessions();
  const { data: documentsData } = useDocumentsList({ page: 1, per_page: 50 });

  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSessionId, setSelectedSessionId] = useState<string>("");

  const effectiveSessionId = selectedSessionId || sessions[0]?.id || "";

  const [resolverError, setResolverError] = useState<string | null>(null);
  const [isResolving, setIsResolving] = useState(false);
  const [resolvedRefs, setResolvedRefs] = useState<ResolvedReferenceCard[]>([]);

  const handleSearchResolver = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const query = searchQuery.trim();
    if (!query) return;

    setIsResolving(true);
    setResolverError(null);
    const docMatch = documentsData?.data?.find(
      (d) =>
        d.title?.toLowerCase().includes(query.toLowerCase()) ||
        d.filename.toLowerCase().includes(query.toLowerCase())
    );

    if (docMatch) {
      try {
        const refs = await documentsApi.resolveReferences(docMatch.id);
        setResolvedRefs(refs);
      } catch (error) {
        setResolvedRefs([]);
        setResolverError(error instanceof Error ? error.message : "Unable to resolve references.");
      } finally {
        setIsResolving(false);
      }
    } else {
      setResolvedRefs([]);
      setResolverError("No matching document was found in this workspace.");
      setIsResolving(false);
    }
  };

  return (
    <div className="h-screen w-screen flex bg-[#fdfcf9] dark:bg-[#181715] text-ink dark:text-[#f3f2ef] overflow-hidden select-none">
      {/* 1. Left Navigation Taskbar */}
      <DashboardTaskbar
        sessions={sessions}
        onSelectSession={(id) => {
          setSelectedSessionId(id);
          navigate(`/dashboard/${id}`);
        }}
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
                Discovery
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-zinc-100 dark:bg-zinc-800 text-muted dark:text-zinc-400 font-normal">
                  {resolvedRefs.length} results
                </span>
              </h1>
              <p className="text-[11px] text-muted dark:text-zinc-400 font-sans">
                Academic Paper Discovery & Reference Resolvers
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Session Selector */}
            <select
              value={effectiveSessionId}
              onChange={(e) => setSelectedSessionId(e.target.value)}
              className="px-2.5 py-1.5 rounded-lg bg-[#f4eee2] dark:bg-[#252320] border border-hairline text-xs text-ink dark:text-zinc-200 outline-none cursor-pointer max-w-[200px] truncate"
            >
              {sessions.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.title}
                </option>
              ))}
            </select>
          </div>
        </header>

        {/* Search & Navigation Bar */}
        <div className="px-6 py-2.5 border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#f8f6f0] dark:bg-[#1a1916] flex flex-wrap items-center justify-between gap-3 shrink-0">
          {/* DOI / arXiv Search input */}
          <form onSubmit={handleSearchResolver} className="flex-1 max-w-md flex items-center gap-2">
            <div className="flex-1 relative">
              <Search className="w-3.5 h-3.5 text-muted absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search DOI, arXiv ID, or paper title..."
                className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-white dark:bg-[#22201c] border border-hairline text-xs outline-none focus:border-coral-500 text-ink dark:text-zinc-100 font-mono shadow-xs"
              />
            </div>
            <button
              type="submit"
              disabled={isResolving || !searchQuery.trim()}
              className="h-8 px-3 rounded-lg text-xs font-medium flex items-center gap-1.5 bg-ink dark:bg-white text-white dark:text-black hover:opacity-90 disabled:opacity-50 transition-colors cursor-pointer shrink-0"
            >
              {isResolving ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <Search className="w-3.5 h-3.5" />
                  <span>Search</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex overflow-hidden">
          <div className="flex-1 p-6 overflow-y-auto max-w-5xl mx-auto space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-semibold font-mono text-muted uppercase tracking-wider">
                Academic Resolvers (Crossref, arXiv, S2)
              </h3>
              <span className="text-xs font-mono text-muted">
                {resolvedRefs.length} results
              </span>
            </div>

            {resolverError && (
              <p role="alert" className="text-xs text-rose-600 dark:text-rose-400 font-sans">
                {resolverError}
              </p>
            )}

            {resolvedRefs.length === 0 ? (
              <div className="py-16 text-center text-xs text-muted space-y-3">
                <Compass className="w-8 h-8 mx-auto text-zinc-400 stroke-[1.5]" />
                <p>No papers resolved yet. Enter a DOI, arXiv ID, or paper title in the search bar above.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {resolvedRefs.map((ref) => (
                  <div
                    key={ref.ref_index}
                    className="p-4 rounded-xl border border-hairline bg-white dark:bg-[#1c1b18] flex items-start justify-between gap-4 shadow-xs"
                  >
                    <div className="space-y-1">
                      <div className="font-semibold text-xs text-ink dark:text-zinc-100 font-anthropic-serif">
                        {ref.title}
                      </div>
                      <div className="text-[11px] text-muted dark:text-zinc-400">
                        {ref.authors?.join(", ")} ({ref.year ?? "N/A"})
                      </div>
                      <div className="flex items-center gap-2 text-[10px] font-mono text-muted pt-1">
                        {ref.doi && <span>DOI: {ref.doi}</span>}
                        {ref.arxiv_id && <span>arXiv: {ref.arxiv_id}</span>}
                        {ref.sources?.map((s) => (
                          <span
                            key={s}
                            className="px-1.5 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400"
                          >
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      {ref.open_access_pdf_url && (
                        <a
                          href={ref.open_access_pdf_url}
                          target="_blank"
                          rel="noreferrer"
                          className="h-8 px-2.5 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-500/20 flex items-center gap-1 transition-colors"
                        >
                          <ExternalLink className="w-3 h-3" />
                          <span>PDF</span>
                        </a>
                      )}
                      <button
                        type="button"
                        onClick={() => {
                          if (ref.resolved_document_id && effectiveSessionId) {
                            sessionsApi.addDocumentToSession(effectiveSessionId, {
                              source_type: "document_id",
                              document_id: ref.resolved_document_id,
                            });
                          }
                          navigate("/dashboard");
                        }}
                        className="h-8 px-3 rounded-lg text-xs font-medium bg-ink dark:bg-white text-white dark:text-black hover:opacity-90 flex items-center gap-1 cursor-pointer transition-colors"
                      >
                        <Plus className="w-3 h-3" />
                        <span>Read</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
