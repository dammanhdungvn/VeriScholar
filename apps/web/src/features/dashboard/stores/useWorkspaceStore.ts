import { create } from "zustand";
import type { BoundingBox } from "@/types/api";

export type IngestionDocumentStatus =
  | "idle"
  | "uploading"
  | "validating"
  | "parsing"
  | "completed"
  | "error";

export type WorkspaceRightTab = "chat" | "notes" | "summary" | "structure" | "references";

export type ZenMode = "none" | "pdf" | "workspace";

export interface ActiveContextChip {
  text: string;
  pageNumber: number;
  bbox?: BoundingBox | null;
  documentTitle?: string;
  documentId?: string | null;
}

export interface WorkspaceState {
  // Trạng thái phiên
  activeSessionId: string | null;
  isStandby: boolean;

  // Trạng thái tài liệu
  activeDocumentId: string | null;
  documentTitle: string | null;
  documentStatus: IngestionDocumentStatus;
  uploadProgress: number;
  statusStage: string | null;
  errorMessage: string | null;

  // Trạng thái tab điều khiển bên phải
  activeRightTab: WorkspaceRightTab;

  // Module 1 Deep Reader Workspace Layout & Focus Modes
  splitRatio: number; // 20 - 80, default 50
  zenMode: ZenMode;
  activeContextChip: ActiveContextChip | null;

  // Actions
  initNewStandbyChat: () => void;
  setSession: (sessionId: string | null) => void;
  setDocument: (documentId: string | null, title?: string | null) => void;
  setStatus: (
    status: IngestionDocumentStatus,
    progress: number,
    stage?: string | null
  ) => void;
  setError: (message: string | null) => void;
  setActiveRightTab: (tab: WorkspaceRightTab) => void;
  setSplitRatio: (ratio: number) => void;
  setZenMode: (mode: ZenMode) => void;
  setActiveContextChip: (chip: ActiveContextChip | null) => void;
  resetWorkspace: () => void;
}

const initialState = {
  activeSessionId: null,
  isStandby: true,
  activeDocumentId: null,
  documentTitle: null,
  documentStatus: "idle" as IngestionDocumentStatus,
  uploadProgress: 0,
  statusStage: null,
  errorMessage: null,
  activeRightTab: "chat" as WorkspaceRightTab,
  splitRatio: 50,
  zenMode: "none" as ZenMode,
  activeContextChip: null as ActiveContextChip | null,
};

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  ...initialState,

  initNewStandbyChat: () =>
    set({
      ...initialState,
    }),

  setSession: (activeSessionId) => set({ activeSessionId }),

  setDocument: (activeDocumentId, documentTitle = null) =>
    set({ activeDocumentId, documentTitle }),

  setStatus: (documentStatus, uploadProgress, statusStage = null) =>
    set((state) => ({
      documentStatus,
      uploadProgress,
      statusStage: statusStage ?? state.statusStage,
      isStandby: documentStatus === "completed" ? false : state.isStandby,
    })),

  setError: (errorMessage) =>
    set({
      documentStatus: "error",
      errorMessage,
    }),

  setActiveRightTab: (activeRightTab) => set({ activeRightTab }),

  setSplitRatio: (splitRatio) =>
    set({ splitRatio: Math.max(20, Math.min(80, Math.round(splitRatio * 10) / 10)) }),

  setZenMode: (zenMode) => set({ zenMode }),

  setActiveContextChip: (activeContextChip) => set({ activeContextChip }),

  resetWorkspace: () =>
    set({
      ...initialState,
    }),
}));

if (typeof window !== "undefined") {
  (window as unknown as { __workspaceStore: typeof useWorkspaceStore }).__workspaceStore =
    useWorkspaceStore;
}
