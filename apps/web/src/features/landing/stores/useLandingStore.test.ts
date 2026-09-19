import { describe, it, expect, beforeEach } from "vitest";
import { useLandingStore } from "./useLandingStore";
import { MOCK_DEMO_PAPERS } from "../data/mock-papers";

describe("useLandingStore", () => {
  beforeEach(() => {
    useLandingStore.getState().setActivePaperId("demo-paper-attention");
    useLandingStore.getState().setUploadModalOpen(false);
    useLandingStore.getState().setMobileMenuOpen(false);
  });

  it("initializes with default attention paper and first citation", () => {
    const state = useLandingStore.getState();
    expect(state.activePaperId).toBe("demo-paper-attention");
    expect(state.activeCitation).not.toBeNull();
    expect(state.isUploadModalOpen).toBe(false);
  });

  it("switches paper and synchronizes active turn and citation", () => {
    useLandingStore.getState().setActivePaperId("demo-paper-resnet");
    const state = useLandingStore.getState();

    expect(state.activePaperId).toBe("demo-paper-resnet");
    const resnetPaper = MOCK_DEMO_PAPERS.find((p) => p.id === "demo-paper-resnet");
    expect(state.activeTurnId).toBe(resnetPaper?.sample_turns[0]?.id);
    expect(state.activeCitation?.paper_title).toBe("Deep Residual Learning for Image Recognition");
  });

  it("toggles upload modal correctly", () => {
    useLandingStore.getState().setUploadModalOpen(true);
    expect(useLandingStore.getState().isUploadModalOpen).toBe(true);

    useLandingStore.getState().setUploadModalOpen(false);
    expect(useLandingStore.getState().isUploadModalOpen).toBe(false);
  });

  it("updates active citation when selected", () => {
    const testCitation = {
      id: "custom-cite-1",
      label: "Custom Author • Tr. 1",
      paper_title: "Custom Paper",
      page: 1,
      bounding_box: [0.1, 0.1, 0.5, 0.5, 1] as [number, number, number, number, number],
      quote_text: "Test quote",
      fact_check_status: "supported" as const,
    };

    useLandingStore.getState().setActiveCitation(testCitation);
    expect(useLandingStore.getState().activeCitationId).toBe("custom-cite-1");
    expect(useLandingStore.getState().activeCitation?.quote_text).toBe("Test quote");
  });
});
