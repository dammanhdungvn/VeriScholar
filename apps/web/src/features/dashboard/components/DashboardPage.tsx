import { useNavigate, Link } from "react-router-dom";
import { useAuthStore } from "@/features/auth/stores/useAuthStore";
import { AcademicLogo } from "@/components/shared/AcademicLogo";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/hooks/useTheme";
import { AtmosphericBackground } from "@/features/landing/components/AtmosphericBackground";
import { Sun, Moon, LogOut, ArrowLeft, ShieldCheck, UserCheck } from "lucide-react";

export function DashboardPage() {
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === "dark";
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="relative min-h-screen w-full flex flex-col justify-between bg-canvas text-ink font-sans antialiased selection:bg-primary/20 selection:text-ink overflow-x-hidden">
      {/* 1. Atmospheric Ambient Canvas */}
      <AtmosphericBackground />

      {/* 2. Top Header Navigation */}
      <header className="relative z-20 w-full max-w-5xl mx-auto px-4 sm:px-6 py-4 sm:py-6 flex items-center justify-between pointer-events-auto">
        <Link
          to="/"
          data-testid="dashboard-brand-logo"
          className="flex items-center focus:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-md py-1"
          aria-label="VeriScholar Trang chủ"
        >
          <AcademicLogo size="lg" inverted={isDark} />
        </Link>

        <div className="flex items-center gap-2.5">
          <Link
            to="/"
            className="inline-flex items-center gap-1.5 text-xs font-sans text-muted hover:text-ink dark:text-[#9c988f] dark:hover:text-[#f5f3ed] transition-colors px-2.5 py-1.5 rounded-lg hover:bg-surface-soft dark:hover:bg-[#201e1b] border border-transparent hover:border-hairline dark:hover:border-[#38332c]"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Trang chủ</span>
          </Link>

          <button
            type="button"
            onClick={toggleTheme}
            data-testid="dashboard-theme-toggle"
            aria-label={isDark ? "Chuyển sang chế độ sáng" : "Chuyển sang chế độ tối"}
            className="inline-flex items-center justify-center w-8 h-8 sm:w-9 sm:h-9 rounded-lg border border-hairline dark:border-[#38332c] bg-canvas/80 dark:bg-[#201e1b]/80 backdrop-blur-md hover:bg-surface-soft dark:hover:bg-[#282522] text-body dark:text-zinc-200 transition-colors shadow-2xs cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
          >
            {isDark ? (
              <Sun className="w-4 h-4 text-amber-400" />
            ) : (
              <Moon className="w-4 h-4 text-zinc-600" />
            )}
          </button>

          <Button
            type="button"
            variant="secondary"
            size="sm"
            onClick={handleLogout}
            data-testid="dashboard-logout-btn"
            className="h-8 sm:h-9 px-2.5 sm:px-3 text-xs text-muted hover:text-error border-hairline dark:border-[#38332c] gap-1.5"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Đăng xuất</span>
          </Button>
        </div>
      </header>

      {/* 3. Main Dashboard Body */}
      <main className="relative z-10 w-full max-w-4xl mx-auto px-4 py-8 my-auto pointer-events-auto">
        <div className="bg-canvas/90 dark:bg-[#1e1c18]/90 backdrop-blur-2xl border border-hairline/90 dark:border-[#3a342b]/80 rounded-2xl p-6 sm:p-10 shadow-sm dark:shadow-[0_16px_48px_rgba(0,0,0,0.4)] text-left space-y-6">
          <div className="space-y-2 border-b border-hairline/60 dark:border-[#38332c]/60 pb-5">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-2xs font-mono font-medium bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Không gian nghiên cứu đã xác thực</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-display font-medium text-ink dark:text-[#f5f3ed] tracking-tight">
              Dashboard
            </h1>
            <p className="text-sm text-body dark:text-[#d1ccc2]">
              Chào mừng, {user?.full_name || "Nhà nghiên cứu"}! Phiên làm việc của bạn đang hoạt động.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl border border-hairline dark:border-[#38332c] bg-surface-soft/40 dark:bg-[#201e1b]/40 space-y-1">
              <div className="text-2xs font-sans text-muted dark:text-[#9c988f]">Tài khoản</div>
              <div className="text-sm font-medium text-ink dark:text-zinc-200 flex items-center gap-1.5">
                <UserCheck className="w-4 h-4 text-primary" />
                <span>{user?.email || "scholar@verischolar.ai"}</span>
              </div>
            </div>

            <div className="p-4 rounded-xl border border-hairline dark:border-[#38332c] bg-surface-soft/40 dark:bg-[#201e1b]/40 space-y-1">
              <div className="text-2xs font-sans text-muted dark:text-[#9c988f]">Cơ quan / Đơn vị</div>
              <div className="text-sm font-medium text-ink dark:text-zinc-200">
                {user?.institution || "Viện Hàn lâm Khoa học & Công nghệ"}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* 4. Bottom Spacer */}
      <div className="h-6 pointer-events-none" aria-hidden="true" />
    </div>
  );
}
