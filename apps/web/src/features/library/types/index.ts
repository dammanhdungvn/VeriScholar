/**
 * Types for Module 4 & 5: Personal Paper Library, Folders & GraphRAG Subgraph
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

// ==============================================================================
// 4-Entity Knowledge Graph & GraphRAG Types (Module 5)
// ==============================================================================

export type GraphNodeType = "Paper" | "Method" | "Dataset" | "MetricResult";
export type GraphEdgeType = "PROPOSES" | "EVALUATED_ON" | "ACHIEVES" | "CITES";
export type GraphQueryMode = "local" | "global" | "hybrid";

export interface GraphNode {
  id: string;
  type: GraphNodeType | string;
  name: string;
  canonical_name?: string;
  degree_centrality?: number;
  role?: "method_hub" | "prior_work" | "derivative_work" | "metric" | string;
  year?: number | null;
  metadata_json?: Record<string, unknown>;
}

export interface GraphEdge {
  id?: string;
  document_id?: string;
  source: string;
  target: string;
  type: GraphEdgeType | string;
  evidence_chunk_id?: string | null;
  page_number?: number | null;
  metadata_json?: Record<string, unknown>;
}

export interface BoundingBox {
  page_number: number;
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface EvidenceChunk {
  chunk_id: string;
  document_id: string;
  page_number: number;
  chunk_text: string;
  bbox?: BoundingBox[] | null;
}

export interface GraphSubgraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
  evidence?: EvidenceChunk[];
}

export interface GraphQueryRequest {
  query: string;
  mode?: GraphQueryMode;
  folder_id?: string | null;
  top_k?: number;
}

export interface GraphQueryResponseData {
  mode_used: GraphQueryMode | string;
  answer: string;
  subgraph: GraphSubgraph;
  evidence_chunks?: EvidenceChunk[];
  meta?: {
    trace_id?: string;
    matched_entities?: number;
    folder_id?: string | null;
    [key: string]: unknown;
  };
}

// ==============================================================================
// Connected Papers Bibliometrics Types (Module 5)
// ==============================================================================

export interface PriorWorkItem {
  id: string;
  title: string;
  year?: number | null;
  in_degree: number;
  citation_key?: string | null;
}

export interface DerivativeWorkItem {
  id: string;
  title: string;
  year?: number | null;
  out_degree: number;
  citation_key?: string | null;
}

export interface BibliometricCouplingEdge {
  paper_a_id: string;
  paper_b_id: string;
  shared_reference_count: number;
}

export interface BibliometricsResponseData {
  folder_id: string;
  prior_works: PriorWorkItem[];
  derivative_works: DerivativeWorkItem[];
  coupling_edges: BibliometricCouplingEdge[];
}
