"""Document Ingestion Service coordinating CAS storage and database persistence."""

import hashlib
import math
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import UUID, uuid4

from api.db.models.blob import DocumentStorageBlobModel
from api.db.models.document import DocumentModel
from api.db.models.session import ResearchSessionModel, SessionDocumentModel
from api.schemas.document import (
    DocumentDetailResponseData,
    DocumentLinks,
    DocumentListItem,
    DocumentListPaginatedEnvelope,
    DocumentUploadResponseData,
    PageMetadataItem,
)
from api.schemas.envelope import PaginationLinks, PaginationMeta
from core.domain.entities.blob import MAX_FILE_SIZE_BYTES
from core.ports.storage import IBlobStoragePort
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

PDF_MAGIC_BYTES = b"%PDF-"
MAX_SESSION_DOCUMENTS = 5


class DocumentService:
    """Service handling document upload, CAS deduplication, and session attachment."""

    def __init__(self, storage: IBlobStoragePort) -> None:
        self.storage = storage

    async def upload_document(
        self,
        file: UploadFile,
        user_id: UUID,
        db: AsyncSession,
        session_id: UUID | None = None,
    ) -> DocumentUploadResponseData:
        """Process an uploaded PDF file, perform CAS deduplication, and register document record.

        Args:
            file: FastAPI UploadFile object.
            user_id: Authenticated user identifier.
            db: Active async database session.
            session_id: Optional research session to link the document to.

        Returns:
            Structured DocumentUploadResponseData.
        """
        filename = file.filename or "untitled.pdf"

        # 1. Read initial chunk to validate Magic Bytes (%PDF-)
        initial_chunk = await file.read(1024)
        if not initial_chunk.startswith(PDF_MAGIC_BYTES):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_FILE_TYPE",
                    "message": "File is not a valid PDF (missing %PDF- header magic bytes).",
                    "field": "file",
                    "action": "Ensure the uploaded file is a valid non-corrupted PDF document.",
                },
            )

        # 2. Stream and compute SHA-256 hash while enforcing 50MB ceiling
        hasher = hashlib.sha256()
        hasher.update(initial_chunk)
        total_size = len(initial_chunk)
        chunks: list[bytes] = [initial_chunk]

        while True:
            chunk = await file.read(64 * 1024)  # 64 KB buffer
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail={
                        "code": "FILE_TOO_LARGE",
                        "message": (
                            f"File exceeds maximum size limit of {MAX_FILE_SIZE_BYTES} bytes."
                        ),
                        "field": "file",
                        "action": "Compress the PDF or choose a file under 50MB.",
                    },
                )
            hasher.update(chunk)
            chunks.append(chunk)

        content_hash = hasher.hexdigest()

        # 3. Validate session if session_id is provided
        if session_id is not None:
            stmt_session = select(ResearchSessionModel).where(
                ResearchSessionModel.id == session_id,
                ResearchSessionModel.user_id == user_id,
            )
            res_session = await db.execute(stmt_session)
            session_obj = res_session.scalar_one_or_none()
            if session_obj is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "SESSION_NOT_FOUND",
                        "message": f"Research session '{session_id}' not found.",
                        "field": "session_id",
                        "action": "Verify session_id exists and belongs to the authenticated user.",
                    },
                )

            # Check max 5 documents per session
            stmt_count = (
                select(func.count())
                .select_from(SessionDocumentModel)
                .where(SessionDocumentModel.session_id == session_id)
            )
            res_count = await db.execute(stmt_count)
            current_doc_count = res_count.scalar() or 0
            if current_doc_count >= MAX_SESSION_DOCUMENTS:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": "SESSION_DOCUMENT_LIMIT_EXCEEDED",
                        "message": (
                            f"Session already has {current_doc_count} documents. "
                            f"Maximum allowed is {MAX_SESSION_DOCUMENTS}."
                        ),
                        "field": "session_id",
                        "action": "Remove a document from session before adding a new one.",
                    },
                )

        # 4. CAS Lookup: Check if blob already exists
        stmt_blob = select(DocumentStorageBlobModel).where(
            DocumentStorageBlobModel.content_hash == content_hash
        )
        res_blob = await db.execute(stmt_blob)
        blob = res_blob.scalar_one_or_none()

        now = datetime.now(UTC)

        if blob is not None:
            # Deduplicated: Increment reference count
            blob.ref_count += 1
        else:
            # Physical save via Storage Port
            async def _stream_chunks():
                for c in chunks:
                    yield c

            storage_path, _ = await self.storage.save_blob(_stream_chunks(), content_hash)

            blob = DocumentStorageBlobModel(
                id=uuid4(),
                content_hash=content_hash,
                storage_path=storage_path,
                file_size_bytes=total_size,
                ref_count=1,
                status="processing",
                created_at=now,
                updated_at=now,
            )
            db.add(blob)
            await db.flush()

        # 5. Create user Document record
        doc = DocumentModel(
            id=uuid4(),
            user_id=user_id,
            blob_id=blob.id,
            filename=filename,
            content_hash=content_hash,
            file_size_bytes=total_size,
            status="uploaded",
            stage="queued",
            progress=0,
            is_persistent=False,
            created_at=now,
            updated_at=now,
        )
        db.add(doc)
        await db.flush()

        # 6. Associate with session if requested
        if session_id is not None:
            session_doc = SessionDocumentModel(
                session_id=session_id,
                document_id=doc.id,
                added_at=now,
            )
            db.add(session_doc)
            await db.flush()

        doc_id_str = str(doc.id)
        links = DocumentLinks(
            self_url=f"/api/v1/documents/{doc_id_str}",
            status_url=f"/api/v1/documents/{doc_id_str}/status",
            file_url=f"/api/v1/documents/{doc_id_str}/file",
            parse_url=f"/api/v1/documents/{doc_id_str}:parse",
        )

        return DocumentUploadResponseData(
            id=doc.id,
            filename=doc.filename,
            file_size_bytes=doc.file_size_bytes,
            content_hash=doc.content_hash,
            status=doc.status,
            stage=doc.stage,
            progress=doc.progress,
            is_persistent=doc.is_persistent,
            session_id=session_id,
            created_at=doc.created_at,
            links=links,
        )

    async def list_documents(
        self,
        user_id: UUID,
        db: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        status_filter: str | None = None,
    ) -> DocumentListPaginatedEnvelope:
        """Retrieve paginated list of user documents conforming to RFC 8288.

        Args:
            user_id: Authenticated user identifier.
            db: Active async database session.
            page: 1-based page index.
            per_page: Number of documents per page.
            status_filter: Optional status filter.

        Returns:
            DocumentListPaginatedEnvelope with data, meta, and navigation links.
        """
        where_clauses = [DocumentModel.user_id == user_id]
        if status_filter:
            where_clauses.append(DocumentModel.status == status_filter)

        # 1. Total count query
        count_stmt = select(func.count(DocumentModel.id)).where(*where_clauses)
        count_res = await db.execute(count_stmt)
        total = count_res.scalar() or 0

        # Calculate total pages
        total_pages = max(1, math.ceil(total / per_page))

        # 2. Paginated items query
        offset = (page - 1) * per_page
        items_stmt = (
            select(DocumentModel)
            .where(*where_clauses)
            .order_by(DocumentModel.created_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        items_res = await db.execute(items_stmt)
        documents = items_res.scalars().all()

        data = [
            DocumentListItem(
                id=doc.id,
                filename=doc.filename,
                title=doc.title,
                status=doc.status,
                is_persistent=doc.is_persistent,
                created_at=doc.created_at,
            )
            for doc in documents
        ]

        # 3. Construct RFC 8288 pagination links
        def _build_url(p: int) -> str:
            if status_filter:
                return f"/api/v1/documents?page={p}&per_page={per_page}&status={status_filter}"
            return f"/api/v1/documents?page={p}&per_page={per_page}"

        first_link = _build_url(1)
        last_link = _build_url(total_pages)
        self_link = _build_url(page)
        prev_link = _build_url(page - 1) if page > 1 else None
        next_link = _build_url(page + 1) if page < total_pages else None

        meta = PaginationMeta(
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )
        links = PaginationLinks(
            first=first_link,
            prev=prev_link,
            self=self_link,
            next=next_link,
            last=last_link,
        )

        return DocumentListPaginatedEnvelope(
            success=True,
            data=data,
            meta=meta,
            links=links,
        )

    async def get_document_detail(
        self,
        document_id: UUID,
        user_id: UUID,
        db: AsyncSession,
    ) -> DocumentDetailResponseData:
        """Retrieve full details of a specific document including spatial page dimensions.

        Args:
            document_id: Unique document identifier.
            user_id: Authenticated user identifier (enforces multi-tenant isolation).
            db: Active async database session.

        Returns:
            DocumentDetailResponseData with normalized pages_metadata.

        Raises:
            HTTPException(404): When document does not exist or belongs to another user.
        """
        stmt = select(DocumentModel).where(
            DocumentModel.id == document_id,
            DocumentModel.user_id == user_id,
        )
        res = await db.execute(stmt)
        doc = res.scalar_one_or_none()

        if doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DOCUMENT_NOT_FOUND",
                    "message": f"Document '{document_id}' not found.",
                    "field": "id",
                    "action": "Verify document ID or check permissions.",
                },
            )

        # Normalize pages_metadata
        normalized_pages: list[PageMetadataItem] = []
        if doc.pages_metadata:
            for p in doc.pages_metadata:
                if isinstance(p, dict):
                    if "dimensions" in p:
                        dims = [float(d) for d in p["dimensions"]]
                    elif "width_pt" in p and "height_pt" in p:
                        dims = [float(p["width_pt"]), float(p["height_pt"])]
                    else:
                        dims = [0.0, 0.0]
                    page_num = p.get("page_number") or p.get("page", 1)
                    rotation = p.get("rotation_deg", 0)
                    normalized_pages.append(
                        PageMetadataItem(
                            page_number=int(page_num),
                            dimensions=dims,
                            rotation_deg=int(rotation),
                        )
                    )
                elif isinstance(p, (list, tuple)) and len(p) >= 3:
                    page_num = int(p[0])
                    width = float(p[1])
                    height = float(p[2])
                    rotation = int(p[3]) if len(p) > 3 else 0
                    normalized_pages.append(
                        PageMetadataItem(
                            page_number=page_num,
                            dimensions=[width, height],
                            rotation_deg=rotation,
                        )
                    )

        return DocumentDetailResponseData(
            id=doc.id,
            filename=doc.filename,
            title=doc.title,
            authors=doc.authors,
            publication_year=doc.publication_year,
            doi=doc.doi,
            page_count=doc.page_count,
            chunk_count=doc.chunk_count,
            file_size_bytes=doc.file_size_bytes,
            status=doc.status,
            is_persistent=doc.is_persistent,
            pages_metadata=normalized_pages,
            created_at=doc.created_at,
        )

    async def get_document_file_stream(
        self,
        document_id: UUID,
        user_id: UUID,
        db: AsyncSession,
        range_header: str | None = None,
    ) -> tuple[AsyncIterator[bytes], dict[str, str], int]:
        """Prepare binary stream and HTTP headers for document PDF streaming.

        Supports HTTP 206 Partial Content (Range header) for Web Canvas lazy-loading.

        Args:
            document_id: Unique document identifier.
            user_id: Authenticated user identifier (enforces multi-tenant scoping).
            db: Active async database session.
            range_header: Optional HTTP 'Range' header string, e.g. 'bytes=0-1024'.

        Returns:
            Tuple of (async_byte_iterator, response_headers_dict, http_status_code).

        Raises:
            HTTPException(404): When document or physical file blob is not found.
            HTTPException(416): When requested byte range is unsatisfiable.
        """
        stmt = select(DocumentModel).where(
            DocumentModel.id == document_id,
            DocumentModel.user_id == user_id,
        )
        res = await db.execute(stmt)
        doc = res.scalar_one_or_none()

        if doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DOCUMENT_NOT_FOUND",
                    "message": f"Document '{document_id}' not found.",
                    "field": "id",
                    "action": "Verify document ID or check permissions.",
                },
            )

        content_hash = doc.content_hash
        if not await self.storage.blob_exists(content_hash):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "FILE_NOT_FOUND",
                    "message": f"Underlying physical file for document '{document_id}' not found.",
                    "field": "content_hash",
                    "action": "Re-upload document file.",
                },
            )

        file_size = doc.file_size_bytes
        safe_filename = doc.filename.replace('"', '"')

        headers = {
            "Content-Type": "application/pdf",
            "Accept-Ranges": "bytes",
            "Content-Disposition": f'inline; filename="{safe_filename}"',
        }

        # Full file streaming (no Range header)
        if not range_header:
            headers["Content-Length"] = str(file_size)
            stream = self.storage.stream_blob_range(content_hash, start_byte=0, end_byte=None)
            return stream, headers, status.HTTP_200_OK

        # Parse HTTP Range header (RFC 9110)
        # Standard format: 'bytes=start-end' or 'bytes=start-'
        if not range_header.startswith("bytes="):
            headers["Content-Length"] = str(file_size)
            stream = self.storage.stream_blob_range(content_hash, start_byte=0, end_byte=None)
            return stream, headers, status.HTTP_200_OK

        range_val = range_header[len("bytes=") :].strip()
        parts = range_val.split("-")

        try:
            if len(parts) != 2:
                raise ValueError("Invalid range parts count")

            start_str, end_str = parts[0].strip(), parts[1].strip()

            if start_str and end_str:
                start = int(start_str)
                end = int(end_str)
            elif start_str and not end_str:
                start = int(start_str)
                end = file_size - 1
            elif not start_str and end_str:
                # Suffix byte range: e.g. bytes=-500 means last 500 bytes
                suffix_len = int(end_str)
                start = max(0, file_size - suffix_len)
                end = file_size - 1
            else:
                raise ValueError("Both start and end omitted")

            if start < 0 or start >= file_size or start > end:
                raise ValueError("Unsatisfiable range boundary")

            # Cap end at file_size - 1
            end = min(end, file_size - 1)
            content_length = (end - start) + 1

            headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
            headers["Content-Length"] = str(content_length)

            stream = self.storage.stream_blob_range(content_hash, start_byte=start, end_byte=end)
            return stream, headers, status.HTTP_206_PARTIAL_CONTENT

        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_416_RANGE_NOT_SATISFIABLE,
                headers={"Content-Range": f"bytes */{file_size}"},
                detail={
                    "code": "RANGE_NOT_SATISFIABLE",
                    "message": f"Range '{range_header}' unsatisfiable for size {file_size}B.",
                    "field": "Range",
                    "action": f"Ensure byte range is within 0 to {file_size - 1}.",
                },
            )
