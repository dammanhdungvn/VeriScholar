/**
 * Academic Document & Retrieval Unit Type Contracts (Module 1)
 * Synchronized 1-1 with FastAPI OpenAPI schemas (api.schemas.document)
 * Zero 'any' policy strictly enforced.
 */

import type { BoundingBox, PageDimensions } from "./api";

export type DocumentStatus = "uploaded" | "pending" | "processing" | "completed" | "failed";

export type DocumentStage =
  | "queued"
  | "validation"
  | "layout_detection"
  | "running_ocr"
  | "chunking"
  | "embedding"
  | "completed"
  | "failed";

export interface PageMetadataItem {
  page_number: number;
  dimensions: [number, number];
  rotation_deg: 0 | 90 | 180 | 270;
}

export interface DocumentListItem {
  id: string;
  filename: string;
  title?: string | null;
  status: DocumentStatus | string;
  is_persistent: boolean;
  created_at: string;
  authors?: string[] | null;
  publication_year?: number | null;
  year?: number | null;
  folder_id?: string | null;
  starred_at?: string | null;
  page_count?: number | null;
  file_size_bytes?: number;
}

export interface DocumentDetailResponseData {
  id: string;
  filename: string;
  title?: string | null;
  authors?: string[] | null;
  publication_year?: number | null;
  doi?: string | null;
  page_count?: number | null;
  chunk_count: number;
  file_size_bytes: number;
  status: string;
  is_persistent: boolean;
  folder_id?: string | null;
  pages_metadata: PageMetadataItem[];
  created_at: string;
  access_status?: string | null;
  abstract?: string | null;
  parsed_metadata?: {
    abstract?: string | null;
    arxiv_id?: string | null;
    venue?: string | null;
    [key: string]: unknown;
  } | null;
}

export interface DocumentUploadResponseData {
  id: string;
  filename: string;
  file_size_bytes: number;
  content_hash?: string;
  status: string;
  stage: string;
  progress?: number;
  is_persistent?: boolean;
  session_id?: string | null;
  title?: string | null;
  is_duplicate?: boolean;
  created_at?: string;
  links?: {
    self_url: string;
    status_url: string;
    file_url: string;
    parse_url: string;
  };
}

export interface StagesDetail {
  validation: string;
  layout_detection: string;
  ocr: string;
  chunking: string;
  embedding: string;
}

export interface DocumentStatusResponseData {
  id: string;
  status: DocumentStatus | string;
  stage: DocumentStage | string;
  progress: number;
  stages_detail: StagesDetail;
  error_message?: string | null;
}

export interface DocumentParseRequest {
  chunk_size?: number;
  chunk_overlap?: number;
  extract_tables?: boolean;
  force_reparse?: boolean;
}

export interface DocumentParseResponseData {
  id: string;
  status: string;
  stage: string;
  progress: number;
  message?: string;
  links?: {
    status_url: string;
    detail_url: string;
  };
}

export interface ParsedReferenceItemSchema {
  title?: string | null;
  authors: string[];
  year?: number | null;
  arxiv_id?: string | null;
  doi?: string | null;
}

export interface ReferenceItemResponse {
  ref_index: number;
  raw_text: string;
  parsed: ParsedReferenceItemSchema;
}

export interface DocumentExtractReferencesResponseData {
  document_id: string;
  total_extracted: number;
  references: ReferenceItemResponse[];
}

export interface DocumentSectionResponse {
  title: string;
  page_number: number;
  bounding_boxes: BoundingBox[];
}

export interface DocumentStructureData {
  document_id: string;
  title?: string | null;
  abstract?: string | null;
  abstract_bounding_boxes: BoundingBox[];
  sections: DocumentSectionResponse[];
}

export interface DocumentChunkItem {
  id: string;
  document_id: string;
  chunk_index: number;
  page_number: number;
  content?: string | null;
  bounding_boxes: BoundingBox[];
  token_count: number;
}

export interface DocumentChunkDetailData {
  id: string;
  document_id: string;
  chunk_index: number;
  page_number: number;
  content: string;
  bounding_boxes: BoundingBox[];
  token_count: number;
  embedding_dimension?: number | null;
  created_at?: string | null;
  updated_at?: string | null;
  links: {
    self: string;
    document: string;
    chunks: string;
    prev_chunk?: string | null;
    next_chunk?: string | null;
  };
}

export interface SummaryPointResponse {
  text: string;
  bounding_boxes: BoundingBox[];
}

export interface DocumentSummaryData {
  document_id: string;
  problem_statement: SummaryPointResponse;
  contributions: SummaryPointResponse;
  limitations: SummaryPointResponse;
  total_tokens?: number | null;
  latency_ms?: number | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface DocumentStarResponseData {
  id: string;
  filename: string;
  title?: string | null;
  status: string;
  is_persistent: boolean;
  folder_id?: string | null;
  updated_at: string;
}

/**
 * Backward compatibility aliases for existing components
 */
export type DocumentChunk = DocumentChunkItem;
export interface DocumentResponse {
  id: string;
  filename: string;
  sha256?: string;
  file_size_bytes: number;
  total_pages?: number;
  page_count?: number | null;
  status: DocumentStatus;
  is_persistent: boolean;
  page_dimensions?: PageDimensions;
  rotation_deg?: 0 | 90 | 180 | 270;
  created_at: string;
  updated_at?: string;
}

export type {
  ResolvedReferenceCard,
  SessionIngestResponse,
} from "@/features/reader/types/reference";
