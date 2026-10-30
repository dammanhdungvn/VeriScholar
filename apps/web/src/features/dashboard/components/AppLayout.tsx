import { Outlet, useNavigate } from "react-router-dom";
import { DashboardTaskbar } from "./DashboardTaskbar";
import { useDashboardSessions } from "../hooks/useDashboardSessions";
import { useWorkspaceStore } from "../stores/useWorkspaceStore";
import { useDashboardStore } from "../stores/useDashboardStore";
import { useReaderStore } from "@/features/reader/stores/useReaderStore";

export function AppLayout() {
  const navigate = useNavigate();
  const { sessions, deleteSession, updateTitle } =
    useDashboardSessions();

  const handleNewSession = () => {
    // BẤT BIẾN 1 (Zero DB Junk): Standby mode without calling POST /api/v1/sessions
    useDashboardStore.getState().setAppMode("chat");
    useWorkspaceStore.getState().initNewStandbyChat();
    useDashboardStore.getState().setActiveSessionId(undefined);
    useDashboardStore.getState().setActiveBbox(null);
    useWorkspaceStore.getState().resetWorkspace();
    useReaderStore.getState().resetReader();
    navigate("/dashboard");
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-canvas dark:bg-[#181715] text-ink dark:text-[#f3f2ef]">
      <DashboardTaskbar
        sessions={sessions}
        onSelectSession={(id) => {
          navigate(`/dashboard/${id}`);
        }}
        onNewSession={handleNewSession}
        onRenameSession={(id, title) => updateTitle(id, title)}
        onDeleteSession={deleteSession}
      />
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative min-w-0">
        <Outlet />
      </main>
    </div>
  );
}
