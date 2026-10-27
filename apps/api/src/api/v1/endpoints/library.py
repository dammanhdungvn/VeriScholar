"""Academic Knowledge Graph & Connected Papers Library Endpoints (Module 5).

Provides:
- POST /api/v1/library/graph:query (and alias /graph-query): Dual-level GraphRAG query
"""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

import structlog
from api.db.models.folder import FolderModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import get_current_user, get_graph_rag_service
from api.schemas.envelope import ResponseMeta, SingleResponseEnvelope
from api.schemas.error import ErrorResponse
from api.services.graph_rag_service import GraphRAGService
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger("api.endpoints.library")

router = APIRouter(prefix="/library", tags=["library"])


class GraphQueryRequest(BaseModel):
    """Payload for querying the personal academic knowledge graph."""

    query: str = Field(
        ...,
        description="Scholarly synthesis or comparative question (3..1000 chars)",
        examples=["Các mô hình Transformer đạt kết quả BLEU và Accuracy như thế nào?"],
    )
    mode: Literal["local", "global", "hybrid"] = Field(
        default="hybrid",
        description=(
            "Search depth: 'local' (micro CTE), 'global' (macro community), 'hybrid' (combined)"
        ),
        examples=["hybrid"],
    )
    folder_id: UUID | None = Field(
        default=None,
        description="Optional folder UUID filter",
        examples=[None],
    )
    top_k: int = Field(
        default=5,
        description="Number of anchor nodes or top communities (1..50)",
        examples=[5],
    )


class GraphQueryResponseData(BaseModel):
    """Data payload returned by GraphRAG query."""

    mode_used: str = Field(description="Depth strategy used: local, global, or hybrid")
    answer: str = Field(description="Synthesized scholarly answer")
    subgraph: dict[str, Any] = Field(
        description="Extracted knowledge subgraph with nodes, edges, and evidence chunks"
    )
    evidence_chunks: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Grounding evidence chunks with page numbers and bounding boxes",
    )
    meta: dict[str, Any] = Field(
        default_factory=dict,
        description="Retrieval trace and match metadata",
    )


class GraphQueryResponseEnvelope(SingleResponseEnvelope[GraphQueryResponseData]):
    """Standard envelope for GraphRAG query with top-level field mirrors for Spec 05 contract."""

    mode_used: str | None = Field(default=None, description="Direct mirror of mode_used")
    answer: str | None = Field(default=None, description="Direct mirror of answer")
    subgraph: dict[str, Any] | None = Field(default=None, description="Direct mirror of subgraph")


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

    # 4. Execute dual-level retrieval & synthesis
    result = await graph_rag_service.query_graph(
        db=db,
        user_id=current_user.id,
        query=sanitized_query,
        mode=payload.mode,
        folder_id=payload.folder_id,
        top_k=payload.top_k,
    )

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
