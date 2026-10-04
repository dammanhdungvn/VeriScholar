/**
 * Personal Library, Hierarchical Folders & Multi-Paper Synthesis Types
 */

export interface FolderItem {
  id: string;
  name: string;
  parent_id: string | null;
  document_count: number;
  created_at: string;
  updated_at: string;
}

export interface CreateFolderPayload {
  name: string;
  parent_id?: string | null;
}

export interface UpdateFolderPayload {
  name?: string;
  parent_id?: string | null;
}

export interface BulkImportPayload {
  identifiers: string[];
  target_folder_id?: string | null;
}

export interface BulkImportResponse {
  batch_id: string;
  total_items: number;
  accepted_identifiers: string[];
  status: "queued" | "processing" | "completed";
  message: string;
}

export interface SynthesizeSourceReference {
  document_id: string;
  title: string;
  page_number: number;
  bounding_boxes: number[][]; // [[x0, y0, x1, y1, page], ...]
}

export interface LibrarySynthesizePayload {
  query: string;
  folder_id?: string | null;
}

export interface LibrarySynthesizeResponse {
  answer: string;
  retrieval_tier_reached: "tier_1_smart_notes" | "tier_2_metadata" | "tier_3_deep_raw_chunks";
  sufficiency_score: number;
  sources: SynthesizeSourceReference[];
}

export interface ComparedDocumentInfo {
  id: string;
  title: string;
  authors: string[] | null;
  publication_year: number | null;
}

export interface LibraryComparePayload {
  document_ids: string[];
  columns?: string[];
}

export interface LibraryCompareResponse {
  columns: string[];
  documents: ComparedDocumentInfo[];
  comparison_matrix: Record<string, Record<string, string>>;
}
