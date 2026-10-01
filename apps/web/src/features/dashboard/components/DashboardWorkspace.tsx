import { useState, useRef, useEffect, useMemo } from "react";
import {
  RotateCcw,
  Sparkles,
  BookMarked,
  ListTree,
  Quote,
  MessageSquare,
  User,
  BrainCircuit,
  Copy,
  Check,
  ThumbsUp,
  ThumbsDown,
  Square,
  ExternalLink,
  ArrowUpRight,
  Settings,
  Archive,
  Sun,
  Moon,
  PanelLeft,
  FileText,
} from "lucide-react";
import type { ChatMessage } from "@/types/dashboard";
import { useTheme } from "@/hooks/useTheme";
import { useDashboardStore } from "../stores/useDashboardStore";
import { useWorkspaceStore } from "../stores/useWorkspaceStore";
import { useReaderStore } from "@/features/reader/stores/useReaderStore";
import { MathRenderer } from "@/components/shared/MathRenderer";
import { DocumentGroundedSummaryCard } from "./DocumentGroundedSummaryCard";
import { CitationBadge } from "./CitationBadge";
import { PresuppositionBanner } from "./PresuppositionBanner";
import { DashboardChatInputBox } from "./DashboardChatInputBox";
import { DocumentTabBar } from "@/features/reader/components/DocumentTabBar";
import { ViewportControls } from "@/features/reader/components/ViewportControls";
import { PdfCanvasViewer } from "@/features/reader/components/PdfCanvasViewer";
import { DocumentStructureSheet } from "@/features/reader/components/DocumentStructureSheet";
import { DocumentChunksSheet } from "@/features/reader/components/DocumentChunksSheet";
import { ReferenceListModal } from "@/features/reader/components/ReferenceListModal";
import { NotesPanelContainer } from "@/features/notes/components/NotesPanelContainer";
import { CreateNoteDialog } from "@/features/notes/components/CreateNoteDialog";
import { AddDocumentModal } from "@/features/sessions/components/AddDocumentModal";
import { SessionSettingsModal } from "@/features/sessions/components/SessionSettingsModal";
import { ExportBundleDialog } from "@/features/sessions/components/ExportBundleDialog";
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
  useExportSessionBundleMutation,
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
}

const DEFAULT_GROUNDED_SUMMARY: DocumentSummaryResponse = {
  document_id: "doc-vaswani-2017",
  problem_statement: {
    text: "Các mô hình chuỗi tuần tự trước đây (RNN, LSTM, GRU) phụ thuộc chặt chẽ vào tính toán tuần tự dọc theo trục thời gian, cản trở việc song song hóa trong huấn luyện và gặp khó khăn khi mô hình hóa các phụ thuộc xa giữa các từ trong văn bản.",
    bounding_boxes: [[0.1, 0.15, 0.9, 0.35, 1]],
  },
  contributions: {
    text: "Đề xuất kiến trúc Transformer loại bỏ hoàn toàn mạng đệ quy, chỉ dựa trên cơ chế Self-Attention đa đầu (Multi-Head Attention) và hàm mã hóa vị trí Positional Encoding:\n$$PE_{(pos, 2i)} = \\sin\\left(\\frac{pos}{10000^{2i/d_{\\text{model}}}}\\right)$$\n$$PE_{(pos, 2i+1)} = \\cos\\left(\\frac{pos}{10000^{2i/d_{\\text{model}}}}\\right)$$\nĐạt BLEU score kỷ lục 28.4 trên tập dịch máy WMT 2014 English-to-German.",
    bounding_boxes: [[0.15, 0.62, 0.85, 0.88, 6]],
  },
  limitations: {
    text: "Độ phức tạp tính toán và tiêu thụ bộ nhớ của ma trận chú ý Self-Attention là $O(n^2)$ theo độ dài chuỗi $n$, khiến việc mở rộng sang các tài liệu cực dài đòi hỏi tài nguyên tính toán phần cứng lớn.",
    bounding_boxes: [[0.1, 0.7, 0.9, 0.95, 7]],
  },
};

/**
 * Formats assistant message markdown into paragraphs with KaTeX support
 */
function FormattedAssistantMessage({ content }: { content: string }) {
  const renderedContent = useMemo(() => {
    const blocks = content.split("$$");

    return blocks.map((chunk, idx) => {
      if (idx % 2 === 1) {
        return (
          <div
            key={idx}
            className="my-3 p-3.5 rounded-2xl bg-[#f7f4ee] dark:bg-[#21201d] border border-[#e5dfd4] dark:border-[#38332c] text-center overflow-x-auto text-coral-600 dark:text-amber-400 shadow-2xs"
          >
            <MathRenderer math={chunk.trim()} block />
          </div>
        );
      }

      const lines = chunk.split("\n").filter((l) => l.length > 0);
      return (
        <div key={idx} className="space-y-2.5">
          {lines.map((line, lIdx) => {
            const tokens = line.split(/(\*\*[^*]+\*\*|\$[^$]+\$)/g);

            return (
              <p key={lIdx} className="leading-relaxed text-xs sm:text-sm text-ink dark:text-zinc-200">
                {tokens.map((token, tIdx) => {
                  if (token.startsWith("**") && token.endsWith("**")) {
                    return (
                      <strong key={tIdx} className="font-semibold text-ink dark:text-zinc-100">
                        {token.slice(2, -2)}
                      </strong>
                    );
                  }
                  if (token.startsWith("$") && token.endsWith("$") && token.length > 2) {
                    return (
                      <MathRenderer
                        key={tIdx}
                        math={token.slice(1, -1)}
                        className="text-coral-600 dark:text-amber-400 px-0.5"
                      />
                    );
                  }
                  return token;
                })}
              </p>
            );
          })}
        </div>
      );
    });
  }, [content]);

  return <div className="space-y-3 font-anthropic-sans leading-relaxed">{renderedContent}</div>;
}

export function DashboardWorkspace({
  messages,
  inputText,
  onChangeText,
  onSend,
  isGenerating,
  onStopGeneration,
  onUploadFile,
  onResetChat,
  summary = DEFAULT_GROUNDED_SUMMARY,
  sessionId,
  sessionTitle,
  sessionVersion: initialSessionVersion = 1,
  documentCount = 1,
  createdAt = new Date().toISOString(),
  onDeletedSession,
}: DashboardWorkspaceProps) {
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
  const setActiveCitation = useReaderStore((s) => s.setActiveCitation);

  // Active Bbox Synchronization
  const activeBbox = activeBboxStore || activeBboxReader;

  // Local Modal States
  const [isAddDocOpen, setIsAddDocOpen] = useState(false);
  const [isCreateNoteOpen, setIsCreateNoteOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isExportOpen, setIsExportOpen] = useState(false);
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
  const exportMutation = useExportSessionBundleMutation();

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

  const handleExportBundle = async (): Promise<Blob> => {
    if (!sessionId) throw new Error("No active session to export");
    return await exportMutation.mutateAsync(sessionId);
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
  const { data: liveSummary } = useDocumentSummary(activeDocumentId);
  const { data: sessionDetail } = useSessionDetail(activeSessionId);

  const deleteDocMutation = useDeleteDocumentMutation();
  const addSessionDocMutation = useAddSessionDocumentMutation();
  const createNoteMutation = useCreateNoteMutation();

  // Auto-select latest/first real document if none is actively selected and no session is active
  useEffect(() => {
    if (!activeSessionId && documentsData?.data && documentsData.data.length > 0) {
      if (!activeDocumentId || activeDocumentId === "doc-default") {
        const firstDoc = documentsData.data[0];
        setActiveDocumentId(firstDoc.id);
        setDocument(firstDoc.id, firstDoc.title || firstDoc.filename);
      }
    }
  }, [activeSessionId, documentsData?.data, activeDocumentId, setActiveDocumentId, setDocument]);

  const currentDocTitle =
    documentDetail?.title ||
    workspaceDocTitle ||
    documentsData?.data?.[0]?.title ||
    documentsData?.data?.[0]?.filename ||
    "Tài liệu nghiên cứu";

  // Effective Documents List for Multi-Paper Tab Bar
  const effectiveOpenIds = useMemo(() => {
    if (openDocumentIds.length > 0) return openDocumentIds;
    if (activeDocumentId && activeDocumentId !== "doc-default") return [activeDocumentId];
    if (documentsData?.data && documentsData.data.length > 0) {
      return [documentsData.data[0].id];
    }
    if (workspaceDocId && workspaceDocId !== "doc-default") {
      return [workspaceDocId];
    }
    return [];
  }, [openDocumentIds, activeDocumentId, documentsData, workspaceDocId]);

  const effectiveDocuments: DocumentListItem[] = useMemo(() => {
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
  }, [documentsData, workspaceDocId, currentDocTitle]);

  // Page Sync when activeBbox changes
  useEffect(() => {
    if (activeBbox && activeBbox[4]) {
      setCurrentPage(activeBbox[4]);
    }
  }, [activeBbox, setCurrentPage]);

  // Scroll active Bbox into view
  useEffect(() => {
    if (activeBbox && activeBbox[4] && bboxRef.current && typeof bboxRef.current.scrollIntoView === "function") {
      bboxRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
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

  const handleCloseDoc = (docId: string) => {
    removeOpenDocument(docId);
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
      } else {
        setActiveDocumentId("");
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

  const handleAddToNote = (selectedText: string, pageNumber: number) => {
    setNoteInitialText(selectedText);
    setNotePageNumber(pageNumber);
    setIsCreateNoteOpen(true);
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
    (isRealDocument ? null : summary || DEFAULT_GROUNDED_SUMMARY);

  const queryClient = useQueryClient();
  const sessionDetailQuery = useSessionDetail(activeSessionId);
  const updateViewportMutation = useUpdateSessionViewportMutation();
  const sessionVersion = sessionDetailQuery.data?.data.version ?? initialSessionVersion;

  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);

  const handleExportPdf = async () => {
    if (!activeDocumentId || activeDocumentId === "doc-default") return;
    setIsExportingPdf(true);
    try {
      const blob = await documentsApi.exportAnnotatedPdf(activeDocumentId);
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = `annotated_${currentDocTitle.replace(/\s+/g, "_")}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      console.warn("Failed to export annotated PDF:", err);
    } finally {
      setIsExportingPdf(false);
    }
  };

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
  useEffect(() => {
    if (!activeSessionId || !activeDocumentId || activeDocumentId === "doc-default") return;
    const sessionDocs = sessionDetail?.data?.documents;
    if (sessionDocs && !sessionDocs.some((d) => d.id === activeDocumentId)) return;
    const timer = setTimeout(() => {
      updateViewportMutation.mutate({
        sessionId: activeSessionId,
        etag: `v${sessionVersion}`,
        data: {
          active_document_id: activeDocumentId,
          active_tab: (activeRightTab === "chat" || activeRightTab === "notes" || activeRightTab === "summary")
            ? activeRightTab
            : "chat",
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
      onContextMenu={handleContextMenu}
      className="flex-1 flex flex-col lg:flex-row h-full overflow-hidden bg-[#faf9f5] dark:bg-[#181715] select-text"
    >
      {/* Mobile Top Navigation & Segmented View Switcher (Visible only on < lg screens) */}
      <div className="lg:hidden h-11 px-3 border-b border-[#e6dfd8] dark:border-[#2a2824] bg-white/80 dark:bg-[#181715]/80 backdrop-blur-md flex items-center justify-between shrink-0 select-none z-20">
        {/* Left: Mobile Sidebar Menu Toggle & Title */}
        <div className="flex items-center gap-2 min-w-0">
          <button
            type="button"
            onClick={toggleSidebar}
            aria-label="Mở danh sách phiên nghiên cứu"
            title="Mở menu phiên nghiên cứu"
            className="p-1.5 rounded-lg hover:bg-surface-soft dark:hover:bg-[#252320] text-muted hover:text-ink dark:text-zinc-400 dark:hover:text-zinc-100 transition-colors cursor-pointer"
          >
            <PanelLeft className="w-4 h-4 text-coral-600 dark:text-coral-400" />
          </button>
          <span className="text-xs font-serif font-medium text-ink dark:text-zinc-200 truncate max-w-[130px] sm:max-w-[220px]">
            {displayTitle}
          </span>
        </div>

        {/* Center/Right: Segmented Switcher Pill [ 📄 Tài liệu ] [ 💬 Trợ lý ] */}
        <div className="inline-flex p-0.5 rounded-lg bg-[#eee9df] dark:bg-[#24221f] text-xs font-medium">
          <button
            type="button"
            onClick={() => setMobileActiveView("reader")}
            aria-label="Chuyển sang chế độ xem tài liệu PDF"
            className={cn(
              "inline-flex items-center gap-1 px-2.5 py-1 rounded-md transition-all cursor-pointer text-[11px]",
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
              "inline-flex items-center gap-1 px-2.5 py-1 rounded-md transition-all cursor-pointer text-[11px]",
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
        className={cn(
          "w-full lg:w-1/2 flex flex-col h-full border-b-0 lg:border-r border-[#e6dfd8] dark:border-[#2a2824] bg-[#faf8f4] dark:bg-[#1c1b18] overflow-hidden",
          mobileActiveView === "reader" ? "flex" : "hidden lg:flex"
        )}
      >
        {/* Multi-Paper Tab Bar */}
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
          onExportPdf={isRealDocument ? handleExportPdf : undefined}
          isExportingPdf={isExportingPdf}
        />

        {/* Dynamic PDF Canvas Viewport Area */}
        {isRealDocument && activeDocumentId ? (
          <PdfCanvasViewer
            documentId={activeDocumentId}
            documentDetail={documentDetail}
            fileUrl={documentsApi.getDocumentFileUrl(activeDocumentId)}
            currentPage={currentPage}
            zoomRatio={zoomRatio}
            rotationDeg={rotationDeg}
            activeBbox={activeBbox}
            onPageCountDetected={setTotalPages}
            onClearHighlight={() => {
              setActiveBboxStore(null);
              setActiveCitation(null, null);
            }}
            onAddToNote={handleAddToNote}
            onAskChat={(prompt) => {
              setActiveRightTab("chat");
              onChangeText(prompt);
              setMobileActiveView("workspace");
            }}
          />
        ) : (isLoadingDocs || isLoadingDocDetail || Boolean(activeDocumentId) || effectiveDocuments.length > 0) ? (
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
                >
                  <div className="absolute -top-3.5 left-2 px-1.5 py-0.5 rounded bg-[#cc785c] text-white text-[10px] font-mono font-medium tracking-wide flex items-center gap-1 shadow-xs">
                    <span>⚑</span>
                    <span>Dẫn chứng • Tr. {activeBbox[4]}</span>
                  </div>
                </div>
              )}

              {/* Clean Studio Paper Loading State (No Mock Text) */}
              <div className="space-y-6 animate-pulse select-none" data-testid="paper-loading-skeleton">
                <header className="text-center pb-5 border-b border-[#e5e1d8] dark:border-[#353027] space-y-2">
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 dark:bg-primary/20 text-primary text-xs font-medium font-sans">
                    <span className="w-2 h-2 rounded-full bg-primary animate-ping" />
                    <span>Đang nạp tài liệu nghiên cứu...</span>
                  </div>
                  <h2 className="font-serif font-bold text-base sm:text-lg text-[#11100f] dark:text-[#fbf9f5] leading-snug line-clamp-2">
                    {displayTitle}
                  </h2>
                  <p className="text-2xs font-mono text-ink-muted dark:text-zinc-400">
                    Phân tích học thuật bảo chứng tọa độ Bounding Box • Trang {currentPage}
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

      {/* ========================================================================= */}
      {/* 2. RIGHT PANE: SOCRATIC COPILOT, SMART NOTES, SUMMARY & KNOWLEDGE DIGEST */}
      {/* ========================================================================= */}
      <section
        onContextMenu={handleContextMenu}
        className={cn(
          "w-full lg:w-1/2 flex flex-col h-full bg-[#faf9f5] dark:bg-[#181715] overflow-hidden relative",
          mobileActiveView === "workspace" ? "flex" : "hidden lg:flex"
        )}
      >
        {/* Right Pane Navigation Tab Bar */}
        <header className="h-11 px-3 bg-white/70 dark:bg-[#1c1b18]/70 backdrop-blur-sm border-b border-[#e6dfd8] dark:border-[#2a2824] flex items-center justify-between select-none shrink-0 z-10 gap-2">
          {/* 5 Tab Switchers */}
          <nav
            role="tablist"
            aria-label="Các khung tính năng học thuật"
            className="flex items-center gap-1 overflow-x-auto scrollbar-none shrink"
          >
            <button
              type="button"
              role="tab"
              aria-selected={activeRightTab === "chat"}
              onClick={() => setActiveRightTab("chat")}
              className={cn(
                "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium transition-colors cursor-pointer",
                activeRightTab === "chat"
                  ? "bg-surface-cream-strong dark:bg-[#2c2925] text-primary font-semibold shadow-2xs border border-hairline"
                  : "text-muted hover:text-ink hover:bg-surface-soft dark:hover:bg-[#252320]"
              )}
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>Đối thoại</span>
            </button>

            <button
              type="button"
              role="tab"
              aria-selected={activeRightTab === "notes"}
              onClick={() => setActiveRightTab("notes")}
              className={cn(
                "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium transition-colors cursor-pointer",
                activeRightTab === "notes"
                  ? "bg-surface-cream-strong dark:bg-[#2c2925] text-primary font-semibold shadow-2xs border border-hairline"
                  : "text-muted hover:text-ink hover:bg-surface-soft dark:hover:bg-[#252320]"
              )}
            >
              <BookMarked className="w-3.5 h-3.5" />
              <span>Sổ tay</span>
            </button>

            <button
              type="button"
              role="tab"
              aria-selected={activeRightTab === "summary"}
              onClick={() => setActiveRightTab("summary")}
              className={cn(
                "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium transition-colors cursor-pointer",
                activeRightTab === "summary"
                  ? "bg-surface-cream-strong dark:bg-[#2c2925] text-primary font-semibold shadow-2xs border border-hairline"
                  : "text-muted hover:text-ink hover:bg-surface-soft dark:hover:bg-[#252320]"
              )}
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Tóm tắt</span>
            </button>

            <button
              type="button"
              role="tab"
              aria-selected={activeRightTab === "structure"}
              onClick={() => setActiveRightTab("structure")}
              className={cn(
                "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium transition-colors cursor-pointer",
                activeRightTab === "structure"
                  ? "bg-surface-cream-strong dark:bg-[#2c2925] text-primary font-semibold shadow-2xs border border-hairline"
                  : "text-muted hover:text-ink hover:bg-surface-soft dark:hover:bg-[#252320]"
              )}
            >
              <ListTree className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Mục lục</span>
            </button>

            <button
              type="button"
              role="tab"
              aria-selected={activeRightTab === "references"}
              onClick={() => setActiveRightTab("references")}
              className={cn(
                "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium transition-colors cursor-pointer",
                activeRightTab === "references"
                  ? "bg-surface-cream-strong dark:bg-[#2c2925] text-primary font-semibold shadow-2xs border border-hairline"
                  : "text-muted hover:text-ink hover:bg-surface-soft dark:hover:bg-[#252320]"
              )}
            >
              <Quote className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Tham khảo</span>
            </button>
          </nav>

          {/* Right Actions: Xuất ZIP, Cài đặt phiên, Mode Dark/Light, Làm mới hội thoại */}
          <div className="flex items-center gap-1.5 shrink-0">
            {/* Export Bundle Button */}
            <button
              type="button"
              onClick={() => setIsExportOpen(true)}
              aria-label="Xuất gói nghiên cứu ngoại tuyến (.zip)"
              title="Xuất gói nghiên cứu ngoại tuyến (.zip)"
              className="inline-flex items-center gap-1.5 h-7 px-2.5 rounded-lg border border-[#e5dfd4] dark:border-[#38332c] bg-white/80 dark:bg-[#252320] hover:bg-[#f5f1ea] dark:hover:bg-[#2e2b26] text-ink dark:text-zinc-200 transition-colors cursor-pointer text-[11px] font-sans shadow-2xs"
            >
              <Archive className="w-3.5 h-3.5 text-primary" />
              <span className="hidden sm:inline font-medium">Xuất ZIP</span>
            </button>

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

            {/* Right Action: Reset Chat when in chat tab */}
            {activeRightTab === "chat" && (
              <button
                type="button"
                onClick={onResetChat}
                title="Làm mới hội thoại"
                className="p-1.5 rounded-lg hover:bg-[#f0ece3] dark:hover:bg-[#282622] text-ink-muted dark:text-zinc-400 hover:text-ink dark:hover:text-zinc-100 transition-colors cursor-pointer shrink-0"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </header>

        {/* TAB 1: SOCRATIC COPILOT CHAT STREAM */}
        {activeRightTab === "chat" && (
          <>
            <div
              ref={chatScrollRef}
              className="flex-1 overflow-y-auto px-4 sm:px-6 py-5 space-y-6 scrollbar-none"
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
                    <span className="text-[10px] text-ink-muted dark:text-zinc-400 font-mono">
                      Trợ lý phản biện &amp; bảo chứng trích dẫn
                    </span>
                  </div>
                </div>
              </div>

              {/* Grounded 3-Point Summary Card - Primer when chat is fresh */}
              {activeSummary && messages.length === 0 && (
                <div className="animate-in fade-in slide-in-from-top-3 duration-300">
                  <DocumentGroundedSummaryCard summary={activeSummary} paperTitle={displayTitle} />
                </div>
              )}

              {/* Scholarly Welcome & Prompt Starter Chips when no messages */}
              {messages.length === 0 && (
                <div className="py-6 px-2 space-y-4 text-center">
                  <div className="w-12 h-12 rounded-2xl bg-primary/10 text-primary flex items-center justify-center mx-auto shadow-xs border border-primary/20">
                    <Sparkles className="w-6 h-6" />
                  </div>
                  <div className="space-y-1">
                    <h3 className="font-serif font-bold text-base text-ink dark:text-zinc-100">
                      Socratic Academic Copilot
                    </h3>
                    <p className="text-xs text-muted max-w-sm mx-auto leading-relaxed">
                      Trợ lý phản biện học thuật chuyên sâu. Đặt câu hỏi về phương pháp, toán học, đối chứng số liệu hoặc bôi đen văn bản trên PDF để hỏi trực tiếp.
                    </p>
                  </div>

                  <div className="pt-2 text-left space-y-2 max-w-md mx-auto">
                    <div className="text-[11px] font-mono font-medium text-muted uppercase tracking-wider px-1">
                      Gợi ý câu hỏi học thuật:
                    </div>
                    {[
                      {
                        label: "🎯 Bản chất cơ chế Self-Attention",
                        prompt: "Hãy giải thích trực quan cơ chế Scaled Dot-Product Attention và tại sao phải chia cho căn bậc hai của dk?",
                      },
                      {
                        label: "📊 So sánh hiệu năng thực nghiệm",
                        prompt: "Tóm tắt các kết quả thực nghiệm về điểm BLEU trên tập WMT 2014 và chi phí tính toán huấn luyện (training FLOPs).",
                      },
                      {
                        label: "⚠️ Điểm yếu & Hạn chế cốt lõi",
                        prompt: "Những hạn chế và thách thức chính của kiến trúc Transformer khi xử lý chuỗi văn bản cực dài là gì?",
                      },
                    ].map((item, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => onChangeText(item.prompt)}
                        className="w-full text-left p-2.5 rounded-xl border border-hairline/80 dark:border-[#2d2924] bg-white dark:bg-[#1f1d1a] hover:border-primary/50 hover:bg-surface-cream-strong/50 dark:hover:bg-[#25221d] transition-all text-xs text-ink dark:text-zinc-200 group cursor-pointer flex items-center justify-between shadow-2xs"
                      >
                        <span className="font-medium group-hover:text-primary transition-colors">
                          {item.label}
                        </span>
                        <ArrowUpRight className="w-3.5 h-3.5 text-muted group-hover:text-primary shrink-0 transition-colors" />
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
                        {message.is_streaming && (
                          <span className="inline-flex items-center gap-1 text-[#cc785c] animate-pulse">
                            <span className="w-1.5 h-1.5 rounded-full bg-[#cc785c]" />
                            <span>Đang suy luận...</span>
                          </span>
                        )}
                      </div>

                      {/* Collapsible Reasoning */}
                      {message.thought && (
                        <details className="group p-2 rounded-xl bg-[#f4efe6]/80 dark:bg-[#211f1c] border border-[#e5dfd4] dark:border-[#332f28] text-2xs font-mono text-ink-muted dark:text-zinc-400">
                          <summary className="cursor-pointer font-medium select-none flex items-center gap-1.5 text-ink dark:text-zinc-300 hover:text-[#cc785c] transition-colors">
                            <BrainCircuit className="w-3.5 h-3.5 text-[#cc785c]" />
                            <span>Suy luận bảo chứng</span>
                          </summary>
                          <div className="mt-2 pt-2 border-t border-hairline/60 dark:border-zinc-800 text-3xs font-mono leading-relaxed whitespace-pre-wrap">
                            {message.thought}
                          </div>
                        </details>
                      )}

                      {/* Presupposition Alert */}
                      {message.presupposition_alert && (
                        <PresuppositionBanner alert={message.presupposition_alert} />
                      )}

                      {/* Formatted Assistant Body */}
                      <FormattedAssistantMessage content={message.content} />

                      {/* Interactive Citations */}
                      {message.citations && message.citations.length > 0 && (
                        <div className="pt-1.5 flex flex-wrap items-center gap-1.5">
                          {message.citations.map((cite, cIdx) => (
                            <CitationBadge key={cIdx} citation={cite} />
                          ))}
                        </div>
                      )}

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
            <div className="shrink-0 pb-4 pt-2 px-3 bg-gradient-to-t from-[#faf9f5] via-[#faf9f5]/90 to-transparent dark:from-[#181715] dark:via-[#181715]/90 z-10">
              {isGenerating && (
                <div className="flex justify-center mb-2">
                  <button
                    type="button"
                    onClick={onStopGeneration}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white dark:bg-[#252320] border border-[#e5dfd4] dark:border-zinc-700/60 text-ink dark:text-zinc-200 text-xs font-sans shadow-xs hover:bg-[#f4efe6] dark:hover:bg-[#2e2a25] transition-colors cursor-pointer"
                  >
                    <Square className="w-3 h-3 fill-current text-[#cc785c]" />
                    <span>Dừng suy luận</span>
                  </button>
                </div>
              )}

              <DashboardChatInputBox
                inputText={inputText}
                onChangeText={onChangeText}
                onSend={onSend}
                isGenerating={isGenerating}
                onUploadFile={onUploadFile}
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

      {/* Export Bundle Dialog */}
      {effectiveSessionId && (
        <ExportBundleDialog
          isOpen={isExportOpen}
          onClose={() => setIsExportOpen(false)}
          sessionId={effectiveSessionId}
          sessionTitle={sessionTitle || currentDocTitle || "Phiên nghiên cứu"}
          onExport={handleExportBundle}
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
              setIsExportOpen(true);
              setContextMenu((prev) => ({ ...prev, isOpen: false }));
            }}
            className="w-full flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-left text-xs hover:bg-[#f3eee5] dark:hover:bg-[#2d2924] hover:text-primary transition-colors cursor-pointer"
          >
            <Archive className="w-3.5 h-3.5 text-primary" />
            <span>Xuất gói nghiên cứu (.zip)</span>
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
    </div>
  );
}
