import { useNavigate } from "react-router-dom";
import { DashboardTaskbar } from "@/features/dashboard/components/DashboardTaskbar";
import { MobileDashboardHeader } from "@/features/dashboard/components/MobileDashboardHeader";
import { LibraryWorkspaceView } from "./LibraryWorkspaceView";
import { useDashboardStore } from "@/features/dashboard/stores/useDashboardStore";
import { useWorkspaceStore } from "@/features/dashboard/stores/useWorkspaceStore";
import { useReaderStore } from "@/features/reader/stores/useReaderStore";
import { useDashboardSessions } from "@/features/dashboard/hooks/useDashboardSessions";
import type { DocumentListItem } from "@/types/document";

export function LibraryPage({ hideTaskbar = true }: { hideTaskbar?: boolean } = {}) {
  const navigate = useNavigate();
  const toggleSidebar = useDashboardStore((s) => s.toggleSidebar);
  const setDocument = useWorkspaceStore((s) => s.setDocument);
  const setStatus = useWorkspaceStore((s) => s.setStatus);
  const { sessions, createSession, selectSession } = useDashboardSessions();

  const handleSelectDocument = async (doc: DocumentListItem) => {
    const targetTitle = doc.title || doc.filename;
    // Set active document in reader
    useReaderStore.getState().setOpenDocumentIds([doc.id]);
    useReaderStore.getState().setActiveDocumentId(doc.id);
    setDocument(doc.id, targetTitle);
    setStatus("completed", 100);

    // Initialize session and navigate to dashboard
    try {
      const newSession = await createSession(`Nghiên cứu: ${targetTitle}`);
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
    <div className="h-screen w-full flex bg-canvas dark:bg-[#181715] text-ink dark:text-[#f3f2ef] overflow-hidden">
      {/* 1. Left Navigation Taskbar (Optional if not wrapped in AppLayout) */}
      {!hideTaskbar && (
        <DashboardTaskbar
          sessions={sessions}
          onSelectSession={(id) => navigate(`/dashboard/${id}`)}
          onNewSession={handleNewSession}
        />
      )}

      {/* 2. Center Library Content */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden relative min-w-0">
        <MobileDashboardHeader
          onToggleSidebar={toggleSidebar}
          onNewSession={handleNewSession}
        />
        <div className="flex-1 flex flex-col h-full overflow-hidden">
          <LibraryWorkspaceView onSelectDocument={handleSelectDocument} />
        </div>
      </div>
    </div>
  );
}
