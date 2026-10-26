import { useState, useMemo } from "react";
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
} from "lucide-react";
import { AcademicLogo } from "@/components/shared/AcademicLogo";
import { useDashboardStore } from "../stores/useDashboardStore";
import { useAuthStore } from "@/features/auth/stores/useAuthStore";
import { AccountSettingsModal } from "@/features/auth/components/AccountSettingsModal";
import { AvatarDropdownPopover } from "@/features/auth/components/AvatarDropdownPopover";
import { getScholarInitials } from "@/features/auth/utils/avatarUtils";
import { useTheme } from "@/hooks/useTheme";
import type { SessionItem } from "@/types/dashboard";
import { cn } from "@/lib/utils";

interface DashboardTaskbarProps {
  sessions?: SessionItem[];
  activeSessionId?: string;
  onSelectSession?: (sessionId: string) => void;
  onNewSession?: () => void;
  onOpenLibrary?: () => void;
}

export function DashboardTaskbar({
  sessions: propSessions,
  activeSessionId,
  onSelectSession: propOnSelectSession,
  onNewSession: propOnNewSession,
  onOpenLibrary,
}: DashboardTaskbarProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { theme } = useTheme();
  const isDark = theme === "dark";
  const { user } = useAuthStore();
  const sidebarState = useDashboardStore((s) => s.sidebarState);
  const toggleSidebar = useDashboardStore((s) => s.toggleSidebar);

  const sessions = useMemo(() => propSessions ?? [], [propSessions]);
  const onSelectSession = propOnSelectSession ?? ((id: string) => navigate(`/dashboard/${id}`));
  const onNewSession = propOnNewSession ?? (() => navigate("/dashboard"));

  const isExpanded = sidebarState === "expanded";
  const [searchQuery, setSearchQuery] = useState("");
  const [filterArchived, setFilterArchived] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isAvatarDropdownOpen, setIsAvatarDropdownOpen] = useState(false);

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
            className="w-full min-h-[44px] md:min-h-0 md:h-9 flex items-center rounded-xl text-xs font-anthropic-serif font-semibold text-white bg-coral-500 hover:bg-coral-600 transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] shadow-xs cursor-pointer overflow-hidden focus:outline-none mb-1"
          >
            <div className="w-10 min-h-[44px] md:min-h-0 md:h-9 shrink-0 flex items-center justify-center">
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
                  "w-full min-h-[44px] md:min-h-0 md:h-9 flex items-center rounded-xl text-xs font-anthropic-serif font-semibold transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] cursor-pointer overflow-hidden focus:outline-none",
                  item.isActive
                    ? "bg-coral-500/15 text-coral-700 dark:text-coral-300 border border-coral-500/25 font-bold"
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
            <div className="flex items-center justify-between text-[10px]">
              <span className="font-semibold text-muted uppercase tracking-wider font-mono">
                {filterArchived ? "Đã lưu trữ" : "Gần đây"} ({displayedSessions.length})
              </span>
              <button
                type="button"
                onClick={() => setFilterArchived(!filterArchived)}
                className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded transition-colors cursor-pointer ${
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

          <div className="px-2 pt-1 pb-1 space-y-1 overflow-y-auto max-h-[calc(100vh-340px)] scrollbar-none">
            {displayedSessions.length === 0 ? (
              <div className="py-6 text-center text-muted text-[11px]">
                {searchQuery.trim() ? "Không tìm thấy phiên" : filterArchived ? "Không có phiên lưu trữ" : "Chưa có phiên nào"}
              </div>
            ) : (
              displayedSessions.map((session) => {
                const isActive = session.id === activeSessionId;
                return (
                  <button
                    key={session.id}
                    type="button"
                    onClick={() => handleItemClick(() => onSelectSession(session.id))}
                    title={session.title}
                    className={`w-full text-left flex items-center gap-2.5 px-3 py-2 min-h-[44px] md:min-h-0 rounded-xl text-xs font-anthropic-serif font-semibold transition-colors cursor-pointer group relative overflow-hidden focus:outline-none ${
                      isActive
                        ? "bg-white dark:bg-[#282622] text-ink dark:text-zinc-100 shadow-xs border border-[#e8e4dc] dark:border-[#38342e]"
                        : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200 hover:bg-[#f4efe6] dark:hover:bg-[#24221e]"
                    }`}
                  >
                    {isActive && (
                      <span className="absolute left-1 top-2 bottom-2 w-1 rounded-full bg-coral-500" />
                    )}
                    <MessageSquare
                      className={`w-3.5 h-3.5 shrink-0 ${
                        isActive ? "text-coral-500" : "text-muted dark:text-zinc-500 group-hover:text-coral-500"
                      }`}
                    />
                    <span className="truncate flex-1 whitespace-nowrap font-anthropic-serif font-semibold">
                      {session.title}
                    </span>
                    {session.is_archived && (
                      <span title="Phiên đã hết hạn lưu trữ (Archived)">
                        <Archive className="w-3 h-3 text-amber-500 shrink-0" />
                      </span>
                    )}
                  </button>
                );
              })
            )}
          </div>
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

          {/* User Details (when expanded): Verified checkmark + email */}
          <div
            className={cn(
              "flex flex-col min-w-0 transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] overflow-hidden",
              isExpanded
                ? "flex-1 opacity-100 max-w-[170px] ml-2.5"
                : "max-w-0 opacity-0 ml-0 pointer-events-none"
            )}
          >
            <div className="flex items-center gap-1 min-w-0">
              <span className="text-xs font-semibold text-ink dark:text-zinc-100 truncate font-serif leading-tight">
                {user?.full_name ?? "Dam Manh Dung"}
              </span>
              <CheckCircle2 className="w-3 h-3 text-[#cc785c] shrink-0" />
            </div>
            <span className="text-3xs text-muted dark:text-zinc-400 truncate font-mono leading-tight mt-0.5">
              {user?.email || "dammanhdungvn@gmail.com"}
            </span>
          </div>
        </button>

        {/* Avatar Dropdown Popover */}
        <AvatarDropdownPopover
          isOpen={isAvatarDropdownOpen}
          onClose={() => setIsAvatarDropdownOpen(false)}
          onOpenSettings={() => setIsSettingsOpen(true)}
          side="top"
          align="left"
          className="bottom-full mb-2 left-2"
        />
      </div>
    </aside>

    {/* Account Settings Modal */}
    <AccountSettingsModal
      isOpen={isSettingsOpen}
      onClose={() => setIsSettingsOpen(false)}
    />
  </>
  );
}

