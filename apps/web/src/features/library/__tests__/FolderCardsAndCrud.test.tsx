import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { LibraryWorkspaceView } from "../components/LibraryWorkspaceView";
import { documentsApi } from "@/features/documents/api/documentsApi";
import { foldersApi } from "../api/foldersApi";

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

describe("Folder Cards & Full CRUD Operations (Task 5)", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders folder cards in Folders tab and drills down to folder papers on click", async () => {
    vi.spyOn(documentsApi, "listDocuments").mockResolvedValue({
      data: [
        {
          id: "doc-1",
          filename: "transformer.pdf",
          title: "Attention Is All You Need",
          status: "completed",
          is_persistent: true,
          folder_id: "folder-ai",
          created_at: "2026-10-25T10:00:00Z",
        },
        {
          id: "doc-2",
          filename: "bert.pdf",
          title: "BERT: Pre-training of Deep Bidirectional Transformers",
          status: "completed",
          is_persistent: true,
          folder_id: null,
          created_at: "2026-10-25T10:00:00Z",
        },
      ],
      meta: {
        total: 2,
        page: 1,
        per_page: 24,
        total_pages: 1,
        request_id: "req-1",
        timestamp: "2026-10-25T10:00:00Z",
      },
      links: mockLinks,
    });

    vi.spyOn(foldersApi, "listFolders").mockResolvedValue([
      {
        id: "folder-ai",
        name: "Generative AI",
        user_id: "user-1",
        parent_id: null,
        color: "#c15f3e",
        description: null,
        subfolder_count: 0,
        created_at: "2026-10-25T10:00:00Z",
        updated_at: "2026-10-25T10:00:00Z",
        document_count: 1,
      },
      {
        id: "folder-nlp",
        name: "NLP Benchmarks",
        user_id: "user-1",
        parent_id: null,
        color: "#c15f3e",
        description: null,
        subfolder_count: 0,
        created_at: "2026-10-25T10:00:00Z",
        updated_at: "2026-10-25T10:00:00Z",
        document_count: 0,
      },
    ]);

    renderWithProviders(<LibraryWorkspaceView />);

    // Switch to Folders tab
    const foldersTabBtn = screen.getByRole("button", { name: /Folders/i });
    fireEvent.click(foldersTabBtn);

    // Verify folder cards are displayed with titles
    await waitFor(() => {
      expect(screen.getByText("Generative AI")).toBeInTheDocument();
      expect(screen.getByText("NLP Benchmarks")).toBeInTheDocument();
    });

    // Verify "+ New Folder" button exists
    expect(screen.getByRole("button", { name: /New Folder/i })).toBeInTheDocument();

    // Click on "Generative AI" folder card to drill down
    const aiCard = screen.getByTestId("folder-card-folder-ai");
    fireEvent.click(aiCard);

    // Verify breadcrumb back button appears and folder title is shown
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Back to Folders/i })).toBeInTheDocument();
      expect(screen.getByText("Attention Is All You Need")).toBeInTheDocument();
      // BERT is not in this folder, so it should not be visible
      expect(screen.queryByText("BERT: Pre-training of Deep Bidirectional Transformers")).toBeNull();
    });

    // Click "Back to Folders" to return to cards grid
    fireEvent.click(screen.getByRole("button", { name: /Back to Folders/i }));
    await waitFor(() => {
      expect(screen.getByText("Generative AI")).toBeInTheDocument();
      expect(screen.getByText("NLP Benchmarks")).toBeInTheDocument();
    });
  });

  it("opens create folder modal and submits new folder", async () => {
    vi.spyOn(documentsApi, "listDocuments").mockResolvedValue({
      data: [],
      meta: {
        total: 0,
        page: 1,
        per_page: 24,
        total_pages: 1,
        request_id: "req-create",
        timestamp: "2026-10-25T10:00:00Z",
      },
      links: mockLinks,
    });

    vi.spyOn(foldersApi, "listFolders").mockResolvedValue([]);
    const createSpy = vi.spyOn(foldersApi, "createFolder").mockResolvedValue({
      id: "folder-new",
      name: "Autonomous Agents",
      user_id: "user-1",
      parent_id: null,
      color: "#c15f3e",
      description: null,
      document_count: 0,
      subfolder_count: 0,
      created_at: "2026-10-25T10:00:00Z",
      updated_at: "2026-10-25T10:00:00Z",
    });

    renderWithProviders(<LibraryWorkspaceView />);

    // Switch to Folders tab
    fireEvent.click(screen.getByRole("button", { name: /Folders/i }));

    // Click "+ New Folder"
    await waitFor(() => {
      expect(screen.getAllByRole("button", { name: /New Folder/i })[0]).toBeInTheDocument();
    });
    fireEvent.click(screen.getAllByRole("button", { name: /New Folder/i })[0]);

    // Input folder name and submit
    const input = screen.getByPlaceholderText(/Foundation Models/i);
    fireEvent.change(input, { target: { value: "Autonomous Agents" } });
    fireEvent.click(screen.getByRole("button", { name: /^Create$/i }));

    await waitFor(() => {
      expect(createSpy).toHaveBeenCalledWith({ name: "Autonomous Agents" });
    });
  });

  it("allows moving document to another folder via MoveToFolderModal", async () => {
    vi.spyOn(documentsApi, "listDocuments").mockResolvedValue({
      data: [
        {
          id: "doc-1",
          filename: "transformer.pdf",
          title: "Attention Is All You Need",
          status: "completed",
          is_persistent: true,
          folder_id: null,
          created_at: "2026-10-25T10:00:00Z",
        },
      ],
      meta: {
        total: 1,
        page: 1,
        per_page: 24,
        total_pages: 1,
        request_id: "req-move",
        timestamp: "2026-10-25T10:00:00Z",
      },
      links: mockLinks,
    });

    vi.spyOn(foldersApi, "listFolders").mockResolvedValue([
      {
        id: "folder-ai",
        name: "Generative AI",
        user_id: "user-1",
        parent_id: null,
        color: "#c15f3e",
        description: null,
        document_count: 1,
        subfolder_count: 0,
        created_at: "2026-10-25T10:00:00Z",
        updated_at: "2026-10-25T10:00:00Z",
      },
    ]);

    const starSpy = vi.spyOn(documentsApi, "starDocument").mockResolvedValue({
      id: "doc-1",
      filename: "transformer.pdf",
      title: "Attention Is All You Need",
      status: "completed",
      is_persistent: true,
      folder_id: "folder-ai",
      updated_at: "2026-10-25T10:00:00Z",
    });

    renderWithProviders(<LibraryWorkspaceView />);

    await waitFor(() => {
      expect(screen.getByText("Attention Is All You Need")).toBeInTheDocument();
    });

    // Click move button on document
    const moveBtn = screen.getByTestId("doc-move-btn-doc-1");
    fireEvent.click(moveBtn);

    // Modal opens
    await waitFor(() => {
      expect(screen.getByText("Move to Folder")).toBeInTheDocument();
      expect(screen.getByText("Generative AI")).toBeInTheDocument();
    });

    // Select Generative AI folder and submit
    fireEvent.click(screen.getByText("Generative AI"));
    fireEvent.click(screen.getByRole("button", { name: /Move Document/i }));

    await waitFor(() => {
      expect(starSpy).toHaveBeenCalledWith("doc-1", "folder-ai");
    });
  });
});
