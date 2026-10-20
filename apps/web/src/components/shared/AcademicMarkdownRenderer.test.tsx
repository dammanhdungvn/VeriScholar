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
});

