"""Dual-Level GraphRAG Query Engine & Connected Papers Bibliometrics Service.

Provides:
1. 2-Step PostgreSQL CTE Graph Traversal (Local search via HNSW cosine + 1-hop expansion).
2. Hierarchical topic community search (Global search via folder community summaries).
3. Hybrid multi-scale knowledge synthesis.
4. Connected Papers Bibliometrics (Bibliographic Coupling CTE, Prior Works, Derivative Works).
"""

from __future__ import annotations

import json
from typing import Any, Literal
from uuid import UUID, uuid4

import httpx
import structlog
from api.core.config import settings
from api.services.embedding_service import EmbeddingService
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger("api.services.graph_rag")


class GraphRAGService:
    """Service for querying scholarly knowledge graphs and computing bibliometrics."""

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        openai_client: Any | None = None,
    ) -> None:
        self.embedding_service = embedding_service
        self.openai_client = openai_client

    async def query_graph(
        self,
        db: AsyncSession,
        user_id: UUID,
        query: str,
        mode: Literal["local", "global", "hybrid"] = "hybrid",
        folder_id: UUID | None = None,
        top_k: int = 5,
    ) -> dict[str, Any]:
        """Execute dual-level scholarly graph retrieval and answer synthesis.

        Parameters
        ----------
        db : AsyncSession
            Active database session.
        user_id : UUID
            Owner scholar identifier (enforces strict multi-tenant isolation).
        query : str
            Scholarly question or topic.
        mode : "local" | "global" | "hybrid"
            Search depth strategy.
        folder_id : UUID | None
            Optional target topic folder filter.
        top_k : int
            Number of anchor nodes or top community summaries to retrieve (1..50).
        """
        clamped_top_k = max(1, min(50, top_k))
        sanitized_query = query.strip() if query else ""

        # Compute query vector if embedding service is configured
        query_vec: list[float] | None = None
        if self.embedding_service is not None and sanitized_query:
            try:
                query_vec = await self.embedding_service.get_embedding(sanitized_query)
            except Exception as err:
                logger.warning("query_embedding_failed", query=sanitized_query, error=str(err))

        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        evidence_chunks: list[dict[str, Any]] = []
        summaries: list[dict[str, Any]] = []

        if mode in ("local", "hybrid"):
            local_bundle = await self._execute_2_step_cte(
                db=db,
                user_id=user_id,
                query=sanitized_query,
                query_vec=query_vec,
                folder_id=folder_id,
                top_k=clamped_top_k,
            )
            nodes = local_bundle["nodes"]
            edges = local_bundle["edges"]
            evidence_chunks = local_bundle["evidence"]

        if mode in ("global", "hybrid"):
            global_bundle = await self._execute_global_scan(
                db=db,
                user_id=user_id,
                query_vec=query_vec,
                folder_id=folder_id,
                top_k=clamped_top_k,
            )
            summaries = global_bundle["summaries"]
            if mode == "global":
                nodes = global_bundle["hub_nodes"]
                edges = []
                evidence_chunks = []
            else:
                # Hybrid: merge global hub nodes into local nodes if not already present
                existing_ids = {n["id"] for n in nodes}
                for hub in global_bundle["hub_nodes"]:
                    if hub["id"] not in existing_ids:
                        nodes.append(hub)
                        existing_ids.add(hub["id"])

        # Synthesize scholarly answer
        answer = await self._synthesize_answer(
            query=sanitized_query,
            mode=mode,
            summaries=summaries,
            nodes=nodes,
            edges=edges,
            evidence=evidence_chunks,
        )

        trace_id = f"trace-graph-{uuid4().hex[:8]}"

        subgraph_payload = {
            "nodes": nodes,
            "edges": edges,
            "evidence": evidence_chunks,
        }

        return {
            "mode_used": mode,
            "answer": answer,
            "subgraph": subgraph_payload,
            "evidence_chunks": evidence_chunks,
            "meta": {
                "trace_id": trace_id,
                "matched_entities": len(nodes),
                "folder_id": str(folder_id) if folder_id else None,
            },
        }

    async def compute_bibliometrics(
        self,
        db: AsyncSession,
        user_id: UUID,
        folder_id: UUID | None = None,
        min_shared_references: int = 2,
    ) -> dict[str, Any]:
        """Compute Connected Papers bibliometric metrics for a scholar's library or folder.

        1. Bibliographic Coupling: Pairs citing >= min_shared_references common references.
        2. Prior Works: Seminal works with highest In-Degree on CITES edges.
        3. Derivative Works: Recent works with highest Out-Degree on CITES edges.
        """
        clamped_min_shared = max(1, min_shared_references)

        # 1. Bibliographic Coupling CTE
        coupling_sql = text("""
            WITH paper_citations AS (
                SELECT 
                    e.source_node_id AS paper_id, 
                    e.target_node_id AS cited_ref_id
                FROM graph_edges e
                LEFT JOIN documents d ON d.id = e.document_id
                WHERE e.user_id = :user_id 
                  AND e.edge_type = 'CITES'
                  AND (CAST(:folder_id AS uuid) IS NULL OR d.folder_id = CAST(:folder_id AS uuid))
            )
            SELECT 
                c1.paper_id AS paper_a_id,
                c2.paper_id AS paper_b_id,
                COUNT(DISTINCT c1.cited_ref_id) AS shared_reference_count
            FROM paper_citations c1
            JOIN paper_citations c2 ON c1.cited_ref_id = c2.cited_ref_id 
                                   AND c1.paper_id < c2.paper_id
            GROUP BY c1.paper_id, c2.paper_id
            HAVING COUNT(DISTINCT c1.cited_ref_id) >= :min_shared_references
            ORDER BY shared_reference_count DESC;
        """)

        res_coupling = await db.execute(
            coupling_sql,
            {
                "user_id": user_id,
                "folder_id": folder_id,
                "min_shared_references": clamped_min_shared,
            },
        )
        coupling_edges = [
            {
                "paper_a_id": str(row.paper_a_id),
                "paper_b_id": str(row.paper_b_id),
                "shared_reference_count": int(row.shared_reference_count),
            }
            for row in res_coupling.all()
        ]

        # 2. Prior Works (Highest In-Degree on CITES)
        prior_sql = text("""
            WITH paper_citations AS (
                SELECT 
                    e.source_node_id AS citing_paper_id, 
                    e.target_node_id AS cited_ref_id
                FROM graph_edges e
                LEFT JOIN documents d ON d.id = e.document_id
                WHERE e.user_id = :user_id 
                  AND e.edge_type = 'CITES'
                  AND (CAST(:folder_id AS uuid) IS NULL OR d.folder_id = CAST(:folder_id AS uuid))
            )
            SELECT 
                n.id,
                n.display_name,
                n.canonical_name,
                n.metadata_json,
                COUNT(DISTINCT c.citing_paper_id) AS in_degree
            FROM paper_citations c
            JOIN graph_nodes n ON n.id = c.cited_ref_id
            WHERE n.user_id = :user_id
            GROUP BY n.id, n.display_name, n.canonical_name, n.metadata_json
            ORDER BY in_degree DESC, n.display_name ASC;
        """)

        res_prior = await db.execute(prior_sql, {"user_id": user_id, "folder_id": folder_id})
        prior_works = []
        for row in res_prior.all():
            meta = row.metadata_json or {}
            title = meta.get("title") or row.display_name or row.canonical_name
            year = meta.get("year") or meta.get("publication_year")
            citation_key = meta.get("citation_key") or f"ref_{str(row.id)[:8]}"
            prior_works.append(
                {
                    "id": str(row.id),
                    "title": title,
                    "year": year,
                    "in_degree": int(row.in_degree),
                    "citation_key": citation_key,
                }
            )

        # 3. Derivative Works (Highest Out-Degree on CITES)
        derivative_sql = text("""
            WITH paper_citations AS (
                SELECT 
                    e.source_node_id AS citing_paper_id, 
                    e.target_node_id AS cited_ref_id
                FROM graph_edges e
                LEFT JOIN documents d ON d.id = e.document_id
                WHERE e.user_id = :user_id 
                  AND e.edge_type = 'CITES'
                  AND (CAST(:folder_id AS uuid) IS NULL OR d.folder_id = CAST(:folder_id AS uuid))
            )
            SELECT 
                n.id,
                n.display_name,
                n.canonical_name,
                n.metadata_json,
                COUNT(DISTINCT c.cited_ref_id) AS out_degree
            FROM paper_citations c
            JOIN graph_nodes n ON n.id = c.citing_paper_id
            WHERE n.user_id = :user_id
            GROUP BY n.id, n.display_name, n.canonical_name, n.metadata_json
            ORDER BY out_degree DESC, n.display_name ASC;
        """)

        res_derivative = await db.execute(
            derivative_sql, {"user_id": user_id, "folder_id": folder_id}
        )
        derivative_works = []
        for row in res_derivative.all():
            meta = row.metadata_json or {}
            title = meta.get("title") or row.display_name or row.canonical_name
            year = meta.get("year") or meta.get("publication_year")
            citation_key = meta.get("citation_key") or f"ref_{str(row.id)[:8]}"
            derivative_works.append(
                {
                    "id": str(row.id),
                    "title": title,
                    "year": year,
                    "out_degree": int(row.out_degree),
                    "citation_key": citation_key,
                }
            )

        return {
            "folder_id": str(folder_id) if folder_id else None,
            "prior_works": prior_works,
            "derivative_works": derivative_works,
            "coupling_edges": coupling_edges,
        }

    async def _execute_2_step_cte(
        self,
        db: AsyncSession,
        user_id: UUID,
        query: str,
        query_vec: list[float] | None,
        folder_id: UUID | None,
        top_k: int,
    ) -> dict[str, Any]:
        """Execute 2-Step CTE: HNSW anchor search -> 1-hop traversal -> evidence chunks."""
        # 1. Anchor Search Clause
        if query_vec is not None:
            vec_str = f"[{','.join(str(f) for f in query_vec)}]"
            cte_sql = text("""
                WITH anchor_nodes AS (
                    SELECT 
                        id, 
                        node_type, 
                        canonical_name,
                        display_name,
                        metadata_json,
                        document_id,
                        1 - (embedding <=> CAST(:query_vec AS vector)) AS similarity
                    FROM graph_nodes
                    WHERE user_id = :user_id AND embedding IS NOT NULL
                    ORDER BY embedding <=> CAST(:query_vec AS vector)
                    LIMIT :top_k
                ),
                connected_edges AS (
                    SELECT 
                        e.id AS edge_id,
                        e.document_id,
                        e.source_node_id,
                        e.target_node_id,
                        e.edge_type,
                        e.metadata_json AS edge_metadata,
                        e.evidence_chunk_id,
                        e.page_number
                    FROM graph_edges e
                    LEFT JOIN documents d ON d.id = e.document_id
                    WHERE e.user_id = :user_id
                      AND (
                          CAST(:folder_id AS uuid) IS NULL 
                          OR d.folder_id = CAST(:folder_id AS uuid)
                      )
                      AND (
                          e.source_node_id IN (SELECT id FROM anchor_nodes)
                          OR e.target_node_id IN (SELECT id FROM anchor_nodes)
                      )
                ),
                neighbor_nodes AS (
                    SELECT DISTINCT
                        n.id,
                        n.node_type,
                        n.canonical_name,
                        n.display_name,
                        n.metadata_json,
                        n.document_id
                    FROM graph_nodes n
                    WHERE n.user_id = :user_id
                      AND n.id IN (
                        SELECT source_node_id FROM connected_edges
                        UNION
                        SELECT target_node_id FROM connected_edges
                      )
                ),
                evidence_chunks AS (
                    SELECT 
                        c.id AS chunk_id,
                        c.document_id,
                        c.page_number,
                        c.content AS chunk_text,
                        c.bounding_boxes AS bbox
                    FROM document_chunks c
                    WHERE c.user_id = :user_id
                      AND c.id IN (
                        SELECT evidence_chunk_id 
                        FROM connected_edges 
                        WHERE evidence_chunk_id IS NOT NULL
                      )
                )
                SELECT 
                    COALESCE((SELECT json_agg(a.*) FROM anchor_nodes a), '[]'::json) 
                        AS anchors,
                    COALESCE((SELECT json_agg(e.*) FROM connected_edges e), '[]'::json) 
                        AS edges,
                    COALESCE((SELECT json_agg(nb.*) FROM neighbor_nodes nb), '[]'::json) 
                        AS neighbors,
                    COALESCE((SELECT json_agg(ev.*) FROM evidence_chunks ev), '[]'::json) 
                        AS evidence;
            """)
            params: dict[str, Any] = {
                "user_id": user_id,
                "query_vec": vec_str,
                "top_k": top_k,
                "folder_id": folder_id,
            }
        else:
            # Fallback text keyword anchor match when embedding vector is absent
            pattern = f"%{query}%" if query else "%"
            cte_sql = text("""
                WITH anchor_nodes AS (
                    SELECT 
                        id, 
                        node_type, 
                        canonical_name,
                        display_name,
                        metadata_json,
                        document_id,
                        1.0 AS similarity
                    FROM graph_nodes
                    WHERE user_id = :user_id
                      AND (canonical_name ILIKE :pattern OR display_name ILIKE :pattern)
                    LIMIT :top_k
                ),
                connected_edges AS (
                    SELECT 
                        e.id AS edge_id,
                        e.document_id,
                        e.source_node_id,
                        e.target_node_id,
                        e.edge_type,
                        e.metadata_json AS edge_metadata,
                        e.evidence_chunk_id,
                        e.page_number
                    FROM graph_edges e
                    LEFT JOIN documents d ON d.id = e.document_id
                    WHERE e.user_id = :user_id
                      AND (
                          CAST(:folder_id AS uuid) IS NULL 
                          OR d.folder_id = CAST(:folder_id AS uuid)
                      )
                      AND (
                          e.source_node_id IN (SELECT id FROM anchor_nodes)
                          OR e.target_node_id IN (SELECT id FROM anchor_nodes)
                      )
                ),
                neighbor_nodes AS (
                    SELECT DISTINCT
                        n.id,
                        n.node_type,
                        n.canonical_name,
                        n.display_name,
                        n.metadata_json,
                        n.document_id
                    FROM graph_nodes n
                    WHERE n.user_id = :user_id
                      AND n.id IN (
                        SELECT source_node_id FROM connected_edges
                        UNION
                        SELECT target_node_id FROM connected_edges
                      )
                ),
                evidence_chunks AS (
                    SELECT 
                        c.id AS chunk_id,
                        c.document_id,
                        c.page_number,
                        c.content AS chunk_text,
                        c.bounding_boxes AS bbox
                    FROM document_chunks c
                    WHERE c.user_id = :user_id
                      AND c.id IN (
                        SELECT evidence_chunk_id 
                        FROM connected_edges 
                        WHERE evidence_chunk_id IS NOT NULL
                      )
                )
                SELECT 
                    COALESCE((SELECT json_agg(a.*) FROM anchor_nodes a), '[]'::json) 
                        AS anchors,
                    COALESCE((SELECT json_agg(e.*) FROM connected_edges e), '[]'::json) 
                        AS edges,
                    COALESCE((SELECT json_agg(nb.*) FROM neighbor_nodes nb), '[]'::json) 
                        AS neighbors,
                    COALESCE((SELECT json_agg(ev.*) FROM evidence_chunks ev), '[]'::json) 
                        AS evidence;
            """)
            params = {
                "user_id": user_id,
                "pattern": pattern,
                "top_k": top_k,
                "folder_id": folder_id,
            }

        res = await db.execute(cte_sql, params)
        row = res.mappings().first()
        if not row:
            return {"nodes": [], "edges": [], "evidence": []}

        raw_anchors = row.get("anchors") or []
        raw_edges = row.get("edges") or []
        raw_neighbors = row.get("neighbors") or []
        raw_evidence = row.get("evidence") or []

        # If parsed as string JSON by DB driver, parse to python list
        anchors_list = json.loads(raw_anchors) if isinstance(raw_anchors, str) else raw_anchors
        edges_list = json.loads(raw_edges) if isinstance(raw_edges, str) else raw_edges
        neighbors_list = (
            json.loads(raw_neighbors) if isinstance(raw_neighbors, str) else raw_neighbors
        )
        evidence_list = json.loads(raw_evidence) if isinstance(raw_evidence, str) else raw_evidence

        # Build clean edge dictionary
        formatted_edges = []
        for e in edges_list:
            formatted_edges.append(
                {
                    "id": str(e.get("edge_id") or e.get("id")),
                    "document_id": str(e["document_id"]) if e.get("document_id") else None,
                    "source": str(e["source_node_id"]),
                    "target": str(e["target_node_id"]),
                    "type": e["edge_type"],
                    "evidence_chunk_id": str(e["evidence_chunk_id"])
                    if e.get("evidence_chunk_id")
                    else None,
                    "page_number": e.get("page_number"),
                    "metadata": e.get("edge_metadata") or {},
                }
            )

        # Merge unique nodes from anchors and neighbors
        nodes_by_id: dict[str, dict[str, Any]] = {}
        for n in anchors_list + neighbors_list:
            nid = str(n["id"])
            if nid not in nodes_by_id:
                nodes_by_id[nid] = n

        formatted_nodes = []
        for nid, n in nodes_by_id.items():
            meta = n.get("metadata_json") or {}
            node_type = n.get("node_type", "Paper")
            display_name = n.get("display_name") or n.get("canonical_name", "")

            # Degree centrality = count of connected edges in this subgraph
            degree = sum(1 for e in formatted_edges if e["source"] == nid or e["target"] == nid)

            # Assign role
            if node_type == "Method":
                role = "method_hub"
            elif node_type == "MetricResult":
                role = "metric"
            elif node_type == "Dataset":
                role = "dataset"
            elif node_type == "Paper":
                in_cites = sum(
                    1 for e in formatted_edges if e["target"] == nid and e["type"] == "CITES"
                )
                out_cites = sum(
                    1 for e in formatted_edges if e["source"] == nid and e["type"] == "CITES"
                )
                if in_cites > out_cites:
                    role = "prior_work"
                elif out_cites > in_cites:
                    role = "derivative_work"
                else:
                    yr = meta.get("year")
                    if yr and yr <= 2018:
                        role = "prior_work"
                    elif yr and yr > 2018:
                        role = "derivative_work"
                    else:
                        role = "prior_work"
            else:
                role = "node"

            node_item: dict[str, Any] = {
                "id": nid,
                "type": node_type,
                "name": display_name,
                "degree_centrality": degree,
                "role": role,
            }
            if "year" in meta:
                node_item["year"] = meta["year"]
            if meta:
                node_item["metadata"] = meta

            formatted_nodes.append(node_item)

        # Format evidence chunks
        formatted_evidence = []
        for ev in evidence_list:
            formatted_evidence.append(
                {
                    "chunk_id": str(ev.get("chunk_id") or ev.get("id")),
                    "document_id": str(ev["document_id"]) if ev.get("document_id") else None,
                    "page_number": ev.get("page_number"),
                    "chunk_text": ev.get("chunk_text") or "",
                    "bbox": ev.get("bbox") or [],
                }
            )

        return {
            "nodes": formatted_nodes,
            "edges": formatted_edges,
            "evidence": formatted_evidence,
        }

    async def _execute_global_scan(
        self,
        db: AsyncSession,
        user_id: UUID,
        query_vec: list[float] | None,
        folder_id: UUID | None,
        top_k: int,
    ) -> dict[str, Any]:
        """Scan folder community summaries and hub nodes for macroscopic analysis."""
        summaries: list[dict[str, Any]] = []

        if query_vec is not None:
            summary_sql = text("""
                SELECT 
                    id, 
                    folder_id, 
                    summary_text, 
                    key_findings,
                    1 - (embedding <=> CAST(:query_vec AS vector)) AS similarity
                FROM folder_community_summaries
                WHERE user_id = :user_id
                  AND (CAST(:folder_id AS uuid) IS NULL OR folder_id = CAST(:folder_id AS uuid))
                  AND embedding IS NOT NULL
                ORDER BY embedding <=> CAST(:query_vec AS vector)
                LIMIT :top_k;
            """)
            res_sum = await db.execute(
                summary_sql,
                {
                    "user_id": user_id,
                    "folder_id": folder_id,
                    "query_vec": f"[{','.join(str(f) for f in query_vec)}]",
                    "top_k": top_k,
                },
            )
            rows = res_sum.mappings().all()
            for r in rows:
                summaries.append(
                    {
                        "id": str(r["id"]),
                        "folder_id": str(r["folder_id"]) if r.get("folder_id") else None,
                        "summary_text": r["summary_text"],
                        "key_findings": r["key_findings"] or [],
                    }
                )

        if not summaries:
            # Fallback scan without vector distance
            summary_sql_basic = text("""
                SELECT id, folder_id, summary_text, key_findings
                FROM folder_community_summaries
                WHERE user_id = :user_id
                  AND (CAST(:folder_id AS uuid) IS NULL OR folder_id = CAST(:folder_id AS uuid))
                LIMIT :top_k;
            """)
            res_sum = await db.execute(
                summary_sql_basic,
                {"user_id": user_id, "folder_id": folder_id, "top_k": top_k},
            )
            for r in res_sum.mappings().all():
                summaries.append(
                    {
                        "id": str(r["id"]),
                        "folder_id": str(r["folder_id"]) if r.get("folder_id") else None,
                        "summary_text": r["summary_text"],
                        "key_findings": r["key_findings"] or [],
                    }
                )

        # Retrieve top Hub nodes (Methods and Datasets) for the user or folder
        hubs_sql = text("""
            SELECT 
                n.id, 
                n.node_type, 
                n.canonical_name, 
                n.display_name, 
                n.metadata_json,
                COUNT(e.id) AS deg
            FROM graph_nodes n
            LEFT JOIN graph_edges e 
                ON (e.source_node_id = n.id OR e.target_node_id = n.id) 
                AND e.user_id = :user_id
            WHERE n.user_id = :user_id
              AND (
                  CAST(:folder_id AS uuid) IS NULL 
                  OR e.document_id IN (
                      SELECT id FROM documents 
                      WHERE folder_id = CAST(:folder_id AS uuid) AND user_id = :user_id
                  )
                  OR n.document_id IN (
                      SELECT id FROM documents 
                      WHERE folder_id = CAST(:folder_id AS uuid) AND user_id = :user_id
                  )
                  OR n.node_type IN ('Method', 'Dataset')
              )
            GROUP BY n.id, n.node_type, n.canonical_name, n.display_name, n.metadata_json
            ORDER BY deg DESC, n.display_name ASC
            LIMIT :top_k;
        """)
        res_hubs = await db.execute(
            hubs_sql, {"user_id": user_id, "folder_id": folder_id, "top_k": top_k}
        )
        hub_nodes = []
        for r in res_hubs.mappings().all():
            meta = r["metadata_json"] or {}
            ntype = r["node_type"]
            if ntype == "Method":
                role = "method_hub"
            elif ntype == "Dataset":
                role = "dataset"
            else:
                role = "node"
            hub_nodes.append(
                {
                    "id": str(r["id"]),
                    "type": ntype,
                    "name": r["display_name"] or r["canonical_name"],
                    "degree_centrality": int(r["deg"]),
                    "role": role,
                    "metadata": meta,
                }
            )

        return {"summaries": summaries, "hub_nodes": hub_nodes}

    async def _synthesize_answer(
        self,
        query: str,
        mode: str,
        summaries: list[dict[str, Any]],
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        evidence: list[dict[str, Any]],
    ) -> str:
        """Synthesize answers via LLM when available, or deterministic template fallback."""
        if self.openai_client is not None or (
            settings.OPENAI_API_KEY is not None and settings.ENVIRONMENT != "test"
        ):
            try:
                llm_answer = await self._call_openai_synthesis(
                    query=query,
                    mode=mode,
                    summaries=summaries,
                    nodes=nodes,
                    edges=edges,
                    evidence=evidence,
                )
                if llm_answer and len(llm_answer.strip()) > 10:
                    return llm_answer.strip()
            except Exception as err:
                logger.warning("llm_answer_synthesis_failed", error=str(err))

        return self._deterministic_template_synthesis(
            mode=mode,
            summaries=summaries,
            nodes=nodes,
            edges=edges,
            evidence=evidence,
        )

    async def _call_openai_synthesis(
        self,
        query: str,
        mode: str,
        summaries: list[dict[str, Any]],
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        evidence: list[dict[str, Any]],
    ) -> str:
        """Call OpenAI chat model to generate a cohesive scholarly synthesis."""
        api_key = ""
        if settings.OPENAI_API_KEY is not None:
            api_key = settings.OPENAI_API_KEY.get_secret_value()
        base_url = (settings.OPENAI_BASE_URL or "https://api.openai.com/v1").rstrip("/")

        context_data = {
            "mode": mode,
            "summaries": summaries,
            "nodes": [
                {
                    "type": n.get("type"),
                    "name": n.get("name"),
                    "role": n.get("role"),
                    "metadata": n.get("metadata"),
                }
                for n in nodes
            ],
            "evidence": [
                {"page": ev.get("page_number"), "text": ev.get("chunk_text")} for ev in evidence[:5]
            ],
        }

        system_prompt = (
            "Bạn là Trợ lý AI Nghiên cứu Khoa học VeriScholar. "
            "Dựa trên đồ thị tri thức 4 thực thể và các trích đoạn minh chứng dưới đây, "
            "hãy trả lời câu hỏi của học giả một cách chính xác, học thuật, cô đọng. "
            "Nếu có số liệu thực nghiệm, hãy dẫn chứng cụ thể kèm số trang."
        )

        ctx_json = json.dumps(context_data, ensure_ascii=False)
        user_content = f"Câu hỏi: {query}\n\nNgữ cảnh dữ liệu đồ thị:\n{ctx_json}"

        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.2,
        }

        if self.openai_client is not None:
            if hasattr(self.openai_client, "post"):
                resp = await self.openai_client.post(
                    f"{base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json=payload,
                )
                data = resp.json() if callable(resp.json) else resp.json
                return data["choices"][0]["message"]["content"]
            elif hasattr(self.openai_client, "chat") and hasattr(
                self.openai_client.chat, "completions"
            ):
                res = await self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=payload["messages"],
                    temperature=0.2,
                )
                return res.choices[0].message.content

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    def _deterministic_template_synthesis(
        self,
        mode: str,
        summaries: list[dict[str, Any]],
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        evidence: list[dict[str, Any]],
    ) -> str:
        """Deterministic rule-based answer synthesis for offline or test execution."""
        # 1. Macro Community Section
        macro_parts: list[str] = []
        for s in summaries:
            txt = s.get("summary_text", "").strip()
            if txt:
                macro_parts.append(f"**Tổng quan đề tài:** {txt}")
            findings = s.get("key_findings")
            if isinstance(findings, list) and findings:
                finding_bullets = "\n".join(f"- {f}" for f in findings)
                macro_parts.append(f"**Phát hiện chính:**\n{finding_bullets}")

        # 2. Micro Evidence Section
        micro_parts: list[str] = []
        papers = [n for n in nodes if n.get("type") == "Paper"]
        methods = [n for n in nodes if n.get("type") == "Method"]
        metrics = [n for n in nodes if n.get("type") == "MetricResult"]
        datasets = [n for n in nodes if n.get("type") == "Dataset"]

        if papers:
            paper_bullets = []
            for p in papers:
                yr = f" ({p['year']})" if p.get("year") else ""
                role_label = (
                    " (Tác phẩm Cội nguồn)"
                    if p.get("role") == "prior_work"
                    else " (Tác phẩm Phái sinh)"
                    if p.get("role") == "derivative_work"
                    else ""
                )
                paper_bullets.append(f"- **{p['name']}**{yr}{role_label}")
            micro_parts.append("**Bài báo liên quan:**\n" + "\n".join(paper_bullets))

        if methods:
            method_names = [f"**{m['name']}**" for m in methods]
            micro_parts.append(f"**Kiến trúc & Phương pháp:** {', '.join(method_names)}")

        if datasets:
            dataset_names = [f"**{d['name']}**" for d in datasets]
            micro_parts.append(f"**Tập dữ liệu chuẩn:** {', '.join(dataset_names)}")

        if metrics:
            metric_bullets = []
            for m in metrics:
                meta = m.get("metadata") or {}
                val = meta.get("value", "")
                mname = meta.get("metric_name", m["name"])
                unit = f" {meta['unit']}" if meta.get("unit") else ""
                task = f" trên tác vụ {meta['task']}" if meta.get("task") else ""
                split = f" ({meta['split']} split)" if meta.get("split") else ""
                metric_bullets.append(f"- **{mname}**: {val}{unit}{task}{split}".strip())
            micro_parts.append("**Minh chứng Thực nghiệm:**\n" + "\n".join(metric_bullets))

        if evidence:
            ev_bullets = []
            for ev in evidence[:3]:
                pg = f" (Trang {ev['page_number']})" if ev.get("page_number") else ""
                txt = ev.get("chunk_text", "").strip()
                if txt:
                    ev_bullets.append(f'> "{txt}"{pg}')
            if ev_bullets:
                micro_parts.append("**Đoạn trích văn bản:**\n" + "\n".join(ev_bullets))

        # 3. Assemble based on requested mode
        if mode == "global":
            if macro_parts:
                return "\n\n".join(macro_parts)
            elif nodes:
                names = [n["name"] for n in nodes]
                return f"Tổng quan đề tài dựa trên các đỉnh tri thức: {', '.join(names)}."
            return "Không tìm thấy dữ liệu tóm tắt cộng đồng phù hợp trong thư mục."

        if mode == "local":
            if micro_parts:
                return (
                    "Trong Kho Yêu thích của bạn, kết quả phân tích vi mô từ đồ thị tri thức:\n\n"
                    + "\n\n".join(micro_parts)
                )
            return (
                "Không tìm thấy thực thể hoặc minh chứng thực nghiệm liên quan "
                "trong đồ thị cá nhân."
            )

        # mode == "hybrid"
        combined: list[str] = []
        if macro_parts:
            combined.extend(macro_parts)
        if micro_parts:
            combined.extend(micro_parts)

        if combined:
            return "\n\n".join(combined)
        return "Không tìm thấy thông tin tri thức phù hợp trong kho lưu trữ của bạn."
