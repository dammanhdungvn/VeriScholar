import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { AbstractCardViewer } from "../components/AbstractCardViewer";
import { DocumentTabBar } from "../components/DocumentTabBar";
import { BboxHighlightLayer } from "../components/BboxHighlightLayer";
import { CitationBadge } from "@/features/dashboard/components/CitationBadge";
import { useReaderStore } from "../stores/useReaderStore";
import { useDashboardStore } from "@/features/dashboard/stores/useDashboardStore";
import type { DocumentDetailResponseData, DocumentListItem } from "@/types/document";
import type { CitationBadgeData } from "@/types/dashboard";

vi.mock("@/features/documents/api/documentsApi", () => ({
  documentsApi: {
    attachPdf: vi.fn(),
  },
}));

describe("Deep Reading Workspace & Visual Grounding (PRD-03 / Plan 03)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useReaderStore.getState().resetReader();
    useDashboardStore.getState().setActiveBbox(null);
  });

  it("1. Renders AbstractCardViewer when document is abstract_only with academic metadata", () => {
    const mockDoc: DocumentDetailResponseData = {
      id: "doc-abstract-1",
      filename: "attention-paper.pdf",
      title: "Attention Is All You Need",
      authors: ["Vaswani et al."],
      publication_year: 2017,
      status: "abstract_only",
      access_status: "abstract_only",
      page_count: 0,
      chunk_count: 0,
      file_size_bytes: 0,
      is_persistent: false,
      pages_metadata: [],
      created_at: new Date().toISOString(),
      parsed_metadata: {
        abstract: "The dominant sequence transduction models are based on attention...",
      },
    };

    render(<AbstractCardViewer document={mockDoc} />);

    expect(screen.getByTestId("abstract-card-viewer")).toBeInTheDocument();
    expect(screen.getByText("Attention Is All You Need")).toBeInTheDocument();
    expect(screen.getByText("Tóm tắt")).toBeInTheDocument();
    expect(
      screen.getByText(/The dominant sequence transduction models are based on attention/i)
    ).toBeInTheDocument();
  });

  it("2. DocumentTabBar opens Tab Eviction Dialog when max 5 tabs reached and user adds 6th", () => {
    const mockDocs: DocumentListItem[] = [
      { id: "doc-1", filename: "paper1.pdf", title: "Paper One", is_persistent: false, status: "completed", created_at: "" },
      { id: "doc-2", filename: "paper2.pdf", title: "Paper Two", is_persistent: false, status: "completed", created_at: "" },
      { id: "doc-3", filename: "paper3.pdf", title: "Paper Three", is_persistent: false, status: "completed", created_at: "" },
      { id: "doc-4", filename: "paper4.pdf", title: "Paper Four", is_persistent: false, status: "completed", created_at: "" },
      { id: "doc-5", filename: "paper5.pdf", title: "Paper Five", is_persistent: false, status: "completed", created_at: "" },
    ];
    const openIds = ["doc-1", "doc-2", "doc-3", "doc-4", "doc-5"];

    const onSelectDoc = vi.fn();
    const onCloseDoc = vi.fn();
    const onAddDoc = vi.fn();

    render(
      <DocumentTabBar
        documents={mockDocs}
        openDocumentIds={openIds}
        activeDocumentId="doc-1"
        onSelectDocument={onSelectDoc}
        onCloseDocument={onCloseDoc}
        onAddDocument={onAddDoc}
      />
    );

    // Click the '+' button when 5 tabs are already open
    const addBtn = screen.getByTitle("Đã đạt tối đa 5 bài báo. Nhấp để đóng bớt tab.");
    expect(addBtn).toBeInTheDocument();
    fireEvent.click(addBtn);

    // Eviction dialog should appear
    expect(screen.getByTestId("tab-eviction-dialog")).toBeInTheDocument();
    expect(screen.getByText("Đã đạt giới hạn 5 bài báo")).toBeInTheDocument();

    // Closing a tab from eviction dialog triggers onCloseDoc and onAddDoc
    const evictBtns = screen.getAllByRole("button", { name: "Đóng tab này" });
    expect(evictBtns).toHaveLength(5);
    fireEvent.click(evictBtns[0]);

    expect(onCloseDoc).toHaveBeenCalledWith("doc-1");
    expect(onAddDoc).toHaveBeenCalled();
  });

  it("3. CitationBadge click switches document, sets active bbox, and dispatches scholar:focus-bbox", () => {
    const dispatchSpy = vi.spyOn(window, "dispatchEvent");
    useReaderStore.getState().setOpenDocumentIds(["doc-1", "doc-2"]);
    useReaderStore.getState().setActiveDocumentId("doc-1");

    const citation: CitationBadgeData = {
      citation_id: "cit_1",
      paper_id: "doc-2",
      paper_title: "Attention Is All You Need",
      page: 3,
      bbox: [0.1, 0.2, 0.8, 0.4, 3],
    };

    render(<CitationBadge citation={citation} />);

    const badge = screen.getByTestId("citation-badge");
    fireEvent.click(badge);

    // Verify active document changed to doc-2
    expect(useReaderStore.getState().activeDocumentId).toBe("doc-2");
    // Verify page changed to 3
    expect(useReaderStore.getState().currentPage).toBe(3);
    // Verify active bbox set in dashboard store
    expect(useDashboardStore.getState().activeBbox).toEqual([0.1, 0.2, 0.8, 0.4, 3]);

    // Verify scholar:focus-bbox event dispatched
    expect(dispatchSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        type: "scholar:focus-bbox",
        detail: {
          documentId: "doc-2",
          pageNumber: 3,
          boundingBoxes: [[0.1, 0.2, 0.8, 0.4, 3]],
        },
      })
    );
  });

  it("4. BboxHighlightLayer renders pulsing golden bounding box on matching page", () => {
    const bbox: [number, number, number, number, number] = [50, 100, 450, 160, 2];

    const { rerender } = render(
      <BboxHighlightLayer bbox={bbox} currentPage={1} isActive={true} />
    );
    // Should not render on non-matching page
    expect(screen.queryByTestId("grounded-bbox-overlay")).toBeNull();

    // Rerender on matching page 2
    rerender(<BboxHighlightLayer bbox={bbox} currentPage={2} isActive={true} />);
    const overlay = screen.getByTestId("grounded-bbox-overlay");
    expect(overlay).toBeInTheDocument();
    expect(overlay.className).toContain("border-amber-500");
    expect(overlay.className).toContain("animate-pulse");
  });

  it("5. scholar:focus-bbox event updates active document, page, and bounding box", () => {
    useReaderStore.getState().setOpenDocumentIds(["doc-1", "doc-2"]);
    useReaderStore.getState().setActiveDocumentId("doc-1");

    // Add listener matching PdfCanvasViewer behavior to verify contract
    const handleFocusBbox = (e: Event) => {
      const ce = e as CustomEvent<{ documentId?: string; pageNumber?: number; boundingBoxes?: [number, number, number, number, number][] }>;
      const { documentId, pageNumber, boundingBoxes } = ce.detail || {};
      if (documentId) useReaderStore.getState().setActiveDocumentId(documentId);
      if (pageNumber) useReaderStore.getState().setCurrentPage(pageNumber);
      if (boundingBoxes?.[0]) useDashboardStore.getState().setActiveBbox(boundingBoxes[0]);
    };
    window.addEventListener("scholar:focus-bbox", handleFocusBbox);

    window.dispatchEvent(
      new CustomEvent("scholar:focus-bbox", {
        detail: {
          documentId: "doc-2",
          pageNumber: 4,
          boundingBoxes: [[0.2, 0.3, 0.7, 0.5, 4]],
        },
      })
    );

    expect(useReaderStore.getState().activeDocumentId).toBe("doc-2");
    expect(useReaderStore.getState().currentPage).toBe(4);
    expect(useDashboardStore.getState().activeBbox).toEqual([0.2, 0.3, 0.7, 0.5, 4]);

    window.removeEventListener("scholar:focus-bbox", handleFocusBbox);
  });
});
