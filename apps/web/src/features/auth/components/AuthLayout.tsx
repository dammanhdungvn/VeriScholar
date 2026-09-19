import { Outlet, Link } from "react-router-dom";
import { AcademicLogo } from "@/components/shared/AcademicLogo";
import { useTheme } from "@/hooks/useTheme";
import { AtmosphericBackground } from "@/features/landing/components/AtmosphericBackground";
import { ArrowLeft, Sun, Moon } from "lucide-react";

export function AuthLayout() {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === "dark";

  return (
    <div className="relative min-h-screen w-full flex flex-col justify-between bg-canvas text-ink font-sans antialiased selection:bg-primary/20 selection:text-ink overflow-x-hidden">
      {/* 1. Reuse Signature Atmospheric Background from Landing Page */}
      <AtmosphericBackground />

      {/* 2. Top Minimal Utility Bar: Back to Home + Theme Switcher */}
      <header className="relative z-20 w-full max-w-5xl mx-auto px-4 sm:px-6 py-4 sm:py-6 flex items-center justify-between pointer-events-auto">
        {/* Back to Home Link */}
        <Link
          to="/"
          data-testid="auth-back-link"
          className="inline-flex items-center gap-1.5 text-xs font-sans text-muted hover:text-ink dark:text-[#9c988f] dark:hover:text-[#f5f3ed] transition-colors group px-2.5 py-1.5 rounded-lg hover:bg-surface-soft dark:hover:bg-[#201e1b] border border-transparent hover:border-hairline dark:hover:border-[#38332c]"
        >
          <ArrowLeft className="w-3.5 h-3.5 transition-transform group-hover:-translate-x-0.5" />
          <span>Về trang chủ</span>
        </Link>

        {/* Theme Toggle Button (Synchronized with Landing Page) */}
        <button
          type="button"
          onClick={toggleTheme}
          data-testid="auth-theme-toggle"
          aria-label={isDark ? "Chuyển sang chế độ sáng" : "Chuyển sang chế độ tối"}
          title={isDark ? "Chuyển sang chế độ sáng" : "Chuyển sang chế độ tối"}
          className="inline-flex items-center justify-center w-8 h-8 sm:w-9 sm:h-9 rounded-lg border border-hairline dark:border-[#38332c] bg-canvas/80 dark:bg-[#201e1b]/80 backdrop-blur-md hover:bg-surface-soft dark:hover:bg-[#282522] text-body dark:text-zinc-200 transition-colors shadow-2xs cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
        >
          {isDark ? (
            <Sun className="w-4 h-4 sm:w-4.5 sm:h-4.5 text-amber-400 transition-transform hover:rotate-45" />
          ) : (
            <Moon className="w-4 h-4 sm:w-4.5 sm:h-4.5 text-zinc-600 transition-transform hover:-rotate-12" />
          )}
        </button>
      </header>

      {/* 3. Centered Editorial Auth Card with Cohesive Brand Logo Anchor */}
      <main className="relative z-10 w-full max-w-[460px] mx-auto px-4 py-4 sm:py-6 my-auto flex flex-col items-center pointer-events-auto">
        {/* Brand Logo - Strictly Centered on the exact vertical axis of the Form */}
        <Link
          to="/"
          data-testid="auth-brand-logo"
          className="mb-5 flex items-center justify-center focus:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-lg py-1 hover:opacity-90 transition-opacity"
          aria-label="VeriScholar Trang chủ"
        >
          <AcademicLogo size="xl" inverted={isDark} />
        </Link>

        {/* The Auth Card: expanded to max-w-[460px] (+12px) for breathing room */}
        <div className="w-full bg-canvas/90 dark:bg-[#1e1c18]/90 backdrop-blur-2xl border border-hairline/90 dark:border-[#3a342b]/80 rounded-2xl p-6 sm:p-8 shadow-sm dark:shadow-[0_16px_48px_rgba(0,0,0,0.4)] transition-all">
          <Outlet />
        </div>
      </main>

      {/* 4. Bottom Subtle Spacer for Vertical Balance */}
      <div className="h-10 sm:h-12 pointer-events-none" aria-hidden="true" />
    </div>
  );
}
