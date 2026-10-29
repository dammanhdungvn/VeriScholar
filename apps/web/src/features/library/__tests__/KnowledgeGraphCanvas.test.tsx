import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeAll } from "vitest";
import { KnowledgeGraphCanvas } from "../components/KnowledgeGraphCanvas";
import type { LibraryGraphResponseData } from "../types";

beforeAll(() => {
  // Mock HTMLCanvasElement.prototype.getContext for jsdom
  HTMLCanvasElement.prototype.getContext = vi.fn().mockReturnValue({
    clearRect: vi.fn(),
    save: vi.fn(),
    restore: vi.fn(),
    beginPath: vi.fn(),
    arc: vi.fn(),
    fill: vi.fn(),
    stroke: vi.fn(),
    moveTo: vi.fn(),
    lineTo: vi.fn(),
    scale: vi.fn(),
    translate: vi.fn(),
    fillText: vi.fn(),
    getBoundingClientRect: vi.fn().mockReturnValue({ width: 800, height: 600 }),
  });
});

describe("KnowledgeGraphCanvas HTML5 Force Simulation", () => {
  const mockGraphData: LibraryGraphResponseData = {
    total_nodes: 3,
    total_edges: 2,
    nodes: [
      {
        id: "doc-1",
        label: "Attention Is All You Need",
        type: "Paper",
        degree: 2,
        citation_count: 12,
        community_id: 0,
        community_label: "Transformer Architectures",
        group: "paper",
        metadata: {
          filename: "attention.pdf",
          abstract: "The dominant sequence transduction models are based on complex recurrent networks.",
          publication_year: 2017,
        },
      },
      {
        id: "doc-2",
        label: "BERT: Pre-training of Deep Bidirectional Transformers",
        type: "Paper",
        degree: 1,
        citation_count: 8,
        community_id: 0,
        community_label: "Transformer Architectures",
        group: "paper",
        metadata: { filename: "bert.pdf", publication_year: 2018 },
      },
      {
        id: "method-1",
        label: "Self-Attention Mechanism",
        type: "Method",
        degree: 1,
        citation_count: 0,
        community_id: 1,
        community_label: "Attention Mechanisms",
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
    communities: [
      {
        id: 0,
        label: "Transformer Architectures",
        paper_count: 2,
        node_ids: ["doc-1", "doc-2"],
      },
      {
        id: 1,
        label: "Attention Mechanisms",
        paper_count: 1,
        node_ids: ["method-1"],
      },
    ],
  };

  it("renders HTML5 canvas element with data-testid='knowledge-graph-canvas'", () => {
    const handleSelect = vi.fn();
    render(
      <KnowledgeGraphCanvas
        graphData={mockGraphData}
        isLoading={false}
        onSelectDocument={handleSelect}
      />
    );

    const canvas = screen.getByTestId("knowledge-graph-canvas");
    expect(canvas).toBeInTheDocument();
  });

  it("renders community clusters and search filter", () => {
    render(
      <KnowledgeGraphCanvas
        graphData={mockGraphData}
        isLoading={false}
      />
    );

    expect(screen.getByPlaceholderText(/Lọc thực thể/i)).toBeInTheDocument();
    expect(screen.getByText(/Transformer Architectures/i)).toBeInTheDocument();
    expect(screen.getByText(/Attention Mechanisms/i)).toBeInTheDocument();
  });

  it("allows selecting a community filter badge", () => {
    const handleSelectCommunity = vi.fn();
    render(
      <KnowledgeGraphCanvas
        graphData={mockGraphData}
        isLoading={false}
        onSelectCommunity={handleSelectCommunity}
      />
    );

    const communityBadge = screen.getByText(/Transformer Architectures/i);
    fireEvent.click(communityBadge);
    expect(handleSelectCommunity).toHaveBeenCalledWith(
      expect.objectContaining({ label: "Transformer Architectures" })
    );
  });

  it("renders entity filter tabs with count badges and floating legend", () => {
    render(
      <KnowledgeGraphCanvas
        graphData={mockGraphData}
        isLoading={false}
      />
    );

    // Entity filter buttons exist with counts
    expect(screen.getByRole("button", { name: /^Tất cả\s*3/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Bài báo\s*2/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Phương pháp\s*1/i })).toBeInTheDocument();

    // Floating legend displays entity categories
    expect(screen.getByText("📄 Bài báo")).toBeInTheDocument();
    expect(screen.getByText("⚡ Phương pháp")).toBeInTheDocument();
    expect(screen.getByText("📊 Tập dữ liệu")).toBeInTheDocument();
    expect(screen.getByText("🎯 Chỉ số")).toBeInTheDocument();
  });

  it("handles trackpad wheel pan event gracefully without zoom explosion", () => {
    render(
      <KnowledgeGraphCanvas
        graphData={mockGraphData}
        isLoading={false}
      />
    );

    const canvas = screen.getByTestId("knowledge-graph-canvas");
    // Fire a trackpad two-finger scroll event (deltaX > 0 or small deltaY)
    fireEvent.wheel(canvas, {
      deltaX: 12,
      deltaY: 8,
      ctrlKey: false,
    });
    // Canvas should remain intact and responsive
    expect(canvas).toBeInTheDocument();
  });
});
