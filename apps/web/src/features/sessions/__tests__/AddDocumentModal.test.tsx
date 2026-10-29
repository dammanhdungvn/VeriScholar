import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { AddDocumentModal } from "../components/AddDocumentModal";
import type { DocumentListItem } from "@/types/document";

describe("AddDocumentModal", () => {
  const mockLibraryDocs: any[] = [
    {
      id: "doc-1",
      title: "Attention Is All You Need.pdf",
      filename: "Attention Is All You Need.pdf",
      status: "completed",
      is_persistent: true,
      created_at: "2026-10-25T00:00:00Z",
      updated_at: "2026-10-25T00:00:00Z",
    },
    {
      id: "doc-2",
      title: "Attention Is All You Need",
      filename: "attention.pdf",
      status: "completed",
      is_persistent: true,
      created_at: "2026-10-25T00:00:00Z",
      updated_at: "2026-10-25T00:00:00Z",
    },
    {
      id: "doc-3",
      title: "Temporary Scratch Paper",
      filename: "scratch.pdf",
      status: "completed",
      is_persistent: false, // Temporary session upload, should NOT appear in Library tab
      created_at: "2026-10-25T00:00:00Z",
      updated_at: "2026-10-25T00:00:00Z",
    },
    {
      id: "doc-4",
      title: "Selective Attention Improves Transformer",
      filename: "selective.pdf",
      status: "completed",
      is_persistent: true,
      created_at: "2026-10-25T00:00:00Z",
      updated_at: "2026-10-25T00:00:00Z",
    },
  ];

  it("deduplicates papers with identical normalized titles and filters out non-persistent docs", () => {
    render(
      <AddDocumentModal
        isOpen={true}
        onClose={vi.fn()}
        availableLibraryDocs={mockLibraryDocs as DocumentListItem[]}
        currentDocumentIds={[]}
        onAddByDocumentId={vi.fn()}
        onAddByUrl={vi.fn()}
      />
    );

    // Attention Is All You Need should only appear once (doc-1, doc-2 deduplicated)
    const attentionCards = screen.getAllByText(/Attention Is All You Need/i);
    expect(attentionCards.length).toBe(1);

    // Selective Attention should be in the document
    expect(screen.getByText("Selective Attention Improves Transformer")).toBeInTheDocument();

    // Temporary Scratch Paper with is_persistent = false should NOT be in the document
    expect(screen.queryByText("Temporary Scratch Paper")).toBeNull();
  });

  it("renders 3 tabs including 'Tải lên PDF' and allows uploading local PDF file", async () => {
    const handleAddByFile = vi.fn().mockResolvedValue(undefined);

    render(
      <AddDocumentModal
        isOpen={true}
        onClose={vi.fn()}
        availableLibraryDocs={mockLibraryDocs as DocumentListItem[]}
        currentDocumentIds={[]}
        onAddByDocumentId={vi.fn()}
        onAddByUrl={vi.fn()}
        onAddByFile={handleAddByFile}
      />
    );

    // Tab 1: Thư viện, Tab 2: Tải lên PDF, Tab 3: Đường dẫn (URL)
    const uploadTabBtn = screen.getByRole("button", { name: /Tải lên PDF/i });
    expect(uploadTabBtn).toBeInTheDocument();

    fireEvent.click(uploadTabBtn);

    const fileInput = screen.getByTestId("session-pdf-file-input");
    expect(fileInput).toBeInTheDocument();

    const pdfFile = new File(["dummy pdf bytes"], "quantum_transformers.pdf", {
      type: "application/pdf",
    });

    fireEvent.change(fileInput, { target: { files: [pdfFile] } });

    await waitFor(() => {
      expect(handleAddByFile).toHaveBeenCalledWith(pdfFile);
    });
  });
});
