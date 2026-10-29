import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { DocumentTabBar } from "../components/DocumentTabBar";

describe("DocumentTabBar 5-document cap invariant", () => {
  const mockDocs = [
    { id: "doc-1", filename: "paper1.pdf", status: "completed" as const, is_persistent: false, created_at: "" },
    { id: "doc-2", filename: "paper2.pdf", status: "completed" as const, is_persistent: false, created_at: "" },
    { id: "doc-3", filename: "paper3.pdf", status: "completed" as const, is_persistent: false, created_at: "" },
    { id: "doc-4", filename: "paper4.pdf", status: "completed" as const, is_persistent: false, created_at: "" },
    { id: "doc-5", filename: "paper5.pdf", status: "completed" as const, is_persistent: false, created_at: "" },
  ];

  it("renders add button when documents count < 5", () => {
    const onAddDocument = vi.fn();
    render(
      <DocumentTabBar
        documents={mockDocs.slice(0, 3)}
        openDocumentIds={["doc-1", "doc-2", "doc-3"]}
        activeDocumentId="doc-1"
        onSelectDocument={vi.fn()}
        onCloseDocument={vi.fn()}
        onAddDocument={onAddDocument}
      />
    );
    const addBtn = screen.getByRole("button", { name: /Nạp thêm bài báo vào phiên/i });
    expect(addBtn).toBeInTheDocument();
    fireEvent.click(addBtn);
    expect(onAddDocument).toHaveBeenCalledTimes(1);
  });

  it("completely hides add button when documents count >= 5", () => {
    render(
      <DocumentTabBar
        documents={mockDocs}
        openDocumentIds={["doc-1", "doc-2", "doc-3", "doc-4", "doc-5"]}
        activeDocumentId="doc-1"
        onSelectDocument={vi.fn()}
        onCloseDocument={vi.fn()}
        onAddDocument={vi.fn()}
      />
    );
    // Must NOT have any button for adding document or 5-document eviction trigger
    expect(screen.queryByRole("button", { name: /bài báo/i })).not.toBeInTheDocument();
  });

  it("renders tab close button with X icon and hover red style, and does not render star icon on tabs", () => {
    const onCloseDocument = vi.fn();
    render(
      <DocumentTabBar
        documents={mockDocs.slice(0, 2)}
        openDocumentIds={["doc-1", "doc-2"]}
        activeDocumentId="doc-1"
        onSelectDocument={vi.fn()}
        onCloseDocument={onCloseDocument}
        onAddDocument={vi.fn()}
      />
    );
    // Star icon must not be in document tabs
    expect(screen.queryByLabelText(/Lưu bài báo vào thư viện/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/Đã lưu vào thư viện/i)).not.toBeInTheDocument();

    // Close button should have X icon and red hover class
    const closeBtn = screen.getByLabelText("Đóng tab paper1.pdf");
    expect(closeBtn).toBeInTheDocument();
    expect(closeBtn.className).toContain("hover:text-rose-600");
  });
});
