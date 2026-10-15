import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { SourceEvidenceModal } from "./SourceEvidenceModal";
import { useWritingStore } from "../stores/useWritingStore";
import type { AtomicClaim } from "../types";

describe("SourceEvidenceModal", () => {
  const mockClaimWithDoc: AtomicClaim = {
    id: "claim-101",
    claim_text: "The Transformer model relies solely on attention mechanisms.",
    normalized_entities: ["transformer", "attention mechanism"],
    status: "supported",
    confidence_score: 0.98,
    evidence_text: "We propose the Transformer, a model architecture eschewing recurrence.",
    evidence_document_id: "doc-vaswani-2017",
    evidence_document_title: "Attention Is All You Need",
    evidence_page: 2,
    evidence_bounding_boxes: [
      [0.12, 0.34, 0.85, 0.42, 2],
      [0.15, 0.50, 0.75, 0.60, 2],
    ],
    reasoning: "Direct quote verified from section 1 Introduction.",
  };

  const mockClaimWithoutDoc: AtomicClaim = {
    id: "claim-102",
    claim_text: "Empirical evaluation shows superior BLEU score.",
    normalized_entities: ["BLEU score"],
    status: "contradicted",
    confidence_score: 0.88,
    evidence_text: "Recurrent models still hold slight edge on synthetic benchmarks.",
    evidence_page: 5,
    evidence_bounding_boxes: [[0.2, 0.3, 0.8, 0.4, 5]],
  };

  beforeEach(() => {
    useWritingStore.getState().reset();
  });

  it("does not render when isOpen is false", () => {
    const { container } = render(
      <SourceEvidenceModal isOpen={false} claim={mockClaimWithDoc} onClose={vi.fn()} />
    );
    expect(container.firstChild).toBeNull();
  });

  it("does not render when claim is null", () => {
    const { container } = render(
      <SourceEvidenceModal isOpen={true} claim={null} onClose={vi.fn()} />
    );
    expect(container.firstChild).toBeNull();
  });

  it("renders source document PDF, claim text, and bounding box overlay when documentId is provided", () => {
    render(
      <SourceEvidenceModal isOpen={true} claim={mockClaimWithDoc} onClose={vi.fn()} />
    );

    // Header & Meta
    expect(screen.getByText(/Attention Is All You Need/i)).toBeDefined();
    expect(screen.getByText("SUPPORTED")).toBeDefined();
    expect(screen.getByText("Trang 2")).toBeDefined();
    expect(screen.getByText("98% độ tin cậy")).toBeDefined();

    // Claim & Evidence Quotes
    expect(screen.getByText(new RegExp(mockClaimWithDoc.claim_text, "i"))).toBeDefined();
    expect(screen.getByText(new RegExp(mockClaimWithDoc.evidence_text!, "i"))).toBeDefined();

    // PDF Iframe Viewport
    const pdfContainer = screen.getByTestId("source-pdf-container");
    expect(pdfContainer).toBeDefined();
    const iframe = pdfContainer.querySelector("iframe");
    expect(iframe).toBeDefined();
    expect(iframe?.getAttribute("src")).toContain("/documents/doc-vaswani-2017/file#page=2");

    // Bounding Box Overlays
    const bboxOverlay = screen.getByTestId("source-evidence-bbox-overlay");
    expect(bboxOverlay).toBeDefined();
    const highlights = screen.getAllByTestId("evidence-bbox-highlight");
    expect(highlights.length).toBe(2);

    // Coordinate badges
    expect(screen.getByText(/Tọa độ Bounding Box/i)).toBeDefined();
    expect(screen.getByText(/#1: \[0.120, 0.340, 0.850, 0.420\]/i)).toBeDefined();
  });

  it("renders citation fallback when evidence_document_id is absent", () => {
    render(
      <SourceEvidenceModal isOpen={true} claim={mockClaimWithoutDoc} onClose={vi.fn()} />
    );

    expect(screen.getByText("CONTRADICTED")).toBeDefined();
    expect(screen.getByTestId("source-pdf-fallback")).toBeDefined();
    expect(screen.getAllByText(new RegExp(mockClaimWithoutDoc.evidence_text!, "i")).length).toBeGreaterThanOrEqual(1);
  });

  it("triggers onClose callback when clicking close button or pressing Escape", () => {
    const onClose = vi.fn();
    render(
      <SourceEvidenceModal isOpen={true} claim={mockClaimWithDoc} onClose={onClose} />
    );

    const closeBtn = screen.getByRole("button", { name: "Đóng" });
    fireEvent.click(closeBtn);
    expect(onClose).toHaveBeenCalledTimes(1);

    fireEvent.keyDown(window, { key: "Escape" });
    expect(onClose).toHaveBeenCalledTimes(2);
  });

  it("can be triggered and closed seamlessly through useWritingStore", () => {
    render(<SourceEvidenceModal />);

    // Initially closed
    expect(screen.queryByRole("dialog")).toBeNull();

    // Open via store
    act(() => {
      useWritingStore.getState().openEvidenceModal(mockClaimWithDoc);
    });
    expect(screen.getByRole("dialog")).toBeDefined();
    expect(screen.getByText(/Attention Is All You Need/i)).toBeDefined();

    // Close via store
    act(() => {
      useWritingStore.getState().closeEvidenceModal();
    });
    expect(screen.queryByRole("dialog")).toBeNull();
  });
});
