import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { LibraryWorkspaceView } from "../components/LibraryWorkspaceView";
import { documentsApi } from "@/features/documents/api/documentsApi";

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
    },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

const mockLinks = {
  first: "/api/v1/documents?page=1",
  prev: null,
  self: "/api/v1/documents?page=1",
  next: null,
  last: "/api/v1/documents?page=1",
};

describe("LibraryWorkspaceView Persistence & Minimalist Icons (Task 5)", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("only displays persistent or categorized documents in My Library", async () => {
    vi.spyOn(documentsApi, "listDocuments").mockResolvedValue({
      data: [
        {
          id: "doc-1",
          filename: "saved_paper.pdf",
          title: "Saved Paper",
          status: "completed",
          is_persistent: true,
          created_at: "2026-10-25T10:00:00Z",
        },
        {
          id: "doc-2",
          filename: "temp_paper.pdf",
          title: "Temporary Paper",
          status: "completed",
          is_persistent: false,
          created_at: "2026-10-25T10:00:00Z",
        },
        {
          id: "doc-3",
          filename: "categorized_paper.pdf",
          title: "Categorized Paper",
          status: "completed",
          is_persistent: false,
          folder_id: "folder-123",
          created_at: "2026-10-25T10:00:00Z",
        },
      ],
      meta: {
        total: 3,
        page: 1,
        per_page: 24,
        total_pages: 1,
        request_id: "req-1",
        timestamp: "2026-10-25T10:00:00Z",
      },
      links: mockLinks,
    });

    renderWithProviders(<LibraryWorkspaceView />);

    await waitFor(() => {
      expect(screen.getByText("Saved Paper")).toBeInTheDocument();
      expect(screen.getByText("Categorized Paper")).toBeInTheDocument();
      expect(screen.queryByText("Temporary Paper")).toBeNull();
    });
  });

  it("renders delete icon button and eliminates internal parse config button", async () => {
    vi.spyOn(documentsApi, "listDocuments").mockResolvedValue({
      data: [
        {
          id: "doc-1",
          filename: "paper1.pdf",
          title: "Paper 1",
          status: "completed",
          is_persistent: true,
          created_at: "2026-10-25T10:00:00Z",
        },
      ],
      meta: {
        total: 1,
        page: 1,
        per_page: 24,
        total_pages: 1,
        request_id: "req-2",
        timestamp: "2026-10-25T10:00:00Z",
      },
      links: mockLinks,
    });

    renderWithProviders(<LibraryWorkspaceView />);

    await waitFor(() => {
      expect(screen.getByText("Paper 1")).toBeInTheDocument();
    });

    // Config button should NOT exist anywhere (eliminating cognitive noise)
    expect(screen.queryByTestId("doc-config-btn-doc-1")).toBeNull();
    expect(screen.queryByTitle("Tùy chọn phân tích")).toBeNull();

    // Delete button exists as icon
    expect(screen.getByTestId("doc-delete-btn-doc-1")).toBeInTheDocument();
  });

  it("hides repetitive completed status badges on cards", async () => {
    vi.spyOn(documentsApi, "listDocuments").mockResolvedValue({
      data: [
        {
          id: "doc-1",
          filename: "paper1.pdf",
          title: "Paper 1",
          status: "completed",
          is_persistent: true,
          created_at: "2026-10-25T10:00:00Z",
        },
        {
          id: "doc-2",
          filename: "paper2.pdf",
          title: "Paper 2",
          status: "indexing",
          is_persistent: true,
          created_at: "2026-10-25T10:00:00Z",
        },
      ],
      meta: {
        total: 2,
        page: 1,
        per_page: 24,
        total_pages: 1,
        request_id: "req-3",
        timestamp: "2026-10-25T10:00:00Z",
      },
      links: mockLinks,
    });

    renderWithProviders(<LibraryWorkspaceView />);

    await waitFor(() => {
      expect(screen.getByText("Paper 1")).toBeInTheDocument();
      expect(screen.getByText("Paper 2")).toBeInTheDocument();
    });

    // "completed" badge should be hidden, but non-completed "indexing" badge is displayed
    expect(screen.queryByText("completed")).toBeNull();
    expect(screen.getByText("indexing")).toBeInTheDocument();
  });

  it("renders 3 ribbon tabs (All Papers, Folders, Knowledge Graph) and switches to Knowledge Graph tab", async () => {
    vi.spyOn(documentsApi, "listDocuments").mockResolvedValue({
      data: [
        {
          id: "doc-1",
          filename: "attention.pdf",
          title: "Attention Is All You Need",
          status: "completed",
          is_persistent: true,
          created_at: "2026-10-25T10:00:00Z",
        },
      ],
      meta: {
        total: 1,
        page: 1,
        per_page: 24,
        total_pages: 1,
        request_id: "req-4",
        timestamp: "2026-10-25T10:00:00Z",
      },
      links: mockLinks,
    });

    renderWithProviders(<LibraryWorkspaceView />);

    // Primary 3 ribbon tabs exist in English
    expect(screen.getByRole("button", { name: /All Papers/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Folders/i })).toBeInTheDocument();
    const graphTabBtn = screen.getByRole("button", { name: /Knowledge Graph/i });
    expect(graphTabBtn).toBeInTheDocument();

    // FAB exists
    expect(screen.getByRole("button", { name: /Trợ lý GraphRAG/i })).toBeInTheDocument();

    // Clicking Knowledge Graph tab switches active view
    fireEvent.click(graphTabBtn);
    expect(graphTabBtn).toHaveClass("font-semibold");
  });
});
