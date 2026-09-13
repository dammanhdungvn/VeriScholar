"""Document endpoints implementing Module 1 Deep Reading & Ingestion API."""

from uuid import UUID

from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import get_current_user, get_document_service
from api.schemas.document import DocumentUploadEnvelope
from api.schemas.envelope import ResponseMeta
from api.services.document_service import DocumentService
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/documents", tags=["Module 1: Documents"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=DocumentUploadEnvelope,
    summary="Tải lên PDF bài báo (nhận session_id tùy chọn)",
    description=(
        "Nạp bài báo khoa học định dạng PDF vào hệ thống.\n\n"
        "**Tính năng kỹ thuật:**\n"
        "- Kiểm tra magic bytes `%PDF-` bắt buộc.\n"
        "- Khống chế dung lượng tối đa 50MB.\n"
        "- Áp dụng Content-Addressable Storage (CAS) khử trùng lặp file vật lý qua SHA-256.\n"
        "- Tùy chọn liên kết ngay vào phiên nghiên cứu (giới hạn tối đa 5 bài báo/phiên).\n"
        "- Trả về Single Resource Envelope kèm HATEOAS navigation links."
    ),
    responses={
        201: {
            "description": "Tải lên thành công, tài liệu đã được ghi nhận vào hàng đợi.",
        },
        400: {
            "description": "Tệp không hợp lệ (không phải định dạng PDF hoặc thiếu %PDF-).",
        },
        404: {
            "description": "Không tìm thấy session_id được chỉ định.",
        },
        409: {
            "description": "Phiên nghiên cứu đã đạt trần tối đa 5 bài báo.",
        },
        413: {
            "description": "Dung lượng tệp vượt quá giới hạn cho phép (50MB).",
        },
    },
)
async def upload_document(
    file: UploadFile = File(..., description="Tệp bài báo học thuật định dạng PDF"),
    session_id: UUID | None = Form(
        None,
        description="ID phiên nghiên cứu cần gắn kết tài liệu (tùy chọn)",
    ),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: DocumentService = Depends(get_document_service),
) -> DocumentUploadEnvelope:
    """Handle multipart upload of academic PDF document."""
    data = await service.upload_document(
        file=file,
        user_id=current_user.id,
        db=db,
        session_id=session_id,
    )
    return DocumentUploadEnvelope(
        success=True,
        data=data,
        meta=ResponseMeta(),
    )
