import { useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { User, Settings } from "lucide-react";
import { useAuthStore } from "@/features/auth/stores/useAuthStore";
import { getScholarInitials } from "@/features/auth/utils/avatarUtils";
import { cn } from "@/lib/utils";

export interface AvatarDropdownPopoverProps {
  isOpen: boolean;
  onClose: () => void;
  side?: "top" | "bottom";
  align?: "left" | "right";
  className?: string;
}

export function AvatarDropdownPopover({
  isOpen,
  onClose,
  side = "bottom",
  align = "right",
  className,
}: AvatarDropdownPopoverProps) {
  const navigate = useNavigate();
  const { user } = useAuthStore();
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
    <div
      ref={popoverRef}
      role="menu"
      aria-label="Tùy chọn người dùng"
      data-testid="avatar-dropdown-popover"
      className={cn(
        "absolute z-50 w-60 p-1.5 rounded-xl bg-white dark:bg-[#201e1b] border border-hairline dark:border-[#38332c] shadow-xl backdrop-blur-md animate-in fade-in zoom-in-95 duration-150 select-none text-ink dark:text-zinc-100",
        side === "top" ? "bottom-full mb-2" : "top-full mt-2",
        align === "right" ? "right-0" : "left-0",
        className
      )}
      onClick={(e) => e.stopPropagation()}
    >
      {/* Header Info */}
      <div className="px-3 py-2 border-b border-hairline/80 dark:border-[#2f2b26] mb-1 flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-lg overflow-hidden border border-hairline dark:border-[#38332c] shrink-0 flex items-center justify-center bg-stone-100 dark:bg-[#2b2722]">
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
            {user?.full_name || "Nhà nghiên cứu"}
          </p>
          <p className="text-3xs text-muted dark:text-zinc-400 truncate font-mono">
            {user?.email || "scholar@verischolar.ai"}
          </p>
        </div>
      </div>

      {/* Action Options */}
      <div className="space-y-0.5">
        <button
          type="button"
          role="menuitem"
          data-testid="popover-profile-btn"
          onClick={() => {
            onClose();
            navigate("/profile");
          }}
          className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium text-ink dark:text-zinc-200 hover:bg-surface-soft dark:hover:bg-[#2c2925] hover:text-primary transition-colors cursor-pointer text-left"
        >
          <User className="w-4 h-4 text-coral-600 dark:text-coral-400 shrink-0" />
          <span>Hồ sơ cá nhân</span>
        </button>

        <button
          type="button"
          role="menuitem"
          data-testid="popover-settings-btn"
          onClick={() => {
            onClose();
            navigate("/settings");
          }}
          className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium text-ink dark:text-zinc-200 hover:bg-surface-soft dark:hover:bg-[#2c2925] hover:text-primary transition-colors cursor-pointer text-left"
        >
          <Settings className="w-4 h-4 text-zinc-500 dark:text-zinc-400 shrink-0" />
          <span>Cài đặt</span>
        </button>
      </div>
    </div>
  );
}
