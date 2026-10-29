import { create } from "zustand";
import type { BoundingBox } from "@/types/api";

export type ReadingMode = "continuous" | "single" | "two-page";
export type ReaderColorTheme = "default" | "dark" | "sepia" | "contrast";
export type FitMode = "custom" | "width" | "page";

export interface ReaderState {
  activeDocumentId: string | null;
  openDocumentIds: string[];
  zoomRatio: number;
  currentPage: number;
  totalPages: number;
  rotationDeg: 0 | 90 | 180 | 270;
  activeCitationId: string | null;
  activeBbox: BoundingBox | null;
  activeBboxes: BoundingBox[] | null;
  readingMode: ReadingMode;
  colorTheme: ReaderColorTheme;
  fitMode: FitMode;
  isThumbnailsOpen: boolean;

  // Actions
  setActiveDocumentId: (id: string | null) => void;
  setOpenDocumentIds: (ids: string[]) => void;
  addOpenDocument: (id: string) => void;
  removeOpenDocument: (id: string) => void;
  setZoomRatio: (zoom: number) => void;
  zoomIn: () => void;
  zoomOut: () => void;
  resetZoom: () => void;
  setCurrentPage: (page: number) => void;
  setTotalPages: (total: number) => void;
  nextPage: () => void;
  prevPage: () => void;
  setRotationDeg: (deg: 0 | 90 | 180 | 270) => void;
  rotateClockwise: () => void;
  setActiveCitation: (
    citationId: string | null,
    bbox: BoundingBox | null,
    page?: number,
    bboxes?: BoundingBox[] | null
  ) => void;
  setReadingMode: (mode: ReadingMode) => void;
  setColorTheme: (theme: ReaderColorTheme) => void;
  setFitMode: (mode: FitMode) => void;
  toggleFitWidth: () => void;
  toggleThumbnails: () => void;
  setIsThumbnailsOpen: (open: boolean) => void;
  resetReader: () => void;
}

export const useReaderStore = create<ReaderState>((set, get) => ({
  activeDocumentId: null,
  openDocumentIds: [],
  zoomRatio: 1.0,
  currentPage: 1,
  totalPages: 1,
  rotationDeg: 0,
  activeCitationId: null,
  activeBbox: null,
  activeBboxes: null,
  readingMode: "continuous",
  colorTheme: "default",
  fitMode: "width",
  isThumbnailsOpen: false,

  setActiveDocumentId: (id) =>
    set((state) => {
      if (!id) return { activeDocumentId: null };
      if (state.activeDocumentId === id) return {};
      const exists = state.openDocumentIds.includes(id);
      return {
        activeDocumentId: id,
        openDocumentIds: exists ? state.openDocumentIds : [...state.openDocumentIds, id].slice(0, 5),
        currentPage: 1,
        activeCitationId: null,
        activeBbox: null,
        activeBboxes: null,
      };
    }),

  setOpenDocumentIds: (ids) =>
    set({
      openDocumentIds: ids.slice(0, 5),
      activeDocumentId: ids[0] ?? null,
    }),

  addOpenDocument: (id) =>
    set((state) => {
      if (state.openDocumentIds.includes(id)) {
        return { activeDocumentId: id };
      }
      if (state.openDocumentIds.length >= 5) {
        // Enforce strict 5-document cap without silent eviction
        return {};
      }
      return {
        openDocumentIds: [...state.openDocumentIds, id],
        activeDocumentId: id,
      };
    }),

  removeOpenDocument: (id) =>
    set((state) => {
      const remaining = state.openDocumentIds.filter((docId) => docId !== id);
      const nextActive = state.activeDocumentId === id ? remaining[0] ?? null : state.activeDocumentId;
      return {
        openDocumentIds: remaining,
        activeDocumentId: nextActive,
      };
    }),

  setZoomRatio: (zoom) =>
    set({ zoomRatio: Math.min(3.0, Math.max(0.5, Number(zoom.toFixed(2)))) }),

  zoomIn: () =>
    set((state) => ({
      zoomRatio: Math.min(3.0, Number((state.zoomRatio + 0.05).toFixed(2))),
      fitMode: "custom",
    })),

  zoomOut: () =>
    set((state) => ({
      zoomRatio: Math.max(0.5, Number((state.zoomRatio - 0.05).toFixed(2))),
      fitMode: "custom",
    })),

  resetZoom: () => set({ zoomRatio: 1.0, fitMode: "width" }),

  setCurrentPage: (page) =>
    set((state) => ({
      currentPage:
        state.totalPages > 1
          ? Math.max(1, Math.min(state.totalPages, page))
          : Math.max(1, page),
    })),

  setTotalPages: (total) =>
    set({
      totalPages: Math.max(1, total),
    }),

  nextPage: () => {
    const { currentPage, totalPages } = get();
    if (currentPage < totalPages) {
      set({ currentPage: currentPage + 1 });
    }
  },

  prevPage: () => {
    const { currentPage } = get();
    if (currentPage > 1) {
      set({ currentPage: currentPage - 1 });
    }
  },

  setRotationDeg: (deg) => set({ rotationDeg: deg }),

  rotateClockwise: () =>
    set((state) => {
      const nextDeg = ((state.rotationDeg + 90) % 360) as 0 | 90 | 180 | 270;
      return { rotationDeg: nextDeg };
    }),

  setActiveCitation: (citationId, bbox, page, bboxes) =>
    set((state) => {
      const primaryBox = bbox ?? (bboxes && bboxes.length > 0 ? bboxes[0] : null);
      return {
        activeCitationId: citationId,
        activeBbox: primaryBox,
        activeBboxes: primaryBox ? [primaryBox] : null,
        currentPage: page !== undefined ? page : primaryBox ? primaryBox[4] : state.currentPage,
      };
    }),

  setReadingMode: (mode) => set({ readingMode: mode }),
  setColorTheme: (theme) => set({ colorTheme: theme }),
  setFitMode: (mode) => set({ fitMode: mode }),
  toggleFitWidth: () =>
    set((s) => ({
      fitMode: s.fitMode === "width" ? "custom" : "width",
      ...(s.fitMode !== "width" ? { zoomRatio: 1.0 } : {}),
    })),
  toggleThumbnails: () => set((s) => ({ isThumbnailsOpen: !s.isThumbnailsOpen })),
  setIsThumbnailsOpen: (open) => set({ isThumbnailsOpen: open }),

  resetReader: () =>
    set({
      activeDocumentId: null,
      openDocumentIds: [],
      zoomRatio: 1.0,
      currentPage: 1,
      totalPages: 1,
      rotationDeg: 0,
      activeCitationId: null,
      activeBbox: null,
      activeBboxes: null,
      readingMode: "continuous",
      colorTheme: "default",
      fitMode: "width",
      isThumbnailsOpen: false,
    }),
}));
