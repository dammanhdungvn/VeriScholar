import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { KnowledgeSubgraphViewer } from "../components/KnowledgeSubgraphViewer";
import { BibliometricsPriorWorksCard } from "../components/BibliometricsPriorWorksCard";
import { LibraryWorkspaceView } from "../components/LibraryWorkspaceView";
import { libraryApi } from "../api/libraryApi";
import type { GraphSubgraph, BibliometricsResponseData } from "../types";

const mockSubgraph: GraphSubgraph = {
  nodes: [
    {
      id: "uuid-1",
      type: "Method",
      name: "Transformer",
      degree_centrality: 8,
      role: "method_hub",
    },
    {
      id: "uuid-2",
      type: "Paper",
      name: "Attention Is All You Need (2017)",
      year: 2017,
      degree_centrality: 14,
      role: "prior_work",
    },
    {
      id: "uuid-3",
      type: "Paper",
      name: "An Image is Worth 16x16 Words (2020)",
      year: 2020,
      degree_centrality: 6,
      role: "derivative_work",
    },
    {
      id: "uuid-4",
      type: "MetricResult",
      name: "BLEU: 28.4",
      degree_centrality: 2,
      role: "metric",
    },
    {
      id: "uuid-5",
      type: "MetricResult",
      name: "Top-1 Accuracy: 88.55%",
      degree_centrality: 2,
      role: "metric",
    },
    {
      id: "uuid-6",
      type: "Dataset",
      name: "WMT-2014 En-De",
      degree_centrality: 4,
    },
  ],
  edges: [
    {
      document_id: "uuid-doc-1",
      source: "uuid-2",
      target: "uuid-1",
      type: "PROPOSES",
      evidence_chunk_id: "chunk-101",
      page_number: 3,
    },
    {
      document_id: "uuid-doc-2",
      source: "uuid-3",
      target: "uuid-1",
      type: "PROPOSES",
      evidence_chunk_id: "chunk-202",
      page_number: 2,
    },
    {
      document_id: "uuid-doc-1",
      source: "uuid-1",
      target: "uuid-4",
      type: "ACHIEVES",
      evidence_chunk_id: "chunk-108",
      page_number: 8,
    },
    {
      document_id: "uuid-doc-2",
      source: "uuid-1",
      target: "uuid-5",
      type: "ACHIEVES",
      evidence_chunk_id: "chunk-205",
      page_number: 5,
    },
    {
      document_id: "uuid-doc-1",
      source: "uuid-1",
      target: "uuid-6",
      type: "EVALUATED_ON",
      page_number: 7,
    },
  ],
  evidence: [
    {
      chunk_id: "chunk-108",
      document_id: "uuid-doc-1",
      page_number: 8,
      chunk_text: "The model achieves 28.4 BLEU on the WMT 2014 English-to-German task.",
      bbox: [{ page_number: 8, x: 100, y: 200, width: 300, height: 50 }],
    },
  ],
};

const mockBibliometrics: BibliometricsResponseData = {
  folder_id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  prior_works: [
    {
      id: "uuid-2",
      title: "Attention Is All You Need",
      year: 2017,
      in_degree: 5,
      citation_key: "vaswani2017",
    },
  ],
  derivative_works: [
    {
      id: "uuid-3",
      title: "An Image is Worth 16x16 Words",
      year: 2020,
      out_degree: 4,
      citation_key: "dosovitskiy2020",
    },
  ],
  coupling_edges: [
    {
      paper_a_id: "uuid-2",
      paper_b_id: "uuid-3",
      shared_reference_count: 4,
    },
  ],
};

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("KnowledgeSubgraphViewer", () => {
  it("renders all 4 entity node types with sizes proportional to degree_centrality", () => {
    const { container } = render(<KnowledgeSubgraphViewer subgraph={mockSubgraph} />);

    // 1. Verify all 4 node types are rendered
    expect(screen.getByText("Transformer")).toBeInTheDocument();
    expect(screen.getByText("Attention Is All You Need (2017)")).toBeInTheDocument();
    expect(screen.getByText("WMT-2014 En-De")).toBeInTheDocument();
    expect(screen.getByText("BLEU: 28.4")).toBeInTheDocument();

    // 2. Node with higher degree_centrality (uuid-2, degree: 14) has larger radius than uuid-4 (degree: 2)
    const highDegreeCircle = container.querySelector('[data-node-id="uuid-2"] circle');
    const lowDegreeCircle = container.querySelector('[data-node-id="uuid-4"] circle');

    expect(highDegreeCircle).not.toBeNull();
    expect(lowDegreeCircle).not.toBeNull();

    const highRadius = Number(highDegreeCircle?.getAttribute("r") || 0);
    const lowRadius = Number(lowDegreeCircle?.getAttribute("r") || 0);
    expect(highRadius).toBeGreaterThan(lowRadius);
  });

  it("renders edges connecting nodes in SVG", () => {
    const { container } = render(<KnowledgeSubgraphViewer subgraph={mockSubgraph} />);

    const edges = container.querySelectorAll('[data-testid="graph-edge"]');
    expect(edges.length).toBe(mockSubgraph.edges.length);
  });

  it("calls onEdgeSelect with page and evidence information when an edge is clicked or double clicked", () => {
    const onEdgeSelect = vi.fn();
    const { container } = render(
      <KnowledgeSubgraphViewer subgraph={mockSubgraph} onEdgeSelect={onEdgeSelect} />
    );

    // Target the edge connecting uuid-1 to uuid-4 (ACHIEVES, page 8, chunk-108)
    const targetEdge = container.querySelector(
      '[data-edge-key="uuid-1->uuid-4"]'
    ) || container.querySelector('[data-testid="graph-edge"]');

    expect(targetEdge).not.toBeNull();
    fireEvent.doubleClick(targetEdge!);

    expect(onEdgeSelect).toHaveBeenCalled();
    const [selectedEdge, evidence] = onEdgeSelect.mock.calls[0];
    expect(selectedEdge.page_number).toBe(8);
    expect(selectedEdge.document_id).toBe("uuid-doc-1");
    expect(evidence).toBeDefined();
    expect(evidence?.chunk_id).toBe("chunk-108");
  });
});

describe("BibliometricsPriorWorksCard", () => {
  it("displays prior works with in-degree and derivative works with out-degree", () => {
    render(<BibliometricsPriorWorksCard data={mockBibliometrics} />);

    // Prior Works section
    expect(screen.getByText("Attention Is All You Need")).toBeInTheDocument();
    expect(screen.getByTestId("prior-work-in-degree")).toHaveTextContent("5");

    // Derivative Works section
    expect(screen.getByText("An Image is Worth 16x16 Words")).toBeInTheDocument();
    expect(screen.getByTestId("derivative-work-out-degree")).toHaveTextContent("4");
  });

  it("displays shared reference count between paper pairs in coupling_edges", () => {
    render(<BibliometricsPriorWorksCard data={mockBibliometrics} />);

    expect(screen.getByText(/4 tài liệu tham khảo chung/i)).toBeInTheDocument();
  });
});

describe("LibraryWorkspaceView GraphRAG Search", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders 3 search modes and executes queryGraph API displaying synthesized answer and subgraph", async () => {
    const querySpy = vi.spyOn(libraryApi, "queryGraph").mockResolvedValue({
      mode_used: "hybrid",
      answer: "Transformer models achieve SOTA on BLEU and Top-1 Accuracy across WMT and ImageNet.",
      subgraph: mockSubgraph,
      meta: { matched_entities: 6 },
    });

    renderWithProviders(<LibraryWorkspaceView />);

    // Verify 3 mode buttons exist
    const hybridBtn = screen.getByRole("button", { name: /hybrid/i });
    const localBtn = screen.getByRole("button", { name: /local/i });
    const globalBtn = screen.getByRole("button", { name: /global/i });

    expect(hybridBtn).toBeInTheDocument();
    expect(localBtn).toBeInTheDocument();
    expect(globalBtn).toBeInTheDocument();

    // Select Local mode
    fireEvent.click(localBtn);

    // Type query
    const searchInput = screen.getByPlaceholderText(/Hỏi đáp SOTA, đối chiếu mô hình hoặc tra cứu đồ thị/i);
    fireEvent.change(searchInput, { target: { value: "Transformer BLEU accuracy" } });

    // Submit search
    const submitBtn = screen.getByTestId("graphrag-search-submit");
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(querySpy).toHaveBeenCalledWith({
        query: "Transformer BLEU accuracy",
        mode: "local",
        folder_id: null,
      });
    });

    // Check synthesized answer is displayed
    await waitFor(() => {
      expect(
        screen.getByText(/Transformer models achieve SOTA on BLEU and Top-1 Accuracy across WMT and ImageNet./i)
      ).toBeInTheDocument();
    });

    // Check subgraph nodes are rendered
    expect(screen.getByText("Transformer")).toBeInTheDocument();
  });
});
