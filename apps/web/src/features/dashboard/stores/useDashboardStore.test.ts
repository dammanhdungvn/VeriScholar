import { describe, it, expect, beforeEach } from "vitest";
import { useDashboardStore } from "./useDashboardStore";

describe("useDashboardStore", () => {
  beforeEach(() => {
    localStorage.clear();
    useDashboardStore.getState().reset();
  });

  it("initializes with collapsed sidebar and chat mode", () => {
    const state = useDashboardStore.getState();
    expect(state.sidebarState).toBe("collapsed");
    expect(state.appMode).toBe("chat");
    expect(state.activeSessionId).toBeUndefined();
    expect(state.activeBbox).toBeNull();
  });

  it("persists sidebarState to localStorage key verischolar_taskbar_state", () => {
    const store = useDashboardStore.getState();
    store.setSidebarState("expanded");
    expect(localStorage.getItem("verischolar_taskbar_state")).toBe("expanded");
    expect(useDashboardStore.getState().sidebarState).toBe("expanded");

    store.toggleSidebar();
    expect(localStorage.getItem("verischolar_taskbar_state")).toBe("collapsed");
    expect(useDashboardStore.getState().sidebarState).toBe("collapsed");

    // Simulating page refresh by calling reset() with localStorage pre-populated
    localStorage.setItem("verischolar_taskbar_state", "expanded");
    useDashboardStore.getState().reset();
    expect(useDashboardStore.getState().sidebarState).toBe("expanded");
  });

  it("toggles sidebar between collapsed and expanded", () => {
    const store = useDashboardStore.getState();
    store.toggleSidebar();
    expect(useDashboardStore.getState().sidebarState).toBe("expanded");

    store.toggleSidebar();
    expect(useDashboardStore.getState().sidebarState).toBe("collapsed");
  });

  it("switches appMode between chat and library", () => {
    useDashboardStore.getState().setAppMode("library");
    expect(useDashboardStore.getState().appMode).toBe("library");

    useDashboardStore.getState().setAppMode("chat");
    expect(useDashboardStore.getState().appMode).toBe("chat");
  });

  it("sets active bbox coordinates", () => {
    const bbox: [number, number, number, number, number] = [0.1, 0.2, 0.3, 0.4, 1];
    useDashboardStore.getState().setActiveBbox(bbox);
    expect(useDashboardStore.getState().activeBbox).toEqual(bbox);

    useDashboardStore.getState().setActiveBbox(null);
    expect(useDashboardStore.getState().activeBbox).toBeNull();
  });

  it("toggles modal states", () => {
    useDashboardStore.getState().setUploadModalOpen(true);
    expect(useDashboardStore.getState().isUploadModalOpen).toBe(true);

    useDashboardStore.getState().setVoiceModalOpen(true);
    expect(useDashboardStore.getState().isVoiceModalOpen).toBe(true);
  });
});
