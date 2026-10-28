"""GraphRAG Query Decomposer and Multi-Intent Router (Module 5).

Decomposes academic queries into macro, micro, and bibliometric intents,
and routes them through the appropriate dual-level graph retrieval pipelines.
"""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger("api.services.graph_rag_router")


class AcademicQueryDecomposer:
    """Decomposes an academic search or question into specific retrieval intents."""

    MACRO_KEYWORDS = [
        "tổng quan",
        "so sánh",
        "sota",
        "xu hướng",
        "overview",
        "survey",
        "comparison",
        "benchmark",
        "các mô hình",
        "toàn cảnh",
        "phân tích các",
        "phương pháp tiếp cận",
        "state-of-the-art",
        "cộng đồng",
        "macro",
    ]

    MICRO_KEYWORDS = [
        "công thức",
        "kết quả",
        "số liệu",
        "giảm bộ nhớ",
        "bleu",
        "accuracy",
        "thực thể",
        "chi tiết",
        "metric",
        "selective attention",
        "layer",
        "architecture",
        "loss",
        "dataset",
        "hiệu năng",
        "thực nghiệm",
        "micro",
    ]

    CITATION_KEYWORDS = [
        "trích dẫn",
        "nền tảng",
        "mối liên hệ",
        "citation",
        "reference",
        "prior work",
        "derivative",
        "nguồn gốc",
        "tác giả",
        "dòng họ",
    ]

    def decompose(self, query: str) -> list[str]:
        """Classify scholarly inquiry and return list of dispatched retrieval tool keys."""
        q = (query or "").lower().strip()
        dispatched: list[str] = []

        is_macro = any(kw in q for kw in self.MACRO_KEYWORDS)
        is_micro = any(kw in q for kw in self.MICRO_KEYWORDS)
        is_citation = any(kw in q for kw in self.CITATION_KEYWORDS)

        if is_macro:
            dispatched.append("community_macro_scan")
        if is_micro:
            dispatched.append("entity_subgraph_lookup")
        if is_citation:
            dispatched.append("bibliometric_graph_trace")

        # Default fallback to dual hybrid if no specific keywords matched
        if not dispatched:
            dispatched = ["community_macro_scan", "entity_subgraph_lookup"]

        return dispatched


class GraphRAGRouter:
    """Intelligently routes academic queries to optimal GraphRAG execution pipelines."""

    def __init__(self, graph_service: Any = None) -> None:
        self.graph_service = graph_service
        self.decomposer = AcademicQueryDecomposer()

    async def route_and_query(
        self,
        db: AsyncSession | None = None,
        user_id: UUID | None = None,
        query: str = "",
        mode: Literal["auto", "local", "global", "hybrid"] = "auto",
        folder_id: UUID | None = None,
        top_k: int = 5,
    ) -> dict[str, Any]:
        """Decompose query, resolve mode, execute GraphRAG retrieval, and bundle badges."""
        dispatched_tools = self.decomposer.decompose(query)

        # Resolve mode
        if mode != "auto":
            resolved_mode = mode
        else:
            has_macro = "community_macro_scan" in dispatched_tools
            has_micro = "entity_subgraph_lookup" in dispatched_tools
            if has_macro and has_micro:
                resolved_mode = "hybrid"
            elif has_macro:
                resolved_mode = "global"
            elif "entity_subgraph_lookup" in dispatched_tools:
                resolved_mode = "local"
            else:
                resolved_mode = "hybrid"

        logger.info(
            "graphrag_query_routed",
            query=query[:60],
            resolved_mode=resolved_mode,
            dispatched_tools=dispatched_tools,
        )

        res: dict[str, Any]
        if self.graph_service is not None and hasattr(self.graph_service, "query_graph"):
            res = await self.graph_service.query_graph(
                db=db,
                user_id=user_id,
                query=query,
                mode=resolved_mode,
                folder_id=folder_id,
                top_k=top_k,
            )
        else:
            res = {
                "mode_used": resolved_mode,
                "answer": "",
                "subgraph": {"nodes": [], "edges": [], "evidence": []},
                "evidence_chunks": [],
                "meta": {},
            }

        res["dispatched_tools"] = dispatched_tools
        if "meta" in res and isinstance(res["meta"], dict):
            res["meta"]["dispatched_tools"] = dispatched_tools
            res["meta"]["resolved_mode"] = resolved_mode

        return res
