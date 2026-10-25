import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { KeyRound } from "lucide-react";
import { LandingNavbar } from "@/features/landing/components/LandingNavbar";
import { AccountSettingsContent } from "./AccountSettingsModal";
import { UserProfileModal } from "@/components/profile/UserProfileModal";
import { useAuthStore } from "@/features/auth/stores/useAuthStore";
import { Button } from "@/components/ui/button";

export function SettingsPage() {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const [isByokModalOpen, setIsByokModalOpen] = useState(false);

  return (
    <div className="min-h-screen bg-canvas dark:bg-[#181715] text-ink dark:text-[#f3f2ef] flex flex-col">
      <LandingNavbar />
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-6 sm:py-8 animate-in fade-in duration-200 space-y-4">
        <div className="flex items-center justify-between p-3.5 rounded-2xl bg-amber-500/10 border border-amber-500/25">
          <div className="flex items-center gap-2.5 text-xs">
            <KeyRound className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0" />
            <span>
              Quản lý Khóa AI cá nhân (BYOK AES-256-GCM), Mã định danh ORCID &amp; Giao diện Học thuật
            </span>
          </div>
          <Button
            type="button"
            variant="primary"
            size="sm"
            onClick={() => setIsByokModalOpen(true)}
            className="rounded-xl text-xs bg-amber-600 hover:bg-amber-700 text-white shrink-0"
          >
            Cấu hình BYOK &amp; ORCID (3 Tabs)
          </Button>
        </div>

        <AccountSettingsContent
          defaultTab="security"
          isPage={true}
          onClose={() => navigate("/dashboard")}
        />

        <UserProfileModal
          isOpen={isByokModalOpen}
          onClose={() => setIsByokModalOpen(false)}
          user={user}
        />
      </main>
    </div>
  );
}
