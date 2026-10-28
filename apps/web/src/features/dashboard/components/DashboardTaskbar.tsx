import { useState, useMemo, useRef, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import {
  Plus,
  MessageSquare,
  Library,
  PenTool,
  PanelLeftClose,
  PanelLeft,
  Search,
  Archive,
  BookOpen,
  CheckCircle2,
  ChevronDown,
  MoreHorizontal,
  Pin,
  Mail,
  MailOpen,
  Pencil,
  Trash2,
  Check,
  X,
} from "lucide-react";
import { AcademicLogo } from "@/components/shared/AcademicLogo";
import { useDashboardStore } from "../stores/useDashboardStore";
import { useAuthStore } from "@/features/auth/stores/useAuthStore";
import { AccountSettingsModal } from "@/features/auth/components/AccountSettingsModal";
import { AvatarDropdownPopover } from "@/features/auth/components/AvatarDropdownPopover";
import { getScholarInitials } from "@/features/auth/utils/avatarUtils";
import { useTheme } from "@/hooks/useTheme";
import { sessionsApi } from "@/features/sessions/api/sessionsApi";
import { useQueryClient } from "@tanstack/react-query";
import type { SessionItem } from "@/types/dashboard";
import { cn } from "@/lib/utils";

const UNREAD_STORAGE_KEY = "verischolar_unread_sessions_v1";

function loadUnreadSessionIds(): Set<string> {
  if (typeof window === "undefined") return new Set();
  try {
    const raw = localStorage.getItem(UNREAD_STORAGE_KEY);
    return raw ? new Set(JSON.parse(raw)) : new Set();
  } catch {
    return new Set();
  }
}

function saveUnreadSessionIds(ids: Set<string>): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(UNREAD_STORAGE_KEY, JSON.stringify(Array.from(ids)));
  } catch {
    // ignore
  }
}

interface DashboardTaskbarProps {
  sessions?: SessionItem[];
  activeSessionId?: string;
  onSelectSession?: (sessionId: string) => void;
  onNewSession?: () => void;
  onOpenLibrary?: () => void;
  onRenameSession?: (sessionId: string, newTitle: string) => Promise<void>;
  onDeleteSession?: (sessionId: string) => Promise<void>;
}

export function DashboardTaskbar({
  sessions: propSessions,
  activeSessionId,
  onSelectSession: propOnSelectSession,
  onNewSession: propOnNewSession,
  onOpenLibrary,
  onRenameSession,
  onDeleteSession,
}: DashboardTaskbarProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { theme } = useTheme();
  const isDark = theme === "dark";
  const { user } = useAuthStore();
  const sidebarState = useDashboardStore((s) => s.sidebarState);
  const toggleSidebar = useDashboardStore((s) => s.toggleSidebar);

  let queryClient: ReturnType<typeof useQueryClient> | null = null;
  try {
    queryClient = useQueryClient();
  } catch {
    queryClient = null;
  }

  const sessions = useMemo(() => propSessions ?? [], [propSessions]);
  const onSelectSession = propOnSelectSession ?? ((id: string) => navigate(`/dashboard/${id}`));
  const onNewSession = propOnNewSession ?? (() => navigate("/dashboard"));

  const isExpanded = sidebarState === "expanded";
  const [searchQuery, setSearchQuery] = useState("");
  const [filterArchived, setFilterArchived] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isAvatarDropdownOpen, setIsAvatarDropdownOpen] = useState(false);
  const [isRecentsCollapsed, setIsRecentsCollapsed] = useState(false);
  const [activeMenuSessionId, setActiveMenuSessionId] = useState<string | null>(null);

  // Read / Unread session tracking
  const [unreadSessionIds, setUnreadSessionIds] = useState<Set<string>>(loadUnreadSessionIds);

  // Inline rename state
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState("");
  const [isSubmittingRename, setIsSubmittingRename] = useState(false);

  // Delete session modal state
  const [deletingSession, setDeletingSession] = useState<SessionItem | null>(null);
  const [isSubmittingDelete, setIsSubmittingDelete] = useState(false);

  const menuContainerRef = useRef<HTMLDivElement>(null);

  // Click-outside listener for context menu
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        menuContainerRef.current &&
        !menuContainerRef.current.contains(event.target as Node)
      ) {
        setActiveMenuSessionId(null);
      }
    }
    if (activeMenuSessionId) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [activeMenuSessionId]);

  const handleSelectSession = (sessionId: string) => {
    if (unreadSessionIds.has(sessionId)) {
      setUnreadSessionIds((prev) => {
        const next = new Set(prev);
        next.delete(sessionId);
        saveUnreadSessionIds(next);
        return next;
      });
    }
    handleItemClick(() => onSelectSession(sessionId));
  };

  const handleToggleUnread = (sessionId: string) => {
    setUnreadSessionIds((prev) => {
      const next = new Set(prev);
      if (next.has(sessionId)) {
        next.delete(sessionId);
      } else {
        next.add(sessionId);
      }
      saveUnreadSessionIds(next);
      return next;
    });
    setActiveMenuSessionId(null);
  };

  const handleStartRename = (session: SessionItem) => {
    setEditingSessionId(session.id);
    setEditingTitle(session.title);
    setActiveMenuSessionId(null);
  };

  const handleSaveRename = async (sessionId: string) => {
    const trimmed = editingTitle.trim();
    if (!trimmed) {
      setEditingSessionId(null);
      return;
    }
    try {
      setIsSubmittingRename(true);
      if (onRenameSession) {
        await onRenameSession(sessionId, trimmed);
      } else {
        const detail = await sessionsApi.getSessionDetail(sessionId);
        const etag = detail.headers?.get?.("etag") || `v${detail.data.version}`;
        await sessionsApi.updateSessionMetadata(sessionId, trimmed, etag);
        queryClient?.invalidateQueries({ queryKey: ["sessions"] });
      }
      const target = sessions.find((s) => s.id === sessionId);
      if (target) target.title = trimmed;
      setEditingSessionId(null);
    } catch (err) {
      console.error("Failed to rename session:", err);
    } finally {
      setIsSubmittingRename(false);
    }
  };

  const handleConfirmDelete = async () => {
    if (!deletingSession) return;
    try {
      setIsSubmittingDelete(true);
      if (onDeleteSession) {
        await onDeleteSession(deletingSession.id);
      } else {
        await sessionsApi.deleteSession(deletingSession.id);
        queryClient?.invalidateQueries({ queryKey: ["sessions"] });
      }
      if (activeSessionId === deletingSession.id) {
        navigate("/dashboard");
      }
      setDeletingSession(null);
    } catch (err) {
      console.error("Failed to delete session:", err);
    } finally {
      setIsSubmittingDelete(false);
    }
  };

  const displayedSessions = useMemo(() => {
    return sessions.filter((session) => {
      if (filterArchived) {
        if (!session.is_archived) return false;
      }
      if (searchQuery.trim()) {
        const q = searchQuery.trim().toLowerCase();
        return session.title.toLowerCase().includes(q);
      }
      return true;
    });
  }, [sessions, searchQuery, filterArchived]);

  const handleItemClick = (callback?: () => void) => {
    if (callback) callback();
    if (typeof window !== "undefined" && window.innerWidth < 768 && isExpanded) {
      toggleSidebar();
    }
  };

  const userInitials = getScholarInitials(user?.full_name, user?.email);

  const pathname = location.pathname;
  const isLibrary = pathname.startsWith("/library");
  const isWriting = pathname.startsWith("/writing");
  const isResearch =
    !isLibrary &&
    !isWriting &&
    (pathname === "/dashboard" ||
      pathname.startsWith("/dashboard/") ||
      pathname.startsWith("/research") ||
      pathname.startsWith("/discovery") ||
      pathname === "/");

  const navItems = [
    {
      id: "research",
      label: "Khám phá & Phiên đọc",
      title: "Khám phá & Phiên đọc (Đọc & Nghiên cứu)",
      icon: BookOpen,
      isActive: isResearch,
      onClick: () => navigate("/dashboard"),
    },
    {
      id: "library",
      label: "Kho Yêu thích",
      title: "Thư viện tài liệu nghiên cứu",
      icon: Library,
      isActive: isLibrary,
      onClick: () => {
        onOpenLibrary?.();
        navigate("/library");
      },
    },
    {
      id: "writing",
      label: "Soạn thảo LaTeX",
      title: "Soạn thảo LaTeX (Agentic Overleaf)",
      icon: PenTool,
      isActive: isWriting,
      onClick: () => navigate("/writing"),
    },
  ];

  return (
    <>
      {/* Mobile Drawer Backdrop */}
      {isExpanded && (
        <div
          role="presentation"
          onClick={toggleSidebar}
          aria-hidden="true"
          data-testid="mobile-drawer-backdrop"
          className="fixed inset-0 bg-black/40 backdrop-blur-xs z-[55] md:hidden animate-in fade-in duration-200"
        />
      )}

      <aside
        aria-label="Thanh điều hướng chính"
        className={cn(
          "h-screen border-r border-[#e8e4dc] dark:border-[#2e2b26] bg-[#fbf9f5] dark:bg-[#1c1b18] flex flex-col justify-between select-none transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] shrink-0 overflow-hidden",
          isExpanded
            ? "w-72 lg:w-60 fixed inset-y-0 left-0 z-[60] shadow-2xl md:relative md:shadow-none"
            : "w-14 md:w-16 hidden md:flex md:relative z-30"
        )}
      >
      {/* 1. Top Section */}
      <div className="flex flex-col w-full">
        {/* Top Header Row with Seamless Synchronized Transition */}
        <div className="h-14 px-2 flex items-center border-b border-[#ece8df] dark:border-[#2a2824] relative overflow-hidden shrink-0">
          {/* Collapsed State: Logo Button (Hover reveals Expand icon) */}
          <div
            className={`absolute inset-y-2 left-0 right-0 flex items-center justify-center transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] ${
              isExpanded
                ? "opacity-0 pointer-events-none scale-90 -translate-x-2"
                : "opacity-100 scale-100 translate-x-0"
            }`}
          >
            <button
              type="button"
              onClick={toggleSidebar}
              aria-label="Mở rộng thanh điều hướng"
              title="Mở rộng sidebar"
              className="group min-h-[44px] min-w-[44px] w-10 h-10 flex items-center justify-center rounded-xl transition-colors cursor-pointer relative text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#f2ece1] dark:hover:bg-[#262420] focus:outline-none"
            >
              <span className="flex items-center justify-center transition-transform group-hover:hidden">
                <AcademicLogo size="sm" showWordmark={false} inverted={isDark} />
              </span>
              <span className="hidden items-center justify-center transition-transform group-hover:flex">
                <PanelLeft className="w-5 h-5 text-coral-600 dark:text-coral-400 stroke-[2.2]" />
              </span>
            </button>
          </div>

          {/* Expanded State: Logo Wordmark & Collapse Button */}
          <div
            className={`w-full px-1 flex items-center justify-between transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] ${
              isExpanded
                ? "opacity-100 translate-x-0"
                : "opacity-0 -translate-x-6 pointer-events-none"
            }`}
          >
            <Link to="/" className="flex items-center gap-2.5 focus:outline-none group">
              <AcademicLogo size="sm" inverted={isDark} />
            </Link>
            <button
              type="button"
              onClick={toggleSidebar}
              aria-label="Thu gọn thanh điều hướng"
              title="Thu gọn sidebar"
              className="min-h-[44px] min-w-[44px] w-9 h-9 flex items-center justify-center text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-surface-cream-strong dark:hover:bg-[#282623] rounded-xl transition-colors cursor-pointer focus:outline-none"
            >
              <PanelLeftClose className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Action Controls - Fixed Axis Icons, Fluid Animated Text */}
        <div className="p-2 space-y-1 shrink-0 overflow-y-auto max-h-[calc(48vh)] scrollbar-none">
          {/* 1. New Chat Button */}
          <button
            type="button"
            onClick={() => handleItemClick(onNewSession)}
            title="Đoạn chat mới"
            className={cn(
              "flex items-center text-xs font-anthropic-serif font-semibold text-white bg-coral-500 hover:bg-coral-600 transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] shadow-xs cursor-pointer overflow-hidden focus:outline-none mb-1",
              isExpanded
                ? "w-full min-h-[44px] md:min-h-0 md:h-9 rounded-xl"
                : "w-10 h-10 aspect-square rounded-full mx-auto justify-center p-0"
            )}
          >
            <div className={cn("shrink-0 flex items-center justify-center", isExpanded ? "w-10 min-h-[44px] md:min-h-0 md:h-9" : "w-10 h-10")}>
              <Plus className="w-4 h-4 stroke-[2.2]" />
            </div>
            <div
              className={`overflow-hidden whitespace-nowrap transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] ${
                isExpanded
                  ? "max-w-[160px] opacity-100 translate-x-0 pr-3"
                  : "max-w-0 opacity-0 -translate-x-2 pointer-events-none"
              }`}
            >
              <span className="font-semibold whitespace-nowrap truncate font-anthropic-serif">
                Đoạn chat mới
              </span>
            </div>
          </button>

          {/* Module Nav Items */}
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => handleItemClick(item.onClick)}
                title={item.title}
                className={cn(
                  "w-full min-h-[44px] md:min-h-0 md:h-9 flex items-center rounded-xl text-xs font-anthropic-serif transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] cursor-pointer overflow-hidden focus:outline-none",
                  item.isActive
                    ? "text-coral-700 dark:text-coral-300 font-bold"
                    : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#f2ece1] dark:hover:bg-[#262420]"
                )}
              >
                <div className="w-10 min-h-[44px] md:min-h-0 md:h-9 shrink-0 flex items-center justify-center">
                  <Icon className="w-4 h-4 text-coral-600 dark:text-coral-400 stroke-[2.2]" />
                </div>
                <div
                  className={`overflow-hidden whitespace-nowrap transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] ${
                    isExpanded
                      ? "max-w-[160px] opacity-100 translate-x-0 pr-3"
                      : "max-w-0 opacity-0 -translate-x-2 pointer-events-none"
                  }`}
                >
                  <span className="truncate whitespace-nowrap font-anthropic-serif font-semibold">
                    {item.label}
                  </span>
                </div>
              </button>
            );
          })}
        </div>


        {/* Sessions List - Graceful Collapse Transition, Hidden in Collapsed State */}
        <div
          className={`transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] overflow-hidden ${
            isExpanded
              ? "max-h-[calc(100vh-280px)] opacity-100 translate-y-0"
              : "max-h-0 opacity-0 -translate-y-2 pointer-events-none"
          }`}
        >
          {/* Divider between Actions & Recent Sessions */}
          <div className="px-2 py-1">
            <div className="border-t border-[#ece8df] dark:border-[#2a2824]" />
          </div>

          {/* Search & Filter Bar */}
          <div className="px-2 py-1 space-y-1.5">
            <div className="relative">
              <Search className="w-3 h-3 text-muted absolute left-2 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Tìm phiên..."
                className="w-full pl-6 pr-2 py-1 rounded-lg bg-canvas dark:bg-[#141311] border border-hairline focus:border-coral-500 outline-none text-[11px] font-sans text-ink dark:text-zinc-200"
              />
            </div>
            <div className="flex items-center justify-between text-[11px] pt-1">
              <button
                type="button"
                data-testid="recents-collapse-toggle"
                onClick={() => setIsRecentsCollapsed(!isRecentsCollapsed)}
                className="flex items-center gap-1.5 font-semibold text-muted hover:text-ink dark:hover:text-zinc-200 cursor-pointer focus:outline-none"
              >
                <span>Recents</span>
                <ChevronDown className={cn("w-3.5 h-3.5 transition-transform duration-200", isRecentsCollapsed && "-rotate-90")} />
                <span className="text-[10px] text-muted font-normal">({displayedSessions.length})</span>
              </button>
              <button
                type="button"
                onClick={() => setFilterArchived(!filterArchived)}
                className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded transition-colors cursor-pointer text-[10px] ${
                  filterArchived
                    ? "bg-amber-500/10 text-amber-700 dark:text-amber-400 font-semibold"
                    : "text-muted hover:text-ink"
                }`}
                title={filterArchived ? "Xem phiên đang hoạt động" : "Xem phiên đã lưu trữ (Archived)"}
              >
                <Archive className="w-3 h-3" />
                <span>{filterArchived ? "Lưu trữ" : "Xem lưu trữ"}</span>
              </button>
            </div>
          </div>

          {!isRecentsCollapsed && (
            <div className="px-2 pt-1 pb-1 space-y-1 overflow-y-auto max-h-[calc(100vh-340px)] scrollbar-none">
              {displayedSessions.length === 0 ? (
                <div className="py-6 text-center text-muted text-[11px]">
                  {searchQuery.trim() ? "Không tìm thấy phiên" : filterArchived ? "Không có phiên lưu trữ" : "Chưa có phiên nào"}
                </div>
              ) : (
                displayedSessions.map((session) => {
                  const isActive = session.id === activeSessionId;
                  const isMenuOpen = activeMenuSessionId === session.id;
                  const isEditing = editingSessionId === session.id;
                  const isUnread = unreadSessionIds.has(session.id);

                  return (
                    <div key={session.id} className="relative group">
                      {isEditing ? (
                        <div className="flex items-center gap-1 px-2 py-1.5 w-full bg-white dark:bg-[#282622] rounded-xl border border-coral-500 shadow-2xs">
                          <input
                            type="text"
                            autoFocus
                            data-testid={`session-rename-input-${session.id}`}
                            value={editingTitle}
                            onChange={(e) => setEditingTitle(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === "Enter") handleSaveRename(session.id);
                              if (e.key === "Escape") setEditingSessionId(null);
                            }}
                            disabled={isSubmittingRename}
                            className="flex-1 bg-transparent text-xs font-sans text-ink dark:text-zinc-100 outline-none min-w-0"
                          />
                          <button
                            type="button"
                            data-testid={`session-rename-save-${session.id}`}
                            disabled={isSubmittingRename}
                            onClick={() => handleSaveRename(session.id)}
                            className="p-1 text-emerald-600 hover:bg-emerald-500/10 rounded cursor-pointer"
                            title="Lưu (Enter)"
                          >
                            <Check className="w-3.5 h-3.5" />
                          </button>
                          <button
                            type="button"
                            onClick={() => setEditingSessionId(null)}
                            className="p-1 text-muted hover:text-ink rounded cursor-pointer"
                            title="Hủy (Esc)"
                          >
                            <X className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      ) : (
                        <>
                          <button
                            type="button"
                            onClick={() => handleSelectSession(session.id)}
                            title={session.title}
                            className={cn(
                              "w-full text-left flex items-center gap-2 px-3 py-2 pr-7 min-h-[44px] md:min-h-0 rounded-xl text-xs font-anthropic-serif font-semibold transition-colors cursor-pointer relative overflow-hidden focus:outline-none",
                              isActive
                                ? "bg-white dark:bg-[#282622] text-ink dark:text-zinc-100 shadow-xs border border-[#e8e4dc] dark:border-[#38342e]"
                                : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200 hover:bg-[#f4efe6] dark:hover:bg-[#24221e]"
                            )}
                          >
                            {isActive && (
                              <span className="absolute left-1 top-2 bottom-2 w-1 rounded-full bg-coral-500" />
                            )}
                            <MessageSquare
                              className={cn(
                                "w-3.5 h-3.5 shrink-0",
                                isActive ? "text-coral-500" : "text-muted dark:text-zinc-500 group-hover:text-coral-500"
                              )}
                            />
                            <span className="truncate flex-1 whitespace-nowrap font-anthropic-serif font-semibold">
                              {session.title}
                            </span>
                            {isUnread && (
                              <span
                                data-testid={`session-unread-dot-${session.id}`}
                                title="Chưa đọc"
                                className="w-2 h-2 rounded-full bg-coral-500 shrink-0 shadow-2xs"
                              />
                            )}
                            {session.is_archived && (
                              <span title="Phiên đã hết hạn lưu trữ (Archived)">
                                <Archive className="w-3 h-3 text-amber-500 shrink-0" />
                              </span>
                            )}
                          </button>

                          {/* More (...) Button */}
                          <button
                            type="button"
                            data-testid={`session-more-btn-${session.id}`}
                            aria-label={`Tùy chọn ${session.title}`}
                            onClick={(e) => {
                              e.stopPropagation();
                              setActiveMenuSessionId(isMenuOpen ? null : session.id);
                            }}
                            className={cn(
                              "absolute right-1.5 top-1/2 -translate-y-1/2 w-6 h-6 rounded-lg flex items-center justify-center text-muted hover:text-ink dark:hover:text-zinc-100 hover:bg-[#e8e3d8] dark:hover:bg-[#33302a] transition-all cursor-pointer z-10",
                              isMenuOpen ? "opacity-100 bg-[#e8e3d8] dark:bg-[#33302a]" : "opacity-0 group-hover:opacity-100"
                            )}
                          >
                            <MoreHorizontal className="w-3.5 h-3.5" />
                          </button>

                          {/* Context Menu Popup (Image 2 style: Pin, Mark as unread/read, Rename, Delete) */}
                          {isMenuOpen && (
                            <div
                              ref={menuContainerRef}
                              data-testid={`session-context-menu-${session.id}`}
                              onClick={(e) => e.stopPropagation()}
                              className="absolute right-0 top-full mt-1 z-50 w-44 p-1 rounded-xl bg-white dark:bg-[#201e1b] border border-[#e5dfd4] dark:border-[#38332c] shadow-xl text-xs select-none animate-in fade-in zoom-in-95 duration-100"
                            >
                              <button
                                type="button"
                                onClick={() => setActiveMenuSessionId(null)}
                                className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-left text-ink dark:text-zinc-200 hover:bg-[#f4efe6] dark:hover:bg-[#2c2925] transition-colors cursor-pointer"
                              >
                                <Pin className="w-3.5 h-3.5 text-zinc-500" />
                                <span>Ghim</span>
                              </button>
                              <button
                                type="button"
                                onClick={() => handleToggleUnread(session.id)}
                                className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-left text-ink dark:text-zinc-200 hover:bg-[#f4efe6] dark:hover:bg-[#2c2925] transition-colors cursor-pointer"
                              >
                                {isUnread ? (
                                  <>
                                    <MailOpen className="w-3.5 h-3.5 text-zinc-500" />
                                    <span>Đánh dấu đã đọc</span>
                                  </>
                                ) : (
                                  <>
                                    <Mail className="w-3.5 h-3.5 text-zinc-500" />
                                    <span>Đánh dấu chưa đọc</span>
                                  </>
                                )}
                              </button>
                              <button
                                type="button"
                                onClick={() => handleStartRename(session)}
                                className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-left text-ink dark:text-zinc-200 hover:bg-[#f4efe6] dark:hover:bg-[#2c2925] transition-colors cursor-pointer"
                              >
                                <Pencil className="w-3.5 h-3.5 text-zinc-500" />
                                <span>Đổi tên</span>
                              </button>
                              <div className="my-1 border-t border-hairline dark:border-[#2f2b26]" />
                              <button
                                type="button"
                                onClick={() => {
                                  setActiveMenuSessionId(null);
                                  setDeletingSession(session);
                                }}
                                className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-left text-rose-600 dark:text-rose-400 hover:bg-rose-500/10 transition-colors cursor-pointer font-medium"
                              >
                                <Trash2 className="w-3.5 h-3.5 text-rose-500" />
                                <span>Xóa</span>
                              </button>
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          )}
        </div>
      </div>

      {/* 2. Bottom Rail: Unified User Profile Button (Cabinet Principle) */}
      <div className="p-2 border-t border-[#ece8df] dark:border-[#2a2824] shrink-0 relative">
        <button
          type="button"
          onClick={() => setIsAvatarDropdownOpen((prev) => !prev)}
          data-testid="taskbar-avatar-btn"
          title={user?.full_name ? `${user.full_name} — Tùy chọn tài khoản` : "Tùy chọn tài khoản"}
          aria-label="Tùy chọn tài khoản"
          className={cn(
            "w-full min-h-[44px] flex items-center rounded-xl transition-all duration-200 cursor-pointer text-left group",
            isExpanded
              ? "px-2.5 py-1.5 hover:bg-[#eae4d8] dark:hover:bg-[#252320]"
              : "justify-center p-0 hover:bg-[#eae4d8] dark:hover:bg-[#252320]"
          )}
        >
          {/* Avatar tròn DU */}
          <div className="w-8 h-8 rounded-full overflow-hidden border border-hairline dark:border-[#38332c] shrink-0 flex items-center justify-center bg-coral-500/10 text-coral-600 dark:text-coral-400 font-serif font-bold text-xs">
            {user?.avatar_url ? (
              <img
                src={user.avatar_url}
                alt={user.full_name || "Scholar avatar"}
                className="w-full h-full object-cover"
                referrerPolicy="no-referrer"
              />
            ) : (
              <span>{userInitials}</span>
            )}
          </div>

          {/* User Details (when expanded): Verified checkmark without redundant email (Rule Item 2) */}
          <div
            className={cn(
              "flex items-center min-w-0 transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] overflow-hidden",
              isExpanded
                ? "flex-1 opacity-100 max-w-[170px] ml-2.5"
                : "max-w-0 opacity-0 ml-0 pointer-events-none"
            )}
          >
            <div className="flex items-center gap-1 min-w-0">
              <span className="text-xs font-semibold text-ink dark:text-zinc-100 truncate font-serif leading-tight">
                {user?.full_name ?? "Dam Manh Dung"}
              </span>
              <CheckCircle2 className="w-3.5 h-3.5 text-[#cc785c] shrink-0" />
            </div>
          </div>
        </button>

        {/* Avatar Dropdown Popover - Floating Overlay Layer */}
        <AvatarDropdownPopover
          isOpen={isAvatarDropdownOpen}
          onClose={() => setIsAvatarDropdownOpen(false)}
          onOpenSettings={() => setIsSettingsOpen(true)}
          className="bottom-16 left-3 shadow-[0_16px_48px_rgba(0,0,0,0.25)]"
        />
      </div>
    </aside>

    {/* Account Settings Modal */}
    <AccountSettingsModal
      isOpen={isSettingsOpen}
      onClose={() => setIsSettingsOpen(false)}
    />

    {/* Delete Session Confirmation Dialog */}
    {deletingSession && (
      <div
        data-testid="delete-session-dialog"
        className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs animate-in fade-in duration-150"
      >
        <div className="w-full max-w-sm rounded-2xl bg-white dark:bg-[#1f1d1a] border border-[#e5dfd4] dark:border-[#38332c] p-5 shadow-2xl space-y-4">
          <div className="space-y-1.5">
            <h3 className="font-serif font-bold text-sm sm:text-base text-ink dark:text-zinc-100">
              Xác nhận xóa phiên nghiên cứu?
            </h3>
            <p className="text-xs text-muted dark:text-zinc-400 leading-relaxed font-sans">
              Bạn có chắc chắn muốn xóa phiên <span className="font-semibold text-ink dark:text-zinc-200 font-serif">"{deletingSession.title}"</span>? Thao tác này không thể hoàn tác.
            </p>
          </div>
          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setDeletingSession(null)}
              disabled={isSubmittingDelete}
              className="px-3 py-1.5 rounded-xl text-xs font-medium text-muted hover:text-ink dark:hover:text-zinc-200 hover:bg-[#f4efe6] dark:hover:bg-[#282521] transition-colors cursor-pointer"
            >
              Hủy
            </button>
            <button
              type="button"
              data-testid="confirm-delete-session-btn"
              disabled={isSubmittingDelete}
              onClick={handleConfirmDelete}
              className="px-3.5 py-1.5 rounded-xl text-xs font-semibold text-white bg-rose-600 hover:bg-rose-700 transition-colors cursor-pointer shadow-xs disabled:opacity-50"
            >
              {isSubmittingDelete ? "Đang xóa..." : "Xóa vĩnh viễn"}
            </button>
          </div>
        </div>
      </div>
    )}
  </>
  );
}

