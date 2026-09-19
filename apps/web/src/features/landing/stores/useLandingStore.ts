import { create } from "zustand";
import type { DemoCitation } from "@/types/landing";
import { MOCK_DEMO_PAPERS } from "../data/mock-papers";

interface LandingState {
  activePaperId: string;
  activeTurnId: string;
  activeCitationId: string | null;
  activeCitation: DemoCitation | null;
  isUploadModalOpen: boolean;
  isVideoModalOpen: boolean;
  isMobileMenuOpen: boolean;

  // Actions
  setActivePaperId: (paperId: string) => void;
  setActiveTurnId: (turnId: string) => void;
  setActiveCitation: (citation: DemoCitation | null) => void;
  setUploadModalOpen: (open: boolean) => void;
  setVideoModalOpen: (open: boolean) => void;
  setMobileMenuOpen: (open: boolean) => void;
}

export const useLandingStore = create<LandingState>((set) => ({
  activePaperId: "demo-paper-attention",
  activeTurnId: "turn-1",
  activeCitationId: "cite-pos-enc",
  activeCitation: MOCK_DEMO_PAPERS[0]?.sample_turns[0]?.citations[0] ?? null,
  isUploadModalOpen: false,
  isVideoModalOpen: false,
  isMobileMenuOpen: false,

  setActivePaperId: (paperId) => {
    const paper = MOCK_DEMO_PAPERS.find((p) => p.id === paperId);
    const firstTurn = paper?.sample_turns[0];
    const firstCitation = firstTurn?.citations[0] ?? null;

    set({
      activePaperId: paperId,
      activeTurnId: firstTurn?.id ?? "",
      activeCitationId: firstCitation?.id ?? null,
      activeCitation: firstCitation,
    });
  },

  setActiveTurnId: (turnId) => {
    set((state) => {
      const paper = MOCK_DEMO_PAPERS.find((p) => p.id === state.activePaperId);
      const turn = paper?.sample_turns.find((t) => t.id === turnId);
      const firstCitation = turn?.citations[0] ?? null;

      return {
        activeTurnId: turnId,
        activeCitationId: firstCitation?.id ?? null,
        activeCitation: firstCitation,
      };
    });
  },

  setActiveCitation: (citation) =>
    set({
      activeCitationId: citation?.id ?? null,
      activeCitation: citation,
    }),

  setUploadModalOpen: (open) => set({ isUploadModalOpen: open }),
  setVideoModalOpen: (open) => set({ isVideoModalOpen: open }),
  setMobileMenuOpen: (open) => set({ isMobileMenuOpen: open }),
}));
