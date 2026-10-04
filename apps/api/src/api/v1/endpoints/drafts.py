"""Endpoints for Module 2: Drafting Workspace, Sandbox Compiler & SAFE Fact-Checking."""

import math
from uuid import UUID

from api.db.models.user import UserModel
from api.deps import get_current_user, get_draft_service
from api.schemas.draft import (
    CompileDraftRequest,
    CreateDraftCommentRequest,
    CreateDraftRequest,
    DraftCommentEnvelope,
    DraftCommentsPageEnvelope,
    DraftEnvelope,
    DraftsPageEnvelope,
    PatchDraftRequest,
    UpdateDraftContentRequest,
    VerifyClaimsEnvelope,
    VerifyClaimsRequest,
)
from api.schemas.envelope import PaginationLinks, PaginationMeta
from api.services.draft_service import DraftService
from fastapi import (
    APIRouter,
    Depends,
    Header,
    Query,
    Response,
    status,
)
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/drafts", tags=["drafts"])


@router.post(
    "",
    response_model=DraftEnvelope,
    status_code=status.HTTP_201_CREATED,
    summary="Create academic draft",
)
async def create_draft(
    req: CreateDraftRequest,
    response: Response,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> DraftEnvelope:
    """Create a new academic draft."""
    draft_data = await draft_service.create_draft(user_id=current_user.id, req=req)
    response.headers["Location"] = f"/api/v1/drafts/{draft_data.id}"
    response.headers["ETag"] = f'"v{draft_data.version}"'
    return DraftEnvelope(data=draft_data)


@router.get(
    "",
    response_model=DraftsPageEnvelope,
    summary="List user drafts",
)
async def list_drafts(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> DraftsPageEnvelope:
    """List drafts owned by the authenticated user with pagination."""
    items, total = await draft_service.list_drafts(
        user_id=current_user.id, page=page, per_page=per_page
    )
    total_pages = max(1, math.ceil(total / per_page)) if total > 0 else 0
    base_url = "/api/v1/drafts"
    meta = PaginationMeta(
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )
    links = PaginationLinks(
        first=f"{base_url}?page=1&per_page={per_page}",
        prev=f"{base_url}?page={page - 1}&per_page={per_page}" if page > 1 else None,
        self=f"{base_url}?page={page}&per_page={per_page}",
        next=f"{base_url}?page={page + 1}&per_page={per_page}" if page < total_pages else None,
        last=f"{base_url}?page={max(1, total_pages)}&per_page={per_page}",
    )
    return DraftsPageEnvelope(
        data=items,
        meta=meta,
        links=links,
    )


@router.get(
    "/{id}",
    response_model=DraftEnvelope,
    summary="Get draft details",
)
async def get_draft(
    id: UUID,
    response: Response,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> DraftEnvelope:
    """Fetch draft details with source code and OCC ETag header."""
    draft_data = await draft_service.get_draft(draft_id=id, user_id=current_user.id)
    response.headers["ETag"] = f'"v{draft_data.version}"'
    return DraftEnvelope(data=draft_data)


@router.put(
    "/{id}",
    response_model=DraftEnvelope,
    summary="Update draft source code (OCC If-Match)",
)
async def update_draft_content(
    id: UUID,
    req: UpdateDraftContentRequest,
    response: Response,
    if_match: str | None = Header(None, alias="If-Match"),
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> DraftEnvelope:
    """Update draft source code guarded by RFC 9110 / RFC 7232 ETag OCC."""
    draft_data = await draft_service.update_draft_content(
        draft_id=id,
        user_id=current_user.id,
        content=req.content,
        if_match_etag=if_match,
    )
    response.headers["ETag"] = f'"v{draft_data.version}"'
    return DraftEnvelope(data=draft_data)


@router.patch(
    "/{id}",
    response_model=DraftEnvelope,
    summary="Patch draft metadata (OCC If-Match)",
)
async def patch_draft(
    id: UUID,
    req: PatchDraftRequest,
    response: Response,
    if_match: str | None = Header(None, alias="If-Match"),
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> DraftEnvelope:
    """Update draft metadata (title, template) guarded by OCC."""
    draft_data = await draft_service.patch_draft(
        draft_id=id,
        user_id=current_user.id,
        req=req,
        if_match_etag=if_match,
    )
    response.headers["ETag"] = f'"v{draft_data.version}"'
    return DraftEnvelope(data=draft_data)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete draft",
)
async def delete_draft(
    id: UUID,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> Response:
    """Permanently delete draft."""
    await draft_service.delete_draft(draft_id=id, user_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{id}:compile",
    summary="Compile LaTeX draft via isolated sandbox broker (SSE Stream)",
)
async def compile_draft(
    id: UUID,
    req: CompileDraftRequest = CompileDraftRequest(),
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> StreamingResponse:
    """Compile draft in sandbox broker, streaming compilation progress and self-healing patches."""
    stream = draft_service.compile_draft_stream(draft_id=id, user_id=current_user.id, req=req)
    return StreamingResponse(
        stream,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post(
    "/{id}:verify-claims",
    response_model=VerifyClaimsEnvelope,
    summary="Run 4-stage SAFE Fact-Checking on selected text",
)
async def verify_claims(
    id: UUID,
    req: VerifyClaimsRequest,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> VerifyClaimsEnvelope:
    """Execute 4-stage SAFE Fact-Checking pipeline on text excerpt with NLI grounding."""
    res = await draft_service.verify_claims(draft_id=id, user_id=current_user.id, req=req)
    return VerifyClaimsEnvelope(data=res)


@router.post(
    "/{id}/comments",
    response_model=DraftCommentEnvelope,
    status_code=status.HTTP_201_CREATED,
    summary="Add line-level peer review comment",
)
async def add_comment(
    id: UUID,
    req: CreateDraftCommentRequest,
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> DraftCommentEnvelope:
    """Add a review comment anchored to a specific line number in the draft."""
    author_name = current_user.full_name or "Peer Reviewer"
    comment_data = await draft_service.add_comment(
        draft_id=id,
        user_id=current_user.id,
        author_name=author_name,
        req=req,
    )
    return DraftCommentEnvelope(data=comment_data)


@router.get(
    "/{id}/comments",
    response_model=DraftCommentsPageEnvelope,
    summary="List comments on draft",
)
async def list_comments(
    id: UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> DraftCommentsPageEnvelope:
    """List peer review comments for the draft with pagination."""
    items, total = await draft_service.list_comments(
        draft_id=id,
        user_id=current_user.id,
        page=page,
        per_page=per_page,
    )
    total_pages = max(1, math.ceil(total / per_page)) if total > 0 else 0
    base_url = f"/api/v1/drafts/{id}/comments"
    meta = PaginationMeta(
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )
    links = PaginationLinks(
        first=f"{base_url}?page=1&per_page={per_page}",
        prev=f"{base_url}?page={page - 1}&per_page={per_page}" if page > 1 else None,
        self=f"{base_url}?page={page}&per_page={per_page}",
        next=f"{base_url}?page={page + 1}&per_page={per_page}" if page < total_pages else None,
        last=f"{base_url}?page={max(1, total_pages)}&per_page={per_page}",
    )
    return DraftCommentsPageEnvelope(
        data=items,
        meta=meta,
        links=links,
    )


@router.get(
    "/{id}/preview-pdf",
    summary="Stream compiled PDF live preview",
)
async def get_preview_pdf(
    id: UUID,
    range: str | None = Header(None, alias="Range"),
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> StreamingResponse:
    """Stream compiled PDF preview with HTTP 206 Partial Content range support."""
    # Ensure user has access to draft
    await draft_service.get_draft(draft_id=id, user_id=current_user.id)

    dummy_pdf = b"%PDF-1.7 Preview compilation output for draft " + str(id).encode()
    total_size = len(dummy_pdf)
    start_byte = 0
    end_byte = total_size - 1
    status_code = status.HTTP_200_OK

    if range and range.startswith("bytes="):
        byte_range = range.replace("bytes=", "").split("-")
        start_byte = int(byte_range[0]) if byte_range[0] else 0
        end_byte = int(byte_range[1]) if len(byte_range) > 1 and byte_range[1] else total_size - 1
        status_code = status.HTTP_206_PARTIAL_CONTENT

    content_length = end_byte - start_byte + 1
    sliced_bytes = dummy_pdf[start_byte : end_byte + 1]

    async def pdf_generator():
        yield sliced_bytes

    headers = {
        "Content-Type": "application/pdf",
        "Content-Length": str(content_length),
        "Accept-Ranges": "bytes",
        "Content-Range": f"bytes {start_byte}-{end_byte}/{total_size}",
    }
    return StreamingResponse(pdf_generator(), status_code=status_code, headers=headers)


@router.get(
    "/{id}/bundle",
    summary="Export camera-ready draft bundle",
)
async def export_draft_bundle(
    id: UUID,
    format: str = Query("zip", pattern="^(zip|pdf)$", description="Bundle format: zip or pdf"),
    current_user: UserModel = Depends(get_current_user),
    draft_service: DraftService = Depends(get_draft_service),
) -> StreamingResponse:
    """Export camera-ready bundle (.zip or .pdf) for publication submission."""
    bundle_bytes, media_type, filename = await draft_service.export_bundle(
        draft_id=id, user_id=current_user.id, format=format
    )

    headers = {
        "Content-Type": media_type,
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Length": str(len(bundle_bytes)),
    }
    return StreamingResponse(
        iter([bundle_bytes]),
        status_code=status.HTTP_200_OK,
        media_type=media_type,
        headers=headers,
    )
