import { useState, useRef, useEffect, useMemo } from "react";
import {
  RotateCcw,
  Sparkles,
  BookMarked,
  ListTree,
  Quote,
  MessageSquare,
  User,
  Copy,
  Check,
  ThumbsUp,
  ThumbsDown,
  Square,
  ExternalLink,
  Settings,
  Sun,
  Moon,
  PanelLeft,
  FileText,
  Maximize2,
  Minimize2,
  X,
} from "lucide-react";
import { VerticalEdgeDock } from "./VerticalEdgeDock";
import type { ChatMessage } from "@/types/dashboard";
import type { BoundingBox } from "@/types/api";
import { useTheme } from "@/hooks/useTheme";
import { useDashboardStore } from "../stores/useDashboardStore";
import {
  useWorkspaceStore,
  MIN_SPLIT_RATIO,
  MAX_SPLIT_RATIO,
  DEFAULT_SPLIT_RATIO,
  MIN_PDF_PANEL_WIDTH_PX,
  MIN_CHAT_PANEL_WIDTH_PX,
} from "../stores/useWorkspaceStore";
import { useReaderStore } from "@/features/reader/stores/useReaderStore";
import { AcademicMarkdownRenderer } from "@/components/shared/AcademicMarkdownRenderer";
import { DocumentGroundedSummaryCard } from "./DocumentGroundedSummaryCard";
import { PresuppositionBanner } from "./PresuppositionBanner";
import { SocraticThinkingBlock } from "./SocraticThinkingBlock";
import { DashboardChatInputBox } from "./DashboardChatInputBox";
import { DocumentTabBar } from "@/features/reader/components/DocumentTabBar";
import { ViewportControls } from "@/features/reader/components/ViewportControls";
import { PdfCanvasViewer } from "@/features/reader/components/PdfCanvasViewer";
import { AbstractOnlyViewer } from "@/features/reader/components/AbstractOnlyViewer";
import { DocumentStructureSheet } from "@/features/reader/components/DocumentStructureSheet";
import { DocumentChunksSheet } from "@/features/reader/components/DocumentChunksSheet";
import { ReferenceListModal } from "@/features/reader/components/ReferenceListModal";
import { NotesPanelContainer } from "@/features/notes/components/NotesPanelContainer";
import { CreateNoteDialog } from "@/features/notes/components/CreateNoteDialog";
import { AddDocumentModal } from "@/features/sessions/components/AddDocumentModal";
import { SessionSettingsModal } from "@/features/sessions/components/SessionSettingsModal";
import { sessionsApi } from "@/features/sessions/api/sessionsApi";
import { WorkspaceToolsMenu } from "./WorkspaceToolsMenu";
import { ParseConfigModal } from "@/features/documents/components/ParseConfigModal";
import { StarDocumentModal } from "@/features/documents/components/StarDocumentModal";
import { useQueryClient } from "@tanstack/react-query";
import {
  useDocumentsList,
  useDocumentDetail,
  useDocumentStructure,
  useDocumentReferences,
  useDocumentSummary,
  useDeleteDocumentMutation,
  DOCUMENT_QUERY_KEYS,
} from "@/features/documents/hooks/useDocumentQueries";
import {
  useAddSessionDocumentMutation,
  useUpdateSessionViewportMutation,
  useSessionDetail,
  useUpdateSessionMetadataMutation,
  useDeleteSessionMutation,
} from "@/features/sessions/hooks/useSessionsQuery";
import { useCreateNoteMutation } from "@/features/notes/hooks/useNotesQuery";
import { documentsApi, type DocumentSummaryResponse } from "@/features/documents/api/documentsApi";
import { computeBoundingBoxStyle } from "@/lib/bounding-box-scaler";
import type { DocumentListItem } from "@/types/document";
import { cn } from "@/lib/utils";

interface DashboardWorkspaceProps {
  messages: ChatMessage[];
  inputText: string;
  onChangeText: (text: string) => void;
  onSend: (text?: string) => void;
  isGenerating: boolean;
  onStopGeneration: () => void;
  onUploadFile?: (file: File) => void;
  onResetChat: () => void;
  summary?: DocumentSummaryResponse | null;
  sessionId?: string;
  sessionTitle?: string;
  sessionVersion?: number;
  documentCount?: number;
  createdAt?: string;
  onDeletedSession?: () => void;
  initialAssistantOpen?: boolean;
}



export function DashboardWorkspace({
  messages = [],
  inputText = "",
  onChangeText = () => {},
  onSend = () => {},
  isGenerating = false,
  onStopGeneration = () => {},
  onUploadFile,
  onResetChat = () => {},
  summary = null,
  sessionId,
  sessionTitle,
  sessionVersion: initialSessionVersion = 1,
  documentCount = 1,
  createdAt = new Date().toISOString(),
  onDeletedSession,
  initialAssistantOpen = true,
}: Partial<DashboardWorkspaceProps> = {}) {
  const [isAssistantOpen, setIsAssistantOpen] = useState(initialAssistantOpen);
  // Store States
  const activeBboxStore = useDashboardStore((s) => s.activeBbox);
  const setActiveBboxStore = useDashboardStore((s) => s.setActiveBbox);
  const toggleSidebar = useDashboardStore((s) => s.toggleSidebar);
  const activeSessionId = useWorkspaceStore((s) => s.activeSessionId);
  const workspaceDocId = useWorkspaceStore((s) => s.activeDocumentId);
  const workspaceDocTitle = useWorkspaceStore((s) => s.documentTitle);
  const activeRightTab = useWorkspaceStore((s) => s.activeRightTab);
  const setActiveRightTab = useWorkspaceStore((s) => s.setActiveRightTab);
  const setDocument = useWorkspaceStore((s) => s.setDocument);

  // Module 1: Resizable Split-Pane, Zen Focus Modes & Context Chip
  const splitRatio = useWorkspaceStore((s) => s.splitRatio);
  const setSplitRatio = useWorkspaceStore((s) => s.setSplitRatio);
  const zenMode = useWorkspaceStore((s) => s.zenMode);
  const setZenMode = useWorkspaceStore((s) => s.setZenMode);
  const activeContextChip = useWorkspaceStore((s) => s.activeContextChip);
  const setActiveContextChip = useWorkspaceStore((s) => s.setActiveContextChip);

  const workspaceContainerRef = useRef<HTMLDivElement>(null);
  const [isDraggingSplit, setIsDraggingSplit] = useState(false);

  // Drag handlers for Resizable Split-Pane
  const handleDividerPointerDown = (e: React.PointerEvent) => {
    e.preventDefault();
    setIsDraggingSplit(true);
  };

  useEffect(() => {
    if (!isDraggingSplit) return;

    const handlePointerMove = (e: PointerEvent) => {
      if (!workspaceContainerRef.current) return;
      const rect = workspaceContainerRef.current.getBoundingClientRect();
      const totalWidth = rect.width;
      if (totalWidth <= 0) return;

      const currentX = e.clientX - rect.left;
      const rawRatio = (currentX / totalWidth) * 100;

      // Enforce both pixel minimums (PDF >= 400px, Chat >= 360px) and percentage bounds [35%, 65%]
      const minPdfRatio = Math.max(MIN_SPLIT_RATIO, (MIN_PDF_PANEL_WIDTH_PX / totalWidth) * 100);
      const maxPdfRatio = Math.min(
        MAX_SPLIT_RATIO,
        ((totalWidth - MIN_CHAT_PANEL_WIDTH_PX) / totalWidth) * 100
      );

      const effectiveMin = Math.min(DEFAULT_SPLIT_RATIO, minPdfRatio);
      const effectiveMax = Math.max(DEFAULT_SPLIT_RATIO, maxPdfRatio);

      const clampedRatio = Math.max(effectiveMin, Math.min(effectiveMax, rawRatio));
      setSplitRatio(Math.round(clampedRatio * 10) / 10);
    };

    const handlePointerUp = () => {
      setIsDraggingSplit(false);
    };

    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("pointerup", handlePointerUp);
    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", handlePointerUp);
    };
  }, [isDraggingSplit, setSplitRatio]);

  const handleDividerKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowLeft") {
      e.preventDefault();
      setSplitRatio(Math.max(MIN_SPLIT_RATIO, splitRatio - 2));
    } else if (e.key === "ArrowRight") {
      e.preventDefault();
      setSplitRatio(Math.min(MAX_SPLIT_RATIO, splitRatio + 2));
    } else if (e.key === "Home" || e.key === "Enter") {
      e.preventDefault();
      setSplitRatio(DEFAULT_SPLIT_RATIO);
    }
  };

  // Exit Zen Reading Mode with Escape key
  useEffect(() => {
    if (zenMode === "none") return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setZenMode("none");
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [zenMode, setZenMode]);

  // Responsive mobile/tablet view switcher state
  const [mobileActiveView, setMobileActiveView] = useState<"reader" | "workspace">("reader");

  // On mobile screens, automatically switch to reader view when a citation or bbox is selected
  const prevBboxRef = useRef(activeBboxStore);
  useEffect(() => {
    if (activeBboxStore && activeBboxStore !== prevBboxRef.current) {
      prevBboxRef.current = activeBboxStore;
      const raf = requestAnimationFrame(() => {
        setMobileActiveView("reader");
      });
      return () => cancelAnimationFrame(raf);
    }
    prevBboxRef.current = activeBboxStore;
  }, [activeBboxStore]);

  const { theme, toggleTheme } = useTheme();
  const isDark = theme === "dark";
  const effectiveSessionId = sessionId || activeSessionId || "";

  const readerDocId = useReaderStore((s) => s.activeDocumentId);
  const openDocumentIds = useReaderStore((s) => s.openDocumentIds);
  const setActiveDocumentId = useReaderStore((s) => s.setActiveDocumentId);
  const addOpenDocument = useReaderStore((s) => s.addOpenDocument);
  const removeOpenDocument = useReaderStore((s) => s.removeOpenDocument);
  const zoomRatio = useReaderStore((s) => s.zoomRatio);
  const zoomIn = useReaderStore((s) => s.zoomIn);
  const zoomOut = useReaderStore((s) => s.zoomOut);
  const resetZoom = useReaderStore((s) => s.resetZoom);
  const currentPage = useReaderStore((s) => s.currentPage);
  const totalPages = useReaderStore((s) => s.totalPages);
  const setCurrentPage = useReaderStore((s) => s.setCurrentPage);
  const setTotalPages = useReaderStore((s) => s.setTotalPages);
  const rotationDeg = useReaderStore((s) => s.rotationDeg);
  const rotateClockwise = useReaderStore((s) => s.rotateClockwise);
  const activeBboxReader = useReaderStore((s) => s.activeBbox);
  const activeBboxesReader = useReaderStore((s) => s.activeBboxes);
  const setActiveCitation = useReaderStore((s) => s.setActiveCitation);

  // Active Bbox Synchronization
  const activeBbox = activeBboxStore || activeBboxReader;

  // Local Modal States
  const [isAddDocOpen, setIsAddDocOpen] = useState(false);
  const [isCreateNoteOpen, setIsCreateNoteOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [noteInitialText, setNoteInitialText] = useState("");
  const [notePageNumber, setNotePageNumber] = useState(1);
  const [isStructureSheetOpen, setIsStructureSheetOpen] = useState(false);
  const [isChunksSheetOpen, setIsChunksSheetOpen] = useState(false);
  const [isRefModalOpen, setIsRefModalOpen] = useState(false);
  const [copiedMsgId, setCopiedMsgId] = useState<string | null>(null);

  // Academic Context Menu State (guards against accidental browser back / gestures)
  const [contextMenu, setContextMenu] = useState<{
    isOpen: boolean;
    x: number;
    y: number;
    selectedText: string;
  }>({
    isOpen: false,
    x: 0,
    y: 0,
    selectedText: "",
  });

  const handleContextMenu = (e: React.MouseEvent) => {
    // Retain default OS text editing context menu for active text inputs
    const target = e.target as HTMLElement | null;
    if (target?.tagName === "INPUT" || target?.tagName === "TEXTAREA") {
      return;
    }

    // Crucial: prevent browser default context menu which triggers "Back" (history.back()) or Linux mouse gestures
    e.preventDefault();
    e.stopPropagation();

    const selected = window.getSelection()?.toString().trim() || "";
    const menuWidth = 230;
    const menuHeight = 250;
    const clampedX = Math.min(e.clientX, window.innerWidth - menuWidth - 12);
    const clampedY = Math.min(e.clientY, window.innerHeight - menuHeight - 12);

    setContextMenu({
      isOpen: true,
      x: Math.max(12, clampedX),
      y: Math.max(12, clampedY),
      selectedText: selected,
    });
  };

  useEffect(() => {
    if (!contextMenu.isOpen) return;

    const handleDismiss = (e: Event) => {
      const menuEl = document.querySelector('[data-testid="academic-context-menu"]');
      if (menuEl && !menuEl.contains(e.target as Node)) {
        setContextMenu((prev) => ({ ...prev, isOpen: false }));
      }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setContextMenu((prev) => ({ ...prev, isOpen: false }));
      }
    };

    const timer = setTimeout(() => {
      window.addEventListener("pointerdown", handleDismiss);
      window.addEventListener("scroll", handleDismiss, true);
    }, 10);
    window.addEventListener("keydown", handleKeyDown);

    return () => {
      clearTimeout(timer);
      window.removeEventListener("pointerdown", handleDismiss);
      window.removeEventListener("scroll", handleDismiss, true);
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [contextMenu.isOpen]);

  // Session Mutations
  const updateTitleMutation = useUpdateSessionMetadataMutation();
  const deleteMutation = useDeleteSessionMutation();

  const handleUpdateTitle = async (newTitle: string, version: number) => {
    if (!sessionId) return;
    await updateTitleMutation.mutateAsync({
      sessionId,
      title: newTitle,
      etag: `v${version}`,
    });
  };

  const handleDeleteSession = async () => {
    if (!sessionId) return;
    await deleteMutation.mutateAsync(sessionId);
    onDeletedSession?.();
  };

  // Real-Time Grounded Summary Stream State
  const [isStreamingSummary, setIsStreamingSummary] = useState(false);
  const [streamedSummary, setStreamedSummary] = useState<DocumentSummaryResponse | null>(null);

  const bboxRef = useRef<HTMLDivElement | null>(null);
  const chatScrollRef = useRef<HTMLDivElement | null>(null);

  // TanStack Queries & Mutations
  const { data: documentsData, isLoading: isLoadingDocs } = useDocumentsList();
  const activeDocumentId = readerDocId || workspaceDocId;
  const { data: documentDetail, isLoading: isLoadingDocDetail } = useDocumentDetail(activeDocumentId);
  const { data: documentStructure } = useDocumentStructure(activeDocumentId);
  const { data: documentReferences } = useDocumentReferences(activeDocumentId);
  const { data: liveSummary } = useDocumentSummary(
    activeRightTab === "summary" ? activeDocumentId : null
  );
  const { data: sessionDetail } = useSessionDetail(activeSessionId);

  const deleteDocMutation = useDeleteDocumentMutation();
  const addSessionDocMutation = useAddSessionDocumentMutation();
  const createNoteMutation = useCreateNoteMutation();

  const currentDocTitle =
    documentDetail?.title ||
    workspaceDocTitle ||
    "Tài liệu nghiên cứu";

  // Effective Documents List for Multi-Paper Tab Bar
  const effectiveOpenIds = useMemo(() => {
    if (openDocumentIds.length > 0) return openDocumentIds;
    if (activeDocumentId && activeDocumentId !== "doc-default") return [activeDocumentId];
    return [];
  }, [openDocumentIds, activeDocumentId]);

  const effectiveDocuments: DocumentListItem[] = useMemo(() => {
    if (effectiveOpenIds.length === 0) return [];
    if (documentsData?.data && documentsData.data.length > 0) {
      return documentsData.data;
    }
    if (workspaceDocId && workspaceDocId !== "doc-default") {
      return [
        {
          id: workspaceDocId,
          filename: `${currentDocTitle}.pdf`,
          title: currentDocTitle,
          status: "completed",
          is_persistent: true,
          created_at: new Date().toISOString(),
        },
      ];
    }
    return [];
  }, [effectiveOpenIds.length, documentsData, workspaceDocId, currentDocTitle]);

  // Page Sync when activeBbox changes
  useEffect(() => {
    if (activeBbox && activeBbox[4]) {
      setCurrentPage(activeBbox[4]);
    }
  }, [activeBbox, setCurrentPage]);

  // Scroll active Bbox into view locally inside viewer container
  useEffect(() => {
    if (activeBbox && activeBbox[4] && bboxRef.current) {
      const container = bboxRef.current.closest<HTMLElement>(".overflow-auto, .overflow-y-auto");
      if (container && typeof container.scrollTo === "function") {
        const containerRect = container.getBoundingClientRect();
        const bboxRect = bboxRef.current.getBoundingClientRect();
        const relativeTop = bboxRect.top - containerRect.top + container.scrollTop;
        const targetScrollTop = relativeTop - container.clientHeight / 2 + bboxRect.height / 2;
        container.scrollTo({ top: Math.max(0, targetScrollTop), behavior: "smooth" });
      }
    }
  }, [activeBbox]);

  // Auto-scroll chat stream
  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [messages, isGenerating]);

  // Sync page count from document detail
  useEffect(() => {
    if (documentDetail?.page_count) {
      setTotalPages(documentDetail.page_count);
    }
  }, [documentDetail?.page_count, setTotalPages]);

  const handleCopy = (msgId: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedMsgId(msgId);
    setTimeout(() => setCopiedMsgId(null), 2000);
  };

  const handleSelectDoc = (docId: string) => {
    setActiveDocumentId(docId);
  };

  const handleCloseDoc = async (docId: string) => {
    removeOpenDocument(docId);
    if (activeDocumentId === docId) {
      const remaining = openDocumentIds.filter((id) => id !== docId);
      if (remaining.length > 0) {
        setActiveDocumentId(remaining[0]);
        setDocument(remaining[0], null);
      } else {
        setActiveDocumentId("");
        setDocument("", null);
      }
    }
    if (effectiveSessionId && docId !== "doc-default") {
      try {
        await sessionsApi.removeDocumentFromSession(effectiveSessionId, docId);
      } catch (err) {
        console.error("Failed to remove document from session:", err);
      }
    }
  };

  const handleDeleteDoc = async (docId: string) => {
    if (docId === "doc-default") {
      removeOpenDocument(docId);
      return;
    }
    await deleteDocMutation.mutateAsync(docId);
    removeOpenDocument(docId);
    if (activeDocumentId === docId) {
      const remaining = openDocumentIds.filter((id) => id !== docId);
      if (remaining.length > 0) {
        setActiveDocumentId(remaining[0]);
        setDocument(remaining[0], null);
      } else {
        setActiveDocumentId("");
        setDocument("", null);
      }
    }
    queryClient.invalidateQueries({ queryKey: DOCUMENT_QUERY_KEYS.lists() });
  };

  const [isParseConfigOpen, setIsParseConfigOpen] = useState(false);
  const [isStarModalOpen, setIsStarModalOpen] = useState(false);
  const [starTargetDoc, setStarTargetDoc] = useState<{ id: string; title: string; isStarred: boolean } | null>(null);

  const handleToggleStar = async (docId: string) => {
    const doc = effectiveDocuments.find((d) => d.id === docId);
    setStarTargetDoc({
      id: docId,
      title: doc?.title || doc?.filename || currentDocTitle,
      isStarred: Boolean(doc?.is_persistent),
    });
    setIsStarModalOpen(true);
  };

  const handleOpenParseConfig = () => {
    if (!activeDocumentId || activeDocumentId === "doc-default") return;
    setIsParseConfigOpen(true);
  };

  const handleReextractReferences = async () => {
    if (!activeDocumentId || activeDocumentId === "doc-default") return;
    try {
      await documentsApi.extractReferences(activeDocumentId, true);
      queryClient.invalidateQueries({ queryKey: DOCUMENT_QUERY_KEYS.references(activeDocumentId) });
    } catch (err) {
      console.warn("Failed to re-extract references:", err);
    }
  };

  const handleAddByDocumentId = async (docId: string) => {
    if (activeSessionId) {
      await addSessionDocMutation.mutateAsync({
        sessionId: activeSessionId,
        data: { source_type: "document_id", document_id: docId },
      });
    }
    addOpenDocument(docId);
    setActiveDocumentId(docId);
  };

  const handleAddByUrl = async (url: string, title?: string) => {
    if (activeSessionId) {
      await addSessionDocMutation.mutateAsync({
        sessionId: activeSessionId,
        data: { source_type: "url", url, title },
      });
    }
  };

  const handleAddToNote = (selectedText: string, pageNumber: number, bbox?: BoundingBox | null) => {
    setNoteInitialText(selectedText);
    setNotePageNumber(pageNumber);
    if (bbox) {
      setActiveBboxStore(bbox);
      setActiveCitation(null, bbox, pageNumber);
    }
    setIsCreateNoteOpen(true);
  };

  const handleAddToChat = (selectedText: string, pageNumber: number, bbox?: BoundingBox | null) => {
    setActiveRightTab("chat");
    setMobileActiveView("workspace");
    setActiveContextChip({
      text: selectedText,
      pageNumber,
      bbox: bbox ?? null,
      documentTitle: currentDocTitle,
      documentId: activeDocumentId,
    });
    if (bbox) {
      setActiveBboxStore(bbox);
      setActiveCitation(null, bbox, pageNumber);
    }
  };

  const handleCreateNoteSubmit = async (payload: {
    document_id?: string | null;
    selected_text: string;
    page_number: number;
    user_note?: string;
    tags?: string[];
  }) => {
    await createNoteMutation.mutateAsync({
      document_id:
        activeDocumentId && activeDocumentId !== "doc-default"
          ? activeDocumentId
          : undefined,
      selected_text: payload.selected_text || "Trích dẫn nghiên cứu",
      page_number: payload.page_number,
      user_note: payload.user_note,
      tags: payload.tags,
    });
    setIsCreateNoteOpen(false);
  };

  // Compute percentage box styling for active bounding box
  const bboxStyle = useMemo(() => {
    if (!activeBbox) return null;
    return computeBoundingBoxStyle(activeBbox);
  }, [activeBbox]);

  const displayTitle = currentDocTitle;

  const isRealDocument = Boolean(
    activeDocumentId &&
    activeDocumentId !== "doc-default"
  );

  const activeSummary =
    streamedSummary ||
    liveSummary ||
    (isRealDocument ? null : summary || null);

  const queryClient = useQueryClient();
  const sessionDetailQuery = useSessionDetail(activeSessionId);
  const updateViewportMutation = useUpdateSessionViewportMutation();
  const sessionVersion = sessionDetailQuery.data?.data.version ?? initialSessionVersion;

  const isResolvingDocument = Boolean(
    isLoadingDocs ||
    isLoadingDocDetail ||
    sessionDetailQuery.isLoading
  );

  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);

  const handleRegenerateSummary = async () => {
    if (!activeDocumentId || activeDocumentId === "doc-default") return;
    setIsGeneratingSummary(true);
    try {
      await documentsApi.generateSummary(activeDocumentId, true);
      queryClient.invalidateQueries({ queryKey: DOCUMENT_QUERY_KEYS.summary(activeDocumentId) });
    } catch (err) {
      console.warn("Failed to regenerate summary:", err);
    } finally {
      setIsGeneratingSummary(false);
    }
  };

  const handleStreamSummary = async () => {
    if (!activeDocumentId || activeDocumentId === "doc-default") return;
    setIsStreamingSummary(true);
    setStreamedSummary({
      document_id: activeDocumentId,
      problem_statement: { text: "", bounding_boxes: [] },
      contributions: { text: "", bounding_boxes: [] },
      limitations: { text: "", bounding_boxes: [] },
    });
    try {
      await documentsApi.streamSummary(activeDocumentId, {
        onStart() {
          setIsStreamingSummary(true);
        },
        onChunk(chunk) {
          setStreamedSummary((prev) => {
            if (!prev) return prev;
            const sec = chunk.section;
            return {
              ...prev,
              [sec]: {
                ...prev[sec],
                text: (prev[sec]?.text || "") + chunk.token,
              },
            };
          });
        },
        onBox(box) {
          setStreamedSummary((prev) => {
            if (!prev) return prev;
            const sec = box.section;
            return {
              ...prev,
              [sec]: {
                ...prev[sec],
                bounding_boxes: box.bounding_boxes as [number, number, number, number, number][],
              },
            };
          });
        },
        onEnd() {
          setIsStreamingSummary(false);
          queryClient.invalidateQueries({ queryKey: DOCUMENT_QUERY_KEYS.summary(activeDocumentId) });
        },
        onError(err) {
          console.error("Stream summary error:", err);
          setIsStreamingSummary(false);
        },
      });
    } catch (err) {
      console.error("Failed to stream summary:", err);
      setIsStreamingSummary(false);
    }
  };

  // Debounced Viewport OCC auto-save (RFC 9110 If-Match)
  const lastSavedViewportRef = useRef<{ page: number; zoom: number; tab: string; docId: string } | null>(null);

  useEffect(() => {
    if (!activeSessionId || !activeDocumentId || activeDocumentId === "doc-default") return;
    const sessionDocs = sessionDetail?.data?.documents;
    if (sessionDocs && !sessionDocs.some((d) => d.id === activeDocumentId)) return;

    const currentTab = (activeRightTab === "chat" || activeRightTab === "notes" || activeRightTab === "summary")
      ? activeRightTab
      : "chat";

    if (
      lastSavedViewportRef.current &&
      lastSavedViewportRef.current.page === currentPage &&
      lastSavedViewportRef.current.zoom === zoomRatio &&
      lastSavedViewportRef.current.tab === currentTab &&
      lastSavedViewportRef.current.docId === activeDocumentId
    ) {
      return;
    }

    const timer = setTimeout(() => {
      lastSavedViewportRef.current = {
        page: currentPage,
        zoom: zoomRatio,
        tab: currentTab,
        docId: activeDocumentId,
      };

      updateViewportMutation.mutate({
        sessionId: activeSessionId,
        etag: `v${sessionVersion}`,
        data: {
          active_document_id: activeDocumentId,
          active_tab: currentTab,
          viewport_state: {
            page: currentPage,
            zoom_ratio: zoomRatio,
            scroll_top: 0,
          },
        },
      });
    }, 1500);

    return () => clearTimeout(timer);
  }, [activeSessionId, activeDocumentId, currentPage, zoomRatio, activeRightTab, sessionVersion, updateViewportMutation, sessionDetail?.data?.documents]);

  return (
    <div
      ref={workspaceContainerRef}
      data-testid="dashboard-workspace-root"
      onContextMenu={handleContextMenu}
      className={cn(
        "flex-1 flex flex-col md:flex-row h-screen overflow-hidden overflow-x-hidden bg-[#faf9f5] dark:bg-[#181715] select-text relative",
        isDraggingSplit && "select-none cursor-col-resize"
      )}
    >
      {/* Mobile Top Navigation & Segmented View Switcher (Visible only on < md screens) */}
      <div className="md:hidden h-12 px-3 border-b border-[#e6dfd8] dark:border-[#2a2824] bg-white/80 dark:bg-[#181715]/80 backdrop-blur-md flex items-center justify-between shrink-0 select-none z-10">
        {/* Left: Mobile Sidebar Menu Toggle & Title */}
        <div className="flex items-center gap-2 min-w-0">
          <button
            type="button"
            onClick={toggleSidebar}
            aria-label="Mở danh sách phiên nghiên cứu"
            title="Mở menu phiên nghiên cứu"
            className="p-1.5 rounded-lg hover:bg-surface-soft dark:hover:bg-[#252320] text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 transition-colors cursor-pointer min-h-[44px] min-w-[44px] flex items-center justify-center"
          >
            <PanelLeft className="w-5 h-5 text-coral-600 dark:text-coral-400" />
          </button>
          <span className="text-xs font-serif font-medium text-ink dark:text-zinc-200 truncate max-w-[130px] sm:max-w-[220px]">
            {displayTitle}
          </span>
        </div>

        {/* Center/Right: Segmented Switcher Pill [ 📄 Xem Bài Báo ] [ 💬 Socratic Copilot ] */}
        <div className="inline-flex p-0.5 rounded-lg bg-[#eee9df] dark:bg-[#24221f] text-xs font-medium border border-hairline/60">
          <button
            type="button"
            onClick={() => setMobileActiveView("reader")}
            aria-label="Chuyển sang chế độ xem tài liệu PDF"
            className={cn(
              "inline-flex items-center justify-center gap-1.5 px-3 py-1.5 min-h-[44px] rounded-md transition-all cursor-pointer text-xs font-medium select-none",
              mobileActiveView === "reader"
                ? "bg-white dark:bg-[#322f2b] text-primary dark:text-coral-400 font-semibold shadow-xs"
                : "text-muted hover:text-ink dark:text-zinc-400"
            )}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Tài liệu</span>
          </button>
          <button
            type="button"
            onClick={() => setMobileActiveView("workspace")}
            aria-label="Chuyển sang chế độ xem trợ lý đối thoại và sổ tay"
            className={cn(
              "inline-flex items-center justify-center gap-1.5 px-3 py-1.5 min-h-[44px] rounded-md transition-all cursor-pointer text-xs font-medium select-none",
              mobileActiveView === "workspace"
                ? "bg-white dark:bg-[#322f2b] text-primary dark:text-coral-400 font-semibold shadow-xs"
                : "text-muted hover:text-ink dark:text-zinc-400"
            )}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Trợ lý</span>
          </button>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 1. LEFT PANE: MULTI-PAPER DEEP READER CANVAS (1 - 5 PAPERS)              */}
      {/* ========================================================================= */}
      <section
        data-testid="paper-reader-container"
        style={
          !isAssistantOpen || zenMode === "pdf"
            ? { width: "100%" }
            : zenMode === "workspace"
            ? { display: "none" }
            : ({
                "--split-ratio": `${splitRatio}%`,
              } as React.CSSProperties)
        }
        className={cn(
          "flex flex-col h-full overflow-hidden transition-[width] duration-75",
          isAssistantOpen && zenMode === "none" && "w-full md:w-[var(--split-ratio)] md:min-w-[320px] border-b-0 md:border-r border-[#e6dfd8] dark:border-[#2a2824] bg-[#faf8f4] dark:bg-[#1c1b18]",
          (!isAssistantOpen || zenMode === "pdf") && "w-full md:w-full border-r-0 bg-[#faf8f4] dark:bg-[#1c1b18]",
          zenMode === "workspace" && "hidden md:hidden",
          zenMode === "pdf" && "w-full",
          mobileActiveView === "reader" ? "flex" : "hidden md:flex"
        )}
      >
        {/* Multi-Paper Tab Bar (Desktop / Tablet only; mobile uses header & switcher) */}
        <div className="hidden md:block">
          <DocumentTabBar
            documents={effectiveDocuments}
            openDocumentIds={effectiveOpenIds}
            activeDocumentId={activeDocumentId || effectiveOpenIds[0] || null}
            onSelectDocument={handleSelectDoc}
            onCloseDocument={handleCloseDoc}
            onAddDocument={() => setIsAddDocOpen(true)}
            onToggleStar={handleToggleStar}
            onDeleteDocument={handleDeleteDoc}
          />
        </div>

        {/* Viewport & Navigation Controls */}
        <ViewportControls
          currentPage={currentPage}
          totalPages={totalPages}
          zoomRatio={zoomRatio}
          onPageChange={setCurrentPage}
          onZoomIn={zoomIn}
          onZoomOut={zoomOut}
          onResetZoom={resetZoom}
          onRotate={rotateClockwise}
          isZenPdf={zenMode === "pdf"}
          onToggleZenPdf={() => setZenMode(zenMode === "pdf" ? "none" : "pdf")}
          onOpenReferences={isRealDocument ? () => setIsRefModalOpen(true) : undefined}
        />

        {/* Dynamic PDF Canvas Viewport Area */}
        {isRealDocument && activeDocumentId && (documentDetail?.access_status === "abstract_only" || documentDetail?.status === "abstract_only") ? (
          <AbstractOnlyViewer
            document={documentDetail}
            onPdfAttached={() => {
              queryClient.invalidateQueries({ queryKey: DOCUMENT_QUERY_KEYS.detail(activeDocumentId) });
              queryClient.invalidateQueries({ queryKey: DOCUMENT_QUERY_KEYS.list() });
            }}
          />
        ) : isRealDocument && activeDocumentId ? (
          <PdfCanvasViewer
            documentId={activeDocumentId}
            documentDetail={documentDetail}
            fileUrl={documentsApi.getDocumentFileUrl(activeDocumentId)}
            currentPage={currentPage}
            zoomRatio={zoomRatio}
            rotationDeg={rotationDeg}
            activeBbox={activeBbox}
            activeBboxes={activeBboxesReader}
            onPageCountDetected={setTotalPages}
            onClearHighlight={() => {
              setActiveBboxStore(null);
              setActiveCitation(null, null);
            }}
            onAddToNote={handleAddToNote}
            onAddToChat={handleAddToChat}
            onAskChat={(prompt) => {
              setActiveRightTab("chat");
              onChangeText(prompt);
              setMobileActiveView("workspace");
            }}
          />
        ) : isResolvingDocument || (bboxStyle && activeBbox) ? (
          <div className="flex-1 overflow-auto p-4 sm:p-6 scrollbar-none flex justify-center bg-[#eae5db]/60 dark:bg-[#141311]">
            <div
              style={{
                transform: `scale(${zoomRatio}) rotate(${rotationDeg}deg)`,
                transformOrigin: "top center",
              }}
              className="w-full max-w-2xl min-h-[780px] bg-white dark:bg-[#1a1917] rounded-sm border border-[#e5dfd4] dark:border-[#2f2b26] p-6 sm:p-8 shadow-sm transition-transform duration-150 relative text-[#141413] dark:text-[#ded8cc]"
            >
              {/* Dynamic Grounded Bounding Box Overlay */}
              {bboxStyle && activeBbox && (
                <div
                  ref={bboxRef}
                  data-testid="grounded-bbox-overlay"
                  style={{
                    left: bboxStyle.left,
                    top: bboxStyle.top,
                    width: bboxStyle.width,
                    height: bboxStyle.height,
                  }}
                  className="absolute z-20 pointer-events-none rounded-md border-2 border-[#cc785c] bg-[#cc785c]/10 shadow-[0_0_12px_rgba(204,120,92,0.35)] animate-in fade-in zoom-in-95 duration-250"
                />
              )}

              {/* Clean Studio Paper Loading State (No Mock Text) */}
              <div className="space-y-6 animate-pulse select-none" data-testid="paper-loading-skeleton">
                <header className="text-center pb-5 border-b border-[#e5e1d8] dark:border-[#353027] space-y-2">
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 dark:bg-primary/20 text-primary text-xs font-medium font-sans">
                    <span className="w-2 h-2 rounded-full bg-primary animate-ping" />
                    <span>Đang nạp tài liệu...</span>
                  </div>
                  <h2 className="font-serif font-bold text-base sm:text-lg text-[#11100f] dark:text-[#fbf9f5] leading-snug line-clamp-2">
                    {displayTitle}
                  </h2>
                  <p className="text-2xs font-mono text-ink-muted dark:text-zinc-400">
                    Trang {currentPage}
                  </p>
                </header>

                {/* Abstract Skeleton Box */}
                <div className="p-4 rounded-lg bg-[#faf8f4] dark:bg-[#181715] border border-[#e5dfd4] dark:border-[#332e26] space-y-2.5">
                  <div className="h-3 w-1/4 bg-zinc-300 dark:bg-zinc-700 rounded" />
                  <div className="h-2.5 w-full bg-zinc-200 dark:bg-zinc-800 rounded" />
                  <div className="h-2.5 w-5/6 bg-zinc-200 dark:bg-zinc-800 rounded" />
                  <div className="h-2.5 w-4/6 bg-zinc-200 dark:bg-zinc-800 rounded" />
                </div>

                {/* 2-Column Scholarly Skeleton */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <div className="h-3.5 w-2/5 bg-zinc-300 dark:bg-zinc-700 rounded" />
                    <div className="h-2.5 w-full bg-zinc-200 dark:bg-zinc-800 rounded" />
                    <div className="h-2.5 w-11/12 bg-zinc-200 dark:bg-zinc-800 rounded" />
                    <div className="h-2.5 w-4/5 bg-zinc-200 dark:bg-zinc-800 rounded" />
                    <div className="h-2.5 w-full bg-zinc-200 dark:bg-zinc-800 rounded" />
                  </div>
                  <div className="space-y-3">
                    <div className="h-3.5 w-1/2 bg-zinc-300 dark:bg-zinc-700 rounded" />
                    <div className="h-2.5 w-full bg-zinc-200 dark:bg-zinc-800 rounded" />
                    <div className="h-2.5 w-5/6 bg-zinc-200 dark:bg-zinc-800 rounded" />
                    <div className="h-10 w-full bg-[#f4efe6] dark:bg-[#22201d] rounded border border-[#e5dfd4]/60 dark:border-[#332e26]" />
                    <div className="h-2.5 w-3/4 bg-zinc-200 dark:bg-zinc-800 rounded" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Empty State: No document uploaded or selected yet */
          <div className="flex-1 flex flex-col items-center justify-center p-8 bg-[#faf8f4] dark:bg-[#141311] text-center select-none">
            <div className="w-16 h-16 rounded-2xl bg-[#f0eae1] dark:bg-[#252320] border border-[#d8d0c5] dark:border-[#38332c] flex items-center justify-center text-primary mb-4 shadow-sm">
              <BookMarked className="w-8 h-8" />
            </div>
            <h3 className="font-serif font-semibold text-base text-ink dark:text-zinc-100 mb-1">
              Chưa có tài liệu nghiên cứu nào
            </h3>
            <p className="text-xs text-muted max-w-sm mb-5 leading-relaxed font-sans">
              Tải lên tệp PDF bài báo khoa học để hệ thống trích xuất tọa độ Bounding Box và kích hoạt đối thoại Socratic.
            </p>
            <button
              type="button"
              onClick={() => setIsAddDocOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium bg-primary text-white hover:bg-primary/90 transition-colors shadow-xs cursor-pointer"
            >
              <span>+ Tải lên tài liệu PDF</span>
            </button>
          </div>
        )}

        {/* Structure Sheet Drawer */}
        <DocumentStructureSheet
          structure={documentStructure}
          isOpen={isStructureSheetOpen}
          onClose={() => setIsStructureSheetOpen(false)}
          onNavigatePage={(page) => setCurrentPage(page)}
        />

        {/* Chunks Sheet Drawer */}
        <DocumentChunksSheet
          documentId={isRealDocument ? activeDocumentId : null}
          isOpen={isChunksSheetOpen}
          onClose={() => setIsChunksSheetOpen(false)}
          onNavigatePage={(page) => setCurrentPage(page)}
          onHighlightBbox={(bbox) => {
            setActiveBboxStore(bbox);
            if (bbox[4]) setCurrentPage(bbox[4]);
            setMobileActiveView("reader");
          }}
        />
      </section>

      {/* Draggable Divider (Tablet & Desktop, Hidden in Zen Modes, Mobile and when Assistant is closed) */}
      {zenMode === "none" && isAssistantOpen && (
        <div
          role="separator"
          tabIndex={0}
          data-testid="split-pane-divider"
          aria-orientation="vertical"
          aria-valuenow={Math.round(splitRatio)}
          aria-valuemin={MIN_SPLIT_RATIO}
          aria-valuemax={MAX_SPLIT_RATIO}
          aria-label="Kéo để điều chỉnh kích thước hai khung làm việc"
          onPointerDown={handleDividerPointerDown}
          onDoubleClick={() => setSplitRatio(DEFAULT_SPLIT_RATIO)}
          onKeyDown={handleDividerKeyDown}
          className={cn(
            "hidden md:flex w-2 -mx-1 z-30 cursor-col-resize items-center justify-center select-none hover:bg-primary/25 active:bg-primary/40 transition-colors focus:outline-none focus:ring-1 focus:ring-primary/40",
            isDraggingSplit && "bg-primary/30"
          )}
        >
          <div className="w-[3px] h-8 rounded-full bg-[#d0c8b9] dark:bg-[#3b362e] group-hover:bg-primary transition-all pointer-events-none" />
        </div>
      )}

      {/* ========================================================================= */}
      {/* 2. RIGHT PANE: SOCRATIC COPILOT, SMART NOTES, SUMMARY & KNOWLEDGE DIGEST */}
      {/* ========================================================================= */}
      <section
        data-testid="assistant-pane-container"
        onContextMenu={handleContextMenu}
        style={
          !isAssistantOpen || zenMode === "pdf"
            ? { display: "none" }
            : zenMode === "workspace"
            ? { width: "100%" }
            : ({
                "--split-ratio-right": `${100 - splitRatio}%`,
              } as React.CSSProperties)
        }
        className={cn(
          "flex flex-col h-full bg-[#faf9f5] dark:bg-[#181715] overflow-hidden relative transition-[width] duration-75",
          (!isAssistantOpen || zenMode === "pdf") && "hidden md:hidden",
          isAssistantOpen && zenMode === "none" && "w-full md:w-[var(--split-ratio-right)] md:min-w-[320px]",
          zenMode === "workspace" && "w-full",
          mobileActiveView === "workspace" ? "flex" : "hidden md:flex"
        )}
      >
        {/* Floating Zen Mode Restore Button */}
        {zenMode !== "none" && (
          <div className="absolute top-2 right-4 z-40 animate-in fade-in slide-in-from-top-2">
            <button
              type="button"
              data-testid="zen-exit-pill"
              onClick={() => setZenMode("none")}
              aria-label="Khôi phục chia đôi màn hình"
              title="Khôi phục chia đôi màn hình (Esc)"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#1b1a18]/90 dark:bg-white/90 text-white dark:text-[#181715] text-xs font-medium shadow-lg backdrop-blur-md hover:scale-105 active:scale-95 transition-all cursor-pointer"
            >
              <Minimize2 className="w-3 h-3" />
              <span>Khôi phục chia đôi (Esc)</span>
            </button>
          </div>
        )}
        {/* Assistant Header (alphaXiv Minimalist Header) */}
        <header className="h-11 px-3 bg-white/80 dark:bg-[#1c1b18]/80 backdrop-blur-sm border-b border-[#e6dfd8] dark:border-[#2a2824] flex items-center justify-between select-none shrink-0 z-10 gap-2">
          {/* Left: Assistant Title & (+) New Chat pill */}
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="flex items-center gap-1.5 shrink-0">
              <div className="w-6 h-6 rounded-lg bg-[#cc785c]/15 text-[#cc785c] flex items-center justify-center">
                <Sparkles className="w-3.5 h-3.5" />
              </div>
              <h2 className="font-serif font-bold text-xs sm:text-sm text-ink dark:text-[#f3f2ef] leading-tight">
                Assistant
              </h2>
            </div>

            {/* Pill: (+) New Chat */}
            <button
              type="button"
              data-testid="new-chat-btn"
              onClick={() => {
                setActiveRightTab("chat");
                onResetChat();
              }}
              title="Bắt đầu đoạn chat mới"
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-[#f5f1ea] dark:bg-[#262420] text-ink dark:text-zinc-200 hover:bg-[#eee8dd] dark:hover:bg-[#302c26] border border-[#e5dfd4] dark:border-[#38332c] transition-colors cursor-pointer shadow-2xs"
            >
              <span className="text-[#cc785c] font-bold">(+)</span>
              <span>New Chat</span>
            </button>
          </div>

          {/* Right Actions: Cài đặt phiên, Mode Dark/Light, Zen Mode, Đóng Assistant */}
          <div className="flex items-center gap-1 sm:gap-1.5 shrink-0">
            {/* Desktop wide tools: Cài đặt, Theme */}
            <div className="hidden md:flex items-center gap-1.5 shrink-0">
              {/* Session Settings Button */}
              <button
                type="button"
                onClick={() => setIsSettingsOpen(true)}
                aria-label="Cài đặt phiên nghiên cứu"
                title="Cài đặt phiên nghiên cứu"
                className="inline-flex items-center justify-center w-7 h-7 rounded-lg border border-[#e5dfd4] dark:border-[#38332c] bg-white/80 dark:bg-[#252320] hover:bg-[#f5f1ea] dark:hover:bg-[#2e2b26] text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 transition-colors cursor-pointer shadow-2xs"
              >
                <Settings className="w-3.5 h-3.5" />
              </button>

              {/* Theme Toggle Button (Dark / Light Mode) */}
              <button
                type="button"
                onClick={toggleTheme}
                aria-label={isDark ? "Chuyển sang chế độ sáng" : "Chuyển sang chế độ tối"}
                title={isDark ? "Chế độ sáng" : "Chế độ tối"}
                className="inline-flex items-center justify-center w-7 h-7 rounded-lg border border-[#e5dfd4] dark:border-[#38332c] bg-white/80 dark:bg-[#252320] hover:bg-[#f5f1ea] dark:hover:bg-[#2e2b26] text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 transition-colors cursor-pointer shadow-2xs"
              >
                {isDark ? (
                  <Sun className="w-3.5 h-3.5 text-amber-400" />
                ) : (
                  <Moon className="w-3.5 h-3.5 text-zinc-600" />
                )}
              </button>
            </div>

            {/* Mobile / Narrow Pane Dropdown */}
            <div className="flex md:hidden items-center shrink-0">
              <WorkspaceToolsMenu
                onOpenSettings={() => setIsSettingsOpen(true)}
                isDark={isDark}
                onToggleTheme={toggleTheme}
              />
            </div>

            {/* Zen Workspace Toggle (Hide PDF) */}
            <button
              type="button"
              data-testid="zen-chat-btn"
              onClick={() => setZenMode(zenMode === "workspace" ? "none" : "workspace")}
              aria-label={zenMode === "workspace" ? "Khôi phục chia đôi màn hình" : "Ẩn PDF / Chế độ đối thoại tập trung (Zen Chat)"}
              title={zenMode === "workspace" ? "Khôi phục chia đôi màn hình (Esc)" : "Ẩn PDF / Chế độ đối thoại tập trung (Zen Chat)"}
              className={cn(
                "inline-flex items-center justify-center w-7 h-7 rounded-lg border border-[#e5dfd4] dark:border-[#38332c] text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 transition-colors cursor-pointer shadow-2xs",
                zenMode === "workspace"
                  ? "bg-primary text-white border-primary hover:bg-primary/90"
                  : "bg-white/80 dark:bg-[#252320] hover:bg-[#f5f1ea] dark:hover:bg-[#2e2b26]"
              )}
            >
              {zenMode === "workspace" ? (
                <Minimize2 className="w-3.5 h-3.5" />
              ) : (
                <Maximize2 className="w-3.5 h-3.5" />
              )}
            </button>

            {/* Close Assistant Button (✕) */}
            <button
              type="button"
              data-testid="close-assistant-btn"
              onClick={() => {
                setIsAssistantOpen(false);
                setMobileActiveView("reader");
              }}
              aria-label="Đóng Assistant"
              title="Đóng Assistant (✕)"
              className="inline-flex items-center justify-center w-7 h-7 rounded-lg border border-[#e5dfd4] dark:border-[#38332c] bg-white/80 dark:bg-[#252320] hover:bg-[#f5f1ea] dark:hover:bg-[#2e2b26] text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 transition-colors cursor-pointer shadow-2xs"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        </header>

        {/* TAB 1: SOCRATIC COPILOT CHAT STREAM */}
        {activeRightTab === "chat" && (
          <>
            <div
              ref={chatScrollRef}
              data-testid="chat-scroll-container"
              className="flex-1 overflow-y-auto overflow-x-hidden px-4 sm:px-6 py-5 space-y-6 scrollbar-none"
            >
              {/* Header Badge */}
              <div className="flex items-center justify-between pb-2 border-b border-hairline/60 dark:border-[#282622]">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-lg bg-[#cc785c]/15 text-[#cc785c] flex items-center justify-center">
                    <Sparkles className="w-3.5 h-3.5" />
                  </div>
                  <div>
                    <h2 className="font-serif font-bold text-xs sm:text-sm text-ink dark:text-[#f3f2ef] leading-tight">
                      Socratic Copilot
                    </h2>
                  </div>
                </div>
              </div>



              {/* Socratic Welcome & Empty State when no messages */}
              {messages.length === 0 && (
                <div
                  data-testid="chat-empty-state"
                  className="flex-1 flex flex-col items-center justify-center text-center py-10 px-4 select-none space-y-4 max-w-md mx-auto my-auto animate-in fade-in duration-200"
                >
                  <div className="w-12 h-12 rounded-2xl bg-[#cc785c]/10 text-[#cc785c] flex items-center justify-center border border-[#cc785c]/20 shadow-xs">
                    <Sparkles className="w-6 h-6" />
                  </div>

                  <div className="space-y-1.5">
                    <h3 className="font-serif font-semibold text-sm sm:text-base text-ink dark:text-zinc-100">
                      Socratic Copilot sẵn sàng đối thoại
                    </h3>
                    <p className="text-xs text-muted dark:text-zinc-400 leading-relaxed font-sans">
                      {isRealDocument
                        ? `Đã nạp bài báo "${displayTitle}". Đặt câu hỏi hoặc chọn gợi ý để đối thoại.`
                        : "Chưa có tài liệu nghiên cứu nào được nạp. Hãy tải lên tệp PDF để kích hoạt trích xuất Bounding Box."}
                    </p>
                  </div>

                  {!isRealDocument && (
                    <button
                      type="button"
                      onClick={() => setIsAddDocOpen(true)}
                      className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[#cc785c]/10 text-[#cc785c] hover:bg-[#cc785c]/20 border border-[#cc785c]/20 transition-colors cursor-pointer shadow-2xs"
                    >
                      <FileText className="w-3.5 h-3.5" />
                      <span>+ Tải lên bài báo PDF</span>
                    </button>
                  )}

                  {/* Empty state hint chips grid */}
                  <div className="w-full pt-3 grid grid-cols-1 sm:grid-cols-2 gap-2 text-left relative z-20 pointer-events-auto">
                    {[
                      {
                        label: "Tóm tắt paper",
                        prompt: "Hãy tóm tắt ngắn gọn và toàn diện nội dung bài báo này (mục tiêu, phương pháp chính và kết luận).",
                      },
                      {
                        label: "Đóng góp chính",
                        prompt: "Những đóng góp và điểm mới cốt lõi (key contributions) của nghiên cứu này là gì?",
                      },
                      {
                        label: "Phương pháp & Kiến trúc",
                        prompt: "Giải thích chi tiết phương pháp nghiên cứu và kiến trúc mô hình được đề xuất trong bài báo.",
                      },
                      {
                        label: "Hạn chế & Thách thức",
                        prompt: "Những hạn chế và thách thức chính của nghiên cứu này là gì, và các tác giả gợi ý hướng phát triển ra sao?",
                      },
                    ].map((item, idx) => (
                      <button
                        key={idx}
                        type="button"
                        data-testid={`empty-hint-chip-${idx}`}
                        onClick={() => {
                          onChangeText(item.prompt);
                          onSend(item.prompt);
                        }}
                        className="flex items-center gap-2 p-2.5 rounded-xl border border-[#e5dfd4] dark:border-[#38332c] bg-white dark:bg-[#201e1a] hover:border-coral-500/60 hover:bg-coral-500/5 transition-all cursor-pointer shadow-2xs text-left group active:scale-95 select-none"
                      >
                        <Sparkles className="w-3.5 h-3.5 text-coral-600 dark:text-coral-400 shrink-0" />
                        <span className="text-xs font-semibold text-ink dark:text-zinc-200 group-hover:text-coral-600 dark:group-hover:text-coral-400">
                          {item.label}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Chat Messages Stream */}
              {messages.map((message) => {
                const isUser = message.role === "user";

                if (isUser) {
                  return (
                    <div key={message.id} className="flex justify-end">
                      <div className="max-w-xl px-4 py-3 rounded-2xl rounded-tr-xs bg-white dark:bg-[#252320] border border-[#e8e4dc] dark:border-[#38332c] text-ink dark:text-zinc-100 text-xs sm:text-sm font-anthropic-sans shadow-xs">
                        <div className="flex items-center gap-1.5 text-3xs font-mono text-ink-muted dark:text-zinc-400 mb-1">
                          <User className="w-3 h-3 text-[#cc785c]" />
                          <span className="font-medium">Học giả</span>
                        </div>
                        <div className="leading-relaxed whitespace-pre-wrap">{message.content}</div>
                      </div>
                    </div>
                  );
                }

                return (
                  <div key={message.id} className="flex gap-3 max-w-2xl">
                    <div className="w-7 h-7 rounded-xl bg-[#cc785c]/10 border border-[#cc785c]/20 text-[#cc785c] flex items-center justify-center shrink-0 mt-1 shadow-2xs">
                      <Sparkles className="w-3.5 h-3.5" />
                    </div>

                    <div className="flex-1 space-y-2.5 min-w-0">
                      <div className="text-3xs font-mono font-medium text-ink-muted dark:text-zinc-500 flex items-center gap-2">
                        <span className="font-semibold text-ink dark:text-zinc-300 font-anthropic-sans">
                          Socratic
                        </span>
                      </div>

                      {/* Presupposition Alert */}
                      {message.presupposition_alert && (
                        <PresuppositionBanner alert={message.presupposition_alert} />
                      )}

                      {/* Socratic Thinking Block with Agent Activity Stepper */}
                      {(message.thought || (message.is_streaming && !message.content)) && (
                        <SocraticThinkingBlock message={message} />
                      )}

                      {/* Formatted Assistant Body with Inline Citations */}
                      <AcademicMarkdownRenderer
                        content={message.content}
                        isStreaming={message.is_streaming}
                        citations={message.citations}
                        onCitationClick={(citationOrId, maybeCitId) => {
                          const citId = typeof citationOrId === "string" ? citationOrId : (maybeCitId || "");
                          let matched = typeof citationOrId === "object" ? citationOrId : null;
                          if (!matched && message.citations && message.citations.length > 0) {
                            matched = message.citations.find(
                              (c) => c.citation_id === citId || c.citation_id === `cit_${citId}`
                            ) || null;
                            if (!matched && citId) {
                              const numericPart = citId.replace(/\D/g, "");
                              if (numericPart) {
                                const idx = parseInt(numericPart, 10) - 1;
                                if (!isNaN(idx) && message.citations[idx]) {
                                  matched = message.citations[idx];
                                }
                              }
                            }
                            if (!matched && message.citations.length === 1) {
                              matched = message.citations[0];
                            }
                          }
                          const targetCitId = (matched as unknown as Record<string, unknown> | null)?.citation_id as string || citId;
                          const currentActiveCitId = useReaderStore.getState().activeCitationId;

                          // Toggle off if clicking the currently active citation
                          if (
                            currentActiveCitId &&
                            (currentActiveCitId === targetCitId ||
                              currentActiveCitId === citId ||
                              currentActiveCitId === `cit_${citId}` ||
                              `cit_${currentActiveCitId}` === targetCitId)
                          ) {
                            setActiveBboxStore(null);
                            setActiveCitation(null, null);
                            return;
                          }

                          if (matched) {
                            const raw = matched as unknown as Record<string, unknown>;
                            const docId = (raw.document_id || raw.paper_id) as string | undefined;
                            const pageNum = (raw.page_number || raw.page) as number | undefined;
                            const bboxes = (raw.bounding_boxes || (raw.bbox ? [raw.bbox] : [])) as BoundingBox[];
                            const primaryBox = (bboxes[0] || raw.bbox || null) as BoundingBox | null;
                            const resolvedPage = pageNum || primaryBox?.[4] || 1;

                            if (docId && docId !== activeDocumentId && openDocumentIds.includes(docId)) {
                              setActiveDocumentId(docId);
                            }

                            if (primaryBox || bboxes.length > 0) {
                              setActiveBboxStore(primaryBox);
                              setActiveCitation(targetCitId, primaryBox, resolvedPage, primaryBox ? [primaryBox] : null);
                              setCurrentPage(resolvedPage);
                              useReaderStore.getState().setCurrentPage(resolvedPage);
                              setMobileActiveView("reader");
                            } else if (resolvedPage) {
                              setActiveCitation(targetCitId, null, resolvedPage, null);
                              setCurrentPage(resolvedPage);
                              useReaderStore.getState().setCurrentPage(resolvedPage);
                              setMobileActiveView("reader");
                            }
                          }
                        }}
                      />

                      {/* Action Toolbar */}
                      {!message.is_streaming && (
                        <div className="flex items-center gap-1 pt-1 text-ink-muted dark:text-zinc-500 text-xs">
                          <button
                            type="button"
                            onClick={() => handleCopy(message.id, message.content)}
                            title="Sao chép câu trả lời"
                            className="p-1 rounded-lg hover:bg-white dark:hover:bg-[#252320] border border-transparent hover:border-[#e5dfd4] dark:hover:border-[#38332c] hover:text-ink dark:hover:text-zinc-200 transition-all cursor-pointer"
                          >
                            {copiedMsgId === message.id ? (
                              <Check className="w-3 h-3 text-emerald-500" />
                            ) : (
                              <Copy className="w-3 h-3" />
                            )}
                          </button>
                          <button
                            type="button"
                            title="Hữu ích"
                            className="p-1 rounded-lg hover:bg-white dark:hover:bg-[#252320] border border-transparent hover:border-[#e5dfd4] dark:hover:border-[#38332c] hover:text-ink dark:hover:text-zinc-200 transition-all cursor-pointer"
                          >
                            <ThumbsUp className="w-3 h-3" />
                          </button>
                          <button
                            type="button"
                            title="Chưa chính xác"
                            className="p-1 rounded-lg hover:bg-white dark:hover:bg-[#252320] border border-transparent hover:border-[#e5dfd4] dark:hover:border-[#38332c] hover:text-ink dark:hover:text-zinc-200 transition-all cursor-pointer"
                          >
                            <ThumbsDown className="w-3 h-3" />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Bottom-Docked Input Bar */}
            <div
              data-testid="chat-composer-container"
              className="shrink-0 pb-4 pt-2 px-3 bg-gradient-to-t from-[#faf9f5] via-[#faf9f5]/90 to-transparent dark:from-[#181715] dark:via-[#181715]/90 z-10 overflow-x-hidden max-w-full"
            >
              {/* Short Prompt Suggestions - Sleek Horizontal Pills at the Bottom */}
              {messages.length === 0 && !isGenerating && (
                <div className="w-full max-w-3xl md:max-w-4xl mx-auto px-4 mb-2.5 relative z-20 pointer-events-auto">
                  <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none flex-nowrap touch-pan-x py-1">
                    {[
                      {
                        label: "Tóm tắt paper",
                        prompt: "Hãy tóm tắt ngắn gọn và toàn diện nội dung bài báo này (mục tiêu, phương pháp chính và kết luận).",
                      },
                      {
                        label: "Đóng góp chính",
                        prompt: "Những đóng góp và điểm mới cốt lõi (key contributions) của nghiên cứu này là gì?",
                      },
                      {
                        label: "Phương pháp & Kiến trúc",
                        prompt: "Giải thích chi tiết phương pháp nghiên cứu và kiến trúc mô hình được đề xuất trong bài báo.",
                      },
                      {
                        label: "Hạn chế & Thách thức",
                        prompt: "Những hạn chế và thách thức chính của nghiên cứu này là gì, và các tác giả gợi ý hướng phát triển ra sao?",
                      },
                    ].map((item, idx) => (
                      <button
                        key={idx}
                        type="button"
                        data-testid={`bottom-hint-chip-${idx}`}
                        onClick={() => {
                          onChangeText(item.prompt);
                          onSend(item.prompt);
                        }}
                        className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-sans border border-[#e5dfd4] dark:border-[#38342e] bg-white/90 dark:bg-[#22211e] text-ink-muted dark:text-zinc-400 hover:text-ink dark:hover:text-zinc-100 hover:border-primary/50 hover:bg-[#f6f2ea] dark:hover:bg-[#2b2722] transition-all cursor-pointer shrink-0 shadow-2xs whitespace-nowrap active:scale-95 select-none"
                      >
                        <Sparkles className="w-3 h-3 text-primary shrink-0" />
                        <span>{item.label}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {isGenerating && (
                <div className="flex justify-center mb-2">
                  <button
                    type="button"
                    onClick={onStopGeneration}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white dark:bg-[#252320] border border-[#e5dfd4] dark:border-zinc-700/60 text-ink dark:text-zinc-200 text-xs font-sans shadow-xs hover:bg-[#f4efe6] dark:hover:bg-[#2e2a25] transition-colors cursor-pointer"
                  >
                    <Square className="w-3 h-3 fill-current text-[#cc785c]" />
                    <span>Dừng</span>
                  </button>
                </div>
              )}

              <DashboardChatInputBox
                inputText={inputText}
                onChangeText={onChangeText}
                onSend={onSend}
                isGenerating={isGenerating}
                onUploadFile={onUploadFile}
                contextChip={activeContextChip}
                onRemoveContextChip={() => setActiveContextChip(null)}
                onContextChipClick={(chip) => {
                  if (chip.bbox) {
                    setActiveBboxStore(chip.bbox);
                    setCurrentPage(chip.bbox[4]);
                  } else if (chip.pageNumber) {
                    setCurrentPage(chip.pageNumber);
                  }
                  setMobileActiveView("reader");
                }}
              />
            </div>
          </>
        )}

        {/* TAB 2: SMART NOTES & AI SYNTHESIS */}
        {activeRightTab === "notes" && (
          <NotesPanelContainer
            documentId={
              activeDocumentId && activeDocumentId !== "doc-default"
                ? activeDocumentId
                : null
            }
          />
        )}

        {/* TAB 3: GROUNDED 3-POINT SUMMARY */}
        {activeRightTab === "summary" && (
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 scrollbar-none">
            <div className="flex items-center justify-between pb-2 border-b border-hairline dark:border-[#2f2b26]">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-primary" />
                <h3 className="font-serif font-bold text-sm text-ink dark:text-zinc-100">
                  3 Luận Điểm Cốt Lõi
                </h3>
              </div>
              {isRealDocument && (
                <button
                  type="button"
                  onClick={handleRegenerateSummary}
                  disabled={isGeneratingSummary}
                  className="px-2.5 py-1 rounded bg-surface-soft hover:bg-surface-cream-strong border border-hairline text-xs text-primary font-medium transition-colors disabled:opacity-50 cursor-pointer"
                >
                  {isGeneratingSummary ? "Đang tạo lại..." : "Tạo lại tóm tắt"}
                </button>
              )}
            </div>
            <DocumentGroundedSummaryCard
              summary={activeSummary}
              paperTitle={displayTitle}
              isGenerating={isGeneratingSummary}
              isStreaming={isStreamingSummary}
              onGenerateSummary={handleRegenerateSummary}
              onStreamSummary={handleStreamSummary}
            />
          </div>
        )}

        {/* TAB 4: DOCUMENT STRUCTURE (TOC) */}
        {activeRightTab === "structure" && (
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 scrollbar-none text-xs">
            <div className="flex items-center justify-between pb-3 border-b border-hairline dark:border-[#2f2b26]">
              <div className="flex items-center gap-2">
                <ListTree className="w-4 h-4 text-primary" />
                <h3 className="font-serif font-bold text-sm text-ink dark:text-zinc-100">
                  Cấu trúc &amp; Phân mục bài báo
                </h3>
              </div>
              {isRealDocument && (
                <button
                  type="button"
                  onClick={handleOpenParseConfig}
                  className="px-2.5 py-1 rounded bg-surface-soft hover:bg-surface-cream-strong border border-hairline text-xs text-primary font-medium transition-colors cursor-pointer"
                >
                  Cấu hình bóc tách
                </button>
              )}
            </div>

            {documentStructure?.abstract && (
              <div className="p-3.5 rounded-md bg-surface-soft dark:bg-[#201e1b] border border-hairline dark:border-[#2e2a24]">
                <h4 className="font-sans font-semibold text-primary uppercase text-[10px] tracking-wider mb-1">
                  Tóm tắt nghiên cứu (Abstract)
                </h4>
                <p className="text-muted leading-relaxed font-serif text-[11px]">
                  {documentStructure.abstract}
                </p>
              </div>
            )}

            <div className="space-y-2">
              <h4 className="text-[10px] uppercase font-mono tracking-wider text-muted font-semibold">
                Danh sách các phần mục
              </h4>

              {(!documentStructure?.sections || documentStructure.sections.length === 0) ? (
                <div className="p-6 text-center text-muted border border-dashed border-hairline rounded-md space-y-2">
                  <p>Chưa phát hiện phân mục tự động cho bài báo này.</p>
                  {isRealDocument && (
                    <button
                      type="button"
                      onClick={handleOpenParseConfig}
                      className="px-3 py-1.5 rounded-md bg-surface-soft hover:bg-surface-cream-strong border border-hairline text-primary font-medium text-xs cursor-pointer"
                    >
                      Cấu hình bóc tách cấu trúc
                    </button>
                  )}
                </div>
              ) : (
                <div className="space-y-1">
                  {documentStructure.sections.map((sec, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => setCurrentPage(sec.page_number)}
                      className="w-full text-left p-2.5 rounded-md hover:bg-surface-cream-strong dark:hover:bg-[#24221f] border border-hairline dark:border-[#2b2722] flex items-center justify-between group transition-colors"
                    >
                      <span className="font-sans text-xs text-ink dark:text-zinc-200 group-hover:text-primary transition-colors font-medium truncate pr-2">
                        {sec.title}
                      </span>
                      <span className="text-[10px] font-mono text-muted shrink-0">
                        Trang {sec.page_number}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 5: EXTRACTED REFERENCES */}
        {activeRightTab === "references" && (
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-3 scrollbar-none text-xs">
            <div className="flex items-center justify-between pb-3 border-b border-hairline dark:border-[#2f2b26]">
              <div className="flex items-center gap-2">
                <Quote className="w-4 h-4 text-primary" />
                <h3 className="font-serif font-bold text-sm text-ink dark:text-zinc-100">
                  Tài liệu tham khảo ({(documentReferences?.references || []).length})
                </h3>
              </div>
            </div>

            {(!documentReferences?.references || documentReferences.references.length === 0) ? (
              <div className="p-8 text-center text-muted border border-dashed border-hairline rounded-md">
                Chưa có tài liệu tham khảo nào được trích xuất.
              </div>
            ) : (
              documentReferences.references.map((ref) => {
                const parsed = ref.parsed;
                const arxivUrl = parsed.arxiv_id ? `https://arxiv.org/abs/${parsed.arxiv_id}` : null;
                const doiUrl = parsed.doi ? `https://doi.org/${parsed.doi}` : null;

                return (
                  <div
                    key={ref.ref_index}
                    className="p-3 rounded-md bg-surface-soft/60 dark:bg-[#22201d] border border-hairline dark:border-[#302c26] space-y-1.5"
                  >
                    <div className="flex items-start gap-2">
                      <span className="inline-flex items-center justify-center w-5 h-5 rounded bg-primary/10 text-primary font-mono text-[11px] font-semibold shrink-0">
                        [{ref.ref_index}]
                      </span>
                      <h5 className="flex-1 font-serif font-medium text-ink dark:text-zinc-100 text-xs leading-snug">
                        {parsed.title || ref.raw_text}
                      </h5>
                    </div>

                    {parsed.authors && parsed.authors.length > 0 && (
                      <p className="text-[11px] text-muted font-sans pl-7">
                        {parsed.authors.join(", ")} {parsed.year ? `(${parsed.year})` : ""}
                      </p>
                    )}

                    <div className="flex items-center gap-3 pl-7 pt-1">
                      {arxivUrl && (
                        <a
                          href={arxivUrl}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-[11px] text-primary hover:underline font-mono"
                        >
                          <span>arXiv:{parsed.arxiv_id}</span>
                          <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      )}
                      {doiUrl && (
                        <a
                          href={doiUrl}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-[11px] text-teal-600 dark:text-teal-400 hover:underline font-mono"
                        >
                          <span>DOI:{parsed.doi}</span>
                          <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        )}
      </section>

      {/* ========================================================================= */}
      {/* 3. MODALS & AUXILIARY DIALOGS                                             */}
      {/* ========================================================================= */}
      <AddDocumentModal
        isOpen={isAddDocOpen}
        onClose={() => setIsAddDocOpen(false)}
        availableLibraryDocs={documentsData?.data || []}
        currentDocumentIds={effectiveOpenIds}
        onAddByDocumentId={handleAddByDocumentId}
        onAddByUrl={handleAddByUrl}
      />

      <CreateNoteDialog
        isOpen={isCreateNoteOpen}
        onClose={() => setIsCreateNoteOpen(false)}
        documentId={
          activeDocumentId && activeDocumentId !== "doc-default"
            ? activeDocumentId
            : undefined
        }
        selectedText={noteInitialText}
        pageNumber={notePageNumber}
        onSubmit={handleCreateNoteSubmit}
      />

      <ReferenceListModal
        isOpen={isRefModalOpen}
        onClose={() => setIsRefModalOpen(false)}
        references={documentReferences?.references || []}
        onReextract={handleReextractReferences}
        documentId={activeDocumentId && activeDocumentId !== "doc-default" ? activeDocumentId : ""}
        sessionId={activeSessionId}
      />

      {/* Parse Configuration Modal */}
      {activeDocumentId && activeDocumentId !== "doc-default" && (
        <ParseConfigModal
          isOpen={isParseConfigOpen}
          onClose={() => setIsParseConfigOpen(false)}
          documentId={activeDocumentId}
          documentTitle={currentDocTitle}
        />
      )}

      {/* Star Document with Folder Selection Modal */}
      {starTargetDoc && (
        <StarDocumentModal
          isOpen={isStarModalOpen}
          onClose={() => {
            setIsStarModalOpen(false);
            setStarTargetDoc(null);
          }}
          documentId={starTargetDoc.id}
          documentTitle={starTargetDoc.title}
          isStarred={starTargetDoc.isStarred}
        />
      )}

      {/* Session Settings Modal */}
      {effectiveSessionId && (
        <SessionSettingsModal
          isOpen={isSettingsOpen}
          onClose={() => setIsSettingsOpen(false)}
          sessionId={effectiveSessionId}
          currentTitle={sessionTitle || currentDocTitle || "Phiên nghiên cứu"}
          version={sessionVersion}
          documentCount={documentCount}
          createdAt={createdAt}
          onUpdateTitle={handleUpdateTitle}
          onDeleteSession={handleDeleteSession}
        />
      )}

      {/* Academic Context Menu Guard (Guarantees right-click never triggers browser back / exits to landing page) */}
      {contextMenu.isOpen && (
        <div
          data-testid="academic-context-menu"
          className="fixed z-50 min-w-[210px] py-1.5 px-1 bg-white/95 dark:bg-[#201e1b]/95 backdrop-blur-md rounded-xl border border-[#e5dfd4] dark:border-[#38332c] shadow-2xl text-xs text-ink dark:text-zinc-200 animate-in fade-in zoom-in-95 duration-100 select-none"
          style={{ top: contextMenu.y, left: contextMenu.x }}
          onClick={(e) => e.stopPropagation()}
        >
          {contextMenu.selectedText && (
            <>
              <button
                type="button"
                onClick={() => {
                  navigator.clipboard.writeText(contextMenu.selectedText);
                  setContextMenu((prev) => ({ ...prev, isOpen: false }));
                }}
                className="w-full flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-left text-xs hover:bg-[#f3eee5] dark:hover:bg-[#2d2924] hover:text-primary transition-colors cursor-pointer"
              >
                <Copy className="w-3.5 h-3.5 text-muted hover:text-primary" />
                <span>Sao chép đoạn trích</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  onChangeText(contextMenu.selectedText);
                  setActiveRightTab("chat");
                  setContextMenu((prev) => ({ ...prev, isOpen: false }));
                }}
                className="w-full flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-left text-xs hover:bg-[#f3eee5] dark:hover:bg-[#2d2924] hover:text-primary transition-colors cursor-pointer"
              >
                <Sparkles className="w-3.5 h-3.5 text-[#cc785c]" />
                <span>Hỏi Socratic Copilot</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  setNoteInitialText(contextMenu.selectedText);
                  setNotePageNumber(currentPage);
                  setIsCreateNoteOpen(true);
                  setContextMenu((prev) => ({ ...prev, isOpen: false }));
                }}
                className="w-full flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-left text-xs hover:bg-[#f3eee5] dark:hover:bg-[#2d2924] hover:text-primary transition-colors cursor-pointer"
              >
                <BookMarked className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                <span>Thêm vào Sổ tay</span>
              </button>

              <div className="my-1 border-t border-hairline/60 dark:border-[#2f2b26]" />
            </>
          )}

          <button
            type="button"
            onClick={() => {
              onResetChat();
              setContextMenu((prev) => ({ ...prev, isOpen: false }));
            }}
            className="w-full flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-left text-xs hover:bg-[#f3eee5] dark:hover:bg-[#2d2924] hover:text-primary transition-colors cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5 text-muted" />
            <span>Làm mới hội thoại</span>
          </button>

          <button
            type="button"
            onClick={() => {
              setIsSettingsOpen(true);
              setContextMenu((prev) => ({ ...prev, isOpen: false }));
            }}
            className="w-full flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-left text-xs hover:bg-[#f3eee5] dark:hover:bg-[#2d2924] hover:text-primary transition-colors cursor-pointer"
          >
            <Settings className="w-3.5 h-3.5 text-muted" />
            <span>Cài đặt phiên nghiên cứu</span>
          </button>

          <div className="my-1 border-t border-hairline/60 dark:border-[#2f2b26]" />

          <button
            type="button"
            onClick={() => {
              toggleTheme();
              setContextMenu((prev) => ({ ...prev, isOpen: false }));
            }}
            className="w-full flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-left text-xs hover:bg-[#f3eee5] dark:hover:bg-[#2d2924] hover:text-primary transition-colors cursor-pointer"
          >
            {isDark ? (
              <>
                <Sun className="w-3.5 h-3.5 text-amber-400" />
                <span>Chuyển sang chế độ sáng</span>
              </>
            ) : (
              <>
                <Moon className="w-3.5 h-3.5 text-zinc-600" />
                <span>Chuyển sang chế độ tối</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* Vertical Edge Dock for Secondary Utilities */}
      <div className="absolute top-14 right-3 z-30">
        <VerticalEdgeDock
          onToggleInfo={() => setIsStructureSheetOpen((prev) => !prev)}
          onToggleNotes={() => {
            if (!isAssistantOpen) setIsAssistantOpen(true);
            setActiveRightTab(activeRightTab === "notes" ? "chat" : "notes");
          }}
          onToggleAssistant={() => setIsAssistantOpen((prev) => !prev)}
          isAssistantOpen={isAssistantOpen}
        />
      </div>

      {/* Floating AI Assistant FAB (rendered when assistant is closed) */}
      {!isAssistantOpen && (
        <button
          type="button"
          data-testid="floating-assistant-fab"
          onClick={() => {
            setIsAssistantOpen(true);
            setMobileActiveView("workspace");
          }}
          aria-label="Mở Assistant"
          title="Mở Assistant"
          className="fixed bottom-6 right-6 z-40 flex items-center gap-2 px-4 py-3 rounded-full bg-[#cc785c] hover:bg-[#b8674d] text-white shadow-xl hover:shadow-2xl hover:scale-105 active:scale-95 transition-all cursor-pointer group"
        >
          <Sparkles className="w-5 h-5 transition-transform group-hover:rotate-12" />
          <span className="text-xs font-semibold tracking-wide">Assistant</span>
        </button>
      )}
    </div>
  );
}
