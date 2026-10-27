"""API Endpoints for Hierarchical Personal Paper Library, Literature Comparison Matrix,
and 2-Tier Hierarchical RAG (Module 4).
"""

from __future__ import annotations

from uuid import UUID

import structlog
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import (
    get_current_user,
    get_folder_service,
    get_graph_rag_service,
    get_library_synthesis_service,
)
from api.schemas.envelope import ResponseMeta, SingleResponseEnvelope
from api.schemas.error import ErrorResponse
from api.schemas.folder import (
    BibliometricsEnvelope,
    BibliometricsResponseData,
    FolderCreateRequest,
    FolderDocumentAssignRequest,
    FolderResponseData,
    FolderSingleEnvelope,
    FolderTreeEnvelope,
    FolderUpdateRequest,
    HierarchicalRagQueryRequest,
    HierarchicalRagQueryResponseData,
)
from api.services.folder_service import FolderService
from api.services.graph_rag_service import GraphRAGService
from api.services.library_synthesis_service import LibrarySynthesisService
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger("api.endpoints.folders")

router = APIRouter(prefix="/folders", tags=["folders"])


# ==============================================================================
# 1. GET /api/v1/folders (List all user folders)
# ==============================================================================
@router.get(
    "",
    response_model=SingleResponseEnvelope[list[FolderResponseData]],
    summary="Danh sách thư mục nghiên cứu cá nhân",
    description=(
        "Truy vấn danh sách tất cả các thư mục đề tài của người dùng cùng số lượng tài liệu."
    ),
    responses={
        200: {"description": "Danh sách thư mục lấy thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực người dùng."},
    },
)
async def list_folders(
    current_user: UserModel = Depends(get_current_user),
    folder_service: FolderService = Depends(get_folder_service),
) -> SingleResponseEnvelope[list[FolderResponseData]]:
    """List all folders belonging to authenticated user."""
    folders = await folder_service.list_folders(user_id=current_user.id)
    return SingleResponseEnvelope(data=folders)


# ==============================================================================
# 2. POST /api/v1/folders (Create folder)
# ==============================================================================
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=FolderSingleEnvelope,
    summary="Tạo thư mục đề tài nghiên cứu mới",
    description="Tạo một thư mục gốc hoặc thư mục con trong cây phân cấp thư viện cá nhân.",
    responses={
        201: {"description": "Thư mục đã được tạo thành công."},
        400: {"model": ErrorResponse, "description": "Dữ liệu thư mục không hợp lệ."},
        409: {"model": ErrorResponse, "description": "Tên thư mục bị trùng lặp trong cùng cấp."},
    },
)
async def create_folder(
    payload: FolderCreateRequest,
    current_user: UserModel = Depends(get_current_user),
    folder_service: FolderService = Depends(get_folder_service),
) -> FolderSingleEnvelope:
    """Create a new research folder."""
    folder = await folder_service.create_folder(user_id=current_user.id, payload=payload)
    return FolderSingleEnvelope(data=folder)


# ==============================================================================
# 3. GET /api/v1/folders/tree (Get nested folder hierarchy)
# ==============================================================================
@router.get(
    "/tree",
    response_model=FolderTreeEnvelope,
    summary="Cây phân cấp thư mục thư viện (Folder Tree)",
    description=(
        "Trả về toàn bộ cấu trúc cây thư mục lồng nhau dạng đa cấp "
        "phục vụ thanh điều hướng Sidebar."
    ),
    responses={
        200: {"description": "Cây thư mục truy xuất thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực người dùng."},
    },
)
async def get_folder_tree(
    current_user: UserModel = Depends(get_current_user),
    folder_service: FolderService = Depends(get_folder_service),
) -> FolderTreeEnvelope:
    """Retrieve full hierarchical nested tree of user folders."""
    tree = await folder_service.get_folder_tree(user_id=current_user.id)
    return FolderTreeEnvelope(success=True, data=tree)


# ==============================================================================
# 5. POST /api/v1/folders/synthesis (2-Tier Hierarchical RAG Query - Global)
# ==============================================================================
@router.post(
    "/synthesis",
    response_model=SingleResponseEnvelope[HierarchicalRagQueryResponseData],
    summary="Truy vấn 2-Tier Hierarchical RAG trong Thư viện",
    description=(
        "Tìm kiếm phân tầng: Tier 1 (Knowledge Notes) -> Tier 2 (Deep Chunks) "
        "kết hợp Sufficiency Gate."
    ),
    responses={
        200: {"description": "Truy vấn RAG thành công."},
        404: {"model": ErrorResponse, "description": "Không tìm thấy tài liệu phù hợp."},
    },
)
async def query_hierarchical_rag(
    payload: HierarchicalRagQueryRequest,
    current_user: UserModel = Depends(get_current_user),
    synthesis_service: LibrarySynthesisService = Depends(get_library_synthesis_service),
) -> SingleResponseEnvelope[HierarchicalRagQueryResponseData]:
    """Execute 2-Tier Hierarchical RAG query across user library."""
    result = await synthesis_service.hierarchical_rag_query(
        user_id=current_user.id,
        query=payload.query,
        folder_id=payload.folder_id,
        enable_thinking=payload.enable_thinking,
    )
    return SingleResponseEnvelope(data=result)


# ==============================================================================
# 6. GET /api/v1/folders/{id} (Get single folder details)
# ==============================================================================
@router.get(
    "/{id}",
    response_model=FolderSingleEnvelope,
    summary="Chi tiết thư mục",
    description="Lấy thông tin chi tiết một thư mục kèm số lượng tài liệu.",
    responses={
        200: {"description": "Thông tin thư mục."},
        404: {"model": ErrorResponse, "description": "Thư mục không tồn tại."},
    },
)
async def get_folder(
    id: UUID,
    current_user: UserModel = Depends(get_current_user),
    folder_service: FolderService = Depends(get_folder_service),
) -> FolderSingleEnvelope:
    """Get single folder by ID."""
    folder = await folder_service.get_folder(user_id=current_user.id, folder_id=id)
    return FolderSingleEnvelope(data=folder)


# ==============================================================================
# 6b. GET /api/v1/folders/{id}/bibliometrics (Connected Papers Bibliometrics)
# ==============================================================================
@router.get(
    "/{id}/bibliometrics",
    response_model=BibliometricsEnvelope,
    summary="Mạng Ghép Cặp Thư Mục Học & Tác Phẩm Cội Nguồn (Connected Papers Bibliometrics)",
    description=(
        "Truy vấn mạng ghép cặp thư mục học (Bibliographic Coupling) và xếp hạng "
        "Tác phẩm Cội nguồn (Prior Works) vs Tác phẩm Phái sinh (Derivative Works) trong thư mục."
    ),
    responses={
        200: {"description": "Kết quả phân tích thư mục học thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực người dùng."},
        404: {"model": ErrorResponse, "description": "Thư mục không tồn tại."},
    },
)
async def get_folder_bibliometrics(
    id: UUID = Path(..., description="UUID của thư mục đề tài nghiên cứu"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    folder_service: FolderService = Depends(get_folder_service),
    graph_rag_service: GraphRAGService = Depends(get_graph_rag_service),
) -> BibliometricsEnvelope:
    """Retrieve Connected Papers bibliographic coupling network and prior/derivative works."""
    # Ensure folder exists and belongs to authenticated scholar
    await folder_service.get_folder(user_id=current_user.id, folder_id=id)

    result = await graph_rag_service.compute_bibliometrics(
        db=db,
        user_id=current_user.id,
        folder_id=id,
    )

    data_payload = BibliometricsResponseData(
        folder_id=result["folder_id"],
        prior_works=result["prior_works"],
        derivative_works=result["derivative_works"],
        coupling_edges=result["coupling_edges"],
    )

    return BibliometricsEnvelope(
        success=True,
        data=data_payload,
        folder_id=result["folder_id"],
        prior_works=result["prior_works"],
        derivative_works=result["derivative_works"],
        coupling_edges=result["coupling_edges"],
        meta=ResponseMeta(),
    )


# ==============================================================================
# 7. PATCH /api/v1/folders/{id} (Update folder metadata / move parent)
# ==============================================================================
@router.patch(
    "/{id}",
    response_model=FolderSingleEnvelope,
    summary="Cập nhật hoặc di chuyển thư mục",
    description=(
        "Đổi tên, đổi màu nhận diện, cập nhật mô tả hoặc di chuyển thư mục trong cây phân cấp."
    ),
    responses={
        200: {"description": "Thư mục cập nhật thành công."},
        400: {
            "model": ErrorResponse,
            "description": "Di chuyển không hợp lệ (Circular hierarchy).",
        },
        404: {"model": ErrorResponse, "description": "Thư mục không tồn tại."},
    },
)
async def update_folder(
    id: UUID,
    payload: FolderUpdateRequest,
    current_user: UserModel = Depends(get_current_user),
    folder_service: FolderService = Depends(get_folder_service),
) -> FolderSingleEnvelope:
    """Update folder properties or move position in hierarchy."""
    folder = await folder_service.update_folder(
        user_id=current_user.id, folder_id=id, payload=payload
    )
    return FolderSingleEnvelope(data=folder)


# ==============================================================================
# 8. DELETE /api/v1/folders/{id} (Delete folder safely)
# ==============================================================================
@router.delete(
    "/{id}",
    response_model=SingleResponseEnvelope[dict[str, str]],
    summary="Xóa thư mục nghiên cứu",
    description=(
        "Xóa thư mục an toàn, các tài liệu bên trong sẽ được đưa về thư mục gốc (Root Library)."
    ),
    responses={
        200: {"description": "Thư mục đã xóa thành công."},
        404: {"model": ErrorResponse, "description": "Thư mục không tồn tại."},
    },
)
async def delete_folder(
    id: UUID,
    current_user: UserModel = Depends(get_current_user),
    folder_service: FolderService = Depends(get_folder_service),
) -> SingleResponseEnvelope[dict[str, str]]:
    """Safely delete folder and unassign contained documents."""
    result = await folder_service.delete_folder(user_id=current_user.id, folder_id=id)
    return SingleResponseEnvelope(data=result)


# ==============================================================================
# 9. POST /api/v1/folders/{id}/documents (Assign documents to folder)
# ==============================================================================
@router.post(
    "/{id}/documents",
    response_model=SingleResponseEnvelope[dict[str, int]],
    summary="Gán tài liệu vào thư mục",
    description="Thêm một hoặc nhiều bài báo khoa học vào thư mục đề tài nghiên cứu.",
    responses={
        200: {"description": "Tài liệu đã được gán vào thư mục thành công."},
        404: {"model": ErrorResponse, "description": "Thư mục không tồn tại."},
    },
)
async def assign_documents_to_folder(
    id: UUID,
    payload: FolderDocumentAssignRequest,
    current_user: UserModel = Depends(get_current_user),
    folder_service: FolderService = Depends(get_folder_service),
) -> SingleResponseEnvelope[dict[str, int]]:
    """Assign or move documents into folder."""
    result = await folder_service.assign_documents(
        user_id=current_user.id, folder_id=id, document_ids=payload.document_ids
    )
    return SingleResponseEnvelope(data=result)


# ==============================================================================
# 10. DELETE /api/v1/folders/{id}/documents (Remove documents from folder)
# ==============================================================================
@router.delete(
    "/{id}/documents",
    response_model=SingleResponseEnvelope[dict[str, int]],
    summary="Bỏ tài liệu khỏi thư mục",
    description="Đưa các bài báo khoa học ra khỏi thư mục về lại thư viện gốc.",
    responses={
        200: {"description": "Đã đưa tài liệu về thư viện gốc."},
        404: {"model": ErrorResponse, "description": "Thư mục không tồn tại."},
    },
)
async def remove_documents_from_folder(
    id: UUID,
    payload: FolderDocumentAssignRequest,
    current_user: UserModel = Depends(get_current_user),
    folder_service: FolderService = Depends(get_folder_service),
) -> SingleResponseEnvelope[dict[str, int]]:
    """Remove documents from folder back to root library."""
    result = await folder_service.remove_documents(
        user_id=current_user.id, folder_id=id, document_ids=payload.document_ids
    )
    return SingleResponseEnvelope(data=result)


# ==============================================================================
# 12. POST /api/v1/folders/{id}/synthesis (2-Tier Hierarchical RAG for Folder)
# ==============================================================================
@router.post(
    "/{id}/synthesis",
    response_model=SingleResponseEnvelope[HierarchicalRagQueryResponseData],
    summary="Truy vấn 2-Tier Hierarchical RAG trong Thư mục",
    description=(
        "Thực hiện tìm kiếm phân tầng chỉ giới hạn trong phạm vi các tài liệu của thư mục này."
    ),
    responses={
        200: {"description": "Truy vấn RAG thành công."},
        404: {"model": ErrorResponse, "description": "Không tìm thấy dữ liệu."},
    },
)
async def query_folder_hierarchical_rag(
    id: UUID,
    payload: HierarchicalRagQueryRequest,
    current_user: UserModel = Depends(get_current_user),
    synthesis_service: LibrarySynthesisService = Depends(get_library_synthesis_service),
) -> SingleResponseEnvelope[HierarchicalRagQueryResponseData]:
    """Execute 2-Tier Hierarchical RAG query scoped to folder."""
    result = await synthesis_service.hierarchical_rag_query(
        user_id=current_user.id,
        query=payload.query,
        folder_id=id,
        enable_thinking=payload.enable_thinking,
    )
    return SingleResponseEnvelope(data=result)
