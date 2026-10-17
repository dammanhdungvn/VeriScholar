/**
 * TypeScript Interfaces and Types for Academic Writing & SAFE Fact-Checking (Module 2).
 */

export type DraftFormat = "latex" | "markdown";

export interface Draft {
  id: string;
  user_id: string;
  title: string;
  content: string;
  format: DraftFormat;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface CreateDraftRequest {
  title?: string;
  content?: string;
  format?: DraftFormat;
}

export interface UpdateDraftRequest {
  title?: string;
  content?: string;
  format?: DraftFormat;
  version: number;
}

export type FactVerificationStatus = "supported" | "contradicted" | "not_enough_info";

export interface AtomicClaim {
  id: string;
  claim_text: string;
  normalized_entities: string[];
  status: FactVerificationStatus;
  confidence_score: number;
  evidence_text?: string;
  evidence_document_id?: string;
  evidence_document_title?: string;
  evidence_page?: number;
  evidence_bounding_boxes?: number[][]; // [x0, y0, x1, y1, page]
  reasoning?: string;
}

export interface VerifyFactsRequest {
  text?: string;
  document_ids?: string[];
}

export interface VerifyFactsResponse {
  draft_id: string;
  verified_text: string;
  claims: AtomicClaim[];
  total_claims: number;
  supported_claims: number;
  contradicted_claims: number;
  unverified_claims: number;
  supported_ratio: number;
  latency_ms: number;
  verified_at: string;
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

export interface PendingSuggestion {
  id: string;
  draft_id: string;
  prompt: string;
  original_text: string;
  suggested_text: string;
  explanation?: string;
  confidence_score: number;
  cursor_start: number;
  cursor_end: number;
  expected_version: number;
  created_at: string;
  base_content?: string;
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

// =============================================================================
// Draft Sharing & Collaborator Types (/drafts/{id}/share)
// =============================================================================

export type SharePermission = "viewer" | "commenter" | "editor";

export interface DraftShareRequest {
  target_email?: string;
  permission?: SharePermission;
  allow_public_link?: boolean;
}

export interface DraftCollaborator {
  user_id?: string | null;
  email: string;
  permission: string;
  granted_at: string;
}

export interface DraftShareResponse {
  draft_id: string;
  share_token: string;
  share_url: string;
  permission: string;
  allow_public_link: boolean;
  collaborators: DraftCollaborator[];
}

// =============================================================================
// Draft Peer Review Comments Types (/drafts/{id}/comments)
// =============================================================================

export interface DraftComment {
  id: string;
  draft_id: string;
  author_id: string;
  author_name: string;
  start_offset: number;
  end_offset: number;
  selected_text: string;
  comment_text: string;
  parent_id?: string | null;
  is_resolved: boolean;
  created_at: string;
  updated_at: string;
  replies?: DraftComment[];
}

export interface CreateDraftCommentRequest {
  start_offset: number;
  end_offset: number;
  selected_text: string;
  comment_text: string;
  parent_id?: string;
}

export interface UpdateDraftCommentRequest {
  comment_text?: string;
  is_resolved?: boolean;
}

export interface OverleafExportResponse {
  launch_url: string;
  draft_id?: string;
}

export interface AssociativeSuggestionItem {
  note_id: string;
  document_id?: string | null;
  document_title: string;
  paper_title: string;
  folder_name?: string | null;
  page_number: number;
  selected_text: string;
  user_note?: string | null;
  note_content?: string;
  similarity_score: number;
  suggested_citation: string;
  reason: string;
  relevance_explanation: string;
  matched_keywords?: string[];
}

export interface AssociativeSuggestionsResponse {
  draft_id: string;
  query_excerpt?: string;
  total_found: number;
  suggestions: AssociativeSuggestionItem[];
}

export interface AssociativeMemorySuggestion {
  id: string;
  title: string;
  page: number;
  citation_key?: string;
  note_id?: string;
  note_snippet?: string;
  similarity_score?: number;
}

