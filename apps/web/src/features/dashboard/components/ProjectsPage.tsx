import { useNavigate } from "react-router-dom";
import { DashboardTaskbar } from "./DashboardTaskbar";
import { MobileDashboardHeader } from "./MobileDashboardHeader";
import { DashboardProjectView } from "./DashboardProjectView";
import { useDashboardStore } from "../stores/useDashboardStore";
import { useDashboardSessions } from "../hooks/useDashboardSessions";
import { useWorkspaceStore } from "../stores/useWorkspaceStore";

export function ProjectsPage() {
  const navigate = useNavigate();
  const toggleSidebar = useDashboardStore((s) => s.toggleSidebar);
  const { sessions, selectSession } = useDashboardSessions();
  const setDocument = useWorkspaceStore((s) => s.setDocument);

  const handleNewSession = () => {
    navigate("/dashboard");
  };

  const handleSelectSession = (sessionId: string) => {
    selectSession(sessionId);
    navigate(`/dashboard/${sessionId}`);
  };

  const handleSelectDocument = (docId: string) => {
    setDocument(docId, "Tài liệu dự án");
    navigate("/dashboard");
  };

  return (
    <div className="h-screen w-screen flex bg-canvas dark:bg-[#181715] text-ink dark:text-[#f3f2ef] overflow-hidden">
      {/* 1. Left Navigation Taskbar */}
      <DashboardTaskbar
        sessions={sessions}
        onSelectSession={handleSelectSession}
        onNewSession={handleNewSession}
      />

      {/* 2. Center Content Area */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative">
        <MobileDashboardHeader
          onToggleSidebar={toggleSidebar}
          onNewSession={handleNewSession}
        />
        <div className="flex-1 flex flex-col h-full overflow-hidden">
          <DashboardProjectView
            onNewSession={handleNewSession}
            onSelectSession={handleSelectSession}
            onSelectDocument={handleSelectDocument}
          />
        </div>
      </main>
    </div>
  );
}
