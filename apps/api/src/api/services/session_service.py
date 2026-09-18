"""Session Service coordinating research sessions and multi-document associations."""

import io
import zipfile
from datetime import UTC, datetime
from uuid import UUID, uuid4

import structlog
from api.db.models.document import DocumentModel
from api.db.models.session import (
    ResearchSessionModel,
    SessionDocumentModel,
    SessionTurnModel,
)
from api.schemas.session import (
    SessionDocumentItem,
    SessionHistoryItem,
    SessionResponseData,
    ViewportStateSchema,
)
from core.domain.entities.session import MAX_SESSION_DOCUMENTS
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger("api.services.session")


class SessionService:
    """Application service managing research session lifecycles."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

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
