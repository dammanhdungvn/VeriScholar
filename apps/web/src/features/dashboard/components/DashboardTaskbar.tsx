import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Plus,
  MessageSquare,
  Library,
  FolderKanban,
  LogOut,
  PanelLeftClose,
  PanelLeft
} from "lucide-react";
import { AcademicLogo } from "@/components/shared/AcademicLogo";
import { useDashboardStore } from "../stores/useDashboardStore";
import { useAuthStore } from "@/features/auth/stores/useAuthStore";
import { useTheme } from "@/hooks/useTheme";
import type { SessionItem } from "@/types/dashboard";

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
  const { theme } = useTheme();
  const isDark = theme === "dark";
  const { user, logout } = useAuthStore();
  const sidebarState = useDashboardStore((s) => s.sidebarState);
  const toggleSidebar = useDashboardStore((s) => s.toggleSidebar);
  const [isToggleHovered, setIsToggleHovered] = useState(false);

  const isExpanded = sidebarState === "expanded";

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const userInitial = user?.full_name
    ? user.full_name.charAt(0).toUpperCase()
    : "V";

  return (
    <aside
      aria-label="Thanh điều hướng chính"
      className={`h-screen border-r border-[#e8e4dc] dark:border-[#2e2b26] bg-[#fbf9f5] dark:bg-[#1c1b18] flex flex-col justify-between select-none z-30 transition-[width] duration-200 ease-in-out shrink-0 overflow-hidden ${
        isExpanded ? "w-64" : "w-14"
      }`}
    >
      {/* 1. Top Section */}
      <div className="flex flex-col w-full">
        {/* Top Header Row */}
        <div className="h-14 px-3 flex items-center justify-between border-b border-[#ece8df] dark:border-[#2a2824]">
          {isExpanded ? (
            <div className="flex items-center justify-between w-full">
              <Link to="/" className="flex items-center gap-2.5 focus:outline-none group">
                <AcademicLogo size="sm" inverted={isDark} />
              </Link>
              <button
                type="button"
                onClick={toggleSidebar}
                aria-label="Thu gọn thanh điều hướng"
                title="Thu gọn sidebar"
                className="w-7 h-7 flex items-center justify-center text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-surface-cream-strong dark:hover:bg-[#282623] rounded-lg transition-colors cursor-pointer focus:outline-none"
              >
                <PanelLeftClose className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center justify-center w-full">
              <button
                type="button"
                onClick={toggleSidebar}
                onMouseEnter={() => setIsToggleHovered(true)}
                onMouseLeave={() => setIsToggleHovered(false)}
                aria-label="Mở rộng thanh điều hướng"
                title="Mở rộng sidebar"
                className="w-9 h-9 flex items-center justify-center rounded-xl transition-colors cursor-pointer relative text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#f2ece1] dark:hover:bg-[#262420] focus:outline-none"
              >
                {isToggleHovered ? (
                  <PanelLeft className="w-4.5 h-4.5 text-coral-600 dark:text-coral-400" />
                ) : (
                  <AcademicLogo size="sm" showWordmark={false} inverted={isDark} />
                )}
              </button>
            </div>
          )}
        </div>

        {/* Action Controls */}
        <div className="p-2 space-y-1.5">
          {/* 1. New Chat Button */}
          <button
            type="button"
            onClick={onNewSession}
            title="Đoạn chat mới"
            className={`h-9 flex items-center rounded-xl text-xs font-sans font-medium transition-colors shadow-xs cursor-pointer overflow-hidden focus:outline-none ${
              isExpanded
                ? "w-full px-3 text-white bg-coral-500 hover:bg-coral-600 gap-2"
                : "w-9 mx-auto p-0 justify-center text-white bg-coral-500 hover:bg-coral-600"
            }`}
          >
            <Plus className="w-4 h-4 shrink-0" />
            {isExpanded && (
              <span className="font-medium whitespace-nowrap truncate">
                Đoạn chat mới
              </span>
            )}
          </button>

          {/* 2. Library Button */}
          <button
            type="button"
            onClick={onOpenLibrary}
            title="Thư viện tài liệu nghiên cứu"
            className={`h-9 flex items-center rounded-xl text-xs font-sans text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#f2ece1] dark:hover:bg-[#262420] transition-colors cursor-pointer overflow-hidden focus:outline-none ${
              isExpanded ? "w-full px-3 gap-2" : "w-9 mx-auto p-0 justify-center"
            }`}
          >
            <Library className="w-4 h-4 shrink-0 text-coral-600 dark:text-coral-400" />
            {isExpanded && (
              <span className="truncate whitespace-nowrap">Thư viện</span>
            )}
          </button>

          {/* 3. Projects Button */}
          <button
            type="button"
            onClick={onOpenProjects}
            title="Dự án nghiên cứu"
            className={`h-9 flex items-center rounded-xl text-xs font-sans text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#f2ece1] dark:hover:bg-[#262420] transition-colors cursor-pointer overflow-hidden focus:outline-none ${
              isExpanded ? "w-full px-3 gap-2" : "w-9 mx-auto p-0 justify-center"
            }`}
          >
            <FolderKanban className="w-4 h-4 shrink-0 text-coral-600 dark:text-coral-400" />
            {isExpanded && (
              <span className="truncate whitespace-nowrap">Dự án</span>
            )}
          </button>
        </div>

        {/* Divider between Actions & Recent Sessions */}
        <div className="px-2 py-1">
          <div className="border-t border-[#ece8df] dark:border-[#2a2824]" />
        </div>

        {/* Sessions List (Expanded) or Quick Icons (Collapsed) */}
        {isExpanded ? (
          <div className="px-2 pt-1 pb-1 overflow-y-auto max-h-[calc(100vh-280px)] space-y-1 custom-scrollbar">
            {sessions.slice(0, 3).map((session) => {
              const isActive = session.id === activeSessionId;
              return (
                <button
                  key={session.id}
                  type="button"
                  onClick={() => onSelectSession(session.id)}
                  title={session.title}
                  className={`w-full text-left flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-xs transition-colors cursor-pointer group relative overflow-hidden focus:outline-none ${
                    isActive
                      ? "bg-white dark:bg-[#282622] text-ink dark:text-zinc-100 font-medium shadow-xs border border-[#e8e4dc] dark:border-[#38342e]"
                      : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-200 hover:bg-[#f4efe6] dark:hover:bg-[#24221e]"
                  }`}
                >
                  {isActive && (
                    <span className="absolute left-1 top-2.5 bottom-2.5 w-1 rounded-full bg-coral-500" />
                  )}
                  <MessageSquare
                    className={`w-3.5 h-3.5 shrink-0 ${
                      isActive ? "text-coral-500" : "text-muted dark:text-zinc-500 group-hover:text-coral-500"
                    }`}
                  />
                  <span className="truncate flex-1 whitespace-nowrap">{session.title}</span>
                </button>
              );
            })}
          </div>
        ) : (
          <div className="flex flex-col items-center gap-1.5 pt-1">
            {sessions.slice(0, 3).map((session) => {
              const isActive = session.id === activeSessionId;
              return (
                <button
                  key={session.id}
                  type="button"
                  onClick={() => onSelectSession(session.id)}
                  title={session.title}
                  className={`w-9 h-9 flex items-center justify-center rounded-xl transition-colors cursor-pointer relative focus:outline-none ${
                    isActive
                      ? "bg-white dark:bg-[#282622] text-coral-500 shadow-xs border border-[#e8e4dc] dark:border-[#38342e]"
                      : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#f2ece1] dark:hover:bg-[#262420]"
                  }`}
                >
                  {isActive && (
                    <span className="absolute left-0.5 top-2.5 bottom-2.5 w-0.5 rounded-full bg-coral-500" />
                  )}
                  <MessageSquare className="w-4 h-4" />
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* 2. Bottom Rail: User Profile */}
      <div className="p-2 border-t border-[#ece8df] dark:border-[#2a2824]">
        {isExpanded ? (
          <div className="flex items-center justify-between p-2 rounded-xl bg-white dark:bg-[#23211e] border border-[#e8e4dc] dark:border-[#38332c] shadow-2xs">
            <div className="flex items-center gap-2.5 truncate pr-1">
              <div className="w-7 h-7 rounded-lg bg-coral-500/10 text-coral-600 dark:text-coral-400 flex items-center justify-center font-sans font-semibold text-xs shrink-0">
                {userInitial}
              </div>
              <div className="flex flex-col truncate">
                <span className="text-xs font-medium text-ink dark:text-zinc-100 truncate">
                  {user?.full_name ?? "Nhà nghiên cứu"}
                </span>
              </div>
            </div>
            <button
              type="button"
              onClick={handleLogout}
              title="Đăng xuất"
              className="text-muted hover:text-coral-600 p-1.5 rounded-lg hover:bg-[#f4efe6] dark:hover:bg-[#2e2a25] transition-colors cursor-pointer shrink-0"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-1.5">
            <div
              title={user?.full_name ?? "Nhà nghiên cứu"}
              className="w-8 h-8 rounded-lg bg-coral-500/10 text-coral-600 dark:text-coral-400 flex items-center justify-center font-sans font-semibold text-xs cursor-pointer shadow-2xs"
            >
              {userInitial}
            </div>
            <button
              type="button"
              onClick={handleLogout}
              title="Đăng xuất"
              className="w-8 h-8 flex items-center justify-center text-muted hover:text-coral-600 hover:bg-[#f4efe6] dark:hover:bg-[#282623] rounded-lg transition-colors cursor-pointer"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>
    </aside>
  );
}
