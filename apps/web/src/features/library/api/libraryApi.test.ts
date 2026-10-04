import { describe, it, expect, vi, beforeEach } from "vitest";
import { libraryApi } from "./libraryApi";

describe("libraryApi", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("lists folders with document counts", async () => {
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Type": "application/json" }),
      json: async () => ({
        success: true,
        data: [
          {
            id: "f-1",
            name: "Machine Learning",
            parent_id: null,
            document_count: 5,
            created_at: "2026-10-04T00:00:00Z",
            updated_at: "2026-10-04T00:00:00Z",
          },
        ],
        meta: { request_id: "req-1", timestamp: "2026-10-04T00:00:00Z" },
      }),
    });

    const folders = await libraryApi.listFolders();
    expect(folders).toHaveLength(1);
    expect(folders[0].name).toBe("Machine Learning");
    expect(folders[0].document_count).toBe(5);
  });

  it("queues bulk import of papers by DOIs", async () => {
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Type": "application/json" }),
      json: async () => ({
        success: true,
        data: {
          batch_id: "batch-1",
          total_items: 2,
          accepted_identifiers: ["10.1145/3308558.3313562", "1706.03762"],
          status: "queued",
          message: "Queued 2 papers",
        },
        meta: { request_id: "req-2", timestamp: "2026-10-04T00:00:00Z" },
      }),
    });

    const res = await libraryApi.bulkImport({
      identifiers: ["10.1145/3308558.3313562", "1706.03762"],
    });

    expect(res.batch_id).toBe("batch-1");
    expect(res.accepted_identifiers).toHaveLength(2);
  });

  it("triggers multi-paper synthesis with Sufficiency Verification Gate", async () => {
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Type": "application/json" }),
      json: async () => ({
        success: true,
        data: {
          answer: "Transformer achieves state-of-the-art results.",
          retrieval_tier_reached: "tier_1_smart_notes",
          sufficiency_score: 0.95,
          sources: [
            {
              document_id: "doc-1",
              title: "Attention Is All You Need",
              page_number: 1,
              bounding_boxes: [[0.1, 0.2, 0.9, 0.3, 1]],
            },
          ],
        },
        meta: { request_id: "req-3", timestamp: "2026-10-04T00:00:00Z" },
      }),
    });

    const res = await libraryApi.synthesize({
      query: "How does Transformer perform?",
    });

    expect(res.sufficiency_score).toBe(0.95);
    expect(res.sources[0].page_number).toBe(1);
  });
});
