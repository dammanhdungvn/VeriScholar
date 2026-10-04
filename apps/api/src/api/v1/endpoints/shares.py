"""Endpoints for Public Resource Sharing & Instant Revocation (Module 1/4 Collaboration)."""

from api.db.models.user import UserModel
from api.deps import get_current_user, get_share_service
from api.schemas.share import (
    CreateShareRequest,
    PublicShareEnvelope,
    ShareEnvelope,
)
from api.services.share_service import ShareService
from fastapi import APIRouter, Depends, Header, Response, status
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/shares", tags=["shares"])


@router.post(
    "",
    response_model=ShareEnvelope,
    status_code=status.HTTP_201_CREATED,
    summary="Create public shareable link",
)
async def create_share_link(
    req: CreateShareRequest,
    current_user: UserModel = Depends(get_current_user),
    share_service: ShareService = Depends(get_share_service),
) -> ShareEnvelope:
    """Generate a zero-auth public read-only link for a document, note, or collection."""
    share_data = await share_service.create_share(user_id=current_user.id, req=req)
    return ShareEnvelope(data=share_data)


@router.get(
    "/{token}",
    response_model=PublicShareEnvelope,
    summary="Get shared resource snapshot (Zero-Auth)",
)
async def get_public_share(
    token: str,
    share_service: ShareService = Depends(get_share_service),
) -> PublicShareEnvelope:
    """Access shared resource snapshot publicly without credentials.

    Returns HTTP 410 Gone immediately if the share link has been revoked or expired.
    """
    public_data = await share_service.get_public_share(token=token)
    return PublicShareEnvelope(data=public_data)


@router.get(
    "/{token}/file",
    summary="Stream shared document file (Zero-Auth with HTTP 206 Range)",
)
async def get_shared_file(
    token: str,
    range: str | None = Header(None, alias="Range"),
    share_service: ShareService = Depends(get_share_service),
) -> StreamingResponse:
    """Stream PDF for a public share link without requiring user authentication.

    Supports RFC 7233 partial content / byte ranges for fast PDF viewer rendering.
    """
    stream, headers, status_code = await share_service.get_shared_file_stream(
        token=token,
        range_header=range,
    )
    return StreamingResponse(stream, status_code=status_code, headers=headers)


@router.delete(
    "/{token}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Instantly revoke a public share link",
)
async def revoke_share_link(
    token: str,
    current_user: UserModel = Depends(get_current_user),
    share_service: ShareService = Depends(get_share_service),
) -> Response:
    """Instantly revoke a share link.

    Subsequent requests to the token will immediately return HTTP 410 Gone.
    Only the resource owner who created the link can revoke it.
    """
    await share_service.revoke_share(token=token, user_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
