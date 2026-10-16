import { describe, it, expect, vi, beforeEach } from "vitest";
import { documentsApi } from "./documentsApi";
import { fetchEventSource } from "@microsoft/fetch-event-source";

vi.mock("@microsoft/fetch-event-source", () => ({
  fetchEventSource: vi.fn(),
}));

describe("documentsApi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("uploads PDF document with multipart/form-data", async () => {
    const mockFile = new File(["%PDF-1.4 test"], "test_paper.pdf", { type: "application/pdf" });
    const mockResponse = {
      success: true,
      data: {
        id: "doc-123",
        filename: "test_paper.pdf",
        file_size_bytes: 14,
        status: "processing",
        stage: "queued",
      },
      meta: { request_id: "req-1", timestamp: "2026-09-21T00:00:00Z" },
    };

    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 202,
      json: async () => mockResponse,
    });

    const result = await documentsApi.uploadDocument(mockFile, "session-abc");
    expect(result.id).toBe("doc-123");
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/documents"),
      expect.objectContaining({ method: "POST" })
    );
  });

  it("retrieves paginated documents list", async () => {
    const mockPaginated = {
      success: true,
      data: [
        {
          id: "doc-1",
          filename: "paper1.pdf",
          title: "Paper One",
          status: "completed",
          is_persistent: true,
          created_at: "2026-09-21T00:00:00Z",
        },
      ],
      meta: {
        total: 1,
        page: 1,
        per_page: 20,
        total_pages: 1,
        request_id: "req-1",
        timestamp: "2026-09-21T00:00:00Z",
      },
      links: {
        first: "/documents?page=1",
        prev: null,
        self: "/documents?page=1",
        next: null,
        last: "/documents?page=1",
      },
    };

    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockPaginated,
    });

    const result = await documentsApi.listDocuments({ page: 1, per_page: 20 });
    expect(result.data).toHaveLength(1);
    expect(result.data[0].title).toBe("Paper One");
    expect(result.meta.total).toBe(1);
  });

  it("fetches singleton 3-point grounded summary", async () => {
    const mockSummary = {
      success: true,
      data: {
        document_id: "doc-1",
        problem_statement: { text: "Problem A", bounding_boxes: [] },
        contributions: { text: "Contrib B", bounding_boxes: [] },
        limitations: { text: "Limit C", bounding_boxes: [] },
      },
      meta: { request_id: "req-1", timestamp: "2026-09-21T00:00:00Z" },
    };

    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockSummary,
    });

    const result = await documentsApi.getSummary("doc-1");
    expect(result.problem_statement.text).toBe("Problem A");
  });

  it("deletes document with HTTP 204 No Content", async () => {
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 204,
    });

    await expect(documentsApi.deleteDocument("doc-1")).resolves.toBeUndefined();
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/documents/doc-1"),
      expect.objectContaining({ method: "DELETE" })
    );
  });

  it("streamSummary attaches generated X-Request-ID to SSE request", async () => {
    await documentsApi.streamSummary("doc-99", {});

    expect(fetchEventSource).toHaveBeenCalledTimes(1);
    const [url, options] = vi.mocked(fetchEventSource).mock.calls[0];
    expect(url).toContain("/documents/doc-99/summary:stream");
    expect(options?.headers).toBeDefined();
    expect(options?.headers?.["X-Request-ID"]).toBeDefined();
    expect(options?.headers?.["X-Request-ID"]).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
    );
  });

  it("streamDocumentSummary propagates explicit requestId and works as alias", async () => {
    await documentsApi.streamDocumentSummary("doc-99", {}, "trace-summary-req-123");

    const [, options] = vi.mocked(fetchEventSource).mock.calls[0];
    expect(options?.headers?.["X-Request-ID"]).toBe("trace-summary-req-123");
  });

  it("resolves scholarly references via POST /documents/{id}/references:resolve (Module 3)", async () => {
    const mockResolved = [
      {
        ref_index: 1,
        raw_text: "Vaswani et al. Attention is all you need. NeurIPS 2017.",
        title: "Attention Is All You Need",
        authors: ["A. Vaswani", "N. Shazeer"],
        year: 2017,
        arxiv_id: "1706.03762",
        open_access_pdf_url: "https://arxiv.org/pdf/1706.03762.pdf",
        sources: ["arXiv", "Exa"],
        citation_count: 120000,
      },
    ];

    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Type": "application/json" }),
      json: async () => ({
        success: true,
        data: mockResolved,
      }),
    });

    const result = await documentsApi.resolveReferences("doc-123");
    expect(result).toHaveLength(1);
    expect(result[0].title).toBe("Attention Is All You Need");
    expect(result[0].open_access_pdf_url).toContain("arxiv.org");
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/documents/doc-123/references:resolve"),
      expect.objectContaining({ method: "POST" })
    );
  });
});
