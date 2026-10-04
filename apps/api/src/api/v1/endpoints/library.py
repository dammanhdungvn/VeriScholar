"""API Endpoints for Personal Library & Multi-paper Synthesis (Module 4 Library API)."""

import math
from uuid import UUID

from api.db.models.user import UserModel
from api.deps import get_current_user, get_library_service
from api.schemas.document import DocumentListPaginatedEnvelope
from api.schemas.envelope import PaginationLinks, PaginationMeta, ResponseMeta
from api.schemas.library import (
    BulkImportEnvelope,
    BulkImportRequest,
    LibraryCompareEnvelope,
    LibraryCompareRequest,
    LibrarySynthesizeEnvelope,
    LibrarySynthesizeRequest,
)
from api.services.library_service import LibraryService
from fastapi import APIRouter, Depends, Query, status

router = APIRouter(prefix="/library", tags=["Library"])


@router.get(
    "/documents",
    status_code=status.HTTP_200_OK,
    response_model=DocumentListPaginatedEnvelope,
    summary="Kho bài báo cá nhân đã Star (phân trang RFC 8288)",
    description=(
        "🎯 **Mục đích:** Truy vấn bài báo khoa học đã lưu vĩnh viễn (Star/Promotion) "
        "vào thư viện cá nhân, hỗ trợ lọc theo thư mục hoặc tìm kiếm từ khóa.\n\n"
        "📥 **Bộ lọc:** `folder_id` (UUID thư mục), `search` (từ khóa tiêu đề hoặc tên tệp), "
        "`page` (mặc định 1), `per_page` (mặc định 20)."
    ),
)
async def list_library_documents(
    folder_id: UUID | None = Query(
        None,
        description="Lọc bài báo theo thư mục đề tài cụ thể (tùy chọn)",
    ),
    search: str | None = Query(
        None,
        description="Tìm kiếm theo tiêu đề hoặc tên tệp bài báo",
    ),
    page: int = Query(
        1,
        ge=1,
        description="Số thứ tự trang kết quả (1-indexed)",
    ),
    per_page: int = Query(
        20,
        ge=1,
        le=100,
        description="Số lượng bài báo trên mỗi trang (1-100)",
    ),
    current_user: UserModel = Depends(get_current_user),
    service: LibraryService = Depends(get_library_service),
) -> DocumentListPaginatedEnvelope:
    """Retrieve paginated collection of starred library documents."""
    items, total = await service.list_library_documents(
        user_id=current_user.id,
        folder_id=folder_id,
        search=search,
        page=page,
        per_page=per_page,
    )

    total_pages = max(1, math.ceil(total / per_page))

    def _build_url(p: int) -> str:
        base = f"/api/v1/library/documents?page={p}&per_page={per_page}"
        if folder_id:
            base += f"&folder_id={folder_id}"
        if search:
            base += f"&search={search}"
        return base

    meta = PaginationMeta(
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )
    links = PaginationLinks(
        first=_build_url(1),
        prev=_build_url(page - 1) if page > 1 else None,
        self=_build_url(page),
        next=_build_url(page + 1) if page < total_pages else None,
        last=_build_url(total_pages),
    )

    return DocumentListPaginatedEnvelope(
        success=True,
        data=items,
        meta=meta,
        links=links,
    )


@router.post(
    "/documents:bulk-import",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=BulkImportEnvelope,
    summary="Nạp hàng loạt 10 - 50 bài báo vào thư viện (Bulk Import)",
    description=(
        "🎯 **Mục đích:** Tiếp nhận danh sách mã học thuật (DOI hoặc arXiv ID, tối đa 50 bài) "
        "để kích hoạt hàng đợi nạp lô vào thư viện cá nhân.\n\n"
        "📤 **Đầu ra:** HTTP 202 Accepted kèm `batch_id` để theo dõi tiến độ nạp lô."
    ),
)
async def bulk_import_documents(
    payload: BulkImportRequest,
    current_user: UserModel = Depends(get_current_user),
    service: LibraryService = Depends(get_library_service),
) -> BulkImportEnvelope:
    """Enqueue batch ingestion of papers into personal library."""
    result = await service.bulk_import(user_id=current_user.id, req=payload)
    return BulkImportEnvelope(
        success=True,
        data=result,
        meta=ResponseMeta(),
    )


@router.post(
    "/synthesize",
    status_code=status.HTTP_200_OK,
    response_model=LibrarySynthesizeEnvelope,
    summary="Agentic Hierarchical RAG trên toàn bộ thư viện cá nhân",
    description=(
        "🎯 **Mục đích:** Tổng hợp đa bài báo trên toàn bộ kho tài liệu cá nhân qua "
        "Cổng Đánh Giá Mức Độ Đầy Đủ Bằng Chứng (Sufficiency Verification Gate)."
    ),
)
async def synthesize_library(
    payload: LibrarySynthesizeRequest,
    current_user: UserModel = Depends(get_current_user),
    service: LibraryService = Depends(get_library_service),
) -> LibrarySynthesizeEnvelope:
    """Run hierarchical RAG synthesis across entire personal library."""
    result = await service.synthesize(
        user_id=current_user.id,
        folder_id=None,
        query=payload.query,
    )
    return LibrarySynthesizeEnvelope(
        success=True,
        data=result,
        meta=ResponseMeta(),
    )


@router.post(
    "/compare",
    status_code=status.HTTP_200_OK,
    response_model=LibraryCompareEnvelope,
    summary="Dựng bảng so sánh tự động giữa các bài báo (Compare Matrix)",
    description=(
        "🎯 **Mục đích:** Dựng bảng ma trận so sánh đa chiều giữa 2 đến 10 bài báo khoa học "
        "theo các khía cạnh nghiên cứu (Method, Dataset, Results, Limitations)."
    ),
)
async def compare_documents(
    payload: LibraryCompareRequest,
    current_user: UserModel = Depends(get_current_user),
    service: LibraryService = Depends(get_library_service),
) -> LibraryCompareEnvelope:
    """Construct multi-dimensional comparison table across selected documents."""
    result = await service.compare_documents(user_id=current_user.id, req=payload)
    return LibraryCompareEnvelope(
        success=True,
        data=result,
        meta=ResponseMeta(),
    )
