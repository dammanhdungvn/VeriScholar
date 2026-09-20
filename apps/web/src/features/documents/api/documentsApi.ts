import { apiClient } from "@/lib/api-client";
import type { BoundingBox } from "@/types/dashboard";

export interface DocumentUploadResponse {
  id: string;
  filename: string;
  file_size_bytes: number;
  status: string;
  stage: string;
  session_id: string | null;
  is_duplicate: boolean;
  title?: string | null;
}

export interface DocumentStatusResponse {
  id: string;
  status: "uploaded" | "pending" | "processing" | "completed" | "failed";
  stage: string;
  progress: number;
  stages_detail: {
    validation: string;
    layout_detection: string;
    ocr: string;
    chunking: string;
    embedding: string;
  };
  error_message?: string | null;
}

export interface DocumentSummaryPoint {
  text: string;
  bounding_boxes: BoundingBox[];
}

export interface DocumentSummaryResponse {
  document_id: string;
  problem_statement: DocumentSummaryPoint;
  contributions: DocumentSummaryPoint;
  limitations: DocumentSummaryPoint;
  total_tokens?: number;
  latency_ms?: number;
}

export interface DocumentDetailResponse {
  id: string;
  title: string | null;
  filename: string;
  page_count: number | null;
  chunk_count: number;
  status: string;
  authors: string[];
  publication_year?: number | null;
  doi?: string | null;
  pages_metadata?: {
    page_number: number;
    dimensions: [number, number];
    rotation_deg: number;
  }[];
}

export interface ParseOptions {
  chunk_size?: number;
  chunk_overlap?: number;
  extract_tables?: boolean;
  force_reparse?: boolean;
}

export const documentsApi = {
  /**
   * Upload raw PDF file to storage blob
   */
  async uploadDocument(file: File, sessionId?: string): Promise<DocumentUploadResponse> {
    const formData = new FormData();
    formData.append("file", file);
    if (sessionId) {
      formData.append("session_id", sessionId);
    }

    return apiClient<DocumentUploadResponse>("/documents", {
      method: "POST",
      body: formData,
    });
  },

  /**
   * Trigger parsing and chunking pipeline
   */
  async parseDocument(documentId: string, options: ParseOptions = {}): Promise<{
    id: string;
    status: string;
    stage: string;
    progress: number;
  }> {
    return apiClient(`/documents/${documentId}:parse`, {
      method: "POST",
      body: JSON.stringify({
        chunk_size: options.chunk_size ?? 512,
        chunk_overlap: options.chunk_overlap ?? 50,
        extract_tables: options.extract_tables ?? true,
        force_reparse: options.force_reparse ?? false,
      }),
    });
  },

  /**
   * Poll status of document parsing pipeline
   */
  async getStatus(documentId: string): Promise<DocumentStatusResponse> {
    return apiClient<DocumentStatusResponse>(`/documents/${documentId}/status`);
  },

  /**
   * Get document metadata and spatial pages info
   */
  async getDocumentDetail(documentId: string): Promise<DocumentDetailResponse> {
    return apiClient<DocumentDetailResponse>(`/documents/${documentId}`);
  },

  /**
   * Fetch 3-point grounded summary
   */
  async getSummary(documentId: string): Promise<DocumentSummaryResponse> {
    return apiClient<DocumentSummaryResponse>(`/documents/${documentId}/summary`);
  },
};
