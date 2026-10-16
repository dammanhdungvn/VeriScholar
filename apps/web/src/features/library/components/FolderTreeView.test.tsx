import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { FolderTreeView } from "./FolderTreeView";
import { foldersApi } from "../api/foldersApi";

vi.mock("../api/foldersApi", () => ({
  foldersApi: {
    listFolders: vi.fn(),
    getFolderTree: vi.fn(),
    createFolder: vi.fn(),
    updateFolder: vi.fn(),
    deleteFolder: vi.fn(),
  },
}));

function renderWithClient(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      {ui}
    </QueryClientProvider>
  );
}

describe("FolderTreeView Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockTreeData = [
    {
      id: "folder-root-1",
      name: "Trí tuệ nhân tạo",
      parent_id: null,
      color: "#6366f1",
      description: "AI papers",
      document_count: 5,
      subfolders: [
        {
          id: "folder-sub-1",
          name: "Mô hình ngôn ngữ lớn (LLM)",
          parent_id: "folder-root-1",
          color: "#cc785c",
          description: "LLM subfolder",
          document_count: 3,
          subfolders: [],
        },
      ],
    },
  ];

  it("renders header and root folder item", async () => {
    vi.mocked(foldersApi.getFolderTree).mockResolvedValueOnce([]);

    renderWithClient(
      <FolderTreeView selectedFolderId={null} onSelectFolder={vi.fn()} />
    );

    expect(screen.getByText("Thư mục đề tài")).toBeInTheDocument();
    expect(screen.getByText("Tất cả bài báo (Root)")).toBeInTheDocument();
  });

  it("displays hierarchical folders and counts from tree query", async () => {
    vi.mocked(foldersApi.getFolderTree).mockResolvedValueOnce(mockTreeData);

    renderWithClient(
      <FolderTreeView selectedFolderId={null} onSelectFolder={vi.fn()} />
    );

    await waitFor(() => {
      expect(screen.getByText("Trí tuệ nhân tạo")).toBeInTheDocument();
      expect(screen.getByText("Mô hình ngôn ngữ lớn (LLM)")).toBeInTheDocument();
    });

    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("fires onSelectFolder when folder node is clicked", async () => {
    vi.mocked(foldersApi.getFolderTree).mockResolvedValueOnce(mockTreeData);
    const onSelectFolder = vi.fn();

    renderWithClient(
      <FolderTreeView selectedFolderId={null} onSelectFolder={onSelectFolder} />
    );

    await waitFor(() => {
      expect(screen.getByText("Trí tuệ nhân tạo")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Trí tuệ nhân tạo"));
    expect(onSelectFolder).toHaveBeenCalledWith("folder-root-1");

    fireEvent.click(screen.getByText("Tất cả bài báo (Root)"));
    expect(onSelectFolder).toHaveBeenCalledWith(null);
  });

  it("toggles create folder form and creates new folder", async () => {
    vi.mocked(foldersApi.getFolderTree).mockResolvedValue(mockTreeData);
    vi.mocked(foldersApi.createFolder).mockResolvedValueOnce({
      id: "folder-new-1",
      user_id: "user-1",
      name: "Thị giác máy tính",
      parent_id: null,
      color: "#6366f1",
      description: null,
      document_count: 0,
      subfolder_count: 0,
      created_at: "2026-10-16T00:00:00Z",
      updated_at: "2026-10-16T00:00:00Z",
    });

    renderWithClient(
      <FolderTreeView selectedFolderId={null} onSelectFolder={vi.fn()} />
    );

    // Open create form
    const createBtn = screen.getByTitle("Tạo thư mục mới");
    fireEvent.click(createBtn);

    const input = screen.getByPlaceholderText("Tên đề tài / thư mục...");
    expect(input).toBeInTheDocument();

    fireEvent.change(input, { target: { value: "Thị giác máy tính" } });
    fireEvent.submit(input.closest("form")!);

    await waitFor(() => {
      expect(foldersApi.createFolder).toHaveBeenCalledWith(
        expect.objectContaining({
          name: "Thị giác máy tính",
          parent_id: null,
        })
      );
    });
  });

  it("handles folder deletion when user confirms", async () => {
    vi.mocked(foldersApi.getFolderTree).mockResolvedValue(mockTreeData);
    vi.mocked(foldersApi.deleteFolder).mockResolvedValueOnce({
      status: "deleted",
      folder_id: "folder-root-1",
    });
    vi.spyOn(window, "confirm").mockReturnValue(true);

    const onSelectFolder = vi.fn();
    renderWithClient(
      <FolderTreeView selectedFolderId="folder-root-1" onSelectFolder={onSelectFolder} />
    );

    await waitFor(() => {
      expect(screen.getByText("Trí tuệ nhân tạo")).toBeInTheDocument();
    });

    const deleteBtn = screen.getAllByTitle("Xóa thư mục")[0];
    fireEvent.click(deleteBtn);

    await waitFor(() => {
      expect(foldersApi.deleteFolder).toHaveBeenCalledWith("folder-root-1");
      expect(onSelectFolder).toHaveBeenCalledWith(null);
    });
  });
});
