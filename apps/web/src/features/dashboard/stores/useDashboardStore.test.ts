import { describe, it, expect, beforeEach } from "vitest";
import { useDashboardStore } from "./useDashboardStore";
import { AVAILABLE_MODELS } from "../data/mockDashboardData";

describe("useDashboardStore", () => {
  beforeEach(() => {
    useDashboardStore.getState().reset();
  });

  it("initializes with collapsed sidebar and chat mode", () => {
    const state = useDashboardStore.getState();
    expect(state.sidebarState).toBe("collapsed");
    expect(state.appMode).toBe("chat");
    expect(state.selectedModel.id).toBe(AVAILABLE_MODELS[0].id);
    expect(state.effortLevel).toBe("Cao");
    expect(state.activeSessionId).toBeUndefined();
    expect(state.activeBbox).toBeNull();
  });

  it("toggles sidebar between collapsed and expanded", () => {
    const store = useDashboardStore.getState();
    store.toggleSidebar();
    expect(useDashboardStore.getState().sidebarState).toBe("expanded");

    store.toggleSidebar();
    expect(useDashboardStore.getState().sidebarState).toBe("collapsed");
  });

  it("switches appMode between chat and cowork", () => {
    useDashboardStore.getState().setAppMode("cowork");
    expect(useDashboardStore.getState().appMode).toBe("cowork");

    useDashboardStore.getState().setAppMode("chat");
    expect(useDashboardStore.getState().appMode).toBe("chat");
  });

  it("updates selectedModel and effortLevel", () => {
    const secondModel = AVAILABLE_MODELS[1];
    useDashboardStore.getState().setSelectedModel(secondModel);
    useDashboardStore.getState().setEffortLevel("Tiêu chuẩn");

    expect(useDashboardStore.getState().selectedModel.id).toBe(secondModel.id);
    expect(useDashboardStore.getState().effortLevel).toBe("Tiêu chuẩn");
  });

  it("sets active bbox coordinates", () => {
    const bbox: [number, number, number, number, number] = [0.1, 0.2, 0.3, 0.4, 1];
    useDashboardStore.getState().setActiveBbox(bbox);
    expect(useDashboardStore.getState().activeBbox).toEqual(bbox);

    useDashboardStore.getState().setActiveBbox(null);
    expect(useDashboardStore.getState().activeBbox).toBeNull();
  });

  it("toggles modal states", () => {
    useDashboardStore.getState().setModelModalOpen(true);
    expect(useDashboardStore.getState().isModelModalOpen).toBe(true);

    useDashboardStore.getState().setUploadModalOpen(true);
    expect(useDashboardStore.getState().isUploadModalOpen).toBe(true);

    useDashboardStore.getState().setVoiceModalOpen(true);
    expect(useDashboardStore.getState().isVoiceModalOpen).toBe(true);
  });
});
