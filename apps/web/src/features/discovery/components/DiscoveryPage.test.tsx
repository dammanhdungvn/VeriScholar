import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DiscoveryPage } from "./DiscoveryPage";
import { dashboardApi } from "@/features/dashboard/api/dashboardApi";
import { documentsApi } from "@/features/documents/api/documentsApi";
import { RECENT_SESSIONS } from "@/features/dashboard/data/mockDashboardData";

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

describe("DiscoveryPage - Academic Resolvers", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(dashboardApi, "listSessions").mockResolvedValue(RECENT_SESSIONS);
    vi.spyOn(documentsApi, "listDocuments").mockResolvedValue({
      data: [
        {
          id: "doc-1",
          filename: "attention.pdf",
          title: "Attention Is All You Need",
          status: "completed",
          is_persistent: true,
          created_at: "2026-01-01T00:00:00Z",
        },
      ],
      meta: {
        request_id: "test-request",
        timestamp: "2026-01-01T00:00:00Z",
        page: 1,
        per_page: 50,
        total: 1,
        total_pages: 1,
      },
      links: {
        first: "/documents?page=1",
        prev: null,
        self: "/documents?page=1",
        next: null,
        last: "/documents?page=1",
      },
    });
  });

  it("renders page header and search input without 2-hop SVG graph tabs", async () => {
    renderDiscoveryPage();

    expect(screen.getByRole("heading", { name: /Discovery/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Search DOI, arXiv ID, or paper title/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Visual Graph/i })).not.toBeInTheDocument();
    expect(screen.getByText(/Academic Resolvers \(Crossref, arXiv, S2\)/i)).toBeInTheDocument();
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

    await waitFor(() => {
      expect(documentsApi.listDocuments).toHaveBeenCalled();
    });

    const searchInput = screen.getByPlaceholderText(/Search DOI, arXiv ID, or paper title/i);
    fireEvent.change(searchInput, { target: { value: "Attention Is All You Need" } });

    const searchButton = screen.getByRole("button", { name: /^Search$/i });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(screen.getByText(/10.48550\/arXiv.1706.03762/i)).toBeInTheDocument();
    });
  });

  it("shows resolver error when no matching document is found", async () => {
    renderDiscoveryPage();

    await waitFor(() => {
      expect(documentsApi.listDocuments).toHaveBeenCalled();
    });

    const searchInput = screen.getByPlaceholderText(/Search DOI, arXiv ID, or paper title/i);
    fireEvent.change(searchInput, { target: { value: "Nonexistent Paper" } });

    const searchButton = screen.getByRole("button", { name: /^Search$/i });
    fireEvent.click(searchButton);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "No matching document was found in this workspace."
    );
  });
});
