"""API Endpoints for Academic Research Writing & Drafts (Module 2)."""

import io
import json
import math
from collections.abc import AsyncIterator
from uuid import UUID, uuid4

import structlog
from api.db.models.user import UserModel
from api.deps import (
    get_current_user,
    get_draft_service,
)
from api.schemas.draft import (
    CompileDraftResponse,
    CreateDraftAssetRequest,
    CreateDraftRequest,
    DraftAssetListResponse,
    DraftAssetResponse,
    DraftAssistRequest,
    DraftAssistResponse,
    DraftChatStreamRequest,
    DraftCompileClearCacheResponse,
    DraftResponse,
    DraftSyncTexForwardRequest,
    DraftSyncTexForwardResponse,
    DraftSyncTexInverseRequest,
    DraftSyncTexInverseResponse,
    LatexSyntaxErrorResponse,
    UpdateDraftRequest,
)
from api.schemas.envelope import (
    PaginatedResponseEnvelope,
    PaginationLinks,
    PaginationMeta,
    SingleResponseEnvelope,
)
from api.schemas.error import ErrorResponse
from api.services.draft_service import DraftService
from core.domain.entities.draft import can_call_costly_ai
from core.domain.exceptions import (
    AssetQuotaExceededError,
    ConcurrencyConflictError,
    DraftRoleForbiddenError,
    MaliciousAssetContentError,
    ZipSlipSecurityError,
)
from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from fastapi.responses import Response as RawResponse
from fastapi.responses import StreamingResponse

logger = structlog.get_logger("api.endpoints.drafts")

router = APIRouter(prefix="/drafts", tags=["drafts"])


def parse_version_from_etag(etag: str | None) -> int | None:
    """Parse integer version from If-Match HTTP ETag header (RFC 9110 / RFC 7232)."""
    if not etag:
        return None
    cleaned = etag.strip(' "W/w')
    if cleaned.startswith(("v", "V")):
        cleaned = cleaned[1:]
    try:
        ver = int(cleaned)
        if ver < 1:
            raise ValueError()
        return ver
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_IF_MATCH_HEADER",
                "message": f"Giá trị If-Match không hợp lệ: '{etag}'. Định dạng chuẩn: '\"v1\"'.",
                "action": "Provide valid If-Match version tag.",
            },
        )


CREATE_DRAFT_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Tạo mới một bản thảo nghiên cứu khoa học (LaTeX hoặc Markdown) trong không gian làm việc Module 2.

📥 **Tham số đầu vào (Request Body application/json):**
- `title` (string, Mặc định: "Untitled Draft"): Tiêu đề bài báo/bản thảo.
- `content` (string, Tùy chọn): Nội dung ban đầu (mã nguồn LaTeX hoặc Markdown).
- `format` (string, Mặc định: "latex"): Định dạng văn bản ("latex" hoặc "markdown").

📤 **Đầu ra & Dữ liệu phản hồi:**
- `HTTP 201 Created`: Trả về `SingleResponseEnvelope[DraftResponse]` chứa dữ liệu bản thảo.
- Headers phản hồi:
  - `Location: /api/v1/drafts/{id}`: Đường dẫn tài nguyên vừa tạo.
  - `ETag: "v1"`: Khóa phiên bản khởi tạo cho OCC."""

LIST_DRAFTS_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Truy xuất danh sách bản thảo của người dùng hiện tại phục vụ hiển thị Dashboard hoặc danh sách chọn.

📥 **Tham số đầu vào (Query Parameters):**
- `page` (int, Mặc định: 1): Số trang (1-indexed).
- `per_page` (int, Mặc định: 20, Tối đa: 100): Số bản thảo mỗi trang."""

GET_DRAFT_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Lấy toàn bộ nội dung chi tiết của bản thảo nghiên cứu theo ID.

📤 **Đầu ra & Dữ liệu phản hồi:**
- `HTTP 200 OK`: `SingleResponseEnvelope[DraftResponse]`
- Header: `ETag: "v{version}"`"""

UPDATE_DRAFT_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Chỉnh sửa tiêu đề, nội dung hoặc định dạng bản thảo với kiểm soát đồng thời lạc quan (OCC).

🔄 **Cơ chế Optimistic Concurrency Control (OCC):**
Cần cung cấp header `If-Match: "v{version}"` hoặc trường `version` trong request body.
Nếu phiên bản không khớp với DB, server trả về `HTTP 412 Precondition Failed`."""


@router.post(
    "",
    response_model=SingleResponseEnvelope[DraftResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Tạo mới bản thảo nghiên cứu (Create Draft)",
    description=CREATE_DRAFT_DESCRIPTION,
    responses={
        201: {"description": "Bản thảo đã được khởi tạo thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực hoặc token không hợp lệ."},
    },
)
async def create_draft(
    request: CreateDraftRequest,
    response: Response,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> SingleResponseEnvelope[DraftResponse]:
    try:
        draft = await draft_service.create_draft(user_id=current_user.id, request=request)
    except KeyError as exc:
        if "SOURCE_SESSION_NOT_FOUND" in str(exc):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "SOURCE_SESSION_NOT_FOUND",
                    "message": "Không tìm thấy phiên nghiên cứu nguồn tương ứng.",
                    "field": "source_session_id",
                },
            )
        raise

    response.headers["Location"] = f"/api/v1/drafts/{draft.id}"
    response.headers["ETag"] = f'"{draft.version}"'
    return SingleResponseEnvelope(
        data=DraftResponse.model_validate(draft),
    )


@router.get(
    "",
    response_model=PaginatedResponseEnvelope[DraftResponse],
    summary="Liệt kê danh sách bản thảo (List Drafts)",
    description=LIST_DRAFTS_DESCRIPTION,
    responses={
        200: {"description": "Danh sách bản thảo được phân trang thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
    },
)
async def list_drafts(
    req: Request,
    page: int = Query(default=1, ge=1, description="Số thứ tự trang kết quả (1-indexed)"),
    per_page: int = Query(default=20, ge=1, le=100, description="Số lượng bản thảo mỗi trang"),
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> PaginatedResponseEnvelope[DraftResponse]:
    skip = (page - 1) * per_page
    items, total = await draft_service.list_drafts(
        user_id=current_user.id,
        skip=skip,
        limit=per_page,
    )
    total_pages = math.ceil(total / per_page) if total > 0 else 1
    base_url = str(req.url).split("?")[0]

    links = PaginationLinks(
        first=f"{base_url}?page=1&per_page={per_page}",
        prev=f"{base_url}?page={page - 1}&per_page={per_page}" if page > 1 else None,
        self=f"{base_url}?page={page}&per_page={per_page}",
        next=f"{base_url}?page={page + 1}&per_page={per_page}" if page < total_pages else None,
        last=f"{base_url}?page={total_pages}&per_page={per_page}",
    )

    return PaginatedResponseEnvelope(
        data=[DraftResponse.model_validate(d) for d in items],
        meta=PaginationMeta(
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            request_id=getattr(req.state, "request_id", None) or f"req_{uuid4().hex[:12]}",
        ),
        links=links,
    )


@router.get(
    "/{id}",
    response_model=SingleResponseEnvelope[DraftResponse],
    summary="Lấy chi tiết bản thảo (Get Draft Details)",
    description=GET_DRAFT_DESCRIPTION,
    responses={
        200: {"description": "Thông tin chi tiết bản thảo."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        404: {"model": ErrorResponse, "description": "Bản thảo không tồn tại."},
    },
)
async def get_draft(
    id: UUID,
    response: Response,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> SingleResponseEnvelope[DraftResponse]:
    draft = await draft_service.get_draft(
        user_id=current_user.id,
        draft_id=id,
        user_email=current_user.email,
    )
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DRAFT_NOT_FOUND",
                "message": f"Bản thảo {id} không tồn tại hoặc bạn không có quyền truy cập.",
            },
        )
    response.headers["ETag"] = f'"{draft.version}"'
    return SingleResponseEnvelope(
        data=DraftResponse.model_validate(draft),
    )


@router.put(
    "/{id}",
    response_model=SingleResponseEnvelope[DraftResponse],
    summary="Cập nhật bản thảo với OCC (Update Draft)",
    description=UPDATE_DRAFT_DESCRIPTION,
    responses={
        200: {"description": "Bản thảo đã cập nhật thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        403: {"model": ErrorResponse, "description": "Vai trò không có quyền sửa đổi."},
        404: {"model": ErrorResponse, "description": "Bản thảo không tồn tại."},
        412: {"model": ErrorResponse, "description": "Xung đột phiên bản (OCC Conflict)."},
        428: {
            "model": ErrorResponse,
            "description": "Thiếu thông tin phiên bản (If-Match hoặc version trong body).",
        },
    },
)
@router.patch(
    "/{id}",
    response_model=SingleResponseEnvelope[DraftResponse],
    summary="Cập nhật bản thảo với OCC (Update Draft - PATCH)",
    description=UPDATE_DRAFT_DESCRIPTION,
    responses={
        200: {"description": "Bản thảo đã cập nhật thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        403: {"model": ErrorResponse, "description": "Vai trò không có quyền sửa đổi."},
        404: {"model": ErrorResponse, "description": "Bản thảo không tồn tại."},
        412: {"model": ErrorResponse, "description": "Xung đột phiên bản (OCC Conflict)."},
        428: {
            "model": ErrorResponse,
            "description": "Thiếu thông tin phiên bản (If-Match hoặc version trong body).",
        },
    },
)
async def update_draft(
    id: UUID,
    request: UpdateDraftRequest,
    response: Response,
    if_match: str | None = Header(None, alias="If-Match"),
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> SingleResponseEnvelope[DraftResponse]:
    # OCC resolution: If-Match header takes precedence over request body
    header_version = parse_version_from_etag(if_match)
    effective_version = header_version if header_version is not None else request.version

    if effective_version is None:
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail={
                "code": "PRECONDITION_REQUIRED",
                "message": (
                    "Header 'If-Match' hoặc trường 'version' trong body là bắt buộc "
                    "để cập nhật bản thảo."
                ),
                "action": 'Provide If-Match: "v{version}" header or version in body.',
            },
        )

    # Re-sync effective version into request object for service
    request.version = effective_version

    try:
        updated_draft = await draft_service.update_draft(
            user_id=current_user.id,
            draft_id=id,
            request=request,
            user_email=current_user.email,
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DRAFT_NOT_FOUND",
                "message": f"Bản thảo {id} không tồn tại hoặc bạn không có quyền truy cập.",
            },
        )
    except DraftRoleForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE_RESTRICTED",
                "message": str(exc),
                "action": "Contact the draft owner for editor permissions.",
            },
        ) from exc
    except ConcurrencyConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail={
                "code": "CONCURRENCY_CONFLICT",
                "message": str(exc),
                "action": (
                    f"Re-fetch draft GET /api/v1/drafts/{id} to get the latest "
                    "version before retrying."
                ),
            },
        ) from exc

    response.headers["ETag"] = f'"{updated_draft.version}"'
    return SingleResponseEnvelope(
        data=DraftResponse.model_validate(updated_draft),
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa vĩnh viễn bản thảo (Delete Draft)",
    responses={
        204: {"description": "Bản thảo đã được xóa thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        403: {"model": ErrorResponse, "description": "Không có quyền xóa bản thảo."},
        404: {"model": ErrorResponse, "description": "Bản thảo không tồn tại."},
    },
)
async def delete_draft(
    id: UUID,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> RawResponse:
    try:
        success = await draft_service.delete_draft(
            user_id=current_user.id,
            draft_id=id,
            user_email=current_user.email,
        )
    except DraftRoleForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE_RESTRICTED",
                "message": str(exc),
                "action": "Only the draft owner can delete this draft.",
            },
        ) from exc

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DRAFT_NOT_FOUND",
                "message": f"Bản thảo {id} không tồn tại hoặc bạn không có quyền truy cập.",
            },
        )
    return RawResponse(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{id}:undo",
    response_model=SingleResponseEnvelope[DraftResponse],
    summary="Hoàn tác thay đổi của AI (Undo AI Changes)",
    description="Khôi phục main.tex và references.bib về trạng thái previous_snapshot.",
    responses={
        200: {"description": "Bản thảo đã được hoàn tác về snapshot trước."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        403: {"model": ErrorResponse, "description": "Vai trò không có quyền sửa đổi."},
        404: {"model": ErrorResponse, "description": "Bản thảo không tồn tại."},
        409: {"model": ErrorResponse, "description": "Không có snapshot để hoàn tác."},
    },
)
@router.post(
    "/{id}/undo",
    response_model=SingleResponseEnvelope[DraftResponse],
    include_in_schema=False,
)
async def undo_draft(
    id: UUID,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> SingleResponseEnvelope[DraftResponse]:
    try:
        restored_draft = await draft_service.undo_draft_snapshot(
            user_id=current_user.id,
            draft_id=id,
            user_email=current_user.email,
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DRAFT_NOT_FOUND",
                "message": f"Bản thảo {id} không tồn tại hoặc bạn không có quyền truy cập.",
            },
        )
    except DraftRoleForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE_RESTRICTED",
                "message": str(exc),
                "action": "Only editors and owners can undo draft changes.",
            },
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "NO_UNDO_SNAPSHOT_AVAILABLE",
                "message": "Không có bản sao lưu trước đó để thực hiện thao tác hoàn tác.",
                "action": "Nút hoàn tác chỉ khả dụng sau khi AI đã can thiệp.",
            },
        ) from exc

    return SingleResponseEnvelope(
        data=DraftResponse.model_validate(restored_draft),
    )


@router.post(
    "/{id}/compile",
    response_model=SingleResponseEnvelope[CompileDraftResponse],
    summary="Biên dịch bản thảo với sandbox tự vá lỗi (Compile Draft)",
    description=(
        "Biên dịch mã nguồn LaTeX của bản thảo trong sandbox với cơ chế "
        "tự vá lỗi Agentic (tối đa 3 lần thử)."
    ),
    responses={
        200: {"description": "Kết quả biên dịch hoặc tự vá lỗi."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        403: {"model": ErrorResponse, "description": "Vai trò không có quyền biên dịch."},
        404: {"model": ErrorResponse, "description": "Bản thảo không tồn tại."},
    },
)
async def compile_draft(
    id: UUID,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> SingleResponseEnvelope[CompileDraftResponse]:
    try:
        result, preview_url = await draft_service.compile_draft(
            user_id=current_user.id,
            draft_id=id,
            user_email=current_user.email,
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DRAFT_NOT_FOUND",
                "message": f"Bản thảo {id} không tồn tại hoặc bạn không có quyền truy cập.",
            },
        )
    except DraftRoleForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE_RESTRICTED",
                "message": str(exc),
                "action": "Viewer and commenter roles cannot compile LaTeX.",
            },
        ) from exc

    errors_response = [
        LatexSyntaxErrorResponse(
            line=e.line,
            column=e.column,
            rule=e.rule,
            message=e.message,
            suggested_fix=e.suggested_fix,
        )
        for e in result.errors
    ]

    response_data = CompileDraftResponse(
        draft_id=id,
        success=result.success,
        pdf_preview_url=preview_url,
        errors=errors_response,
        logs=result.logs,
        retries_attempted=result.retries_attempted,
        is_sandboxed=result.is_sandboxed,
    )
    return SingleResponseEnvelope(data=response_data)


@router.post(
    "/{id}/compile:clear-cache",
    response_model=SingleResponseEnvelope[DraftCompileClearCacheResponse],
    summary="Xóa bộ nhớ đệm và biên dịch lại sạch (Compile Clear Cache)",
    description=(
        "Xóa bộ nhớ đệm /tmp/drafts/{id}/cache/ và biên dịch lại từ đầu bằng Overleaf CLSI."
    ),
    responses={
        200: {"description": "Kết quả biên dịch sạch."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        403: {"model": ErrorResponse, "description": "Không có quyền biên dịch."},
        404: {"model": ErrorResponse, "description": "Bản thảo không tồn tại."},
    },
)
@router.post(
    "/{id}/compile/clear-cache",
    response_model=SingleResponseEnvelope[DraftCompileClearCacheResponse],
    include_in_schema=False,
)
async def compile_clear_cache(
    id: UUID,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> SingleResponseEnvelope[DraftCompileClearCacheResponse]:
    try:
        result = await draft_service.compile_draft_clsi(
            user_id=current_user.id,
            draft_id=id,
            clear_cache=True,
            user_email=current_user.email,
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DRAFT_NOT_FOUND",
                "message": f"Bản thảo {id} không tồn tại hoặc bạn không có quyền truy cập.",
            },
        )
    except DraftRoleForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE_RESTRICTED",
                "message": str(exc),
            },
        ) from exc

    pdf_url = f"/api/v1/drafts/{id}/preview.pdf" if result.get("pdf_path") else None
    response_data = DraftCompileClearCacheResponse(
        draft_id=id,
        cache_cleared=True,
        success=result.get("success", False),
        pdf_preview_url=pdf_url,
        logs=result.get("logs", ""),
        diagnostics=result.get("diagnostics", []),
    )
    return SingleResponseEnvelope(data=response_data)


@router.api_route(
    "/{id}/preview.pdf",
    methods=["GET", "HEAD"],
    summary="Tải bản xem trước PDF trực tiếp (Live PDF Preview)",
    description="Truy xuất file PDF đã biên dịch của bản thảo để hiển thị trên PDF.js Canvas.",
    responses={
        200: {"content": {"application/pdf": {}}, "description": "Dữ liệu PDF nhị phân."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        403: {
            "model": ErrorResponse,
            "description": "Vai trò không có quyền xem bản dựng preview.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Bản thảo hoặc bản dựng preview không tồn tại.",
        },
    },
)
async def get_draft_preview(
    id: UUID,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> RawResponse:
    try:
        pdf_bytes = await draft_service.get_draft_preview_pdf(
            user_id=current_user.id,
            draft_id=id,
            user_email=current_user.email,
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DRAFT_NOT_FOUND",
                "message": f"Bản thảo {id} không tồn tại hoặc bạn không có quyền truy cập.",
            },
        )
    except DraftRoleForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE_RESTRICTED",
                "message": str(exc),
                "action": "Viewer and commenter roles cannot compile preview PDF.",
            },
        ) from exc

    if not pdf_bytes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "PDF_PREVIEW_NOT_READY",
                "message": "Không thể tạo bản xem trước PDF do lỗi biên dịch chưa được vá.",
                "action": (
                    f"Call POST /api/v1/drafts/{id}/compile first to inspect compilation errors."
                ),
            },
        )

    return RawResponse(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="draft_{id.hex[:8]}_preview.pdf"'},
    )


@router.post(
    "/{id}/synctex:forward",
    response_model=SingleResponseEnvelope[DraftSyncTexForwardResponse],
    summary="Đồng bộ thuận SyncTeX: Dòng code -> Tọa độ PDF (Forward Search)",
    responses={
        200: {"description": "Tọa độ trang PDF."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        404: {"model": ErrorResponse, "description": "Bản thảo hoặc PDF không tồn tại."},
    },
)
@router.post(
    "/{id}/synctex/forward",
    response_model=SingleResponseEnvelope[DraftSyncTexForwardResponse],
    include_in_schema=False,
)
async def synctex_forward_endpoint(
    id: UUID,
    request: DraftSyncTexForwardRequest,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> SingleResponseEnvelope[DraftSyncTexForwardResponse]:
    try:
        coords = await draft_service.synctex_forward(
            user_id=current_user.id,
            draft_id=id,
            file=request.file,
            line=request.line,
            column=request.column,
            user_email=current_user.email,
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DRAFT_NOT_FOUND",
                "message": f"Bản thảo {id} không tồn tại hoặc bạn không có quyền truy cập.",
            },
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "PDF_NOT_COMPILED",
                "message": str(exc),
            },
        ) from exc

    return SingleResponseEnvelope(
        data=DraftSyncTexForwardResponse.model_validate(coords),
    )


@router.post(
    "/{id}/synctex:inverse",
    response_model=SingleResponseEnvelope[DraftSyncTexInverseResponse],
    summary="Đồng bộ nghịch SyncTeX: Nhấp điểm PDF -> Dòng code (Inverse Search)",
    responses={
        200: {"description": "Tệp và dòng mã nguồn tương ứng."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        404: {"model": ErrorResponse, "description": "Bản thảo hoặc PDF không tồn tại."},
    },
)
@router.post(
    "/{id}/synctex/inverse",
    response_model=SingleResponseEnvelope[DraftSyncTexInverseResponse],
    include_in_schema=False,
)
async def synctex_inverse_endpoint(
    id: UUID,
    request: DraftSyncTexInverseRequest,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> SingleResponseEnvelope[DraftSyncTexInverseResponse]:
    try:
        loc = await draft_service.synctex_inverse(
            user_id=current_user.id,
            draft_id=id,
            page=request.page,
            x=request.x,
            y=request.y,
            user_email=current_user.email,
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DRAFT_NOT_FOUND",
                "message": f"Bản thảo {id} không tồn tại hoặc bạn không có quyền truy cập.",
            },
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "PDF_NOT_COMPILED",
                "message": str(exc),
            },
        ) from exc

    return SingleResponseEnvelope(
        data=DraftSyncTexInverseResponse.model_validate(loc),
    )


EXPORT_BUNDLE_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Tự động đóng gói trọn bộ cấu trúc thư mục đạt chuẩn nộp bài cho các hội nghị và
tạp chí quốc tế (IEEE, ACM, Springer, Elsevier, arXiv).

📦 **Cấu trúc gói nộp bài (.zip):**
- `main.tex` (hoặc `main.md`): Mã nguồn tài liệu chính.
- `references.bib`: Danh mục trích dẫn BibTeX tự động phân giải.
- `preview.pdf`: Bản dựng PDF hoàn chỉnh chất lượng in ấn.
- `figures/`: Thư mục chứa hình ảnh minh họa (.gitkeep).
- `README.txt`: Hướng dẫn biên dịch và tái lập kết quả."""


@router.post(
    "/{id}:export-bundle",
    summary="Xuất gói nộp bài học thuật chuẩn quốc tế (Camera-Ready Submission Bundle)",
    description=EXPORT_BUNDLE_DESCRIPTION,
    responses={
        200: {
            "content": {"application/zip": {}},
            "description": "Tệp tin nén ZIP chuẩn học thuật.",
        },
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        403: {
            "model": ErrorResponse,
            "description": "Vai trò không có quyền tải submission bundle.",
        },
        404: {"model": ErrorResponse, "description": "Bản thảo không tồn tại."},
    },
)
@router.post(
    "/{id}/export-bundle",
    include_in_schema=False,
)
@router.get(
    "/{id}/export-bundle",
    include_in_schema=False,
)
async def export_draft_bundle(
    id: UUID,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> StreamingResponse:
    try:
        zip_bytes = await draft_service.export_submission_bundle(
            user_id=current_user.id,
            draft_id=id,
            user_email=current_user.email,
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DRAFT_NOT_FOUND",
                "message": f"Bản thảo {id} không tồn tại hoặc bạn không có quyền truy cập.",
            },
        )
    except DraftRoleForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE_RESTRICTED",
                "message": str(exc),
                "action": "Viewer and commenter roles cannot download raw submission bundle.",
            },
        ) from exc

    return StreamingResponse(
        io.BytesIO(zip_bytes),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="draft_{id.hex[:8]}_bundle.zip"',
            "Content-Length": str(len(zip_bytes)),
        },
    )


ASSIST_DRAFT_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Trợ lý viết học thuật sinh gợi ý sửa đổi hoặc mở rộng bản thảo dựa trên prompt
và bộ đệm ngữ cảnh (<pre_context>, <target_selection>, <post_context>).
Phục vụ Suggestion Review Panel để người dùng xem trước diff trước khi chấp nhận."""


@router.post(
    "/{id}/assist",
    response_model=SingleResponseEnvelope[DraftAssistResponse],
    summary="Trợ lý viết học thuật sinh gợi ý sửa đổi (AI Writing Assist)",
    description=ASSIST_DRAFT_DESCRIPTION,
    responses={
        200: {"description": "Gợi ý đoạn văn đề xuất thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        403: {
            "model": ErrorResponse,
            "description": "Vai trò không có quyền sử dụng AI trợ lý viết.",
        },
        404: {"model": ErrorResponse, "description": "Bản thảo không tồn tại."},
    },
)
async def assist_draft(
    id: UUID,
    request: DraftAssistRequest,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> SingleResponseEnvelope[DraftAssistResponse]:
    from datetime import UTC, datetime

    effective_prompt = request.prompt or request.instruction or f"Execute {request.action}"
    try:
        orig, suggested, explanation, confidence, citations = await draft_service.assist_draft(
            user_id=current_user.id,
            draft_id=id,
            prompt=request.prompt,
            instruction=request.instruction,
            action=request.action,
            pre_context=request.pre_context,
            target_selection=request.target_selection,
            post_context=request.post_context,
            section_title=request.section_title,
            cursor_position=request.cursor_position,
            temperature=request.temperature,
            user_email=current_user.email,
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DRAFT_NOT_FOUND",
                "message": f"Bản thảo {id} không tồn tại hoặc bạn không có quyền truy cập.",
            },
        )
    except DraftRoleForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE_RESTRICTED",
                "message": str(exc),
                "action": "Viewer and commenter roles cannot run AI writing assist.",
            },
        ) from exc

    response_data = DraftAssistResponse(
        draft_id=id,
        action=request.action,
        prompt=effective_prompt,
        original_text=orig if orig else None,
        suggested_text=suggested,
        generated_text=suggested,
        explanation=explanation,
        confidence_score=confidence,
        suggested_citations=citations,
        suggested_at=datetime.now(UTC),
    )
    return SingleResponseEnvelope(data=response_data)


@router.post(
    "/{id}/chat:stream",
    summary="Tương tác AI Co-Author phát luồng SSE không đệm (Chat Stream)",
    description="Phát luồng Server-Sent Events (SSE) theo chuẩn ReAct Agentic Overleaf CLSI.",
    responses={
        200: {
            "content": {"text/event-stream": {}},
            "description": "Luồng SSE unbuffered thời gian thực.",
        },
        400: {"model": ErrorResponse, "description": "Prompt rỗng hoặc không hợp lệ."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        403: {"model": ErrorResponse, "description": "Không có quyền gọi AI trợ lý."},
        404: {"model": ErrorResponse, "description": "Bản thảo không tồn tại."},
        412: {"model": ErrorResponse, "description": "Xung đột phiên bản (OCC)."},
    },
)
@router.post(
    "/{id}/chat/stream",
    include_in_schema=False,
)
async def chat_stream(
    id: UUID,
    request: DraftChatStreamRequest,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> StreamingResponse:
    effective_prompt = (request.prompt or request.message or "").strip()
    if not effective_prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "EMPTY_PROMPT_CONTENT",
                "message": "Yêu cầu gửi tới trợ lý AI không được để trống.",
                "action": "Provide a non-empty prompt for the coauthor agent.",
            },
        )

    # Check existence & permissions first before starting stream
    draft, role = await draft_service.get_user_draft_role(
        draft_id=id,
        user_id=current_user.id,
        user_email=current_user.email,
    )
    if not draft or not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DRAFT_NOT_FOUND",
                "message": f"Bản thảo {id} không tồn tại hoặc bạn không có quyền truy cập.",
            },
        )
    if not can_call_costly_ai(role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE_RESTRICTED",
                "message": (
                    f"Role '{role.value}' is strictly forbidden from invoking costly AI assistant"
                ),
            },
        )
    if request.version is not None and draft.version != request.version:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail={
                "code": "CONCURRENCY_CONFLICT",
                "message": (
                    f"Resource version conflict: expected {request.version}, "
                    f"current {draft.version}"
                ),
            },
        )

    async def sse_generator() -> AsyncIterator[str]:
        try:
            async for ev in draft_service.stream_chat_assist(
                user_id=current_user.id,
                draft_id=id,
                message=effective_prompt,
                current_content=request.current_content,
                current_bib_content=request.current_bib_content,
                version=request.version,
                user_email=current_user.email,
            ):
                ev_name = ev.get("event") or ev.get("type", "message")
                ev_data = ev.get("data", {})
                yield f"event: {ev_name}\ndata: {json.dumps(ev_data, ensure_ascii=False)}\n\n"
        except Exception as exc:
            err_data = {"error": str(exc)}
            yield f"event: error\ndata: {json.dumps(err_data, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ==============================================================================
# Assets Endpoints (/drafts/{id}/assets)
# ==============================================================================


@router.post(
    "/{id}/assets",
    response_model=SingleResponseEnvelope[DraftAssetResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký hoặc tải lên tệp đính kèm học thuật cho bản thảo (Assets)",
    responses={
        201: {"description": "Đăng ký tệp đính kèm thành công."},
        400: {"model": ErrorResponse, "description": "Tệp tin vi phạm bảo mật hoặc định dạng."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        403: {"model": ErrorResponse, "description": "Vai trò không có quyền tải lên tài sản."},
        404: {"model": ErrorResponse, "description": "Bản thảo không tồn tại."},
    },
)
async def create_draft_asset(
    id: UUID,
    request: CreateDraftAssetRequest,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> SingleResponseEnvelope[DraftAssetResponse]:
    try:
        asset = await draft_service.create_asset(
            user_id=current_user.id,
            draft_id=id,
            request=request,
            user_email=current_user.email,
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DRAFT_NOT_FOUND",
                "message": f"Bản thảo {id} không tồn tại hoặc bạn không có quyền truy cập.",
            },
        )
    except DraftRoleForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE_RESTRICTED",
                "message": str(exc),
                "action": "Only editors and owners can upload assets.",
            },
        ) from exc
    except (ZipSlipSecurityError, MaliciousAssetContentError, AssetQuotaExceededError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "ASSET_SECURITY_VIOLATION",
                "message": str(exc),
                "action": (
                    "Ensure asset is valid, free of path traversal or dangerous macros, "
                    "and within size limits."
                ),
            },
        ) from exc

    return SingleResponseEnvelope(data=asset)


@router.get(
    "/{id}/assets",
    response_model=SingleResponseEnvelope[DraftAssetListResponse],
    summary="Lấy danh sách tệp đính kèm học thuật của bản thảo",
    responses={
        200: {"description": "Truy xuất danh sách tệp đính kèm thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        404: {"model": ErrorResponse, "description": "Bản thảo không tồn tại."},
    },
)
async def list_draft_assets(
    id: UUID,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> SingleResponseEnvelope[DraftAssetListResponse]:
    try:
        assets = await draft_service.list_assets(
            user_id=current_user.id,
            draft_id=id,
            user_email=current_user.email,
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DRAFT_NOT_FOUND",
                "message": f"Bản thảo {id} không tồn tại hoặc bạn không có quyền truy cập.",
            },
        )
    return SingleResponseEnvelope(
        data=DraftAssetListResponse(
            draft_id=id,
            items=assets,
            total=len(assets),
        )
    )
