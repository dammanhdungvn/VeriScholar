import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { AcademicMarkdownRenderer } from "../AcademicMarkdownRenderer";
import type { CitationBadgeData } from "@/types/dashboard";

describe("ConceptPillsAndPreview", () => {
  const mockCitations: CitationBadgeData[] = [
    {
      citation_id: "cit_1",
      paper_id: "doc-1",
      paper_title: "Attention Is All You Need",
      page: 3,
      bbox: [0.1, 0.2, 0.8, 0.4, 3],
      concept_name: "Architecture",
      snippet:
        "The Transformer follows this overall architecture using stacked self-attention and point-wise, fully connected layers.",
    },
    {
      citation_id: "cit_2",
      paper_id: "doc-1",
      paper_title: "Attention Is All You Need",
      page: 5,
      bbox: [0.15, 0.25, 0.85, 0.45, 5],
      concept_name: "Multi-Head Attention",
      snippet:
        "Multi-head attention allows the model to jointly attend to information from different representation subspaces.",
    },
  ];

  it("renders concept pills [ ↪ Architecture ] instead of raw [1] [2]", () => {
    // Test explicit concept tag [cite:Architecture]
    const { rerender } = render(
      <AcademicMarkdownRenderer
        content="Mô hình đề xuất kiến trúc mới [cite:Architecture]."
        citations={mockCitations}
      />
    );

    const pill = screen.getByTestId("concept-pill");
    expect(pill).toBeInTheDocument();
    expect(pill.textContent).toContain("↪");
    expect(pill.textContent).toContain("Architecture");
    expect(pill.textContent).toBe("[ ↪ Architecture ]");
    // Ensure raw [1] or raw [cite:...] token is NOT rendered
    expect(screen.queryByText("[1]")).toBeNull();
    expect(screen.queryByText("[cite:Architecture]")).toBeNull();

    // Test numbered citation [1] mapped to semantic concept "Architecture"
    rerender(
      <AcademicMarkdownRenderer
        content="Mô hình đề xuất kiến trúc mới [1]."
        citations={mockCitations}
      />
    );

    const pillMapped = screen.getByTestId("concept-pill");
    expect(pillMapped.textContent).toBe("[ ↪ Architecture ]");
    expect(screen.queryByText("[1]")).toBeNull();
  });

  it("completely removes footer section citation-sources-footer (Nguồn trích dẫn (X))", () => {
    render(
      <AcademicMarkdownRenderer
        content="Kiến trúc mạng [1] và cơ chế [2]."
        citations={mockCitations}
        isStreaming={false}
      />
    );

    // citation-sources-footer must NOT exist
    expect(screen.queryByTestId("citation-sources-footer")).toBeNull();
    expect(screen.queryByText(/Nguồn trích dẫn/)).toBeNull();
  });

  it("hovering over a concept pill renders floating popover preview card with snippet and Page X", () => {
    render(
      <AcademicMarkdownRenderer
        content="Mô hình Transformer [cite:Architecture] mang lại hiệu quả cao."
        citations={mockCitations}
      />
    );

    const pill = screen.getByTestId("concept-pill");
    expect(screen.queryByTestId("concept-preview-popover")).toBeNull();

    // Hover over pill
    fireEvent.mouseEnter(pill);

    const popover = screen.getByTestId("concept-preview-popover");
    expect(popover).toBeInTheDocument();
    // Verifies snippet is displayed
    expect(popover.textContent).toContain(
      "The Transformer follows this overall architecture using stacked self-attention"
    );
    // Verifies Page X badge is displayed
    expect(popover.textContent).toContain("Page 3");

    // Unhover
    fireEvent.mouseLeave(pill);
    expect(screen.queryByTestId("concept-preview-popover")).toBeNull();
  });

  it("clicking concept pill calls onCitationClick with citation data and id", () => {
    const onCitationClick = vi.fn();
    render(
      <AcademicMarkdownRenderer
        content="Mô hình Transformer [cite:Architecture] mang lại hiệu quả cao."
        citations={mockCitations}
        onCitationClick={onCitationClick}
      />
    );

    const pill = screen.getByTestId("concept-pill");
    fireEvent.click(pill);

    expect(onCitationClick).toHaveBeenCalledTimes(1);
    expect(onCitationClick).toHaveBeenCalledWith(
      expect.objectContaining({
        concept_name: "Architecture",
        page: 3,
        citation_id: "cit_1",
      }),
      "cit_1"
    );
  });
});
