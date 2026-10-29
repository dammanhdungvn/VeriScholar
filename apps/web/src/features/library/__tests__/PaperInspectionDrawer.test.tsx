import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { PaperInspectionDrawer } from "../components/PaperInspectionDrawer";
import type { LibraryGraphNode, LibraryGraphEdge } from "../types";

describe("PaperInspectionDrawer Component (Wiki Peek Sheet)", () => {
  const dummyNode: LibraryGraphNode = {
    id: "doc-attention",
    label: "Attention Is All You Need",
    type: "Paper",
    group: "paper",
    degree: 15,
    citation_count: 15,
    community_id: 0,
    community_label: "Transformer Architectures",
    metadata: {
      publication_year: 2017,
      abstract: "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.",
      filename: "attention.pdf",
    },
  };

  const dummyNeighbor: LibraryGraphNode = {
    id: "doc-bert",
    label: "BERT: Pre-training of Deep Bidirectional Transformers",
    type: "Paper",
    group: "paper",
    degree: 10,
    citation_count: 10,
    community_id: 0,
    community_label: "Transformer Architectures",
    metadata: {
      publication_year: 2018,
    },
  };

  const dummyEdges: LibraryGraphEdge[] = [
    {
      source: "doc-bert",
      target: "doc-attention",
      relation: "cites",
      label: "cites",
      weight: 1.0,
    },
  ];

  it("renders paper details, year, abstract, and action buttons", () => {
    const handleClose = vi.fn();
    const handleOpenReader = vi.fn();
    const handleAskAI = vi.fn();

    render(
      <PaperInspectionDrawer
        isOpen={true}
        node={dummyNode}
        allNodes={[dummyNode, dummyNeighbor]}
        allEdges={dummyEdges}
        onClose={handleClose}
        onOpenReader={handleOpenReader}
        onAskAI={handleAskAI}
      />
    );

    expect(screen.getByText("Attention Is All You Need")).toBeInTheDocument();
    expect(screen.getByText("2017")).toBeInTheDocument();
    expect(screen.getByText("Transformer Architectures")).toBeInTheDocument();
    expect(screen.getByText(/sequence transduction models/i)).toBeInTheDocument();

    // Connected derivatives (BERT cites Attention)
    expect(screen.getByText(/BERT: Pre-training/i)).toBeInTheDocument();

    // Action buttons
    const readerBtn = screen.getByRole("button", { name: /Open in Deep Reader/i });
    const aiBtn = screen.getByRole("button", { name: /Ask AI About Paper/i });

    expect(readerBtn).toBeInTheDocument();
    expect(aiBtn).toBeInTheDocument();

    fireEvent.click(readerBtn);
    expect(handleOpenReader).toHaveBeenCalledWith("doc-attention");

    fireEvent.click(aiBtn);
    expect(handleAskAI).toHaveBeenCalled();
  });

  it("returns null when not open", () => {
    const { container } = render(
      <PaperInspectionDrawer
        isOpen={false}
        node={dummyNode}
        allNodes={[dummyNode]}
        allEdges={[]}
        onClose={vi.fn()}
      />
    );
    expect(container.firstChild).toBeNull();
  });
});
