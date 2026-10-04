"""API Endpoints for References Resolving & Citation Graph (Module 3 References API)."""

from uuid import UUID

from api.db.models.user import UserModel
from api.deps import get_current_user, get_reference_service
from api.schemas.envelope import ResponseMeta
from api.schemas.reference import (
    CitationGraphEnvelope,
    ReferenceResolveEnvelope,
    ReferenceResolveRequest,
)
from api.services.reference_service import ReferenceService
from fastapi import APIRouter, Depends, Path, Query, status

router = APIRouter(prefix="/references", tags=["References"])


@router.post(
    ":resolve",
    status_code=status.HTTP_200_OK,
    response_model=ReferenceResolveEnvelope,
    summary="Batch Resolving & Leaky Bucket qua Global Academic Cache",
    description=(
        "🎯 **Mục đích:** Phân giải danh sách tài liệu tham khảo học thuật hàng loạt qua "
        "Global Academic Cache (< 10ms) và Leaky Bucket Rate Limiter.\n\n"
        "📤 **Đầu ra:** Danh sách bài báo đã phân giải kèm cờ `has_open_access_pdf` "
        "và `pdf_download_url`."
    ),
)
async def resolve_references(
    payload: ReferenceResolveRequest,
    current_user: UserModel = Depends(get_current_user),
    service: ReferenceService = Depends(get_reference_service),
) -> ReferenceResolveEnvelope:
    """Resolve a batch of academic references with cached metrics."""
    result = await service.resolve_references(req=payload)
    return ReferenceResolveEnvelope(
        success=True,
        data=result,
        meta=ResponseMeta(),
    )


@router.get(
    "/{document_id}/graph",
    status_code=status.HTTP_200_OK,
    response_model=CitationGraphEnvelope,
    summary="Truy vấn Đồ thị Tri thức Trích dẫn (Cycle Breaking, max_hops <= 2)",
    description=(
        "🎯 **Mục đích:** Khai thác đồ thị trích dẫn đa tầng của bài báo khoa học. "
        "Tự động ngắt chu trình lặp vô hạn (Cycle Breaking) qua thuật toán BFS có tập visited."
    ),
)
async def get_citation_graph(
    document_id: UUID = Path(..., description="UUID của bài báo gốc cần dựng đồ thị"),
    max_hops: int = Query(2, ge=1, le=2, description="Độ sâu tối đa của đồ thị (1 hoặc 2 hops)"),
    relations: str = Query("CITES,EXTENDS,BENCHMARKS_ON", description="Quan hệ trích dẫn"),
    current_user: UserModel = Depends(get_current_user),
    service: ReferenceService = Depends(get_reference_service),
) -> CitationGraphEnvelope:
    """Retrieve citation knowledge graph with cycle breaking."""
    graph = await service.get_citation_graph(
        document_id=document_id,
        user_id=current_user.id,
        max_hops=max_hops,
        relations=relations,
    )
    return CitationGraphEnvelope(
        success=True,
        data=graph,
        meta=ResponseMeta(),
    )
