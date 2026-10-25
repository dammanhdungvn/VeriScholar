import { useNavigate } from "react-router-dom";
import { LandingNavbar } from "@/features/landing/components/LandingNavbar";
import { ScholarSettingsView } from "./ScholarSettingsView";

export function ProfilePage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#faf8f5] dark:bg-[#181715] text-[#1a1918] dark:text-[#f4f1ea] flex flex-col transition-colors duration-200">
      <LandingNavbar />
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-6 sm:py-8 animate-in fade-in duration-200">
        <ScholarSettingsView
          variant="page"
          defaultTab="profile"
          onClose={() => navigate("/dashboard")}
        />
      </main>
    </div>
  );
}
