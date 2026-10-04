/**
 * Academic Drafting Workspace, Compile Sandbox & SAFE Fact-Checking Types
 */

export interface CreateDraftPayload {
  title: string;
  format?: "latex" | "markdown";
  template?: string;
  initial_content?: string;
}

export interface UpdateDraftContentPayload {
  content: string;
}

export interface PatchDraftPayload {
  title?: string;
  template?: string;
}

export interface DraftItem {
  id: string;
  user_id: string;
  title: string;
  format: "latex" | "markdown";
  template: string;
  content: string;
  version: number;
  last_compiled_at: string | null;
  last_compile_status: string | null;
  pdf_preview_storage_path: string | null;
  created_at: string;
  updated_at: string;
}

export interface CompileDraftPayload {
  compiler_engine?: "tectonic" | "pdflatex";
  auto_self_heal?: boolean;
  max_heal_attempts?: number;
}

export interface CreateDraftCommentPayload {
  line_number: number;
  selected_text: string;
  comment: string;
}

export interface DraftCommentItem {
  id: string;
  draft_id: string;
  user_id: string;
  author_name: string;
  line_number: number;
  selected_text: string;
  comment: string;
  status: "open" | "resolved";
  created_at: string;
  updated_at: string;
}

export interface ClaimCitation {
  document_id: string | null;
  page_number: number | null;
  bounding_boxes: number[][]; // [[x0, y0, x1, y1, page], ...]
  quote: string | null;
}

export interface ClaimVerificationResult {
  claim_index: number;
  claim_text: string;
  verdict: "supported" | "contradicted" | "not_enough_info";
  confidence: number;
  citation: ClaimCitation | null;
}

export interface VerifyClaimsPayload {
  selected_text: string;
  document_ids?: string[];
}

export interface VerifyClaimsResponse {
  verification_id: string;
  draft_id: string;
  selected_text: string;
  claims: ClaimVerificationResult[];
  total_claims: number;
  supported_count: number;
  contradicted_count: number;
  not_enough_info_count: number;
}
