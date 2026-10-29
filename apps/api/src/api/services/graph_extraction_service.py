"""Academic Knowledge Graph Extraction and Semantic Disambiguation Service.

Provides structured academic entity extraction, incremental LightRAG graph ingestion
with cosine >= 0.90 disambiguation hubs, and orphan-safe document graph pruning.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any
from uuid import UUID

import httpx
import structlog
from api.core.config import settings
from api.db.models.chunk import DocumentChunkModel
from api.db.models.graph import GraphEdgeModel, GraphNodeModel
from api.services.embedding_service import EmbeddingService
from core.services.graph_extractor import (
    VALID_EDGE_TYPES,
    VALID_NODE_TYPES,
    ExtractedEntity,
    ExtractedGraphPayload,
    ExtractedRelation,
    MetricContextTuple,
    normalize_canonical_name,
)
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger("api.services.graph_extraction")


def _safe_canonical_name(name: str, max_len: int = 250) -> str:
    """Safely truncate or hash canonical name to never exceed max_len (<= 255 chars)."""
    if len(name) <= max_len:
        return name
    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()[:16]
    prefix_len = max_len - 17
    return f"{name[:prefix_len]}_{digest}"


class GraphExtractionService:
    """Service for extracting, disambiguating, and managing 4-entity academic graphs."""

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        openai_client: Any | None = None,
    ) -> None:
        self.embedding_service = embedding_service
        self.openai_client = openai_client

    async def extract_paper_entities(self, document_id: UUID, text: str) -> ExtractedGraphPayload:
        """Extract academic entities and relations from paper text.

        Uses OpenAI Structured Outputs when available, with a deterministic
        rule-based fallback parser for offline/test environments.
        """
        stripped = text.strip() if text else ""
        if not stripped:
            return ExtractedGraphPayload(entities=[], relations=[])

        # 1. Direct JSON check
        if stripped.startswith("{") and stripped.endswith("}"):
            try:
                return ExtractedGraphPayload.model_validate_json(stripped)
            except Exception:
                pass

        # 2. OpenAI Structured Outputs if client or API key is configured
        if self.openai_client is not None or (
            settings.OPENAI_API_KEY is not None and settings.ENVIRONMENT != "test"
        ):
            try:
                extracted = await self._call_openai_structured_extraction(text)
                if extracted is not None:
                    return extracted
            except Exception as err:
                logger.warning(
                    "openai_extraction_failed_fallback_to_rules",
                    document_id=str(document_id),
                    error=str(err),
                )

        # 3. Rule-based offline fallback parser
        return self._fallback_rule_based_parser(text)

    async def _call_openai_structured_extraction(self, text: str) -> ExtractedGraphPayload | None:
        """Call OpenAI chat completion with strict JSON Schema structured output."""
        api_key = ""
        if settings.OPENAI_API_KEY is not None:
            api_key = settings.OPENAI_API_KEY.get_secret_value()
        base_url = (settings.OPENAI_BASE_URL or "https://api.openai.com/v1").rstrip("/")

        json_schema = {
            "name": "extracted_academic_graph",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": ["Paper", "Method", "Dataset", "MetricResult"],
                                },
                                "name": {"type": "string"},
                                "description": {"type": ["string", "null"]},
                                "page_number": {"type": "integer"},
                                "context_tuple": {
                                    "type": ["object", "null"],
                                    "properties": {
                                        "dataset": {"type": ["string", "null"]},
                                        "task": {"type": ["string", "null"]},
                                        "split": {"type": ["string", "null"]},
                                        "metric_name": {"type": ["string", "null"]},
                                        "value": {"type": ["number", "null"]},
                                        "unit": {"type": ["string", "null"]},
                                    },
                                    "required": [
                                        "dataset",
                                        "task",
                                        "split",
                                        "metric_name",
                                        "value",
                                        "unit",
                                    ],
                                    "additionalProperties": False,
                                },
                            },
                            "required": [
                                "type",
                                "name",
                                "page_number",
                                "description",
                                "context_tuple",
                            ],
                            "additionalProperties": False,
                        },
                    },
                    "relations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "source_name": {"type": "string"},
                                "target_name": {"type": "string"},
                                "type": {
                                    "type": "string",
                                    "enum": ["PROPOSES", "EVALUATED_ON", "ACHIEVES", "CITES"],
                                },
                                "page_number": {"type": "integer"},
                            },
                            "required": ["source_name", "target_name", "type", "page_number"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["entities", "relations"],
                "additionalProperties": False,
            },
        }

        system_prompt = (
            "You are an academic knowledge graph extractor for scholarly literature. "
            "Extract entities (Paper, Method, Dataset, MetricResult) and directed relations "
            "(PROPOSES, EVALUATED_ON, ACHIEVES, CITES) adhering strictly to the schema."
        )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text[:12000]},
            ],
            "response_format": {"type": "json_schema", "json_schema": json_schema},
            "temperature": 0.0,
        }

        if self.openai_client is not None:
            if hasattr(self.openai_client, "post"):
                resp = await self.openai_client.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                if hasattr(resp, "raise_for_status"):
                    resp.raise_for_status()
                data = resp.json() if callable(resp.json) else resp.json
                raw_content = data["choices"][0]["message"]["content"]
                if isinstance(raw_content, str):
                    return ExtractedGraphPayload.model_validate_json(raw_content)
                return ExtractedGraphPayload.model_validate(raw_content)
            elif hasattr(self.openai_client, "chat") and hasattr(
                self.openai_client.chat, "completions"
            ):
                resp = await self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=payload["messages"],
                    response_format=payload["response_format"],
                    temperature=0.0,
                )
                raw_content = resp.choices[0].message.content
                if isinstance(raw_content, str):
                    return ExtractedGraphPayload.model_validate_json(raw_content)
                return ExtractedGraphPayload.model_validate(raw_content)
            else:
                raise TypeError(f"Unsupported openai_client type: {type(self.openai_client)}")

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_content = data["choices"][0]["message"]["content"]
            return ExtractedGraphPayload.model_validate_json(raw_content)

    def _fallback_rule_based_parser(self, text: str) -> ExtractedGraphPayload:
        """Deterministic regex-based fallback extractor for tests and offline usage."""
        entities: list[ExtractedEntity] = []
        relations: list[ExtractedRelation] = []

        seen_entities: dict[str, ExtractedEntity] = {}

        # 1. Parse line by line
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        entity_pattern = re.compile(
            r"^(Paper|Method|Dataset|MetricResult)\s*:\s*(.+)$", re.IGNORECASE
        )
        relation_pattern = re.compile(
            r"^(.+?)\s+(PROPOSES|EVALUATED_ON|ACHIEVES|CITES)\s+(.+?)(?:\s*\(p\.?(\d+)\))?$",
            re.IGNORECASE,
        )

        for line in lines:
            ent_m = entity_pattern.match(line)
            if ent_m:
                etype_raw = ent_m.group(1).capitalize()
                raw_name = ent_m.group(2).strip()

                # Normalize valid entity type
                etype = next((t for t in VALID_NODE_TYPES if t.lower() == etype_raw.lower()), None)
                if not etype:
                    continue

                context_tuple = None
                clean_name = raw_name
                # Parse optional context tuple inside parentheses e.g. "BLEU: 28.4 (split=test)"
                if "(" in raw_name and raw_name.endswith(")"):
                    name_part, ctx_part = raw_name[:-1].split("(", 1)
                    clean_name = name_part.strip()
                    ctx_dict: dict[str, Any] = {}
                    for item in ctx_part.split(","):
                        if "=" in item:
                            k, v = item.split("=", 1)
                            k, v = k.strip().lower(), v.strip()
                            if k == "value":
                                try:
                                    ctx_dict[k] = float(v)
                                except ValueError:
                                    pass
                            else:
                                ctx_dict[k] = v
                    if ctx_dict:
                        context_tuple = MetricContextTuple(**ctx_dict)

                entity = ExtractedEntity(
                    type=etype,  # type: ignore[arg-type]
                    name=clean_name,
                    page_number=1,
                    context_tuple=context_tuple,
                )
                seen_entities[clean_name] = entity
                entities.append(entity)
                continue

            rel_m = relation_pattern.match(line)
            if rel_m:
                src = rel_m.group(1).strip()
                rel_type_raw = rel_m.group(2).upper()
                tgt = rel_m.group(3).strip()
                page = int(rel_m.group(4)) if rel_m.group(4) else 1

                rel_type = next((r for r in VALID_EDGE_TYPES if r == rel_type_raw), None)
                if rel_type:
                    relations.append(
                        ExtractedRelation(
                            source_name=src,
                            target_name=tgt,
                            type=rel_type,  # type: ignore[arg-type]
                            page_number=page,
                        )
                    )

        # If entities were parsed but no explicit relations, infer canonical relations
        if entities and not relations:
            papers = [e for e in entities if e.type == "Paper"]
            methods = [e for e in entities if e.type == "Method"]
            datasets = [e for e in entities if e.type == "Dataset"]
            metrics = [e for e in entities if e.type == "MetricResult"]

            if papers and methods:
                for p in papers:
                    for m in methods:
                        relations.append(
                            ExtractedRelation(
                                source_name=p.name,
                                target_name=m.name,
                                type="PROPOSES",
                                page_number=m.page_number,
                            )
                        )
            if methods and datasets:
                for m in methods:
                    for d in datasets:
                        relations.append(
                            ExtractedRelation(
                                source_name=m.name,
                                target_name=d.name,
                                type="EVALUATED_ON",
                                page_number=d.page_number,
                            )
                        )
            elif papers and datasets:
                for p in papers:
                    for d in datasets:
                        relations.append(
                            ExtractedRelation(
                                source_name=p.name,
                                target_name=d.name,
                                type="EVALUATED_ON",
                                page_number=d.page_number,
                            )
                        )
            if methods and metrics:
                for m in methods:
                    for r in metrics:
                        relations.append(
                            ExtractedRelation(
                                source_name=m.name,
                                target_name=r.name,
                                type="ACHIEVES",
                                page_number=r.page_number,
                            )
                        )
            elif papers and metrics:
                for p in papers:
                    for r in metrics:
                        relations.append(
                            ExtractedRelation(
                                source_name=p.name,
                                target_name=r.name,
                                type="ACHIEVES",
                                page_number=r.page_number,
                            )
                        )

        return ExtractedGraphPayload(entities=entities, relations=relations)

    async def ingest_paper_graph(
        self,
        db: AsyncSession,
        user_id: UUID,
        document_id: UUID,
        payload: ExtractedGraphPayload,
    ) -> dict[str, int]:
        """Ingest extracted entities and relations into graph_nodes and graph_edges.

        Applies Cosine >= 0.90 semantic entity disambiguation for Hub merging.
        Preserves independent contextual bindings for MetricResult entities.
        """
        nodes_created = 0
        nodes_merged = 0
        edges_created = 0

        # Mapping from entity name variants to resolved node ID
        entity_name_to_node_id: dict[str, UUID] = {}

        for entity in payload.entities:
            # MetricResult nodes are contextual bindings specific to an evaluation/document
            if entity.type == "MetricResult":
                ctx = entity.context_tuple
                tokens = [normalize_canonical_name(entity.name)]
                if ctx:
                    if ctx.dataset:
                        tokens.append(normalize_canonical_name(ctx.dataset))
                    if ctx.split:
                        tokens.append(normalize_canonical_name(ctx.split))
                    if ctx.task:
                        tokens.append(normalize_canonical_name(ctx.task))
                    if ctx.value is not None:
                        tokens.append(str(ctx.value))
                tokens.append(str(document_id))
                canonical_name = "::".join(tokens)
            else:
                canonical_name = normalize_canonical_name(entity.name)

            if len(canonical_name) > 250:
                canonical_name = _safe_canonical_name(canonical_name, max_len=250)

            # Compute embedding if service available
            v_entity: list[float] | None = None
            if self.embedding_service is not None:
                try:
                    v_entity = await self.embedding_service.get_embedding(entity.name)
                except Exception as err:
                    logger.warning(
                        "embedding_failed_for_entity",
                        entity_name=entity.name,
                        error=str(err),
                    )

            # Step 1: Check exact canonical name match
            stmt_exact = select(GraphNodeModel).where(
                GraphNodeModel.user_id == user_id,
                GraphNodeModel.node_type == entity.type,
                GraphNodeModel.canonical_name == canonical_name,
            )
            res_exact = await db.execute(stmt_exact)
            matched_node = res_exact.scalar_one_or_none()

            # Step 2: Semantic disambiguation (Cosine >= 0.90) for non-Metric entities
            if matched_node is None and entity.type != "MetricResult" and v_entity is not None:
                stmt_candidate = (
                    select(
                        GraphNodeModel,
                        (1.0 - GraphNodeModel.embedding.cosine_distance(v_entity)).label("sim"),
                    )
                    .where(
                        GraphNodeModel.user_id == user_id,
                        GraphNodeModel.node_type == entity.type,
                        GraphNodeModel.embedding.is_not(None),
                    )
                    .order_by(GraphNodeModel.embedding.cosine_distance(v_entity).asc())
                    .limit(1)
                )
                res_cand = await db.execute(stmt_candidate)
                cand_row = res_cand.first()
                # Threshold Cosine >= 0.90 (tolerance for floating point 0.89999)
                if cand_row and cand_row.sim is not None and cand_row.sim >= 0.89999:
                    matched_node = cand_row[0]

            if matched_node is not None:
                # Reusing existing Hub node
                nodes_merged += 1
                # Update aliases in metadata_json if new variation
                meta = dict(matched_node.metadata_json or {})
                aliases = list(meta.get("aliases") or [])
                if entity.name not in aliases and entity.name != matched_node.display_name:
                    aliases.append(entity.name)
                    meta["aliases"] = aliases
                    matched_node.metadata_json = meta
                    db.add(matched_node)

                resolved_node_id = matched_node.id
            else:
                # Create a new graph node
                if entity.type == "MetricResult":
                    meta = {}
                    if entity.context_tuple:
                        meta = entity.context_tuple.model_dump(exclude_none=True)
                    meta["page_number"] = entity.page_number
                else:
                    meta = {"aliases": [entity.name]}
                    if entity.description:
                        meta["description"] = entity.description

                display_name = entity.name[:255] if len(entity.name) > 255 else entity.name
                new_node = GraphNodeModel(
                    user_id=user_id,
                    document_id=document_id,
                    node_type=entity.type,
                    canonical_name=canonical_name,
                    display_name=display_name,
                    description=entity.description,
                    metadata_json=meta,
                    embedding=v_entity,
                )
                db.add(new_node)
                await db.flush()
                nodes_created += 1
                resolved_node_id = new_node.id

            entity_name_to_node_id[entity.name] = resolved_node_id
            entity_name_to_node_id[normalize_canonical_name(entity.name)] = resolved_node_id
            entity_name_to_node_id[canonical_name] = resolved_node_id

        # Step 3: Ingest edges connecting resolved nodes
        for rel in payload.relations:
            src_id = entity_name_to_node_id.get(rel.source_name) or entity_name_to_node_id.get(
                normalize_canonical_name(rel.source_name)
            )
            tgt_id = entity_name_to_node_id.get(rel.target_name) or entity_name_to_node_id.get(
                normalize_canonical_name(rel.target_name)
            )

            # If node not in current payload mapping, attempt lookup in graph_nodes
            if src_id is None:
                src_canon = normalize_canonical_name(rel.source_name)
                if len(src_canon) > 250:
                    src_canon = _safe_canonical_name(src_canon, max_len=250)
                s_stmt = (
                    select(GraphNodeModel.id)
                    .where(
                        GraphNodeModel.user_id == user_id,
                        GraphNodeModel.canonical_name == src_canon,
                    )
                    .limit(1)
                )
                s_res = await db.execute(s_stmt)
                src_id = s_res.scalars().first()

            if tgt_id is None:
                tgt_canon = normalize_canonical_name(rel.target_name)
                if len(tgt_canon) > 250:
                    tgt_canon = _safe_canonical_name(tgt_canon, max_len=250)
                t_stmt = (
                    select(GraphNodeModel.id)
                    .where(
                        GraphNodeModel.user_id == user_id,
                        GraphNodeModel.canonical_name == tgt_canon,
                    )
                    .limit(1)
                )
                t_res = await db.execute(t_stmt)
                tgt_id = t_res.scalars().first()

            if src_id is None or tgt_id is None:
                logger.warning(
                    "relation_endpoint_unresolved",
                    source=rel.source_name,
                    target=rel.target_name,
                    type=rel.type,
                )
                continue

            # Check if edge already exists for this document
            stmt_edge_exist = select(GraphEdgeModel).where(
                GraphEdgeModel.user_id == user_id,
                GraphEdgeModel.document_id == document_id,
                GraphEdgeModel.source_node_id == src_id,
                GraphEdgeModel.target_node_id == tgt_id,
                GraphEdgeModel.edge_type == rel.type,
            )
            exist_edge_res = await db.execute(stmt_edge_exist)
            if exist_edge_res.scalar_one_or_none() is not None:
                continue

            # Query evidence chunk if page_number is provided
            evidence_chunk_id: UUID | None = None
            if rel.page_number is not None:
                chunk_stmt = (
                    select(DocumentChunkModel.id)
                    .where(
                        DocumentChunkModel.document_id == document_id,
                        DocumentChunkModel.page_number == rel.page_number,
                    )
                    .limit(1)
                )
                chunk_res = await db.execute(chunk_stmt)
                evidence_chunk_id = chunk_res.scalar_one_or_none()

            edge = GraphEdgeModel(
                user_id=user_id,
                document_id=document_id,
                source_node_id=src_id,
                target_node_id=tgt_id,
                edge_type=rel.type,
                weight=1.0,
                evidence_chunk_id=evidence_chunk_id,
                page_number=rel.page_number,
                metadata_json={"source": rel.source_name, "target": rel.target_name},
            )
            db.add(edge)
            edges_created += 1

        await db.flush()

        logger.info(
            "paper_graph_ingested",
            document_id=str(document_id),
            nodes_created=nodes_created,
            nodes_merged=nodes_merged,
            edges_created=edges_created,
        )

        return {
            "nodes_created": nodes_created,
            "nodes_merged": nodes_merged,
            "edges_created": edges_created,
        }

    async def prune_document_graph(
        self, db: AsyncSession, user_id: UUID, document_id: UUID
    ) -> dict[str, int]:
        """Prune all edges of document_id and cleanly purge orphan nodes.

        Preserves shared Hub nodes referenced by other documents, setting
        their document_id to NULL if formerly tied to the pruned document.
        """
        # 1. Identify all node IDs linked to edges of this document
        edge_nodes_stmt = select(
            GraphEdgeModel.source_node_id,
            GraphEdgeModel.target_node_id,
        ).where(
            GraphEdgeModel.user_id == user_id,
            GraphEdgeModel.document_id == document_id,
        )
        edge_nodes_res = await db.execute(edge_nodes_stmt)
        candidate_node_ids: set[UUID] = set()
        for src, tgt in edge_nodes_res.all():
            candidate_node_ids.add(src)
            candidate_node_ids.add(tgt)

        # Also collect nodes directly attributed to document_id
        doc_nodes_stmt = select(GraphNodeModel.id).where(
            GraphNodeModel.user_id == user_id,
            GraphNodeModel.document_id == document_id,
        )
        doc_nodes_res = await db.execute(doc_nodes_stmt)
        for n_id in doc_nodes_res.scalars().all():
            candidate_node_ids.add(n_id)

        # 2. Delete all edges belonging to document_id
        del_edges_stmt = delete(GraphEdgeModel).where(
            GraphEdgeModel.user_id == user_id,
            GraphEdgeModel.document_id == document_id,
        )
        del_res = await db.execute(del_edges_stmt)
        edges_deleted = del_res.rowcount or 0
        await db.flush()

        # 3. Sweep candidate nodes: prune orphans, preserve shared Hubs
        nodes_pruned = 0
        for node_id in candidate_node_ids:
            rem_edge_stmt = (
                select(func.count())
                .select_from(GraphEdgeModel)
                .where(
                    GraphEdgeModel.user_id == user_id,
                    (GraphEdgeModel.source_node_id == node_id)
                    | (GraphEdgeModel.target_node_id == node_id),
                )
            )
            rem_res = await db.execute(rem_edge_stmt)
            edge_count = rem_res.scalar_one()

            if edge_count == 0:
                # Node is an orphan: delete it safely
                del_node_stmt = delete(GraphNodeModel).where(
                    GraphNodeModel.id == node_id,
                    GraphNodeModel.user_id == user_id,
                )
                await db.execute(del_node_stmt)
                nodes_pruned += 1
            else:
                # Node is shared with other documents (Hub): preserve it!
                node_stmt = select(GraphNodeModel).where(
                    GraphNodeModel.id == node_id,
                    GraphNodeModel.user_id == user_id,
                )
                n_res = await db.execute(node_stmt)
                n = n_res.scalar_one_or_none()
                if n and n.document_id == document_id:
                    n.document_id = None
                    db.add(n)

        await db.flush()

        logger.info(
            "document_graph_pruned",
            document_id=str(document_id),
            edges_deleted=edges_deleted,
            nodes_pruned=nodes_pruned,
        )

        return {
            "edges_deleted": edges_deleted,
            "nodes_pruned": nodes_pruned,
        }
