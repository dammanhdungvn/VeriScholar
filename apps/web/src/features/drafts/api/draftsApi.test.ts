import { describe, it, expect, vi, beforeEach } from "vitest";
import { draftsApi } from "./draftsApi";

describe("draftsApi", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("creates a draft and captures response with ETag", async () => {
    const mockHeaders = new Headers({
      "Content-Type": "application/json",
      ETag: '"v1"',
    });

    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 201,
      headers: mockHeaders,
      json: async () => ({
        success: true,
        data: {
          id: "draft-1",
          user_id: "user-1",
          title: "Test Draft",
          format: "latex",
          template: "ieee_conference",
          content: "\\documentclass{article}",
          version: 1,
          last_compiled_at: null,
          last_compile_status: null,
          pdf_preview_storage_path: null,
          created_at: "2026-10-04T00:00:00Z",
          updated_at: "2026-10-04T00:00:00Z",
        },
        meta: { request_id: "req-1", timestamp: "2026-10-04T00:00:00Z" },
      }),
    });

    const result = await draftsApi.createDraft({
      title: "Test Draft",
      format: "latex",
    });

    expect(result.data.id).toBe("draft-1");
    expect(result.etag).toBe('"v1"');
  });

  it("sends If-Match header when updating draft content with OCC", async () => {
    const mockHeaders = new Headers({
      "Content-Type": "application/json",
      ETag: '"v2"',
    });

    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: mockHeaders,
      json: async () => ({
        success: true,
        data: {
          id: "draft-1",
          user_id: "user-1",
          title: "Test Draft",
          format: "latex",
          template: "ieee_conference",
          content: "\\documentclass{article}\n% Updated",
          version: 2,
          last_compiled_at: null,
          last_compile_status: null,
          pdf_preview_storage_path: null,
          created_at: "2026-10-04T00:00:00Z",
          updated_at: "2026-10-04T00:00:00Z",
        },
        meta: { request_id: "req-2", timestamp: "2026-10-04T00:00:00Z" },
      }),
    });

    const result = await draftsApi.updateDraftContent(
      "draft-1",
      { content: "\\documentclass{article}\n% Updated" },
      "v1"
    );

    expect(result.data.version).toBe(2);
    expect(result.etag).toBe('"v2"');
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/drafts/draft-1"),
      expect.objectContaining({
        method: "PUT",
        headers: expect.any(Headers),
      })
    );
  });

  it("requests camera-ready export bundle as blob", async () => {
    const mockBlob = new Blob([new Uint8Array([80, 75, 3, 4])], {
      type: "application/zip",
    });

    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Type": "application/zip" }),
      blob: async () => mockBlob,
    });

    const blob = await draftsApi.exportBundle("draft-1", "zip");
    expect(blob.type).toBe("application/zip");
  });
});
