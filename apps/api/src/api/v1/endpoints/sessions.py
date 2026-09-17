"""API Endpoints for Research Sessions (Module 1: Dual-Pane Research Workspace)."""

import io
from uuid import UUID

import structlog
from api.db.models.user import UserModel
from api.deps import (
    get_current_user,
    get_idempotency_port,
    get_session_chat_service,
    get_session_service,
)
from api.schemas.envelope import PaginationLinks, PaginationMeta, ResponseMeta
from api.schemas.error import ErrorResponse
from api.schemas.session import (
    SessionAddDocumentRequest,
    SessionChatMessageRequest,
    SessionCreateRequest,
    SessionHistoryEnvelope,
    SessionSingleEnvelope,
    SessionTurnListEnvelope,
    SessionUpdateMetadataRequest,
    SessionUpdateViewportRequest,
)
from api.services.session_chat_service import SessionChatService
from api.services.session_service import SessionService
from core.ports.idempotency import IIdempotencyPort
from fastapi import (
    APIRouter,
    Depends,
    File,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse, StreamingResponse

logger = structlog.get_logger("api.endpoints.sessions")

router = APIRouter(prefix="/sessions", tags=["sessions"])


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
# 45. POST /api/v1/sessions (Khởi tạo phiên nghiên cứu mới)
# ==============================================================================
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=SessionSingleEnvelope,
    summary="Khởi tạo phiên nghiên cứu đa bài mới (Research Session)",
    responses={
        201: {"description": "Phiên nghiên cứu đã được khởi tạo thành công."},
        200: {"description": "Phiên nghiên cứu đã được tạo trước đó (Idempotent Cache Hit)."},
        400: {"model": ErrorResponse, "description": "Vượt quá dung lượng 5 bài báo."},
        404: {"model": ErrorResponse, "description": "Tài liệu không tồn tại."},
        422: {"model": ErrorResponse, "description": "Dữ liệu không hợp lệ."},
    },
)
async def create_session(
    payload: SessionCreateRequest,
    response: Response,
    include_documents: bool = Query(
        False, description="Nhúng danh sách metadata chi tiết của các bài báo"
    ),
    idempotency_key: str | None = Header(
        None,
        alias="Idempotency-Key",
        description="Khóa định danh chống trùng lặp request (24h)",
    ),
    current_user: UserModel = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
    idempotency: IIdempotencyPort = Depends(get_idempotency_port),
) -> SessionSingleEnvelope | JSONResponse:
    """Create a new multi-paper research session with idempotency and auto-naming support."""
    if idempotency_key:
        cache_key = f"idempotency:session_create:{current_user.id}:{idempotency_key}"
        cached_resp = await idempotency.get_response(cache_key)
        if cached_resp:
            session_id = cached_resp.get("data", {}).get("id")
            version = cached_resp.get("data", {}).get("version", 1)
            response.headers["X-Cache"] = "Idempotent-Hit"
            response.headers["Location"] = f"/api/v1/sessions/{session_id}"
            response.headers["ETag"] = f'"v{version}"'
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=cached_resp,
                headers=dict(response.headers),
            )

    data = await session_service.create_session(
        user_id=current_user.id,
        title=payload.title,
        initial_document_ids=payload.initial_document_ids,
        include_documents=include_documents,
    )

    response.headers["Location"] = f"/api/v1/sessions/{data.id}"
    response.headers["ETag"] = f'"v{data.version}"'

    envelope = SessionSingleEnvelope(data=data, meta=ResponseMeta())

    if idempotency_key:
        cache_key = f"idempotency:session_create:{current_user.id}:{idempotency_key}"
        await idempotency.store_response(
            key=cache_key,
            response_data=envelope.model_dump(mode="json"),
            status_code=status.HTTP_201_CREATED,
        )

    return envelope


# ==============================================================================
# 46. GET /api/v1/sessions (Lấy lịch sử các phiên nghiên cứu - Sidebar History)
# ==============================================================================
@router.get(
    "",
    response_model=SessionHistoryEnvelope,
    summary="Lấy lịch sử các phiên nghiên cứu (Sidebar History)",
    responses={
        200: {"description": "Danh sách lịch sử các phiên nghiên cứu phân trang thành công."}
    },
)
async def list_sessions(
    page: int = Query(1, ge=1, description="Chỉ số trang (1-indexed)"),
    per_page: int = Query(20, ge=1, le=100, description="Số lượng mục trên mỗi trang"),
    include_archived: bool = Query(
        False, description="Bao gồm cả các phiên đã lưu trữ quá hạn TTL"
    ),
    q: str | None = Query(None, description="Từ khóa tìm kiếm theo tiêu đề phiên"),
    current_user: UserModel = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
) -> SessionHistoryEnvelope:
    """List research sessions for current user sidebar history."""
    items, total = await session_service.list_sessions(
        user_id=current_user.id,
        page=page,
        per_page=per_page,
        include_archived=include_archived,
        query=q,
    )
    total_pages = (total + per_page - 1) // per_page if total > 0 else 0

    base_url = f"/api/v1/sessions?page={page}&per_page={per_page}"
    meta = PaginationMeta(
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )
    links = PaginationLinks(
        first=f"/api/v1/sessions?page=1&per_page={per_page}",
        prev=f"/api/v1/sessions?page={page - 1}&per_page={per_page}" if page > 1 else None,
        self=base_url,
        next=f"/api/v1/sessions?page={page + 1}&per_page={per_page}"
        if page < total_pages
        else None,
        last=f"/api/v1/sessions?page={total_pages}&per_page={per_page}"
        if total_pages > 0
        else None,
    )
    return SessionHistoryEnvelope(data=items, meta=meta, links=links)


# ==============================================================================
# 47. GET /api/v1/sessions/{id} (Khôi phục nguyên vẹn phiên)
# ==============================================================================
@router.get(
    "/{id}",
    response_model=SessionSingleEnvelope,
    summary="Khôi phục nguyên vẹn phiên (Snapshots, Tabs, Viewport)",
    responses={
        200: {
            "description": "Chi tiết toàn vẹn phiên nghiên cứu.",
            "headers": {
                "ETag": {
                    "description": "Khóa OCC version hiện tại (ví dụ: '\"v14\"')",
                    "schema": {"type": "string"},
                }
            },
        },
        404: {"model": ErrorResponse, "description": "Phiên không tồn tại."},
    },
)
async def get_session(
    id: UUID,
    response: Response,
    current_user: UserModel = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
) -> SessionSingleEnvelope:
    """Restore complete state of a research session (Snapshot, Tabs, Viewport)."""
    data = await session_service.get_session_detail(session_id=id, user_id=current_user.id)
    response.headers["ETag"] = f'"v{data.version}"'
    return SessionSingleEnvelope(data=data, meta=ResponseMeta())


# ==============================================================================
# 48. PATCH /api/v1/sessions/{id} (Cập nhật tiêu đề / metadata phiên nghiên cứu)
# ==============================================================================
@router.patch(
    "/{id}",
    response_model=SessionSingleEnvelope,
    summary="Cập nhật tiêu đề / metadata phiên nghiên cứu (OCC If-Match)",
    responses={
        200: {
            "description": "Cập nhật tiêu đề thành công.",
            "headers": {
                "ETag": {
                    "description": "Khóa OCC version mới sau cập nhật (ví dụ: '\"v15\"')",
                    "schema": {"type": "string"},
                }
            },
        },
        412: {
            "model": ErrorResponse,
            "description": "Xung đột phiên bản đồng thời (CONCURRENCY_CONFLICT).",
        },
        404: {"model": ErrorResponse, "description": "Phiên không tồn tại."},
        428: {"model": ErrorResponse, "description": "Thiếu header If-Match."},
    },
)
async def update_session_metadata(
    id: UUID,
    payload: SessionUpdateMetadataRequest,
    response: Response,
    if_match: str | None = Header(
        None,
        alias="If-Match",
        description="Phiên bản ETag hiện tại bắt buộc (ví dụ: '\"v1\"')",
    ),
    current_user: UserModel = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
) -> SessionSingleEnvelope:
    """Update research session title using Optimistic Concurrency Control."""
    expected_version = parse_version_from_etag(if_match)
    data = await session_service.update_metadata_occ(
        session_id=id,
        user_id=current_user.id,
        title=payload.title,
        expected_version=expected_version,
    )
    response.headers["ETag"] = f'"v{data.version}"'
    return SessionSingleEnvelope(data=data, meta=ResponseMeta())


# ==============================================================================
# 49. PATCH /api/v1/sessions/{id}/viewport (Tự động lưu vị trí cuộn trang & Tab)
# ==============================================================================
@router.patch(
    "/{id}/viewport",
    response_model=SessionSingleEnvelope,
    summary="Tự động lưu vị trí cuộn trang PDF và Tab đang mở (OCC)",
    responses={
        200: {
            "description": "Lưu trạng thái viewport thành công.",
            "headers": {
                "ETag": {
                    "description": "Khóa OCC version mới sau cập nhật",
                    "schema": {"type": "string"},
                }
            },
        },
        412: {"model": ErrorResponse, "description": "Xung đột phiên bản đồng thời."},
        404: {"model": ErrorResponse, "description": "Phiên không tồn tại."},
    },
)
async def update_session_viewport(
    id: UUID,
    payload: SessionUpdateViewportRequest,
    response: Response,
    if_match: str | None = Header(
        None,
        alias="If-Match",
        description="Phiên bản ETag hiện tại bắt buộc (ví dụ: '\"v1\"')",
    ),
    current_user: UserModel = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
) -> SessionSingleEnvelope:
    """Save viewport state, zoom ratio, scroll offset, and active tab with OCC."""
    expected_version = parse_version_from_etag(if_match)
    data = await session_service.update_viewport_occ(
        session_id=id,
        user_id=current_user.id,
        viewport_state=payload.viewport_state.model_dump(),
        active_tab=payload.active_tab,
        active_document_id=payload.active_document_id,
        expected_version=expected_version,
    )
    response.headers["ETag"] = f'"v{data.version}"'
    return SessionSingleEnvelope(data=data, meta=ResponseMeta())


# ==============================================================================
# 50. DELETE /api/v1/sessions/{id} (Xóa phiên nghiên cứu)
# ==============================================================================
@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa phiên nghiên cứu",
    responses={
        204: {"description": "Xóa phiên thành công (No Content)."},
        404: {"model": ErrorResponse, "description": "Phiên không tồn tại."},
    },
)
async def delete_session(
    id: UUID,
    current_user: UserModel = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
) -> Response:
    """Delete a research session and cascade cleanup its associations."""
    await session_service.delete_session(session_id=id, user_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ==============================================================================
# 51. POST /api/v1/sessions/{id}/documents (Nạp bài vào phiên - Pure JSON)
# ==============================================================================
@router.post(
    "/{id}/documents",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Nạp bài vào phiên (Pure JSON: url hoặc document_id)",
    responses={
        202: {"description": "Yêu cầu nạp bài đã được chấp nhận và lên lịch."},
        422: {"model": ErrorResponse, "description": "Vượt quá ngưỡng trần 5 bài báo."},
        409: {"model": ErrorResponse, "description": "Tài liệu đã tồn tại trong phiên."},
        404: {"model": ErrorResponse, "description": "Phiên hoặc bài báo không tồn tại."},
    },
)
async def add_document_to_session(
    id: UUID,
    payload: SessionAddDocumentRequest,
    current_user: UserModel = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
) -> JSONResponse:
    """Add a document into an active session with capacity cap of 5 papers."""
    result = await session_service.add_document_to_session(
        session_id=id,
        user_id=current_user.id,
        source_type=payload.source_type,
        document_id=payload.document_id,
        url=payload.url,
        title=payload.title,
    )
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "success": True,
            "data": result,
            "meta": ResponseMeta().model_dump(mode="json"),
        },
    )


# ==============================================================================
# 52. POST /api/v1/sessions/{id}/messages (Hỏi đáp đa bài báo & Stream SSE)
# ==============================================================================
@router.post(
    "/{id}/messages",
    summary="Gửi câu hỏi & Stream SSE (Cross-Document Namespacing)",
    responses={
        200: {
            "description": "Dòng sự kiện SSE chứa câu trả lời và trích dẫn bounding box.",
            "content": {"text/event-stream": {}},
        },
        404: {"model": ErrorResponse, "description": "Phiên không tồn tại."},
        403: {"model": ErrorResponse, "description": "Phiên đã bị lưu trữ."},
    },
)
async def post_session_message(
    id: UUID,
    payload: SessionChatMessageRequest,
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    chat_service: SessionChatService = Depends(get_session_chat_service),
) -> StreamingResponse:
    """Stream chat Q&A using Cross-Document Context Namespacing and Disconnect Guard."""
    generator = chat_service.stream_chat(
        session_id=id,
        user_id=current_user.id,
        request=payload,
        is_disconnected=request.is_disconnected,
    )
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ==============================================================================
# 53. GET /api/v1/sessions/{id}/messages (Lịch sử hội thoại của phiên)
# ==============================================================================
@router.get(
    "/{id}/messages",
    response_model=SessionTurnListEnvelope,
    summary="Lấy lịch sử hội thoại của phiên (phân trang)",
    responses={200: {"description": "Lịch sử hội thoại theo trình tự thời gian."}},
)
async def get_session_messages(
    id: UUID,
    page: int = Query(1, ge=1, description="Chỉ số trang (1-indexed)"),
    per_page: int = Query(50, ge=1, le=100, description="Số lượng lượt trên mỗi trang"),
    current_user: UserModel = Depends(get_current_user),
    chat_service: SessionChatService = Depends(get_session_chat_service),
) -> SessionTurnListEnvelope:
    """List conversation messages and citations in chronological order."""
    items, total = await chat_service.get_messages(
        session_id=id,
        user_id=current_user.id,
        page=page,
        per_page=per_page,
    )
    total_pages = (total + per_page - 1) // per_page if total > 0 else 0
    base_url = f"/api/v1/sessions/{id}/messages?page={page}&per_page={per_page}"
    meta = PaginationMeta(
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )
    links = PaginationLinks(
        first=f"/api/v1/sessions/{id}/messages?page=1&per_page={per_page}",
        prev=f"/api/v1/sessions/{id}/messages?page={page - 1}&per_page={per_page}"
        if page > 1
        else None,
        self=base_url,
        next=f"/api/v1/sessions/{id}/messages?page={page + 1}&per_page={per_page}"
        if page < total_pages
        else None,
        last=f"/api/v1/sessions/{id}/messages?page={total_pages}&per_page={per_page}"
        if total_pages > 0
        else None,
    )
    return SessionTurnListEnvelope(data=items, meta=meta, links=links)


# ==============================================================================
# 54. DELETE /api/v1/sessions/{id}/messages (Xóa toàn bộ tin nhắn - Idempotent)
# ==============================================================================
@router.delete(
    "/{id}/messages",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa toàn bộ lịch sử hội thoại của phiên (Idempotent 204)",
    responses={204: {"description": "Đã xóa sạch lịch sử tin nhắn."}},
)
async def delete_session_messages(
    id: UUID,
    current_user: UserModel = Depends(get_current_user),
    chat_service: SessionChatService = Depends(get_session_chat_service),
) -> Response:
    """Clear all conversation history in the session (Idempotent 204)."""
    await chat_service.clear_messages(session_id=id, user_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ==============================================================================
# 55. POST /api/v1/sessions/{id}:restore-archived (Khôi phục phiên quá hạn TTL)
# ==============================================================================
@router.post(
    "/{id}:restore-archived",
    response_model=SessionSingleEnvelope,
    summary="Tải lại file PDF gốc để kích hoạt lại phiên quá hạn TTL",
    responses={
        200: {"description": "Kích hoạt lại phiên nghiên cứu thành công."},
        400: {"model": ErrorResponse, "description": "Tệp PDF không hợp lệ."},
        404: {"model": ErrorResponse, "description": "Phiên không tồn tại."},
    },
)
async def restore_archived_session(
    id: UUID,
    response: Response,
    file: UploadFile = File(..., description="Tệp PDF gốc để tái kích hoạt phiên"),
    current_user: UserModel = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
) -> SessionSingleEnvelope:
    """Reactivate an archived session by uploading original document binary."""
    data = await session_service.restore_archived_session(
        session_id=id,
        user_id=current_user.id,
        file=file,
    )
    response.headers["ETag"] = f'"v{data.version}"'
    return SessionSingleEnvelope(data=data, meta=ResponseMeta())


# ==============================================================================
# 56. POST /api/v1/sessions/{id}:export-bundle (Full Offline Research Bundle .zip)
# ==============================================================================
@router.post(
    "/{id}:export-bundle",
    summary="Xuất Gói Nghiên Cứu Ngoại Tuyến Trọn Gói (Full Offline Research Bundle .zip)",
    responses={
        200: {
            "content": {"application/zip": {}},
            "description": (
                "Gói nén ZIP chứa tài liệu PDF, master_lesson.md và chat_transcript.html."
            ),
        },
        404: {"model": ErrorResponse, "description": "Phiên nghiên cứu không tồn tại."},
    },
)
async def export_session_bundle(
    id: UUID,
    current_user: UserModel = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
) -> StreamingResponse:
    """Generate and download a self-contained offline research bundle ZIP."""
    zip_bytes = await session_service.export_bundle(session_id=id, user_id=current_user.id)
    return StreamingResponse(
        io.BytesIO(zip_bytes),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="verischolar_session_{id}.zip"',
            "Content-Length": str(len(zip_bytes)),
        },
    )
