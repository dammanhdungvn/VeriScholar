/**
 * Smart Research Notes & Knowledge Digest Type Contracts
 * Synchronized 1-1 with FastAPI OpenAPI schemas (api.schemas.note)
 * Zero 'any' policy strictly enforced.
 */

import type { BoundingBox } from "./api";

export type NoteSynthesisMode =
  | "concept_lesson"
  | "literature_review"
  | "research_gap"
  | "active_recall_quiz";

export interface CreateNoteRequest {
  document_id?: string | null;
  chunk_id?: string | null;
  selected_text: string;
  bounding_boxes?: BoundingBox[];
  page_number?: number;
  user_note?: string | null;
  tags?: string[];
}

export interface UpdateNoteRequest {
  user_note?: string | null;
  tags?: string[] | null;
}

export interface NoteResponse {
  id: string;
  document_id?: string | null;
  chunk_id?: string | null;
  selected_text: string;
  bounding_boxes: BoundingBox[];
  page_number: number;
  user_note?: string | null;
  tags: string[];
  frozen_snapshot: Record<string, unknown>;
  is_source_detached: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface NoteListItemResponse {
  id: string;
  document_id?: string | null;
  document_title?: string | null;
  selected_text: string;
  page_number: number;
  user_note?: string | null;
  tags: string[];
  is_source_detached: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface SynthesizeNotesRequest {
  note_ids: string[];
  mode?: NoteSynthesisMode;
  language?: string;
  target_title?: string | null;
}

export interface InteractiveBadgeResponse {
  badge_id: string;
  note_id: string;
  document_id?: string | null;
  citation_label: string;
  page_number: number;
  bounding_boxes: BoundingBox[];
  quote_text: string;
  is_source_detached: boolean;
}

export interface NoteSynthesisResponse {
  id: string;
  title: string;
  mode: string;
  language: string;
  markdown_content: string;
  interactive_badges: InteractiveBadgeResponse[];
  source_note_ids: string[];
  created_at: string;
  updated_at: string;
}
