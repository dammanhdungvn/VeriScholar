import { DashboardTaskbar } from "./DashboardTaskbar";
import { DashboardHeader } from "./DashboardHeader";
import { DashboardHeroSection } from "./DashboardHeroSection";
import { DashboardChatStreamView } from "./DashboardChatStreamView";
import { DashboardCoworkView } from "./DashboardCoworkView";
import { DashboardAmbientBackground } from "./DashboardAmbientBackground";
import { useDashboardStore } from "../stores/useDashboardStore";
import { useDashboardSessions } from "../hooks/useDashboardSessions";
import { useStreamingChat } from "../hooks/useStreamingChat";
import { DashboardErrorBoundary } from "@/components/ui/DashboardErrorBoundary";

export function DashboardContainer() {
  const appMode = useDashboardStore((s) => s.appMode);
  const activeSessionId = useDashboardStore((s) => s.activeSessionId);

  const {
    sessions,
    activeSession,
    createSession,
    selectSession
  } = useDashboardSessions();

  const {
    messages,
    inputText,
    setInputText,
    isGenerating,
    sendMessage,
    stopGeneration,
    resetChat,
    loadExistingSession
  } = useStreamingChat({ activeSessionId });

  const handleNewSession = async () => {
    const newSession = await createSession();
    resetChat();
    loadExistingSession(newSession.id);
  };

  const handleSelectSession = (sessionId: string) => {
    selectSession(sessionId);
    loadExistingSession(sessionId);
  };

  const handleFileUpload = async (file: File) => {
    const cleanTitle = file.name.replace(/\.pdf$/i, "");
    const newSession = await createSession(`Nghiên cứu: ${cleanTitle}`);
    resetChat();
    loadExistingSession(newSession.id);
  };

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
        <DashboardAmbientBackground isHero={appMode !== "cowork" && messages.length === 0} />

        {/* Minimal Header */}
        <DashboardHeader sessionTitle={activeSession?.title} />

        {/* View Switcher based on AppMode & Message count with Error Boundary */}
        <DashboardErrorBoundary onReset={resetChat}>
          {appMode === "cowork" ? (
            <DashboardCoworkView />
          ) : messages.length === 0 ? (
            <DashboardHeroSection
              inputText={inputText}
              onChangeText={setInputText}
              onSend={sendMessage}
              isGenerating={isGenerating}
              onUploadFile={handleFileUpload}
            />
          ) : (
            <DashboardChatStreamView
              messages={messages}
              inputText={inputText}
              onChangeText={setInputText}
              onSend={sendMessage}
              isGenerating={isGenerating}
              onStopGeneration={stopGeneration}
              onUploadFile={handleFileUpload}
            />
          )}
        </DashboardErrorBoundary>
      </main>
    </div>
  );
}
