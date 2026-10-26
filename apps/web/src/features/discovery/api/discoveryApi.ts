import { apiClient } from "@/lib/api-client";

export interface ScholarlyPaper {
  title: string;
  authors: string[];
  publication_year: number | null;
  venue?: string | null;
  doi?: string | null;
  arxiv_id?: string | null;
  abstract?: string | null;
  access_status: "open_access_pdf" | "abstract_only";
  pdf_url?: string | null;
}

export interface OpenReadingPayload {
  title: string;
  authors?: string[];
  publication_year?: number | null;
  doi?: string | null;
  arxiv_id?: string | null;
  abstract?: string | null;
  pdf_url?: string | null;
}

export interface OpenReadingResponseData {
  session_id: string;
  document_id: string;
  status: string;
  access_status: string;
}

export const discoveryApi = {
  /**
   * Search academic papers across multi-source scholarly databases (arXiv, S2, Exa).
   */
  async search(query: string, limit = 10): Promise<ScholarlyPaper[]> {
    return apiClient<ScholarlyPaper[]>("/discovery/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query, limit }),
    });
  },

  /**
   * Create an instant reading session from a search result (Zero-to-Reading).
   */
  async openReading(payload: OpenReadingPayload): Promise<OpenReadingResponseData> {
    return apiClient<OpenReadingResponseData>("/discovery/open-reading", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  },
};
