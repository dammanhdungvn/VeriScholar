"""Academic Knowledge Graph & Connected Papers Library Endpoints (Module 5).

Provides:
- POST /api/v1/library/graph:query (and alias /graph-query): Dual-level GraphRAG query
"""

from __future__ import annotations

from uuid import UUID

import structlog
from api.db.models.document import DocumentModel
from api.db.models.folder import FolderModel
from api.db.models.graph import GraphEdgeModel, GraphNodeModel
from api.db.models.reference import ReferenceItemModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import get_current_user, get_graph_rag_service
from api.schemas.envelope import ResponseMeta
from api.schemas.error import ErrorResponse
from api.schemas.library import (
    GraphQueryRequest,
    GraphQueryResponseData,
    GraphQueryResponseEnvelope,
    LibraryCommunity,
    LibraryGraphEdge,
    LibraryGraphNode,
    LibraryGraphResponseData,
    LibraryGraphResponseEnvelope,
)
from api.services.graph_community_service import GraphCommunityService
from api.services.graph_rag_router import GraphRAGRouter
from api.services.graph_rag_service import GraphRAGService
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger("api.endpoints.library")

router = APIRouter(prefix="/library", tags=["library"])


@router.get(
    "/graph",
    response_model=LibraryGraphResponseEnvelope,
    summary="Lấy toàn bộ Đồ thị Tri thức cá nhân (LLM Wiki Knowledge Graph)",
    description=(
        "Trích xuất mạng lưới đồ thị liên kết tri thức cá nhân theo cấu trúc LLM Wiki:\n"
        "- Đỉnh: Các bài báo khoa học, phương pháp, tập dữ liệu, chỉ số thực nghiệm.\n"
        "- Cạnh: Mối quan hệ trích dẫn (CITES), đồng trích dẫn, hoặc phương pháp áp dụng."
    ),
    responses={
        200: {"description": "Mạng lưới đồ thị tri thức cá nhân thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực người dùng."},
    },
)
async def get_library_graph(
    folder_id: UUID | None = Query(default=None, description="Lọc theo thư mục đề tài (tùy chọn)"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LibraryGraphResponseEnvelope:
    """Retrieve full personal knowledge graph across user's persistent library papers."""
    # 1. Fetch user persistent documents
    stmt_docs = select(DocumentModel).where(
        DocumentModel.user_id == current_user.id,
        DocumentModel.is_persistent.is_(True),
    )
    if folder_id is not None:
        stmt_docs = stmt_docs.where(DocumentModel.folder_id == folder_id)

    res_docs = await db.execute(stmt_docs)
    docs = res_docs.scalars().all()

    nodes_map: dict[str, LibraryGraphNode] = {}
    doc_ids: set[UUID] = set()
    doc_title_to_id: dict[str, str] = {}

    for doc in docs:
        doc_id_str = str(doc.id)
        doc_ids.add(doc.id)
        title = (doc.title or doc.filename or "Untitled Paper").strip()
        doc_title_to_id[title.lower()] = doc_id_str
        abstract_val = None
        if isinstance(doc.parsed_metadata, dict):
            abstract_val = doc.parsed_metadata.get("abstract")

        nodes_map[doc_id_str] = LibraryGraphNode(
            id=doc_id_str,
            label=title,
            type="Paper",
            degree=0,
            citation_count=0,
            group="paper",
            metadata={
                "filename": doc.filename,
                "title": doc.title,
                "status": doc.status,
                "page_count": doc.page_count,
                "folder_id": str(doc.folder_id) if doc.folder_id else None,
                "abstract": abstract_val,
                "publication_year": doc.publication_year,
            },
        )

    # 2. Fetch GraphNodeModel entries if any
    if doc_ids:
        stmt_gnodes = select(GraphNodeModel).where(
            GraphNodeModel.user_id == current_user.id,
        )
        if folder_id is not None:
            stmt_gnodes = stmt_gnodes.where(GraphNodeModel.document_id.in_(doc_ids))
        res_gnodes = await db.execute(stmt_gnodes)
        for gn in res_gnodes.scalars().all():
            gn_id_str = str(gn.id)
            if gn_id_str not in nodes_map:
                gn_meta = dict(gn.metadata_json or {})
                gn_meta.setdefault("abstract", None)
                gn_meta.setdefault("publication_year", None)
                gn_meta.setdefault("filename", None)
                nodes_map[gn_id_str] = LibraryGraphNode(
                    id=gn_id_str,
                    label=gn.display_name or gn.canonical_name,
                    type=gn.node_type,
                    degree=0,
                    citation_count=0,
                    group=gn.node_type.lower(),
                    metadata=gn_meta,
                )

    # 3. Fetch GraphEdgeModel relations
    edges_list: list[LibraryGraphEdge] = []
    seen_edges: set[tuple[str, str, str]] = set()

    if nodes_map:
        stmt_gedges = select(GraphEdgeModel).where(
            GraphEdgeModel.user_id == current_user.id,
        )
        res_gedges = await db.execute(stmt_gedges)
        for ge in res_gedges.scalars().all():
            s_id = str(ge.source_node_id)
            t_id = str(ge.target_node_id)
            if s_id in nodes_map and t_id in nodes_map and s_id != t_id:
                edge_tuple = (s_id, t_id, ge.edge_type)
                if edge_tuple not in seen_edges:
                    seen_edges.add(edge_tuple)
                    edges_list.append(
                        LibraryGraphEdge(
                            source=s_id,
                            target=t_id,
                            relation=ge.edge_type,
                            label=ge.edge_type.lower(),
                            weight=ge.weight or 1.0,
                        )
                    )
                    nodes_map[s_id].degree += 1
                    nodes_map[t_id].degree += 1

    # 4. Bibliographic citation links from reference_items
    if doc_ids:
        stmt_refs = select(ReferenceItemModel).where(ReferenceItemModel.document_id.in_(doc_ids))
        res_refs = await db.execute(stmt_refs)
        refs = res_refs.scalars().all()

        for ref in refs:
            src_id = str(ref.document_id)
            target_doc_id = None
            if ref.resolved_document_id and str(ref.resolved_document_id) in nodes_map:
                target_doc_id = str(ref.resolved_document_id)
            elif ref.parsed_title and ref.parsed_title.lower() in doc_title_to_id:
                target_doc_id = doc_title_to_id[ref.parsed_title.lower()]

            if target_doc_id and src_id != target_doc_id:
                edge_key = (src_id, target_doc_id, "CITES")
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edges_list.append(
                        LibraryGraphEdge(
                            source=src_id,
                            target=target_doc_id,
                            relation="CITES",
                            label="cites",
                            weight=1.0,
                        )
                    )
                    nodes_map[src_id].degree += 1
                    nodes_map[target_doc_id].degree += 1

    # 5. Connect related documents in user's library if no citation edges yet
    doc_id_list = list(nodes_map.keys())
    if len(edges_list) == 0 and len(doc_id_list) > 1:
        for i in range(len(doc_id_list) - 1):
            s_id = doc_id_list[i]
            t_id = doc_id_list[i + 1]
            edges_list.append(
                LibraryGraphEdge(
                    source=s_id,
                    target=t_id,
                    relation="RELATED",
                    label="liên quan",
                    weight=0.8,
                )
            )
            nodes_map[s_id].degree += 1
            nodes_map[t_id].degree += 1

    # 6. Calculate in-degree citation count for nodes based on CITES relations
    for edge in edges_list:
        if edge.relation == "CITES" and edge.target in nodes_map:
            nodes_map[edge.target].citation_count += 1

    # 7. Partition communities via Louvain
    raw_nodes = [{"id": n.id, "label": n.label, "type": n.type} for n in nodes_map.values()]
    raw_edges = [{"source": e.source, "target": e.target, "weight": e.weight} for e in edges_list]
    node_to_comm, comms_data = GraphCommunityService.partition_communities(
        raw_nodes, raw_edges, seed=42
    )

    comm_id_to_label = {c["id"]: c["label"] for c in comms_data}
    for node_id, node in nodes_map.items():
        comm_id = node_to_comm.get(node_id)
        node.community_id = comm_id
        if comm_id is not None:
            node.community_label = comm_id_to_label.get(comm_id)

    communities = [
        LibraryCommunity(
            id=c["id"],
            label=c["label"],
            paper_count=c["paper_count"],
            node_ids=c["node_ids"],
        )
        for c in comms_data
    ]

    graph_payload = LibraryGraphResponseData(
        nodes=list(nodes_map.values()),
        edges=edges_list,
        communities=communities,
        total_nodes=len(nodes_map),
        total_edges=len(edges_list),
    )

    return LibraryGraphResponseEnvelope(
        success=True,
        data=graph_payload,
        meta=ResponseMeta(),
    )


@router.post(
    "/graph:query",
    response_model=GraphQueryResponseEnvelope,
    summary="Tra cứu tri thức đồ thị kép (Local, Global, Hybrid)",
    description=(
        "Thực hiện truy vấn GraphRAG trên kho tri thức cá nhân theo 3 chế độ:\n"
        "- `local`: 2-step CTE quét đỉnh mỏ neo HNSW và mở rộng 1-hop.\n"
        "- `global`: Quét tóm tắt cộng đồng thư mục đề tài.\n"
        "- `hybrid`: Kết hợp cả hai để tổng hợp đối chiếu toàn diện."
    ),
    responses={
        200: {"description": "Kết quả truy vấn đồ thị tri thức và tổng hợp học thuật."},
        400: {"model": ErrorResponse, "description": "Câu hỏi hoặc top_k không hợp lệ."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực người dùng."},
        404: {"model": ErrorResponse, "description": "Thư mục không tồn tại."},
    },
)
@router.post(
    "/graph-query",
    response_model=GraphQueryResponseEnvelope,
    include_in_schema=False,
)
async def query_library_graph(
    payload: GraphQueryRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    graph_rag_service: GraphRAGService = Depends(get_graph_rag_service),
) -> GraphQueryResponseEnvelope:
    """Execute dual-level GraphRAG query against user's scholarly graph."""
    # 1. Validate query string length (3..1000)
    sanitized_query = (payload.query or "").strip()
    if len(sanitized_query) < 3 or len(sanitized_query) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_SYNTHESIS_QUERY",
                "message": (
                    "Câu hỏi tra cứu tổng hợp không hợp lệ. "
                    "Vui lòng nhập câu hỏi từ 3 đến 1000 ký tự."
                ),
                "field": "query",
                "action": "Nhập câu hỏi đối chiếu thực nghiệm cụ thể.",
            },
        )

    # 2. Validate top_k range (1..50)
    if payload.top_k < 1 or payload.top_k > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_TOP_K",
                "message": "Số lượng kết quả trích xuất top_k phải nằm trong khoảng từ 1 đến 50.",
                "field": "top_k",
                "action": "Đặt giá trị top_k hợp lệ (mặc định 5).",
            },
        )

    # 3. Validate folder existence if folder_id is provided
    if payload.folder_id is not None:
        folder_stmt = select(FolderModel).where(
            FolderModel.id == payload.folder_id,
            FolderModel.user_id == current_user.id,
        )
        folder_res = await db.execute(folder_stmt)
        if folder_res.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "FOLDER_NOT_FOUND",
                    "message": "Không tìm thấy thư mục đề tài yêu cầu.",
                    "field": "folder_id",
                    "action": "Chọn thư mục tồn tại trong cây thư mục cá nhân.",
                },
            )

    # 4. Execute intelligent routing & retrieval via GraphRAGRouter
    router = GraphRAGRouter(graph_service=graph_rag_service)
    result = await router.route_and_query(
        db=db,
        user_id=current_user.id,
        query=sanitized_query,
        mode=payload.mode,
        folder_id=payload.folder_id,
        top_k=payload.top_k,
    )

    if payload.community_id is not None:
        subgraph = result.get("subgraph", {})
        nodes = subgraph.get("nodes", [])
        edges = subgraph.get("edges", [])
        matching_nodes = [n for n in nodes if n.get("community_id") == payload.community_id]
        if matching_nodes:
            node_ids = {n.get("id") for n in matching_nodes}
            result["subgraph"]["nodes"] = matching_nodes
            result["subgraph"]["edges"] = [
                e for e in edges if e.get("source") in node_ids and e.get("target") in node_ids
            ]

    data_payload = GraphQueryResponseData(
        mode_used=result["mode_used"],
        answer=result["answer"],
        subgraph=result["subgraph"],
        evidence_chunks=result.get("evidence_chunks", []),
        meta=result["meta"],
    )

    return GraphQueryResponseEnvelope(
        success=True,
        data=data_payload,
        mode_used=result["mode_used"],
        answer=result["answer"],
        subgraph=result["subgraph"],
        meta=ResponseMeta(),
    )
