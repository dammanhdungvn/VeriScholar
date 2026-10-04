import { describe, it, expect, vi, beforeEach } from "vitest";
import { sharesApi } from "./sharesApi";

describe("sharesApi", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("creates a shareable link", async () => {
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 201,
      headers: new Headers({ "Content-Type": "application/json" }),
      json: async () => ({
        success: true,
        data: {
          share_token: "shr_abc123",
          resource_type: "document",
          resource_id: "doc-1",
          permission: "read_only",
          share_url: "/shares/shr_abc123",
          expires_at: null,
          created_at: "2026-10-04T00:00:00Z",
        },
        meta: { request_id: "req-1", timestamp: "2026-10-04T00:00:00Z" },
      }),
    });

    const result = await sharesApi.createShare({
      resource_type: "document",
      resource_id: "doc-1",
    });

    expect(result.share_token).toBe("shr_abc123");
    expect(result.permission).toBe("read_only");
  });

  it("revokes an active share link", async () => {
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 204,
      headers: new Headers(),
    });

    await expect(sharesApi.revokeShare("shr_abc123")).resolves.toBeUndefined();
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/shares/shr_abc123"),
      expect.objectContaining({ method: "DELETE" })
    );
  });
});
