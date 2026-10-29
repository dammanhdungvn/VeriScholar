import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { KnowledgeGraphCanvas } from "../components/KnowledgeGraphCanvas";
import type { LibraryGraphResponseData } from "../types";

describe("KnowledgeGraphCanvas", () => {
  const mockGraphData: LibraryGraphResponseData = {
    total_nodes: 3,
    total_edges: 2,
    nodes: [
      {
        id: "doc-1",
        label: "Attention Is All You Need",
        type: "Paper",
        degree: 2,
        group: "paper",
        metadata: { filename: "attention.pdf" },
      },
      {
        id: "doc-2",
        label: "BERT: Pre-training of Deep Bidirectional Transformers",
        type: "Paper",
        degree: 1,
        group: "paper",
        metadata: { filename: "bert.pdf" },
      },
      {
        id: "method-1",
        label: "Self-Attention Mechanism",
        type: "Method",
        degree: 1,
        group: "method",
      },
    ],
    edges: [
      {
        source: "doc-1",
        target: "doc-2",
        relation: "CITES",
        label: "cites",
        weight: 1.0,
      },
      {
        source: "doc-1",
        target: "method-1",
        relation: "USES_METHOD",
        label: "uses_method",
        weight: 1.0,
      },
    ],
  };

  it("renders graph nodes and stats banner correctly", () => {
    render(
      <KnowledgeGraphCanvas
        graphData={mockGraphData}
        isLoading={false}
        onSelectDocument={vi.fn()}
      />
    );

    expect(screen.getByText(/Attention Is All You Need/i)).toBeInTheDocument();
    expect(screen.getByText(/BERT: Pre-training/i)).toBeInTheDocument();
    expect(screen.getByText(/Self-Attention Mechanism/i)).toBeInTheDocument();
  });

  it("opens node detail inspector when clicking a node", () => {
    const handleSelectDoc = vi.fn();
    render(
      <KnowledgeGraphCanvas
        graphData={mockGraphData}
        isLoading={false}
        onSelectDocument={handleSelectDoc}
      />
    );

    const paperNode = screen.getByText(/Attention Is All You Need/i);
    fireEvent.click(paperNode);

    // Inspector drawer should appear showing details
    expect(screen.getByText(/Chi tiết thực thể/i)).toBeInTheDocument();
    expect(screen.getByText(/Bậc liên kết:/i)).toBeInTheDocument();
  });

  it("filters nodes via search input", () => {
    render(
      <KnowledgeGraphCanvas
        graphData={mockGraphData}
        isLoading={false}
        onSelectDocument={vi.fn()}
      />
    );

    const searchInput = screen.getByPlaceholderText(/Lọc thực thể theo tên/i);
    fireEvent.change(searchInput, { target: { value: "BERT" } });

    expect(screen.getByText(/BERT: Pre-training/i)).toBeInTheDocument();
  });
});
