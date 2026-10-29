import { apiClient } from "@/lib/api-client";
import type {
  GraphQueryRequest,
  GraphQueryResponseData,
  BibliometricsResponseData,
  LibraryGraphResponseData,
} from "../types";

export const libraryApi = {
  /**
   * Dual-level GraphRAG query: micro CTE traversal, macro community summaries, or hybrid
   */
  async queryGraph(payload: GraphQueryRequest): Promise<GraphQueryResponseData> {
    return apiClient<GraphQueryResponseData>("/library/graph:query", {
      method: "POST",
      body: JSON.stringify({
        query: payload.query,
        mode: payload.mode || "hybrid",
        folder_id: payload.folder_id || null,
        top_k: payload.top_k || 5,
      }),
    });
  },

  /**
   * Get Connected Papers bibliometrics analysis for a given folder
   */
  async getFolderBibliometrics(folderId: string): Promise<BibliometricsResponseData> {
    return apiClient<BibliometricsResponseData>(`/folders/${folderId}/bibliometrics`, {
      method: "GET",
    });
  },

  /**
   * Get full personal knowledge graph across user's library (LLM Wiki)
   */
  async getLibraryGraph(folderId?: string | null): Promise<LibraryGraphResponseData> {
    const params = folderId ? `?folder_id=${encodeURIComponent(folderId)}` : "";
    return apiClient<LibraryGraphResponseData>(`/library/graph${params}`, {
      method: "GET",
    });
  },
};
