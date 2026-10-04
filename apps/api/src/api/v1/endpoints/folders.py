"""API Endpoints for Project Folders (Module 4 Library API)."""

from uuid import UUID

from api.db.models.user import UserModel
from api.deps import get_current_user, get_folder_service, get_library_service
from api.schemas.envelope import ResponseMeta
from api.schemas.folder import (
    FolderCreateRequest,
    FolderItemEnvelope,
    FolderListEnvelope,
    FolderUpdateRequest,
)
from api.schemas.library import (
    LibrarySynthesizeEnvelope,
    LibrarySynthesizeRequest,
)
from api.services.folder_service import FolderService
from api.services.library_service import LibraryService
from fastapi import APIRouter, Depends, Path, status

router = APIRouter(prefix="/folders", tags=["Folders"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=FolderListEnvelope,
    summary="Danh sách thư mục đề tài nghiên cứu",
    description=(
        "🎯 **Mục đích:** Lấy toàn bộ danh sách thư mục đề tài nghiên cứu của người dùng, "
        "kèm số lượng bài báo khoa học đã lưu (star) trong từng thư mục.\n\n"
        "📤 **Đầu ra:** Danh sách các thư mục kèm `document_count` và quan hệ phân cấp `parent_id`."
    ),
)
async def list_folders(
    current_user: UserModel = Depends(get_current_user),
    service: FolderService = Depends(get_folder_service),
) -> FolderListEnvelope:
    """Retrieve all folders for current user."""
    folders = await service.list_folders(user_id=current_user.id)
    return FolderListEnvelope(
        success=True,
        data=folders,
        meta=ResponseMeta(),
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=FolderItemEnvelope,
    summary="Tạo thư mục đề tài mới",
    description=(
        "🎯 **Mục đích:** Khởi tạo thư mục đề tài nghiên cứu mới.\n\n"
        "📥 **Đầu vào:** `name` (tên thư mục), `parent_id` (UUID cha nếu lồng, null nếu gốc).\n\n"
        "📤 **Đầu ra:** Thông tin thư mục vừa tạo thành công."
    ),
)
async def create_folder(
    payload: FolderCreateRequest,
    current_user: UserModel = Depends(get_current_user),
    service: FolderService = Depends(get_folder_service),
) -> FolderItemEnvelope:
    """Create a new folder."""
    folder = await service.create_folder(user_id=current_user.id, req=payload)
    return FolderItemEnvelope(
        success=True,
        data=folder,
        meta=ResponseMeta(),
    )


@router.patch(
    "/{folder_id}",
    status_code=status.HTTP_200_OK,
    response_model=FolderItemEnvelope,
    summary="Đổi tên hoặc di chuyển thư mục",
    description=(
        "🎯 **Mục đích:** Cập nhật tên hoặc vị trí cha của thư mục đề tài.\n\n"
        "🛡️ **An toàn phân cấp:** Ngăn chặn tuyệt đối việc gán thư mục làm cha của chính nó "
        "hoặc di chuyển vào một thư mục con cháu bên trong (Cycle Breaking)."
    ),
)
async def update_folder(
    folder_id: UUID = Path(..., description="UUID của thư mục cần chỉnh sửa"),
    payload: FolderUpdateRequest = ...,
    current_user: UserModel = Depends(get_current_user),
    service: FolderService = Depends(get_folder_service),
) -> FolderItemEnvelope:
    """Update folder name or move parent."""
    folder = await service.update_folder(
        user_id=current_user.id,
        folder_id=folder_id,
        req=payload,
    )
    return FolderItemEnvelope(
        success=True,
        data=folder,
        meta=ResponseMeta(),
    )


@router.delete(
    "/{folder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa thư mục đề tài",
    description=(
        "🎯 **Mục đích:** Xóa thư mục đề tài nghiên cứu.\n\n"
        "🛡️ **Cam kết bảo toàn dữ liệu (Zero Data Loss):** Các bài báo khoa học đã lưu "
        "trong thư mục bị xóa sẽ tự động chuyển về trạng thái Chưa phân loại (`folder_id: null`), "
        "hoàn toàn không bị xóa mất khỏi thư viện cá nhân của người dùng."
    ),
)
async def delete_folder(
    folder_id: UUID = Path(..., description="UUID của thư mục cần xóa"),
    current_user: UserModel = Depends(get_current_user),
    service: FolderService = Depends(get_folder_service),
) -> None:
    """Delete a folder and uncategorize contained documents."""
    await service.delete_folder(user_id=current_user.id, folder_id=folder_id)


@router.post(
    "/{folder_id}:synthesize",
    status_code=status.HTTP_200_OK,
    response_model=LibrarySynthesizeEnvelope,
    summary="Agentic Hierarchical RAG trên thư mục đề tài",
    description=(
        "🎯 **Mục đích:** Tổng hợp đa bài báo khoa học trong phạm vi thư mục chỉ định "
        "qua cơ chế Cổng Đánh Giá Mức Độ Đầy Đủ Bằng Chứng (Sufficiency Verification Gate)."
    ),
)
async def synthesize_folder(
    folder_id: UUID = Path(..., description="UUID của thư mục cần tổng hợp"),
    payload: LibrarySynthesizeRequest = ...,
    current_user: UserModel = Depends(get_current_user),
    service: LibraryService = Depends(get_library_service),
) -> LibrarySynthesizeEnvelope:
    """Run hierarchical RAG synthesis on documents within a specific folder."""
    result = await service.synthesize(
        user_id=current_user.id,
        folder_id=folder_id,
        query=payload.query,
    )
    return LibrarySynthesizeEnvelope(
        success=True,
        data=result,
        meta=ResponseMeta(),
    )
