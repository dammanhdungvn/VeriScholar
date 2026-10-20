import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DiscoveryPage } from "./DiscoveryPage";
import { sessionsApi } from "@/features/sessions/api/sessionsApi";
import { dashboardApi } from "@/features/dashboard/api/dashboardApi";
import { documentsApi } from "@/features/documents/api/documentsApi";
import { RECENT_SESSIONS } from "@/features/dashboard/data/mockDashboardData";
import type { CitationGraphData } from "@/features/reader/types/reference";

const MOCK_GRAPH: CitationGraphData = {
  nodes: [
    {
      id: "doc-1",
      title: "Attention Is All You Need",
      authors: ["Ashish Vaswani", "Noam Shazeer"],
      year: 2017,
      is_session_document: true,
      depth: 0,
      citation_count: 112000,
    },
    {
      id: "doc-2",
      title: "Layer Normalization",
      authors: ["Jimmy Lei Ba", "Geoffrey E Hinton"],
      year: 2016,
      is_session_document: false,
      depth: 1,
      citation_count: 24000,
    },
  ],
  edges: [
    {
      source: "doc-1",
      target: "doc-2",
      relation: "CITES",
      confidence: 0.9,
    },
  ],
  reading_path: ["doc-2", "doc-1"],
};

function renderDiscoveryPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/discovery"]}>
        <DiscoveryPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("DiscoveryPage - Interactive Citation Graph & Academic Resolvers", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(dashboardApi, "listSessions").mockResolvedValue(RECENT_SESSIONS);
    vi.spyOn(sessionsApi, "getCitationGraph").mockResolvedValue(MOCK_GRAPH);
  });

  it("renders page header, search input, and view toggles", async () => {
    renderDiscoveryPage();

    expect(screen.getByRole("heading", { name: /Discovery/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Search DOI, arXiv ID, or paper title/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Visual Graph/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Cards/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Resolvers/i })).toBeInTheDocument();
  });

  it("fetches and displays citation graph nodes on canvas", async () => {
    renderDiscoveryPage();

    await waitFor(() => {
      expect(sessionsApi.getCitationGraph).toHaveBeenCalled();
    });

    // Seed node details should be visible in the inspector
    await waitFor(() => {
      expect(screen.getAllByText(/Attention Is All You Need/i).length).toBeGreaterThan(0);
    });

    expect(screen.getByText(/Seed Document/i)).toBeInTheDocument();
    expect(screen.getByText(/Ashish Vaswani, Noam Shazeer/i)).toBeInTheDocument();
  });

  it("displays topological reading path chips", async () => {
    renderDiscoveryPage();

    await waitFor(() => {
      expect(screen.getByText(/Reading Path:/i)).toBeInTheDocument();
    });

    expect(screen.getAllByText(/Layer Normalization/i).length).toBeGreaterThan(0);
  });

  it("switches to Cards view when clicking Cards tab", async () => {
    renderDiscoveryPage();

    await waitFor(() => {
      expect(sessionsApi.getCitationGraph).toHaveBeenCalled();
    });

    const cardsTab = screen.getByText(/Cards/i);
    fireEvent.click(cardsTab);

    await waitFor(() => {
      expect(screen.getByText(/Year: 2017/i)).toBeInTheDocument();
      expect(screen.getByText(/Year: 2016/i)).toBeInTheDocument();
    });
  });

  it("allows searching paper resolvers and displays results", async () => {
    vi.spyOn(documentsApi, "resolveReferences").mockResolvedValue([
      {
        ref_index: 1,
        raw_text: "Vaswani et al. Attention Is All You Need. NeurIPS 2017.",
        title: "Attention Is All You Need",
        authors: ["Ashish Vaswani", "Noam Shazeer"],
        year: 2017,
        doi: "10.48550/arXiv.1706.03762",
        arxiv_id: "1706.03762",
        sources: ["arXiv"],
      },
    ]);

    renderDiscoveryPage();

    const searchInput = screen.getByPlaceholderText(/Search DOI, arXiv ID, or paper title/i);
    fireEvent.change(searchInput, { target: { value: "1706.03762" } });

    const searchButton = screen.getByRole("button", { name: /^Search$/i });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(screen.getByText(/Academic Resolvers \(Crossref, arXiv, S2\)/i)).toBeInTheDocument();
      expect(screen.getByText(/10.48550\/arXiv.1706.03762/i)).toBeInTheDocument();
    });
  });

  it("shows clean empty state and allows loading sample graph if session has no nodes", async () => {
    vi.spyOn(sessionsApi, "getCitationGraph").mockResolvedValue({
      nodes: [],
      edges: [],
    });

    renderDiscoveryPage();

    await waitFor(() => {
      expect(screen.getByText(/No Citation Graph for this Session/i)).toBeInTheDocument();
    });

    const loadSampleBtn = screen.getByRole("button", {
      name: /Load Sample Graph/i,
    });
    expect(loadSampleBtn).toBeInTheDocument();

    fireEvent.click(loadSampleBtn);

    await waitFor(() => {
      expect(screen.getAllByText(/Attention Is All You Need/i).length).toBeGreaterThan(0);
    });
  });
});
