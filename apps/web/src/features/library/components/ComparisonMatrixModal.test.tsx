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

  it("filters matrix rows by method/keyword and resets filter", async () => {
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

    const topicInput = screen.getByPlaceholderText(/Cơ chế Attention/i);
    fireEvent.change(topicInput, { target: { value: "Transformer Scaling" } });
    fireEvent.submit(topicInput.closest("form")!);

    await waitFor(() => {
      expect(screen.getByText("Attention Is All You Need")).toBeInTheDocument();
      expect(screen.getByText("FlashAttention: Fast and Memory-Efficient Exact Attention")).toBeInTheDocument();
    });

    // Search for "FlashAttention"
    const searchInput = screen.getByTestId("search-matrix-input");
    fireEvent.change(searchInput, { target: { value: "FlashAttention" } });

    expect(screen.queryByText("Attention Is All You Need")).not.toBeInTheDocument();
    expect(screen.getByText("FlashAttention: Fast and Memory-Efficient Exact Attention")).toBeInTheDocument();

    // Clear search
    const clearBtn = screen.getByRole("button", { name: "Xóa bộ lọc" });
    fireEvent.click(clearBtn);

    expect(screen.getByText("Attention Is All You Need")).toBeInTheDocument();
    expect(screen.getByText("FlashAttention: Fast and Memory-Efficient Exact Attention")).toBeInTheDocument();
  });

  it("exports matrix as CSV / Excel file when clicking Xuất CSV / Excel button", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: mockMatrixResult,
      }),
    });

    const createObjectURLSpy = vi.fn().mockReturnValue("blob:http://localhost/test-uuid");
    const revokeObjectURLSpy = vi.fn();
    window.URL.createObjectURL = createObjectURLSpy;
    window.URL.revokeObjectURL = revokeObjectURLSpy;

    renderWithClient(
      <ComparisonMatrixModal isOpen={true} onClose={vi.fn()} />
    );

    const topicInput = screen.getByPlaceholderText(/Cơ chế Attention/i);
    fireEvent.change(topicInput, { target: { value: "Transformer Scaling" } });
    fireEvent.submit(topicInput.closest("form")!);

    await waitFor(() => {
      expect(screen.getByTestId("export-csv-btn")).toBeInTheDocument();
    });

    const exportBtn = screen.getByTestId("export-csv-btn");
    expect(screen.getByText("Xuất CSV / Excel")).toBeInTheDocument();
    fireEvent.click(exportBtn);

    expect(createObjectURLSpy).toHaveBeenCalled();
    expect(revokeObjectURLSpy).toHaveBeenCalledWith("blob:http://localhost/test-uuid");
  });

  it("paginates large-scale matrix rows and handles page navigation", async () => {
    // Generate 25 rows
    const manyRows = Array.from({ length: 25 }, (_, i) => ({
      document_id: `doc-${i + 1}`,
      title: `Paper Title ${i + 1}`,
      authors: [`Author ${i + 1}`],
      year: 2020 + (i % 5),
      core_methodology: `Methodology ${i + 1}`,
      datasets_used: [`Dataset ${i + 1}`],
      key_metrics: { Accuracy: `${80 + i}%` },
      strengths: [`Strength ${i + 1}`],
      limitations: [`Limitation ${i + 1}`],
    }));

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: {
          ...mockMatrixResult,
          documents_compared: 25,
          rows: manyRows,
        },
      }),
    });

    renderWithClient(
      <ComparisonMatrixModal isOpen={true} onClose={vi.fn()} />
    );

    const topicInput = screen.getByPlaceholderText(/Cơ chế Attention/i);
    fireEvent.change(topicInput, { target: { value: "Large Scale Survey" } });
    fireEvent.submit(topicInput.closest("form")!);

    await waitFor(() => {
      expect(screen.getByText("Paper Title 1")).toBeInTheDocument();
      expect(screen.getByText("Paper Title 10")).toBeInTheDocument();
      // Page size is 10, so row 11 should not be on page 1
      expect(screen.queryByText("Paper Title 11")).not.toBeInTheDocument();
    });

    expect(screen.getByText("Trang 1 / 3")).toBeInTheDocument();

    // Click Next page
    const nextBtn = screen.getByTestId("matrix-next-page");
    fireEvent.click(nextBtn);

    expect(screen.getByText("Paper Title 11")).toBeInTheDocument();
    expect(screen.getByText("Paper Title 20")).toBeInTheDocument();
    expect(screen.queryByText("Paper Title 1")).not.toBeInTheDocument();
    expect(screen.getByText("Trang 2 / 3")).toBeInTheDocument();

    // Click Prev page
    const prevBtn = screen.getByTestId("matrix-prev-page");
    fireEvent.click(prevBtn);

    expect(screen.getByText("Paper Title 1")).toBeInTheDocument();
    expect(screen.getByText("Trang 1 / 3")).toBeInTheDocument();
  });
});
