import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { WritingPreviewPane } from "./WritingPreviewPane";
import { useWritingStore } from "../stores/useWritingStore";

// Mock draftsApi
vi.mock("../api/draftsApi", () => ({
  draftsApi: {
    getPreviewPdfBlob: vi.fn().mockResolvedValue(new Blob(["mock-pdf"], { type: "application/pdf" })),
    getPreviewPdfUrl: vi.fn((id: string) => `http://localhost:8000/api/v1/drafts/${id}/preview.pdf`),
  },
}));

describe("WritingPreviewPane", () => {
  beforeEach(() => {
    useWritingStore.getState().reset();
  });

  it("does not render any bounding box overlay or citation badge on the draft PDF preview", async () => {
    // Populate store with activeBoundingBoxes and draft
    useWritingStore.getState().setDraft({
      id: "draft-xyz",
      user_id: "user-1",
      title: "Test Draft",
      content: "\\begin{document}Content\\end{document}",
      format: "latex",
      version: 1,
      created_at: "2026-10-15T00:00:00Z",
      updated_at: "2026-10-15T00:00:00Z",
    });
    useWritingStore.getState().setActiveBoundingBoxes([[0.1, 0.2, 0.8, 0.4, 1]], 1);
    useWritingStore.getState().setPreviewPdfBlobUrl("blob:http://localhost:5173/mock-preview");

    render(<WritingPreviewPane />);

    // Header title
    expect(screen.getByText("Bản Dựng PDF Trực Tiếp")).toBeInTheDocument();

    // Verify evidence badge is NOT present
    expect(screen.queryByText(/dẫn chứng/i)).toBeNull();

    // Verify bounding box overlay container is NOT present
    expect(screen.queryByLabelText("Khung trích dẫn bằng chứng")).toBeNull();
    expect(screen.queryByText(/Dẫn chứng #1/i)).toBeNull();
  });

  it("renders zoom controls and handles zoom in, zoom out, and reset buttons", async () => {
    useWritingStore.getState().setDraft({
      id: "draft-xyz",
      user_id: "user-1",
      title: "Test Draft",
      content: "Content",
      format: "latex",
      version: 1,
      created_at: "2026-10-15T00:00:00Z",
      updated_at: "2026-10-15T00:00:00Z",
    });
    render(<WritingPreviewPane />);

    const zoomInBtn = screen.getByTitle("Phóng to");
    const zoomOutBtn = screen.getByTitle("Thu nhỏ");
    const resetZoomBtn = screen.getByTitle("Đặt lại 100%");

    expect(zoomInBtn).toBeInTheDocument();
    expect(zoomOutBtn).toBeInTheDocument();
    expect(resetZoomBtn).toBeInTheDocument();
    expect(screen.getByText("100%")).toBeInTheDocument();

    // Zoom in: 100% -> 115%
    fireEvent.click(zoomInBtn);
    expect(screen.getByText("115%")).toBeInTheDocument();

    // Zoom out twice: 115% -> 100% -> 85%
    fireEvent.click(zoomOutBtn);
    expect(screen.getByText("100%")).toBeInTheDocument();
    fireEvent.click(zoomOutBtn);
    expect(screen.getByText("85%")).toBeInTheDocument();

    // Reset: 85% -> 100%
    fireEvent.click(resetZoomBtn);
    expect(screen.getByText("100%")).toBeInTheDocument();
  });

  it("displays sandbox compilation spinner when isCompiling is true", () => {
    useWritingStore.getState().setCompiling(true);
    render(<WritingPreviewPane />);

    expect(screen.getByText(/Đang biên dịch bản thảo trong sandbox/i)).toBeInTheDocument();
  });
});
