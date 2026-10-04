import {
  apiClient,
  apiClientWithMeta,
  type ApiPaginatedResult,
} from "@/lib/api-client";
import type {
  FolderItem,
  CreateFolderPayload,
  UpdateFolderPayload,
  BulkImportPayload,
  BulkImportResponse,
  LibrarySynthesizePayload,
  LibrarySynthesizeResponse,
  LibraryComparePayload,
  LibraryCompareResponse,
} from "@/types/library";
import type { DocumentListItem } from "@/types/document";

export const libraryApi = {
  /**
   * GET /api/v1/folders
   * List all research folders with document counts
   */
  async listFolders(): Promise<FolderItem[]> {
    return apiClient<FolderItem[]>("/folders", { method: "GET" });
  },

  /**
   * POST /api/v1/folders
   * Create a new research topic folder
   */
  async createFolder(payload: CreateFolderPayload): Promise<FolderItem> {
    return apiClient<FolderItem>("/folders", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * PATCH /api/v1/folders/{id}
   * Rename or move a folder with cycle breaking
   */
  async updateFolder(id: string, payload: UpdateFolderPayload): Promise<FolderItem> {
    return apiClient<FolderItem>(`/folders/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  /**
   * DELETE /api/v1/folders/{id}
   * Remove folder and detach member documents safely
   */
  async deleteFolder(id: string): Promise<void> {
    return apiClient<void>(`/folders/${id}`, { method: "DELETE" });
  },

  /**
   * GET /api/v1/library/starred
   * List user-starred persistent research papers
   */
  async listStarredDocuments(
    params: { folder_id?: string; page?: number; per_page?: number } = {}
  ): Promise<ApiPaginatedResult<DocumentListItem>> {
    const query = new URLSearchParams();
    if (params.folder_id) query.set("folder_id", params.folder_id);
    if (params.page) query.set("page", params.page.toString());
    if (params.per_page) query.set("per_page", params.per_page.toString());
    const qs = query.toString();
    const endpoint = `/library/starred${qs ? `?${qs}` : ""}`;

    return apiClientWithMeta<DocumentListItem>(endpoint, { method: "GET" });
  },

  /**
   * POST /api/v1/library/import
   * Batch import research papers by DOIs / arXiv IDs
   */
  async bulkImport(payload: BulkImportPayload): Promise<BulkImportResponse> {
    return apiClient<BulkImportResponse>("/library/import", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * POST /api/v1/library/synthesize
   * Hierarchical multi-document RAG synthesis with Sufficiency Verification Gate
   */
  async synthesize(payload: LibrarySynthesizePayload): Promise<LibrarySynthesizeResponse> {
    return apiClient<LibrarySynthesizeResponse>("/library/synthesize", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * POST /api/v1/library/compare
   * Comparative matrix across 2 to 10 research papers
   */
  async compare(payload: LibraryComparePayload): Promise<LibraryCompareResponse> {
    return apiClient<LibraryCompareResponse>("/library/compare", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};
