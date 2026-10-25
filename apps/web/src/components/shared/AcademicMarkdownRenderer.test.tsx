import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { AcademicMarkdownRenderer } from "./AcademicMarkdownRenderer";

describe("AcademicMarkdownRenderer", () => {
  it("renders markdown headings, lists, bold and italic text cleanly", () => {
    const markdown = `
## Tóm tắt bài báo Attention Is All You Need
- Mục tiêu: **Transformer** architecture
- Cơ chế *self-attention* hiệu quả
`;

    render(<AcademicMarkdownRenderer content={markdown} />);

    expect(
      screen.getByRole("heading", { level: 2, name: /Tóm tắt bài báo Attention Is All You Need/i })
    ).toBeInTheDocument();
    expect(screen.getByText("Transformer")).toBeInTheDocument();
    expect(screen.getByText("self-attention")).toBeInTheDocument();
  });

  it("renders inline and block math via MathRenderer", () => {
    const mathContent = `
Công thức Attention được tính như sau:
$$
\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V
$$
với độ phức tạp $O(n^2)$.
`;

    const { container } = render(<AcademicMarkdownRenderer content={mathContent} />);

    // Block math has class containing text-center / katex
    expect(container.querySelector(".katex-display, .katex, [data-testid='math-block']")).toBeDefined();
    expect(screen.getByText(/với độ phức tạp/i)).toBeInTheDocument();
  });

  it("renders interactive citation chips and responds to clicks", () => {
    const onCitationClick = vi.fn();
    const content = "Mô hình Transformer được giới thiệu [^cit_1] và hoàn thiện tại [cit_2] cùng [^cit-encoder] và [^3].";

    render(
      <AcademicMarkdownRenderer
        content={content}
        onCitationClick={onCitationClick}
      />
    );

    const cit1Btn = screen.getByRole("button", { name: /\[cit_1\]/i });
    const cit2Btn = screen.getByRole("button", { name: /\[cit_2\]/i });
    const citEncBtn = screen.getByRole("button", { name: /\[cit-encoder\]/i });
    const cit3Btn = screen.getByRole("button", { name: /\[3\]/i });

    expect(cit1Btn).toBeInTheDocument();
    expect(cit2Btn).toBeInTheDocument();
    expect(citEncBtn).toBeInTheDocument();
    expect(cit3Btn).toBeInTheDocument();

    fireEvent.click(cit1Btn);
    expect(onCitationClick).toHaveBeenCalledWith("cit_1");

    fireEvent.click(cit2Btn);
    expect(onCitationClick).toHaveBeenCalledWith("cit_2");

    fireEvent.click(citEncBtn);
    expect(onCitationClick).toHaveBeenCalledWith("cit-encoder");

    fireEvent.click(cit3Btn);
    expect(onCitationClick).toHaveBeenCalledWith("3");
  });

  it("applies Claude typography classes: Serif headings, 1.55 line height, and humanist body", () => {
    const markdown = `# Tiêu đề chính
Đây là đoạn văn bản phân tích theo chuẩn Claude.
> Trích dẫn học thuật Socratic`;

    const { container } = render(<AcademicMarkdownRenderer content={markdown} />);

    const h1 = screen.getByRole("heading", { level: 1 });
    expect(h1).toHaveClass("font-serif");

    const p = screen.getByText(/Đây là đoạn văn bản/i);
    expect(p).toHaveClass("leading-[1.55]");

    const blockquote = container.querySelector("blockquote");
    expect(blockquote).toBeInTheDocument();
    expect(blockquote).toHaveClass("border-l-2");
  });

  it("sanitizes broken [^\\text{cit}] artifacts cleanly without rendering raw LaTeX markup", () => {
    const rawContent =
      "Tuy nhiên, vì đoạn công thức này không xuất hiện trong tài liệu đã cung cấp, tôi chưa thể gắn thẻ trích dẫn [^\\text{cit}] một cách hợp lệ.";

    const { container } = render(<AcademicMarkdownRenderer content={rawContent} />);

    expect(container.textContent).not.toContain("[^\\text{cit}]");
    expect(container.textContent).not.toContain("\\text{cit}");
    expect(screen.getByText(/tôi chưa thể gắn thẻ trích dẫn một cách hợp lệ/i)).toBeInTheDocument();
  });

  it("converts [^\\text{cit_1}] to numbered [1] and links to bounding box", () => {
    const onCitationClick = vi.fn();
    const mockCitations = [
      {
        citation_id: "cit_1",
        paper_id: "doc-attention",
        paper_title: "Attention Is All You Need",
        page: 7,
        bbox: [0.1, 0.2, 0.8, 0.4, 7] as [number, number, number, number, number],
      },
    ];

    const content = "Cơ chế Scaled Dot-Product Attention [^\\text{cit_1}] rất hiệu quả.";

    render(
      <AcademicMarkdownRenderer
        content={content}
        citations={mockCitations}
        onCitationClick={onCitationClick}
      />
    );

    const badge = screen.getByRole("button", { name: /^\[1\]$/ });
    expect(badge).toBeInTheDocument();
    expect(badge.textContent).toBe("[1]");

    fireEvent.click(badge);
    expect(onCitationClick).toHaveBeenCalledWith(mockCitations[0], "1");
  });

  it("renders numbered citations [1], [2] and links to bounding box", () => {
    const onCitationClick = vi.fn();
    const mockCitations = [
      {
        citation_id: "cit_1",
        paper_id: "doc-1",
        paper_title: "Attention Is All You Need",
        page: 3,
        bbox: [0.1, 0.2, 0.8, 0.4, 3] as [number, number, number, number, number],
      },
      {
        citation_id: "cit_2",
        paper_id: "doc-1",
        paper_title: "Attention Is All You Need",
        page: 7,
        bbox: [0.2, 0.3, 0.7, 0.5, 7] as [number, number, number, number, number],
      },
    ];

    const content = "Mô hình Self-Attention [1] kết hợp Multi-Head [2].";

    render(
      <AcademicMarkdownRenderer
        content={content}
        citations={mockCitations}
        onCitationClick={onCitationClick}
      />
    );

    const badge1 = screen.getByRole("button", { name: /^\[1\]$/ });
    const badge2 = screen.getByRole("button", { name: /^\[2\]$/ });

    expect(badge1).toBeInTheDocument();
    expect(badge2).toBeInTheDocument();
    expect(badge1.textContent).toBe("[1]");
    expect(badge2.textContent).toBe("[2]");

    fireEvent.click(badge1);
    expect(onCitationClick).toHaveBeenCalledWith(mockCitations[0], "1");

    fireEvent.click(badge2);
    expect(onCitationClick).toHaveBeenCalledWith(mockCitations[1], "2");

    // References footer should be displayed
    const footer = screen.getByTestId("citation-sources-footer");
    expect(footer).toBeInTheDocument();
    expect(screen.getByText("Nguồn trích dẫn (2)")).toBeInTheDocument();

    const footerItems = screen.getAllByTestId("citation-source-item");
    expect(footerItems).toHaveLength(2);

    fireEvent.click(footerItems[0]);
    expect(onCitationClick).toHaveBeenCalledWith(mockCitations[0], "cit_1");
  });

  it("does not render spurious citations when content does not cite any sources", () => {
    const mockCitations = [
      {
        citation_id: "cit_1",
        paper_id: "doc-1",
        paper_title: "Attention Is All You Need",
        page: 3,
        bbox: [0.1, 0.2, 0.8, 0.4, 3] as [number, number, number, number, number],
      },
    ];

    const content = "Đoạn công thức này không xuất hiện trong tài liệu đã cung cấp.";

    render(
      <AcademicMarkdownRenderer
        content={content}
        citations={mockCitations}
      />
    );

    expect(screen.queryByTestId("citation-badge")).not.toBeInTheDocument();
    expect(screen.queryByTestId("citation-sources-footer")).not.toBeInTheDocument();
  });
});

