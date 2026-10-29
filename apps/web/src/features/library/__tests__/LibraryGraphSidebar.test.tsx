import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeAll } from "vitest";
import { LibraryGraphSidebar } from "../components/LibraryGraphSidebar";
import type { LibraryGraphResponseData } from "../types";

describe("LibraryGraphSidebar Component", () => {
  beforeAll(() => {
    // jsdom HTMLCanvasElement mock
    if (typeof window !== "undefined") {
      window.HTMLCanvasElement.prototype.getContext = vi.fn().mockReturnValue({
        clearRect: vi.fn(),
        save: vi.fn(),
        restore: vi.fn(),
        scale: vi.fn(),
        translate: vi.fn(),
        beginPath: vi.fn(),
        arc: vi.fn(),
        fill: vi.fn(),
        stroke: vi.fn(),
        moveTo: vi.fn(),
        lineTo: vi.fn(),
        fillText: vi.fn(),
        measureText: vi.fn().mockReturnValue({ width: 50 }),
      }) as any;
    }
  });

  const mockGraphData: LibraryGraphResponseData = {
    total_nodes: 2,
    total_edges: 1,
    nodes: [
      {
        id: "doc-1",
        label: "Attention Is All You Need",
        type: "Paper",
        group: "paper",
        degree: 4,
        citation_count: 12,
        community_id: 0,
        community_label: "Transformers",
        metadata: {
          publication_year: 2017,
          abstract: "Attention model for NLP.",
        },
      },
      {
        id: "doc-2",
        label: "BERT",
        type: "Paper",
        group: "paper",
        degree: 2,
        citation_count: 8,
        community_id: 0,
        community_label: "Transformers",
      },
    ],
    edges: [
      {
        source: "doc-2",
        target: "doc-1",
        relation: "cites",
        label: "cites",
        weight: 1.0,
      },
    ],
    communities: [
      {
        id: 0,
        label: "Transformers",
        paper_count: 2,
        node_ids: ["doc-1", "doc-2"],
      },
    ],
  };

  it("renders sidebar with title, stats, and canvas container", () => {
    const handleClose = vi.fn();
    render(
      <LibraryGraphSidebar
        isOpen={true}
        onClose={handleClose}
        graphData={mockGraphData}
        isLoading={false}
      />
    );

    expect(screen.getByText("Wiki Graph")).toBeInTheDocument();
    expect(screen.getByText(/2 nodes · 1 edge/i)).toBeInTheDocument();
    expect(screen.getByTestId("knowledge-graph-canvas")).toBeInTheDocument();

    const closeBtn = screen.getByRole("button", { name: /Close sidebar/i });
    expect(closeBtn).toBeInTheDocument();
    fireEvent.click(closeBtn);
    expect(handleClose).toHaveBeenCalled();
  });

  it("renders focused paper badge when focusedNodeId is provided", () => {
    const handleClearFocus = vi.fn();
    render(
      <LibraryGraphSidebar
        isOpen={true}
        onClose={vi.fn()}
        graphData={mockGraphData}
        focusedNodeId="doc-1"
        onClearFocus={handleClearFocus}
      />
    );

    expect(screen.getByText(/Focused: Attention Is All You Need/i)).toBeInTheDocument();
    const clearBtn = screen.getByRole("button", { name: /Clear focus/i });
    fireEvent.click(clearBtn);
    expect(handleClearFocus).toHaveBeenCalled();
  });

  it("renders nothing when isOpen is false", () => {
    const { container } = render(
      <LibraryGraphSidebar
        isOpen={false}
        onClose={vi.fn()}
        graphData={mockGraphData}
      />
    );
    expect(container.firstChild).toBeNull();
  });
});
