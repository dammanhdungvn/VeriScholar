"""API Endpoints for Smart Research Notes & Knowledge Digest (Module 1)."""

import math
from uuid import UUID

import structlog
from api.db.models.user import UserModel
from api.deps import (
    get_current_user,
    get_idempotency_port,
    get_note_service,
    get_note_synthesis_service,
)
from api.schemas.envelope import (
    PaginatedResponseEnvelope,
    PaginationLinks,
    PaginationMeta,
    ResponseMeta,
    SingleResponseEnvelope,
)
from api.schemas.error import ErrorResponse
from api.schemas.note import (
    CreateNoteRequest,
    NoteListItemResponse,
    NoteResponse,
    NoteSynthesisResponse,
    SynthesizeNotesRequest,
    UpdateNoteRequest,
)
from api.services.note_service import NoteService
from api.services.note_synthesis_service import NoteSynthesisService
from core.domain.exceptions import (
    ConcurrencyConflictError,
    EntityNotFoundError,
    InvalidNoteDataError,
    NoteNotFoundError,
    NoteSynthesisError,
    PreconditionRequiredError,
)
from core.ports.idempotency import IIdempotencyPort
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
from fastapi.responses import JSONResponse
from fastapi.responses import Response as RawResponse

logger = structlog.get_logger("api.endpoints.notes")

router = APIRouter(prefix="/notes", tags=["notes"])


def parse_version_from_etag(etag: str | None) -> int:
    """Parse integer version from If-Match HTTP ETag header (RFC 9110 / RFC 7232)."""
    if not etag:
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail={
                "code": "PRECONDITION_REQUIRED",
                "message": (
                    "Header 'If-Match' (ETag phiên bản, ví dụ '\"v1\"') là bắt buộc theo RFC 7232."
                ),
                "action": 'Include If-Match: "v{version}" header in request.',
            },
        )
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


# ==============================================================================
# 16. POST /api/v1/notes (Lưu trích dẫn & ghi chú cá nhân)
# ==============================================================================
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleResponseEnvelope[NoteResponse],
    summary="Lưu trích dẫn & ghi chú cá nhân (Add to Note)",
    responses={
        201: {
            "description": "Ghi chú đã được lưu thành công kèm Frozen Evidence Snapshot.",
            "headers": {
                "Location": {
                    "description": "Đường dẫn URI đến ghi chú vừa tạo.",
                    "schema": {"type": "string"},
                },
                "ETag": {
                    "description": "Khóa OCC version khởi tạo ('\"v1\"').",
                    "schema": {"type": "string"},
                },
            },
        },
        400: {"model": ErrorResponse, "description": "Dữ liệu ghi chú không hợp lệ."},
        404: {"model": ErrorResponse, "description": "Tài liệu đính kèm không tồn tại."},
    },
)
async def create_note(
    payload: CreateNoteRequest,
    response: Response,
    current_user: UserModel = Depends(get_current_user),
    note_service: NoteService = Depends(get_note_service),
) -> SingleResponseEnvelope[NoteResponse]:
    """Save academic quote with bounding boxes, personal memo and frozen evidence snapshot."""
    try:
        note_data = await note_service.create_note(user_id=current_user.id, req=payload)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DOCUMENT_NOT_FOUND",
                "message": str(e),
                "action": "Check document_id and try again.",
            },
        )
    except InvalidNoteDataError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_NOTE_DATA",
                "message": str(e),
                "action": "Provide valid non-empty selected text and positive page number.",
            },
        )

    response.headers["Location"] = f"/api/v1/notes/{note_data.id}"
    response.headers["ETag"] = f'"v{note_data.version}"'
    return SingleResponseEnvelope(data=note_data, meta=ResponseMeta())


# ==============================================================================
# 17. GET /api/v1/notes (Danh sách ghi chú có bộ lọc và phân trang)
# ==============================================================================
@router.get(
    "",
    response_model=PaginatedResponseEnvelope[NoteListItemResponse],
    summary="Danh sách ghi chú (lọc theo document_id, tag, folder_id)",
    responses={
        200: {"description": "Danh sách ghi chú kèm phân trang RFC 8288."},
    },
)
async def list_notes(
    request: Request,
    document_id: UUID | None = Query(None, description="Lọc theo ID tài liệu"),
    tag: str | None = Query(None, description="Lọc theo thẻ học thuật"),
    folder_id: UUID | None = Query(None, description="Lọc theo ID thư mục chứa tài liệu"),
    page: int = Query(1, ge=1, description="Số trang (1-indexed)"),
    per_page: int = Query(50, ge=1, le=100, description="Số mục trên mỗi trang"),
    current_user: UserModel = Depends(get_current_user),
    note_service: NoteService = Depends(get_note_service),
) -> PaginatedResponseEnvelope[NoteListItemResponse]:
    """Retrieve user research notes collection filtered by document, tag, or folder."""
    items, total = await note_service.list_notes(
        user_id=current_user.id,
        document_id=document_id,
        tag=tag,
        folder_id=folder_id,
        page=page,
        per_page=per_page,
    )

    total_pages = max(1, math.ceil(total / per_page)) if total > 0 else 1
    base_url = str(request.url.remove_query_params(["page", "per_page"]))
    sep = "&" if "?" in base_url else "?"

    links = PaginationLinks(
        first=f"{base_url}{sep}page=1&per_page={per_page}",
        prev=(f"{base_url}{sep}page={page - 1}&per_page={per_page}" if page > 1 else None),
        self=f"{base_url}{sep}page={page}&per_page={per_page}",
        next=(
            f"{base_url}{sep}page={page + 1}&per_page={per_page}" if page < total_pages else None
        ),
        last=f"{base_url}{sep}page={total_pages}&per_page={per_page}",
    )

    meta = PaginationMeta(
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )

    return PaginatedResponseEnvelope(data=items, meta=meta, links=links)


# ==============================================================================
# 18. GET /api/v1/notes/{id} (Chi tiết ghi chú kèm Frozen Evidence Snapshot)
# ==============================================================================
@router.get(
    "/{id}",
    response_model=SingleResponseEnvelope[NoteResponse],
    summary="Chi tiết ghi chú kèm Frozen Evidence Snapshot",
    responses={
        200: {
            "description": "Chi tiết toàn vẹn của ghi chú kèm Frozen Evidence Snapshot.",
            "headers": {
                "ETag": {
                    "description": "Khóa OCC version hiện tại (ví dụ: '\"v1\"')",
                    "schema": {"type": "string"},
                }
            },
        },
        404: {"model": ErrorResponse, "description": "Ghi chú không tồn tại."},
    },
)
async def get_note(
    id: UUID,
    response: Response,
    current_user: UserModel = Depends(get_current_user),
    note_service: NoteService = Depends(get_note_service),
) -> SingleResponseEnvelope[NoteResponse]:
    """Retrieve full details of a note including immutable evidence snapshot."""
    try:
        data = await note_service.get_note_by_id(note_id=id, user_id=current_user.id)
    except NoteNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOTE_NOT_FOUND",
                "message": str(e),
                "action": "Verify note ID.",
            },
        )

    response.headers["ETag"] = f'"v{data.version}"'
    return SingleResponseEnvelope(data=data, meta=ResponseMeta())


# ==============================================================================
# 19. PATCH /api/v1/notes/{id} (Sửa ghi chú / tag có kiểm soát OCC If-Match)
# ==============================================================================
@router.patch(
    "/{id}",
    response_model=SingleResponseEnvelope[NoteResponse],
    summary="Sửa ghi chú / tag (Kiểm soát đồng thời OCC If-Match)",
    responses={
        200: {
            "description": "Cập nhật ghi chú thành công.",
            "headers": {
                "ETag": {
                    "description": "Khóa OCC version mới sau cập nhật (ví dụ: '\"v2\"')",
                    "schema": {"type": "string"},
                }
            },
        },
        400: {"model": ErrorResponse, "description": "Dữ liệu không hợp lệ."},
        404: {"model": ErrorResponse, "description": "Ghi chú không tồn tại."},
        412: {
            "model": ErrorResponse,
            "description": "Xung đột phiên bản đồng thời (CONCURRENCY_CONFLICT).",
        },
        428: {
            "model": ErrorResponse,
            "description": "Thiếu header If-Match bắt buộc.",
        },
    },
)
async def update_note(
    id: UUID,
    payload: UpdateNoteRequest,
    response: Response,
    if_match: str | None = Header(
        None,
        alias="If-Match",
        description="Phiên bản ETag hiện tại bắt buộc (ví dụ: '\"v1\"')",
    ),
    current_user: UserModel = Depends(get_current_user),
    note_service: NoteService = Depends(get_note_service),
) -> SingleResponseEnvelope[NoteResponse]:
    """Update personal memo or tags using Optimistic Concurrency Control."""
    try:
        data = await note_service.update_note(
            note_id=id,
            user_id=current_user.id,
            req=payload,
            if_match_header=if_match,
        )
    except PreconditionRequiredError as e:
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail={
                "code": "PRECONDITION_REQUIRED",
                "message": str(e),
                "action": 'Include If-Match: "v{version}" header.',
            },
        )
    except ConcurrencyConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail={
                "code": "CONCURRENCY_CONFLICT",
                "message": str(e),
                "action": "Fetch latest note state and retry with updated ETag.",
            },
        )
    except NoteNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOTE_NOT_FOUND",
                "message": str(e),
                "action": "Verify note ID.",
            },
        )

    response.headers["ETag"] = f'"v{data.version}"'
    return SingleResponseEnvelope(data=data, meta=ResponseMeta())


# ==============================================================================
# 20. DELETE /api/v1/notes/{id} (Xóa ghi chú khỏi sổ tay)
# ==============================================================================
@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa ghi chú khỏi sổ tay",
    responses={
        204: {"description": "Ghi chú đã được xóa thành công khỏi sổ tay (Idempotent)."},
    },
)
async def delete_note(
    id: UUID,
    current_user: UserModel = Depends(get_current_user),
    note_service: NoteService = Depends(get_note_service),
) -> RawResponse:
    """Delete note idempotently without altering the source academic document."""
    await note_service.delete_note(note_id=id, user_id=current_user.id)
    return RawResponse(status_code=status.HTTP_204_NO_CONTENT)


# ==============================================================================
# 21. POST /api/v1/notes:synthesize (AI Tổng hợp ghi chú thành bài học)
# ==============================================================================
@router.post(
    ":synthesize",
    response_model=SingleResponseEnvelope[NoteSynthesisResponse],
    summary="AI Tổng hợp ghi chú thành bài học (3 modes + Badges)",
    responses={
        200: {
            "description": "Tổng hợp tri thức thành công với interactive citation badges.",
        },
        400: {"model": ErrorResponse, "description": "Dữ liệu yêu cầu không hợp lệ."},
    },
)
async def synthesize_notes(
    payload: SynthesizeNotesRequest,
    response: Response,
    idempotency_key: str | None = Header(
        None,
        alias="Idempotency-Key",
        description="Khóa lũy đẳng tùy chọn",
    ),
    current_user: UserModel = Depends(get_current_user),
    synthesis_service: NoteSynthesisService = Depends(get_note_synthesis_service),
    idempotency_port: IIdempotencyPort = Depends(get_idempotency_port),
) -> SingleResponseEnvelope[NoteSynthesisResponse] | JSONResponse:
    """Synthesize research notes into structured concept lesson, review, or gap analysis."""
    # Check idempotency cache if key provided
    if idempotency_key:
        cache_key = f"idempotency:note_synthesize:{current_user.id}:{idempotency_key}"
        cached_resp = await idempotency_port.get_response(cache_key)
        if cached_resp:
            response.headers["X-Cache"] = "Idempotent-Hit"
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=cached_resp,
                headers=dict(response.headers),
            )

    try:
        data = await synthesis_service.synthesize_notes(
            user_id=current_user.id,
            req=payload,
        )
    except NoteSynthesisError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "SYNTHESIS_FAILED",
                "message": str(e),
                "action": "Ensure note_ids belong to current user and contain valid content.",
            },
        )

    envelope = SingleResponseEnvelope(data=data, meta=ResponseMeta())

    if idempotency_key:
        cache_key = f"idempotency:note_synthesize:{current_user.id}:{idempotency_key}"
        await idempotency_port.store_response(
            key=cache_key,
            response_data=envelope.model_dump(mode="json"),
            status_code=200,
            ttl_seconds=86400,
        )

    return envelope
