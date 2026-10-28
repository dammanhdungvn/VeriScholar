import { fetchEventSource } from "@microsoft/fetch-event-source";
import {
  apiClient,
  apiClientWithMeta,
  apiClientBlob,
  resolveApiUrl,
  type ApiPaginatedResult,
} from "@/lib/api-client";
import { AUTH_TOKEN_STORAGE_KEY } from "@/features/auth/stores/useAuthStore";
import type {
  Draft,
  CreateDraftRequest,
  UpdateDraftRequest,
  CompileDraftResponse,
  DraftAssistRequest,
  DraftAssistResponse,
  CreateDraftAssetRequest,
  DraftAsset,
  DraftAssetListResponse,
  SyncTexForwardResult,
  SyncTexInverseResult,
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
   * POST /api/v1/drafts/{id}/synctex:forward
   * Forward search: source line -> PDF coordinates.
   */
  async synctexForward(
    id: string,
    file: string = "main.tex",
    line: number,
    col: number = 1
  ): Promise<SyncTexForwardResult> {
    const data = await apiClient<{
      page: number;
      h?: number;
      v?: number;
      x?: number;
      y?: number;
      width: number;
      height: number;
    }>(`/drafts/${id}/synctex:forward`, {
      method: "POST",
      body: JSON.stringify({ file, line, column: col }),
    });
    return {
      page: data.page,
      x: data.x ?? data.h ?? 0,
      y: data.y ?? data.v ?? 0,
      width: data.width,
      height: data.height,
    };
  },

  /**
   * POST /api/v1/drafts/{id}/synctex:inverse
   * Inverse search: PDF page & point click -> source file and line.
   */
  async synctexInverse(
    id: string,
    page: number,
    x: number,
    y: number
  ): Promise<SyncTexInverseResult> {
    const data = await apiClient<{
      file: string;
      line: number;
      column?: number;
      col?: number;
    }>(`/drafts/${id}/synctex:inverse`, {
      method: "POST",
      body: JSON.stringify({ page, x, y }),
    });
    return {
      file: data.file,
      line: data.line,
      col: data.col ?? data.column ?? 1,
    };
  },

  /**
   * POST /api/v1/drafts/{id}/compile:clear-cache
   * Clear sandbox cache and perform clean compilation.
   */
  async recompileClearCache(id: string): Promise<CompileDraftResponse> {
    return apiClient<CompileDraftResponse>(`/drafts/${id}/compile:clear-cache`, {
      method: "POST",
    });
  },

  /**
   * POST /api/v1/drafts/{id}:undo
   * Undo AI modifications and restore previous snapshot.
   */
  async undoDraft(id: string): Promise<Draft> {
    return apiClient<Draft>(`/drafts/${id}:undo`, {
      method: "POST",
    });
  },

  /**
   * POST /api/v1/drafts/{id}/chat:stream
   * Stream unbuffered SSE responses for AI Co-Author assistant.
   */
  async streamDraftChat(
    id: string,
    prompt: string,
    callbacks: {
      onToken?: (token: string) => void;
      onBadge?: (badge: string) => void;
      onComplete?: (data: any) => void;
      onError?: (err: any) => void;
      signal?: AbortSignal;
    }
  ): Promise<void> {
    const url = resolveApiUrl(`/drafts/${id}/chat:stream`);
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    try {
      const token =
        typeof window !== "undefined"
          ? localStorage.getItem(AUTH_TOKEN_STORAGE_KEY)
          : null;
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }
    } catch {
      // Ignore storage errors
    }

    await fetchEventSource(url, {
      method: "POST",
      headers,
      body: JSON.stringify({ prompt, message: prompt }),
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
          const evName = event.event || parsed.type || parsed.event;

          // Badge detection
          if (evName === "thinking" || evName === "status" || evName === "badge") {
            const badgeText = parsed.badge || parsed.message || parsed.status;
            if (badgeText) {
              callbacks.onBadge?.(badgeText);
            }
          } else if (evName === "tool_start") {
            const toolName = parsed.name || parsed.data?.name;
            if (toolName === "query_library_graph_rag") {
              callbacks.onBadge?.("🔍 Tra cứu GraphRAG");
            } else if (toolName === "edit_latex_files") {
              callbacks.onBadge?.("✍️ Cập nhật mã nguồn");
            } else if (toolName === "compile_latex_e2b") {
              callbacks.onBadge?.("⚙️ Biên dịch E2B");
            } else if (toolName) {
              callbacks.onBadge?.(`⚙️ ${toolName}`);
            }
          }

          // Token emission
          if (evName === "token") {
            const tokenStr =
              typeof parsed === "string"
                ? parsed
                : parsed.token || parsed.delta || parsed.text || "";
            if (tokenStr) callbacks.onToken?.(tokenStr);
          } else if (parsed.token) {
            callbacks.onToken?.(parsed.token);
          }

          // Completion
          if (evName === "done") {
            if (parsed.final_answer) {
              callbacks.onToken?.(parsed.final_answer);
            }
            callbacks.onComplete?.(parsed);
          }

          // Error
          if (evName === "error") {
            callbacks.onError?.(parsed);
          }
        } catch {
          if (event.data) {
            callbacks.onToken?.(event.data);
          }
        }
      },
      onerror(err) {
        callbacks.onError?.(err);
        throw err;
      },
    });
  },
};

