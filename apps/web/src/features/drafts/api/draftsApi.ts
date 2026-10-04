import {
  apiClient,
  apiClientWithHeaders,
  apiClientWithMeta,
  apiClientBlob,
  resolveApiUrl,
  type ApiResponseWithHeaders,
  type ApiPaginatedResult,
} from "@/lib/api-client";
import { AUTH_TOKEN_STORAGE_KEY } from "@/features/auth/stores/useAuthStore";
import type {
  CreateDraftPayload,
  UpdateDraftContentPayload,
  PatchDraftPayload,
  DraftItem,
  CompileDraftPayload,
  CreateDraftCommentPayload,
  DraftCommentItem,
  VerifyClaimsPayload,
  VerifyClaimsResponse,
} from "@/types/draft";

function normalizeIfMatchHeader(etag: string): string {
  const trimmed = etag.trim();
  if (trimmed.startsWith('"') && trimmed.endsWith('"')) {
    return trimmed;
  }
  return `"${trimmed}"`;
}

export const draftsApi = {
  /**
   * POST /api/v1/drafts
   * Create a new academic draft
   */
  async createDraft(payload: CreateDraftPayload): Promise<ApiResponseWithHeaders<DraftItem>> {
    return apiClientWithHeaders<DraftItem>("/drafts", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * GET /api/v1/drafts
   * List drafts owned by current user with pagination
   */
  async listDrafts(params: { page?: number; per_page?: number } = {}): Promise<ApiPaginatedResult<DraftItem>> {
    const query = new URLSearchParams();
    if (params.page) query.set("page", params.page.toString());
    if (params.per_page) query.set("per_page", params.per_page.toString());
    const qs = query.toString();
    const endpoint = `/drafts${qs ? `?${qs}` : ""}`;

    return apiClientWithMeta<DraftItem>(endpoint, { method: "GET" });
  },

  /**
   * GET /api/v1/drafts/{id}
   * Get draft detail with current OCC ETag
   */
  async getDraft(id: string): Promise<ApiResponseWithHeaders<DraftItem>> {
    return apiClientWithHeaders<DraftItem>(`/drafts/${id}`, { method: "GET" });
  },

  /**
   * PUT /api/v1/drafts/{id}
   * Update full draft content guarded by OCC If-Match header
   */
  async updateDraftContent(
    id: string,
    payload: UpdateDraftContentPayload,
    ifMatchEtag: string
  ): Promise<ApiResponseWithHeaders<DraftItem>> {
    return apiClientWithHeaders<DraftItem>(`/drafts/${id}`, {
      method: "PUT",
      headers: {
        "If-Match": normalizeIfMatchHeader(ifMatchEtag),
      },
      body: JSON.stringify(payload),
    });
  },

  /**
   * PATCH /api/v1/drafts/{id}
   * Update draft metadata with optional OCC If-Match header
   */
  async patchDraft(
    id: string,
    payload: PatchDraftPayload,
    ifMatchEtag?: string
  ): Promise<ApiResponseWithHeaders<DraftItem>> {
    const headers: Record<string, string> = {};
    if (ifMatchEtag) {
      headers["If-Match"] = normalizeIfMatchHeader(ifMatchEtag);
    }
    return apiClientWithHeaders<DraftItem>(`/drafts/${id}`, {
      method: "PATCH",
      headers,
      body: JSON.stringify(payload),
    });
  },

  /**
   * DELETE /api/v1/drafts/{id}
   * Remove draft
   */
  async deleteDraft(id: string): Promise<void> {
    return apiClient<void>(`/drafts/${id}`, { method: "DELETE" });
  },

  /**
   * POST /api/v1/drafts/{id}:compile
   * SSE Stream for LaTeX compilation with agentic self-healing
   */
  compileDraftStream(
    id: string,
    payload: CompileDraftPayload,
    callbacks: {
      onMessage: (event: string, data: unknown) => void;
      onError?: (error: Error) => void;
      onComplete?: () => void;
    }
  ): AbortController {
    const controller = new AbortController();
    const url = resolveApiUrl(`/drafts/${id}:compile`);

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    };

    if (typeof window !== "undefined") {
      const token = localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }
    }

    fetch(url, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok || !response.body) {
          throw new Error(`SSE stream connection failed: HTTP ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const parts = buffer.split("\n\n");
          buffer = parts.pop() || "";

          for (const part of parts) {
            const lines = part.split("\n");
            let eventName = "message";
            let dataStr = "";

            for (const line of lines) {
              if (line.startsWith("event:")) {
                eventName = line.replace("event:", "").trim();
              } else if (line.startsWith("data:")) {
                dataStr = line.replace("data:", "").trim();
              }
            }

            if (dataStr) {
              try {
                callbacks.onMessage(eventName, JSON.parse(dataStr));
              } catch {
                callbacks.onMessage(eventName, dataStr);
              }
            }
          }
        }
        callbacks.onComplete?.();
      })
      .catch((err) => {
        if (err.name !== "AbortError") {
          callbacks.onError?.(err);
        }
      });

    return controller;
  },

  /**
   * GET /api/v1/drafts/{id}/preview-pdf
   * Stream compiled PDF preview
   */
  async getPreviewPdf(id: string): Promise<Blob> {
    return apiClientBlob(`/drafts/${id}/preview-pdf`);
  },

  /**
   * POST /api/v1/drafts/{id}:verify-claims
   * Run 4-stage SAFE Fact-Checking on selected text
   */
  async verifyClaims(id: string, payload: VerifyClaimsPayload): Promise<VerifyClaimsResponse> {
    return apiClient<VerifyClaimsResponse>(`/drafts/${id}:verify-claims`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * POST /api/v1/drafts/{id}/comments
   * Add a peer review line comment
   */
  async createComment(id: string, payload: CreateDraftCommentPayload): Promise<DraftCommentItem> {
    return apiClient<DraftCommentItem>(`/drafts/${id}/comments`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * GET /api/v1/drafts/{id}/comments
   * List peer review comments for the draft
   */
  async listComments(
    id: string,
    params: { page?: number; per_page?: number } = {}
  ): Promise<ApiPaginatedResult<DraftCommentItem>> {
    const query = new URLSearchParams();
    if (params.page) query.set("page", params.page.toString());
    if (params.per_page) query.set("per_page", params.per_page.toString());
    const qs = query.toString();
    const endpoint = `/drafts/${id}/comments${qs ? `?${qs}` : ""}`;

    return apiClientWithMeta<DraftCommentItem>(endpoint, { method: "GET" });
  },

  /**
   * GET /api/v1/drafts/{id}/bundle
   * Export camera-ready submission bundle (.zip or .pdf)
   */
  async exportBundle(id: string, format: "zip" | "pdf" = "zip"): Promise<Blob> {
    return apiClientBlob(`/drafts/${id}/bundle?format=${format}`);
  },
};
