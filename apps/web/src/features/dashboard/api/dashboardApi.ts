import { apiClient } from "@/lib/api-client";
import type {
  SessionItem,
  SessionDetail,
  CreateSessionRequest,
  UpdateSessionTitleRequest,
  AddDocumentToSessionRequest,
  AddDocumentToSessionResponse,
  SessionTurnItem
} from "@/types/dashboard";

/**
 * Dashboard API Service communicating with FastAPI Backend
 */
export const dashboardApi = {
  /**
   * List recent research sessions
   */
  async listSessions(
    page = 1,
    perPage = 20,
    q?: string,
    includeArchived?: boolean
  ): Promise<SessionItem[]> {
    const params = new URLSearchParams({
      page: String(page),
      per_page: String(perPage),
    });
    if (q) params.set("q", q);
    if (includeArchived !== undefined) params.set("include_archived", String(includeArchived));

    const response = await apiClient<SessionItem[] | { items: SessionItem[] }>(
      `/sessions?${params.toString()}`
    );

    if (Array.isArray(response)) {
      return response;
    }
    if (response && Array.isArray((response as { items: SessionItem[] }).items)) {
      return (response as { items: SessionItem[] }).items;
    }
    return [];
  },

  /**
   * Get single session detail with documents and viewport state
   */
  async getSession(id: string): Promise<SessionDetail> {
    return apiClient<SessionDetail>(`/sessions/${id}?include_documents=true`);
  },

  /**
   * Create a new research session
   */
  async createSession(req: CreateSessionRequest = {}): Promise<SessionDetail> {
    return apiClient<SessionDetail>("/sessions", {
      method: "POST",
      body: JSON.stringify(req),
    });
  },

  /**
   * Update session title with Optimistic Concurrency Control (OCC)
   */
  async updateSessionTitle(
    id: string,
    req: UpdateSessionTitleRequest,
    version: number
  ): Promise<SessionDetail> {
    return apiClient<SessionDetail>(`/sessions/${id}`, {
      method: "PATCH",
      headers: {
        "If-Match": `"v${version}"`,
      },
      body: JSON.stringify(req),
    });
  },

  /**
   * Delete research session
   */
  async deleteSession(id: string): Promise<void> {
    return apiClient<void>(`/sessions/${id}`, {
      method: "DELETE",
    });
  },

  /**
   * Add document to session (via document_id or URL)
   */
  async addDocument(
    id: string,
    req: AddDocumentToSessionRequest
  ): Promise<AddDocumentToSessionResponse> {
    return apiClient<AddDocumentToSessionResponse>(`/sessions/${id}/documents`, {
      method: "POST",
      body: JSON.stringify(req),
    });
  },

  /**
   * Get conversation history for a session
   */
  async getMessages(id: string, page = 1, perPage = 50): Promise<SessionTurnItem[]> {
    const response = await apiClient<SessionTurnItem[] | { items: SessionTurnItem[] }>(
      `/sessions/${id}/messages?page=${page}&per_page=${perPage}`
    );
    if (Array.isArray(response)) {
      return response;
    }
    if (response && Array.isArray((response as { items: SessionTurnItem[] }).items)) {
      return (response as { items: SessionTurnItem[] }).items;
    }
    return [];
  },
};
