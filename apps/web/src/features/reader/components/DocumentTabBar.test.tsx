import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { DocumentTabBar } from "./DocumentTabBar";
import type { DocumentListItem } from "@/types/document";

describe("DocumentTabBar Component", () => {
  const mockDocs: DocumentListItem[] = [
    {
      id: "doc-1",
      filename: "paper1.pdf",
      title: "Attention Is All You Need",
      status: "completed",
      is_persistent: false,
      created_at: "2026-09-21T00:00:00Z",
    },
    {
      id: "doc-2",
      filename: "paper2.pdf",
      title: "BERT Pre-training",
      status: "completed",
      is_persistent: true,
      created_at: "2026-09-21T00:00:00Z",
    },
  ];

  it("renders tabs for all open documents with active document highlighted", () => {
    const onSelect = vi.fn();
    const onClose = vi.fn();
    const onAdd = vi.fn();

    render(
      <DocumentTabBar
        documents={mockDocs}
        openDocumentIds={["doc-1", "doc-2"]}
        activeDocumentId="doc-1"
        onSelectDocument={onSelect}
        onCloseDocument={onClose}
        onAddDocument={onAdd}
      />
    );

    expect(screen.getByText("Attention Is All You Need")).toBeInTheDocument();
    expect(screen.getByText("BERT Pre-training")).toBeInTheDocument();

    const activeTab = screen.getByRole("tab", { selected: true });
    expect(activeTab).toHaveTextContent("Attention Is All You Need");
  });

  it("calls onSelectDocument when clicking an inactive tab", () => {
    const onSelect = vi.fn();

    render(
      <DocumentTabBar
        documents={mockDocs}
        openDocumentIds={["doc-1", "doc-2"]}
        activeDocumentId="doc-1"
        onSelectDocument={onSelect}
        onCloseDocument={vi.fn()}
        onAddDocument={vi.fn()}
      />
    );

    fireEvent.click(screen.getByText("BERT Pre-training"));
    expect(onSelect).toHaveBeenCalledWith("doc-2");
  });

  it("calls onAddDocument when clicking plus button", () => {
    const onAdd = vi.fn();

    render(
      <DocumentTabBar
        documents={mockDocs}
        openDocumentIds={["doc-1"]}
        activeDocumentId="doc-1"
        onSelectDocument={vi.fn()}
        onCloseDocument={vi.fn()}
        onAddDocument={onAdd}
      />
    );

    const addBtn = screen.getByRole("button", { name: /nạp thêm bài báo/i });
    fireEvent.click(addBtn);
    expect(onAdd).toHaveBeenCalled();
  });
});
