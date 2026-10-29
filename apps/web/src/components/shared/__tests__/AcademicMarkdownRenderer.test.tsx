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

  it("does not render citation-sources-footer after streaming finishes (footers eliminated)", () => {
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

    expect(screen.queryByTestId("citation-sources-footer")).toBeNull();
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

  it("does not render legacy footer even when multiple references are present", () => {
    const mockCitations = Array.from({ length: 8 }, (_, idx) => ({
      citation_id: `cit_${idx + 1}`,
      paper_id: `doc-${idx + 1}`,
      page: idx + 1,
      paper_title: `Paper ${idx + 1}`,
      bbox: [0.1, 0.2, 0.8, 0.4, idx + 1] as [number, number, number, number, number],
    }));

    render(
      <AcademicMarkdownRenderer
        content="Testing all references [1], [2], [3], [4], [5], [6], [7]."
        citations={mockCitations}
        isStreaming={false}
      />
    );

    expect(screen.queryByTestId("citation-sources-footer")).toBeNull();
  });

  it("renders ungrounded literature reference numbers as plain text and eliminates ghost citation badge buttons", () => {
    const mockCitations = [
      {
        citation_id: "cit_1",
        paper_id: "doc-1",
        page: 2,
        paper_title: "Attention Is All You Need",
        bbox: [0.1, 0.2, 0.8, 0.4, 2] as [number, number, number, number, number],
      },
    ];

    render(
      <AcademicMarkdownRenderer
        content="Các mô hình LSTM [13] và GRU [7] được trích dẫn trong văn bản [1]."
        citations={mockCitations}
        isStreaming={false}
      />
    );

    // Only grounded citation should be rendered as an interactive concept pill button
    const pills = screen.getAllByTestId("concept-pill");
    expect(pills.length).toBe(1);
    expect(pills[0].textContent).toBe("[ ↪ Attention Is All You Need ]");

    // [13] and [7] should be present as text in the document, but NOT as buttons
    expect(screen.getByText(/LSTM \[13\]/)).toBeDefined();
    expect(screen.getByText(/GRU \[7\]/)).toBeDefined();
    expect(screen.queryByRole("button", { name: "[13]" })).toBeNull();
    expect(screen.queryByRole("button", { name: "[7]" })).toBeNull();
  });
});
