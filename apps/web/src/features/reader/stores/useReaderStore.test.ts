import { describe, it, expect, beforeEach } from "vitest";
import { useReaderStore } from "./useReaderStore";

describe("useReaderStore", () => {
  beforeEach(() => {
    useReaderStore.getState().resetReader();
  });

  it("initializes with default reader state", () => {
    const state = useReaderStore.getState();
    expect(state.activeDocumentId).toBeNull();
    expect(state.openDocumentIds).toEqual([]);
    expect(state.zoomRatio).toBe(1.0);
    expect(state.currentPage).toBe(1);
    expect(state.totalPages).toBe(1);
    expect(state.rotationDeg).toBe(0);
    expect(state.activeCitationId).toBeNull();
    expect(state.activeBbox).toBeNull();
  });

  it("handles adding and removing open documents (max 5 without silent eviction)", () => {
    useReaderStore.getState().addOpenDocument("doc-1");
    useReaderStore.getState().addOpenDocument("doc-2");
    useReaderStore.getState().addOpenDocument("doc-3");
    useReaderStore.getState().addOpenDocument("doc-4");
    useReaderStore.getState().addOpenDocument("doc-5");
    useReaderStore.getState().addOpenDocument("doc-6");

    const state = useReaderStore.getState();
    expect(state.openDocumentIds).toHaveLength(5);
    expect(state.openDocumentIds).toEqual(["doc-1", "doc-2", "doc-3", "doc-4", "doc-5"]);
    expect(state.openDocumentIds).not.toContain("doc-6");
    expect(state.activeDocumentId).toBe("doc-5");

    useReaderStore.getState().removeOpenDocument("doc-5");
    expect(useReaderStore.getState().openDocumentIds).toHaveLength(4);
    expect(useReaderStore.getState().activeDocumentId).toBe("doc-1");
  });

  it("manages zoom in/out within bounds 0.5 to 3.0", () => {
    useReaderStore.getState().setZoomRatio(0.5);
    useReaderStore.getState().zoomOut();
    expect(useReaderStore.getState().zoomRatio).toBe(0.5);

    useReaderStore.getState().setZoomRatio(3.0);
    useReaderStore.getState().zoomIn();
    expect(useReaderStore.getState().zoomRatio).toBe(3.0);

    useReaderStore.getState().resetZoom();
    expect(useReaderStore.getState().zoomRatio).toBe(1.0);

    useReaderStore.getState().zoomIn();
    expect(useReaderStore.getState().zoomRatio).toBe(1.05);

    useReaderStore.getState().zoomOut();
    expect(useReaderStore.getState().zoomRatio).toBe(1.0);

    useReaderStore.getState().zoomOut();
    expect(useReaderStore.getState().zoomRatio).toBe(0.95);
  });

  it("manages page rotation clockwise in 90 degree increments", () => {
    expect(useReaderStore.getState().rotationDeg).toBe(0);
    useReaderStore.getState().rotateClockwise();
    expect(useReaderStore.getState().rotationDeg).toBe(90);
    useReaderStore.getState().rotateClockwise();
    expect(useReaderStore.getState().rotationDeg).toBe(180);
    useReaderStore.getState().rotateClockwise();
    expect(useReaderStore.getState().rotationDeg).toBe(270);
    useReaderStore.getState().rotateClockwise();
    expect(useReaderStore.getState().rotationDeg).toBe(0);
  });

  it("sets active citation and jumps to target page", () => {
    useReaderStore.getState().setTotalPages(10);
    useReaderStore.getState().setActiveCitation("cit-42", [0.1, 0.2, 0.8, 0.4, 5], 5);

    const state = useReaderStore.getState();
    expect(state.activeCitationId).toBe("cit-42");
    expect(state.activeBbox).toEqual([0.1, 0.2, 0.8, 0.4, 5]);
    expect(state.currentPage).toBe(5);
  });

  it("manages fitMode (default width), toggleFitWidth, and resets to width", () => {
    expect(useReaderStore.getState().fitMode).toBe("width");

    // Zooming in sets fitMode to custom
    useReaderStore.getState().zoomIn();
    expect(useReaderStore.getState().fitMode).toBe("custom");

    // Toggling returns to width
    useReaderStore.getState().toggleFitWidth();
    expect(useReaderStore.getState().fitMode).toBe("width");
    expect(useReaderStore.getState().zoomRatio).toBe(1.0);

    // Toggling again switches back to custom
    useReaderStore.getState().toggleFitWidth();
    expect(useReaderStore.getState().fitMode).toBe("custom");

    // Explicit setFitMode
    useReaderStore.getState().setFitMode("width");
    expect(useReaderStore.getState().fitMode).toBe("width");

    // resetReader restores fitMode to width
    useReaderStore.getState().setFitMode("custom");
    useReaderStore.getState().resetReader();
    expect(useReaderStore.getState().fitMode).toBe("width");
  });
});
