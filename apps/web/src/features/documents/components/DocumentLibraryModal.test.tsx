import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DocumentLibraryModal } from "./DocumentLibraryModal";
import { documentsApi } from "../api/documentsApi";
import { foldersApi } from "@/features/library/api/foldersApi";

vi.mock("../api/documentsApi", () => ({
  documentsApi: {
    listDocuments: vi.fn(),
    deleteDocument: vi.fn(),
  },
}));

vi.mock("@/features/library/api/foldersApi", () => ({
  foldersApi: {
    listFolders: vi.fn(),
    getFolderTree: vi.fn(),
    createFolder: vi.fn(),
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

describe("DocumentLibraryModal Component Integration", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockDocuments = [
    {
      id: "doc-1",
      filename: "attention.pdf",
      title: "Attention Is All You Need",
      status: "completed",
      is_persistent: true,
      created_at: "2026-10-16T00:00:00Z",
    },
  ];

  it("renders DocumentLibraryModal with FolderTreeView and Matrix button", () => {
    vi.mocked(documentsApi.listDocuments).mockResolvedValueOnce({
      data: mockDocuments,
      meta: {
        total: 1,
        page: 1,
        per_page: 10,
        total_pages: 1,
        request_id: "req-1",
        timestamp: "2026-10-16T00:00:00Z",
      },
      links: { first: "/documents", prev: null, self: "/documents", next: null, last: "/documents" },
    });
    vi.mocked(foldersApi.getFolderTree).mockResolvedValueOnce([]);

    renderWithClient(
      <DocumentLibraryModal
        isOpen={true}
        onClose={vi.fn()}
        onSelectDocument={vi.fn()}
      />
    );

    // Modal header
    expect(screen.getByRole("dialog", { name: "Thư viện tài liệu nghiên cứu" })).toBeInTheDocument();

    // Folder Tree pane on left
    expect(screen.getByText("Thư mục đề tài")).toBeInTheDocument();
    expect(screen.getByText("Tất cả bài báo (Root)")).toBeInTheDocument();

    // Matrix button in header
    expect(screen.getByText("Tạo Ma Trận Đối Chiếu")).toBeInTheDocument();
  });

  it("opens ComparisonMatrixModal when clicking Tạo Ma Trận Đối Chiếu", () => {
    vi.mocked(documentsApi.listDocuments).mockResolvedValueOnce({
      data: mockDocuments,
      meta: {
        total: 1,
        page: 1,
        per_page: 10,
        total_pages: 1,
        request_id: "req-1",
        timestamp: "2026-10-16T00:00:00Z",
      },
      links: { first: "/documents", prev: null, self: "/documents", next: null, last: "/documents" },
    });
    vi.mocked(foldersApi.getFolderTree).mockResolvedValueOnce([]);

    renderWithClient(
      <DocumentLibraryModal
        isOpen={true}
        onClose={vi.fn()}
        onSelectDocument={vi.fn()}
      />
    );

    const matrixBtn = screen.getByText("Tạo Ma Trận Đối Chiếu");
    fireEvent.click(matrixBtn);

    // Should open ComparisonMatrixModal dialog
    expect(screen.getByRole("dialog", { name: "Ma trận so sánh đối chiếu học thuật" })).toBeInTheDocument();
  });
});
