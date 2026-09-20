import { create } from "zustand";
import type { SidebarState, AppMode, ModelOption, BoundingBox } from "@/types/dashboard";
import { AVAILABLE_MODELS } from "../data/mockDashboardData";

interface DashboardState {
  sidebarState: SidebarState;
  appMode: AppMode;
  selectedModel: ModelOption;
  effortLevel: string;
  activeSessionId?: string;
  activeBbox: BoundingBox | null;
  isModelModalOpen: boolean;
  isUploadModalOpen: boolean;
  isVoiceModalOpen: boolean;

  // Actions
  toggleSidebar: () => void;
  setSidebarState: (state: SidebarState) => void;
  setAppMode: (mode: AppMode) => void;
  setSelectedModel: (model: ModelOption) => void;
  setEffortLevel: (level: string) => void;
  setActiveSessionId: (id?: string) => void;
  setActiveBbox: (bbox: BoundingBox | null) => void;
  setModelModalOpen: (open: boolean) => void;
  setUploadModalOpen: (open: boolean) => void;
  setVoiceModalOpen: (open: boolean) => void;
  reset: () => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  sidebarState: "collapsed",
  appMode: "chat",
  selectedModel: AVAILABLE_MODELS[0],
  effortLevel: "Cao",
  activeSessionId: undefined,
  activeBbox: null,
  isModelModalOpen: false,
  isUploadModalOpen: false,
  isVoiceModalOpen: false,

  toggleSidebar: () =>
    set((state) => ({
      sidebarState: state.sidebarState === "collapsed" ? "expanded" : "collapsed"
    })),

  setSidebarState: (sidebarState) => set({ sidebarState }),
  setAppMode: (appMode) => set({ appMode }),
  setSelectedModel: (selectedModel) => set({ selectedModel }),
  setEffortLevel: (effortLevel) => set({ effortLevel }),
  setActiveSessionId: (activeSessionId) => set({ activeSessionId }),
  setActiveBbox: (activeBbox) => set({ activeBbox }),
  setModelModalOpen: (isModelModalOpen) => set({ isModelModalOpen }),
  setUploadModalOpen: (isUploadModalOpen) => set({ isUploadModalOpen }),
  setVoiceModalOpen: (isVoiceModalOpen) => set({ isVoiceModalOpen }),

  reset: () =>
    set({
      sidebarState: "collapsed",
      appMode: "chat",
      selectedModel: AVAILABLE_MODELS[0],
      effortLevel: "Cao",
      activeSessionId: undefined,
      activeBbox: null,
      isModelModalOpen: false,
      isUploadModalOpen: false,
      isVoiceModalOpen: false
    })
}));

if (typeof window !== "undefined") {
  (window as unknown as { __dashboardStore: typeof useDashboardStore }).__dashboardStore = useDashboardStore;
}
