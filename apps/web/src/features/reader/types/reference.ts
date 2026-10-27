/**
 * Academic Reference Resolver & Multi-Paper Ingestion Types (Module 3 - PRD §3.3)
 * Synchronized with backend Exa resolver and session ingestion schemas.
 */

export interface ResolvedReferenceCard {
  ref_index: number;
  raw_text: string;
  title?: string;
  parsed_title?: string | null;
  authors?: string[];
  parsed_authors?: string[];
  year?: number | null;
  parsed_year?: number | null;
  doi?: string | null;
  arxiv_id?: string | null;
  access_status?: string;
  open_access_pdf_url?: string | null;
  pdf_url?: string | null;
  abstract?: string | null;
  citation_count?: number | null;
  sources?: string[];
  landing_url?: string | null;
  is_ingested?: boolean;
  is_in_session?: boolean;
  resolved_document_id?: string | null;
}

export interface SessionReferenceIngestResponse {
  session_id: string;
  document_id: string;
  session_document_id?: string;
  title: string;
  status: string;
  access_status: string;
  ref_index: number;
  fallback_reason?: string | null;
  total_documents_in_session: number;
  ingested_documents: Array<{
    id: string;
    title: string;
    filename: string;
  }>;
}

export interface SessionIngestResponse {
  session_id: string;
  ingested_documents: Array<{
    id: string;
    title: string;
    filename: string;
  }>;
  total_documents_in_session: number;
  document_id?: string;
  status?: string;
  access_status?: string;
  ref_index?: number;
}

export interface CitationGraphNode {
  id: string;
  title: string;
  authors?: string[];
  year?: number | null;
  doi?: string | null;
  arxiv_id?: string | null;
  depth?: number;
  is_session_doc?: boolean;
  is_session_document?: boolean;
  citation_count?: number | null;
}

export interface CitationGraphEdge {
  source: string;
  target: string;
  relationship?: "CITES" | "EXTENDS" | "BENCHMARKS_ON" | string;
  relation?: "CITES" | "EXTENDS" | "BENCHMARKS_ON" | string;
  confidence?: number;
  scope?: "domain" | "session";
}

export interface CitationGraphData {
  session_id?: string;
  nodes: CitationGraphNode[];
  edges: CitationGraphEdge[];
  topological_order?: string[];
  reading_path?: string[];
}

