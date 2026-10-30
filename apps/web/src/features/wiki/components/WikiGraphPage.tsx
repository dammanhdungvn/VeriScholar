import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { MobileDashboardHeader } from "@/features/dashboard/components/MobileDashboardHeader";
import { WikiGraphWorkspaceView } from "./WikiGraphWorkspaceView";
import { useDashboardStore } from "@/features/dashboard/stores/useDashboardStore";
import { useWorkspaceStore } from "@/features/dashboard/stores/useWorkspaceStore";
import { useReaderStore } from "@/features/reader/stores/useReaderStore";
import { useDashboardSessions } from "@/features/dashboard/hooks/useDashboardSessions";
import { sessionsApi } from "@/features/sessions/api/sessionsApi";
import { SESSION_QUERY_KEYS } from "@/features/sessions/hooks/useSessionsQuery";

export function WikiGraphPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const toggleSidebar = useDashboardStore((s) => s.toggleSidebar);
  const setDocument = useWorkspaceStore((s) => s.setDocument);
  const setStatus = useWorkspaceStore((s) => s.setStatus);
  const { createSession, selectSession } = useDashboardSessions();

  const handleSelectDocument = async (doc: { id: string; title?: string; filename: string }) => {
    const targetTitle = doc.title || doc.filename;
    useReaderStore.getState().setOpenDocumentIds([doc.id]);
    useReaderStore.getState().setActiveDocumentId(doc.id);
    setDocument(doc.id, targetTitle);
    setStatus("completed", 100);

    try {
      const newSession = await createSession(`Research: ${targetTitle}`);
      try {
        await sessionsApi.addDocumentToSession(newSession.id, {
          source_type: "document_id",
          document_id: doc.id,
        });
        await queryClient.invalidateQueries({ queryKey: SESSION_QUERY_KEYS.lists() });
        await queryClient.invalidateQueries({ queryKey: SESSION_QUERY_KEYS.detail(newSession.id) });
      } catch (err) {
        console.warn("Failed to attach document to session:", err);
      }
      selectSession(newSession.id);
      navigate(`/dashboard/${newSession.id}`);
    } catch {
      navigate("/dashboard");
    }
  };

  const handleNewSession = () => {
    navigate("/dashboard");
  };

  return (
    <div className="h-screen w-full flex flex-col bg-canvas dark:bg-[#181715] text-ink dark:text-[#f3f2ef] overflow-hidden">
      <MobileDashboardHeader
        onToggleSidebar={toggleSidebar}
        onNewSession={handleNewSession}
      />
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <WikiGraphWorkspaceView onSelectDocument={handleSelectDocument} />
      </div>
    </div>
  );
}
