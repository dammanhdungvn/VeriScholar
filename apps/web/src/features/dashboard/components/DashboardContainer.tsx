import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { DashboardTaskbar } from "./DashboardTaskbar";
import { LibraryWorkspaceView } from "@/features/library/components/LibraryWorkspaceView";
import { DashboardAmbientBackground } from "./DashboardAmbientBackground";
import { HeroUploadDropzone } from "./HeroUploadDropzone";
import { UnifiedHeroWorkspace } from "./UnifiedHeroWorkspace";
import { DashboardWorkspace } from "./DashboardWorkspace";
import { MobileDashboardHeader } from "./MobileDashboardHeader";
import { discoveryApi, type ScholarlyPaper } from "@/features/discovery/api/discoveryApi";
import { useDashboardStore } from "../stores/useDashboardStore";
import { useWorkspaceStore } from "../stores/useWorkspaceStore";
import { useDashboardSessions } from "../hooks/useDashboardSessions";
import { useStreamingChat } from "../hooks/useStreamingChat";
import { useDocumentIngestion } from "../hooks/useDocumentIngestion";
import { DashboardErrorBoundary } from "@/components/ui/DashboardErrorBoundary";
import { RestoreArchivedModal } from "@/features/sessions/components/RestoreArchivedModal";
import { useRestoreArchivedSessionMutation, useSessionDetail } from "@/features/sessions/hooks/useSessionsQuery";
import { useReaderStore } from "@/features/reader/stores/useReaderStore";
import { DocumentLibraryModal } from "@/features/documents/components/DocumentLibraryModal";
import { sessionsApi } from "@/features/sessions/api/sessionsApi";
import type { DocumentListItem } from "@/types/document";

export function DashboardContainer() {
  const { sessionId: routeSessionId } = useParams<{ sessionId?: string }>();
  const navigate = useNavigate();

  const appMode = useDashboardStore((s) => s.appMode);
  const setAppMode = useDashboardStore((s) => s.setAppMode);
  const activeSessionId = useDashboardStore((s) => s.activeSessionId);
  const setActiveSessionId = useDashboardStore((s) => s.setActiveSessionId);
  const setActiveBbox = useDashboardStore((s) => s.setActiveBbox);
  const toggleSidebar = useDashboardStore((s) => s.toggleSidebar);

  const isStandby = useWorkspaceStore((s) => s.isStandby);
  const activeDocumentId = useWorkspaceStore((s) => s.activeDocumentId);
  const documentTitle = useWorkspaceStore((s) => s.documentTitle);
  const documentStatus = useWorkspaceStore((s) => s.documentStatus);
  const initNewStandbyChat = useWorkspaceStore((s) => s.initNewStandbyChat);
  const setSession = useWorkspaceStore((s) => s.setSession);
  const setDocument = useWorkspaceStore((s) => s.setDocument);
  const setStatus = useWorkspaceStore((s) => s.setStatus);
  const resetWorkspace = useWorkspaceStore((s) => s.resetWorkspace);

  const { ingest } = useDocumentIngestion();

  const {
    sessions,
    activeSession,
    selectSession,
    createSession,
  } = useDashboardSessions();

  const effectiveSessionId = routeSessionId || activeSessionId;

  const {
    messages,
    inputText,
    setInputText,
    isGenerating,
    sendMessage,
    stopGeneration,
    resetChat,
    loadExistingSession,
  } = useStreamingChat({
    activeSessionId: effectiveSessionId,
    onSessionCreated: (newId) => {
      selectSession(newId);
      navigate(`/dashboard/${newId}`, { replace: true });
    },
  });

  // Query session detail when routeSessionId is present
  const { data: sessionDetailRes } = useSessionDetail(routeSessionId);

  // Sync routeSessionId with active session state
  useEffect(() => {
    if (routeSessionId) {
      if (routeSessionId !== activeSessionId) {
        selectSession(routeSessionId);
        setSession(routeSessionId);
        setStatus("completed", 100);
        loadExistingSession(routeSessionId);
      }
    } else if (activeSessionId) {
      // Navigated to /dashboard without session ID
      initNewStandbyChat();
      setActiveSessionId(undefined);
      setActiveBbox(null);
      resetChat();
    }
  }, [
    routeSessionId,
    activeSessionId,
    selectSession,
    setSession,
    setStatus,
    loadExistingSession,
    initNewStandbyChat,
    setActiveSessionId,
    setActiveBbox,
    resetChat,
  ]);

  // Synchronize document details when session details are loaded from API
  const syncedSessionIdRef = useRef<string | null>(null);

  useEffect(() => {
    if (sessionDetailRes?.data) {
      const detail = sessionDetailRes.data;
      const docIds = detail.document_ids || [];
      if (docIds.length > 0) {
        useReaderStore.getState().setOpenDocumentIds(docIds);
        const activeDocId = detail.active_document_id || docIds[0];
        const matchedDoc = detail.documents?.find((d) => d.id === activeDocId);
        const title = matchedDoc?.title || detail.title;
        setDocument(activeDocId, title);
        if (useReaderStore.getState().activeDocumentId !== activeDocId) {
          useReaderStore.getState().setActiveDocumentId(activeDocId);
        }

        if (syncedSessionIdRef.current !== detail.id && detail.viewport_state?.page) {
          syncedSessionIdRef.current = detail.id;
          useReaderStore.getState().setCurrentPage(detail.viewport_state.page);
        }
      }
    }
  }, [sessionDetailRes?.data, setDocument]);

  // Synchronize document details if activeSession from cached list has documents
  useEffect(() => {
    if (activeSession && activeSession.document_ids && activeSession.document_ids.length > 0) {
      useReaderStore.getState().setOpenDocumentIds(activeSession.document_ids);
      const activeDocId = activeSession.document_ids[0];
      setDocument(activeDocId, activeSession.title);
    }
  }, [activeSession, setDocument]);

  /**
   * BẤT BIẾN 1 (Zero DB Junk):
   * Bấm "Đoạn chat mới" chỉ chuyển trạng thái Client sang Standby,
   * TUYỆT ĐỐI KHÔNG gọi API POST /api/v1/sessions khi chưa có tài liệu.
   */
  const handleNewSession = () => {
    setAppMode("chat");
    initNewStandbyChat();
    setActiveSessionId(undefined);
    setActiveBbox(null);
    resetChat();
    resetWorkspace(); // Reset pending upload and document status
    navigate("/dashboard");
  };

  const [isRestoreOpen, setIsRestoreOpen] = useState(false);
  const [isLibraryOpen, setIsLibraryOpen] = useState(false);
  const restoreArchivedMutation = useRestoreArchivedSessionMutation();

  const handleSelectDocumentFromLibrary = async (doc: DocumentListItem) => {
    setIsLibraryOpen(false);
    const targetTitle = doc.title || doc.filename;

    if (effectiveSessionId) {
      try {
        await sessionsApi.addDocumentToSession(effectiveSessionId, {
          source_type: "document_id",
          document_id: doc.id,
        });
      } catch {
        // ignore if already present
      }
      const currentOpen = useReaderStore.getState().openDocumentIds;
      if (!currentOpen.includes(doc.id)) {
        useReaderStore.getState().setOpenDocumentIds([...currentOpen, doc.id]);
      }
      setDocument(doc.id, targetTitle);
      setStatus("completed", 100);
    } else {
      // Standby mode: initialize new session with document
      const newSession = await createSession(`Nghiên cứu: ${targetTitle}`);
      try {
        await sessionsApi.addDocumentToSession(newSession.id, {
          source_type: "document_id",
          document_id: doc.id,
        });
      } catch {
        // ignore
      }
      useReaderStore.getState().setOpenDocumentIds([doc.id]);
      setDocument(doc.id, targetTitle);
      selectSession(newSession.id);
      navigate(`/dashboard/${newSession.id}`, { replace: true });
      setStatus("completed", 100);
      loadExistingSession(newSession.id);
    }
  };

  const handleRestoreArchived = async (file: File) => {
    if (effectiveSessionId) {
      await restoreArchivedMutation.mutateAsync({ sessionId: effectiveSessionId, file });
      loadExistingSession(effectiveSessionId);
    }
  };

  const handleSelectSession = (sessionId: string) => {
    setAppMode("chat");
    navigate(`/dashboard/${sessionId}`);
    selectSession(sessionId);
    setSession(sessionId);
    setStatus("completed", 100);
    loadExistingSession(sessionId);
  };

  const pendingInitialPromptRef = useRef<string | null>(null);

  /**
   * Bắt đầu luồng Ingestion tự động:
   * Upload CAS blob -> Tạo Session hợp lệ -> Trigger Parse & Embed -> Polling -> Workspace Active
   */
  const handleFileUpload = async (file: File) => {
    try {
      const result = await ingest(
        file,
        (createdSessionId) => {
          selectSession(createdSessionId);
          navigate(`/dashboard/${createdSessionId}`, { replace: true });
        },
        effectiveSessionId
      );
      if (result?.sessionId) {
        selectSession(result.sessionId);
        navigate(`/dashboard/${result.sessionId}`, { replace: true });
        loadExistingSession(result.sessionId);

        // Auto-send user prompt if staged alongside file upload (Rule Item 10)
        if (pendingInitialPromptRef.current) {
          const prompt = pendingInitialPromptRef.current;
          pendingInitialPromptRef.current = null;
          setTimeout(() => {
            sendMessage(prompt);
          }, 350);
        }
      }
    } catch {
      pendingInitialPromptRef.current = null;
      // Error is set in useWorkspaceStore.errorMessage and handled by HeroUploadDropzone UI
      if (!effectiveSessionId) {
        navigate("/dashboard", { replace: true });
      }
    }
  };

  const handleSendChatWithFiles = async (prompt: string, files: File[]) => {
    if (files.length === 0) {
      if (prompt) sendMessage(prompt);
      return;
    }

    if (prompt.trim()) {
      pendingInitialPromptRef.current = prompt.trim();
    }

    await handleFileUpload(files[0]);
  };

  /**
   * Khởi tạo phiên đọc tức thì từ kết quả bài báo khoa học (Zero-to-Reading)
   */
  const handleOpenPaper = async (paper: ScholarlyPaper) => {
    try {
      const res = await discoveryApi.openReading({
        title: paper.title,
        authors: paper.authors,
        publication_year: paper.publication_year,
        doi: paper.doi,
        arxiv_id: paper.arxiv_id,
        abstract: paper.abstract,
        pdf_url: paper.pdf_url,
      });
      if (res?.session_id) {
        selectSession(res.session_id);
        navigate(`/dashboard/${res.session_id}`, { replace: true });
        loadExistingSession(res.session_id);
      }
    } catch {
      if (!effectiveSessionId) {
        navigate("/dashboard", { replace: true });
      }
    }
  };

  const isProcessing =
    documentStatus === "uploading" ||
    documentStatus === "validating" ||
    documentStatus === "parsing";

  const showStandbyHero =
    isProcessing ||
    documentStatus === "error" ||
    (!routeSessionId && isStandby && messages.length === 0 && !activeDocumentId);



  return (
    <div className="h-screen w-screen flex bg-canvas dark:bg-[#181715] text-ink dark:text-[#f3f2ef] overflow-hidden">
      {/* 1. Collapsible Left Taskbar / Sidebar */}
      <DashboardTaskbar
        sessions={sessions}
        activeSessionId={effectiveSessionId}
        onSelectSession={handleSelectSession}
        onNewSession={handleNewSession}
        onOpenLibrary={() => navigate("/library")}
      />

      {/* 2. Center Canvas Area */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative">
        {/* Sticky Mobile Dashboard Header (< 768px) */}
        <MobileDashboardHeader
          onToggleSidebar={toggleSidebar}
          onNewSession={handleNewSession}
        />

        {/* Dynamic Academic Ambient Background */}
        <DashboardAmbientBackground
          isHero={appMode === "chat" && showStandbyHero}
        />

        {/* Expired / Archived Session Re-activation Alert Banner */}
        {activeSession?.is_archived && (
          <div className="h-9 px-4 bg-amber-500/10 border-b border-amber-500/20 flex items-center justify-between text-xs text-amber-700 dark:text-amber-400 shrink-0 select-none">
            <span>Phiên nghiên cứu này đã hết hạn lưu trữ (30 ngày).</span>
            <button
              type="button"
              onClick={() => setIsRestoreOpen(true)}
              className="px-2.5 py-0.5 rounded bg-amber-500 hover:bg-amber-600 text-white font-medium text-[11px] transition-colors cursor-pointer"
            >
              Tải lại PDF để khôi phục
            </button>
          </div>
        )}

        {/* View Switcher based on AppMode, Standby State & Workspace with Error Boundary */}
        <DashboardErrorBoundary onReset={resetChat}>
          {appMode === "library" ? (
            <LibraryWorkspaceView
              onSelectDocument={(doc) => {
                handleSelectDocumentFromLibrary(doc);
                setAppMode("chat");
              }}
            />
          ) : isProcessing || documentStatus === "error" ? (
            <div className="flex-1 flex items-center justify-center p-4">
              <HeroUploadDropzone onIngest={handleFileUpload} />
            </div>
          ) : showStandbyHero ? (
            <UnifiedHeroWorkspace
              inputText={inputText}
              onChangeText={setInputText}
              onSendChat={(text) => sendMessage(text)}
              onSendChatWithFiles={handleSendChatWithFiles}
              onIngestFile={handleFileUpload}
              onOpenPaper={handleOpenPaper}
              isGenerating={isGenerating}
            />
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
              sessionId={activeSession?.id || effectiveSessionId}
              sessionTitle={activeSession?.title || (documentTitle ? `Nghiên cứu: ${documentTitle}` : undefined)}
              sessionVersion={activeSession?.version}
              documentCount={activeSession?.document_ids?.length ?? 1}
              createdAt={activeSession?.created_at}
              onDeletedSession={handleNewSession}
            />
          )}
        </DashboardErrorBoundary>

        {/* Restore Archived Session Modal */}
        <RestoreArchivedModal
          isOpen={isRestoreOpen}
          onClose={() => setIsRestoreOpen(false)}
          sessionId={effectiveSessionId || ""}
          onRestore={handleRestoreArchived}
        />

        {/* Document Library Modal */}
        <DocumentLibraryModal
          isOpen={isLibraryOpen}
          onClose={() => setIsLibraryOpen(false)}
          onSelectDocument={handleSelectDocumentFromLibrary}
          activeDocumentId={activeDocumentId}
        />
      </main>
    </div>
  );
}
