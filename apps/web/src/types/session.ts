/**
 * Research Sessions & Dual-Pane Workspace Type Contracts
 * Synchronized 1-1 with FastAPI OpenAPI schemas (api.schemas.session)
 * Zero 'any' policy strictly enforced.
 */

import type { BoundingBox } from "./api";

export interface ViewportStateSchema {
  page: number;
  zoom_ratio: number;
  scroll_top: number;
}

export interface SessionDocumentItem {
  id: string;
  title?: string | null;
  filename: string;
  status: string;
  file_size_bytes: number;
  added_at: string;
  display_order: number;
}

export interface SessionCreateRequest {
  title?: string | null;
  initial_document_ids?: string[];
}

export interface SessionResponseData {
  id: string;
  title: string;
  document_ids: string[];
  active_document_id?: string | null;
  viewport_state: ViewportStateSchema;
  active_tab: string;
  is_archived: boolean;
  version: number;
  message_count?: number;
  documents?: SessionDocumentItem[] | null;
  warnings?: string[];
  created_at: string;
  updated_at: string;
}

export interface SessionHistoryItem {
  id: string;
  title: string;
  document_count: number;
  active_tab: string;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface SessionUpdateMetadataRequest {
  title: string;
}

export type SessionActiveTab = "chat" | "notes" | "summary" | "graph" | "draft";

export interface SessionUpdateViewportRequest {
  active_document_id?: string | null;
  viewport_state: ViewportStateSchema;
  active_tab?: SessionActiveTab;
}

export interface SessionAddDocumentRequest {
  source_type: "document_id" | "url";
  document_id?: string | null;
  url?: string | null;
  title?: string | null;
}

export interface CitationItemSchema {
  citation_id: string;
  document_id: string;
  document_title: string;
  page_number: number;
  bounding_boxes: BoundingBox[];
  score?: number;
}

export interface SessionTurnItem {
  id: string;
  session_id: string;
  question: string;
  answer: string;
  citations: CitationItemSchema[];
  prompt_tokens?: number;
  completion_tokens?: number;
  total_tokens?: number;
  latency_ms?: number;
  finish_reason?: string;
  created_at: string;
}

export interface SessionChatMessageRequest {
  question: string;
  stream?: boolean;
  scope?: "multi_paper" | "single_paper";
  focused_document_id?: string | null;
  enable_thinking?: boolean;
  interactive_response?: Record<string, unknown> | null;
}

export type {
  SessionIngestResponse,
  CitationGraphData,
  CitationGraphNode,
  CitationGraphEdge,
} from "@/features/reader/types/reference";
