"""Application service for Public Resource Sharing & Instant Revocation (Module 1/4)."""

import secrets
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import UUID

from api.db.models.document import DocumentModel
from api.db.models.note import ResearchNoteModel
from api.db.models.share import ShareModel
from api.schemas.share import (
    CreateShareRequest,
    PublicShareResourceData,
    ShareResponseData,
)
from core.ports.storage import IBlobStoragePort
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ShareService:
    """Orchestrates public link generation, instant revocation, and zero-auth read access."""

    def __init__(self, db: AsyncSession, storage: IBlobStoragePort) -> None:
        self.db = db
        self.storage = storage

    async def create_share(
        self,
        user_id: UUID,
        req: CreateShareRequest,
    ) -> ShareResponseData:
        """Create a public read-only share link for an owned resource."""
        # 1. Validate ownership of the target resource
        if req.resource_type == "note":
            note_stmt = select(ResearchNoteModel).where(
                ResearchNoteModel.id == req.resource_id,
                ResearchNoteModel.user_id == user_id,
            )
            note_res = await self.db.execute(note_stmt)
            if note_res.scalar_one_or_none() is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "RESOURCE_NOT_FOUND",
                        "message": f"Note '{req.resource_id}' not found or access denied.",
                        "field": "resource_id",
                        "action": "Verify note ID.",
                    },
                )
        elif req.resource_type == "document":
            doc_stmt = select(DocumentModel).where(
                DocumentModel.id == req.resource_id,
                DocumentModel.user_id == user_id,
            )
            doc_res = await self.db.execute(doc_stmt)
            if doc_res.scalar_one_or_none() is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "RESOURCE_NOT_FOUND",
                        "message": f"Document '{req.resource_id}' not found or access denied.",
                        "field": "resource_id",
                        "action": "Verify document ID.",
                    },
                )

        # 2. Generate secure unique token
        token = f"sh_{secrets.token_urlsafe(24)}"

        share = ShareModel(
            token=token,
            user_id=user_id,
            resource_type=req.resource_type,
            resource_id=req.resource_id,
            permission=req.permission or "read_only",
            expires_at=req.expires_at,
            is_revoked=False,
        )
        self.db.add(share)
        await self.db.commit()
        await self.db.refresh(share)

        now = datetime.now(UTC)
        return ShareResponseData(
            share_token=share.token,
            resource_type=share.resource_type,
            resource_id=share.resource_id,
            permission=share.permission,
            share_url=f"/share/{share.token}",
            expires_at=share.expires_at,
            created_at=share.created_at or now,
        )

    async def get_public_share(self, token: str) -> PublicShareResourceData:
        """Fetch public shared resource snapshot without requiring authentication."""
        stmt = select(ShareModel).where(ShareModel.token == token)
        res = await self.db.execute(stmt)
        share = res.scalar_one_or_none()

        if share is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "SHARE_NOT_FOUND",
                    "message": "Share link not found.",
                    "field": "token",
                    "action": "Verify the share link URL.",
                },
            )

        # Check instant revocation -> HTTP 410 Gone
        if share.is_revoked:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail={
                    "code": "SHARE_REVOKED",
                    "message": "This shared resource link has been revoked by the owner.",
                    "field": "token",
                    "action": "Contact the owner for a new share link.",
                },
            )

        # Check expiration
        now = datetime.now(UTC)
        if share.expires_at and share.expires_at < now:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail={
                    "code": "SHARE_EXPIRED",
                    "message": "This share link has expired.",
                    "field": "token",
                    "action": "Request an updated share link.",
                },
            )

        # Fetch underlying resource
        resource_data: dict = {}
        if share.resource_type == "note":
            note_stmt = select(ResearchNoteModel).where(ResearchNoteModel.id == share.resource_id)
            note_res = await self.db.execute(note_stmt)
            note = note_res.scalar_one_or_none()
            if note:
                resource_data = {
                    "id": str(note.id),
                    "selected_text": note.selected_text,
                    "user_note": note.user_note,
                    "tags": note.tags,
                    "page_number": note.page_number,
                    "bounding_boxes": note.bounding_boxes,
                    "frozen_snapshot": note.frozen_snapshot,
                }
        elif share.resource_type == "document":
            doc_stmt = select(DocumentModel).where(DocumentModel.id == share.resource_id)
            doc_res = await self.db.execute(doc_stmt)
            doc = doc_res.scalar_one_or_none()
            if doc:
                resource_data = {
                    "id": str(doc.id),
                    "filename": doc.filename,
                    "title": doc.title,
                    "authors": doc.authors,
                    "publication_year": doc.publication_year,
                    "page_count": doc.page_count,
                    "pages_metadata": doc.pages_metadata,
                }

        return PublicShareResourceData(
            share_token=share.token,
            resource_type=share.resource_type,
            resource_id=share.resource_id,
            permission=share.permission,
            resource_data=resource_data,
            created_at=share.created_at or now,
        )

    async def revoke_share(self, token: str, user_id: UUID) -> bool:
        """Instantly revoke a share link, rendering it HTTP 410 Gone."""
        stmt = select(ShareModel).where(ShareModel.token == token)
        res = await self.db.execute(stmt)
        share = res.scalar_one_or_none()

        if share is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "SHARE_NOT_FOUND",
                    "message": "Share link not found.",
                    "field": "token",
                    "action": "Verify share token.",
                },
            )

        if share.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "REVOCATION_FORBIDDEN",
                    "message": "Only the resource owner can revoke this share link.",
                    "field": "token",
                    "action": "Ensure you are authenticated as the owner.",
                },
            )

        share.is_revoked = True
        await self.db.commit()
        return True

    async def get_shared_file_stream(
        self,
        token: str,
        range_header: str | None = None,
    ) -> tuple[AsyncIterator[bytes], dict[str, str], int]:
        """Stream PDF for public share link without requiring user authentication."""
        # 1. Verify share token
        stmt = select(ShareModel).where(ShareModel.token == token)
        res = await self.db.execute(stmt)
        share = res.scalar_one_or_none()

        if share is None or share.is_revoked:
            err_code = (
                status.HTTP_410_GONE if share and share.is_revoked else status.HTTP_404_NOT_FOUND
            )
            raise HTTPException(
                status_code=err_code,
                detail={
                    "code": "SHARE_INACCESSIBLE",
                    "message": "Share link is inactive or revoked.",
                    "field": "token",
                    "action": "Request a valid share link.",
                },
            )

        # 2. Find document
        doc_id = share.resource_id
        if share.resource_type == "note":
            note_stmt = select(ResearchNoteModel).where(ResearchNoteModel.id == share.resource_id)
            note_res = await self.db.execute(note_stmt)
            note = note_res.scalar_one_or_none()
            if not note or not note.document_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"code": "FILE_NOT_FOUND", "message": "Source document not found."},
                )
            doc_id = note.document_id

        doc_stmt = select(DocumentModel).where(DocumentModel.id == doc_id)
        doc_res = await self.db.execute(doc_stmt)
        doc = doc_res.scalar_one_or_none()
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "FILE_NOT_FOUND", "message": "Document file not found."},
            )

        total_size = doc.file_size_bytes
        start_byte = 0
        end_byte = total_size - 1
        status_code = status.HTTP_200_OK

        if range_header and range_header.startswith("bytes="):
            byte_range = range_header.replace("bytes=", "").split("-")
            start_byte = int(byte_range[0]) if byte_range[0] else 0
            end_byte = (
                int(byte_range[1]) if len(byte_range) > 1 and byte_range[1] else total_size - 1
            )
            status_code = status.HTTP_206_PARTIAL_CONTENT

        content_length = end_byte - start_byte + 1
        headers = {
            "Content-Type": "application/pdf",
            "Content-Length": str(content_length),
            "Accept-Ranges": "bytes",
            "Content-Range": f"bytes {start_byte}-{end_byte}/{total_size}",
        }

        stream = self.storage.stream_blob_range(
            doc.content_hash,
            start_byte=start_byte,
            end_byte=end_byte,
        )
        return stream, headers, status_code
