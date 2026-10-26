import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DiscoveryPage } from "@/features/discovery/components/DiscoveryPage";
import { discoveryApi, type ScholarlyPaper } from "@/features/discovery/api/discoveryApi";
import { DocumentUploadModal } from "@/features/documents/components/DocumentUploadModal";

const mockNavigate = vi.fn();

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
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
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("DiscoveryPage Component", () => {
  const mockPapers: ScholarlyPaper[] = [
    {
      title: "Attention Is All You Need",
      authors: ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
      publication_year: 2017,
      venue: "NeurIPS 2017",
      doi: "10.48550/arXiv.1706.03762",
      arxiv_id: "1706.03762",
      abstract:
        "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
      access_status: "open_access_pdf",
      pdf_url: "https://arxiv.org/pdf/1706.03762.pdf",
    },
    {
      title: "Scaling Laws for Neural Language Models",
      authors: ["Jared Kaplan", "Sam McCandlish"],
      publication_year: 2020,
      venue: "arXiv preprint",
      doi: "10.48550/arXiv.2001.08361",
      arxiv_id: "2001.08361",
      abstract: "We investigate empirical scaling laws for language model performance...",
      access_status: "abstract_only",
      pdf_url: null,
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders search bar and displays Open Access vs Abstract Only cards", async () => {
    vi.spyOn(discoveryApi, "search").mockResolvedValue(mockPapers);

    renderWithProviders(<DiscoveryPage />);

    const searchInput = screen.getByPlaceholderText(/tìm kiếm bài báo/i);
    expect(searchInput).toBeInTheDocument();

    fireEvent.change(searchInput, { target: { value: "Transformer language models" } });
    fireEvent.keyDown(searchInput, { key: "Enter", code: "Enter" });

    await waitFor(() => {
      expect(screen.getByText(/Attention Is All You Need/i)).toBeInTheDocument();
      expect(screen.getByText(/Mở Đọc Sâu/i)).toBeInTheDocument();
      expect(screen.getByText(/Scaling Laws for Neural Language Models/i)).toBeInTheDocument();
      expect(screen.getByText(/Xem Tóm Tắt/i)).toBeInTheDocument();
    });
  });

  it("calls openReading API and redirects to /dashboard/{sessionId} on click Mở Đọc Sâu", async () => {
    vi.spyOn(discoveryApi, "search").mockResolvedValue(mockPapers);
    vi.spyOn(discoveryApi, "openReading").mockResolvedValue({
      session_id: "session-abc-123",
      document_id: "doc-xyz-456",
      status: "parsing",
      access_status: "open_access_pdf",
    });

    renderWithProviders(<DiscoveryPage />);

    const searchInput = screen.getByPlaceholderText(/tìm kiếm bài báo/i);
    fireEvent.change(searchInput, { target: { value: "Transformer" } });
    fireEvent.keyDown(searchInput, { key: "Enter", code: "Enter" });

    await waitFor(() => {
      expect(screen.getByText(/Attention Is All You Need/i)).toBeInTheDocument();
    });

    const openReadingBtn = screen.getByText(/Mở Đọc Sâu/i);
    fireEvent.click(openReadingBtn);

    await waitFor(() => {
      expect(discoveryApi.openReading).toHaveBeenCalledWith(
        expect.objectContaining({
          title: "Attention Is All You Need",
          pdf_url: "https://arxiv.org/pdf/1706.03762.pdf",
        })
      );
      expect(mockNavigate).toHaveBeenCalledWith("/dashboard/session-abc-123");
    });
  });
});

describe("DocumentUploadModal Component", () => {
  it("rejects files larger than 50MB with clear Vietnamese error message", async () => {
    const handleClose = vi.fn();
    const handleSuccess = vi.fn();

    render(
      <DocumentUploadModal
        isOpen={true}
        onClose={handleClose}
        onUploadSuccess={handleSuccess}
      />
    );

    // Create a mock 55MB file
    const oversizedFile = new File([new ArrayBuffer(100)], "oversized.pdf", {
      type: "application/pdf",
    });
    Object.defineProperty(oversizedFile, "size", { value: 55 * 1024 * 1024 });

    const fileInput = screen.getByTestId("pdf-file-input");
    fireEvent.change(fileInput, { target: { files: [oversizedFile] } });

    await waitFor(() => {
      expect(
        screen.getByText(/Dung lượng tệp vượt quá giới hạn tối đa 50MB/i)
      ).toBeInTheDocument();
    });
    expect(handleSuccess).not.toHaveBeenCalled();
  });
});
