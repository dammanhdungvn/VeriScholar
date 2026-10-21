import { Link } from "react-router-dom";
import {
  PanelLeft,
  MessageSquare,
  Briefcase,
  Library,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface WritingIconRailProps {
  onToggleFileTree: () => void;
  isFileTreeOpen: boolean;
  onOpenSettings?: () => void;
}

export function WritingIconRail({
  onToggleFileTree,
  isFileTreeOpen,
  onOpenSettings,
}: WritingIconRailProps) {
  return (
    <aside
      data-testid="writing-icon-rail"
      className="hidden md:flex w-12 shrink-0 bg-[#f4eee5] dark:bg-[#161513] border-r border-[#e5dfd4] dark:border-[#2a2824] flex-col items-center justify-between py-3 select-none z-30"
    >
      {/* Top Group: Brand Logo & Navigation */}
      <div className="flex flex-col items-center gap-3 w-full">
        {/* Brand Logo - Navigates back to Dashboard */}
        <Link
          to="/dashboard"
          data-testid="rail-logo-btn"
          title="VeriScholar — Quay về Trang chủ / Dashboard"
          className="w-8 h-8 rounded-xl bg-coral-500 text-white flex items-center justify-center shadow-xs hover:bg-coral-600 transition-transform active:scale-95 group"
        >
          <span className="font-serif font-black text-sm tracking-tight group-hover:scale-105 transition-transform">
            V
          </span>
        </Link>

        <div className="w-6 h-px bg-[#e5dfd4] dark:bg-[#2a2824] my-1" />

        {/* Toggle File Tree / Outline Sidebar */}
        <button
          type="button"
          data-testid="toggle-file-tree-btn"
          onClick={onToggleFileTree}
          title={isFileTreeOpen ? "Thu gọn danh sách tệp & dàn ý" : "Mở danh sách tệp & dàn ý (Sidebar)"}
          className={cn(
            "w-8 h-8 rounded-lg flex items-center justify-center transition-colors cursor-pointer",
            isFileTreeOpen
              ? "bg-white dark:bg-[#24221e] text-coral-600 dark:text-coral-400 shadow-2xs border border-[#e2dcd2] dark:border-[#33302b]"
              : "text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#eae4d9] dark:hover:bg-[#252320]"
          )}
        >
          <PanelLeft className="w-4 h-4" />
        </button>

        {/* Quick Switcher: Chat */}
        <Link
          to="/dashboard"
          data-testid="rail-nav-chat"
          title="Chuyển đến Đoạn chat Socratic (Chat)"
          className="w-8 h-8 rounded-lg flex items-center justify-center text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#eae4d9] dark:hover:bg-[#252320] transition-colors"
        >
          <MessageSquare className="w-4 h-4" />
        </Link>

        {/* Quick Switcher: Project */}
        <Link
          to="/dashboard"
          data-testid="rail-nav-project"
          title="Chuyển đến Quản lý Dự án (Project)"
          className="w-8 h-8 rounded-lg flex items-center justify-center text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#eae4d9] dark:hover:bg-[#252320] transition-colors"
        >
          <Briefcase className="w-4 h-4" />
        </Link>

        {/* Quick Switcher: Library */}
        <Link
          to="/dashboard"
          data-testid="rail-nav-library"
          title="Chuyển đến Thư viện Tài liệu (Library)"
          className="w-8 h-8 rounded-lg flex items-center justify-center text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#eae4d9] dark:hover:bg-[#252320] transition-colors"
        >
          <Library className="w-4 h-4" />
        </Link>
      </div>

      {/* Bottom Group: Settings & Assistant */}
      <div className="flex flex-col items-center gap-2 w-full">
        <button
          type="button"
          data-testid="rail-settings-btn"
          onClick={onOpenSettings}
          title="Cài đặt biên dịch & định dạng bài báo"
          className="w-8 h-8 rounded-lg flex items-center justify-center text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#eae4d9] dark:hover:bg-[#252320] transition-colors cursor-pointer"
        >
          <Settings className="w-4 h-4" />
        </button>
      </div>
    </aside>
  );
}
