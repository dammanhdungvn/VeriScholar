import {
  apiClient,
  apiClientWithHeaders,
  apiClientWithMeta,
  type ApiResponseWithHeaders,
  type ApiPaginatedResult,
} from "@/lib/api-client";
import type {
  CreateNoteRequest,
  UpdateNoteRequest,
  NoteResponse,
  NoteListItemResponse,
  SynthesizeNotesRequest,
  NoteSynthesisResponse,
} from "@/types/note";

export interface ListNotesParams {
  document_id?: string;
  tag?: string;
  folder_id?: string;
  page?: number;
  per_page?: number;
}

function normalizeIfMatchHeader(etag: string): string {
  const trimmed = etag.trim();
  if (trimmed.startsWith('"') && trimmed.endsWith('"')) {
    return trimmed;
  }
  return `"${trimmed}"`;
}

export const notesApi = {
  /**
   * 16. POST /api/v1/notes
   * Lưu trích dẫn & ghi chú cá nhân (Add to Note) kèm Frozen Snapshot
   */
  async createNote(
    data: CreateNoteRequest,
    idempotencyKey?: string
  ): Promise<ApiResponseWithHeaders<NoteResponse>> {
    const headers: Record<string, string> = {};
    if (idempotencyKey) {
      headers["Idempotency-Key"] = idempotencyKey;
    }

    return apiClientWithHeaders<NoteResponse>("/notes", {
      method: "POST",
      headers,
      body: JSON.stringify(data),
    });
  },

  /**
   * 17. GET /api/v1/notes
   * Danh sách ghi chú cá nhân (phân trang và lọc theo document_id, tag)
   */
  async listNotes(params: ListNotesParams = {}): Promise<ApiPaginatedResult<NoteListItemResponse>> {
    const query = new URLSearchParams();
    if (params.document_id) query.set("document_id", params.document_id);
    if (params.tag) query.set("tag", params.tag);
    if (params.folder_id) query.set("folder_id", params.folder_id);
    if (params.page !== undefined) query.set("page", String(params.page));
    if (params.per_page !== undefined) query.set("per_page", String(params.per_page));

    const queryString = query.toString();
    const endpoint = queryString ? `/notes?${queryString}` : "/notes";
    return apiClientWithMeta<NoteListItemResponse>(endpoint);
  },

  /**
   * 18. GET /api/v1/notes/{id}
   * Chi tiết ghi chú kèm Frozen Evidence Snapshot và ETag
   */
  async getNoteDetail(noteId: string): Promise<ApiResponseWithHeaders<NoteResponse>> {
    return apiClientWithHeaders<NoteResponse>(`/notes/${noteId}`);
  },

  /**
   * 19. PATCH /api/v1/notes/{id}
   * Sửa ghi chú / tag có kiểm soát đồng thời OCC (bắt buộc Header If-Match)
   */
  async updateNote(
    noteId: string,
    data: UpdateNoteRequest,
    etag: string
  ): Promise<ApiResponseWithHeaders<NoteResponse>> {
    return apiClientWithHeaders<NoteResponse>(`/notes/${noteId}`, {
      method: "PATCH",
      headers: {
        "If-Match": normalizeIfMatchHeader(etag),
      },
      body: JSON.stringify(data),
    });
  },

  /**
   * 20. DELETE /api/v1/notes/{id}
   * Xóa ghi chú khỏi sổ tay
   */
  async deleteNote(noteId: string): Promise<void> {
    return apiClient<void>(`/notes/${noteId}`, {
      method: "DELETE",
    });
  },

  /**
   * 21. POST /api/v1/notes:synthesize
   * AI Tổng hợp ghi chú thành bài học đúc kết (4 modes) kèm Interactive Badges
   */
  async synthesizeNotes(
    data: SynthesizeNotesRequest,
    idempotencyKey?: string
  ): Promise<NoteSynthesisResponse> {
    const headers: Record<string, string> = {};
    if (idempotencyKey) {
      headers["Idempotency-Key"] = idempotencyKey;
    }

    return apiClient<NoteSynthesisResponse>("/notes:synthesize", {
      method: "POST",
      headers,
      body: JSON.stringify(data),
    });
  },
};
