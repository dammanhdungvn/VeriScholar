import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { AbstractOnlyViewer } from "../components/AbstractOnlyViewer";
import { documentsApi } from "@/features/documents/api/documentsApi";
import type { DocumentDetailResponseData } from "@/types/document";

vi.mock("@/features/documents/api/documentsApi", () => ({
  documentsApi: {
    attachPdf: vi.fn(),
  },
}));

describe("AbstractOnlyViewer Component", () => {
  const mockDocument: DocumentDetailResponseData = {
    id: "doc-12345",
    filename: "attention-is-all-you-need.pdf",
    title: "Attention Is All You Need",
    authors: ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
    publication_year: 2017,
    doi: "10.48550/arXiv.1706.03762",
    page_count: 0,
    chunk_count: 0,
    file_size_bytes: 0,
    status: "abstract_only",
    access_status: "abstract_only",
    is_persistent: false,
    pages_metadata: [],
    created_at: new Date().toISOString(),
    parsed_metadata: {
      abstract: "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
      arxiv_id: "1706.03762",
      venue: "NeurIPS 2017",
    },
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders paper title, authors, year, abstract, and 'Tóm tắt' badge", () => {
    render(<AbstractOnlyViewer document={mockDocument} />);

    // Title
    const titleEl = screen.getByRole("heading", { level: 2 });
    expect(titleEl).toHaveTextContent("Attention Is All You Need");
    expect(titleEl.className).toContain("font-serif");

    // Badge
    expect(screen.getByText("Tóm tắt")).toBeInTheDocument();

    // Authors and Year
    expect(screen.getByText(/Ashish Vaswani, Noam Shazeer, Niki Parmar/i)).toBeInTheDocument();
    expect(screen.getByText("2017")).toBeInTheDocument();

    // Abstract content
    expect(
      screen.getByText(/The dominant sequence transduction models are based on complex recurrent/i)
    ).toBeInTheDocument();
  });

  it("renders external DOI and arXiv links opening in a new tab", () => {
    render(<AbstractOnlyViewer document={mockDocument} />);

    // DOI link
    const doiLink = screen.getByRole("link", { name: /doi/i });
    expect(doiLink).toBeInTheDocument();
    expect(doiLink).toHaveAttribute("href", "https://doi.org/10.48550/arXiv.1706.03762");
    expect(doiLink).toHaveAttribute("target", "_blank");
    expect(doiLink).toHaveAttribute("rel", "noopener noreferrer");

    // arXiv link
    const arxivLink = screen.getByRole("link", { name: /arxiv/i });
    expect(arxivLink).toBeInTheDocument();
    expect(arxivLink).toHaveAttribute("href", "https://arxiv.org/abs/1706.03762");
    expect(arxivLink).toHaveAttribute("target", "_blank");
    expect(arxivLink).toHaveAttribute("rel", "noopener noreferrer");
  });

  it("handles file selection via input, calls attachPdf, and triggers onPdfAttached", async () => {
    const onPdfAttached = vi.fn();
    const mockUploadResponse = {
      id: "doc-12345",
      filename: "paper.pdf",
      file_size_bytes: 1024,
      status: "completed",
      stage: "completed",
    };
    vi.mocked(documentsApi.attachPdf).mockResolvedValueOnce(mockUploadResponse);

    render(<AbstractOnlyViewer document={mockDocument} onPdfAttached={onPdfAttached} />);

    expect(screen.getByText("Đính kèm bản PDF đầy đủ")).toBeInTheDocument();
    expect(screen.getByText("Kéo thả hoặc nhấn để chọn tệp PDF")).toBeInTheDocument();

    const file = new File(["%PDF-1.4 test"], "paper.pdf", { type: "application/pdf" });
    const fileInput = screen.getByTestId("pdf-upload-input");

    fireEvent.change(fileInput, { target: { files: [file] } });

    // Displays loading indicator
    expect(screen.getByText("Đang tải lên và xử lý...")).toBeInTheDocument();

    await waitFor(() => {
      expect(documentsApi.attachPdf).toHaveBeenCalledWith("doc-12345", file);
      expect(onPdfAttached).toHaveBeenCalledTimes(1);
    });
  });

  it("handles drag-and-drop of PDF file", async () => {
    const onPdfAttached = vi.fn();
    vi.mocked(documentsApi.attachPdf).mockResolvedValueOnce({
      id: "doc-12345",
      filename: "dropped.pdf",
      file_size_bytes: 2048,
      status: "completed",
      stage: "completed",
    });

    render(<AbstractOnlyViewer document={mockDocument} onPdfAttached={onPdfAttached} />);

    const dropzone = screen.getByTestId("pdf-dropzone");
    const file = new File(["%PDF-1.5 test"], "dropped.pdf", { type: "application/pdf" });

    fireEvent.drop(dropzone, {
      dataTransfer: {
        files: [file],
      },
    });

    await waitFor(() => {
      expect(documentsApi.attachPdf).toHaveBeenCalledWith("doc-12345", file);
      expect(onPdfAttached).toHaveBeenCalledTimes(1);
    });
  });

  it("rejects non-PDF files and displays a friendly error", async () => {
    const onPdfAttached = vi.fn();
    render(<AbstractOnlyViewer document={mockDocument} onPdfAttached={onPdfAttached} />);

    const txtFile = new File(["not a pdf"], "notes.txt", { type: "text/plain" });
    const fileInput = screen.getByTestId("pdf-upload-input");

    fireEvent.change(fileInput, { target: { files: [txtFile] } });

    expect(documentsApi.attachPdf).not.toHaveBeenCalled();
    expect(onPdfAttached).not.toHaveBeenCalled();
    expect(screen.getByText(/Vui lòng chọn tệp định dạng PDF/i)).toBeInTheDocument();
  });

  it("displays error message when attachPdf fails", async () => {
    vi.mocked(documentsApi.attachPdf).mockRejectedValueOnce(
      new Error("Không thể tải lên tệp PDF. Vui lòng thử lại.")
    );

    render(<AbstractOnlyViewer document={mockDocument} />);

    const file = new File(["%PDF-1.4 test"], "paper.pdf", { type: "application/pdf" });
    const fileInput = screen.getByTestId("pdf-upload-input");

    fireEvent.change(fileInput, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText(/Không thể tải lên tệp PDF/i)).toBeInTheDocument();
    });
  });
});
