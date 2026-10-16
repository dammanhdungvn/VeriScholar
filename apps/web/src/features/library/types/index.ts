/**
 * Types for Module 4: Personal Paper Library, Literature Comparison Matrix & Hierarchical RAG
 */

export interface FolderItem {
  id: string;
  user_id: string;
  name: string;
  parent_id: string | null;
  color: string;
  description: string | null;
  document_count: number;
  subfolder_count: number;
  created_at: string;
  updated_at: string;
}

export interface FolderTreeItem {
  id: string;
  name: string;
  parent_id: string | null;
  color: string;
  description: string | null;
  document_count: number;
  subfolders: FolderTreeItem[];
}

export interface FolderCreatePayload {
  name: string;
  parent_id?: string | null;
  color?: string;
  description?: string | null;
}

export interface FolderUpdatePayload {
  name?: string;
  parent_id?: string | null;
  color?: string;
  description?: string | null;
}

export interface FolderDocumentAssignPayload {
  document_ids: string[];
}

export interface ComparisonMatrixRow {
  document_id: string;
  title: string;
  authors: string[];
  year: number | null;
  core_methodology: string;
  datasets_used: string[];
  key_metrics: Record<string, string>;
  strengths: string[];
  limitations: string[];
}

export interface SufficiencyGateResult {
  is_sufficient: boolean;
  sufficiency_score: number;
  analyzed_aspects: string[];
  missing_aspects: string[];
  recommended_search_queries: string[];
  reasoning: string;
}

export interface ComparisonMatrixResponse {
  matrix_id: string;
  topic: string;
  folder_id: string | null;
  documents_compared: number;
  rows: ComparisonMatrixRow[];
  summary_synthesis: string;
  sufficiency: SufficiencyGateResult;
  markdown_table: string;
  generated_at: string;
}

export interface ComparisonMatrixRequest {
  topic: string;
  folder_id?: string | null;
  document_ids?: string[] | null;
}

export interface HierarchicalRagRequest {
  query: string;
  folder_id?: string | null;
  enable_thinking?: boolean;
  stream?: boolean;
}

export interface HierarchicalRagResponse {
  answer: string;
  thought?: string | null;
  tier_used: "tier1_notes" | "tier2_chunks" | "hybrid";
  notes_retrieved_count: number;
  chunks_retrieved_count: number;
  sufficiency: SufficiencyGateResult;
  citations: Array<{
    document_id?: string;
    document_title?: string;
    page_number?: number;
    bbox?: number[];
    [key: string]: unknown;
  }>;
}
