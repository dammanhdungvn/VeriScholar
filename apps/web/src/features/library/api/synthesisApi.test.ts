import { describe, it, expect, vi, beforeEach } from "vitest";
import { synthesisApi } from "./synthesisApi";
import type { ComparisonMatrixResponse } from "../types";

describe("synthesisApi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockResponse: ComparisonMatrixResponse = {
    matrix_id: "matrix-1",
    folder_id: null,
    topic: "Attention Mechanisms",
    documents_compared: 2,
    rows: [
      {
        document_id: "doc-1",
        title: "Attention Is All You Need",
        authors: ["Vaswani et al."],
        year: 2017,
        core_methodology: "Transformer Self-Attention",
        datasets_used: ["WMT 2014 En-De"],
        key_metrics: { BLEU: "28.4" },
        strengths: ["Highly parallel"],
        limitations: ["Quadratic memory complexity"],
      },
    ],
    summary_synthesis: "Transformer Attention Analysis",
    markdown_table: "| Title | Core Method |\n| Attention | Transformer |",
    sufficiency: {
      sufficiency_score: 0.95,
      is_sufficient: true,
      analyzed_aspects: ["Attention", "Scaling"],
      missing_aspects: [],
      recommended_search_queries: [],
      reasoning: "Comprehensive literature coverage",
    },
    generated_at: "2026-10-16T00:00:00Z",
  };

  it("generates global literature comparison matrix", async () => {
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: mockResponse,
        meta: { request_id: "req-matrix-1", timestamp: "2026-10-16T00:00:00Z" },
      }),
    });

    const result = await synthesisApi.generateComparisonMatrix({
      topic: "Attention Mechanisms",
    });

    expect(result.topic).toBe("Attention Mechanisms");
    expect(result.rows).toHaveLength(1);
    expect(result.sufficiency.is_sufficient).toBe(true);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/folders/comparison-matrix"),
      expect.objectContaining({ method: "POST" })
    );
  });

  it("generates folder-scoped literature comparison matrix", async () => {
    const mockFolderResponse: ComparisonMatrixResponse = {
      ...mockResponse,
      topic: "Vision Transformers",
      documents_compared: 1,
    };

    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: mockFolderResponse,
        meta: { request_id: "req-matrix-2", timestamp: "2026-10-16T00:00:00Z" },
      }),
    });

    const result = await synthesisApi.generateFolderComparisonMatrix("folder-42", {
      topic: "Vision Transformers",
    });

    expect(result.documents_compared).toBe(1);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/folders/folder-42/comparison-matrix"),
      expect.objectContaining({ method: "POST" })
    );
  });

  it("executes 2-Tier Hierarchical RAG query", async () => {
    const mockRAG = {
      answer: "Hierarchical RAG synthesis result",
      thought: "Thinking trace...",
      tier_used: "tier1_notes",
      notes_retrieved_count: 2,
      chunks_retrieved_count: 0,
      sufficiency: {
        sufficiency_score: 0.9,
        is_sufficient: true,
        analyzed_aspects: [],
        missing_aspects: [],
        recommended_search_queries: [],
        reasoning: "High confidence notes found",
      },
      citations: [
        {
          citation_id: "c-1",
          document_id: "doc-1",
          document_title: "Attention",
          page_number: 1,
          source: "curated_note",
        },
      ],
    };

    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: mockRAG,
        meta: { request_id: "req-rag-1", timestamp: "2026-10-16T00:00:00Z" },
      }),
    });

    const result = await synthesisApi.hierarchicalRagQuery({
      query: "How does multi-head attention work?",
      folder_id: "folder-1",
    });

    expect(result.answer).toContain("Hierarchical RAG");
    expect(result.citations).toHaveLength(1);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/folders/synthesis"),
      expect.objectContaining({ method: "POST" })
    );
  });
});
