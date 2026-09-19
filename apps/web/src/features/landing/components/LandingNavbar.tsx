import { ArrowUpRight, Sparkles, Sun, Moon } from "lucide-react";
import { AcademicLogo } from "@/components/shared/AcademicLogo";
import { Button } from "@/components/ui/button";
import { useLandingStore } from "../stores/useLandingStore";
import { useTheme } from "@/hooks/useTheme";

export function LandingNavbar() {
  const setUploadModalOpen = useLandingStore((s) => s.setUploadModalOpen);
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === "dark";

  return (
    <header className="sticky top-0 z-40 w-full h-18 sm:h-20 bg-canvas/85 backdrop-blur-md border-b border-hairline/80 transition-colors">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-full flex items-center justify-between">
        {/* Logo - Wider & Clearly Visible */}
        <a href="#" className="flex items-center focus:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-sm py-1">
          <AcademicLogo size="xl" inverted={isDark} />
        </a>

        {/* Action Cluster - GitHub, "Dùng thử ngay", & Theme Toggle */}
        <div className="flex items-center gap-2.5 sm:gap-3">
          <a
            href="https://github.com/dammanhdungvn/VeriScholar"
            target="_blank"
            rel="noopener noreferrer"
            data-testid="nav-github-link"
            className="inline-flex items-center justify-center w-8 h-8 sm:w-9 sm:h-9 rounded-md border border-hairline bg-canvas hover:bg-surface-soft text-body hover:text-ink transition-colors shadow-2xs group focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
            aria-label="GitHub Repository"
            title="GitHub Repository"
          >
            <svg className="w-4 h-4 sm:w-4.5 sm:h-4.5 fill-current transition-transform group-hover:scale-110" viewBox="0 0 24 24" aria-hidden="true">
              <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
            </svg>
          </a>

          <Button
            variant="primary"
            size="sm"
            onClick={() => setUploadModalOpen(true)}
            data-testid="nav-try-btn"
            className="group text-xs sm:text-sm cursor-pointer shadow-xs whitespace-nowrap shrink-0"
          >
            <Sparkles className="w-3.5 h-3.5 text-on-primary transition-transform group-hover:scale-110" />
            <span>Dùng thử ngay</span>
            <ArrowUpRight className="w-3 h-3 text-on-primary/80 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
          </Button>

          {/* Theme Toggle Button (Light/Dark Mode) — Strictly positioned to the right of "Dùng thử ngay" */}
          <button
            type="button"
            onClick={toggleTheme}
            data-testid="theme-toggle-btn"
            aria-label={isDark ? "Chuyển sang chế độ sáng" : "Chuyển sang chế độ tối"}
            title={isDark ? "Chuyển sang chế độ sáng" : "Chuyển sang chế độ tối"}
            className="inline-flex items-center justify-center w-8 h-8 sm:w-9 sm:h-9 rounded-md border border-hairline bg-canvas hover:bg-surface-soft text-body hover:text-ink transition-colors shadow-2xs cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-primary shrink-0"
          >
            {isDark ? (
              <Sun className="w-4 h-4 sm:w-4.5 sm:h-4.5 text-amber-400 transition-transform hover:rotate-45" />
            ) : (
              <Moon className="w-4 h-4 sm:w-4.5 sm:h-4.5 text-zinc-600 transition-transform hover:-rotate-12" />
            )}
          </button>
        </div>
      </div>
    </header>
  );
}
