import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { AcademicMarkdownRenderer } from "../AcademicMarkdownRenderer";
import { TypingWaveIndicator } from "../TypingWaveIndicator";

describe("TypingWaveIndicator", () => {
  it("renders 3 bouncing dots with staggered animation", () => {
    render(<TypingWaveIndicator />);
    const indicator = screen.getByTestId("typing-wave-indicator");
    expect(indicator).toBeInTheDocument();
    expect(indicator.children).toHaveLength(3);
  });
});

describe("AcademicMarkdownRenderer isStreaming caret", () => {
  it("renders typing caret when isStreaming is true", () => {
    render(<AcademicMarkdownRenderer content="AI is drafting this response..." isStreaming={true} />);
    const caret = screen.getByTestId("typing-caret");
    expect(caret).toBeInTheDocument();
  });

  it("does not render typing caret when isStreaming is false", () => {
    render(<AcademicMarkdownRenderer content="AI finished drafting." isStreaming={false} />);
    expect(screen.queryByTestId("typing-caret")).toBeNull();
  });

  it("does not render citation-sources-footer while streaming", () => {
    const mockCitations = [
      {
        citation_id: "cit_1",
        paper_id: "doc-1",
        page: 1,
        paper_title: "Paper One",
        bbox: [0.1, 0.2, 0.8, 0.4, 1] as [number, number, number, number, number],
      },
    ];

    render(
      <AcademicMarkdownRenderer
        content="Đang suy luận và trích dẫn theo tài liệu [1]..."
        citations={mockCitations}
        isStreaming={true}
      />
    );

    expect(screen.queryByTestId("citation-sources-footer")).toBeNull();
  });

  it("renders citation-sources-footer only after streaming finishes", () => {
    const mockCitations = [
      {
        citation_id: "cit_1",
        paper_id: "doc-1",
        page: 1,
        paper_title: "Paper One",
        bbox: [0.1, 0.2, 0.8, 0.4, 1] as [number, number, number, number, number],
      },
    ];

    render(
      <AcademicMarkdownRenderer
        content="Đã trả lời xong theo tài liệu [1]."
        citations={mockCitations}
        isStreaming={false}
      />
    );

    expect(screen.getByTestId("citation-sources-footer")).toBeInTheDocument();
  });

  it("does not dump citations when text has no inline citation tokens", () => {
    const mockCitations = [
      {
        citation_id: "cit_1",
        paper_id: "doc-1",
        page: 1,
        paper_title: "Paper One",
        bbox: [0.1, 0.2, 0.8, 0.4, 1] as [number, number, number, number, number],
      },
      {
        citation_id: "cit_2",
        paper_id: "doc-2",
        page: 2,
        paper_title: "Paper Two",
        bbox: [0.1, 0.2, 0.8, 0.4, 2] as [number, number, number, number, number],
      },
    ];

    render(
      <AcademicMarkdownRenderer
        content="Không tìm thấy thông tin của mục này trong tài liệu."
        citations={mockCitations}
        isStreaming={false}
      />
    );

    expect(screen.queryByTestId("citation-sources-footer")).toBeNull();
  });
});
