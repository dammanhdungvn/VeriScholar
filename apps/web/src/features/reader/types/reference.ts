/**
 * Academic Reference Resolver & Multi-Paper Ingestion Types (Module 3 - PRD §3.3)
 * Synchronized with backend Exa resolver and session ingestion schemas.
 */

export interface ResolvedReferenceCard {
  ref_index: number;
  raw_text: string;
  title: string;
  authors: string[];
  year?: number | null;
  doi?: string | null;
  arxiv_id?: string | null;
  open_access_pdf_url?: string | null;
  abstract?: string | null;
  citation_count?: number | null;
  sources: string[];
  landing_url?: string | null;
  is_ingested?: boolean;
  resolved_document_id?: string | null;
}

export interface SessionIngestResponse {
  session_id: string;
  ingested_documents: Array<{
    id: string;
    title: string;
    filename: string;
  }>;
  total_documents_in_session: number;
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

