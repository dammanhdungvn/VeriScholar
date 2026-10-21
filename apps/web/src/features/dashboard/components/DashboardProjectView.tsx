import { useState, useMemo } from "react";
import {
  Folder,
  Share2,
  MessageSquare,
  Plus,
  Search,
  FileText,
  CheckCircle2,
  Calendar,
  ArrowRight,
  Check
} from "lucide-react";
import { useDashboardSessions } from "../hooks/useDashboardSessions";
import { useDocumentsList } from "@/features/documents/hooks/useDocumentQueries";
import { useDashboardStore } from "../stores/useDashboardStore";
import { cn } from "@/lib/utils";

interface DashboardProjectViewProps {
  onNewSession?: () => void;
  onSelectSession?: (sessionId: string) => void;
  onSelectDocument?: (docId: string) => void;
}

type ProjectSubTab = "sessions" | "sources";

export function DashboardProjectView({
  onNewSession,
  onSelectSession,
  onSelectDocument,
}: DashboardProjectViewProps) {
  const setAppMode = useDashboardStore((s) => s.setAppMode);
  const { sessions, selectSession } = useDashboardSessions();
  const { data: documentsData } = useDocumentsList({ page: 1, per_page: 20 });

  const [activeSubTab, setActiveSubTab] = useState<ProjectSubTab>("sessions");
  const [searchQuery, setSearchQuery] = useState("");
  const [copiedShare, setCopiedShare] = useState(false);

  const documents = useMemo(() => documentsData?.data || [], [documentsData]);

  const filteredSessions = useMemo(() => {
    if (!searchQuery.trim()) return sessions;
    const q = searchQuery.toLowerCase();
    return sessions.filter((s) => s.title.toLowerCase().includes(q));
  }, [sessions, searchQuery]);

  const filteredDocs = useMemo(() => {
    if (!searchQuery.trim()) return documents;
    const q = searchQuery.toLowerCase();
    return documents.filter(
      (d) =>
        (d.title ? d.title.toLowerCase().includes(q) : false) ||
        d.filename.toLowerCase().includes(q)
    );
  }, [documents, searchQuery]);

  const handleShare = () => {
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(window.location.href);
      setCopiedShare(true);
      setTimeout(() => setCopiedShare(false), 2500);
    }
  };

  const handleOpenSession = (sessionId: string) => {
    if (onSelectSession) {
      onSelectSession(sessionId);
    } else {
      selectSession(sessionId);
      setAppMode("chat");
    }
  };

  const handleCreateNewProjectSession = () => {
    if (onNewSession) {
      onNewSession();
    }
    setAppMode("chat");
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#fbf9f5] dark:bg-[#181715] overflow-hidden select-none">
      {/* 1. Project Top Header */}
      <header className="h-14 px-6 border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#fdfcf9] dark:bg-[#1c1b18] flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-stone-500/10 dark:bg-stone-500/20 flex items-center justify-center text-stone-700 dark:text-stone-300">
            <Folder className="w-4 h-4 fill-current/20 stroke-[2]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-semibold font-anthropic-serif text-ink dark:text-zinc-100">
                VeriScholar
              </h1>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-medium bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20">
                Active Project
              </span>
            </div>
            <p className="text-[11px] text-muted dark:text-zinc-400">
              Research workspace & document synthesis
            </p>
          </div>
        </div>

        {/* Share Button */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleShare}
            className="h-8 px-3 rounded-lg text-xs font-medium flex items-center gap-1.5 bg-[#ece8df] dark:bg-[#282623] hover:bg-[#e2dcd2] dark:hover:bg-[#322f2b] text-ink dark:text-zinc-200 transition-colors cursor-pointer shadow-xs"
            title="Share Project"
          >
            {copiedShare ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 stroke-[2.5]" />
                <span className="text-emerald-700 dark:text-emerald-400 font-semibold">Copied</span>
              </>
            ) : (
              <>
                <Share2 className="w-3.5 h-3.5 text-[#c15f3e]" />
                <span>Share</span>
              </>
            )}
          </button>
        </div>
      </header>

      {/* 2. Navigation Ribbon: Chats & Sources */}
      <div className="px-6 py-2 border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#f8f6f0] dark:bg-[#1a1916] flex items-center justify-between shrink-0">
        <div className="flex items-center gap-1 text-xs font-medium">
          <button
            type="button"
            onClick={() => setActiveSubTab("sessions")}
            className={cn(
              "px-3 py-1 rounded-lg flex items-center gap-1.5 transition-all cursor-pointer",
              activeSubTab === "sessions"
                ? "bg-white dark:bg-[#24221e] text-ink dark:text-zinc-100 font-semibold shadow-xs border border-[#e2dcd2] dark:border-[#33302b]"
                : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200"
            )}
          >
            <MessageSquare className="w-3.5 h-3.5 stroke-[2]" />
            <span>Chats ({sessions.length})</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveSubTab("sources")}
            className={cn(
              "px-3 py-1 rounded-lg flex items-center gap-1.5 transition-all cursor-pointer",
              activeSubTab === "sources"
                ? "bg-white dark:bg-[#24221e] text-ink dark:text-zinc-100 font-semibold shadow-xs border border-[#e2dcd2] dark:border-[#33302b]"
                : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200"
            )}
          >
            <FileText className="w-3.5 h-3.5 stroke-[2]" />
            <span>Sources ({documents.length})</span>
          </button>
        </div>
      </div>

      {/* 3. Tab Body Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-6 max-w-5xl mx-auto space-y-6">
            {/* Action Bar & Search */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              {activeSubTab === "sessions" ? (
                <button
                  type="button"
                  onClick={handleCreateNewProjectSession}
                  className="h-8 px-3.5 rounded-lg text-xs font-medium text-white bg-[#c15f3e] hover:bg-[#a84f32] transition-colors shadow-xs flex items-center gap-1.5 cursor-pointer w-fit"
                >
                  <Plus className="w-3.5 h-3.5 stroke-[2.5]" />
                  <span>+ New Chat</span>
                </button>
              ) : (
                <div className="text-xs font-medium text-muted dark:text-zinc-400">
                  Project Sources
                </div>
              )}

              {/* Search input */}
              <div className="relative w-full sm:w-64">
                <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-muted dark:text-zinc-500 pointer-events-none" />
                <input
                  type="text"
                  placeholder={
                    activeSubTab === "sessions"
                      ? "Search chats..."
                      : "Search sources..."
                  }
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full h-8 pl-8 pr-3 rounded-lg bg-white dark:bg-[#201e1a] border border-[#e2dcd2] dark:border-[#322f2a] text-xs text-ink dark:text-zinc-100 placeholder:text-muted dark:placeholder:text-zinc-500 outline-none focus:border-[#c15f3e] transition-colors"
                />
              </div>
            </div>

            {/* SubTab 1: Chats (Sessions List) */}
            {activeSubTab === "sessions" && (
              <div className="space-y-3">
                {filteredSessions.length === 0 ? (
                  <div className="p-12 text-center rounded-2xl border border-dashed border-[#e2dcd2] dark:border-[#2e2b26] bg-[#f8f6f0]/50 dark:bg-[#1a1916]/50">
                    <MessageSquare className="w-8 h-8 text-muted dark:text-zinc-600 mx-auto mb-2" />
                    <p className="text-sm font-anthropic-serif font-semibold text-ink dark:text-zinc-200">
                      No chats in project
                    </p>
                    <p className="text-xs text-muted dark:text-zinc-400 mt-1 max-w-sm mx-auto">
                      Start a new chat to explore, critique, and synthesize research.
                    </p>
                    <button
                      type="button"
                      onClick={handleCreateNewProjectSession}
                      className="mt-4 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-white bg-[#c15f3e] hover:bg-[#a84f32] cursor-pointer"
                    >
                      <Plus className="w-3.5 h-3.5 stroke-[2.2]" />
                      <span>Start Chat</span>
                    </button>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {filteredSessions.map((session) => (
                      <div
                        key={session.id}
                        onClick={() => handleOpenSession(session.id)}
                        className="p-4 rounded-xl border border-[#e8e4dc] dark:border-[#2a2824] bg-white dark:bg-[#1f1d1a] hover:border-[#c15f3e]/40 dark:hover:border-[#c15f3e]/40 hover:shadow-xs transition-all cursor-pointer group flex flex-col justify-between"
                      >
                        <div>
                          <div className="flex items-start justify-between gap-2">
                            <h3 className="text-sm font-semibold text-ink dark:text-zinc-100 group-hover:text-[#c15f3e] dark:group-hover:text-[#c15f3e] transition-colors line-clamp-1">
                              {session.title || "Untitled Chat"}
                            </h3>
                            <span className="text-[10px] font-mono text-muted dark:text-zinc-500 whitespace-nowrap">
                              v{session.version}
                            </span>
                          </div>

                          <div className="flex items-center gap-2 mt-2">
                            <span className="inline-flex items-center gap-1 text-[11px] text-muted dark:text-zinc-400 font-mono">
                              <Calendar className="w-3 h-3" />
                              {new Date(session.updated_at || session.created_at).toLocaleDateString()}
                            </span>
                            {session.document_ids && session.document_ids.length > 0 && (
                              <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-md bg-[#f2ece1] dark:bg-[#282622] text-zinc-700 dark:text-zinc-300 font-mono">
                                <FileText className="w-3 h-3 text-[#c15f3e]" />
                                {session.document_ids.length} docs
                              </span>
                            )}
                          </div>
                        </div>

                        <div className="mt-4 pt-3 border-t border-[#f0eae1] dark:border-[#282622] flex items-center justify-between text-xs text-[#c15f3e] font-medium">
                          <span>Open Chat</span>
                          <ArrowRight className="w-3.5 h-3.5 transform group-hover:translate-x-1 transition-transform" />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* SubTab 2: Sources List */}
            {activeSubTab === "sources" && (
              <div className="space-y-3">
                {filteredDocs.length === 0 ? (
                  <div className="p-12 text-center rounded-2xl border border-dashed border-[#e2dcd2] dark:border-[#2e2b26] bg-[#f8f6f0]/50 dark:bg-[#1a1916]/50">
                    <FileText className="w-8 h-8 text-muted dark:text-zinc-600 mx-auto mb-2" />
                    <p className="text-sm font-anthropic-serif font-semibold text-ink dark:text-zinc-200">
                      No sources in project
                    </p>
                    <p className="text-xs text-muted dark:text-zinc-400 mt-1 max-w-sm mx-auto">
                      Upload PDFs or import documents from the library.
                    </p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {filteredDocs.map((doc) => (
                      <div
                        key={doc.id}
                        onClick={() => onSelectDocument && onSelectDocument(doc.id)}
                        className="p-4 rounded-xl border border-[#e8e4dc] dark:border-[#2a2824] bg-white dark:bg-[#1f1d1a] hover:border-[#c15f3e]/40 dark:hover:border-[#c15f3e]/40 hover:shadow-xs transition-all cursor-pointer group"
                      >
                        <div className="flex items-start gap-3">
                          <div className="w-9 h-9 rounded-lg bg-stone-500/10 text-stone-700 dark:text-stone-300 flex items-center justify-center shrink-0">
                            <FileText className="w-4 h-4 stroke-[2]" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <h3 className="text-sm font-semibold text-ink dark:text-zinc-100 group-hover:text-[#c15f3e] dark:group-hover:text-[#c15f3e] transition-colors truncate">
                              {doc.title || doc.filename}
                            </h3>
                            <p className="text-xs text-muted dark:text-zinc-400 truncate mt-0.5">
                              {doc.authors && doc.authors.length > 0
                                ? doc.authors.join(", ")
                                : "Unknown Author"}
                            </p>
                            <div className="flex items-center gap-2 mt-2">
                              {doc.status === "completed" && (
                                <span className="inline-flex items-center gap-1 text-[10px] font-mono text-emerald-700 dark:text-emerald-400 bg-emerald-500/10 px-1.5 py-0.2 rounded-md">
                                  <CheckCircle2 className="w-3 h-3" /> Ready
                                </span>
                              )}
                              {doc.page_count && (
                                <span className="text-[10px] font-mono text-muted dark:text-zinc-400">
                                  {doc.page_count} pages
                                </span>
                              )}
                              {doc.file_size_bytes ? (
                                <span className="text-[10px] font-mono text-muted dark:text-zinc-400">
                                  {(doc.file_size_bytes / (1024 * 1024)).toFixed(1)} MB
                                </span>
                              ) : null}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
      </div>
    </div>
  );
}
