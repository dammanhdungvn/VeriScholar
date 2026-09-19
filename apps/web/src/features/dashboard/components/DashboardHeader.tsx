import { Sun, Moon } from "lucide-react";
import { useTheme } from "@/hooks/useTheme";

interface DashboardHeaderProps {
  sessionTitle?: string;
}

export function DashboardHeader({ sessionTitle }: DashboardHeaderProps) {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === "dark";

  return (
    <header className="h-11 w-full px-4 border-b border-hairline/80 dark:border-[#282622] flex items-center justify-between bg-canvas/80 dark:bg-[#181715]/80 backdrop-blur-md shrink-0 select-none z-10">
      {/* Left: Active Session Title */}
      <div className="flex items-center gap-2 text-xs font-sans">
        {sessionTitle && (
          <span className="text-muted dark:text-zinc-400 font-medium truncate max-w-xs sm:max-w-md">
            {sessionTitle}
          </span>
        )}
      </div>

      {/* Right Controls: Theme Toggle */}
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={toggleTheme}
          aria-label={isDark ? "Chuyển sang chế độ sáng" : "Chuyển sang chế độ tối"}
          title={isDark ? "Chế độ sáng" : "Chế độ tối"}
          className="inline-flex items-center justify-center w-7 h-7 rounded-lg border border-hairline dark:border-zinc-700/60 bg-surface-soft/60 dark:bg-[#282623] hover:bg-surface-cream-strong dark:hover:bg-[#322f2b] text-ink dark:text-zinc-200 transition-colors cursor-pointer"
        >
          {isDark ? (
            <Sun className="w-3.5 h-3.5 text-amber-400" />
          ) : (
            <Moon className="w-3.5 h-3.5 text-zinc-600" />
          )}
        </button>
      </div>
    </header>
  );
}
