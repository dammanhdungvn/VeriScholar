import { useState } from "react";
import { ArrowUpRight, Sparkles, Sun, Moon, LayoutDashboard, User } from "lucide-react";
import { Link } from "react-router-dom";
import { AcademicLogo } from "@/components/shared/AcademicLogo";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/hooks/useTheme";
import { useAuthStore } from "@/features/auth/stores/useAuthStore";
import { AccountSettingsModal } from "@/features/auth/components/AccountSettingsModal";

export function LandingNavbar() {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === "dark";
  const { isAuthenticated, user } = useAuthStore();
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);


  return (
    <header className="sticky top-2.5 sm:top-4 z-40 w-full px-4 sm:px-6 pointer-events-none transition-all duration-300">
      <div className="max-w-5xl mx-auto h-15 sm:h-16 px-4 sm:px-5 rounded-2xl bg-canvas/80 dark:bg-[#22201c]/80 backdrop-blur-2xl border border-hairline/90 dark:border-[#3a342b]/70 shadow-sm dark:shadow-[0_8px_32px_rgba(0,0,0,0.32)] flex items-center justify-between pointer-events-auto transition-all">
        {/* Logo - Wider & Clearly Visible */}
        <Link
          to="/"
          className="flex items-center focus:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-md py-1"
          aria-label="VeriScholar Trang chủ"
        >
          <AcademicLogo size="xl" inverted={isDark} />
        </Link>

        {/* Action Cluster - GitHub, User / "Dùng thử ngay", & Theme Toggle */}
        <div className="flex items-center gap-1.5 sm:gap-2.5">
          <a
            href="https://github.com/dammanhdungvn/VeriScholar"
            target="_blank"
            rel="noopener noreferrer"
            data-testid="nav-github-link"
            className="inline-flex items-center justify-center w-8 h-8 sm:w-9 sm:h-9 rounded-lg border border-hairline dark:border-[#423c34] bg-canvas dark:bg-[#2d2924] hover:bg-surface-soft dark:hover:bg-[#38332c] text-body hover:text-ink dark:text-zinc-200 dark:hover:text-white transition-colors shadow-2xs group focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
            aria-label="GitHub Repository"
            title="GitHub Repository"
          >
            <svg className="w-4 h-4 sm:w-4.5 sm:h-4.5 fill-current transition-transform group-hover:scale-110" viewBox="0 0 24 24" aria-hidden="true">
              <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
            </svg>
          </a>

          {/* Primary Action Button:
              - Authenticated: Navigates directly to /dashboard ("Dashboard")
              - Guest/Unauthenticated: Navigates to /login ("Dùng thử ngay")
          */}
          {isAuthenticated ? (
            <Button
              asChild
              variant="primary"
              size="sm"
              data-testid="nav-try-btn"
              className="group text-xs sm:text-sm cursor-pointer shadow-xs whitespace-nowrap shrink-0 rounded-lg"
            >
              <Link to="/dashboard">
                <LayoutDashboard className="w-3.5 h-3.5 text-on-primary transition-transform group-hover:scale-110" />
                <span>Dashboard</span>
                <ArrowUpRight className="w-3 h-3 text-on-primary/80 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
              </Link>
            </Button>
          ) : (
            <Button
              asChild
              variant="primary"
              size="sm"
              data-testid="nav-try-btn"
              className="group text-xs sm:text-sm cursor-pointer shadow-xs whitespace-nowrap shrink-0 rounded-lg"
            >
              <Link to="/login">
                <Sparkles className="w-3.5 h-3.5 text-on-primary transition-transform group-hover:scale-110" />
                <span>Dùng thử ngay</span>
                <ArrowUpRight className="w-3 h-3 text-on-primary/80 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
              </Link>
            </Button>
          )}

          {/* User Settings Button (When Authenticated) */}
          {isAuthenticated && (
            <button
              type="button"
              onClick={() => setIsSettingsOpen(true)}
              data-testid="nav-settings-btn"
              aria-label="Cài đặt tài khoản"
              title={user?.full_name ? `${user.full_name} — Cài đặt tài khoản` : "Cài đặt tài khoản"}
              className="inline-flex items-center justify-center w-8 h-8 sm:w-9 sm:h-9 rounded-lg border border-hairline dark:border-[#423c34] bg-canvas dark:bg-[#2d2924] hover:bg-surface-soft dark:hover:bg-[#38332c] text-body hover:text-ink dark:text-zinc-200 dark:hover:text-white transition-colors shadow-2xs cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-primary shrink-0"
            >
              <User className="w-4 h-4 sm:w-4.5 sm:h-4.5" />
            </button>
          )}

          {/* Theme Toggle Button (Light/Dark Mode) — Strictly positioned to the right of "Dùng thử ngay" */}
          <button
            type="button"
            onClick={toggleTheme}
            data-testid="theme-toggle-btn"
            aria-label={isDark ? "Chuyển sang chế độ sáng" : "Chuyển sang chế độ tối"}
            title={isDark ? "Chuyển sang chế độ sáng" : "Chuyển sang chế độ tối"}
            className="inline-flex items-center justify-center w-8 h-8 sm:w-9 sm:h-9 rounded-lg border border-hairline dark:border-[#423c34] bg-canvas dark:bg-[#2d2924] hover:bg-surface-soft dark:hover:bg-[#38332c] text-body hover:text-ink dark:text-zinc-200 dark:hover:text-white transition-colors shadow-2xs cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-primary shrink-0"
          >
            {isDark ? (
              <Sun className="w-4 h-4 sm:w-4.5 sm:h-4.5 text-amber-400 transition-transform hover:rotate-45" />
            ) : (
              <Moon className="w-4 h-4 sm:w-4.5 sm:h-4.5 text-zinc-600 transition-transform hover:-rotate-12" />
            )}
          </button>
        </div>
      </div>

      {/* Account Settings Modal */}
      <AccountSettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />
    </header>

  );
}
