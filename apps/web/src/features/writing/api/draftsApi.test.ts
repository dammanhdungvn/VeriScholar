import { describe, it, expect, vi, beforeEach } from "vitest";
import { draftsApi } from "./draftsApi";

describe("draftsApi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("creates draft via POST /drafts", async () => {
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 201,
      headers: new Headers({ "Content-Type": "application/json" }),
      json: async () => ({
        success: true,
        data: {
          id: "draft-1",
          user_id: "user-1",
          title: "New Draft",
          content: "\\begin{document}Hello\\end{document}",
          format: "latex",
          version: 1,
          created_at: "2026-10-15T00:00:00Z",
          updated_at: "2026-10-15T00:00:00Z",
        },
      }),
    });

    const draft = await draftsApi.createDraft({
      title: "New Draft",
      format: "latex",
    });

    expect(draft.id).toBe("draft-1");
    expect(draft.version).toBe(1);
    expect(fetch).toHaveBeenCalledTimes(1);
    const [url, opts] = vi.mocked(fetch).mock.calls[0];
    expect(url).toContain("/drafts");
    expect(opts?.method).toBe("POST");
  });

  it("updates draft with If-Match OCC header via PUT /drafts/{id}", async () => {
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Type": "application/json" }),
      json: async () => ({
        success: true,
        data: {
          id: "draft-1",
          user_id: "user-1",
          title: "Updated Title",
          content: "Updated Content",
          format: "latex",
          version: 2,
          created_at: "2026-10-15T00:00:00Z",
          updated_at: "2026-10-15T01:00:00Z",
        },
      }),
    });

    const draft = await draftsApi.updateDraft("draft-1", {
      title: "Updated Title",
      content: "Updated Content",
      format: "latex",
      version: 1,
    });

    expect(draft.version).toBe(2);
    const [, opts] = vi.mocked(fetch).mock.calls[0];
    expect(opts?.method).toBe("PUT");
    const headers = opts?.headers as Headers;
    expect(headers.get("If-Match")).toBe('"v1"');
  });

  it("exports camera-ready submission bundle ZIP via POST /drafts/{id}:export-bundle", async () => {
    const mockBlob = new Blob(["PK zip dummy"], { type: "application/zip" });
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      blob: async () => mockBlob,
    });

    const blob = await draftsApi.exportBundle("draft-1");
    expect(blob.type).toBe("application/zip");
    const [url, opts] = vi.mocked(fetch).mock.calls[0];
    expect(url).toContain("/drafts/draft-1:export-bundle");
    expect(opts?.method).toBe("POST");
  });

  it("requests AI writing assist suggestions via POST /drafts/{id}/assist", async () => {
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Type": "application/json" }),
      json: async () => ({
        success: true,
        data: {
          draft_id: "draft-1",
          prompt: "Viết tiếp phần mở đầu",
          original_text: "Existing intro",
          suggested_text: "Existing intro with scholarly expansion",
          explanation: "Đã mở rộng phần mở đầu",
          confidence_score: 0.95,
          suggested_at: "2026-10-15T00:00:00Z",
        },
      }),
    });

    const res = await draftsApi.assistDraft("draft-1", {
      prompt: "Viết tiếp phần mở đầu",
      target_selection: "Existing intro",
    });

    expect(res.draft_id).toBe("draft-1");
    expect(res.suggested_text).toContain("scholarly expansion");
    expect(fetch).toHaveBeenCalledTimes(1);
    const [url, opts] = vi.mocked(fetch).mock.calls[0];
    expect(url).toContain("/drafts/draft-1/assist");
    expect(opts?.method).toBe("POST");
  });

  it("lists draft assets via GET /drafts/{id}/assets", async () => {
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Type": "application/json" }),
      json: async () => ({
        success: true,
        data: {
          draft_id: "draft-1",
          items: [
            {
              id: "asset-1",
              draft_id: "draft-1",
              asset_type: "image",
              filename: "fig1.png",
              file_size_bytes: 1234,
              storage_url: "/files/fig1.png",
              created_at: "2026-10-15T00:00:00Z",
            },
          ],
          total: 1,
        },
      }),
    });

    const res = await draftsApi.listAssets("draft-1");
    expect(res.total).toBe(1);
    expect(res.items[0].filename).toBe("fig1.png");
    const [url, opts] = vi.mocked(fetch).mock.calls[0];
    expect(url).toContain("/drafts/draft-1/assets");
    expect(opts?.method).toBe("GET");
  });

  it("creates draft asset via POST /drafts/{id}/assets", async () => {
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 201,
      headers: new Headers({ "Content-Type": "application/json" }),
      json: async () => ({
        success: true,
        data: {
          id: "asset-2",
          draft_id: "draft-1",
          asset_type: "bibtex",
          filename: "refs.bib",
          file_size_bytes: 500,
          storage_url: "/files/refs.bib",
          created_at: "2026-10-15T00:00:00Z",
        },
      }),
    });

    const asset = await draftsApi.createAsset("draft-1", {
      asset_type: "bibtex",
      filename: "refs.bib",
      content_base64: "YmlidGV4IGRhdGE=",
    });

    expect(asset.id).toBe("asset-2");
    expect(asset.filename).toBe("refs.bib");
    const [url, opts] = vi.mocked(fetch).mock.calls[0];
    expect(url).toContain("/drafts/draft-1/assets");
    expect(opts?.method).toBe("POST");
  });

  it("does not expose removed out-of-scope draft API methods", () => {
    expect("verifyFacts" in draftsApi).toBe(false);
    expect("exportToOverleaf" in draftsApi).toBe(false);
    expect("shareDraft" in draftsApi).toBe(false);
    expect("getComments" in draftsApi).toBe(false);
    expect("getAssociativeSuggestions" in draftsApi).toBe(false);
  });
});
