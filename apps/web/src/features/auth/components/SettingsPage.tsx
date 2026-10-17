import { useNavigate } from "react-router-dom";
import { LandingNavbar } from "@/features/landing/components/LandingNavbar";
import { AccountSettingsContent } from "./AccountSettingsModal";

export function SettingsPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-canvas dark:bg-[#181715] text-ink dark:text-[#f3f2ef] flex flex-col">
      <LandingNavbar />
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-6 sm:py-8 animate-in fade-in duration-200">
        <AccountSettingsContent
          defaultTab="security"
          isPage={true}
          onClose={() => navigate("/dashboard")}
        />
      </main>
    </div>
  );
}
