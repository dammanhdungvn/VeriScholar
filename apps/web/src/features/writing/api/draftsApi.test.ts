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

  it("triggers SAFE fact-checking via POST /drafts/{id}/verify-facts", async () => {
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Type": "application/json" }),
      json: async () => ({
        success: true,
        data: {
          draft_id: "draft-1",
          verified_text: "Transformers excel.",
          claims: [
            {
              id: "claim-1",
              claim_text: "Transformers excel.",
              normalized_entities: ["Transformer"],
              status: "supported",
              confidence_score: 0.95,
              evidence_text: "Transformers achieve state-of-the-art results.",
              evidence_page: 1,
              evidence_bounding_boxes: [[0.1, 0.2, 0.8, 0.4, 1]],
            },
          ],
          total_claims: 1,
          supported_claims: 1,
          contradicted_claims: 0,
          unverified_claims: 0,
          supported_ratio: 1.0,
          latency_ms: 120,
          verified_at: "2026-10-15T00:00:00Z",
        },
      }),
    });

    const res = await draftsApi.verifyFacts("draft-1", {
      text: "Transformers excel.",
    });

    expect(res.supported_claims).toBe(1);
    expect(res.claims[0].status).toBe("supported");
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

  it("gets and updates draft share settings via GET and POST /drafts/{id}/share", async () => {
    const mockShareData = {
      draft_id: "draft-1",
      share_token: "tok-123",
      share_url: "http://localhost:5173/share/tok-123",
      permission: "editor",
      allow_public_link: true,
      collaborators: [
        {
          email: "collab@mit.edu",
          permission: "editor",
          granted_at: "2026-10-15T00:00:00Z",
        },
      ],
    };

    // 1. GET
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Type": "application/json" }),
      json: async () => ({
        success: true,
        data: mockShareData,
      }),
    });

    const settings = await draftsApi.getShareSettings("draft-1");
    expect(settings.share_token).toBe("tok-123");
    expect(settings.collaborators[0].email).toBe("collab@mit.edu");

    // 2. POST
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Type": "application/json" }),
      json: async () => ({
        success: true,
        data: {
          ...mockShareData,
          collaborators: [
            ...mockShareData.collaborators,
            {
              email: "new@mit.edu",
              permission: "viewer",
              granted_at: "2026-10-15T01:00:00Z",
            },
          ],
        },
      }),
    });

    const updated = await draftsApi.shareDraft("draft-1", {
      target_email: "new@mit.edu",
      permission: "viewer",
    });

    expect(updated.collaborators).toHaveLength(2);
  });

  it("manages peer review comments via GET, POST, PATCH, and DELETE", async () => {
    const mockComment = {
      id: "comm-1",
      draft_id: "draft-1",
      author_id: "user-1",
      author_name: "Dr. Turing",
      start_offset: 10,
      end_offset: 25,
      selected_text: "transformers",
      comment_text: "Please add citation.",
      is_resolved: false,
      created_at: "2026-10-15T00:00:00Z",
      updated_at: "2026-10-15T00:00:00Z",
      replies: [],
    };

    // 1. GET /drafts/{id}/comments
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Type": "application/json" }),
      json: async () => ({
        success: true,
        data: [mockComment],
      }),
    });

    const comments = await draftsApi.getComments("draft-1");
    expect(comments).toHaveLength(1);
    expect(comments[0].comment_text).toBe("Please add citation.");
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/drafts/draft-1/comments"),
      expect.objectContaining({ method: "GET" })
    );

    // 2. POST /drafts/{id}/comments
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 201,
      headers: new Headers({ "Content-Type": "application/json" }),
      json: async () => ({
        success: true,
        data: mockComment,
      }),
    });

    const created = await draftsApi.createComment("draft-1", {
      start_offset: 10,
      end_offset: 25,
      selected_text: "transformers",
      comment_text: "Please add citation.",
    });
    expect(created.id).toBe("comm-1");
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/drafts/draft-1/comments"),
      expect.objectContaining({ method: "POST" })
    );

    // 3. PATCH /drafts/{id}/comments/{commentId}
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Type": "application/json" }),
      json: async () => ({
        success: true,
        data: { ...mockComment, is_resolved: true },
      }),
    });

    const updated = await draftsApi.updateComment("draft-1", "comm-1", {
      is_resolved: true,
    });
    expect(updated.is_resolved).toBe(true);
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/drafts/draft-1/comments/comm-1"),
      expect.objectContaining({ method: "PATCH" })
    );

    // 4. DELETE /drafts/{id}/comments/{commentId}
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 204,
      headers: new Headers({ "Content-Type": "application/json" }),
      json: async () => ({
        success: true,
      }),
    });

    await draftsApi.deleteComment("draft-1", "comm-1");
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/drafts/draft-1/comments/comm-1"),
      expect.objectContaining({ method: "DELETE" })
    );
  });

  it("exports draft to Overleaf via POST /drafts/{id}/overleaf", async () => {
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Type": "application/json" }),
      json: async () => ({
        success: true,
        data: {
          draft_id: "draft-1",
          launch_url: "https://www.overleaf.com/docs?snip_uri=http%3A%2F%2F127.0.0.1%3A8000%2Fapi%2Fv1%2Fdrafts%2Fdraft-1%2Foverleaf-launch",
          project_name: "VeriScholar_Draft_draft-1",
        },
      }),
    });

    const result = await draftsApi.exportToOverleaf("draft-1");
    expect(result.launch_url).toContain("overleaf.com");
    expect(result.draft_id).toBe("draft-1");
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/drafts/draft-1/overleaf"),
      expect.objectContaining({ method: "POST" })
    );
  });

  it("retrieves proactive associative suggestions via POST /drafts/{id}/associative-suggestions", async () => {
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Type": "application/json" }),
      json: async () => ({
        success: true,
        data: {
          draft_id: "draft-1",
          total_found: 1,
          suggestions: [
            {
              note_id: "note-1",
              document_title: "Attention Is All You Need",
              paper_title: "Attention Is All You Need",
              page_number: 4,
              selected_text: "Multi-head attention mechanism",
              user_note: "Breakthrough architecture",
              similarity_score: 0.92,
              suggested_citation: "\\cite{vaswani2017attention}",
              reason: "High lexical similarity with draft content",
              relevance_explanation: "Đoạn văn có các thuật ngữ tương đồng cao",
            },
          ],
        },
      }),
    });

    const result = await draftsApi.getAssociativeSuggestions("draft-1", {
      content: "We propose multi-head attention mechanism.",
      limit: 3,
    });

    expect(result.draft_id).toBe("draft-1");
    expect(result.total_found).toBe(1);
    expect(result.suggestions[0].note_id).toBe("note-1");
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/drafts/draft-1/associative-suggestions"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          content: "We propose multi-head attention mechanism.",
          limit: 3,
        }),
      })
    );
  });
});
