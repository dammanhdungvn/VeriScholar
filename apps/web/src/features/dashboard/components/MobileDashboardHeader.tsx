import { useState } from "react";
import { Link } from "react-router-dom";
import { Menu, Sun, Moon } from "lucide-react";
import { AcademicLogo } from "@/components/shared/AcademicLogo";
import { useTheme } from "@/hooks/useTheme";
import { useAuthStore } from "@/features/auth/stores/useAuthStore";
import { AvatarDropdownPopover } from "@/features/auth/components/AvatarDropdownPopover";
import { AccountSettingsModal } from "@/features/auth/components/AccountSettingsModal";
import { getScholarInitials } from "@/features/auth/utils/avatarUtils";
import { cn } from "@/lib/utils";

interface MobileDashboardHeaderProps {
  onToggleSidebar: () => void;
  onNewSession?: () => void;
}

export function MobileDashboardHeader({
  onToggleSidebar,
  onNewSession: _onNewSession,
}: MobileDashboardHeaderProps) {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === "dark";
  const { user } = useAuthStore();
  const [isAvatarDropdownOpen, setIsAvatarDropdownOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  return (
    <>
      <header
        data-testid="mobile-dashboard-header"
        className={cn(
          "sticky top-0 md:hidden w-full h-13 px-3 bg-[#faf9f5]/95 dark:bg-[#181715]/95 backdrop-blur-md border-b border-[#e8e4dc] dark:border-[#2a2824] flex items-center justify-between select-none shrink-0 transition-all",
          isAvatarDropdownOpen ? "z-50" : "z-40"
        )}
      >
        {/* Left: Hamburger Menu (3 gạch) touch target >= 44px */}
        <button
          type="button"
          onClick={onToggleSidebar}
          aria-label="Mở menu điều hướng"
          title="Mở menu điều hướng"
          data-testid="mobile-header-menu-btn"
          className="min-h-[44px] min-w-[44px] w-11 h-11 flex items-center justify-center rounded-xl text-ink dark:text-zinc-200 hover:bg-[#f2ece1] dark:hover:bg-[#262420] transition-colors cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
        >
          <Menu className="w-5 h-5 text-coral-600 dark:text-coral-400 stroke-[2.2]" />
        </button>

        {/* Center: Logo học thuật và tên VeriScholar trang nhã */}
        <Link
          to="/"
          className="flex items-center min-h-[44px] focus:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-md py-1"
          aria-label="VeriScholar Trang chủ"
        >
          <AcademicLogo size="md" inverted={isDark} />
        </Link>

        {/* Right Action Cluster: Theme Toggle, Avatar */}
        <div className="flex items-center gap-1 shrink-0">

          {/* Nút chuyển đổi Theme Sáng / Tối */}
          <button
            type="button"
            onClick={toggleTheme}
            data-testid="mobile-header-theme-toggle"
            aria-label={isDark ? "Chuyển sang chế độ sáng" : "Chuyển sang chế độ tối"}
            title={isDark ? "Chế độ sáng" : "Chế độ tối"}
            className="min-h-[44px] min-w-[44px] w-10 h-10 flex items-center justify-center rounded-xl text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 hover:bg-[#f2ece1] dark:hover:bg-[#262420] transition-colors cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
          >
            {isDark ? (
              <Sun className="w-4.5 h-4.5 text-amber-400" />
            ) : (
              <Moon className="w-4.5 h-4.5 text-zinc-600" />
            )}
          </button>

          {/* Avatar người dùng với AvatarDropdownPopover */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setIsAvatarDropdownOpen((prev) => !prev)}
              data-testid="mobile-header-avatar-btn"
              aria-label="Tùy chọn tài khoản"
              title={user?.full_name ? `${user.full_name} — Tùy chọn tài khoản` : "Tùy chọn tài khoản"}
              className="min-h-[44px] min-w-[44px] w-9 h-9 flex items-center justify-center rounded-xl p-0.5 cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-primary shrink-0"
            >
              {user?.avatar_url ? (
                <img
                  src={user.avatar_url}
                  alt={user.full_name || "Scholar avatar"}
                  className="w-8 h-8 object-cover rounded-lg"
                  referrerPolicy="no-referrer"
                />
              ) : (
                <div className="w-8 h-8 rounded-lg bg-coral-500/10 text-coral-600 dark:text-coral-400 flex items-center justify-center font-anthropic-serif font-bold text-xs border border-coral-500/20">
                  {getScholarInitials(user?.full_name, user?.email)}
                </div>
              )}
            </button>

            <AvatarDropdownPopover
              isOpen={isAvatarDropdownOpen}
              onClose={() => setIsAvatarDropdownOpen(false)}
              onOpenSettings={() => setIsSettingsOpen(true)}
              side="bottom"
              align="right"
            />
          </div>
        </div>
      </header>

      {/* Account Settings Modal */}
      <AccountSettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />
    </>
  );
}
