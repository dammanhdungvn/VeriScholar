import { DashboardTaskbar } from "./DashboardTaskbar";
import { DashboardHeader } from "./DashboardHeader";
import { DashboardCoworkView } from "./DashboardCoworkView";
import { DashboardAmbientBackground } from "./DashboardAmbientBackground";
import { HeroUploadDropzone } from "./HeroUploadDropzone";
import { DashboardWorkspace } from "./DashboardWorkspace";
import { useDashboardStore } from "../stores/useDashboardStore";
import { useWorkspaceStore } from "../stores/useWorkspaceStore";
import { useDashboardSessions } from "../hooks/useDashboardSessions";
import { useStreamingChat } from "../hooks/useStreamingChat";
import { useDocumentIngestion } from "../hooks/useDocumentIngestion";
import { DashboardErrorBoundary } from "@/components/ui/DashboardErrorBoundary";

export function DashboardContainer() {
  const appMode = useDashboardStore((s) => s.appMode);
  const activeSessionId = useDashboardStore((s) => s.activeSessionId);
  const setActiveSessionId = useDashboardStore((s) => s.setActiveSessionId);
  const setActiveBbox = useDashboardStore((s) => s.setActiveBbox);

  const isStandby = useWorkspaceStore((s) => s.isStandby);
  const activeDocumentId = useWorkspaceStore((s) => s.activeDocumentId);
  const documentTitle = useWorkspaceStore((s) => s.documentTitle);
  const initNewStandbyChat = useWorkspaceStore((s) => s.initNewStandbyChat);
  const setSession = useWorkspaceStore((s) => s.setSession);
  const setStatus = useWorkspaceStore((s) => s.setStatus);

  const { ingest } = useDocumentIngestion();

  const {
    sessions,
    activeSession,
    selectSession,
  } = useDashboardSessions();

  const {
    messages,
    inputText,
    setInputText,
    isGenerating,
    sendMessage,
    stopGeneration,
    resetChat,
    loadExistingSession,
  } = useStreamingChat({ activeSessionId });

  /**
   * BẤT BIẾN 1 (Zero DB Junk):
   * Bấm "Đoạn chat mới" chỉ chuyển trạng thái Client sang Standby,
   * TUYỆT ĐỐI KHÔNG gọi API POST /api/v1/sessions khi chưa có tài liệu.
   */
  const handleNewSession = () => {
    initNewStandbyChat();
    setActiveSessionId(undefined);
    setActiveBbox(null);
    resetChat();
  };

  const handleSelectSession = (sessionId: string) => {
    selectSession(sessionId);
    setSession(sessionId);
    setStatus("completed", 100);
    loadExistingSession(sessionId);
  };

  /**
   * Bắt đầu luồng Ingestion tự động:
   * Upload CAS blob -> Tạo Session hợp lệ -> Trigger Parse & Embed -> Polling -> Workspace Active
   */
  const handleFileUpload = async (file: File) => {
    try {
      const result = await ingest(file);
      if (result?.sessionId) {
        selectSession(result.sessionId);
        loadExistingSession(result.sessionId);
      }
    } catch {
      // Error is set in useWorkspaceStore.errorMessage and handled by HeroUploadDropzone UI
    }
  };

  const showStandbyHero = isStandby && messages.length === 0 && !activeDocumentId;

  return (
    <div className="h-screen w-screen flex bg-canvas dark:bg-[#181715] text-ink dark:text-[#f3f2ef] overflow-hidden">
      {/* 1. Collapsible Left Taskbar / Sidebar */}
      <DashboardTaskbar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewSession={handleNewSession}
      />

      {/* 2. Center Canvas Area */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative">
        {/* Dynamic Academic Ambient Background */}
        <DashboardAmbientBackground isHero={appMode !== "cowork" && showStandbyHero} />

        {/* Minimal Header */}
        <DashboardHeader
          sessionTitle={activeSession?.title || (documentTitle ? `Nghiên cứu: ${documentTitle}` : undefined)}
        />

        {/* View Switcher based on AppMode, Standby State & Workspace with Error Boundary */}
        <DashboardErrorBoundary onReset={resetChat}>
          {appMode === "cowork" ? (
            <DashboardCoworkView />
          ) : showStandbyHero ? (
            <div className="flex-1 flex items-center justify-center p-6 overflow-y-auto">
              <HeroUploadDropzone onIngest={handleFileUpload} />
            </div>
          ) : (
            <DashboardWorkspace
              messages={messages}
              inputText={inputText}
              onChangeText={setInputText}
              onSend={sendMessage}
              isGenerating={isGenerating}
              onStopGeneration={stopGeneration}
              onUploadFile={handleFileUpload}
              onResetChat={resetChat}
            />
          )}
        </DashboardErrorBoundary>
      </main>
    </div>
  );
}
