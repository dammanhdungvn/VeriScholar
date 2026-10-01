import { describe, it, expect, vi, beforeEach } from "vitest";
import { sessionsApi } from "./sessionsApi";

describe("sessionsApi", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("creates session with initial documents and receives ETag", async () => {
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
          id: "session-1",
          title: "Session One",
          document_ids: ["doc-1"],
          viewport_state: { page: 1, zoom_ratio: 1, scroll_top: 0 },
          active_tab: "chat",
          is_archived: false,
          version: 1,
          created_at: "2026-09-21T00:00:00Z",
          updated_at: "2026-09-21T00:00:00Z",
        },
        meta: { request_id: "req-1", timestamp: "2026-09-21T00:00:00Z" },
      }),
    });

    const result = await sessionsApi.createSession({
      title: "Session One",
      initial_document_ids: ["doc-1"],
    });

    expect(result.data.id).toBe("session-1");
    expect(result.etag).toBe('"v1"');
  });

  it("updates viewport with OCC If-Match header", async () => {
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
          id: "session-1",
          title: "Session One",
          document_ids: ["doc-1"],
          viewport_state: { page: 3, zoom_ratio: 1.25, scroll_top: 150 },
          active_tab: "notes",
          is_archived: false,
          version: 2,
          created_at: "2026-09-21T00:00:00Z",
          updated_at: "2026-09-21T00:00:00Z",
        },
        meta: { request_id: "req-1", timestamp: "2026-09-21T00:00:00Z" },
      }),
    });

    const result = await sessionsApi.updateSessionViewport(
      "session-1",
      {
        viewport_state: { page: 3, zoom_ratio: 1.25, scroll_top: 150 },
        active_tab: "notes",
      },
      "v1"
    );

    expect(result.data.viewport_state.page).toBe(3);
    expect(result.etag).toBe('"v2"');
  });

  it("exports session bundle as binary zip blob", async () => {
    const mockBlob = new Blob(["PK zip binary test data"], { type: "application/zip" });

    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      blob: async () => mockBlob,
    });

    const result = await sessionsApi.exportSessionBundle("session-1");
    expect(result.type).toBe("application/zip");
  });
});
