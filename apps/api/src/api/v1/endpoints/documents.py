"""Document endpoints implementing Module 1 Deep Reading & Ingestion API."""

from uuid import UUID

from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import get_current_user, get_document_service, get_idempotency_port
from api.schemas.document import (
    DocumentChunkDetailEnvelope,
    DocumentChunkPaginatedEnvelope,
    DocumentDetailEnvelope,
    DocumentExtractReferencesEnvelope,
    DocumentExtractReferencesRequest,
    DocumentListPaginatedEnvelope,
    DocumentParseEnvelope,
    DocumentParseRequest,
    DocumentStarEnvelope,
    DocumentStarRequest,
    DocumentStatusEnvelope,
    DocumentStructureEnvelope,
    DocumentUploadEnvelope,
)
from api.schemas.envelope import ResponseMeta
from api.services.document_service import DocumentService
from core.ports.idempotency import IIdempotencyPort
from fastapi import APIRouter, Body, Depends, File, Form, Header, Path, Query, UploadFile, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/documents", tags=["Module 1: Documents"])

UPLOAD_DESCRIPTION = (
    "🎯 **Mục đích:** Tải tệp PDF bài báo lên hệ thống để bắt đầu quy trình bóc "
    "tách.\n"
    "\n"
    "📥 **Đầu vào (multipart/form-data):**\n"
    "- `file`: Tệp PDF bài báo (bắt buộc, tối đa 50MB, magic bytes `%PDF-`).\n"
    "- `session_id`: UUID phiên nghiên cứu cần gắn tài liệu (tùy chọn, tối đa 5 "
    "bài/phiên).\n"
    "\n"
    "📤 **Đầu ra (HTTP 201):**\n"
    "- Trả về `id`, `status: uploaded`, và các liên kết HATEOAS (`status_url`, "
    "`file_url`).\n"
    "\n"
    "⚠️ **Lưu ý:**\n"
    "- Khử trùng lặp CAS: file trùng hash SHA-256 sẽ tái sử dụng bản ghi cũ.\n"
    "- Lỗi thường gặp: `400` (sai định dạng), `413` (>50MB), `409` (phiên đã đầy "
    "5 bài)."
)

LIST_DESCRIPTION = (
    "🎯 **Mục đích:** Hiển thị danh sách bài báo người dùng trên thư viện hoặc "
    "sidebar.\n"
    "\n"
    "📥 **Đầu vào (Query parameters):**\n"
    "- `page`: Số thứ tự trang kết quả (mặc định: `1`, tối thiểu: `1`).\n"
    "- `per_page`: Số lượng bài báo mỗi trang (mặc định: `20`, tối đa: `100`).\n"
    "- `status`: Lọc theo trạng thái (`uploaded`, `processing`, `completed`, "
    "`failed`).\n"
    "\n"
    "📤 **Đầu ra (HTTP 200):**\n"
    "- Mảng `items` tóm tắt bài báo (`id`, `filename`, `title`, `status`, "
    "`created_at`).\n"
    "- Object `meta` phân trang và `links` điều hướng RFC 8288 (`next`, "
    "`prev`...).\n"
    "\n"
    "⚠️ **Lưu ý:**\n"
    "- Sắp xếp mặc định: `created_at DESC` (bài báo mới nhất hiển thị trước).\n"
    "- Đảm bảo cô lập dữ liệu: chỉ hiển thị tài liệu của người dùng hiện tại."
)

DETAIL_DESCRIPTION = (
    "🎯 **Mục đích:** Lấy siêu dữ liệu học thuật và kích thước trang cho Canvas "
    "(PDF.js).\n"
    "\n"
    "📥 **Đầu vào (Path parameter):**\n"
    "- `document_id`: UUID của bài báo khoa học.\n"
    "\n"
    "📤 **Đầu ra (HTTP 200):**\n"
    "- Thông tin học thuật (`title`, `authors`, `doi`, `page_count`, "
    "`chunk_count`...).\n"
    "- `pages_metadata`: Mảng kích thước `[width, height]` và góc xoay từng "
    "trang PDF.\n"
    "\n"
    "⚠️ **Lưu ý:**\n"
    "- Trả về `404` nếu tài liệu không tồn tại hoặc không thuộc quyền sở hữu."
)

FILE_DESCRIPTION = (
    "🎯 **Mục đích:** Cung cấp luồng PDF nhị phân cho Canvas xem trước "
    "(PDF.js).\n"
    "\n"
    "📥 **Đầu vào:**\n"
    "- `document_id`: UUID bài báo (Path parameter).\n"
    "- `Range`: Header tùy chọn (ví dụ: `bytes=0-1024`) để yêu cầu phân đoạn "
    "byte.\n"
    "\n"
    "📤 **Đầu ra:**\n"
    "- Stream nhị phân `application/pdf`.\n"
    "- `HTTP 200 OK`: Tải toàn bộ tệp PDF.\n"
    "- `HTTP 206 Partial Content`: Tải phân đoạn byte phục vụ lazy-load "
    "Canvas.\n"
    "\n"
    "⚠️ **Lưu ý:**\n"
    "- Trả về `416 Range Not Satisfiable` nếu dải byte yêu cầu vượt quá dung "
    "lượng tệp."
)

STATUS_DESCRIPTION = (
    "🎯 **Mục đích:** Frontend polling định kỳ (1-2s) hiển thị tiến độ bóc tách "
    "bài báo.\n"
    "\n"
    "📥 **Đầu vào (Path parameter):**\n"
    "- `document_id`: UUID của bài báo đang xử lý.\n"
    "\n"
    "📤 **Đầu ra (HTTP 200):**\n"
    "- `status`: Trạng thái tổng quát (`uploaded`, `processing`, `completed`, "
    "`failed`).\n"
    "- `progress`: Phần trăm hoàn thành tổng thể (`0` đến `100%`).\n"
    "- `stage`: Tên bước hiện tại (`running_ocr`, `chunking`, `embedding`...).\n"
    "- `stages_detail`: Trạng thái con 5 chặng (`validation`, `ocr`, "
    "`chunking`...).\n"
    "- `error_message`: Chi tiết lỗi nếu bước xử lý gặp sự cố.\n"
    "\n"
    "⚠️ **Lưu ý:**\n"
    '- Dừng polling ngay khi `status == "completed"` hoặc `status == "failed"`.'
)

STAR_DESCRIPTION = (
    "🎯 **Mục đích:** Lưu bài báo từ phiên nghiên cứu tạm thời vào kho thư viện "
    "cá nhân vĩnh viễn (Star).\n\n"
    "📥 **Đầu vào:**\n"
    "- `document_id`: UUID của bài báo khoa học (bắt buộc, Path parameter).\n"
    "- `folder_id`: UUID thư mục đề tài nghiên cứu (tùy chọn, Request body). "
    'Mặc định là `{ "folder_id": null }` để lưu bài báo vào thư viện chung.\n\n'
    "📤 **Đầu ra (HTTP 200):**\n"
    "- Trả về thông tin bài báo với `is_persistent: true` và `folder_id` "
    "đã gán trong một giao dịch ACID.\n\n"
    "⚠️ **Lưu ý:**\n"
    "- Thao tác mang tính lũy thừa (Idempotent): gọi lại nhiều lần sẽ cập nhật "
    "folder_id mà không tạo bản ghi trùng lặp.\n"
    "- Khi thao tác trên Swagger UI: hãy chọn example 'Lưu vào thư viện chung' "
    '({ "folder_id": null }). Chỉ truyền UUID vào folder_id khi bạn đã tạo '
    "thư mục thực tế trong hệ thống."
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


@router.post(
    "/{document_id}:star",
    status_code=status.HTTP_200_OK,
    response_model=DocumentStarEnvelope,
    summary="Lưu bài báo vào thư viện cá nhân (Star/Promotion)",
    description=STAR_DESCRIPTION,
    responses={
        200: {"description": "Lưu bài báo vào thư viện cá nhân thành công."},
        404: {
            "description": "Không tìm thấy bài báo hoặc thư mục được chỉ định.",
        },
        422: {"description": "Định dạng UUID không hợp lệ."},
    },
)
async def star_document(
    document_id: UUID = Path(
        ...,
        description="UUID của bài báo khoa học cần lưu vào thư viện cá nhân",
    ),
    payload: DocumentStarRequest | None = Body(
        default=None,
        openapi_examples={
            "without_folder": {
                "summary": "Lưu vào thư viện chung (Mặc định)",
                "description": (
                    "Lưu bài báo vào thư viện cá nhân mà không gán thư mục (folder_id: null)"
                ),
                "value": {"folder_id": None},
            },
            "with_folder": {
                "summary": "Lưu kèm gán vào thư mục",
                "description": "Lưu bài báo và phân loại vào thư mục nghiên cứu cụ thể",
                "value": {"folder_id": "8a391512-4217-48f1-a1b7-d1fa18600d89"},
            },
        },
    ),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: DocumentService = Depends(get_document_service),
) -> DocumentStarEnvelope:
    """Promote a document to persistent user library retention (Star)."""
    folder_id = payload.folder_id if payload else None
    data = await service.star_document(
        document_id=document_id,
        user_id=current_user.id,
        db=db,
        folder_id=folder_id,
    )
    return DocumentStarEnvelope(
        success=True,
        data=data,
        meta=ResponseMeta(),
    )


DELETE_DESCRIPTION = (
    "🎯 **Mục đích:** Xóa vĩnh viễn bài báo khỏi hệ thống theo đồ thị phụ thuộc "
    "và cam kết không lưu giữ (Zero-Retention Guarantee).\n\n"
    "📥 **Đầu vào (Path parameter):**\n"
    "- `document_id`: UUID của bài báo khoa học cần xóa (bắt buộc).\n\n"
    "📤 **Đầu ra (HTTP 204 No Content):**\n"
    "- Không có nội dung trả về (Empty response body).\n\n"
    "⚠️ **Lưu ý:**\n"
    "- Tự động thực thi `ON DELETE CASCADE` xóa sạch các đoạn văn bản (chunks), "
    "vector nhúng (embeddings), và liên kết phiên làm việc (session_documents).\n"
    "- Tự động giải phóng Content-Addressable Storage (CAS): giảm `ref_count` "
    "trong bảng `document_storage_blobs`; chỉ xóa tệp PDF vật lý trên đĩa "
    "khi `ref_count == 0`.\n"
    "- Đảm bảo cô lập dữ liệu (Multi-tenant): Cố gắng xóa tài liệu của người khác "
    "hoặc tài liệu không tồn tại sẽ nhận mã lỗi `404 DOCUMENT_NOT_FOUND`."
)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa bài báo theo đồ thị phụ thuộc (Zero-Retention)",
    description=DELETE_DESCRIPTION,
    responses={
        204: {
            "description": (
                "Xóa bài báo và các dữ liệu liên quan thành công (Không có nội dung trả về)."
            )
        },
        404: {
            "description": "Không tìm thấy bài báo hoặc người dùng không có quyền truy cập.",
        },
        422: {
            "description": "Định dạng UUID không hợp lệ.",
        },
    },
)
async def delete_document(
    document_id: UUID = Path(
        ...,
        description="UUID của bài báo khoa học cần xóa",
    ),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: DocumentService = Depends(get_document_service),
) -> None:
    """Permanently delete a document, cascading its dependency graph (Zero-Retention)."""
    await service.delete_document(
        document_id=document_id,
        user_id=current_user.id,
        db=db,
    )
    return None


PARSE_DESCRIPTION = (
    "🎯 **Mục đích:** Kích hoạt hoặc bóc tách lại bài báo theo các tùy chọn cấu hình chunking, "
    "hỗ trợ cơ chế Idempotency chống gửi trùng lặp.\n\n"
    "📥 **Đầu vào:**\n"
    "- `document_id`: UUID của bài báo (bắt buộc, Path parameter).\n"
    "- `Idempotency-Key`: UUID khóa khử trùng lặp (tùy chọn, Header, cửa sổ 24 giờ).\n"
    "- `chunk_size`: Kích thước token mục tiêu cho mỗi chunk (mặc định: 512, từ 100 đến 2048).\n"
    "- `chunk_overlap`: Số token gối đầu (mặc định: 50, từ 0 đến 200, phải nhỏ hơn chunk_size).\n"
    "- `extract_tables`: Bật nhận diện bố cục bảng biểu & hình ảnh chuyên sâu (mặc định: true).\n"
    "- `force_reparse`: Bắt buộc tái bóc tách lại bài báo (mặc định: false).\n\n"
    "📤 **Đầu ra (HTTP 202 Accepted):**\n"
    "- Trả về `id`, `status: processing`, `stage: validation`, `progress: 0`, và các liên kết "
    "HATEOAS (`status_url`, `detail_url`).\n\n"
    "⚠️ **Lưu ý:**\n"
    "- Khi gửi kèm `Idempotency-Key`, các request trùng lặp trong 24 giờ sẽ nhận lại phản hồi gốc "
    "kèm header `X-Cache: Idempotent-Hit` mà không thực thi lại pipeline.\n"
    "- Nếu tài liệu đang xử lý (`status=processing`) và không bật `force_reparse=true`, hệ thống "
    "trả về lỗi `409 DOCUMENT_PROCESSING`.\n"
    "- Nếu tài liệu đã hoàn tất (`status=completed`) và không bật `force_reparse=true`, hệ thống "
    "trả về thông báo trạng thái hiện tại kèm hướng dẫn sử dụng `force_reparse`.\n"
    "- Lỗi thường gặp: `404` (không tìm thấy), `409` (đang xử lý), `422` (sai định dạng)."
)


@router.post(
    "/{document_id}:parse",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=DocumentParseEnvelope,
    summary="Kích hoạt / Bóc tách lại với Idempotency",
    description=PARSE_DESCRIPTION,
    responses={
        202: {
            "description": "Tiến trình bóc tách bài báo được tiếp nhận thành công.",
            "model": DocumentParseEnvelope,
        },
        404: {
            "description": "Không tìm thấy bài báo hoặc người dùng không có quyền truy cập.",
        },
        409: {
            "description": "Bài báo đang trong tiến trình xử lý và chưa hoàn tất.",
        },
        422: {
            "description": "Tham số đầu vào hoặc UUID không hợp lệ.",
        },
    },
)
async def parse_document(
    document_id: UUID = Path(
        ...,
        description="UUID của bài báo khoa học cần bóc tách",
    ),
    payload: DocumentParseRequest = Body(
        default_factory=DocumentParseRequest,
        description="Tùy chọn cấu hình bóc tách và chunking",
    ),
    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key",
        description="Khóa UUID khử trùng lặp trong vòng 24 giờ",
    ),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: DocumentService = Depends(get_document_service),
    idempotency: IIdempotencyPort = Depends(get_idempotency_port),
) -> DocumentParseEnvelope | JSONResponse:
    """Trigger or re-trigger document parsing with 24-hour idempotency protection."""
    cache_key = None
    if idempotency_key:
        cache_key = f"idempotency:parse:{current_user.id}:{document_id}:{idempotency_key}"
        cached_resp = await idempotency.get_response(cache_key)
        if cached_resp is not None:
            return JSONResponse(
                status_code=status.HTTP_202_ACCEPTED,
                content=cached_resp,
                headers={"X-Cache": "Idempotent-Hit"},
            )

    data = await service.trigger_parse_document(
        document_id=document_id,
        user_id=current_user.id,
        parse_req=payload,
        db=db,
    )

    envelope = DocumentParseEnvelope(
        data=data,
        meta=ResponseMeta(),
    )
    envelope_dict = envelope.model_dump(mode="json")

    if cache_key:
        await idempotency.store_response(
            key=cache_key,
            response_data=envelope_dict,
            status_code=status.HTTP_202_ACCEPTED,
            ttl_seconds=86400,
        )
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content=envelope_dict,
            headers={"X-Cache": "Miss"},
        )

    return envelope


EXTRACT_REFERENCES_DESCRIPTION = (
    "🎯 **Mục đích:** Bóc tách toàn bộ danh mục tài liệu tham khảo (References / Bibliography) "
    "từ bài báo khoa học, phân tích cú pháp chi tiết thành các trường học thuật (Title, Authors, "
    "Year, arXiv ID, DOI) và lưu vào cơ sở dữ liệu.\n\n"
    "📥 **Đầu vào:**\n"
    "- `document_id`: UUID của bài báo khoa học (bắt buộc, Path parameter).\n"
    "- `force_reextract`: Bỏ qua bộ nhớ đệm DB và bóc tách lại từ PDF (mặc định: false).\n\n"
    "📤 **Đầu ra (HTTP 200 OK):**\n"
    "- `document_id`: UUID tài liệu.\n"
    "- `total_extracted`: Tổng số tài liệu tham khảo bóc tách được.\n"
    "- `references`: Danh sách tham khảo với `ref_index`, `raw_text` và `parsed` "
    "(title, authors, year, arxiv_id, doi).\n\n"
    "⚠️ **Lưu ý:**\n"
    "- Sử dụng bộ đệm database: Lần gọi tiếp theo trả về kết quả ngay (< 15ms).\n"
    "- Đảm bảo cô lập người dùng: Trả về `404 DOCUMENT_NOT_FOUND` nếu không thuộc quyền sở hữu."
)


@router.post(
    "/{document_id}:extract-references",
    status_code=status.HTTP_200_OK,
    response_model=DocumentExtractReferencesEnvelope,
    summary="Bóc tách danh mục tài liệu tham khảo",
    description=EXTRACT_REFERENCES_DESCRIPTION,
    responses={
        200: {
            "description": "Bóc tách danh mục tài liệu tham khảo thành công.",
            "model": DocumentExtractReferencesEnvelope,
        },
        404: {
            "description": "Không tìm thấy bài báo hoặc người dùng không có quyền truy cập.",
        },
        422: {
            "description": "Định dạng UUID không hợp lệ.",
        },
    },
)
async def extract_references(
    document_id: UUID = Path(
        ...,
        description="UUID của bài báo khoa học cần bóc tách danh mục tham khảo",
    ),
    payload: DocumentExtractReferencesRequest | None = Body(
        default=None,
        description="Tùy chọn cấu hình bóc tách tài liệu tham khảo",
    ),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: DocumentService = Depends(get_document_service),
) -> DocumentExtractReferencesEnvelope:
    """Extract or retrieve structured scholarly references from a document."""
    force_reextract = payload.force_reextract if payload else False
    data = await service.extract_document_references(
        document_id=document_id,
        user_id=current_user.id,
        db=db,
        force_reextract=force_reextract,
    )
    return DocumentExtractReferencesEnvelope(
        success=True,
        data=data,
        meta=ResponseMeta(),
    )


GET_STRUCTURE_DESCRIPTION = (
    "🎯 **Mục đích:** Truy xuất cấu trúc phân cấp bài báo khoa học (Table of Contents, "
    "Headings, Sections và Abstract) kèm tọa độ Bounding Box chuẩn hóa để phục vụ điều hướng "
    "và hiển thị trên giao diện Deep Reading Canvas (PDF.js).\n\n"
    "📥 **Đầu vào:**\n"
    "- `document_id`: UUID của bài báo khoa học (bắt buộc, Path parameter).\n"
    "- `force_refresh`: Bỏ qua bộ đệm database và ép bóc tách lại từ tệp PDF gốc "
    "(mặc định: false, Query parameter).\n\n"
    "📤 **Đầu ra (HTTP 200 OK):**\n"
    "- `document_id`: UUID tài liệu.\n"
    "- `title`: Tiêu đề học thuật của bài báo.\n"
    "- `abstract`: Toàn văn phần tóm tắt tác giả.\n"
    "- `abstract_bounding_boxes`: Danh sách Bounding Box chuẩn hóa [[x0, y0, x1, y1, page], ...].\n"
    "- `sections`: Danh sách các mục (title, page_number, bounding_boxes).\n\n"
    "⚠️ **Lưu ý:**\n"
    "- Tối ưu hóa phản hồi: Trả về trực tiếp từ bộ đệm database (< 15ms) nếu đã được xử lý.\n"
    "- Đảm bảo cô lập người dùng: Trả về `404 DOCUMENT_NOT_FOUND` nếu không thuộc quyền sở hữu."
)


@router.get(
    "/{document_id}/structure",
    status_code=status.HTTP_200_OK,
    response_model=DocumentStructureEnvelope,
    summary="Truy xuất cấu trúc bài báo (TOC, Headings, Sections)",
    description=GET_STRUCTURE_DESCRIPTION,
    responses={
        200: {
            "description": "Truy xuất cấu trúc bài báo thành công.",
            "model": DocumentStructureEnvelope,
        },
        404: {
            "description": "Không tìm thấy bài báo hoặc người dùng không có quyền truy cập.",
        },
        422: {
            "description": "Định dạng UUID không hợp lệ.",
        },
    },
)
async def get_document_structure(
    document_id: UUID = Path(
        ...,
        description="UUID của bài báo khoa học cần truy xuất cấu trúc",
    ),
    force_refresh: bool = Query(
        default=False,
        description="Nếu True, bỏ qua bộ nhớ đệm và phân tích lại cấu trúc từ PDF",
    ),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: DocumentService = Depends(get_document_service),
) -> DocumentStructureEnvelope:
    """Retrieve or extract hierarchical document structure (TOC, abstract, and sections)."""
    data = await service.get_document_structure(
        document_id=document_id,
        user_id=current_user.id,
        db=db,
        force_refresh=force_refresh,
    )
    return DocumentStructureEnvelope(
        success=True,
        data=data,
        meta=ResponseMeta(),
    )


GET_CHUNKS_DESCRIPTION = (
    "🎯 **Mục đích:** Truy xuất danh sách các khối văn bản ngữ nghĩa (Chunks) "
    "kèm tọa độ không gian chính xác (Bounding Boxes) để hiển thị lớp phủ highlight "
    "trực quan trên PDF.js Web Canvas.\n\n"
    "📥 **Đầu vào:**\n"
    "- `document_id`: UUID của bài báo (bắt buộc, Path parameter).\n"
    "- `page`: Số thứ tự trang phân trang kết quả (mặc định: 1, 1-indexed).\n"
    "- `per_page`: Số lượng chunk trên mỗi trang kết quả (mặc định: 50, 1-200).\n"
    "- `page_number`: Tùy chọn lọc các chunk thuộc riêng một trang vật lý của "
    "file PDF (1-indexed).\n"
    "- `include_content`: Cờ tối ưu băng thông (mặc định: true). Khi đặt `false`, "
    "trường `content` trả về `null`, giúp tiết kiệm hơn 80% dung lượng payload "
    "chỉ để vẽ highlight.\n\n"
    "📤 **Đầu ra (HTTP 200 OK):**\n"
    "- Danh sách các chunks kèm theo siêu dữ liệu phân trang chuẩn RFC 8288 "
    "(first, prev, self, next, last).\n\n"
    "⚠️ **Lưu ý:**\n"
    "- Nếu tài liệu chưa từng được phân đoạn trước đó, hệ thống sẽ tự động bóc "
    "tách và lưu vào cơ sở dữ liệu."
)


@router.get(
    "/{document_id}/chunks",
    status_code=status.HTTP_200_OK,
    response_model=DocumentChunkPaginatedEnvelope,
    summary="Danh sách Chunks (phân trang + include_content)",
    description=GET_CHUNKS_DESCRIPTION,
    responses={
        200: {"description": "Truy xuất danh sách chunks thành công kèm siêu dữ liệu phân trang."},
        404: {"description": "Không tìm thấy tài liệu hoặc người dùng không có quyền truy cập."},
        422: {"description": "Tham số phân trang hoặc định dạng UUID không hợp lệ."},
    },
)
async def get_document_chunks(
    document_id: UUID = Path(
        ...,
        description="UUID của bài báo khoa học",
    ),
    page: int = Query(
        1,
        ge=1,
        description="Số thứ tự trang kết quả (1-indexed)",
    ),
    per_page: int = Query(
        50,
        ge=1,
        le=200,
        description="Số lượng chunks tối đa trên mỗi trang (1-200)",
    ),
    page_number: int | None = Query(
        None,
        ge=1,
        description="Tùy chọn lọc các chunk thuộc riêng một trang cụ thể của file PDF",
    ),
    include_content: bool = Query(
        True,
        description=(
            "Nếu false, trường content trả về null giúp giảm >80% dung lượng "
            "payload phục vụ vẽ Canvas"
        ),
    ),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: DocumentService = Depends(get_document_service),
) -> DocumentChunkPaginatedEnvelope:
    """Retrieve paginated chunks of a document with visual grounding bounding boxes."""
    return await service.get_document_chunks(
        document_id=document_id,
        user_id=current_user.id,
        db=db,
        page=page,
        per_page=per_page,
        page_number=page_number,
        include_content=include_content,
    )


GET_CHUNK_DETAIL_DESCRIPTION = (
    "🎯 **Mục đích:** Truy xuất toàn văn nội dung, tọa độ Bounding Boxes hình học "
    "chuẩn hóa và liên kết điều hướng lân cận cho một đoạn bằng chứng (Chunk) cụ thể.\n"
    "\n"
    "📥 **Đầu vào (Path parameters):**\n"
    "- `document_id`: UUID của bài báo khoa học.\n"
    "- `chunk_id`: UUID của đoạn bằng chứng (Chunk).\n"
    "\n"
    "📤 **Đầu ra (HTTP 200):**\n"
    "- `content`: Toàn văn nội dung đoạn văn bản.\n"
    "- `bounding_boxes`: Danh sách tọa độ chuẩn hóa [[x0, y0, x1, y1, page], ...] "
    "hỗ trợ Deep Reading Canvas highlight.\n"
    "- `token_count`: Số lượng tokens tính toán của đoạn.\n"
    "- `links`: Các liên kết điều hướng lân cận `prev_chunk` và `next_chunk` "
    "phục vụ Citation Inspector duyệt mở rộng ngữ cảnh.\n"
    "\n"
    "⚠️ **Lưu ý:**\n"
    "- Nếu `chunk_id` không tồn tại trong tài liệu: trả về `404 CHUNK_NOT_FOUND`.\n"
    "- Nếu `document_id` không tồn tại hoặc sai quyền sở hữu: trả về `404 DOCUMENT_NOT_FOUND`."
)


@router.get(
    "/{document_id}/chunks/{chunk_id}",
    status_code=status.HTTP_200_OK,
    response_model=DocumentChunkDetailEnvelope,
    summary="Chi tiết 1 đoạn bằng chứng (Chunk Detail + Nav Links)",
    description=GET_CHUNK_DETAIL_DESCRIPTION,
    responses={
        200: {
            "description": (
                "Truy xuất chi tiết đoạn bằng chứng thành công kèm tọa độ bounding boxes "
                "và navigational links."
            )
        },
        404: {"description": "Không tìm thấy tài liệu hoặc không tìm thấy chunk tương ứng."},
        422: {"description": "Định dạng UUID không hợp lệ."},
    },
)
async def get_document_chunk_detail(
    document_id: UUID = Path(
        ...,
        description="UUID của bài báo khoa học",
    ),
    chunk_id: UUID = Path(
        ...,
        description="UUID của đoạn bằng chứng (Chunk)",
    ),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: DocumentService = Depends(get_document_service),
) -> DocumentChunkDetailEnvelope:
    """Retrieve detailed content, spatial coordinates, and traversal links of a single chunk."""
    return await service.get_document_chunk_detail(
        document_id=document_id,
        chunk_id=chunk_id,
        user_id=current_user.id,
        db=db,
    )
