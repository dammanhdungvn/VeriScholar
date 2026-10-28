import { render, screen, fireEvent, waitFor } from "@testing-library/react";
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
      meta: { total: 3, page: 1, limit: 24, total_pages: 1 },
    });

    renderWithProviders(<LibraryWorkspaceView />);

    await waitFor(() => {
      expect(screen.getByText("Saved Paper")).toBeInTheDocument();
      expect(screen.getByText("Categorized Paper")).toBeInTheDocument();
      expect(screen.queryByText("Temporary Paper")).toBeNull();
    });
  });

  it("renders icon buttons for config and delete instead of raw text", async () => {
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
      meta: { total: 1, page: 1, limit: 24, total_pages: 1 },
    });

    renderWithProviders(<LibraryWorkspaceView />);

    await waitFor(() => {
      expect(screen.getByText("Paper 1")).toBeInTheDocument();
    });

    // Config and Delete should NOT be rendered as raw text in actions
    expect(screen.queryByText("Config")).toBeNull();
    expect(screen.queryByText("Delete")).toBeNull();

    // Icon buttons with appropriate testids/titles should exist
    expect(screen.getByTestId("doc-config-btn-doc-1")).toBeInTheDocument();
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
      meta: { total: 2, page: 1, limit: 24, total_pages: 1 },
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
});
