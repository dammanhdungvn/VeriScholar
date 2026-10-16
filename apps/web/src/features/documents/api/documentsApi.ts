import {
  apiClient,
  apiClientWithMeta,
  apiClientBlob,
  resolveApiUrl,
  generateRequestId,
  type ApiPaginatedResult,
} from "@/lib/api-client";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { AUTH_TOKEN_STORAGE_KEY } from "@/features/auth/stores/useAuthStore";
import type {
  DocumentDetailResponseData,
  DocumentListItem,
  DocumentUploadResponseData,
  DocumentStatusResponseData,
  DocumentParseRequest,
  DocumentParseResponseData,
  DocumentExtractReferencesResponseData,
  DocumentStructureData,
  DocumentChunkItem,
  DocumentChunkDetailData,
  DocumentSummaryData,
  DocumentStarResponseData,
  ResolvedReferenceCard,
} from "@/types/document";

export interface StreamSummaryCallbacks {
  onStart?: (data: { document_id: string; status: string }) => void;
  onChunk?: (data: { section: "problem_statement" | "contributions" | "limitations"; token: string }) => void;
  onBox?: (data: { section: "problem_statement" | "contributions" | "limitations"; bounding_boxes: number[][] }) => void;
  onEnd?: (data: { document_id: string; finish_reason: string }) => void;
  onError?: (error: Error) => void;
  signal?: AbortSignal;
}

/**
 * Backward compatibility type aliases
 */
export type DocumentSummaryResponse = DocumentSummaryData;
export type DocumentDetailResponse = DocumentDetailResponseData;
export type DocumentUploadResponse = DocumentUploadResponseData;
export type DocumentStatusResponse = DocumentStatusResponseData;
export type ParseOptions = DocumentParseRequest;

export interface ListDocumentsParams {
  page?: number;
  per_page?: number;
  status?: string;
}

export interface ListChunksParams {
  page?: number;
  per_page?: number;
  page_number?: number;
  include_content?: boolean;
}

export const documentsApi = {
  /**
   * 1. POST /api/v1/documents
   * Tải tệp PDF bài báo lên hệ thống (hỗ trợ session_id tùy chọn)
   */
  async uploadDocument(
    file: File,
    sessionId?: string,
    autoParse = true,
    title?: string,
    idempotencyKey?: string
  ): Promise<DocumentUploadResponseData> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("auto_parse", String(autoParse));
    if (sessionId) {
      formData.append("session_id", sessionId);
    }
    if (title) {
      formData.append("title", title);
    }

    const headers: Record<string, string> = {};
    if (idempotencyKey) {
      headers["Idempotency-Key"] = idempotencyKey;
    }

    return apiClient<DocumentUploadResponseData>("/documents", {
      method: "POST",
      body: formData,
      headers,
    });
  },

  /**
   * 2. GET /api/v1/documents
   * Danh sách bài báo cá nhân (phân trang RFC 8288)
   */
  async listDocuments(params: ListDocumentsParams = {}): Promise<ApiPaginatedResult<DocumentListItem>> {
    const query = new URLSearchParams();
    if (params.page !== undefined) query.set("page", String(params.page));
    if (params.per_page !== undefined) query.set("per_page", String(params.per_page));
    if (params.status) query.set("status", params.status);

    const queryString = query.toString();
    const endpoint = queryString ? `/documents?${queryString}` : "/documents";
    return apiClientWithMeta<DocumentListItem>(endpoint);
  },

  /**
   * 3. GET /api/v1/documents/{id}
   * Chi tiết tài liệu kèm khổ trang (page_dimensions) và góc xoay (rotation_deg)
   */
  async getDocumentDetail(documentId: string): Promise<DocumentDetailResponseData> {
    return apiClient<DocumentDetailResponseData>(`/documents/${documentId}`);
  },

  /**
   * 4. GET /api/v1/documents/{id}/file
   * Stream nhị phân PDF cho Canvas (Hỗ trợ HTTP 206 Partial Content)
   */
  getDocumentFileUrl(documentId: string): string {
    return resolveApiUrl(`/documents/${documentId}/file`);
  },

  async streamDocumentFile(documentId: string, range?: string): Promise<Blob> {
    const headers: Record<string, string> = {};
    if (range) {
      headers.Range = range;
    }
    return apiClientBlob(`/documents/${documentId}/file`, { headers });
  },

  /**
   * 5. GET /api/v1/documents/{id}/status
   * Polling tiến độ bóc tách (stage: running_ocr, progress 0 - 100%)
   */
  async getStatus(documentId: string): Promise<DocumentStatusResponseData> {
    return apiClient<DocumentStatusResponseData>(`/documents/${documentId}/status`);
  },

  /**
   * 6. POST /api/v1/documents/{id}:star
   * Atomic Promotion Transition (lưu bài báo vĩnh viễn vào thư viện cá nhân)
   */
  async starDocument(documentId: string, folderId?: string | null): Promise<DocumentStarResponseData> {
    return apiClient<DocumentStarResponseData>(`/documents/${documentId}:star`, {
      method: "POST",
      body: JSON.stringify({ folder_id: folderId ?? null }),
    });
  },

  /**
   * 7. DELETE /api/v1/documents/{id}
   * Xóa bài báo theo đồ thị phụ thuộc (Zero-Retention Cascade Purge)
   */
  async deleteDocument(documentId: string): Promise<void> {
    return apiClient<void>(`/documents/${documentId}`, {
      method: "DELETE",
    });
  },

  /**
   * 8. POST /api/v1/documents/{id}:parse
   * Kích hoạt / Bóc tách lại với Idempotency
   */
  async parseDocument(
    documentId: string,
    options: DocumentParseRequest = {},
    idempotencyKey?: string
  ): Promise<DocumentParseResponseData> {
    const headers: Record<string, string> = {};
    if (idempotencyKey) {
      headers["Idempotency-Key"] = idempotencyKey;
    }

    return apiClient<DocumentParseResponseData>(`/documents/${documentId}:parse`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        chunk_size: options.chunk_size ?? 512,
        chunk_overlap: options.chunk_overlap ?? 50,
        extract_tables: options.extract_tables ?? true,
        force_reparse: options.force_reparse ?? false,
      }),
    });
  },

  /**
   * 9. POST /api/v1/documents/{id}:extract-references
   * Bóc tách danh mục tài liệu tham khảo (arXiv, DOI, authors)
   */
  async extractReferences(
    documentId: string,
    forceReextract = false
  ): Promise<DocumentExtractReferencesResponseData> {
    return apiClient<DocumentExtractReferencesResponseData>(
      `/documents/${documentId}:extract-references`,
      {
        method: "POST",
        body: JSON.stringify({ force_reextract: forceReextract }),
      }
    );
  },

  /**
   * 9b. POST /api/v1/documents/{id}/references:resolve
   * Phân giải danh mục tài liệu tham khảo với Exa và các nguồn học thuật (Module 3)
   */
  async resolveReferences(documentId: string): Promise<ResolvedReferenceCard[]> {
    return apiClient<ResolvedReferenceCard[]>(
      `/documents/${documentId}/references:resolve`,
      {
        method: "POST",
      }
    );
  },

  /**
   * 10. GET /api/v1/documents/{id}/structure
   * Singleton: Cấu trúc bài báo (TOC, Headings, Sections, Abstract Bounding Boxes)
   */
  async getStructure(documentId: string): Promise<DocumentStructureData> {
    return apiClient<DocumentStructureData>(`/documents/${documentId}/structure`);
  },

  /**
   * 11. GET /api/v1/documents/{id}/chunks
   * Danh sách Chunks (phân trang + include_content tối ưu băng thông)
   */
  async getChunks(
    documentId: string,
    params: ListChunksParams = {}
  ): Promise<ApiPaginatedResult<DocumentChunkItem>> {
    const query = new URLSearchParams();
    if (params.page !== undefined) query.set("page", String(params.page));
    if (params.per_page !== undefined) query.set("per_page", String(params.per_page));
    if (params.page_number !== undefined) query.set("page_number", String(params.page_number));
    if (params.include_content !== undefined) query.set("include_content", String(params.include_content));

    const queryString = query.toString();
    const endpoint = queryString ? `/documents/${documentId}/chunks?${queryString}` : `/documents/${documentId}/chunks`;
    return apiClientWithMeta<DocumentChunkItem>(endpoint);
  },

  /**
   * 12. GET /api/v1/documents/{id}/chunks/{chunk_id}
   * Chi tiết 1 đoạn bằng chứng kèm vector embedding
   */
  async getChunkDetail(documentId: string, chunkId: string): Promise<DocumentChunkDetailData> {
    return apiClient<DocumentChunkDetailData>(`/documents/${documentId}/chunks/${chunkId}`);
  },

  /**
   * 13. GET /api/v1/documents/{id}/summary
   * Singleton: Lấy bản tóm tắt 3 ý cốt lõi kèm micro-bounding boxes
   */
  async getSummary(documentId: string): Promise<DocumentSummaryData> {
    return apiClient<DocumentSummaryData>(`/documents/${documentId}/summary`);
  },

  /**
   * 14. POST /api/v1/documents/{id}/summary:generate
   * Custom Method: Sinh mới tóm tắt 3 ý
   */
  async generateSummary(
    documentId: string,
    force = false,
    idempotencyKey?: string
  ): Promise<DocumentSummaryData> {
    const headers: Record<string, string> = {};
    if (idempotencyKey) {
      headers["Idempotency-Key"] = idempotencyKey;
    }

    return apiClient<DocumentSummaryData>(`/documents/${documentId}/summary:generate`, {
      method: "POST",
      headers,
      body: JSON.stringify({ force }),
    });
  },

  /**
   * 15. GET /api/v1/documents/{id}/export-pdf
   * Xuất file PDF kèm Native Annotations chuẩn ISO
   */
  async exportAnnotatedPdf(documentId: string, includeHighlights = true): Promise<Blob> {
    return apiClientBlob(`/documents/${documentId}/export-pdf?include_highlights=${includeHighlights}`);
  },

  /**
   * 16. POST /api/v1/documents/{id}/summary:stream
   * Stream tóm tắt 3 ý cốt lõi luồng động SSE (Real-Time Grounded Summary Stream)
   */
  async streamSummary(
    documentId: string,
    callbacks: StreamSummaryCallbacks = {},
    requestId?: string
  ): Promise<void> {
    const token = localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
    const finalRequestId = generateRequestId(requestId);
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      "X-Request-ID": finalRequestId,
    };
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    const devUserId = import.meta.env.VITE_DEV_USER_ID || "00000000-0000-0000-0000-000000000001";
    headers["x-user-id"] = devUserId;

    const url = resolveApiUrl(`/documents/${documentId}/summary:stream`);

    await fetchEventSource(url, {
      method: "POST",
      headers,
      signal: callbacks.signal,
      async onopen(response) {
        if (response.ok && response.headers.get("content-type")?.includes("text/event-stream")) {
          return;
        }
        let errMessage = `Failed to open summary stream: ${response.status} ${response.statusText}`;
        try {
          const errJson = await response.json();
          if (errJson?.detail?.message) {
            errMessage = errJson.detail.message;
          }
        } catch {
          // ignore
        }
        throw new Error(errMessage);
      },
      onmessage(ev) {
        if (!ev.data) return;
        try {
          const payload = JSON.parse(ev.data);
          switch (ev.event) {
            case "summary_start":
              callbacks.onStart?.(payload);
              break;
            case "summary_chunk":
              callbacks.onChunk?.(payload);
              break;
            case "summary_box":
              callbacks.onBox?.(payload);
              break;
            case "summary_end":
              callbacks.onEnd?.(payload);
              break;
            case "error":
              callbacks.onError?.(new Error(payload.message || "SSE Error"));
              break;
          }
        } catch (e) {
          console.error("Failed to parse SSE payload", e);
        }
      },
      onerror(err) {
        callbacks.onError?.(err instanceof Error ? err : new Error(String(err)));
        throw err;
      },
    });
  },

  streamDocumentSummary(
    documentId: string,
    callbacks: StreamSummaryCallbacks = {},
    requestId?: string
  ): Promise<void> {
    return this.streamSummary(documentId, callbacks, requestId);
  },
};

