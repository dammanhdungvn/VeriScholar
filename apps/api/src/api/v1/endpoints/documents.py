"""Document endpoints implementing Module 1 Deep Reading & Ingestion API."""

from uuid import UUID

from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import get_current_user, get_document_service
from api.schemas.document import (
    DocumentDetailEnvelope,
    DocumentListPaginatedEnvelope,
    DocumentUploadEnvelope,
)
from api.schemas.envelope import ResponseMeta
from api.services.document_service import DocumentService
from fastapi import APIRouter, Depends, File, Form, Header, Query, UploadFile, status
from fastapi.responses import StreamingResponse
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


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=DocumentListPaginatedEnvelope,
    summary="Danh sách bài báo (phân trang page/per_page)",
    description=(
        "Lấy danh sách các bài báo khoa học thuộc quyền sở hữu của người dùng hiện tại.\n\n"
        "**Tính năng kỹ thuật:**\n"
        "- Phân trang chuẩn **RFC 8288** (`first`, `prev`, `self`, `next`, `last`).\n"
        "- Đảm bảo cô lập dữ liệu người dùng (Multi-tenant Scoping).\n"
        "- Hỗ trợ lọc theo trạng thái xử lý (`status`).\n"
        "- Sắp xếp mặc định theo thứ tự thời gian tạo mới nhất (`created_at DESC`)."
    ),
    responses={
        200: {
            "description": "Truy vấn danh sách bài báo thành công kèm siêu dữ liệu phân trang.",
        },
        422: {
            "description": "Tham số phân trang không hợp lệ (page < 1 hoặc per_page > 100).",
        },
    },
)
async def list_documents(
    page: int = Query(
        1,
        ge=1,
        description="Số thứ tự trang kết quả (1-indexed)",
    ),
    per_page: int = Query(
        20,
        ge=1,
        le=100,
        description="Số lượng bài báo tối đa trên mỗi trang (1-100)",
    ),
    status_filter: str | None = Query(
        None,
        alias="status",
        description=(
            "Tùy chọn lọc theo trạng thái tài liệu "
            "('uploaded', 'pending', 'processing', 'completed', 'failed')"
        ),
    ),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: DocumentService = Depends(get_document_service),
) -> DocumentListPaginatedEnvelope:
    """Retrieve paginated documents collection for current user."""
    return await service.list_documents(
        user_id=current_user.id,
        db=db,
        page=page,
        per_page=per_page,
        status_filter=status_filter,
    )


@router.get(
    "/{document_id}",
    status_code=status.HTTP_200_OK,
    response_model=DocumentDetailEnvelope,
    summary="Chi tiết tài liệu kèm Spatial Metadata",
    description=(
        "Lấy thông tin siêu dữ liệu chi tiết của bài báo học thuật, bao gồm mảng "
        "kích thước hình học (`dimensions`) và góc xoay (`rotation_deg`) từng trang PDF "
        "phục vụ dựng khung vẽ trực quan trên Web Canvas (PDF.js).\n\n"
        "**Tính năng kỹ thuật:**\n"
        "- Đảm bảo cô lập dữ liệu người dùng (Multi-tenant Scoping).\n"
        "- Trả về danh sách `pages_metadata` chuẩn hóa với page 1-indexed.\n"
        "- Bao bọc Single Resource Envelope chuẩn với `request_id` và `timestamp`."
    ),
    responses={
        200: {
            "description": "Lấy chi tiết tài liệu và Spatial Metadata thành công.",
        },
        404: {
            "description": "Không tìm thấy tài liệu hoặc người dùng không có quyền truy cập.",
        },
        422: {
            "description": "Định dạng document_id không phải UUID hợp lệ.",
        },
    },
)
async def get_document_detail(
    document_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: DocumentService = Depends(get_document_service),
) -> DocumentDetailEnvelope:
    """Retrieve detailed document metadata and spatial page dimensions."""
    data = await service.get_document_detail(
        document_id=document_id,
        user_id=current_user.id,
        db=db,
    )
    return DocumentDetailEnvelope(
        success=True,
        data=data,
        meta=ResponseMeta(),
    )


@router.get(
    "/{document_id}/file",
    response_class=StreamingResponse,
    summary="Stream PDF nhị phân cho Canvas (HTTP 206 Partial Content)",
    description=(
        "Stream tệp nhị phân PDF phục vụ hiển thị trực quan trên Web Canvas (PDF.js).\n\n"
        "**Tính năng kỹ thuật:**\n"
        "- Hỗ trợ tiêu đề `Range: bytes=start-end` cho HTTP 206 Partial Content "
        "(lazy-loading trang tối ưu hóa băng thông).\n"
        "- Hỗ trợ HTTP 200 OK khi client tải toàn bộ tệp.\n"
        "- Trả về `Accept-Ranges: bytes` và `Content-Disposition: inline`.\n"
        "- Bảo đảm an toàn Multi-tenant Scoping: trả về 404 nếu không sở hữu tài liệu."
    ),
    responses={
        200: {
            "description": "Tải toàn bộ tệp PDF thành công.",
            "content": {"application/pdf": {}},
        },
        206: {
            "description": "Phản hồi phân đoạn tệp PDF (Partial Content).",
            "content": {"application/pdf": {}},
        },
        404: {
            "description": "Không tìm thấy tài liệu hoặc tệp nhị phân bị thiếu.",
        },
        416: {
            "description": "Dải byte yêu cầu nằm ngoài phạm vi kích thước tệp.",
        },
    },
)
async def stream_document_file(
    document_id: UUID,
    range_header: str | None = Header(default=None, alias="Range"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: DocumentService = Depends(get_document_service),
) -> StreamingResponse:
    """Stream PDF binary chunks supporting HTTP 206 Partial Content."""
    stream, headers, status_code = await service.get_document_file_stream(
        document_id=document_id,
        user_id=current_user.id,
        db=db,
        range_header=range_header,
    )
    return StreamingResponse(
        content=stream,
        status_code=status_code,
        headers=headers,
        media_type="application/pdf",
    )
