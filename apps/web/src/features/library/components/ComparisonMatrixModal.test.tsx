import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ComparisonMatrixModal } from "./ComparisonMatrixModal";
import type { ComparisonMatrixResponse } from "../types";

function renderWithClient(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      {ui}
    </QueryClientProvider>
  );
}

describe("ComparisonMatrixModal Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockMatrixResult: ComparisonMatrixResponse = {
    matrix_id: "matrix-1",
    folder_id: null,
    documents_compared: 2,
    topic: "Transformer Scaling",
    rows: [
      {
        document_id: "doc-1",
        title: "Attention Is All You Need",
        authors: ["Vaswani et al."],
        year: 2017,
        core_methodology: "Multi-Head Self-Attention",
        datasets_used: ["WMT 2014 En-De", "WMT 2014 En-Fr"],
        key_metrics: { BLEU: "28.4" },
        strengths: ["Highly parallel"],
        limitations: ["O(n^2) sequence memory"],
      },
      {
        document_id: "doc-2",
        title: "FlashAttention: Fast and Memory-Efficient Exact Attention",
        authors: ["Tri Dao et al."],
        year: 2022,
        core_methodology: "IO-Aware Tiling & Recomputation",
        datasets_used: ["Long-range Arena", "GPT-2 Benchmark"],
        key_metrics: { Speedup: "3x" },
        strengths: ["IO-Aware"],
        limitations: ["Requires GPU SRAM hardware support"],
      },
    ],
    summary_synthesis: "Kiến trúc Attention và các tối ưu hóa phần cứng IO-Aware.",
    markdown_table: "| Paper | Method |\n| Attention | Transformer |\n| FlashAttention | Tiling |",
    sufficiency: {
      sufficiency_score: 0.94,
      is_sufficient: true,
      analyzed_aspects: [],
      missing_aspects: [],
      recommended_search_queries: [],
      reasoning: "Các bài báo cung cấp đầy đủ bức tranh từ kiến trúc nền tảng đến kỹ thuật tối ưu phần cứng.",
    },
    generated_at: "2026-10-16T00:00:00Z",
  };

  it("does not render when isOpen is false", () => {
    renderWithClient(
      <ComparisonMatrixModal isOpen={false} onClose={vi.fn()} />
    );
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("renders input form and generates comparison matrix", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: mockMatrixResult,
      }),
    });

    renderWithClient(
      <ComparisonMatrixModal isOpen={true} onClose={vi.fn()} />
    );

    expect(screen.getByRole("dialog", { name: "Ma trận so sánh đối chiếu học thuật" })).toBeInTheDocument();
    expect(screen.getByText("Tổng hợp & So sánh Đa Bài báo Tự động")).toBeInTheDocument();

    const input = screen.getByPlaceholderText(/Cơ chế Attention/i);
    fireEvent.change(input, { target: { value: "Transformer Scaling" } });
    fireEvent.submit(input.closest("form")!);

    // Should now display the matrix results table
    await waitFor(() => {
      expect(screen.getByText("Attention Is All You Need")).toBeInTheDocument();
      expect(screen.getByText("FlashAttention: Fast and Memory-Efficient Exact Attention")).toBeInTheDocument();
    });

    // Verify Sufficiency Gate score
    expect(screen.getByText(/ĐỦ DẪN CHỨNG \(94%\)/i)).toBeInTheDocument();
  });

  it("switches tabs between Table and Markdown view and copies markdown", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: mockMatrixResult,
      }),
    });

    const writeTextSpy = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, {
      clipboard: { writeText: writeTextSpy },
    });

    renderWithClient(
      <ComparisonMatrixModal isOpen={true} onClose={vi.fn()} />
    );

    const input = screen.getByPlaceholderText(/Cơ chế Attention/i);
    fireEvent.change(input, { target: { value: "Transformer Scaling" } });
    fireEvent.submit(input.closest("form")!);

    await waitFor(() => {
      expect(screen.getByText("Attention Is All You Need")).toBeInTheDocument();
    });

    // Click tab Markdown
    const markdownTab = screen.getByText("Mã nguồn Markdown");
    fireEvent.click(markdownTab);

    expect(screen.getByText(/Sao chép bảng/i)).toBeInTheDocument();

    // Click copy button
    const copyBtn = screen.getByText(/Sao chép bảng/i);
    fireEvent.click(copyBtn);

    expect(writeTextSpy).toHaveBeenCalledWith(mockMatrixResult.markdown_table);
  });

  it("calls onClose when close button is clicked", () => {
    const onClose = vi.fn();
    renderWithClient(
      <ComparisonMatrixModal isOpen={true} onClose={onClose} />
    );

    const closeBtn = screen.getByRole("button", { name: "Đóng ma trận đối chiếu" });
    fireEvent.click(closeBtn);

    expect(onClose).toHaveBeenCalled();
  });
});
