import { Outlet, useNavigate } from "react-router-dom";
import { DashboardTaskbar } from "./DashboardTaskbar";
import { useDashboardSessions } from "../hooks/useDashboardSessions";

export function AppLayout() {
  const navigate = useNavigate();
  const { sessions, createSession, selectSession, deleteSession, updateTitle } =
    useDashboardSessions();

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-canvas dark:bg-[#181715] text-ink dark:text-[#f3f2ef]">
      <DashboardTaskbar
        sessions={sessions}
        onSelectSession={(id) => {
          selectSession(id);
          navigate(`/dashboard/${id}`);
        }}
        onNewSession={async () => {
          try {
            const session = await createSession();
            selectSession(session.id);
            navigate(`/dashboard/${session.id}`);
          } catch {
            navigate("/dashboard");
          }
        }}
        onRenameSession={(id, title) => updateTitle(id, title)}
        onDeleteSession={deleteSession}
      />
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative min-w-0">
        <Outlet />
      </main>
    </div>
  );
}
