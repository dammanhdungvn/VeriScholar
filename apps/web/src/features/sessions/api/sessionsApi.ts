import {
  apiClient,
  apiClientWithHeaders,
  apiClientWithMeta,
  resolveApiUrl,
  generateRequestId,
  type ApiResponseWithHeaders,
  type ApiPaginatedResult,
} from "@/lib/api-client";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { AUTH_TOKEN_STORAGE_KEY } from "@/features/auth/stores/useAuthStore";
import type {
  SessionCreateRequest,
  SessionResponseData,
  SessionHistoryItem,
  SessionUpdateViewportRequest,
  SessionAddDocumentRequest,
  SessionChatMessageRequest,
  SessionTurnItem,
  CitationItemSchema,
  SessionIngestResponse,
} from "@/types/session";

export interface ListSessionsParams {
  page?: number;
  per_page?: number;
  include_archived?: boolean;
}

export interface ListSessionMessagesParams {
  page?: number;
  per_page?: number;
}

export interface StreamEventCallbacks {
  onStart?: (data: { turn_id: string; message_id: string; created_at: string }) => void;
  onCitations?: (citations: CitationItemSchema[]) => void;
  onReasoning?: (thought: string) => void;
  onToken?: (token: string) => void;
  onDone?: (data: { turn_id: string; message_id: string; total_tokens: number; finish_reason: string }) => void;
  onError?: (error: Error) => void;
  signal?: AbortSignal;
}

function normalizeIfMatchHeader(etag: string): string {
  const trimmed = etag.trim();
  if (trimmed.startsWith('"') && trimmed.endsWith('"')) {
    return trimmed;
  }
  return `"${trimmed}"`;
}

export const sessionsApi = {
  /**
   * 45. POST /api/v1/sessions
   * Khởi tạo phiên nghiên cứu đa bài mới (Research Session)
   */
  async createSession(
    data: SessionCreateRequest = {},
    idempotencyKey?: string
  ): Promise<ApiResponseWithHeaders<SessionResponseData>> {
    const headers: Record<string, string> = {};
    if (idempotencyKey) {
      headers["Idempotency-Key"] = idempotencyKey;
    }

    return apiClientWithHeaders<SessionResponseData>("/sessions", {
      method: "POST",
      headers,
      body: JSON.stringify(data),
    });
  },

  /**
   * 46. GET /api/v1/sessions
   * Lấy lịch sử các phiên nghiên cứu (Sidebar History)
   */
  async listSessions(params: ListSessionsParams = {}): Promise<ApiPaginatedResult<SessionHistoryItem>> {
    const query = new URLSearchParams();
    if (params.page !== undefined) query.set("page", String(params.page));
    if (params.per_page !== undefined) query.set("per_page", String(params.per_page));
    if (params.include_archived !== undefined) query.set("include_archived", String(params.include_archived));

    const queryString = query.toString();
    const endpoint = queryString ? `/sessions?${queryString}` : "/sessions";
    return apiClientWithMeta<SessionHistoryItem>(endpoint);
  },

  /**
   * 47. GET /api/v1/sessions/{id}
   * Khôi phục nguyên vẹn phiên nghiên cứu (Snapshots, Tabs, Viewport)
   */
  async getSessionDetail(sessionId: string): Promise<ApiResponseWithHeaders<SessionResponseData>> {
    return apiClientWithHeaders<SessionResponseData>(`/sessions/${sessionId}`);
  },

  /**
   * 48. PATCH /api/v1/sessions/{id}
   * Cập nhật tiêu đề phiên nghiên cứu (Kiểm soát đồng thời OCC If-Match)
   */
  async updateSessionMetadata(
    sessionId: string,
    title: string,
    etag: string
  ): Promise<ApiResponseWithHeaders<SessionResponseData>> {
    return apiClientWithHeaders<SessionResponseData>(`/sessions/${sessionId}`, {
      method: "PATCH",
      headers: {
        "If-Match": normalizeIfMatchHeader(etag),
      },
      body: JSON.stringify({ title }),
    });
  },

  /**
   * 49. PATCH /api/v1/sessions/{id}/viewport
   * Tự động lưu vị trí cuộn trang PDF và Tab đang mở (OCC)
   */
  async updateSessionViewport(
    sessionId: string,
    data: SessionUpdateViewportRequest,
    etag: string
  ): Promise<ApiResponseWithHeaders<SessionResponseData>> {
    return apiClientWithHeaders<SessionResponseData>(`/sessions/${sessionId}/viewport`, {
      method: "PATCH",
      headers: {
        "If-Match": normalizeIfMatchHeader(etag),
      },
      body: JSON.stringify(data),
    });
  },

  /**
   * 50. DELETE /api/v1/sessions/{id}
   * Xóa phiên nghiên cứu
   */
  async deleteSession(sessionId: string): Promise<void> {
    return apiClient<void>(`/sessions/${sessionId}`, {
      method: "DELETE",
    });
  },

  /**
   * 51. POST /api/v1/sessions/{id}/documents
   * Nạp bài vào phiên (Pure JSON: source_type 'url' hoặc 'document_id')
   */
  async addDocumentToSession(
    sessionId: string,
    data: SessionAddDocumentRequest
  ): Promise<SessionResponseData> {
    return apiClient<SessionResponseData>(`/sessions/${sessionId}/documents`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  /**
   * 52. POST /api/v1/sessions/{id}/messages
   * Gửi câu hỏi & Stream SSE (Cross-Document Namespacing)
   */
  async sendSessionMessageStream(
    sessionId: string,
    data: SessionChatMessageRequest,
    callbacks: StreamEventCallbacks,
    idempotencyKey?: string,
    requestId?: string
  ): Promise<void> {
    const url = resolveApiUrl(`/sessions/${sessionId}/messages`);
    const finalRequestId = generateRequestId(requestId);
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      "X-Request-ID": finalRequestId,
    };

    if (idempotencyKey) {
      headers["Idempotency-Key"] = idempotencyKey;
    }

    if (typeof window !== "undefined") {
      try {
        const token = localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
        if (token) {
          headers.Authorization = `Bearer ${token}`;
        }
      } catch {
        // Ignore localStorage errors
      }
    }

    await fetchEventSource(url, {
      method: "POST",
      headers,
      body: JSON.stringify({ ...data, stream: true }),
      signal: callbacks.signal,
      async onopen(response) {
        if (!response.ok) {
          throw new Error(`SSE Connection failed with HTTP ${response.status}`);
        }
      },
      onmessage(event) {
        if (!event.data) return;

        try {
          const parsed = JSON.parse(event.data);
          switch (event.event) {
            case "start":
              callbacks.onStart?.(parsed);
              break;
            case "citations":
              callbacks.onCitations?.(parsed.citations || []);
              break;
            case "reasoning":
              callbacks.onReasoning?.(parsed.thought || "");
              break;
            case "token":
              callbacks.onToken?.(parsed.token || "");
              break;
            case "done":
              callbacks.onDone?.(parsed);
              break;
            default:
              if (parsed.token) {
                callbacks.onToken?.(parsed.token);
              }
              break;
          }
        } catch {
          // Fallback plain text token if not JSON
          if (event.event === "token" || !event.event) {
            callbacks.onToken?.(event.data);
          }
        }
      },
      onerror(err) {
        callbacks.onError?.(err instanceof Error ? err : new Error(String(err)));
        throw err; // Stop reconnecting on hard error
      },
    });
  },

  /**
   * 53. GET /api/v1/sessions/{id}/messages
   * Lấy lịch sử hội thoại của phiên (phân trang)
   */
  async listSessionMessages(
    sessionId: string,
    params: ListSessionMessagesParams = {}
  ): Promise<ApiPaginatedResult<SessionTurnItem>> {
    const query = new URLSearchParams();
    if (params.page !== undefined) query.set("page", String(params.page));
    if (params.per_page !== undefined) query.set("per_page", String(params.per_page));

    const queryString = query.toString();
    const endpoint = queryString ? `/sessions/${sessionId}/messages?${queryString}` : `/sessions/${sessionId}/messages`;
    return apiClientWithMeta<SessionTurnItem>(endpoint);
  },

  /**
   * 54. DELETE /api/v1/sessions/{id}/messages
   * Xóa lịch sử hội thoại của phiên (Idempotent 204)
   */
  async clearSessionMessages(sessionId: string): Promise<void> {
    return apiClient<void>(`/sessions/${sessionId}/messages`, {
      method: "DELETE",
    });
  },

  /**
   * 55. POST /api/v1/sessions/{id}:restore-archived
   * Tải lại file PDF gốc để kích hoạt lại phiên quá hạn TTL 30 ngày
   */
  async restoreArchivedSession(
    sessionId: string,
    file: File
  ): Promise<ApiResponseWithHeaders<SessionResponseData>> {
    const formData = new FormData();
    formData.append("file", file);

    return apiClientWithHeaders<SessionResponseData>(`/sessions/${sessionId}:restore-archived`, {
      method: "POST",
      body: formData,
    });
  },

  /**
   * 56. POST /api/v1/sessions/{id}/references:ingest
   * Nạp các bài báo tham khảo Open-Access vào phiên đọc sâu (Giới hạn tối đa 5 bài) (Module 3)
   */
  async ingestReferences(
    sessionId: string,
    documentId: string,
    refIndices: number[]
  ): Promise<SessionIngestResponse> {
    return apiClient<SessionIngestResponse>(
      `/sessions/${sessionId}/references:ingest`,
      {
        method: "POST",
        body: JSON.stringify({
          document_id: documentId,
          selected_ref_indices: refIndices,
        }),
      }
    );
  },
};
