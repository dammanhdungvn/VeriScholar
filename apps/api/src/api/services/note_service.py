"""Application service for Research Notes management (CRUD, OCC, Filters, Snapshots)."""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from api.db.models.chunk import DocumentChunkModel
from api.db.models.document import DocumentModel
from api.db.models.note import ResearchNoteModel
from api.schemas.note import (
    CreateNoteRequest,
    NoteListItemResponse,
    NoteResponse,
    UpdateNoteRequest,
)
from core.domain.exceptions import (
    ConcurrencyConflictError,
    EntityNotFoundError,
    InvalidNoteDataError,
    NoteNotFoundError,
    PreconditionRequiredError,
)
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class NoteService:
    """Orchestrates Research Note CRUD, frozen evidence preservation, and OCC."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_note(
        self,
        user_id: UUID,
        req: CreateNoteRequest,
    ) -> NoteResponse:
        """Create a new research note with an immutable frozen evidence snapshot."""
        if not req.selected_text or not req.selected_text.strip():
            raise InvalidNoteDataError("Selected text cannot be empty.")
        if req.page_number < 1:
            raise InvalidNoteDataError("Page number must be at least 1.")

        frozen_snapshot: dict[str, Any] = {
            "page_number": req.page_number,
            "selected_text": req.selected_text,
            "bounding_boxes": req.bounding_boxes,
            "captured_at": datetime.now(timezone.utc).isoformat(),
        }

        # If document_id is provided, verify ownership and enrich snapshot
        if req.document_id:
            doc_stmt = select(DocumentModel).where(
                DocumentModel.id == req.document_id,
                DocumentModel.user_id == user_id,
            )
            doc_res = await self.db.execute(doc_stmt)
            doc = doc_res.scalar_one_or_none()
            if not doc:
                raise EntityNotFoundError(
                    "Tài liệu nghiên cứu không tồn tại hoặc bạn không có quyền truy cập."
                )

            # Chunk metadata if present
            chunk_section = None
            if req.chunk_id:
                chunk_stmt = select(DocumentChunkModel).where(
                    DocumentChunkModel.id == req.chunk_id,
                    DocumentChunkModel.document_id == req.document_id,
                )
                chunk_res = await self.db.execute(chunk_stmt)
                chunk = chunk_res.scalar_one_or_none()
                if chunk:
                    chunk_section = f"Chunk {chunk.chunk_index} (Page {chunk.page_number})"

            parsed_meta = doc.parsed_metadata or {}
            frozen_snapshot.update(
                {
                    "document_id": str(doc.id),
                    "document_title": doc.title or doc.filename,
                    "authors": doc.authors or [],
                    "year": doc.publication_year,
                    "doi": doc.doi,
                    "arxiv_id": parsed_meta.get("arxiv_id"),
                    "source_filename": doc.filename,
                    "chunk_id": str(req.chunk_id) if req.chunk_id else None,
                    "chunk_section": chunk_section,
                }
            )
        else:
            frozen_snapshot.update(
                {
                    "document_id": None,
                    "document_title": "Ghi chú tự do (Không đính kèm văn bản)",
                    "authors": [],
                    "year": None,
                    "doi": None,
                    "arxiv_id": None,
                    "source_filename": "",
                    "chunk_id": None,
                    "chunk_section": None,
                }
            )

        # Deduplicate tags
        seen_tags: set[str] = set()
        cleaned_tags: list[str] = []
        for t in req.tags:
            clean_t = t.strip()
            if clean_t and clean_t not in seen_tags:
                seen_tags.add(clean_t)
                cleaned_tags.append(clean_t)

        now = datetime.now(timezone.utc)
        note_model = ResearchNoteModel(
            id=uuid4(),
            user_id=user_id,
            document_id=req.document_id,
            chunk_id=req.chunk_id,
            selected_text=req.selected_text,
            bounding_boxes=req.bounding_boxes,
            page_number=req.page_number,
            user_note=req.user_note,
            tags=cleaned_tags,
            frozen_snapshot=frozen_snapshot,
            is_source_detached=False,
            version=1,
            created_at=now,
            updated_at=now,
        )
        self.db.add(note_model)
        await self.db.commit()
        await self.db.refresh(note_model)

        return NoteResponse(
            id=note_model.id,
            document_id=note_model.document_id,
            chunk_id=note_model.chunk_id,
            selected_text=note_model.selected_text,
            bounding_boxes=note_model.bounding_boxes,
            page_number=note_model.page_number,
            user_note=note_model.user_note,
            tags=note_model.tags,
            frozen_snapshot=note_model.frozen_snapshot,
            is_source_detached=bool(getattr(note_model, "is_source_detached", False)),
            version=note_model.version,
            created_at=note_model.created_at or now,
            updated_at=note_model.updated_at or now,
        )

    async def list_notes(
        self,
        user_id: UUID,
        document_id: UUID | None = None,
        tag: str | None = None,
        folder_id: UUID | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[NoteListItemResponse], int]:
        """List user notes with optional filters and pagination."""
        base_query = select(ResearchNoteModel).where(ResearchNoteModel.user_id == user_id)

        if document_id:
            base_query = base_query.where(ResearchNoteModel.document_id == document_id)

        if tag:
            # Query PostgreSQL array using any/contains or exact tag filter
            base_query = base_query.where(ResearchNoteModel.tags.contains([tag]))

        if folder_id:
            # Filter through joined DocumentModel if document belongs to folder
            base_query = base_query.join(
                DocumentModel, ResearchNoteModel.document_id == DocumentModel.id
            ).where(DocumentModel.folder_id == folder_id)

        # Count total items
        count_stmt = select(func.count()).select_from(base_query.subquery())
        count_res = await self.db.execute(count_stmt)
        total = count_res.scalar_one() or 0

        # Pagination and order
        offset = (page - 1) * per_page
        query = (
            base_query.order_by(ResearchNoteModel.created_at.desc()).offset(offset).limit(per_page)
        )
        res = await self.db.execute(query)
        notes = list(res.scalars().all())

        now = datetime.now(timezone.utc)
        items: list[NoteListItemResponse] = []
        for n in notes:
            doc_title = None
            if getattr(n, "document", None):
                doc_title = n.document.title or n.document.filename
            elif n.frozen_snapshot:
                doc_title = n.frozen_snapshot.get("document_title")

            items.append(
                NoteListItemResponse(
                    id=n.id,
                    document_id=n.document_id,
                    document_title=doc_title,
                    selected_text=n.selected_text,
                    page_number=n.page_number,
                    user_note=n.user_note,
                    tags=n.tags,
                    is_source_detached=bool(getattr(n, "is_source_detached", False)),
                    version=n.version,
                    created_at=n.created_at or now,
                    updated_at=n.updated_at or now,
                )
            )

        return items, total

    async def get_note_by_id(
        self,
        note_id: UUID,
        user_id: UUID,
    ) -> NoteResponse:
        """Retrieve a specific note with full snapshot details."""
        stmt = select(ResearchNoteModel).where(
            ResearchNoteModel.id == note_id,
            ResearchNoteModel.user_id == user_id,
        )
        res = await self.db.execute(stmt)
        note = res.scalar_one_or_none()
        if not note:
            raise NoteNotFoundError("Ghi chú không tồn tại hoặc bạn không có quyền truy cập.")

        now = datetime.now(timezone.utc)
        return NoteResponse(
            id=note.id,
            document_id=note.document_id,
            chunk_id=note.chunk_id,
            selected_text=note.selected_text,
            bounding_boxes=note.bounding_boxes,
            page_number=note.page_number,
            user_note=note.user_note,
            tags=note.tags,
            frozen_snapshot=note.frozen_snapshot,
            is_source_detached=bool(getattr(note, "is_source_detached", False)),
            version=note.version,
            created_at=note.created_at or now,
            updated_at=note.updated_at or now,
        )

    async def update_note(
        self,
        note_id: UUID,
        user_id: UUID,
        req: UpdateNoteRequest,
        if_match_header: str | None,
    ) -> NoteResponse:
        """Update personal memo or tags with strict OCC (If-Match) validation."""
        if not if_match_header or not if_match_header.strip():
            raise PreconditionRequiredError(
                "Header 'If-Match' là bắt buộc để cập nhật ghi chú (RFC 7232)."
            )

        # Parse version from header (supports 'v1', '"v1"', '1', '"1"')
        cleaned_match = if_match_header.strip().strip('"').lstrip("v")
        try:
            expected_version = int(cleaned_match)
        except ValueError:
            raise ConcurrencyConflictError(
                f"Giá trị header If-Match không hợp lệ: '{if_match_header}'."
            )

        stmt = select(ResearchNoteModel).where(
            ResearchNoteModel.id == note_id,
            ResearchNoteModel.user_id == user_id,
        )
        res = await self.db.execute(stmt)
        note = res.scalar_one_or_none()
        if not note:
            raise NoteNotFoundError("Ghi chú không tồn tại hoặc bạn không có quyền truy cập.")

        # OCC Version check
        if note.version != expected_version:
            raise ConcurrencyConflictError(
                f"Xung đột phiên bản dữ liệu (OCC): Phiên bản hiện tại là {note.version}, "
                f"nhưng If-Match yêu cầu {expected_version}."
            )

        # Apply updates
        if req.user_note is not None:
            note.user_note = req.user_note

        if req.tags is not None:
            seen_tags: set[str] = set()
            cleaned_tags: list[str] = []
            for t in req.tags:
                clean_t = t.strip()
                if clean_t and clean_t not in seen_tags:
                    seen_tags.add(clean_t)
                    cleaned_tags.append(clean_t)
            note.tags = cleaned_tags

        # Increment version explicitly (trigger will also guarantee atomicity)
        note.version += 1
        now = datetime.now(timezone.utc)
        note.updated_at = now

        await self.db.commit()
        await self.db.refresh(note)

        return NoteResponse(
            id=note.id,
            document_id=note.document_id,
            chunk_id=note.chunk_id,
            selected_text=note.selected_text,
            bounding_boxes=note.bounding_boxes,
            page_number=note.page_number,
            user_note=note.user_note,
            tags=note.tags,
            frozen_snapshot=note.frozen_snapshot,
            is_source_detached=bool(getattr(note, "is_source_detached", False)),
            version=note.version,
            created_at=note.created_at or now,
            updated_at=note.updated_at or now,
        )

    async def delete_note(
        self,
        note_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Delete a research note idempotently without affecting source documents."""
        stmt = select(ResearchNoteModel).where(
            ResearchNoteModel.id == note_id,
            ResearchNoteModel.user_id == user_id,
        )
        res = await self.db.execute(stmt)
        note = res.scalar_one_or_none()
        if note:
            await self.db.delete(note)
            await self.db.commit()
            return True
        return False
