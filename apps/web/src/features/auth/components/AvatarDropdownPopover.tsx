import { useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Settings,
  Sparkles,
  HelpCircle,
  LogOut,
  ChevronRight,
} from "lucide-react";
import { useAuthStore } from "@/features/auth/stores/useAuthStore";
import { getScholarInitials } from "@/features/auth/utils/avatarUtils";
import { cn } from "@/lib/utils";

export interface AvatarDropdownPopoverProps {
  isOpen: boolean;
  onClose: () => void;
  side?: "top" | "bottom";
  align?: "left" | "right";
  className?: string;
  onOpenSettings?: () => void;
}

export function AvatarDropdownPopover({
  isOpen,
  onClose,
  side = "bottom",
  align = "right",
  className,
  onOpenSettings,
}: AvatarDropdownPopoverProps) {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const popoverRef = useRef<HTMLDivElement>(null);

  // Close on Escape or click outside
  useEffect(() => {
    if (!isOpen) return;

    const handlePointerDown = (e: PointerEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };

    // Delay slightly to prevent the toggle click itself from triggering close
    const timer = setTimeout(() => {
      window.addEventListener("pointerdown", handlePointerDown);
    }, 10);
    window.addEventListener("keydown", handleKeyDown);

    return () => {
      clearTimeout(timer);
      window.removeEventListener("pointerdown", handlePointerDown);
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const initials = getScholarInitials(user?.full_name, user?.email);

  return (
    <>
      {/* Floating Backdrop Layer (Rule Item 3 - Floating overlay above all taskbar layers) */}
      <div
        className="fixed inset-0 z-[95] bg-black/5 dark:bg-black/20 backdrop-blur-[0.5px] transition-opacity cursor-default"
        onClick={onClose}
        aria-hidden="true"
        data-testid="avatar-popover-backdrop"
      />

      <div
        ref={popoverRef}
        role="menu"
        aria-label="Tùy chọn người dùng"
        data-testid="avatar-dropdown-popover"
        className={cn(
          "fixed z-[100] w-64 p-1.5 rounded-2xl bg-white dark:bg-[#201e1b] border border-hairline dark:border-[#38332c] shadow-[0_20px_50px_rgba(0,0,0,0.3)] backdrop-blur-md animate-in fade-in zoom-in-95 duration-150 select-none text-ink dark:text-zinc-100",
          className
        )}
        onClick={(e) => e.stopPropagation()}
      >
      {/* 1. Header Card: [Avatar] Dam Manh Dung • Tài khoản cá nhân / email kèm ChevronRight */}
      <button
        type="button"
        role="menuitem"
        data-testid="popover-header-card"
        onClick={() => {
          onClose();
          navigate("/profile");
        }}
        className="w-full p-2 rounded-xl flex items-center gap-2.5 text-left hover:bg-[#f4efe6] dark:hover:bg-[#2c2925] transition-colors cursor-pointer group"
      >
        <div className="w-8 h-8 rounded-full overflow-hidden border border-hairline dark:border-[#38332c] shrink-0 flex items-center justify-center bg-stone-100 dark:bg-[#2b2722]">
          {user?.avatar_url ? (
            <img
              src={user.avatar_url}
              alt={user.full_name || "Scholar avatar"}
              className="w-full h-full object-cover"
              referrerPolicy="no-referrer"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center font-serif font-bold text-xs bg-gradient-to-br from-amber-700 via-amber-800 to-amber-950 text-amber-100 dark:from-amber-600 dark:to-amber-800">
              {initials}
            </div>
          )}
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-xs font-semibold text-ink dark:text-zinc-100 truncate font-serif">
            {user?.full_name || "Dam Manh Dung"}
          </p>
          <p className="text-3xs text-muted dark:text-zinc-400 truncate font-mono">
            {user?.email || "Tài khoản cá nhân"}
          </p>
        </div>
        <ChevronRight className="w-4 h-4 text-muted group-hover:text-ink dark:group-hover:text-zinc-200 transition-colors shrink-0" />
      </button>

      {/* Divider */}
      <div className="my-1 border-b border-hairline/80 dark:border-[#2f2b26]" />

      {/* 2. Action List */}
      <div className="space-y-0.5">
        {/* Nâng cấp gói */}
        <button
          type="button"
          role="menuitem"
          data-testid="popover-upgrade-btn"
          onClick={() => {
            onClose();
            if (onOpenSettings) {
              onOpenSettings();
            } else {
              navigate("/settings");
            }
          }}
          className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium text-ink dark:text-zinc-200 hover:bg-[#f4efe6] dark:hover:bg-[#2c2925] hover:text-primary transition-colors cursor-pointer text-left"
        >
          <Sparkles className="w-4 h-4 text-amber-500 shrink-0" />
          <span>Nâng cấp gói</span>
        </button>

        {/* Cài đặt */}
        <button
          type="button"
          role="menuitem"
          data-testid="popover-settings-btn"
          onClick={() => {
            onClose();
            if (onOpenSettings) {
              onOpenSettings();
            } else {
              navigate("/settings");
            }
          }}
          className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium text-ink dark:text-zinc-200 hover:bg-[#f4efe6] dark:hover:bg-[#2c2925] hover:text-primary transition-colors cursor-pointer text-left"
        >
          <Settings className="w-4 h-4 text-zinc-500 dark:text-zinc-400 shrink-0" />
          <span>Cài đặt</span>
        </button>
      </div>

      {/* Divider */}
      <div className="my-1 border-b border-hairline/80 dark:border-[#2f2b26]" />

      {/* 3. Footer List */}
      <div className="space-y-0.5">
        {/* Trợ giúp */}
        <button
          type="button"
          role="menuitem"
          data-testid="popover-help-btn"
          onClick={() => {
            onClose();
          }}
          className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium text-ink dark:text-zinc-200 hover:bg-[#f4efe6] dark:hover:bg-[#2c2925] hover:text-primary transition-colors cursor-pointer text-left"
        >
          <HelpCircle className="w-4 h-4 text-zinc-500 dark:text-zinc-400 shrink-0" />
          <span>Trợ giúp</span>
        </button>

        {/* Đăng xuất */}
        <button
          type="button"
          role="menuitem"
          data-testid="popover-logout-btn"
          onClick={() => {
            onClose();
            logout();
            navigate("/login");
          }}
          className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium text-rose-600 dark:text-rose-400 hover:bg-rose-500/10 hover:text-rose-700 dark:hover:text-rose-300 transition-colors cursor-pointer text-left"
        >
          <LogOut className="w-4 h-4 text-rose-500 shrink-0" />
          <span>Đăng xuất</span>
        </button>
      </div>
    </div>
  </>
  );
}
