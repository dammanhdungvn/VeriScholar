/**
 * TypeScript Interfaces and Types for Academic Writing & LaTeX Compilation (Module 2).
 */

export type DraftFormat = "latex" | "markdown";

export interface Draft {
  id: string;
  user_id: string;
  title: string;
  content: string;
  bib_content?: string | null;
  format: DraftFormat;
  template?: string | null;
  source_session_id?: string | null;
  pdf_preview_url?: string | null;
  previous_snapshot?: {
    content?: string;
    bib_content?: string;
    version?: number;
    saved_at?: string;
  } | null;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface CreateDraftRequest {
  title?: string;
  content?: string;
  bib_content?: string;
  format?: DraftFormat;
}

export interface UpdateDraftRequest {
  title?: string;
  content?: string;
  bib_content?: string | null;
  format?: DraftFormat;
  version?: number;
}

export interface LatexSyntaxError {
  line: number;
  column: number;
  rule: string;
  message: string;
  suggested_fix?: string | null;
}

export interface CompileDraftResponse {
  draft_id: string;
  success: boolean;
  pdf_preview_url?: string | null;
  errors: LatexSyntaxError[];
  logs: string;
  retries_attempted: number;
}

export interface SyncTexForwardResult {
  page: number;
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface SyncTexInverseResult {
  file: string;
  line: number;
  col: number;
}

export type WorkspaceMode =
  | "tri-pane" // [Code Editor] | [PDF Preview] | [AI Assistant]
  | "dual-code" // [Code Editor] | [PDF Preview]
  | "dual-ai" // [PDF Preview] | [AI Assistant]
  | "zen-pdf" // [PDF Preview 100%]
  | "zen-code"; // [Code Editor 100%]

export interface DraftAssistRequest {
  prompt: string;
  pre_context?: string;
  target_selection?: string;
  post_context?: string;
  cursor_position?: number;
}

export interface DraftAssistResponse {
  draft_id: string;
  prompt: string;
  original_text?: string | null;
  suggested_text: string;
  explanation?: string | null;
  confidence_score: number;
  suggested_at: string;
}

// =============================================================================
// Asset Management Types (/drafts/{id}/assets)
// =============================================================================

export type DraftAssetType =
  | "image"
  | "bibtex"
  | "table"
  | "dataset"
  | "supplementary";

export interface CreateDraftAssetRequest {
  asset_type?: DraftAssetType;
  filename: string;
  content_base64?: string;
  caption?: string;
  latex_label?: string;
}

export interface DraftAsset {
  id: string;
  draft_id: string;
  asset_type: string;
  filename: string;
  file_size_bytes: number;
  storage_url: string;
  caption?: string | null;
  latex_label?: string | null;
  created_at: string;
}

export interface DraftAssetListResponse {
  draft_id: string;
  items: DraftAsset[];
  total: number;
}

