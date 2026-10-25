export type SidebarState = "collapsed" | "expanded";
export type AppMode = "chat" | "library";

export type BoundingBox = [number, number, number, number, number]; // [x0, y0, x1, y1, page]

export interface CitationBadgeData {
  citation_id?: string;
  paper_id: string;
  paper_title: string;
  page: number;
  bbox: BoundingBox;
}

export interface PresuppositionAlertData {
  flawed_premise: string;
  correction: string;
  grounded_bbox: BoundingBox;
  page: number;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
  is_streaming?: boolean;
  thought?: string;
  citations?: CitationBadgeData[];
  presupposition_alert?: PresuppositionAlertData;
}

export interface ViewportState {
  page: number;
  zoom_ratio: number;
  scroll_top: number;
}

export interface SessionDocument {
  id: string;
  title: string;
  filename: string;
  status: "uploaded" | "processing" | "completed" | "failed";
  file_size_bytes: number;
  added_at: string;
  display_order: number;
}

export interface SessionItem {
  id: string;
  title: string;
  document_ids: string[];
  created_at: string;
  updated_at: string;
  version: number;
  unread?: boolean;
  is_archived?: boolean;
}

export interface SessionDetail extends SessionItem {
  active_document_id?: string | null;
  viewport_state: ViewportState;
  active_tab: "chat" | "notes" | "highlights" | "mindmap";
  is_archived: boolean;
  documents?: SessionDocument[];
  warnings?: string[];
}

export interface CreateSessionRequest {
  title?: string;
  initial_document_ids?: string[];
}

export interface UpdateSessionTitleRequest {
  title: string;
}

export interface UpdateSessionViewportRequest {
  viewport_state: ViewportState;
  active_tab?: "chat" | "notes" | "highlights" | "mindmap";
  active_document_id?: string | null;
}

export interface AddDocumentToSessionRequest {
  source_type: "document_id" | "url";
  document_id?: string;
  url?: string;
  title?: string;
}

export interface AddDocumentToSessionResponse {
  session_id: string;
  document_id: string;
  status: "associated" | "queued";
  display_order: number;
  message: string;
}

export interface PostSessionMessageRequest {
  question: string;
  stream?: boolean;
  scope?: "multi_paper" | "active_paper";
  interactive_response?: Record<string, unknown> | null;
}

export interface SSESessionStartEvent {
  turn_id: string;
  message_id: string;
  created_at: string;
}

export interface SSESessionReasoningEvent {
  thought: string;
}

export interface SSESessionCitationItem {
  citation_id: string;
  document_id: string;
  document_title: string;
  page_number: number;
  bounding_boxes: BoundingBox[];
  score: number;
}

export interface SSESessionCitationsEvent {
  citations: SSESessionCitationItem[];
}

export interface SSESessionTokenEvent {
  token: string;
}

export interface SSESessionDoneEvent {
  finish_reason: string;
  prompt_tokens?: number;
  completion_tokens?: number;
  total_tokens?: number;
  latency_ms?: number;
  intent?: string;
}

export interface SSESessionErrorEvent {
  code: string;
  message: string;
  action?: string;
}

export interface SessionTurnItem {
  turn_id: string;
  question: string;
  answer: string;
  citations: CitationBadgeData[];
  presupposition_alert?: PresuppositionAlertData;
  latency_ms?: number;
  prompt_tokens?: number;
  completion_tokens?: number;
  created_at: string;
}

export interface IdeaPrompt {
  id: string;
  title: string;
  subtitle?: string;
  prompt: string;
  iconName: string;
}
