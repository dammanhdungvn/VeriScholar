"""API Endpoints for Academic Research Writing & Drafts (Module 2)."""

import io
import math
from uuid import UUID, uuid4

import structlog
from api.db.models.user import UserModel
from api.deps import (
    get_associative_memory_service,
    get_current_user,
    get_draft_service,
)
from api.schemas.draft import (
    AtomicClaimResponse,
    CompileDraftResponse,
    CreateDraftAssetRequest,
    CreateDraftCommentRequest,
    CreateDraftRequest,
    DraftAssetListResponse,
    DraftAssetResponse,
    DraftAssistRequest,
    DraftAssistResponse,
    DraftCommentListResponse,
    DraftCommentResponse,
    DraftResponse,
    DraftShareRequest,
    DraftShareResponse,
    LatexSyntaxErrorResponse,
    OverleafExportResponse,
    UpdateDraftCommentRequest,
    UpdateDraftRequest,
    VerifyFactsRequest,
    VerifyFactsResponse,
)
from api.schemas.envelope import (
    PaginatedResponseEnvelope,
    PaginationLinks,
    PaginationMeta,
    SingleResponseEnvelope,
)
from api.schemas.error import ErrorResponse
from api.services.associative_memory_service import (
    AssociativeMemoryService,
    AssociativeSuggestionsRequest,
    AssociativeSuggestionsResponse,
)
from api.services.draft_service import DraftService
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
    draft = await draft_service.create_draft(user_id=current_user.id, request=request)
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


VERIFY_FACTS_DESCRIPTION = """🎯 **Mục đích & Ngữ cảnh sử dụng:**
Kích hoạt quy trình kiểm chứng sự thật 4 bước SAFE (Search-Augmented Factuality Evaluator)
cho toàn bộ bản thảo hoặc một đoạn trích dẫn được chọn đối chiếu với kho tài liệu khoa học.

📥 **Tham số đầu vào:**
- `id` (UUID, Path, Bắt buộc): UUID của bản thảo cần kiểm chứng.
- Request Body (application/json, Tùy chọn):
  - `text` (string, Tùy chọn): Đoạn văn bản cần kiểm chứng. Mặc định kiểm chứng toàn văn.
  - `document_ids` (list[UUID], Tùy chọn): Giới hạn phạm vi đối chiếu trong các tài liệu chỉ định.

📤 **Đầu ra & Dữ liệu phản hồi:**
- `HTTP 200 OK`: `SingleResponseEnvelope[VerifyFactsResponse]` chứa báo cáo kiểm chứng:
  - `claims`: Mệnh đề nguyên tử kèm nhãn (supported, contradicted, not_enough_info),
    độ tin cậy (`confidence_score`), trích dẫn, trang và BoundingBox `[x0, y0, x1, y1, page]`.
  - `supported_ratio`: Tỷ lệ mệnh đề được chứng minh (0.0 - 1.0).
  - `latency_ms`: Thời gian xử lý kiểm chứng song song."""


@router.post(
    "/{id}/verify-facts",
    response_model=SingleResponseEnvelope[VerifyFactsResponse],
    summary="Kiểm chứng sự thật bản thảo qua SAFE (Verify Draft Facts)",
    description=VERIFY_FACTS_DESCRIPTION,
    responses={
        200: {"description": "Báo cáo kiểm chứng sự thật SAFE thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        403: {"model": ErrorResponse, "description": "Vai trò không có quyền kiểm chứng sự thật."},
        404: {"model": ErrorResponse, "description": "Bản thảo không tồn tại."},
    },
)
async def verify_draft_facts(
    id: UUID,
    request: VerifyFactsRequest | None = None,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> SingleResponseEnvelope[VerifyFactsResponse]:
    req = request or VerifyFactsRequest()
    try:
        report = await draft_service.verify_draft_facts(
            user_id=current_user.id,
            draft_id=id,
            text=req.text,
            document_ids=req.document_ids,
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
                "action": "Viewer and commenter roles cannot run AI fact verification.",
            },
        ) from exc

    claims_response = [
        AtomicClaimResponse(
            id=c.id,
            claim_text=c.claim_text,
            normalized_entities=c.normalized_entities,
            status=c.status.value,
            confidence_score=c.confidence_score,
            evidence_text=c.evidence_text,
            evidence_document_id=c.evidence_document_id,
            evidence_document_title=c.evidence_document_title,
            evidence_page=c.evidence_page,
            evidence_bounding_boxes=[b.to_list() for b in c.evidence_bounding_boxes],
            reasoning=c.reasoning,
        )
        for c in report.claims
    ]

    response_data = VerifyFactsResponse(
        draft_id=report.draft_id,
        verified_text=report.verified_text,
        claims=claims_response,
        total_claims=report.total_claims,
        supported_claims=report.supported_claims,
        contradicted_claims=report.contradicted_claims,
        unverified_claims=report.unverified_claims,
        supported_ratio=report.supported_ratio,
        latency_ms=report.latency_ms,
        verified_at=report.verified_at,
    )
    return SingleResponseEnvelope(data=response_data)


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
    )
    return SingleResponseEnvelope(data=response_data)


@router.get(
    "/{id}/preview.pdf",
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


# ==============================================================================
# Share Endpoints (/drafts/{id}/share)
# ==============================================================================


@router.post(
    "/{id}/share",
    response_model=SingleResponseEnvelope[DraftShareResponse],
    summary="Cấu hình chia sẻ hoặc mời cộng tác viên cho bản thảo (Share)",
    responses={
        200: {"description": "Cấu hình chia sẻ bản thảo thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        403: {"model": ErrorResponse, "description": "Chỉ chủ bản thảo mới có quyền chia sẻ."},
        404: {"model": ErrorResponse, "description": "Bản thảo không tồn tại."},
    },
)
async def share_draft(
    id: UUID,
    request: DraftShareRequest,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> SingleResponseEnvelope[DraftShareResponse]:
    try:
        settings = await draft_service.share_draft(
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
                "action": "Only the draft owner can configure share settings.",
            },
        ) from exc

    return SingleResponseEnvelope(data=settings)


@router.get(
    "/{id}/share",
    response_model=SingleResponseEnvelope[DraftShareResponse],
    summary="Lấy thông tin chia sẻ và danh sách cộng tác viên của bản thảo",
    responses={
        200: {"description": "Truy xuất thông tin chia sẻ thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        404: {"model": ErrorResponse, "description": "Bản thảo không tồn tại."},
    },
)
async def get_draft_share(
    id: UUID,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> SingleResponseEnvelope[DraftShareResponse]:
    try:
        settings = await draft_service.get_share_settings(
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
    return SingleResponseEnvelope(data=settings)


# ==============================================================================
# Peer Review Comments & Annotations Endpoints (/drafts/{id}/comments) - PRD §3.2
# ==============================================================================


@router.post(
    "/{id}/comments",
    response_model=SingleResponseEnvelope[DraftCommentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Thêm bình luận phản biện hoặc trả lời trên bản thảo (PRD §3.2)",
    responses={
        201: {"description": "Tạo bình luận thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        403: {
            "model": ErrorResponse,
            "description": "Không có quyền bình luận (ví dụ: vai trò viewer).",
        },
        404: {"model": ErrorResponse, "description": "Bản thảo hoặc bình luận cha không tồn tại."},
    },
)
async def create_draft_comment(
    id: UUID,
    request: CreateDraftCommentRequest,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> SingleResponseEnvelope[DraftCommentResponse]:
    author_name = current_user.full_name or current_user.email
    try:
        comment = await draft_service.create_comment(
            user_id=current_user.id,
            draft_id=id,
            request=request,
            author_name=author_name,
            user_email=current_user.email,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "RESOURCE_NOT_FOUND",
                "message": str(exc),
            },
        ) from exc
    except DraftRoleForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE_RESTRICTED",
                "message": str(exc),
                "action": "Commenter, Editor, or Owner role required to post comments.",
            },
        ) from exc

    return SingleResponseEnvelope(data=comment)


@router.get(
    "/{id}/comments",
    response_model=SingleResponseEnvelope[DraftCommentListResponse],
    summary="Lấy danh sách bình luận phản biện của bản thảo (PRD §3.2)",
    responses={
        200: {"description": "Truy xuất danh sách bình luận thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        404: {
            "model": ErrorResponse,
            "description": "Bản thảo không tồn tại hoặc không có quyền truy cập.",
        },
    },
)
async def list_draft_comments(
    id: UUID,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> SingleResponseEnvelope[DraftCommentListResponse]:
    try:
        comments_list = await draft_service.list_comments(
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
            },
        ) from exc

    return SingleResponseEnvelope(data=comments_list)


@router.patch(
    "/{id}/comments/{comment_id}",
    response_model=SingleResponseEnvelope[DraftCommentResponse],
    summary="Cập nhật nội dung hoặc trạng thái giải quyết của bình luận",
    responses={
        200: {"description": "Cập nhật bình luận thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        403: {"model": ErrorResponse, "description": "Không có quyền sửa đổi bình luận."},
        404: {"model": ErrorResponse, "description": "Bản thảo hoặc bình luận không tồn tại."},
    },
)
async def update_draft_comment(
    id: UUID,
    comment_id: UUID,
    request: UpdateDraftCommentRequest,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> SingleResponseEnvelope[DraftCommentResponse]:
    try:
        updated = await draft_service.update_comment(
            user_id=current_user.id,
            draft_id=id,
            comment_id=comment_id,
            request=request,
            user_email=current_user.email,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "RESOURCE_NOT_FOUND",
                "message": str(exc),
            },
        ) from exc
    except DraftRoleForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE_RESTRICTED",
                "message": str(exc),
            },
        ) from exc

    return SingleResponseEnvelope(data=updated)


@router.delete(
    "/{id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa bình luận phản biện (chỉ tác giả hoặc chủ bản thảo)",
    responses={
        204: {"description": "Xóa bình luận thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        403: {
            "model": ErrorResponse,
            "description": "Chỉ tác giả bình luận hoặc chủ bản thảo mới có quyền xóa.",
        },
        404: {"model": ErrorResponse, "description": "Bản thảo hoặc bình luận không tồn tại."},
    },
)
async def delete_draft_comment(
    id: UUID,
    comment_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> Response:
    try:
        await draft_service.delete_comment(
            user_id=current_user.id,
            draft_id=id,
            comment_id=comment_id,
            user_email=current_user.email,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "RESOURCE_NOT_FOUND",
                "message": str(exc),
            },
        ) from exc
    except DraftRoleForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN_ROLE_RESTRICTED",
                "message": str(exc),
            },
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{id}:export-overleaf",
    response_model=SingleResponseEnvelope[OverleafExportResponse],
    summary="Đồng bộ trực tiếp 1-click sang Overleaf (Overleaf 1-Click Sync)",
    description=(
        "Tạo URL trực tiếp mở bản thảo và gói tài liệu trên Overleaf theo chuẩn Web Launch API."
    ),
    responses={
        200: {"description": "Dữ liệu mở Overleaf được sinh thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
        404: {"model": ErrorResponse, "description": "Bản thảo không tồn tại."},
    },
)
@router.post(
    "/{id}/overleaf",
    response_model=SingleResponseEnvelope[OverleafExportResponse],
    include_in_schema=False,
)
@router.get(
    "/{id}/overleaf-launch",
    response_model=SingleResponseEnvelope[OverleafExportResponse],
    include_in_schema=False,
)
async def export_overleaf(
    id: UUID,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> SingleResponseEnvelope[OverleafExportResponse]:
    try:
        data = await draft_service.export_overleaf(
            user_id=current_user.id,
            draft_id=id,
            user_email=current_user.email,
        )
        return SingleResponseEnvelope(data=OverleafExportResponse.model_validate(data))
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "RESOURCE_NOT_FOUND", "message": str(exc)},
        ) from exc


@router.post(
    "/{id}/associative-suggestions",
    response_model=SingleResponseEnvelope[AssociativeSuggestionsResponse],
    summary="Gợi ý liên kết tri thức chủ động (Proactive Scholarly Associative Memory)",
    description=(
        "Đối chiếu đoạn văn đang soạn thảo với kho ghi chú tri thức lịch sử để gợi ý trích dẫn."
    ),
    responses={
        200: {"description": "Gợi ý tri thức chủ động được trích xuất thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực."},
    },
)
async def get_associative_suggestions(
    id: UUID,
    request: AssociativeSuggestionsRequest,
    current_user: UserModel = Depends(get_current_user),
    memory_service: AssociativeMemoryService = Depends(get_associative_memory_service),
) -> SingleResponseEnvelope[AssociativeSuggestionsResponse]:
    res = await memory_service.get_suggestions_for_draft(
        user_id=current_user.id,
        draft_id=id,
        request=request,
    )
    return SingleResponseEnvelope(data=res)
