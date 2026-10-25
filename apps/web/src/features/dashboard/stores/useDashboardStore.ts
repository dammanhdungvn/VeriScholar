import { create } from "zustand";
import type { SidebarState, AppMode, BoundingBox } from "@/types/dashboard";

interface DashboardState {
  sidebarState: SidebarState;
  appMode: AppMode;
  activeSessionId?: string;
  activeBbox: BoundingBox | null;
  isUploadModalOpen: boolean;
  isVoiceModalOpen: boolean;
  isReasoningEnabled: boolean;

  // Actions
  toggleReasoning: () => void;
  setReasoningEnabled: (enabled: boolean) => void;
  toggleSidebar: () => void;
  setSidebarState: (state: SidebarState) => void;
  setAppMode: (mode: AppMode) => void;
  setActiveSessionId: (id?: string) => void;
  setActiveBbox: (bbox: BoundingBox | null) => void;
  setUploadModalOpen: (open: boolean) => void;
  setVoiceModalOpen: (open: boolean) => void;
  reset: () => void;
}

export const TASKBAR_STATE_STORAGE_KEY = "verischolar_taskbar_state";

export function getStoredSidebarState(): SidebarState {
  if (typeof window === "undefined") {
    return "collapsed";
  }
  try {
    const saved = localStorage.getItem(TASKBAR_STATE_STORAGE_KEY);
    if (saved === "expanded" || saved === "collapsed") {
      return saved;
    }
  } catch {
    // Ignore storage read issues in test/private browsing
  }
  return "collapsed";
}

function persistSidebarState(state: SidebarState) {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(TASKBAR_STATE_STORAGE_KEY, state);
  } catch {
    // Ignore storage write issues
  }
}

export const useDashboardStore = create<DashboardState>((set) => ({
  sidebarState: getStoredSidebarState(),
  appMode: "chat",
  activeSessionId: undefined,
  activeBbox: null,
  isUploadModalOpen: false,
  isVoiceModalOpen: false,
  isReasoningEnabled: true,

  toggleReasoning: () =>
    set((state) => ({ isReasoningEnabled: !state.isReasoningEnabled })),

  setReasoningEnabled: (isReasoningEnabled) => set({ isReasoningEnabled }),

  toggleSidebar: () =>
    set((state) => {
      const nextState: SidebarState = state.sidebarState === "collapsed" ? "expanded" : "collapsed";
      persistSidebarState(nextState);
      return { sidebarState: nextState };
    }),

  setSidebarState: (sidebarState) => {
    persistSidebarState(sidebarState);
    set({ sidebarState });
  },
  setAppMode: (appMode) => set({ appMode }),
  setActiveSessionId: (activeSessionId) => set({ activeSessionId }),
  setActiveBbox: (activeBbox) => set({ activeBbox }),
  setUploadModalOpen: (isUploadModalOpen) => set({ isUploadModalOpen }),
  setVoiceModalOpen: (isVoiceModalOpen) => set({ isVoiceModalOpen }),

  reset: () =>
    set({
      sidebarState: getStoredSidebarState(),
      appMode: "chat",
      activeSessionId: undefined,
      activeBbox: null,
      isUploadModalOpen: false,
      isVoiceModalOpen: false,
      isReasoningEnabled: true,
    })
}));

if (typeof window !== "undefined") {
  (window as unknown as { __dashboardStore: typeof useDashboardStore }).__dashboardStore = useDashboardStore;
}
