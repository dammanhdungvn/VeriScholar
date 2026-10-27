"""Session Service coordinating research sessions and multi-document associations."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import structlog
from api.db.models.document import DocumentModel
from api.db.models.reference import ReferenceItemModel
from api.db.models.session import (
    ResearchSessionModel,
    SessionDocumentModel,
    SessionTurnModel,
)
from api.schemas.session import (
    IngestedReferenceItem,
    SessionDocumentItem,
    SessionHistoryItem,
    SessionIngestReferencesResponseData,
    SessionResponseData,
    ViewportStateSchema,
)
from core.domain.entities.reference import (
    ExtractedReference,
    ParsedReferenceInfo,
    has_public_academic_identifier,
)
from core.ports.academic_resolver import IAcademicSearchResolverPort
from core.services.citation_parser import (
    MAX_SESSION_DOCUMENTS,
    DocumentAlreadyInSessionError,
    SessionTabLimitExceededError,
    validate_session_tab_capacity,
)
from core.services.exa_resolver import InMemoryAcademicResolverAdapter
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import delete, func, select
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

        cur_docs_stmt = select(SessionDocumentModel.document_id).where(
            SessionDocumentModel.session_id == session_id
        )
        cur_docs_res = await self.db.execute(cur_docs_stmt)
        current_doc_ids = [row[0] for row in cur_docs_res.fetchall()]

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
                page_count=1,
                content_hash=f"url_{uuid4().hex[:16]}",
                status="parsing",
            )
            self.db.add(placeholder_doc)
            await self.db.flush()
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "code": "INVALID_SOURCE_TYPE",
                    "message": "source_type phải là 'document_id' hoặc 'url'.",
                    "action": "Select valid source_type.",
                },
            )

        try:
            validate_session_tab_capacity(current_doc_ids, target_doc_id)
        except DocumentAlreadyInSessionError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": exc.code,
                    "message": exc.message,
                    "action": "Tài liệu đã tồn tại trong phiên.",
                },
            ) from exc
        except SessionTabLimitExceededError as exc:
            logger.warning(
                "session_capacity_exceeded",
                session_id=str(session_id),
                count=len(current_doc_ids),
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": exc.code,
                    "message": exc.message,
                    "action": "Vui lòng gỡ bớt bài báo trước khi nạp thêm (tối đa 5 bài).",
                },
            ) from exc

        new_link = SessionDocumentModel(
            session_id=session_id,
            document_id=target_doc_id,
            display_order=len(current_doc_ids),
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

    async def remove_document_from_session(
        self,
        session_id: UUID,
        document_id: UUID,
        user_id: UUID,
    ) -> None:
        """Remove a document from an active session and reassign active_document_id if needed."""
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

        del_stmt = delete(SessionDocumentModel).where(
            SessionDocumentModel.session_id == session_id,
            SessionDocumentModel.document_id == document_id,
        )
        del_res = await self.db.execute(del_stmt)
        if del_res.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DOCUMENT_NOT_IN_SESSION",
                    "message": "Bài báo không thuộc phiên nghiên cứu này.",
                    "action": "Verify document ID in current session.",
                },
            )

        if session.active_document_id == document_id:
            rem_stmt = (
                select(SessionDocumentModel.document_id)
                .where(SessionDocumentModel.session_id == session_id)
                .limit(1)
            )
            rem_res = await self.db.execute(rem_stmt)
            next_active_id = rem_res.scalar_one_or_none()
            session.active_document_id = next_active_id

        session.version += 1
        session.updated_at = datetime.now(UTC)
        await self.db.commit()

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
                target_stmt = select(DocumentModel).where(
                    DocumentModel.id == ref_item.resolved_document_id,
                    DocumentModel.user_id == user_id,
                )
                target_doc = (await self.db.execute(target_stmt)).scalar_one_or_none()
                if target_doc is None:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        detail={
                            "code": "REFERENCE_ENTITY_NOT_OWNED",
                            "message": (
                                "Tài liệu tham khảo đã liên kết không thuộc tenant hiện tại."
                            ),
                            "action": (
                                "Resolve the reference again before adding it to this session."
                            ),
                        },
                    )

            # A deterministic title-only fallback is displayable but is not a
            # validated academic entity and must not enter the graph.
            if not has_public_academic_identifier(resolved) and not (
                ref_item.doi or ref_item.arxiv_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail={
                        "code": "ACADEMIC_ENTITY_UNRESOLVED",
                        "message": (
                            "Không thể đưa tài liệu tham khảo vào đồ thị vì chưa có DOI "
                            "hoặc arXiv ID đã xác thực."
                        ),
                        "action": (
                            "Resolve the reference through a supported academic resolver first."
                        ),
                    },
                )

            if not target_doc:
                doc_title = resolved.title or ref_item.parsed_title or f"Reference #{ref_idx}"
                authors_val = resolved.authors or ref_item.parsed_authors or []
                target_doc = DocumentModel(
                    user_id=user_id,
                    filename=f"reference_{ref_idx}",
                    title=doc_title,
                    authors=authors_val,
                    publication_year=resolved.year or ref_item.parsed_year,
                    doi=resolved.doi or ref_item.doi,
                    # This record represents validated citation metadata only.  It
                    # is deliberately not a PDF placeholder or content hash.
                    content_hash="",
                    file_size_bytes=0,
                    status="metadata_only",
                    stage="metadata_only",
                    progress=0,
                    error_message=(
                        "Metadata-only reference: no source PDF has been ingested; "
                        "content retrieval is unavailable."
                    ),
                    is_persistent=False,
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
