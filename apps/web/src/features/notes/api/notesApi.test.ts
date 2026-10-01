import { describe, it, expect, vi, beforeEach } from "vitest";
import { notesApi } from "./notesApi";
import { ApiError } from "@/lib/api-client";

describe("notesApi", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("creates a note and captures response with ETag", async () => {
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
          id: "note-1",
          selected_text: "Attention is all you need",
          page_number: 1,
          bounding_boxes: [],
          tags: ["core"],
          frozen_snapshot: {},
          is_source_detached: false,
          version: 1,
          created_at: "2026-09-21T00:00:00Z",
          updated_at: "2026-09-21T00:00:00Z",
        },
        meta: { request_id: "req-1", timestamp: "2026-09-21T00:00:00Z" },
      }),
    });

    const result = await notesApi.createNote({
      selected_text: "Attention is all you need",
      page_number: 1,
      tags: ["core"],
    });

    expect(result.data.id).toBe("note-1");
    expect(result.etag).toBe('"v1"');
  });

  it("sends If-Match header when updating note with OCC", async () => {
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
          id: "note-1",
          selected_text: "Attention is all you need",
          user_note: "Updated note text",
          page_number: 1,
          bounding_boxes: [],
          tags: ["core", "verified"],
          frozen_snapshot: {},
          is_source_detached: false,
          version: 2,
          created_at: "2026-09-21T00:00:00Z",
          updated_at: "2026-09-21T00:00:00Z",
        },
        meta: { request_id: "req-1", timestamp: "2026-09-21T00:00:00Z" },
      }),
    });

    const result = await notesApi.updateNote("note-1", { user_note: "Updated note text" }, "v1");
    expect(result.data.version).toBe(2);
    expect(result.etag).toBe('"v2"');

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/notes/note-1"),
      expect.objectContaining({
        headers: expect.any(Headers),
      })
    );
  });

  it("throws ApiError with HTTP 412 when OCC conflict occurs", async () => {
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: false,
      status: 412,
      statusText: "Precondition Failed",
      json: async () => ({
        success: false,
        error: {
          code: "CONCURRENCY_CONFLICT",
          message: "Note version conflict",
        },
        meta: { request_id: "req-err", timestamp: "2026-09-21T00:00:00Z" },
      }),
    });

    await expect(
      notesApi.updateNote("note-1", { user_note: "Conflict text" }, "v1")
    ).rejects.toThrow(ApiError);
  });

  it("calls synthesize notes endpoint with mode", async () => {
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: {
          id: "synth-1",
          title: "Synthesized Lesson",
          mode: "concept_lesson",
          language: "vi",
          markdown_content: "# Lesson content",
          interactive_badges: [],
          source_note_ids: ["note-1"],
          created_at: "2026-09-21T00:00:00Z",
          updated_at: "2026-09-21T00:00:00Z",
        },
        meta: { request_id: "req-1", timestamp: "2026-09-21T00:00:00Z" },
      }),
    });

    const result = await notesApi.synthesizeNotes({
      note_ids: ["note-1"],
      mode: "concept_lesson",
    });

    expect(result.title).toBe("Synthesized Lesson");
  });
});
