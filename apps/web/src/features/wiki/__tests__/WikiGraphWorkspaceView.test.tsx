import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeAll } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import { WikiGraphWorkspaceView } from "../components/WikiGraphWorkspaceView";
import { libraryApi } from "@/features/library/api/libraryApi";

beforeAll(() => {
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
      fillRect: vi.fn(),
      measureText: vi.fn().mockReturnValue({ width: 50 }),
      getBoundingClientRect: vi.fn().mockReturnValue({ width: 800, height: 600 }),
    }) as any;
  }
});

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
      <BrowserRouter>{ui}</BrowserRouter>
    </QueryClientProvider>
  );
}

describe("WikiGraphWorkspaceView Component", () => {
  it("renders Wiki Graph workspace with 3 mode tabs (Đồ thị, Trang Wiki, Khoảng trống)", async () => {
    vi.spyOn(libraryApi, "getLibraryGraph").mockResolvedValue({
      nodes: [
        {
          id: "doc-1",
          label: "Attention Is All You Need",
          type: "Paper",
          degree: 3,
          group: "paper",
          citation_count: 10,
        },
      ],
      edges: [],
      communities: [],
      total_nodes: 1,
      total_edges: 0,
    });

    vi.spyOn(libraryApi, "listWikiPages").mockResolvedValue([
      {
        id: "w-1",
        slug: "attention-mechanism",
        title: "Self-Attention Mechanism",
        page_type: "concept",
        markdown_content: "Scaled Dot-Product Attention equation: $\\text{Attention}(Q,K,V)$",
        yaml_metadata: {},
        wikilinks: ["transformer"],
        created_at: "2026-10-25T10:00:00Z",
        updated_at: "2026-10-25T10:00:00Z",
      },
    ]);

    vi.spyOn(libraryApi, "getResearchGaps").mockResolvedValue({
      total_papers_analyzed: 5,
      identified_limitations: [{ limitation: "Quadratic memory bottleneck" }],
      unsolved_frontiers: [{ open_question: "Linear attention without accuracy degradation" }],
      recommended_directions: ["FlashAttention hardware alignment"],
      synthesized_matrix_markdown: "### Research Gaps Summary\n\n- Frontier 1",
    });

    renderWithProviders(<WikiGraphWorkspaceView />);

    expect(screen.getByTestId("wiki-graph-workspace")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Đồ thị tri thức/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Trang Wiki/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Khoảng trống/i })).toBeInTheDocument();

    // Default: Graph Canvas is rendered
    expect(screen.getByTestId("knowledge-graph-canvas")).toBeInTheDocument();

    // Switch to Trang Wiki tab
    const wikiTabBtn = screen.getByRole("button", { name: /Trang Wiki/i });
    fireEvent.click(wikiTabBtn);

    await waitFor(() => {
      expect(screen.getAllByText("Self-Attention Mechanism").length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText("[[attention-mechanism]]").length).toBeGreaterThanOrEqual(1);
    });

    // Switch to Khoảng trống tab
    const gapsTabBtn = screen.getByRole("button", { name: /Khoảng trống/i });
    fireEvent.click(gapsTabBtn);

    await waitFor(() => {
      expect(screen.getByText(/Ma trận khoảng trống nghiên cứu/i)).toBeInTheDocument();
      expect(screen.getByText(/FlashAttention hardware alignment/i)).toBeInTheDocument();
    });
  });
});
