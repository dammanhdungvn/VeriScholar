"""Document endpoints implementing Module 1 Deep Reading & Ingestion API."""

from uuid import UUID

from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import get_current_user, get_document_service
from api.schemas.document import (
    DocumentDetailEnvelope,
    DocumentListPaginatedEnvelope,
    DocumentStatusEnvelope,
    DocumentUploadEnvelope,
)
from api.schemas.envelope import ResponseMeta
from api.services.document_service import DocumentService
from fastapi import APIRouter, Depends, File, Form, Header, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/documents", tags=["Module 1: Documents"])

UPLOAD_DESCRIPTION = (
    "🎯 **Mục đích:** Tải tệp PDF bài báo lên hệ thống để bắt đầu quy trình bóc "
    "tách.\\n"
    "\\n"
    "📥 **Đầu vào (multipart/form-data):**\\n"
    "- `file`: Tệp PDF bài báo (bắt buộc, tối đa 50MB, magic bytes `%PDF-`).\\n"
    "- `session_id`: UUID phiên nghiên cứu cần gắn tài liệu (tùy chọn, tối đa 5 "
    "bài/phiên).\\n"
    "\\n"
    "📤 **Đầu ra (HTTP 201):**\\n"
    "- Trả về `id`, `status: uploaded`, và các liên kết HATEOAS (`status_url`, "
    "`file_url`).\\n"
    "\\n"
    "⚠️ **Lưu ý:**\\n"
    "- Khử trùng lặp CAS: file trùng hash SHA-256 sẽ tái sử dụng bản ghi cũ.\\n"
    "- Lỗi thường gặp: `400` (sai định dạng), `413` (>50MB), `409` (phiên đã đầy "
    "5 bài)."
)

LIST_DESCRIPTION = (
    "🎯 **Mục đích:** Hiển thị danh sách bài báo người dùng trên thư viện hoặc "
    "sidebar.\\n"
    "\\n"
    "📥 **Đầu vào (Query parameters):**\\n"
    "- `page`: Số thứ tự trang kết quả (mặc định: `1`, tối thiểu: `1`).\\n"
    "- `per_page`: Số lượng bài báo mỗi trang (mặc định: `20`, tối đa: `100`).\\n"
    "- `status`: Lọc theo trạng thái (`uploaded`, `processing`, `completed`, "
    "`failed`).\\n"
    "\\n"
    "📤 **Đầu ra (HTTP 200):**\\n"
    "- Mảng `items` tóm tắt bài báo (`id`, `filename`, `title`, `status`, "
    "`created_at`).\\n"
    "- Object `meta` phân trang và `links` điều hướng RFC 8288 (`next`, "
    "`prev`...).\\n"
    "\\n"
    "⚠️ **Lưu ý:**\\n"
    "- Sắp xếp mặc định: `created_at DESC` (bài báo mới nhất hiển thị trước).\\n"
    "- Đảm bảo cô lập dữ liệu: chỉ hiển thị tài liệu của người dùng hiện tại."
)

DETAIL_DESCRIPTION = (
    "🎯 **Mục đích:** Lấy siêu dữ liệu học thuật và kích thước trang cho Canvas "
    "(PDF.js).\\n"
    "\\n"
    "📥 **Đầu vào (Path parameter):**\\n"
    "- `document_id`: UUID của bài báo khoa học.\\n"
    "\\n"
    "📤 **Đầu ra (HTTP 200):**\\n"
    "- Thông tin học thuật (`title`, `authors`, `doi`, `page_count`, "
    "`chunk_count`...).\\n"
    "- `pages_metadata`: Mảng kích thước `[width, height]` và góc xoay từng "
    "trang PDF.\\n"
    "\\n"
    "⚠️ **Lưu ý:**\\n"
    "- Trả về `404` nếu tài liệu không tồn tại hoặc không thuộc quyền sở hữu."
)

FILE_DESCRIPTION = (
    "🎯 **Mục đích:** Cung cấp luồng PDF nhị phân cho Canvas xem trước "
    "(PDF.js).\\n"
    "\\n"
    "📥 **Đầu vào:**\\n"
    "- `document_id`: UUID bài báo (Path parameter).\\n"
    "- `Range`: Header tùy chọn (ví dụ: `bytes=0-1024`) để yêu cầu phân đoạn "
    "byte.\\n"
    "\\n"
    "📤 **Đầu ra:**\\n"
    "- Stream nhị phân `application/pdf`.\\n"
    "- `HTTP 200 OK`: Tải toàn bộ tệp PDF.\\n"
    "- `HTTP 206 Partial Content`: Tải phân đoạn byte phục vụ lazy-load "
    "Canvas.\\n"
    "\\n"
    "⚠️ **Lưu ý:**\\n"
    "- Trả về `416 Range Not Satisfiable` nếu dải byte yêu cầu vượt quá dung "
    "lượng tệp."
)

STATUS_DESCRIPTION = (
    "🎯 **Mục đích:** Frontend polling định kỳ (1-2s) hiển thị tiến độ bóc tách "
    "bài báo.\\n"
    "\\n"
    "📥 **Đầu vào (Path parameter):**\\n"
    "- `document_id`: UUID của bài báo đang xử lý.\\n"
    "\\n"
    "📤 **Đầu ra (HTTP 200):**\\n"
    "- `status`: Trạng thái tổng quát (`uploaded`, `processing`, `completed`, "
    "`failed`).\\n"
    "- `progress`: Phần trăm hoàn thành tổng thể (`0` đến `100%`).\\n"
    "- `stage`: Tên bước hiện tại (`running_ocr`, `chunking`, `embedding`...).\\n"
    "- `stages_detail`: Trạng thái con 5 chặng (`validation`, `ocr`, "
    "`chunking`...).\\n"
    "- `error_message`: Chi tiết lỗi nếu bước xử lý gặp sự cố.\\n"
    "\\n"
    "⚠️ **Lưu ý:**\\n"
    '- Dừng polling ngay khi `status == "completed"` hoặc `status == "failed"`.'
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=DocumentUploadEnvelope,
    summary="Tải lên PDF bài báo (nhận session_id tùy chọn)",
    description=UPLOAD_DESCRIPTION,
    responses={
        201: {"description": "Tải lên thành công, tài liệu đã được ghi nhận vào hàng đợi."},
        400: {"description": "Tệp không hợp lệ (không phải định dạng PDF hoặc thiếu %PDF-)."},
        404: {"description": "Không tìm thấy session_id được chỉ định."},
        409: {"description": "Phiên nghiên cứu đã đạt trần tối đa 5 bài báo."},
        413: {"description": "Dung lượng tệp vượt quá giới hạn cho phép (50MB)."},
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
    description=LIST_DESCRIPTION,
    responses={
        200: {"description": "Truy vấn danh sách bài báo thành công kèm siêu dữ liệu phân trang."},
        422: {"description": "Tham số phân trang không hợp lệ (page < 1 hoặc per_page > 100)."},
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
    summary="Chi tiết tài liệu kèm Spatial Metadata cho Canvas",
    description=DETAIL_DESCRIPTION,
    responses={
        200: {"description": "Lấy chi tiết tài liệu và Spatial Metadata thành công."},
        404: {"description": "Không tìm thấy tài liệu hoặc người dùng không có quyền truy cập."},
        422: {"description": "Định dạng document_id không phải UUID hợp lệ."},
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
    description=FILE_DESCRIPTION,
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


@router.get(
    "/{document_id}/status",
    response_model=DocumentStatusEnvelope,
    summary="Polling tiến độ bóc tách bài báo (0 - 100%)",
    description=STATUS_DESCRIPTION,
    responses={
        200: {
            "description": "Lấy thông tin tiến độ bóc tách thành công.",
        },
        404: {
            "description": "Không tìm thấy tài liệu hoặc người dùng không có quyền truy cập.",
        },
    },
)
async def get_document_status(
    document_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: DocumentService = Depends(get_document_service),
) -> DocumentStatusEnvelope:
    """Query document ingestion progress and stage breakdown."""
    data = await service.get_document_status(
        document_id=document_id,
        user_id=current_user.id,
        db=db,
    )
    return DocumentStatusEnvelope(
        data=data,
        meta=ResponseMeta(),
    )
