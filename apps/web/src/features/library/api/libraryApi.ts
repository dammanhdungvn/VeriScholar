import { apiClient } from "@/lib/api-client";
import type {
  GraphQueryRequest,
  GraphQueryResponseData,
  BibliometricsResponseData,
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
};
