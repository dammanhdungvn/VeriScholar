"""Session Service coordinating research sessions and multi-document associations."""

from __future__ import annotations

import hashlib
import io
import zipfile
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import structlog
from api.db.models.document import DocumentModel
from api.db.models.reference import CitationEdgeModel, ReferenceItemModel
from api.db.models.session import (
    ResearchSessionModel,
    SessionDocumentModel,
    SessionTurnModel,
)
from api.schemas.session import (
    CitationGraphEdge,
    CitationGraphNode,
    CitationGraphResponseData,
    IngestedReferenceItem,
    SessionDocumentItem,
    SessionHistoryItem,
    SessionIngestReferencesResponseData,
    SessionResponseData,
    ViewportStateSchema,
)
from core.domain.entities.reference import ExtractedReference, ParsedReferenceInfo
from core.domain.entities.session import MAX_SESSION_DOCUMENTS
from core.ports.academic_resolver import IAcademicSearchResolverPort
from core.services.exa_resolver import InMemoryAcademicResolverAdapter
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from api.services.document_service import DocumentService

logger = structlog.get_logger("api.services.session")


class SessionService:
    """Application service managing research session lifecycles."""

    def __init__(
        self,
        db: AsyncSession,
        document_service: DocumentService | None = None,
    ) -> None:
        self.db = db
        self.document_service = document_service

    async def create_session(
        self,
        user_id: UUID,
        title: str | None = None,
        initial_document_ids: list[UUID] | None = None,
        include_documents: bool = False,
    ) -> SessionResponseData:
        """Create a new research session and associate initial documents."""
        raw_ids = initial_document_ids or []
        cleaned_doc_ids: list[UUID] = list(dict.fromkeys(raw_ids))

        if len(cleaned_doc_ids) > MAX_SESSION_DOCUMENTS:
            logger.warning(
                "session_capacity_exceeded",
                user_id=str(user_id),
                count=len(cleaned_doc_ids),
                max_allowed=MAX_SESSION_DOCUMENTS,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "SESSION_CAPACITY_EXCEEDED",
                    "message": (
                        f"Phiên đọc tối đa chỉ chứa {MAX_SESSION_DOCUMENTS} bài báo. "
                        "Vui lòng gỡ bớt bài báo trước khi nạp thêm."
                    ),
                    "action": (
                        f"Reduce initial_document_ids to {MAX_SESSION_DOCUMENTS} "
                        "or fewer documents."
                    ),
                },
            )

        docs_by_id: dict[UUID, DocumentModel] = {}
        warnings: list[str] = []

        if cleaned_doc_ids:
            stmt = select(DocumentModel).where(
                DocumentModel.id.in_(cleaned_doc_ids),
                DocumentModel.user_id == user_id,
            )
            result = await self.db.execute(stmt)
            fetched_docs = list(result.scalars().all())
            docs_by_id = {doc.id: doc for doc in fetched_docs}

            missing_or_forbidden = [
                doc_id for doc_id in cleaned_doc_ids if doc_id not in docs_by_id
            ]
            if missing_or_forbidden:
                logger.warning(
                    "session_create_document_not_found",
                    user_id=str(user_id),
                    missing_ids=[str(x) for x in missing_or_forbidden],
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "DOCUMENT_NOT_FOUND",
                        "message": "Tài liệu không tồn tại hoặc bạn không có quyền truy cập.",
                        "action": "Ensure all document IDs exist and belong to current user.",
                    },
                )

            for doc_id in cleaned_doc_ids:
                doc = docs_by_id[doc_id]
                if doc.status != "completed":
                    doc_label = doc.title or doc.filename
                    warnings.append(
                        f"Tài liệu '{doc_label}' đang ở trạng thái '{doc.status}'. "
                        "Khả năng hỏi đáp AI có thể bị hạn chế cho đến khi bóc tách xong."
                    )

        if title is not None and title.strip():
            resolved_title = title.strip()
        elif cleaned_doc_ids:
            first_doc = docs_by_id[cleaned_doc_ids[0]]
            doc_label = first_doc.title or first_doc.filename
            resolved_title = f"Nghiên cứu: {doc_label}"[:255]
        else:
            now_str = datetime.now(UTC).strftime("%d/%m/%Y %H:%M")
            resolved_title = f"Phiên nghiên cứu {now_str}"

        session_id = uuid4()
        active_doc_id = cleaned_doc_ids[0] if cleaned_doc_ids else None
        default_viewport = {"page": 1, "zoom_ratio": 1.0, "scroll_top": 0.0}

        session_model = ResearchSessionModel(
            id=session_id,
            user_id=user_id,
            title=resolved_title,
            active_document_id=active_doc_id,
            viewport_state=default_viewport,
            active_tab="chat",
            is_archived=False,
            archived_at=None,
            version=1,
        )
        self.db.add(session_model)
        await self.db.flush()

        session_doc_models: list[SessionDocumentModel] = []
        for idx, doc_id in enumerate(cleaned_doc_ids):
            session_doc = SessionDocumentModel(
                session_id=session_id,
                document_id=doc_id,
                display_order=idx,
            )
            self.db.add(session_doc)
            session_doc_models.append(session_doc)

        await self.db.commit()
        await self.db.refresh(session_model)

        logger.info(
            "session_created",
            session_id=str(session_model.id),
            user_id=str(user_id),
            title=resolved_title,
            document_count=len(cleaned_doc_ids),
        )

        embedded_docs: list[SessionDocumentItem] | None = None
        if include_documents and cleaned_doc_ids:
            embedded_docs = []
            for idx, doc_id in enumerate(cleaned_doc_ids):
                d = docs_by_id[doc_id]
                sd = session_doc_models[idx]
                embedded_docs.append(
                    SessionDocumentItem(
                        id=d.id,
                        title=d.title,
                        filename=d.filename,
                        status=d.status,
                        file_size_bytes=d.file_size_bytes,
                        added_at=sd.added_at or datetime.now(UTC),
                        display_order=sd.display_order,
                    )
                )

        return SessionResponseData(
            id=session_model.id,
            title=session_model.title,
            document_ids=cleaned_doc_ids,
            active_document_id=session_model.active_document_id,
            viewport_state=ViewportStateSchema(**session_model.viewport_state),
            active_tab=session_model.active_tab,
            is_archived=session_model.is_archived,
            version=session_model.version,
            documents=embedded_docs,
            warnings=warnings,
            created_at=session_model.created_at,
            updated_at=session_model.updated_at,
        )

    async def list_sessions(
        self,
        user_id: UUID,
        page: int = 1,
        per_page: int = 20,
        include_archived: bool = False,
        query: str | None = None,
    ) -> tuple[list[SessionHistoryItem], int]:
        """List sessions belonging to user for sidebar history with pagination and search."""
        stmt = select(ResearchSessionModel).where(ResearchSessionModel.user_id == user_id)
        if not include_archived:
            stmt = stmt.where(ResearchSessionModel.is_archived.is_(False))
        if query and query.strip():
            stmt = stmt.where(ResearchSessionModel.title.ilike(f"%{query.strip()}%"))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.order_by(ResearchSessionModel.updated_at.desc())
        stmt = stmt.offset((page - 1) * per_page).limit(per_page)
        res = await self.db.execute(stmt)
        sessions = list(res.scalars().all())

        if not sessions:
            return [], total

        session_ids = [s.id for s in sessions]
        doc_count_stmt = (
            select(
                SessionDocumentModel.session_id,
                func.count(SessionDocumentModel.document_id).label("doc_count"),
            )
            .where(SessionDocumentModel.session_id.in_(session_ids))
            .group_by(SessionDocumentModel.session_id)
        )
        doc_counts_res = await self.db.execute(doc_count_stmt)
        counts_map = dict(doc_counts_res.all())

        items = [
            SessionHistoryItem(
                id=s.id,
                title=s.title,
                document_count=counts_map.get(s.id, 0),
                active_tab=s.active_tab,
                is_archived=s.is_archived,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in sessions
        ]
        return items, total

    async def get_session_detail(
        self,
        session_id: UUID,
        user_id: UUID,
    ) -> SessionResponseData:
        """Retrieve full session snapshot, tabs, documents, and viewport state."""
        stmt = select(ResearchSessionModel).where(
            ResearchSessionModel.id == session_id,
            ResearchSessionModel.user_id == user_id,
        )
        res = await self.db.execute(stmt)
        session = res.scalar_one_or_none()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "SESSION_NOT_FOUND",
                    "message": "Phiên nghiên cứu không tồn tại hoặc bạn không có quyền truy cập.",
                    "action": "Verify session ID or create a new session.",
                },
            )

        doc_stmt = (
            select(SessionDocumentModel, DocumentModel)
            .join(DocumentModel, SessionDocumentModel.document_id == DocumentModel.id)
            .where(SessionDocumentModel.session_id == session_id)
            .order_by(SessionDocumentModel.display_order.asc())
        )
        doc_res = await self.db.execute(doc_stmt)
        pairs = doc_res.all()

        document_ids = [sd.document_id for sd, _ in pairs]
        documents = [
            SessionDocumentItem(
                id=d.id,
                title=d.title,
                filename=d.filename,
                status=d.status,
                file_size_bytes=d.file_size_bytes,
                added_at=sd.added_at or datetime.now(UTC),
                display_order=sd.display_order,
            )
            for sd, d in pairs
        ]

        msg_count_stmt = select(func.count(SessionTurnModel.id)).where(
            SessionTurnModel.session_id == session_id
        )
        msg_res = await self.db.execute(msg_count_stmt)
        msg_count = msg_res.scalar_one() or 0

        return SessionResponseData(
            id=session.id,
            title=session.title,
            document_ids=document_ids,
            active_document_id=session.active_document_id,
            viewport_state=ViewportStateSchema(**session.viewport_state),
            active_tab=session.active_tab,
            is_archived=session.is_archived,
            version=session.version,
            message_count=msg_count,
            documents=documents,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )

    async def update_metadata_occ(
        self,
        session_id: UUID,
        user_id: UUID,
        title: str,
        expected_version: int,
    ) -> SessionResponseData:
        """Update session title adhering to OCC (If-Match version)."""
        stmt = select(ResearchSessionModel).where(
            ResearchSessionModel.id == session_id,
            ResearchSessionModel.user_id == user_id,
        )
        res = await self.db.execute(stmt)
        session = res.scalar_one_or_none()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "SESSION_NOT_FOUND",
                    "message": "Phiên nghiên cứu không tồn tại hoặc bạn không có quyền truy cập.",
                    "action": "Verify session ID.",
                },
            )

        if session.is_archived:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "SESSION_ARCHIVED",
                    "message": "Phiên nghiên cứu đã lưu trữ, không thể chỉnh sửa tiêu đề.",
                    "action": "Restore session before editing.",
                },
            )

        if session.version != expected_version:
            logger.warning(
                "occ_version_mismatch",
                session_id=str(session_id),
                expected=expected_version,
                actual=session.version,
            )
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail={
                    "code": "CONCURRENCY_CONFLICT",
                    "message": (
                        f"Xung đột phiên bản đồng thời (If-Match 'v{expected_version}' "
                        f"khác phiên bản hiện tại 'v{session.version}'). "
                        "Vui lòng tải lại trạng thái mới nhất."
                    ),
                    "action": "Fetch current session state before applying updates.",
                },
            )

        session.title = title.strip()
        session.version += 1
        session.updated_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(session)

        return await self.get_session_detail(session_id, user_id)

    async def update_viewport_occ(
        self,
        session_id: UUID,
        user_id: UUID,
        viewport_state: dict,
        active_tab: str,
        active_document_id: UUID | None,
        expected_version: int,
    ) -> SessionResponseData:
        """Auto-save PDF scroll/zoom viewport state and active tab with OCC."""
        stmt = select(ResearchSessionModel).where(
            ResearchSessionModel.id == session_id,
            ResearchSessionModel.user_id == user_id,
        )
        res = await self.db.execute(stmt)
        session = res.scalar_one_or_none()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "SESSION_NOT_FOUND",
                    "message": "Phiên nghiên cứu không tồn tại hoặc bạn không có quyền truy cập.",
                    "action": "Verify session ID.",
                },
            )

        if session.is_archived:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "SESSION_ARCHIVED",
                    "message": "Phiên nghiên cứu đã lưu trữ, không thể cập nhật viewport.",
                    "action": "Restore session before navigating.",
                },
            )

        if session.version != expected_version:
            logger.warning(
                "viewport_occ_mismatch",
                session_id=str(session_id),
                expected=expected_version,
                actual=session.version,
            )
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail={
                    "code": "CONCURRENCY_CONFLICT",
                    "message": (
                        f"Xung đột phiên bản đồng thời (If-Match 'v{expected_version}' "
                        f"khác phiên bản hiện tại 'v{session.version}')."
                    ),
                    "action": "Refresh workspace session state.",
                },
            )

        if active_document_id is not None:
            doc_check = select(SessionDocumentModel).where(
                SessionDocumentModel.session_id == session_id,
                SessionDocumentModel.document_id == active_document_id,
            )
            c_res = await self.db.execute(doc_check)
            if not c_res.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "INVALID_ACTIVE_DOCUMENT",
                        "message": "Tài liệu được chọn không nằm trong phiên làm việc này.",
                        "action": "Select a document associated with the session.",
                    },
                )
            session.active_document_id = active_document_id

        session.viewport_state = viewport_state
        session.active_tab = active_tab
        session.version += 1
        session.updated_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(session)

        return await self.get_session_detail(session_id, user_id)

    async def delete_session(
        self,
        session_id: UUID,
        user_id: UUID,
    ) -> None:
        """Delete a research session and cascade cleanup its associations."""
        stmt = select(ResearchSessionModel).where(
            ResearchSessionModel.id == session_id,
            ResearchSessionModel.user_id == user_id,
        )
        res = await self.db.execute(stmt)
        session = res.scalar_one_or_none()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "SESSION_NOT_FOUND",
                    "message": "Phiên nghiên cứu không tồn tại hoặc bạn không có quyền truy cập.",
                    "action": "Verify session ID.",
                },
            )

        await self.db.delete(session)
        await self.db.commit()
        logger.info("session_deleted", session_id=str(session_id), user_id=str(user_id))

    async def add_document_to_session(
        self,
        session_id: UUID,
        user_id: UUID,
        source_type: str,
        document_id: UUID | None = None,
        url: str | None = None,
        title: str | None = None,
    ) -> dict:
        """Add a document to an existing session via pure JSON AIP pattern."""
        stmt = select(ResearchSessionModel).where(
            ResearchSessionModel.id == session_id,
            ResearchSessionModel.user_id == user_id,
        )
        res = await self.db.execute(stmt)
        session = res.scalar_one_or_none()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "SESSION_NOT_FOUND",
                    "message": "Phiên nghiên cứu không tồn tại hoặc bạn không có quyền truy cập.",
                    "action": "Verify session ID.",
                },
            )

        if session.is_archived:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "SESSION_ARCHIVED",
                    "message": ("Phiên đã bị lưu trữ. Vui lòng kích hoạt lại trước khi nạp thêm."),
                    "action": "Call restore-archived endpoint.",
                },
            )

        count_stmt = select(func.count(SessionDocumentModel.document_id)).where(
            SessionDocumentModel.session_id == session_id
        )
        count_res = await self.db.execute(count_stmt)
        current_count = count_res.scalar_one() or 0

        if current_count >= MAX_SESSION_DOCUMENTS:
            logger.warning(
                "session_capacity_exceeded",
                session_id=str(session_id),
                count=current_count,
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "code": "SESSION_CAPACITY_EXCEEDED",
                    "message": (
                        f"Phiên đọc tối đa chỉ chứa {MAX_SESSION_DOCUMENTS} bài báo. "
                        "Vui lòng gỡ bớt bài báo trước khi nạp thêm."
                    ),
                    "action": "Remove a document from session before adding a new one.",
                },
            )

        target_doc_id: UUID
        if source_type == "document_id":
            if not document_id:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail={
                        "code": "MISSING_DOCUMENT_ID",
                        "message": "Vui lòng truyền document_id khi source_type là 'document_id'.",
                        "action": "Provide valid document_id.",
                    },
                )

            doc_stmt = select(DocumentModel).where(
                DocumentModel.id == document_id,
                DocumentModel.user_id == user_id,
            )
            doc_res = await self.db.execute(doc_stmt)
            target_doc = doc_res.scalar_one_or_none()
            if not target_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "DOCUMENT_NOT_FOUND",
                        "message": "Tài liệu không tồn tại hoặc bạn không có quyền truy cập.",
                        "action": "Ensure document exists and belongs to current user.",
                    },
                )

            existing_link = select(SessionDocumentModel).where(
                SessionDocumentModel.session_id == session_id,
                SessionDocumentModel.document_id == document_id,
            )
            link_res = await self.db.execute(existing_link)
            if link_res.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": "DOCUMENT_ALREADY_IN_SESSION",
                        "message": "Tài liệu này đã có trong phiên nghiên cứu.",
                        "action": "Document is already active in session.",
                    },
                )
            target_doc_id = document_id
        elif source_type == "url":
            if not url:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail={
                        "code": "MISSING_URL",
                        "message": "Vui lòng truyền URL khi source_type là 'url'.",
                        "action": "Provide valid paper URL.",
                    },
                )
            target_doc_id = uuid4()
            placeholder_doc = DocumentModel(
                id=target_doc_id,
                user_id=user_id,
                filename=url.split("/")[-1] or "paper_from_url.pdf",
                title=title or "Tài liệu nạp qua liên kết URL",
                file_size_bytes=1024,
                content_hash=f"url_{uuid4().hex}",
                status="processing",
                stage="queued",
                progress=0,
            )
            self.db.add(placeholder_doc)
            await self.db.flush()
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "code": "INVALID_SOURCE_TYPE",
                    "message": "source_type chỉ chấp nhận 'document_id' hoặc 'url'.",
                    "action": "Use 'document_id' or 'url'.",
                },
            )

        new_link = SessionDocumentModel(
            session_id=session_id,
            document_id=target_doc_id,
            display_order=current_count,
        )
        self.db.add(new_link)

        if session.active_document_id is None:
            session.active_document_id = target_doc_id

        session.version += 1
        session.updated_at = datetime.now(UTC)
        await self.db.commit()

        logger.info(
            "document_added_to_session",
            session_id=str(session_id),
            document_id=str(target_doc_id),
            source_type=source_type,
        )

        return {
            "document_id": str(target_doc_id),
            "session_id": str(session_id),
            "status": "queued" if source_type == "url" else "associated",
            "version": session.version,
        }

    async def restore_archived_session(
        self,
        session_id: UUID,
        user_id: UUID,
        file: UploadFile,
    ) -> SessionResponseData:
        """Reactivate an expired TTL session by uploading original PDF."""
        stmt = select(ResearchSessionModel).where(
            ResearchSessionModel.id == session_id,
            ResearchSessionModel.user_id == user_id,
        )
        res = await self.db.execute(stmt)
        session = res.scalar_one_or_none()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "SESSION_NOT_FOUND",
                    "message": "Phiên nghiên cứu không tồn tại hoặc bạn không có quyền truy cập.",
                    "action": "Verify session ID.",
                },
            )

        content = await file.read()
        if not content.startswith(b"%PDF"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_PDF_HEADER",
                    "message": "Tệp tải lên không phải là định dạng PDF hợp lệ.",
                    "action": "Provide a valid PDF file.",
                },
            )

        session.is_archived = False
        session.archived_at = None
        session.version += 1
        session.updated_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(session)

        logger.info("session_archived_restored", session_id=str(session_id))
        return await self.get_session_detail(session_id, user_id)

    async def export_bundle(
        self,
        session_id: UUID,
        user_id: UUID,
    ) -> bytes:
        """Export full offline research bundle zip."""
        stmt = select(ResearchSessionModel).where(
            ResearchSessionModel.id == session_id,
            ResearchSessionModel.user_id == user_id,
        )
        res = await self.db.execute(stmt)
        session = res.scalar_one_or_none()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "SESSION_NOT_FOUND",
                    "message": "Phiên nghiên cứu không tồn tại hoặc bạn không có quyền truy cập.",
                    "action": "Verify session ID.",
                },
            )

        docs_stmt = (
            select(DocumentModel)
            .join(SessionDocumentModel, DocumentModel.id == SessionDocumentModel.document_id)
            .where(SessionDocumentModel.session_id == session_id)
            .order_by(SessionDocumentModel.display_order.asc())
        )
        docs_res = await self.db.execute(docs_stmt)
        documents = list(docs_res.scalars().all())

        turns_stmt = (
            select(SessionTurnModel)
            .where(SessionTurnModel.session_id == session_id)
            .order_by(SessionTurnModel.created_at.asc())
        )
        turns_res = await self.db.execute(turns_stmt)
        turns = list(turns_res.scalars().all())

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for doc in documents:
                pdf_filename = doc.filename or f"{doc.id}.pdf"
                label = doc.title or doc.filename
                content_bytes: bytes | None = None
                if self.document_service is not None:
                    try:
                        pdf_bytes, fn, _ = await self.document_service.export_annotated_pdf(
                            doc.id, user_id, self.db, include_highlights=True
                        )
                        content_bytes = pdf_bytes
                        if fn:
                            pdf_filename = fn
                    except Exception as ex:
                        logger.warning(
                            "export_annotated_pdf_fallback",
                            doc_id=str(doc.id),
                            error=str(ex),
                        )
                if content_bytes is None:
                    content_bytes = f"%PDF-1.4\n% VeriScholar PDF: {label}\n%%EOF".encode("utf-8")
                zf.writestr(f"documents/{pdf_filename}", content_bytes)

            doc_titles = [f"- {d.title or d.filename} (ID: {d.id})" for d in documents]
            doc_list_str = "\n".join(doc_titles) if doc_titles else "*(Chưa nạp tài liệu)*"

            turns_md: list[str] = []
            for idx, turn in enumerate(turns, start=1):
                turns_md.append(f"### Q{idx}: {turn.question}\n\n**A:** {turn.answer}\n")
            turns_md_str = "\n".join(turns_md) if turns_md else "*(Chưa có lịch sử đối thoại)*"

            master_lesson = (
                f'---\nsession_id: "{session.id}"\ntitle: "{session.title}"\n'
                f'exported_at: "{datetime.now(UTC).isoformat()}"\n'
                f"documents_count: {len(documents)}\nturns_count: {len(turns)}\n---\n\n"
                f"# {session.title}\n\n## 1. Danh Mục Tài Liệu Trong Phiên\n{doc_list_str}\n\n"
                f"## 2. Các Luận Điểm Nghiên Cứu & Đối Thoại\n{turns_md_str}\n\n"
                f"## 3. Bản Quyền & Trích Dẫn\nĐược xuất tự động từ hệ sinh thái VeriScholar.\n"
            )
            zf.writestr("master_lesson.md", master_lesson.encode("utf-8"))

            chat_cards: list[str] = []
            for idx, turn in enumerate(turns, start=1):
                chat_cards.append(
                    f'<div class="turn-card"><div class="user-q"><strong>Hỏi {idx}:</strong> '
                    f'{turn.question}</div><div class="assistant-a"><strong>VeriScholar:</strong> '
                    f"{turn.answer}</div></div>"
                )
            chat_cards_html = (
                "\n".join(chat_cards)
                if chat_cards
                else "<p><em>Chưa có câu hỏi nào trong phiên.</em></p>"
            )

            html_content = (
                f'<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8">'
                f"<title>{session.title} - VeriScholar Offline Transcript</title>"
                f"<style>body {{ font-family: sans-serif; max-width: 860px; margin: 40px auto; "
                f"padding: 0 20px; line-height: 1.6; color: #1e293b; background: #f8fafc; }}"
                f".turn-card {{ background: #ffffff; border-radius: 8px; padding: 18px; "
                f"margin-bottom: 16px; border-left: 4px solid #3b82f6; }}"
                f".user-q {{ font-weight: 600; color: #1e3a8a; margin-bottom: 8px; }}"
                f"</style></head><body>"
                f'<h1>{session.title}</h1><div class="meta">'
                f"Phiên ID: {session.id} • Số bài báo: {len(documents)}</div>"
                f'<div class="chat-container">{chat_cards_html}</div></body></html>'
            )
            zf.writestr("chat_transcript.html", html_content.encode("utf-8"))

        return buf.getvalue()

    async def ingest_references(
        self,
        session_id: UUID,
        user_id: UUID,
        document_id: UUID,
        selected_ref_indices: list[int],
        resolver: IAcademicSearchResolverPort | None = None,
    ) -> SessionIngestReferencesResponseData:
        """Ingest selected open-access references into session documents (PRD §3.3).

        Strictly enforces Session Capacity Cap <= 5 papers.
        Raises HTTP 422 Unprocessable Entity if current_doc_count + len(selected_ref_indices) > 5.
        """
        # 1. Enforce session ownership
        session_stmt = select(ResearchSessionModel).where(
            ResearchSessionModel.id == session_id,
            ResearchSessionModel.user_id == user_id,
        )
        session_res = await self.db.execute(session_stmt)
        session = session_res.scalar_one_or_none()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "SESSION_NOT_FOUND",
                    "message": "Phiên nghiên cứu không tồn tại hoặc bạn không có quyền truy cập.",
                    "action": "Verify session ID.",
                },
            )
        if session.is_archived:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "SESSION_ARCHIVED",
                    "message": "Phiên đã bị lưu trữ. Vui lòng kích hoạt lại trước khi nạp thêm.",
                    "action": "Call restore-archived endpoint.",
                },
            )

        # 2. Enforce source document ownership
        doc_stmt = select(DocumentModel).where(
            DocumentModel.id == document_id,
            DocumentModel.user_id == user_id,
        )
        doc_res = await self.db.execute(doc_stmt)
        source_doc = doc_res.scalar_one_or_none()
        if not source_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DOCUMENT_NOT_FOUND",
                    "message": f"Tài liệu nguồn '{document_id}' không tồn tại.",
                    "action": "Verify document ID.",
                },
            )

        # 3. Check session capacity (Cap <= 5 papers)
        count_stmt = select(func.count(SessionDocumentModel.document_id)).where(
            SessionDocumentModel.session_id == session_id
        )
        count_res = await self.db.execute(count_stmt)
        current_count = count_res.scalar_one() or 0

        if current_count + len(selected_ref_indices) > MAX_SESSION_DOCUMENTS:
            logger.warning(
                "session_capacity_exceeded_ingest",
                session_id=str(session_id),
                current=current_count,
                requested=len(selected_ref_indices),
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "code": "SESSION_CAPACITY_EXCEEDED",
                    "message": (
                        "Phiên đọc sâu giới hạn tối đa 5 bài báo. Vui lòng bỏ bớt bài "
                        "hoặc lưu vào Thư viện (Module 4) để quản lý kho lớn hơn"
                    ),
                    "action": "Reduce selected references or manage documents in library.",
                },
            )

        # 4. Ingest references
        active_resolver = resolver or InMemoryAcademicResolverAdapter()
        ingested_items: list[IngestedReferenceItem] = []

        for idx, ref_idx in enumerate(selected_ref_indices):
            ref_stmt = select(ReferenceItemModel).where(
                ReferenceItemModel.document_id == document_id,
                ReferenceItemModel.ref_index == ref_idx,
            )
            ref_res = await self.db.execute(ref_stmt)
            ref_item = ref_res.scalar_one_or_none()
            if not ref_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "REFERENCE_NOT_FOUND",
                        "message": f"Tài liệu tham khảo #{ref_idx} không tồn tại trong bài báo.",
                        "action": "Extract references first.",
                    },
                )

            extracted = ExtractedReference(
                ref_index=ref_item.ref_index,
                raw_text=ref_item.raw_text,
                parsed=ParsedReferenceInfo(
                    title=ref_item.parsed_title,
                    authors=ref_item.parsed_authors or [],
                    year=ref_item.parsed_year,
                    arxiv_id=ref_item.arxiv_id,
                    doi=ref_item.doi,
                ),
            )
            resolved = await active_resolver.resolve_reference(extracted)

            target_doc: DocumentModel | None = None
            if ref_item.resolved_document_id:
                target_doc = await self.db.get(DocumentModel, ref_item.resolved_document_id)

            if not target_doc:
                doc_title = resolved.title or ref_item.parsed_title or f"Reference #{ref_idx}"
                authors_val = resolved.authors or ref_item.parsed_authors or []
                content_seed = f"ref_{document_id}_{ref_idx}_{doc_title}".encode("utf-8")
                content_hash = hashlib.sha256(content_seed).hexdigest()

                target_doc = DocumentModel(
                    user_id=user_id,
                    filename=f"ingested_{ref_idx}.pdf",
                    title=doc_title,
                    authors=authors_val,
                    publication_year=resolved.year or ref_item.parsed_year,
                    doi=resolved.doi or ref_item.doi,
                    content_hash=content_hash,
                    file_size_bytes=1024,
                    status="ready",
                    stage="completed",
                    progress=100,
                    is_persistent=True,
                )
                self.db.add(target_doc)
                await self.db.flush()

                ref_item.resolved_document_id = target_doc.id

            display_order = current_count + idx
            sess_doc_stmt = select(SessionDocumentModel).where(
                SessionDocumentModel.session_id == session_id,
                SessionDocumentModel.document_id == target_doc.id,
            )
            existing_link = (await self.db.execute(sess_doc_stmt)).scalar_one_or_none()
            if not existing_link:
                self.db.add(
                    SessionDocumentModel(
                        session_id=session_id,
                        document_id=target_doc.id,
                        display_order=display_order,
                    )
                )

            # Record citation edge (source document cites target document)
            edge_stmt = select(CitationEdgeModel).where(
                CitationEdgeModel.source_document_id == document_id,
                CitationEdgeModel.target_document_id == target_doc.id,
            )
            existing_edge = (await self.db.execute(edge_stmt)).scalar_one_or_none()
            if not existing_edge:
                self.db.add(
                    CitationEdgeModel(
                        source_document_id=document_id,
                        target_document_id=target_doc.id,
                        relation="CITES",
                        confidence=1.0,
                    )
                )

            ingested_items.append(
                IngestedReferenceItem(
                    ref_index=ref_idx,
                    document_id=target_doc.id,
                    title=target_doc.title or "Untitled",
                    authors=target_doc.authors or [],
                    open_access_pdf_url=resolved.open_access_pdf_url,
                    display_order=display_order,
                )
            )

        await self.db.commit()

        final_count_res = await self.db.execute(count_stmt)
        final_count = final_count_res.scalar_one() or (current_count + len(ingested_items))

        return SessionIngestReferencesResponseData(
            session_id=session_id,
            total_ingested=len(ingested_items),
            session_document_count=final_count,
            ingested_documents=ingested_items,
        )

    @staticmethod
    def _infer_citation_relation(raw_text: str, title: str | None) -> str:
        """Infer relation type (CITES, EXTENDS, BENCHMARKS_ON) from citation text."""
        combined = f"{raw_text} {title or ''}".lower()
        bench_terms = ["benchmark", "dataset", "baseline", "evaluation metric"]
        if any(term in combined for term in bench_terms):
            return "BENCHMARKS_ON"
        extend_terms = ["extend", "improves upon", "built upon", "generalized", "enhancement"]
        if any(term in combined for term in extend_terms):
            return "EXTENDS"
        return "CITES"

    async def get_citation_graph(
        self,
        session_id: UUID,
        user_id: UUID,
    ) -> CitationGraphResponseData:
        """Construct multi-paper citation graph with Cycle Breaking & Max-Hop (k <= 2)."""
        # 1. Enforce session ownership
        session_stmt = select(ResearchSessionModel).where(
            ResearchSessionModel.id == session_id,
            ResearchSessionModel.user_id == user_id,
        )
        session_res = await self.db.execute(session_stmt)
        session = session_res.scalar_one_or_none()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "SESSION_NOT_FOUND",
                    "message": "Phiên nghiên cứu không tồn tại hoặc bạn không có quyền truy cập.",
                    "action": "Verify session ID.",
                },
            )

        # 2. Fetch all session documents (Depth 0)
        docs_stmt = (
            select(DocumentModel)
            .join(SessionDocumentModel, SessionDocumentModel.document_id == DocumentModel.id)
            .where(SessionDocumentModel.session_id == session_id)
            .order_by(SessionDocumentModel.display_order.asc())
        )
        session_docs = list((await self.db.execute(docs_stmt)).scalars().all())
        session_doc_ids = {str(d.id) for d in session_docs}

        nodes_dict: dict[str, CitationGraphNode] = {}
        edges: list[CitationGraphEdge] = []
        edge_set: set[tuple[str, str]] = set()

        for doc in session_docs:
            nodes_dict[str(doc.id)] = CitationGraphNode(
                id=str(doc.id),
                title=doc.title or doc.filename,
                authors=doc.authors or [],
                year=doc.publication_year,
                doi=doc.doi,
                arxiv_id=None,
                is_session_document=True,
                depth=0,
            )

        # 3. Hop 1 Traversal (Depth 1)
        depth_1_doc_ids: set[str] = set()

        for doc in session_docs:
            u_id = str(doc.id)

            # Explicit CitationEdgeModel
            edge_stmt = select(CitationEdgeModel).where(
                CitationEdgeModel.source_document_id == doc.id
            )
            edge_res = await self.db.execute(edge_stmt)
            for e in edge_res.scalars().all():
                v_id = str(e.target_document_id)
                if v_id == u_id:
                    continue  # Self-loop cycle breaking
                if (u_id, v_id) not in edge_set:
                    edge_set.add((u_id, v_id))
                    edges.append(
                        CitationGraphEdge(
                            source=u_id,
                            target=v_id,
                            relation=e.relation,
                            confidence=e.confidence,
                        )
                    )
                if v_id not in nodes_dict:
                    t_doc = await self.db.get(DocumentModel, e.target_document_id)
                    if t_doc:
                        nodes_dict[v_id] = CitationGraphNode(
                            id=v_id,
                            title=t_doc.title or t_doc.filename,
                            authors=t_doc.authors or [],
                            year=t_doc.publication_year,
                            doi=t_doc.doi,
                            arxiv_id=None,
                            is_session_document=v_id in session_doc_ids,
                            depth=1,
                        )
                        depth_1_doc_ids.add(v_id)

            # ReferenceItemModel
            ref_stmt = select(ReferenceItemModel).where(ReferenceItemModel.document_id == doc.id)
            ref_res = await self.db.execute(ref_stmt)
            for r in ref_res.scalars().all():
                if r.resolved_document_id:
                    v_id = str(r.resolved_document_id)
                    if v_id == u_id:
                        continue  # Self-loop cycle breaking
                    if (u_id, v_id) not in edge_set:
                        edge_set.add((u_id, v_id))
                        rel = self._infer_citation_relation(r.raw_text, r.parsed_title)
                        edges.append(
                            CitationGraphEdge(
                                source=u_id,
                                target=v_id,
                                relation=rel,
                                confidence=0.95,
                            )
                        )
                    if v_id not in nodes_dict:
                        t_doc = await self.db.get(DocumentModel, r.resolved_document_id)
                        if t_doc:
                            nodes_dict[v_id] = CitationGraphNode(
                                id=v_id,
                                title=t_doc.title or t_doc.filename,
                                authors=t_doc.authors or [],
                                year=t_doc.publication_year,
                                doi=t_doc.doi,
                                arxiv_id=None,
                                is_session_document=v_id in session_doc_ids,
                                depth=1,
                            )
                            depth_1_doc_ids.add(v_id)
                else:
                    ref_node_id = f"ref_{doc.id}_{r.ref_index}"
                    if (u_id, ref_node_id) not in edge_set:
                        edge_set.add((u_id, ref_node_id))
                        rel = self._infer_citation_relation(r.raw_text, r.parsed_title)
                        edges.append(
                            CitationGraphEdge(
                                source=u_id,
                                target=ref_node_id,
                                relation=rel,
                                confidence=0.90,
                            )
                        )
                    if ref_node_id not in nodes_dict:
                        nodes_dict[ref_node_id] = CitationGraphNode(
                            id=ref_node_id,
                            title=r.parsed_title or r.raw_text[:80],
                            authors=r.parsed_authors or [],
                            year=r.parsed_year,
                            doi=r.doi,
                            arxiv_id=r.arxiv_id,
                            is_session_document=False,
                            depth=1,
                        )

        # 4. Hop 2 Traversal (Depth 2) with Strict Cycle Breaking (k <= 2)
        for v_id in list(depth_1_doc_ids):
            try:
                v_uuid = UUID(v_id)
            except ValueError:
                continue

            # Query edges of depth 1 doc
            edge_stmt = select(CitationEdgeModel).where(
                CitationEdgeModel.source_document_id == v_uuid
            )
            edge_res = await self.db.execute(edge_stmt)
            for e in edge_res.scalars().all():
                w_id = str(e.target_document_id)
                # Cycle breaking: do not add edges back to depth 0 or reverse edge
                if w_id in session_doc_ids or w_id == v_id or (w_id, v_id) in edge_set:
                    continue
                if (v_id, w_id) not in edge_set:
                    edge_set.add((v_id, w_id))
                    edges.append(
                        CitationGraphEdge(
                            source=v_id,
                            target=w_id,
                            relation=e.relation,
                            confidence=e.confidence,
                        )
                    )
                if w_id not in nodes_dict:
                    w_doc = await self.db.get(DocumentModel, e.target_document_id)
                    if w_doc:
                        nodes_dict[w_id] = CitationGraphNode(
                            id=w_id,
                            title=w_doc.title or w_doc.filename,
                            authors=w_doc.authors or [],
                            year=w_doc.publication_year,
                            doi=w_doc.doi,
                            arxiv_id=None,
                            is_session_document=False,
                            depth=2,
                        )

            # Query references of depth 1 doc
            ref_stmt = select(ReferenceItemModel).where(ReferenceItemModel.document_id == v_uuid)
            ref_res = await self.db.execute(ref_stmt)
            for r in ref_res.scalars().all():
                if r.resolved_document_id:
                    w_id = str(r.resolved_document_id)
                    # Cycle breaking check
                    if w_id in session_doc_ids or w_id == v_id or (w_id, v_id) in edge_set:
                        continue
                    if (v_id, w_id) not in edge_set:
                        edge_set.add((v_id, w_id))
                        rel = self._infer_citation_relation(r.raw_text, r.parsed_title)
                        edges.append(
                            CitationGraphEdge(
                                source=v_id,
                                target=w_id,
                                relation=rel,
                                confidence=0.95,
                            )
                        )
                    if w_id not in nodes_dict:
                        w_doc = await self.db.get(DocumentModel, r.resolved_document_id)
                        if w_doc:
                            nodes_dict[w_id] = CitationGraphNode(
                                id=w_id,
                                title=w_doc.title or w_doc.filename,
                                authors=w_doc.authors or [],
                                year=w_doc.publication_year,
                                doi=w_doc.doi,
                                arxiv_id=None,
                                is_session_document=False,
                                depth=2,
                            )
                else:
                    ref_node_id = f"ref_{v_id}_{r.ref_index}"
                    if (v_id, ref_node_id) not in edge_set:
                        edge_set.add((v_id, ref_node_id))
                        rel = self._infer_citation_relation(r.raw_text, r.parsed_title)
                        edges.append(
                            CitationGraphEdge(
                                source=v_id,
                                target=ref_node_id,
                                relation=rel,
                                confidence=0.90,
                            )
                        )
                    if ref_node_id not in nodes_dict:
                        nodes_dict[ref_node_id] = CitationGraphNode(
                            id=ref_node_id,
                            title=r.parsed_title or r.raw_text[:80],
                            authors=r.parsed_authors or [],
                            year=r.parsed_year,
                            doi=r.doi,
                            arxiv_id=r.arxiv_id,
                            is_session_document=False,
                            depth=2,
                        )

        # 5. Compute Foundational Reading Path (Topological Ordering)
        # Prerequisite edge: target -> source (cited prior work should be read before citing work)
        all_node_ids = list(nodes_dict.keys())
        prereq_graph: dict[str, list[str]] = {nid: [] for nid in all_node_ids}
        in_degree: dict[str, int] = {nid: 0 for nid in all_node_ids}

        for edge in edges:
            u, v = edge.target, edge.source
            if u in prereq_graph and v in prereq_graph:
                prereq_graph[u].append(v)
                in_degree[v] += 1

        def _node_sort_key(nid: str) -> tuple[int, int]:
            return (nodes_dict[nid].depth, -(nodes_dict[nid].year or 0))

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        queue.sort(key=_node_sort_key, reverse=True)

        reading_path: list[str] = []
        visited_topo: set[str] = set()

        while queue:
            curr = queue.pop(0)
            if curr in visited_topo:
                continue
            visited_topo.add(curr)
            reading_path.append(curr)

            for neighbor in prereq_graph.get(curr, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] <= 0 and neighbor not in visited_topo:
                    queue.append(neighbor)
            queue.sort(key=_node_sort_key, reverse=True)

        remaining = [nid for nid in all_node_ids if nid not in visited_topo]
        remaining.sort(key=_node_sort_key, reverse=True)
        reading_path.extend(remaining)

        return CitationGraphResponseData(
            session_id=session_id,
            nodes=list(nodes_dict.values()),
            edges=edges,
            reading_path=reading_path,
        )
