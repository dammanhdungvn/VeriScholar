import { describe, it, expect, vi, beforeEach } from "vitest";
import { sessionsApi } from "./sessionsApi";
import { fetchEventSource } from "@microsoft/fetch-event-source";

vi.mock("@microsoft/fetch-event-source", () => ({
  fetchEventSource: vi.fn(),
}));

describe("sessionsApi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
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

  it("sendSessionMessageStream attaches X-Request-ID header to SSE request", async () => {
    await sessionsApi.sendSessionMessageStream(
      "session-1",
      { question: "What is attention?", stream: true },
      {}
    );

    expect(fetchEventSource).toHaveBeenCalledTimes(1);
    const [url, options] = vi.mocked(fetchEventSource).mock.calls[0];
    expect(url).toContain("/sessions/session-1/messages");
    expect(options?.headers).toBeDefined();
    expect(options?.headers?.["X-Request-ID"]).toBeDefined();
    expect(options?.headers?.["X-Request-ID"]).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
    );
  });

  it("sendSessionMessageStream propagates custom requestId when provided", async () => {
    await sessionsApi.sendSessionMessageStream(
      "session-1",
      { question: "Explain transformer", stream: true },
      {},
      "idemp-key-1",
      "custom-trace-req-888"
    );

    const [, options] = vi.mocked(fetchEventSource).mock.calls[0];
    expect(options?.headers?.["X-Request-ID"]).toBe("custom-trace-req-888");
    expect(options?.headers?.["Idempotency-Key"]).toBe("idemp-key-1");
  });
});
