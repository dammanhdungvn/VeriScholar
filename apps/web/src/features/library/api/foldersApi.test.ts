import { describe, it, expect, vi, beforeEach } from "vitest";
import { foldersApi } from "./foldersApi";

describe("foldersApi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("lists all user folders", async () => {
    const mockData = [
      {
        id: "folder-1",
        user_id: "user-1",
        name: "Deep Learning",
        parent_id: null,
        color: "#6366f1",
        document_count: 5,
        subfolder_count: 1,
        created_at: "2026-10-16T00:00:00Z",
        updated_at: "2026-10-16T00:00:00Z",
      },
    ];

    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: mockData,
        meta: { request_id: "req-1", timestamp: "2026-10-16T00:00:00Z" },
      }),
    });

    const result = await foldersApi.listFolders();
    expect(result).toHaveLength(1);
    expect(result[0].name).toBe("Deep Learning");
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/folders"),
      expect.objectContaining({ method: "GET" })
    );
  });

  it("retrieves hierarchical folder tree", async () => {
    const mockTree = [
      {
        id: "folder-1",
        name: "NLP",
        parent_id: null,
        color: "#6366f1",
        document_count: 3,
        subfolders: [
          {
            id: "folder-2",
            name: "Transformers",
            parent_id: "folder-1",
            color: "#cc785c",
            document_count: 2,
            subfolders: [],
          },
        ],
      },
    ];

    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: mockTree,
        meta: { request_id: "req-2", timestamp: "2026-10-16T00:00:00Z" },
      }),
    });

    const result = await foldersApi.getFolderTree();
    expect(result).toHaveLength(1);
    expect(result[0].subfolders).toHaveLength(1);
    expect(result[0].subfolders[0].name).toBe("Transformers");
  });

  it("creates a new folder", async () => {
    const payload = {
      name: "Computer Vision",
      color: "#10b981",
      description: "CV research papers",
    };

    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 201,
      json: async () => ({
        success: true,
        data: {
          id: "folder-3",
          user_id: "user-1",
          name: "Computer Vision",
          parent_id: null,
          color: "#10b981",
          description: "CV research papers",
          document_count: 0,
          subfolder_count: 0,
          created_at: "2026-10-16T00:00:00Z",
          updated_at: "2026-10-16T00:00:00Z",
        },
      }),
    });

    const result = await foldersApi.createFolder(payload);
    expect(result.id).toBe("folder-3");
    expect(result.name).toBe("Computer Vision");
  });

  it("updates folder properties", async () => {
    const updatePayload = { name: "Renamed Vision", color: "#f59e0b" };

    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: {
          id: "folder-3",
          user_id: "user-1",
          name: "Renamed Vision",
          parent_id: null,
          color: "#f59e0b",
          document_count: 0,
          subfolder_count: 0,
          created_at: "2026-10-16T00:00:00Z",
          updated_at: "2026-10-16T00:00:00Z",
        },
      }),
    });

    const result = await foldersApi.updateFolder("folder-3", updatePayload);
    expect(result.name).toBe("Renamed Vision");
  });

  it("deletes folder safely", async () => {
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: { status: "deleted", folder_id: "folder-3" },
      }),
    });

    const result = await foldersApi.deleteFolder("folder-3");
    expect(result.status).toBe("deleted");
  });

  it("assigns and removes documents to folder", async () => {
    // Assign
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: { assigned_count: 2 },
      }),
    });

    const assignRes = await foldersApi.assignDocuments("folder-1", {
      document_ids: ["doc-1", "doc-2"],
    });
    expect(assignRes.assigned_count).toBe(2);

    // Remove
    globalThis.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: { removed_count: 2 },
      }),
    });

    const removeRes = await foldersApi.removeDocuments("folder-1", {
      document_ids: ["doc-1", "doc-2"],
    });
    expect(removeRes.removed_count).toBe(2);
  });
});
