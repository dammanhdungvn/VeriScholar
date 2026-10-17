import {
  apiClient,
  apiClientWithMeta,
  apiClientBlob,
  resolveApiUrl,
  type ApiPaginatedResult,
} from "@/lib/api-client";
import type {
  Draft,
  CreateDraftRequest,
  UpdateDraftRequest,
  VerifyFactsRequest,
  VerifyFactsResponse,
  CompileDraftResponse,
  DraftAssistRequest,
  DraftAssistResponse,
  CreateDraftAssetRequest,
  DraftAsset,
  DraftAssetListResponse,
  DraftShareRequest,
  DraftShareResponse,
  DraftComment,
  CreateDraftCommentRequest,
  UpdateDraftCommentRequest,
  OverleafExportResponse,
  AssociativeSuggestionsResponse,
} from "../types";

export const draftsApi = {
  /**
   * POST /api/v1/drafts
   * Create a new research writing draft.
   */
  async createDraft(request: CreateDraftRequest): Promise<Draft> {
    return apiClient<Draft>("/drafts", {
      method: "POST",
      body: JSON.stringify(request),
    });
  },

  /**
   * GET /api/v1/drafts
   * List paginated research writing drafts for current user.
   */
  async listDrafts(
    page: number = 1,
    perPage: number = 20
  ): Promise<ApiPaginatedResult<Draft>> {
    const searchParams = new URLSearchParams({
      page: String(page),
      per_page: String(perPage),
    });

    const endpoint = `/drafts?${searchParams.toString()}`;
    return apiClientWithMeta<Draft>(endpoint, {
      method: "GET",
    });
  },


  /**
   * GET /api/v1/drafts/{id}
   * Retrieve full draft details by ID.
   */
  async getDraft(id: string): Promise<Draft> {
    return apiClient<Draft>(`/drafts/${id}`, {
      method: "GET",
    });
  },

  /**
   * PUT /api/v1/drafts/{id}
   * Update draft with Optimistic Concurrency Control (OCC).
   */
  async updateDraft(
    id: string,
    request: UpdateDraftRequest,
    ifMatch?: string
  ): Promise<Draft> {
    const etag = ifMatch
      ? ifMatch.startsWith('"')
        ? ifMatch
        : `"${ifMatch}"`
      : `"v${request.version}"`;
    return apiClient<Draft>(`/drafts/${id}`, {
      method: "PUT",
      headers: {
        "If-Match": etag,
      },
      body: JSON.stringify(request),
    });
  },

  /**
   * DELETE /api/v1/drafts/{id}
   * Delete draft permanently.
   */
  async deleteDraft(id: string): Promise<void> {
    return apiClient<void>(`/drafts/${id}`, {
      method: "DELETE",
    });
  },

  /**
   * POST /api/v1/drafts/{id}/verify-facts
   * Trigger 4-stage SAFE fact-checking pipeline.
   */
  async verifyFacts(
    id: string,
    request?: VerifyFactsRequest
  ): Promise<VerifyFactsResponse> {
    return apiClient<VerifyFactsResponse>(`/drafts/${id}/verify-facts`, {
      method: "POST",
      body: JSON.stringify(request || {}),
    });
  },

  /**
   * POST /api/v1/drafts/{id}/compile
   * Trigger sandboxed LaTeX compilation with Agentic self-healing.
   */
  async compileDraft(id: string): Promise<CompileDraftResponse> {
    return apiClient<CompileDraftResponse>(`/drafts/${id}/compile`, {
      method: "POST",
    });
  },

  /**
   * URL for live PDF preview iframe/canvas.
   */
  getPreviewPdfUrl(id: string): string {
    return resolveApiUrl(`/drafts/${id}/preview.pdf`);
  },

  /**
   * GET /api/v1/drafts/{id}/preview.pdf
   * Fetch rendered PDF preview blob.
   */
  async getPreviewPdfBlob(id: string): Promise<Blob> {
    return apiClientBlob(`/drafts/${id}/preview.pdf`);
  },

  /**
   * POST /api/v1/drafts/{id}/assist
   * Request AI writing assist suggestions without directly overwriting the draft.
   */
  async assistDraft(
    id: string,
    request: DraftAssistRequest
  ): Promise<DraftAssistResponse> {
    return apiClient<DraftAssistResponse>(`/drafts/${id}/assist`, {
      method: "POST",
      body: JSON.stringify(request),
    });
  },

  /**
   * POST /api/v1/drafts/{id}:export-bundle
   * Download camera-ready academic submission bundle (.zip).
   */
  async exportBundle(id: string): Promise<Blob> {
    return apiClientBlob(`/drafts/${id}:export-bundle`, {
      method: "POST",
    });
  },

  /**
   * GET /api/v1/drafts/{id}/assets
   * Retrieve list of academic assets associated with the draft.
   */
  async listAssets(id: string): Promise<DraftAssetListResponse> {
    return apiClient<DraftAssetListResponse>(`/drafts/${id}/assets`, {
      method: "GET",
    });
  },

  /**
   * POST /api/v1/drafts/{id}/assets
   * Register or upload a draft asset.
   */
  async createAsset(
    id: string,
    request: CreateDraftAssetRequest
  ): Promise<DraftAsset> {
    return apiClient<DraftAsset>(`/drafts/${id}/assets`, {
      method: "POST",
      body: JSON.stringify(request),
    });
  },

  /**
   * GET /api/v1/drafts/{id}/share
   * Retrieve sharing configuration and collaborator list.
   */
  async getShareSettings(id: string): Promise<DraftShareResponse> {
    return apiClient<DraftShareResponse>(`/drafts/${id}/share`, {
      method: "GET",
    });
  },

  /**
   * POST /api/v1/drafts/{id}/share
   * Configure sharing permissions or invite a collaborator.
   */
  async shareDraft(
    id: string,
    request: DraftShareRequest
  ): Promise<DraftShareResponse> {
    return apiClient<DraftShareResponse>(`/drafts/${id}/share`, {
      method: "POST",
      body: JSON.stringify(request),
    });
  },

  /**
   * GET /api/v1/drafts/{id}/comments
   * Retrieve list of peer review comments.
   */
  async getComments(draftId: string): Promise<DraftComment[]> {
    return apiClient<DraftComment[]>(`/drafts/${draftId}/comments`, {
      method: "GET",
    });
  },

  /**
   * POST /api/v1/drafts/{id}/comments
   * Create a new comment or reply on selected text in draft.
   */
  async createComment(
    draftId: string,
    payload: CreateDraftCommentRequest
  ): Promise<DraftComment> {
    return apiClient<DraftComment>(`/drafts/${draftId}/comments`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * PATCH /api/v1/drafts/{id}/comments/{commentId}
   * Update or resolve comment.
   */
  async updateComment(
    draftId: string,
    commentId: string,
    payload: UpdateDraftCommentRequest
  ): Promise<DraftComment> {
    return apiClient<DraftComment>(`/drafts/${draftId}/comments/${commentId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  /**
   * DELETE /api/v1/drafts/{id}/comments/{commentId}
   * Delete comment permanently.
   */
  async deleteComment(draftId: string, commentId: string): Promise<void> {
    return apiClient<void>(`/drafts/${draftId}/comments/${commentId}`, {
      method: "DELETE",
    });
  },

  /**
   * POST /api/v1/drafts/{id}/overleaf
   * Synchronize draft and retrieve 1-Click Overleaf launch URL.
   */
  async exportToOverleaf(id: string): Promise<OverleafExportResponse> {
    return apiClient<OverleafExportResponse>(`/drafts/${id}/overleaf`, {
      method: "POST",
    });
  },

  /**
   * POST /api/v1/drafts/{id}/associative-suggestions
   * Retrieve proactive scholarly associative memory suggestions based on draft content.
   */
  async getAssociativeSuggestions(
    id: string,
    payload: {
      content?: string;
      text?: string;
      limit?: number;
      min_similarity?: number;
    } = {}
  ): Promise<AssociativeSuggestionsResponse> {
    return apiClient<AssociativeSuggestionsResponse>(
      `/drafts/${id}/associative-suggestions`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    );
  },
};

