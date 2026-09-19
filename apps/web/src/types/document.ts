import type { BoundingBox, PageDimensions } from "./api";

export type DocumentStatus = "uploaded" | "parsing" | "chunking" | "indexing" | "completed" | "failed";

export interface DocumentChunk {
  id: string;
  document_id: string;
  chunk_index: number;
  content: string;
  bounding_box: BoundingBox;
  section_title?: string | null;
  page: number;
}

export interface DocumentResponse {
  id: string;
  filename: string;
  sha256: string;
  file_size_bytes: number;
  total_pages: number;
  status: DocumentStatus;
  is_persistent: boolean;
  page_dimensions: PageDimensions;
  rotation_deg: 0 | 90 | 180 | 270;
  created_at: string;
  updated_at: string;
}
