import { useState, useMemo } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Plus,
  MessageSquare,
  Library,
  FolderKanban,
  LogOut,
  PanelLeftClose,
  PanelLeft,
  Search,
  Archive,
  Sun,
  Moon,
  FileCode,
  Building2,
  Shield,
} from "lucide-react";
import { AcademicLogo } from "@/components/shared/AcademicLogo";
import { useDashboardStore } from "../stores/useDashboardStore";
import { useAuthStore } from "@/features/auth/stores/useAuthStore";
import { useTheme } from "@/hooks/useTheme";
import type { SessionItem } from "@/types/dashboard";
import { cn } from "@/lib/utils";

interface DashboardTaskbarProps {
  sessions: SessionItem[];
  activeSessionId?: string;
  onSelectSession: (sessionId: string) => void;
  onNewSession: () => void;
  onOpenLibrary?: () => void;
  onOpenProjects?: () => void;
}

export function DashboardTaskbar({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewSession,
  onOpenLibrary,
  onOpenProjects
}: DashboardTaskbarProps) {
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === "dark";
  const { user, logout } = useAuthStore();
  const sidebarState = useDashboardStore((s) => s.sidebarState);
  const toggleSidebar = useDashboardStore((s) => s.toggleSidebar);

  const isExpanded = sidebarState === "expanded";
  const [searchQuery, setSearchQuery] = useState("");
  const [filterArchived, setFilterArchived] = useState(false);

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

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const userInitial = user?.full_name
    ? user.full_name.charAt(0).toUpperCase()
    : "V";

  return (
    <>
      {/* Mobile Drawer Backdrop */}
      {isExpanded && (
        <div
          role="presentation"
          onClick={toggleSidebar}
          aria-hidden="true"
          className="fixed inset-0 bg-black/40 backdrop-blur-xs z-40 md:hidden animate-in fade-in duration-200"
        />
      )}

      <aside
        aria-label="Thanh điều hướng chính"
        className={cn(
          "h-screen border-r border-[#e8e4dc] dark:border-[#2e2b26] bg-[#fbf9f5] dark:bg-[#1c1b18] flex flex-col justify-between select-none transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] shrink-0 overflow-hidden",
          isExpanded
            ? "w-64 fixed inset-y-0 left-0 z-50 shadow-2xl md:relative md:shadow-none"
            : "w-14 hidden md:flex md:relative z-30"
        )}
      >
      {/* 1. Top Section */}
      <div className="flex flex-col w-full">
        {/* Top Header Row with Seamless Synchronized Transition */}
        <div className="h-14 px-2 flex items-center border-b border-[#ece8df] dark:border-[#2a2824] relative overflow-hidden shrink-0">
          {/* Collapsed State: Logo Button (Hover reveals Expand icon) */}
          <div
            className={`absolute left-2 top-2 bottom-2 w-10 flex items-center justify-center transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] ${
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
              className="group w-10 h-10 flex items-center justify-center rounded-xl transition-colors cursor-pointer relative text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#f2ece1] dark:hover:bg-[#262420] focus:outline-none"
            >
              <span className="flex items-center justify-center transition-transform group-hover:hidden">
                <AcademicLogo size="sm" showWordmark={false} inverted={isDark} />
              </span>
              <span className="hidden items-center justify-center transition-transform group-hover:flex">
                <PanelLeft className="w-4.5 h-4.5 text-coral-600 dark:text-coral-400 stroke-[2.2]" />
              </span>
            </button>
          </div>

          {/* Expanded State: Logo Wordmark & Collapse Button */}
          <div
            className={`w-60 px-1 flex items-center justify-between transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] ${
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
              className="w-8 h-8 flex items-center justify-center text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-surface-cream-strong dark:hover:bg-[#282623] rounded-lg transition-colors cursor-pointer focus:outline-none"
            >
              <PanelLeftClose className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Action Controls - Fixed Axis Icons, Fluid Animated Text */}
        <div className="p-2 space-y-1.5 shrink-0">
          {/* 1. New Chat Button */}
          <button
            type="button"
            onClick={onNewSession}
            title="Đoạn chat mới"
            className="w-full h-9 flex items-center rounded-xl text-xs font-anthropic-serif font-semibold text-white bg-coral-500 hover:bg-coral-600 transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] shadow-xs cursor-pointer overflow-hidden focus:outline-none"
          >
            <div className="w-10 h-9 shrink-0 flex items-center justify-center">
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

          {/* 2. Library Button */}
          <button
            type="button"
            onClick={onOpenLibrary}
            title="Thư viện tài liệu nghiên cứu"
            className="w-full h-9 flex items-center rounded-xl text-xs font-anthropic-serif font-semibold text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#f2ece1] dark:hover:bg-[#262420] transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] cursor-pointer overflow-hidden focus:outline-none"
          >
            <div className="w-10 h-9 shrink-0 flex items-center justify-center">
              <Library className="w-4 h-4 text-coral-600 dark:text-coral-400 stroke-[2.2]" />
            </div>
            <div
              className={`overflow-hidden whitespace-nowrap transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] ${
                isExpanded
                  ? "max-w-[160px] opacity-100 translate-x-0 pr-3"
                  : "max-w-0 opacity-0 -translate-x-2 pointer-events-none"
              }`}
            >
              <span className="truncate whitespace-nowrap font-anthropic-serif font-semibold">
                Thư viện
              </span>
            </div>
          </button>

          {/* 3. Projects Button */}
          <button
            type="button"
            onClick={onOpenProjects}
            title="Dự án nghiên cứu"
            className="w-full h-9 flex items-center rounded-xl text-xs font-anthropic-serif font-semibold text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#f2ece1] dark:hover:bg-[#262420] transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] cursor-pointer overflow-hidden focus:outline-none"
          >
            <div className="w-10 h-9 shrink-0 flex items-center justify-center">
              <FolderKanban className="w-4 h-4 text-coral-600 dark:text-coral-400 stroke-[2.2]" />
            </div>
            <div
              className={`overflow-hidden whitespace-nowrap transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] ${
                isExpanded
                  ? "max-w-[160px] opacity-100 translate-x-0 pr-3"
                  : "max-w-0 opacity-0 -translate-x-2 pointer-events-none"
              }`}
            >
              <span className="truncate whitespace-nowrap font-anthropic-serif font-semibold">
                Dự án
              </span>
            </div>
          </button>

          {/* 4. Academic Drafts Button */}
          <button
            type="button"
            onClick={() => navigate("/drafts")}
            title="Bản thảo học thuật & LaTeX"
            className="w-full h-9 flex items-center rounded-xl text-xs font-anthropic-serif font-semibold text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#f2ece1] dark:hover:bg-[#262420] transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] cursor-pointer overflow-hidden focus:outline-none"
          >
            <div className="w-10 h-9 shrink-0 flex items-center justify-center">
              <FileCode className="w-4 h-4 text-coral-600 dark:text-coral-400 stroke-[2.2]" />
            </div>
            <div
              className={`overflow-hidden whitespace-nowrap transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] ${
                isExpanded
                  ? "max-w-[160px] opacity-100 translate-x-0 pr-3"
                  : "max-w-0 opacity-0 -translate-x-2 pointer-events-none"
              }`}
            >
              <span className="truncate whitespace-nowrap font-anthropic-serif font-semibold">
                Bản thảo LaTeX
              </span>
            </div>
          </button>

          {/* 5. Collaborative Labs Button */}
          <button
            type="button"
            onClick={() => navigate("/labs")}
            title="Phòng Lab nghiên cứu"
            className="w-full h-9 flex items-center rounded-xl text-xs font-anthropic-serif font-semibold text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#f2ece1] dark:hover:bg-[#262420] transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] cursor-pointer overflow-hidden focus:outline-none"
          >
            <div className="w-10 h-9 shrink-0 flex items-center justify-center">
              <Building2 className="w-4 h-4 text-coral-600 dark:text-coral-400 stroke-[2.2]" />
            </div>
            <div
              className={`overflow-hidden whitespace-nowrap transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] ${
                isExpanded
                  ? "max-w-[160px] opacity-100 translate-x-0 pr-3"
                  : "max-w-0 opacity-0 -translate-x-2 pointer-events-none"
              }`}
            >
              <span className="truncate whitespace-nowrap font-anthropic-serif font-semibold">
                Phòng Lab
              </span>
            </div>
          </button>

          {/* 6. Admin Console Button (if admin role) */}
          {user?.role === "admin" && (
            <button
              type="button"
              onClick={() => navigate("/admin")}
              title="Quản trị hệ thống"
              className="w-full h-9 flex items-center rounded-xl text-xs font-anthropic-serif font-semibold text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-950/30 transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] cursor-pointer overflow-hidden focus:outline-none"
            >
              <div className="w-10 h-9 shrink-0 flex items-center justify-center">
                <Shield className="w-4 h-4 text-purple-600 dark:text-purple-400 stroke-[2.2]" />
              </div>
              <div
                className={`overflow-hidden whitespace-nowrap transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] ${
                  isExpanded
                    ? "max-w-[160px] opacity-100 translate-x-0 pr-3"
                    : "max-w-0 opacity-0 -translate-x-2 pointer-events-none"
                }`}
              >
                <span className="truncate whitespace-nowrap font-anthropic-serif font-semibold">
                  Admin Console
                </span>
              </div>
            </button>
          )}
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
                    onClick={() => onSelectSession(session.id)}
                    title={session.title}
                    className={`w-full text-left flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-anthropic-serif font-semibold transition-colors cursor-pointer group relative overflow-hidden focus:outline-none ${
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

      {/* 2. Bottom Rail: Theme Switcher & User Profile */}
      <div className="p-2 border-t border-[#ece8df] dark:border-[#2a2824] shrink-0 flex flex-col gap-1.5">
        {/* Collapsed Theme Button */}
        {!isExpanded && (
          <button
            type="button"
            onClick={toggleTheme}
            aria-label={isDark ? "Chuyển sang chế độ sáng" : "Chuyển sang chế độ tối"}
            title={isDark ? "Chế độ sáng" : "Chế độ tối"}
            className="w-10 h-10 mx-auto flex items-center justify-center rounded-xl text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#f2ece1] dark:hover:bg-[#262420] transition-colors cursor-pointer"
          >
            {isDark ? (
              <Sun className="w-4 h-4 text-amber-400" />
            ) : (
              <Moon className="w-4 h-4 text-zinc-600" />
            )}
          </button>
        )}

        {isExpanded && (
          <div className="px-2.5 py-1.5 bg-white dark:bg-[#23211e] rounded-xl border border-[#e8e4dc] dark:border-[#38332c] text-[10px] font-mono space-y-1 shadow-2xs">
            <div className="flex justify-between text-muted">
              <span>Hạn mức Token</span>
              <span className="font-semibold text-coral-600 dark:text-coral-400">
                {user?.token_quota
                  ? `${Math.round(((user.tokens_used || 0) / user.token_quota) * 100)}%`
                  : "Đầy đủ"}
              </span>
            </div>
            <div className="h-1.5 w-full bg-zinc-200 dark:bg-zinc-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-coral-500 rounded-full transition-all duration-500"
                style={{
                  width: `${
                    user?.token_quota
                      ? Math.min(
                          100,
                          Math.round(((user.tokens_used || 0) / user.token_quota) * 100)
                        )
                      : 10
                  }%`,
                }}
              />
            </div>
          </div>
        )}

        <div
          className={`w-full h-11 flex items-center rounded-xl transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] overflow-hidden ${
            isExpanded
              ? "bg-white dark:bg-[#23211e] border border-[#e8e4dc] dark:border-[#38332c] px-2 shadow-2xs"
              : "bg-transparent border-transparent justify-center p-0"
          }`}
        >
          {/* Avatar box - Fixed size, perfectly centered in collapsed mode */}
          <div
            title={user?.full_name ?? "Nhà nghiên cứu"}
            className="w-7 h-7 rounded-lg bg-coral-500/10 text-coral-600 dark:text-coral-400 flex items-center justify-center font-anthropic-serif font-bold text-xs shrink-0 cursor-pointer"
          >
            {userInitial}
          </div>

          {/* User Details & Controls - Smooth Width & Opacity Transition */}
          <div
            className={`flex items-center justify-between min-w-0 transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] ${
              isExpanded
                ? "flex-1 opacity-100 max-w-[170px] ml-2.5"
                : "max-w-0 opacity-0 ml-0 pointer-events-none"
            }`}
          >
            <div className="flex flex-col truncate pr-1">
              <span className="text-xs font-semibold text-ink dark:text-zinc-100 truncate font-anthropic-serif">
                {user?.full_name ?? "Nhà nghiên cứu"}
              </span>
            </div>

            <div className="flex items-center gap-0.5 shrink-0">
              <button
                type="button"
                onClick={toggleTheme}
                aria-label={isDark ? "Chuyển sang chế độ sáng" : "Chuyển sang chế độ tối"}
                title={isDark ? "Chế độ sáng" : "Chế độ tối"}
                className="text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 p-1.5 rounded-lg hover:bg-[#f4efe6] dark:hover:bg-[#2e2a25] transition-colors cursor-pointer"
              >
                {isDark ? (
                  <Sun className="w-3.5 h-3.5 text-amber-400" />
                ) : (
                  <Moon className="w-3.5 h-3.5 text-zinc-600" />
                )}
              </button>

              <button
                type="button"
                onClick={handleLogout}
                title="Đăng xuất"
                className="text-muted hover:text-coral-600 p-1.5 rounded-lg hover:bg-[#f4efe6] dark:hover:bg-[#2e2a25] transition-colors cursor-pointer shrink-0"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </aside>
  </>
  );
}
