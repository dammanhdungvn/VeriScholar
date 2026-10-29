import { apiClient } from "@/lib/api-client";
import type {
  GraphQueryRequest,
  GraphQueryResponseData,
  BibliometricsResponseData,
  LibraryGraphResponseData,
  WikiPageItem,
  ResearchGapsResponseData,
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

  /**
   * List compiled academic wiki pages
   */
  async listWikiPages(): Promise<WikiPageItem[]> {
    const res = await apiClient<{ total: number; pages: WikiPageItem[] } | WikiPageItem[]>("/library/wiki", {
      method: "GET",
    });
    if (Array.isArray(res)) {
      return res;
    }
    return (res as { total: number; pages: WikiPageItem[] })?.pages ?? [];
  },

  /**
   * Get a compiled academic wiki page by slug
   */
  async getWikiPage(slug: string): Promise<WikiPageItem> {
    return apiClient<WikiPageItem>(`/library/wiki/${encodeURIComponent(slug)}`, {
      method: "GET",
    });
  },

  /**
   * Synthesize research gaps across library papers
   */
  async getResearchGaps(folderId?: string | null, topK: number = 5): Promise<ResearchGapsResponseData> {
    return apiClient<ResearchGapsResponseData>("/library/research-gaps", {
      method: "POST",
      body: JSON.stringify({
        folder_id: folderId || null,
        top_k: topK,
      }),
    });
  },
};
