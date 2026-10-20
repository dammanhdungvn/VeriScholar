import { useNavigate } from "react-router-dom";
import { FileText } from "lucide-react";
import { DashboardTaskbar } from "@/features/dashboard/components/DashboardTaskbar";
import { MobileDashboardHeader } from "@/features/dashboard/components/MobileDashboardHeader";
import { useDashboardStore } from "@/features/dashboard/stores/useDashboardStore";
import { useDashboardSessions } from "@/features/dashboard/hooks/useDashboardSessions";
import { NotesPanelContainer } from "./NotesPanelContainer";

export function NotesPage() {
  const navigate = useNavigate();
  const toggleSidebar = useDashboardStore((s) => s.toggleSidebar);
  const { sessions } = useDashboardSessions();

  return (
    <div className="h-screen w-screen flex bg-canvas dark:bg-[#181715] text-ink dark:text-[#f3f2ef] overflow-hidden">
      {/* 1. Left Navigation Taskbar */}
      <DashboardTaskbar
        sessions={sessions}
        onSelectSession={(id) => navigate(`/dashboard/${id}`)}
        onNewSession={() => navigate("/dashboard")}
      />

      {/* 2. Center Content Area */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative">
        <MobileDashboardHeader
          onToggleSidebar={toggleSidebar}
          onNewSession={() => navigate("/dashboard")}
        />

        {/* Top Header */}
        <header className="h-14 px-6 border-b border-[#e8e4dc] dark:border-[#2e2b26] bg-[#fdfcf9] dark:bg-[#1c1b18] flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-ink dark:text-zinc-200">
              <FileText className="w-4 h-4 stroke-[2]" />
            </div>
            <div>
              <h1 className="text-sm font-semibold font-anthropic-serif text-ink dark:text-zinc-100">
                Notes
              </h1>
              <p className="text-[11px] text-muted dark:text-zinc-400 font-sans">
                Evidence Notes · Knowledge Synthesis
              </p>
            </div>
          </div>
        </header>

        {/* Full-width Notes Container */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <NotesPanelContainer />
        </div>
      </main>
    </div>
  );
}
