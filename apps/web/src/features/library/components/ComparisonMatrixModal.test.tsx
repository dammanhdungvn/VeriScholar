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

  it("exports matrix as CSV / Excel file with strict RFC 4180 escaping and UTF-8 BOM", async () => {
    let capturedBlobContent = "";

    const originalBlob = globalThis.Blob;
    globalThis.Blob = class MockBlob extends originalBlob {
      constructor(blobParts?: BlobPart[], options?: BlobPropertyBag) {
        super(blobParts, options);
        if (blobParts && blobParts.length > 0) {
          capturedBlobContent = blobParts.map((p) => String(p)).join("");
        }
      }
    };

    const createObjectURLSpy = vi.fn().mockReturnValue("blob:http://localhost/test-uuid");
    const revokeObjectURLSpy = vi.fn();
    window.URL.createObjectURL = createObjectURLSpy;
    window.URL.revokeObjectURL = revokeObjectURLSpy;

    const adversarialRows = [
      {
        document_id: "adv-1",
        title: 'Attention Is "All" You Need: The "Transformer" Era',
        authors: ["Vaswani, Ashish", "Shazeer, Noam"],
        year: 2017,
        core_methodology: "Self-Attention with Q, K, V vectors",
        datasets_used: ["WMT, 2014 En-De", "WMT, 2014 En-Fr"],
        key_metrics: { "F1-Score": "94,2%", BLEU: '28.4 "SOTA"' },
        strengths: ['Highly "parallel" computation', "Eliminates recurrence, convolution"],
        limitations: ["O(n^2) sequence memory\nquadratic bottleneck"],
      },
      {
        document_id: "adv-2",
        title: "Paper with, Commas, and Null Fields",
        authors: undefined,
        year: null,
        core_methodology: "Heuristic, empirical analysis",
        datasets_used: [],
        key_metrics: {},
        strengths: [],
        limitations: [],
      },
    ];

    const mockResponse: ComparisonMatrixResponse = {
      matrix_id: "matrix-adv",
      folder_id: null,
      documents_compared: 2,
      topic: 'Testing "Quotes" & Commas',
      rows: adversarialRows as unknown as ComparisonMatrixResponse["rows"],
      summary_synthesis: "Adversarial synthesis",
      markdown_table: "| Adv |",
      sufficiency: {
        sufficiency_score: 0.9,
        is_sufficient: true,
        analyzed_aspects: [],
        missing_aspects: [],
        recommended_search_queries: [],
        reasoning: "Good",
      },
      generated_at: "2026-10-16T00:00:00Z",
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: mockResponse,
      }),
    });

    renderWithClient(
      <ComparisonMatrixModal isOpen={true} onClose={vi.fn()} />
    );

    const input = screen.getByPlaceholderText(/Cơ chế Attention/i);
    fireEvent.change(input, { target: { value: 'Testing "Quotes" & Commas' } });
    fireEvent.submit(input.closest("form")!);

    await waitFor(() => {
      expect(screen.getByTestId("export-csv-btn")).toBeInTheDocument();
    });

    const exportBtn = screen.getByTestId("export-csv-btn");
    expect(screen.getByText("Xuất CSV / Excel")).toBeInTheDocument();
    fireEvent.click(exportBtn);

    expect(createObjectURLSpy).toHaveBeenCalled();
    expect(revokeObjectURLSpy).toHaveBeenCalledWith("blob:http://localhost/test-uuid");

    // 1. Verify UTF-8 BOM is present at character index 0
    expect(capturedBlobContent.charCodeAt(0)).toBe(0xfeff);

    // 2. Verify Double Quote escaping: inner double quotes become double-double quotes ("")
    expect(capturedBlobContent).toContain('"Attention Is ""All"" You Need: The ""Transformer"" Era"');
    expect(capturedBlobContent).toContain('28.4 ""SOTA""');

    // 3. Verify Comma escaping
    expect(capturedBlobContent).toContain('"Vaswani, Ashish; Shazeer, Noam"');
    expect(capturedBlobContent).toContain('"WMT, 2014 En-De; WMT, 2014 En-Fr"');

    // 4. Verify newline in limitations is safely enclosed
    expect(capturedBlobContent).toContain('"O(n^2) sequence memory\nquadratic bottleneck"');

    // 5. Verify null / undefined fields are exported as empty quotes
    expect(capturedBlobContent).toContain('""');

    globalThis.Blob = originalBlob;
  });

  it("handles 120 simulated papers with strict DOM pagination (pageSize 10, 50) and boundary checks", async () => {
    const totalSimulated = 120;
    const manyRows = Array.from({ length: totalSimulated }, (_, i) => ({
      document_id: `doc-${i + 1}`,
      title: i % 10 === 0 ? `BioASQ Study ${i + 1}` : `Deep Learning Architecture ${i + 1}`,
      authors: [`Author ${i + 1}`, `Co-Author ${i + 1}`],
      year: 2020 + (i % 5),
      core_methodology: `Attention Mechanism Variant ${i + 1}`,
      datasets_used: i % 10 === 0 ? ["BioASQ", "PubMedQA"] : ["WMT-14", "GLUE"],
      key_metrics: { Accuracy: `${85 + (i % 15)}%`, F1: `0.${90 + (i % 9)}` },
      strengths: [`High throughput in pipeline ${i + 1}`],
      limitations: [`Memory footprint scale ${i + 1}`],
    }));

    const mockResponse: ComparisonMatrixResponse = {
      matrix_id: "matrix-120",
      folder_id: null,
      documents_compared: totalSimulated,
      topic: "Large Scale Foundation Models",
      rows: manyRows,
      summary_synthesis: "Synthesizing 120 papers...",
      markdown_table: "| 120 Papers |",
      sufficiency: {
        sufficiency_score: 0.98,
        is_sufficient: true,
        analyzed_aspects: ["Architectures", "Metrics"],
        missing_aspects: [],
        recommended_search_queries: [],
        reasoning: "High sufficiency with 120 empirical papers.",
      },
      generated_at: "2026-10-16T00:00:00Z",
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: mockResponse,
      }),
    });

    const { container } = renderWithClient(
      <ComparisonMatrixModal isOpen={true} onClose={vi.fn()} />
    );

    const input = screen.getByPlaceholderText(/Cơ chế Attention/i);
    fireEvent.change(input, { target: { value: "Large Scale Foundation Models" } });
    fireEvent.submit(input.closest("form")!);

    await waitFor(() => {
      expect(screen.getByText("BioASQ Study 1")).toBeInTheDocument();
    });

    // 1. Verify initial DOM paging: exactly 10 rows in tbody
    const tbodyRows = container.querySelectorAll("tbody tr");
    expect(tbodyRows.length).toBe(10);
    expect(screen.getByText("Trang 1 / 12")).toBeInTheDocument();

    // Verify boundary: Prev button is disabled on Page 1
    const prevBtn = screen.getByTestId("matrix-prev-page");
    const nextBtn = screen.getByTestId("matrix-next-page");
    expect(prevBtn).toBeDisabled();
    expect(nextBtn).not.toBeDisabled();

    // 2. Navigate to Page 2
    fireEvent.click(nextBtn);
    expect(screen.getByText("Trang 2 / 12")).toBeInTheDocument();
    expect(screen.getByText("BioASQ Study 11")).toBeInTheDocument();
    expect(screen.queryByText("BioASQ Study 1")).not.toBeInTheDocument();
    expect(container.querySelectorAll("tbody tr").length).toBe(10);

    // 3. Test changing Page Size to 50
    const pageSizeSelect = screen.getByLabelText("Số dòng mỗi trang");
    fireEvent.change(pageSizeSelect, { target: { value: "50" } });
    expect(screen.getByText("Trang 1 / 3")).toBeInTheDocument();
    expect(container.querySelectorAll("tbody tr").length).toBe(50);

    // 4. Test real-time filtering among 120 papers
    const searchInput = screen.getByTestId("search-matrix-input");
    fireEvent.change(searchInput, { target: { value: "BioASQ" } });
    expect(screen.getByText(/Kết quả lọc:/i)).toBeInTheDocument();
    expect(container.querySelectorAll("tbody tr").length).toBe(12);
    expect(screen.getByText("Trang 1 / 1")).toBeInTheDocument();
  });

  it("disables submit button when topic input is empty or whitespace", () => {
    renderWithClient(
      <ComparisonMatrixModal isOpen={true} onClose={vi.fn()} />
    );

    const submitBtn = screen.getByRole("button", { name: /Sinh Ma Trận Đối Chiếu/i });
    expect(submitBtn).toBeDisabled();

    const input = screen.getByPlaceholderText(/Cơ chế Attention/i);
    fireEvent.change(input, { target: { value: "    " } });
    expect(submitBtn).toBeDisabled();

    fireEvent.change(input, { target: { value: "Empirical Analysis of LLM" } });
    expect(submitBtn).not.toBeDisabled();
  });

  it("displays error alert when synthesis API fails with 500 error", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => ({
        detail: "Hệ thống tổng hợp gặp sự cố máy chủ nội bộ (500).",
      }),
    });

    renderWithClient(
      <ComparisonMatrixModal isOpen={true} onClose={vi.fn()} />
    );

    const input = screen.getByPlaceholderText(/Cơ chế Attention/i);
    fireEvent.change(input, { target: { value: "Faulty Query" } });
    fireEvent.submit(input.closest("form")!);

    await waitFor(() => {
      expect(screen.getByRole("alert")).toBeInTheDocument();
    });
  });
});
