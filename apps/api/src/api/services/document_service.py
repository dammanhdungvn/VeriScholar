"""Document Ingestion Service coordinating CAS storage and database persistence."""

import asyncio
import hashlib
import json
import logging
import math
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import httpx
from api.adapters.chunk_extractor import PyMuPDFChunkExtractor
from api.adapters.heuristic_summarizer import HeuristicGroundedSummarizer
from api.adapters.pdf_structure_extractor import PyMuPDFStructureExtractor
from api.db.models.blob import DocumentStorageBlobModel
from api.db.models.chunk import DocumentChunkModel
from api.db.models.document import DocumentModel
from api.db.models.folder import FolderModel
from api.db.models.reference import ReferenceItemModel
from api.db.models.session import ResearchSessionModel, SessionDocumentModel
from api.db.models.summary import DocumentSummaryModel
from api.schemas.document import (
    DocumentChunkDetailData,
    DocumentChunkDetailEnvelope,
    DocumentChunkItem,
    DocumentChunkNavigationLinks,
    DocumentChunkPaginatedEnvelope,
    DocumentDetailResponseData,
    DocumentExtractReferencesResponseData,
    DocumentLinks,
    DocumentListItem,
    DocumentListPaginatedEnvelope,
    DocumentParseLinks,
    DocumentParseRequest,
    DocumentParseResponseData,
    DocumentResolveReferencesResponseData,
    DocumentSectionResponse,
    DocumentStarResponseData,
    DocumentStatusResponseData,
    DocumentStructureData,
    DocumentSummaryData,
    DocumentSummaryEnvelope,
    DocumentUploadResponseData,
    PageMetadataItem,
    ParsedReferenceItemSchema,
    ReferenceItemResponse,
    ResolvedAcademicReferenceResponse,
    StagesDetail,
    SummaryPointResponse,
)
from api.schemas.envelope import PaginationLinks, PaginationMeta
from api.services.ai_tracing_service import AITracingService
from api.services.embedding_service import EmbeddingService
from core.domain.entities.blob import MAX_FILE_SIZE_BYTES
from core.domain.entities.chunk import DocumentChunk
from core.domain.entities.reference import (
    ExtractedReference,
    ParsedReferenceInfo,
    extract_references_from_text,
)
from core.domain.value_objects.bounding_box import BoundingBox
from core.domain.value_objects.enums import BlobStatus, DocumentStage, DocumentStatus
from core.ports.academic_resolver import IAcademicSearchResolverPort
from core.ports.chunk import IChunkExtractorPort
from core.ports.storage import IBlobStoragePort
from core.ports.structure import IStructureExtractorPort
from core.ports.summary import IDocumentSummarizerPort
from core.services.document_validator import AcademicPaperValidator
from core.services.exa_resolver import InMemoryAcademicResolverAdapter
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import delete, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

PDF_MAGIC_BYTES = b"%PDF-"
MAX_SESSION_DOCUMENTS = 5


@asynccontextmanager
async def _safe_nested_transaction(db: Any) -> AsyncIterator[None]:
    """Execute within a savepoint if supported, suppressing duplicate key errors safely."""
    if hasattr(db, "begin_nested"):
        try:
            async with db.begin_nested():
                yield
        except IntegrityError:
            pass
    else:
        yield


class DocumentService:
    """Service handling document upload, CAS deduplication, and session attachment."""

    def __init__(
        self,
        storage: IBlobStoragePort,
        structure_extractor: IStructureExtractorPort | None = None,
        chunk_extractor: IChunkExtractorPort | None = None,
        summarizer: IDocumentSummarizerPort | None = None,
        ai_tracing: AITracingService | None = None,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        self.storage = storage
        self.structure_extractor = structure_extractor or PyMuPDFStructureExtractor()
        self.chunk_extractor = chunk_extractor or PyMuPDFChunkExtractor()
        self.summarizer = (
            summarizer
            if (summarizer is not None and not hasattr(summarizer, "dependency"))
            else HeuristicGroundedSummarizer()
        )
        self.ai_tracing = (
            ai_tracing
            if (ai_tracing is not None and not hasattr(ai_tracing, "dependency"))
            else AITracingService()
        )
        self.embedding_service = (
            embedding_service
            if (embedding_service is not None and not hasattr(embedding_service, "dependency"))
            else None
        )

    def _get_or_init_embedding_service(self) -> EmbeddingService | None:
        """Get or lazily initialize the EmbeddingService."""
        if self.embedding_service is not None and not hasattr(self.embedding_service, "dependency"):
            return self.embedding_service
        try:
            self.embedding_service = EmbeddingService()
            return self.embedding_service
        except Exception:
            return None

    async def _generate_chunk_embeddings(self, chunks: list[Any]) -> list[list[float] | None]:
        """Generate 1536-dimensional embeddings for chunks using EmbeddingService.

        Handles missing keys, offline environment, or API errors gracefully by returning None.
        """
        if not chunks:
            return []
        texts = [getattr(c, "content", getattr(c, "text", str(c))) for c in chunks]
        emb_svc = self._get_or_init_embedding_service()
        if emb_svc is not None:
            try:
                embeddings = await emb_svc.get_embeddings_batch(texts)
                if len(embeddings) == len(chunks):
                    return embeddings
            except Exception as e:
                logger.warning(
                    "Failed to generate chunk embeddings batch: %s",
                    str(e),
                )
        return [None] * len(chunks)

    async def _build_chunk_models(
        self,
        extracted_chunks: list[Any],
        user_id: UUID,
        document_id: UUID,
        now: datetime,
    ) -> list[DocumentChunkModel]:
        """Build DocumentChunkModel instances with computed embeddings."""
        embeddings = await self._generate_chunk_embeddings(extracted_chunks)
        return [
            DocumentChunkModel(
                id=ec.id,
                user_id=user_id,
                document_id=document_id,
                chunk_index=ec.chunk_index,
                page_number=ec.page_number,
                content=ec.content,
                bounding_boxes=ec.bounding_boxes_raw,
                token_count=ec.token_count,
                embedding=embeddings[i] if embeddings and i < len(embeddings) else None,
                created_at=now,
                updated_at=now,
            )
            for i, ec in enumerate(extracted_chunks)
        ]

    @staticmethod
    def _extract_summary_metadata(
        problem_statement: str,
        contributions: str,
        limitations: str,
        chunks: list[Any] | None = None,
        abstract: str | None = None,
    ) -> dict[str, list[str]]:
        """Extract the 4-pillar Summary Index for Macro RAG retrieval.

        1. original_problem: Core bottlenecks of prior methods.
        2. proposed_solution: Breakthrough architecture & technical solutions.
        3. key_insights: Foundational theoretical contributions.
        4. quantitative_results: Empirical quantitative metrics (BLEU, F1, Loss, etc.).
        """

        def split_points(text: str) -> list[str]:
            if not text or not text.strip():
                return []
            lines = [
                line.strip().lstrip("-•*0123456789.) ").strip()
                for line in text.split("\n")
                if line.strip()
            ]
            if not lines:
                lines = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
            return [line for line in lines if len(line) > 10]

        original_problem = split_points(problem_statement)
        if not original_problem and abstract:
            original_problem = [abstract[:300]]
        if not original_problem:
            original_problem = ["No explicit problem statement identified."]

        proposed_solution = split_points(contributions)
        if not proposed_solution and abstract:
            proposed_solution = [abstract[:300]]
        if not proposed_solution:
            proposed_solution = ["No explicit proposed solution identified."]

        key_insights = split_points(limitations)
        if not key_insights:
            key_insights = proposed_solution[:2]

        quantitative_results: list[str] = []
        metric_pattern = re.compile(
            r"(\b\d+(\.\d+)?%|\bF1\b|\bBLEU\b|\baccuracy\b|\bPearson\b|\bSpearman\b|\bp\s*[<=]\s*0\.\d+|\bAUC\b|\bprecision\b|\brecall\b|\bSOTA\b)",
            re.IGNORECASE,
        )
        all_texts: list[str] = []
        if abstract:
            all_texts.append(abstract)
        if chunks:
            for c in chunks:
                content = getattr(c, "content", "")
                if content:
                    all_texts.append(content)

        for text_block in all_texts:
            sentences = re.split(r"(?<=[.!?])\s+", text_block)
            for s in sentences:
                s_clean = s.strip()
                if len(s_clean) > 20 and metric_pattern.search(s_clean):
                    if s_clean not in quantitative_results:
                        quantitative_results.append(s_clean)
                    if len(quantitative_results) >= 5:
                        break
            if len(quantitative_results) >= 5:
                break

        if not quantitative_results:
            quantitative_results = ["Empirical evaluation results detailed in publication tables."]

        return {
            "original_problem": original_problem,
            "proposed_solution": proposed_solution,
            "key_insights": key_insights,
            "quantitative_results": quantitative_results,
        }

    async def parse_document_background(
        self,
        document_id: UUID,
        user_id: UUID,
    ) -> None:
        """Background worker to extract chunks, compute vector embeddings, and build summary index.

        Runs asynchronously via FastAPI BackgroundTasks outside the HTTP request lifecycle.
        Creates its own isolated AsyncSessionLocal database transaction.
        """
        from api.db.session import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            stmt = select(DocumentModel).where(
                DocumentModel.id == document_id,
                DocumentModel.user_id == user_id,
            )
            try:
                # 1. Fetch document record
                res = await session.execute(stmt)
                doc = res.scalar_one_or_none()
                if not doc:
                    logger.warning(
                        "Document not found for background parsing: %s",
                        str(document_id),
                    )
                    return

                # 2. Check physical PDF blob
                if not doc.content_hash or not (await self.storage.blob_exists(doc.content_hash)):
                    logger.warning(
                        "Physical blob not found for background parsing: %s",
                        str(document_id),
                    )
                    return

                # 3. Transition stage to processing / chunking
                now = datetime.now(UTC)
                doc.status = DocumentStatus.PROCESSING.value
                doc.stage = DocumentStage.CHUNKING.value
                doc.progress = 30
                doc.updated_at = now
                await session.commit()

                # Re-fetch document in active session
                res = await session.execute(stmt)
                doc = res.scalar_one_or_none()
                if not doc:
                    return

                pdf_bytes = await self.storage.read_blob(doc.content_hash)

                # 4. Check existing chunks
                count_stmt = (
                    select(func.count())
                    .select_from(DocumentChunkModel)
                    .where(DocumentChunkModel.document_id == document_id)
                )
                count_res = await session.execute(count_stmt)
                existing_count = count_res.scalar() or 0

                chunk_models: list[DocumentChunkModel] = []
                if existing_count == 0:
                    parse_opts = (doc.parsed_metadata or {}).get("parse_options", {})
                    c_size = parse_opts.get("chunk_size", 512)
                    c_overlap = parse_opts.get("chunk_overlap", 50)
                    extracted_chunks = await asyncio.to_thread(
                        self.chunk_extractor.extract_chunks,
                        pdf_bytes,
                        doc.id,
                        c_size,
                        c_overlap,
                    )
                    if extracted_chunks:
                        now = datetime.now(UTC)
                        chunk_models = await self._build_chunk_models(
                            extracted_chunks, doc.user_id, doc.id, now
                        )
                        async with _safe_nested_transaction(session):
                            session.add_all(chunk_models)
                            doc.chunk_count = len(chunk_models)
                            await session.flush()
                else:
                    stmt_chunks = (
                        select(DocumentChunkModel)
                        .where(DocumentChunkModel.document_id == document_id)
                        .order_by(DocumentChunkModel.chunk_index.asc())
                    )
                    chunk_models = list((await session.execute(stmt_chunks)).scalars().all())

                # 5. Backfill embeddings if any chunks lack them
                missing_chunks = [c for c in chunk_models if c.embedding is None]
                if missing_chunks:
                    emb_svc = self._get_or_init_embedding_service()
                    if emb_svc is not None:
                        try:
                            texts = [c.content for c in missing_chunks]
                            embs = await emb_svc.get_embeddings_batch(texts)
                            for c, emb in zip(missing_chunks, embs):
                                if emb is not None:
                                    c.embedding = emb
                            await session.flush()
                        except Exception as e:
                            logger.warning(
                                "Failed generating embeddings in background parsing: %s",
                                str(e),
                            )

                # 6. Extract summary & 4-pillar Summary Index
                try:
                    await self._precompute_summary_if_missing(
                        doc=doc,
                        chunk_models=chunk_models,
                        pdf_bytes=pdf_bytes,
                        db=session,
                    )
                except Exception as e:
                    logger.warning(
                        "Failed precomputing summary in background parse: %s",
                        str(e),
                    )

                # 7. Finalize document state
                doc.status = DocumentStatus.COMPLETED.value
                doc.stage = DocumentStage.COMPLETED.value
                doc.progress = 100
                doc.updated_at = datetime.now(UTC)
                await session.commit()
                logger.info(
                    "Background parsing completed successfully: %s",
                    str(document_id),
                )

            except Exception as exc:
                logger.exception(
                    "Error during background parsing of document: %s",
                    str(document_id),
                )
                try:
                    await session.rollback()
                    res = await session.execute(stmt)
                    failed_doc = res.scalar_one_or_none()
                    if failed_doc:
                        failed_doc.status = DocumentStatus.FAILED.value
                        failed_doc.error_message = str(exc)
                        failed_doc.updated_at = datetime.now(UTC)
                        await session.commit()
                except Exception:
                    pass

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
            # Self-healing: Ensure physical file exists in storage
            if not await self.storage.blob_exists(content_hash):

                async def _stream_chunks_repair():
                    for c in chunks:
                        yield c

                await self.storage.save_blob(_stream_chunks_repair(), content_hash)
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
                status=BlobStatus.PROCESSING.value,
                created_at=now,
                updated_at=now,
            )
            try:
                db.add(blob)
                await db.flush()
            except IntegrityError:
                # Concurrent CAS race condition: another worker inserted the blob just now
                await db.rollback()
                res_blob = await db.execute(stmt_blob)
                blob = res_blob.scalar_one_or_none()
                if blob is not None:
                    blob.ref_count += 1
                else:
                    raise

        # 5. Create user Document record
        doc = DocumentModel(
            id=uuid4(),
            user_id=user_id,
            blob_id=blob.id,
            filename=filename,
            content_hash=content_hash,
            file_size_bytes=total_size,
            chunk_count=0,
            pages_metadata=[],
            status=DocumentStatus.UPLOADED.value,
            stage=DocumentStage.QUEUED.value,
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

    async def attach_pdf(
        self,
        document_id: UUID,
        file: UploadFile,
        user_id: UUID,
        db: AsyncSession,
    ) -> DocumentUploadResponseData:
        """Attach a full PDF file to an existing abstract_only document, performing CAS dedup."""
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
                    "field": "document_id",
                },
            )

        initial_chunk = await file.read(1024)
        if not initial_chunk.startswith(PDF_MAGIC_BYTES):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_FILE_TYPE",
                    "message": "File is not a valid PDF (missing %PDF- header magic bytes).",
                    "field": "file",
                },
            )

        hasher = hashlib.sha256()
        hasher.update(initial_chunk)
        total_size = len(initial_chunk)
        chunks: list[bytes] = [initial_chunk]

        while True:
            chunk = await file.read(64 * 1024)
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
                    },
                )
            hasher.update(chunk)
            chunks.append(chunk)

        content_hash = hasher.hexdigest()

        # CAS Blob Check
        stmt_blob = select(DocumentStorageBlobModel).where(
            DocumentStorageBlobModel.content_hash == content_hash
        )
        res_blob = await db.execute(stmt_blob)
        blob = res_blob.scalar_one_or_none()

        if blob is not None:
            blob.ref_count += 1
        else:

            async def _stream_chunks():
                for c in chunks:
                    yield c

            storage_path, _ = await self.storage.save_blob(_stream_chunks(), content_hash)
            blob = DocumentStorageBlobModel(
                id=uuid4(),
                content_hash=content_hash,
                storage_path=storage_path,
                file_size_bytes=total_size,
                mime_type="application/pdf",
                ref_count=1,
            )
            db.add(blob)
            await db.flush()

        doc.blob_id = blob.id
        doc.content_hash = content_hash
        doc.file_size_bytes = total_size
        doc.status = "parsing"
        doc.stage = "queued"
        doc.progress = 0
        doc.access_status = "open_access_pdf"
        if file.filename:
            doc.filename = file.filename

        await db.commit()

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
            created_at=doc.created_at,
            links=links,
            access_status=doc.access_status,
        )

    async def ingest_pdf_from_url(
        self,
        pdf_url: str,
        db: AsyncSession | None = None,
    ) -> tuple[str, int] | None:
        """Download external open-access PDF, validate, and register into CAS storage.

        Args:
            pdf_url: Remote URL pointing to open-access PDF (e.g. arXiv, Unpaywall).
            db: Optional active async database session to persist CAS blob record.

        Returns:
            Tuple of (content_hash, file_size_bytes) on success, or None on failure.
        """
        clean_url = pdf_url.strip()
        if not clean_url.startswith(("http://", "https://")):
            return None

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(clean_url)
                if response.status_code != 200:
                    logger.warning(
                        "PDF download returned non-200 status %d from %s",
                        response.status_code,
                        clean_url,
                    )
                    return None

                content = getattr(response, "content", b"")
                if not content:
                    if hasattr(response, "aiter_bytes"):
                        chunks_acc: list[bytes] = []
                        async for c in response.aiter_bytes():
                            chunks_acc.append(c)
                        content = b"".join(chunks_acc)
                    elif hasattr(response, "iter_bytes"):
                        content = b"".join(response.iter_bytes())

                if len(content) > MAX_FILE_SIZE_BYTES:
                    logger.warning(
                        "PDF download exceeds MAX_FILE_SIZE_BYTES (%d bytes) from %s",
                        len(content),
                        clean_url,
                    )
                    return None

                if not content.startswith(PDF_MAGIC_BYTES):
                    logger.warning(
                        "Downloaded payload from %s missing %%PDF- magic bytes",
                        clean_url,
                    )
                    return None

                content_hash = hashlib.sha256(content).hexdigest()
                file_size_bytes = len(content)

                chunk_size = 64 * 1024
                chunks = [content[i : i + chunk_size] for i in range(0, len(content), chunk_size)]

                async def _stream_chunks():
                    for chunk in chunks:
                        yield chunk

                storage_path, _ = await self.storage.save_blob(_stream_chunks(), content_hash)

                if db is not None:
                    stmt_blob = select(DocumentStorageBlobModel).where(
                        DocumentStorageBlobModel.content_hash == content_hash
                    )
                    res_blob = await db.execute(stmt_blob)
                    blob = res_blob.scalar_one_or_none()

                    now = datetime.now(UTC)
                    if blob is not None:
                        blob.ref_count += 1
                        if not await self.storage.blob_exists(content_hash):

                            async def _stream_chunks_repair():
                                for chunk in chunks:
                                    yield chunk

                            await self.storage.save_blob(_stream_chunks_repair(), content_hash)
                    else:
                        blob = DocumentStorageBlobModel(
                            id=uuid4(),
                            content_hash=content_hash,
                            storage_path=storage_path,
                            file_size_bytes=file_size_bytes,
                            ref_count=1,
                            status=BlobStatus.COMPLETED.value,
                            created_at=now,
                            updated_at=now,
                        )
                        try:
                            async with _safe_nested_transaction(db):
                                db.add(blob)
                                await db.flush()
                        except IntegrityError:
                            res_blob = await db.execute(stmt_blob)
                            blob = res_blob.scalar_one_or_none()
                            if blob is not None:
                                blob.ref_count += 1

                return content_hash, file_size_bytes
        except Exception as exc:
            logger.warning("Exception during PDF ingestion from %s: %s", clean_url, exc)
            return None

    async def list_documents(
        self,
        user_id: UUID,
        db: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        status_filter: str | None = None,
        search: str | None = None,
        star: bool | None = None,
    ) -> DocumentListPaginatedEnvelope:
        """Retrieve paginated list of user documents conforming to RFC 8288.

        Args:
            user_id: Authenticated user identifier.
            db: Active async database session.
            page: 1-based page index.
            per_page: Number of documents per page.
            status_filter: Optional status filter.
            search: Optional search keyword matching title or filename.
            star: Optional boolean filter for persistent/starred documents.

        Returns:
            DocumentListPaginatedEnvelope with data, meta, and navigation links.
        """
        where_clauses = [DocumentModel.user_id == user_id]
        if status_filter:
            where_clauses.append(DocumentModel.status == status_filter)
        if star is not None:
            where_clauses.append(DocumentModel.is_persistent == star)
        if search and search.strip():
            term = f"%{search.strip()}%"
            where_clauses.append(
                or_(
                    DocumentModel.title.ilike(term),
                    DocumentModel.filename.ilike(term),
                )
            )

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
            url = f"/api/v1/documents?page={p}&per_page={per_page}"
            if status_filter:
                url += f"&status={status_filter}"
            if search and search.strip():
                url += f"&search={search.strip()}"
            if star is not None:
                url += f"&star={str(star).lower()}"
            return url

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
            chunk_count=doc.chunk_count or 0,
            file_size_bytes=doc.file_size_bytes,
            status=doc.status,
            is_persistent=doc.is_persistent,
            folder_id=doc.folder_id,
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

        if doc.access_status == "abstract_only":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DOCUMENT_ABSTRACT_ONLY",
                    "message": (
                        f"Document '{document_id}' is abstract-only and has no PDF file attached."
                    ),
                    "field": "access_status",
                    "action": "Attach a PDF file to enable full-text reading.",
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
            "ETag": f'"{content_hash}"',
            "Cache-Control": "public, max-age=86400, immutable",
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

    @staticmethod
    def _compute_stages_detail(
        status_val: str,
        stage_val: str,
        parsed_metadata: dict | None = None,
    ) -> StagesDetail:
        """Compute or extract the 5-stage ingestion pipeline progress breakdown."""
        if status_val == DocumentStatus.COMPLETED.value:
            return StagesDetail(
                validation="completed",
                layout_detection="completed",
                ocr="completed",
                chunking="completed",
                embedding="completed",
            )

        if (
            parsed_metadata
            and isinstance(parsed_metadata, dict)
            and "stages_detail" in parsed_metadata
        ):
            stored = parsed_metadata["stages_detail"]
            if isinstance(stored, dict):
                return StagesDetail(
                    validation=stored.get("validation", "pending"),
                    layout_detection=stored.get("layout_detection", "pending"),
                    ocr=stored.get("ocr", "pending"),
                    chunking=stored.get("chunking", "pending"),
                    embedding=stored.get("embedding", "pending"),
                )

        pipeline_order = ["validation", "layout_detection", "ocr", "chunking", "embedding"]
        stage_norm = stage_val.lower().strip()
        stage_map = {
            "validation": 0,
            "layout_detection": 1,
            "running_ocr": 2,
            "ocr": 2,
            "parsing": 2,
            "chunking": 3,
            "embedding": 4,
        }

        if status_val == DocumentStatus.FAILED.value:
            curr_idx = stage_map.get(stage_norm, 0)
            details = {}
            for i, st in enumerate(pipeline_order):
                if i < curr_idx:
                    details[st] = "completed"
                elif i == curr_idx:
                    details[st] = "failed"
                else:
                    details[st] = "pending"
            return StagesDetail(**details)

        if (
            status_val in (DocumentStatus.UPLOADED.value, DocumentStatus.PENDING.value)
            and stage_norm == DocumentStage.QUEUED.value
        ):
            return StagesDetail(
                validation="pending",
                layout_detection="pending",
                ocr="pending",
                chunking="pending",
                embedding="pending",
            )

        curr_idx = stage_map.get(stage_norm, 0)
        details = {}
        for i, st in enumerate(pipeline_order):
            if i < curr_idx:
                details[st] = "completed"
            elif i == curr_idx:
                details[st] = "in_progress"
            else:
                details[st] = "pending"
        return StagesDetail(**details)

    async def get_document_status(
        self,
        document_id: UUID,
        user_id: UUID,
        db: AsyncSession,
    ) -> DocumentStatusResponseData:
        """Query document processing progress and stage detail.

        Args:
            document_id: Unique document identifier.
            user_id: Authenticated user identifier (enforces multi-tenant scoping).
            db: Active async database session.

        Returns:
            DocumentStatusResponseData containing status, stage, progress and stages_detail.

        Raises:
            HTTPException(404): When document is not found or not owned by user.
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

        # If document is actively processing and physical PDF blob exists,
        # ensure layout chunking completes
        if doc.status == DocumentStatus.PROCESSING.value and doc.content_hash:
            if await self.storage.blob_exists(doc.content_hash):
                count_existing_stmt = (
                    select(func.count())
                    .select_from(DocumentChunkModel)
                    .where(DocumentChunkModel.document_id == document_id)
                )
                count_res = await db.execute(count_existing_stmt)
                existing_count = count_res.scalar() or 0

                if existing_count == 0:
                    pdf_bytes = await self.storage.read_blob(doc.content_hash)
                    parse_opts = (doc.parsed_metadata or {}).get("parse_options", {})
                    c_size = parse_opts.get("chunk_size", 512)
                    c_overlap = parse_opts.get("chunk_overlap", 50)
                    extracted_chunks = await asyncio.to_thread(
                        self.chunk_extractor.extract_chunks,
                        pdf_bytes,
                        doc.id,
                        c_size,
                        c_overlap,
                    )
                    if extracted_chunks:
                        now = datetime.now(UTC)
                        chunk_models = await self._build_chunk_models(
                            extracted_chunks, doc.user_id, doc.id, now
                        )
                        try:
                            async with _safe_nested_transaction(db):
                                db.add_all(chunk_models)
                                doc.chunk_count = len(chunk_models)
                                doc.status = DocumentStatus.COMPLETED.value
                                doc.stage = DocumentStage.COMPLETED.value
                                doc.progress = 100
                                doc.updated_at = now
                                await db.flush()
                        except Exception:
                            logger.exception(
                                "Failed to persist document chunks for %s", document_id
                            )

                        # Ensure doc is active and unexpired
                        res = await db.execute(stmt)
                        fresh_doc = res.scalar_one_or_none()
                        if fresh_doc is not None:
                            doc = fresh_doc
                else:
                    doc.chunk_count = existing_count
                    doc.status = DocumentStatus.COMPLETED.value
                    doc.stage = DocumentStage.COMPLETED.value
                    doc.progress = 100
                    doc.updated_at = datetime.now(UTC)
                    await db.flush()

        stages_detail = self._compute_stages_detail(
            status_val=doc.status,
            stage_val=doc.stage,
            parsed_metadata=doc.parsed_metadata,
        )

        return DocumentStatusResponseData(
            id=doc.id,
            status=doc.status,
            stage=doc.stage,
            progress=doc.progress,
            stages_detail=stages_detail,
            error_message=doc.error_message,
        )

    async def star_document(
        self,
        document_id: UUID,
        user_id: UUID,
        db: AsyncSession,
        folder_id: UUID | None = None,
        toggle: bool = False,
    ) -> DocumentStarResponseData:
        """Promote a document to persistent library retention in an atomic ACID transaction.

        Args:
            document_id: Unique document identifier.
            user_id: Authenticated user identifier (enforces multi-tenant isolation).
            db: Active async database session.
            folder_id: Optional folder identifier to associate the starred document with.
            toggle: If True, toggles persistent star status
                (starred -> unstarred, unstarred -> starred).

        Returns:
            DocumentStarResponseData with current is_persistent state and assigned folder_id.

        Raises:
            HTTPException(404): If folder does not exist or document does not exist/belong to user.
        """
        # 1. Validate folder ownership if provided
        if folder_id is not None:
            folder_stmt = select(FolderModel).where(
                FolderModel.id == folder_id,
                FolderModel.user_id == user_id,
            )
            folder_res = await db.execute(folder_stmt)
            folder = folder_res.scalar_one_or_none()
            if folder is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "FOLDER_NOT_FOUND",
                        "message": f"Folder '{folder_id}' not found or access denied.",
                        "field": "folder_id",
                        "action": "Verify folder ID or check user permissions.",
                    },
                )

        # 2. Query document with multi-tenant scoping
        doc_stmt = select(DocumentModel).where(
            DocumentModel.id == document_id,
            DocumentModel.user_id == user_id,
        )
        doc_res = await db.execute(doc_stmt)
        doc = doc_res.scalar_one_or_none()

        if doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DOCUMENT_NOT_FOUND",
                    "message": f"Document '{document_id}' not found.",
                    "field": "id",
                    "action": "Verify document ID or check access permissions.",
                },
            )

        # 3. Update persistence and folder association atomically
        now = datetime.now(UTC)
        if toggle:
            doc.is_persistent = not doc.is_persistent
            if not doc.is_persistent:
                doc.folder_id = None
            elif folder_id is not None:
                doc.folder_id = folder_id
        else:
            doc.is_persistent = True
            doc.folder_id = folder_id

        doc.updated_at = now
        await db.flush()

        return DocumentStarResponseData(
            id=doc.id,
            filename=doc.filename,
            title=doc.title,
            status=doc.status,
            is_persistent=doc.is_persistent,
            folder_id=doc.folder_id,
            updated_at=doc.updated_at,
        )

    async def toggle_star(
        self,
        document_id: UUID,
        user_id: UUID,
        db: AsyncSession,
    ) -> DocumentStarResponseData:
        """Toggle persistent library retention status of a document."""
        return await self.star_document(
            document_id=document_id,
            user_id=user_id,
            db=db,
            folder_id=None,
            toggle=True,
        )

    async def delete_document(
        self,
        document_id: UUID,
        user_id: UUID,
        db: AsyncSession,
    ) -> bool:
        """Purge a document according to Zero-Retention Guarantee & CAS Multi-Tenant Invariant.

        1. Enforce multi-tenant scoping: Document must exist and belong to `user_id`.
        2. Delete `DocumentModel` record (PostgreSQL cascades child chunks/vectors/sessions).
        3. Inspect associated CAS `DocumentStorageBlobModel`:
           - Decrement `blob.ref_count -= 1`.
           - If `blob.ref_count <= 0`:
             - Remove blob row from database.
             - Permanently delete underlying physical binary file from storage.
        4. Flush database changes.

        Args:
            document_id: Unique document identifier to delete.
            user_id: Authenticated user identifier (enforces multi-tenant isolation).
            db: Active async database session.

        Raises:
            HTTPException(404): When document does not exist or belongs to another user.
        """
        # 1. Query document with multi-tenant scoping
        doc_stmt = select(DocumentModel).where(
            DocumentModel.id == document_id,
            DocumentModel.user_id == user_id,
        )
        doc_res = await db.execute(doc_stmt)
        doc = doc_res.scalar_one_or_none()

        if doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DOCUMENT_NOT_FOUND",
                    "message": f"Document '{document_id}' not found.",
                    "field": "id",
                    "action": "Verify document ID or check access permissions.",
                },
            )

        blob_id = doc.blob_id
        content_hash = doc.content_hash

        # 2. Delete document entity from PostgreSQL
        await db.delete(doc)

        # 3. Handle CAS blob reference counting and physical purge
        blob = None
        if blob_id is not None:
            blob_stmt = select(DocumentStorageBlobModel).where(
                DocumentStorageBlobModel.id == blob_id
            )
            blob_res = await db.execute(blob_stmt)
            blob = blob_res.scalar_one_or_none()
        elif content_hash:
            blob_stmt = select(DocumentStorageBlobModel).where(
                DocumentStorageBlobModel.content_hash == content_hash
            )
            blob_res = await db.execute(blob_stmt)
            blob = blob_res.scalar_one_or_none()

        purged_physical = False
        if blob is not None:
            blob.ref_count -= 1
            if blob.ref_count <= 0:
                await db.delete(blob)
                await self.storage.delete_blob(content_hash)
                purged_physical = True

        await db.commit()
        return purged_physical

    async def trigger_parse_document(
        self,
        document_id: UUID,
        user_id: UUID,
        parse_req: DocumentParseRequest,
        db: AsyncSession,
    ) -> DocumentParseResponseData:
        """Trigger or re-trigger parsing pipeline for an uploaded document.

        Args:
            document_id: Unique document identifier.
            user_id: Authenticated user identifier (enforces multi-tenant isolation).
            parse_req: Parsing options (chunk_size, chunk_overlap, extract_tables, etc.).
            db: Active async database session.

        Returns:
            DocumentParseResponseData with status, stage, progress and navigation links.

        Raises:
            HTTPException(404): When document not found or belongs to another user.
            HTTPException(409): When document is currently processing and force_reparse=False.
        """
        # 1. Query document with multi-tenant scoping
        doc_stmt = select(DocumentModel).where(
            DocumentModel.id == document_id,
            DocumentModel.user_id == user_id,
        )
        doc_res = await db.execute(doc_stmt)
        doc = doc_res.scalar_one_or_none()

        if doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DOCUMENT_NOT_FOUND",
                    "message": f"Document '{document_id}' not found.",
                    "field": "id",
                    "action": "Verify document ID or check access permissions.",
                },
            )

        status_url = f"/api/v1/documents/{document_id}/status"
        detail_url = f"/api/v1/documents/{document_id}"
        links = DocumentParseLinks(status_url=status_url, detail_url=detail_url)

        # 2. State machine checks
        if doc.status == DocumentStatus.PROCESSING.value and not parse_req.force_reparse:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "DOCUMENT_PROCESSING",
                    "message": (
                        f"Document '{document_id}' is already being processed (stage: {doc.stage})."
                    ),
                    "field": "id",
                    "action": (
                        f"Poll progress via GET {status_url} or pass force_reparse=true to restart."
                    ),
                },
            )

        if doc.status == DocumentStatus.COMPLETED.value and not parse_req.force_reparse:
            return DocumentParseResponseData(
                id=doc.id,
                status=doc.status,
                stage=doc.stage,
                progress=doc.progress,
                message="Document already parsed. Set force_reparse=true to reprocess.",
                links=links,
            )

        # 3. 3-Tier Academic Document Gate (Reject non-scholarly files or scan-only PDFs)
        if await self.storage.blob_exists(doc.content_hash):
            doc_bytes = await self.storage.read_blob(doc.content_hash)
            await asyncio.to_thread(AcademicPaperValidator.validate_pdf, doc_bytes)

        # 4. Transition document state to processing / validation
        now = datetime.now(UTC)
        doc.status = DocumentStatus.PROCESSING.value
        doc.stage = DocumentStage.VALIDATION.value
        doc.progress = 0
        doc.error_message = None
        doc.updated_at = now

        # Update or record parse_options in parsed_metadata
        current_meta = dict(doc.parsed_metadata) if doc.parsed_metadata else {}
        current_meta["parse_options"] = {
            "chunk_size": parse_req.chunk_size,
            "chunk_overlap": parse_req.chunk_overlap,
            "extract_tables": parse_req.extract_tables,
            "force_reparse": parse_req.force_reparse,
            "triggered_at": now.isoformat(),
        }
        current_meta["stages_detail"] = {
            "validation": "in_progress",
            "layout_detection": "pending",
            "ocr": "pending",
            "chunking": "pending",
            "embedding": "pending",
        }
        doc.parsed_metadata = current_meta

        await db.flush()

        return DocumentParseResponseData(
            id=doc.id,
            status=doc.status,
            stage=doc.stage,
            progress=doc.progress,
            message="Document parsing pipeline initiated.",
            links=links,
        )

    async def extract_document_references(
        self,
        document_id: UUID,
        user_id: UUID,
        db: AsyncSession,
        force_reextract: bool = False,
    ) -> DocumentExtractReferencesResponseData:
        """Extract or retrieve cached scholarly references from a document.

        Args:
            document_id: Unique document identifier.
            user_id: Authenticated user identifier (enforces multi-tenant scoping).
            db: Active async database session.
            force_reextract: If True, bypass database cache and re-extract from PDF.

        Returns:
            DocumentExtractReferencesResponseData containing document_id, total_extracted,
            and structured references list.

        Raises:
            HTTPException(404): If document not found or belongs to another user,
                                or physical PDF blob is missing.
        """
        # 1. Enforce multi-tenant scoping
        doc_stmt = select(DocumentModel).where(
            DocumentModel.id == document_id,
            DocumentModel.user_id == user_id,
        )
        doc_res = await db.execute(doc_stmt)
        doc = doc_res.scalar_one_or_none()

        if doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DOCUMENT_NOT_FOUND",
                    "message": f"Document '{document_id}' not found.",
                    "field": "id",
                    "action": "Verify document ID or check access permissions.",
                },
            )

        # 2. Check cached database references if not forcing re-extraction
        if not force_reextract:
            cached_stmt = (
                select(ReferenceItemModel)
                .where(ReferenceItemModel.document_id == document_id)
                .order_by(ReferenceItemModel.ref_index.asc())
            )
            cached_res = await db.execute(cached_stmt)
            cached_items = cached_res.scalars().all()
            if cached_items:
                return DocumentExtractReferencesResponseData(
                    document_id=document_id,
                    total_extracted=len(cached_items),
                    references=[
                        ReferenceItemResponse(
                            ref_index=item.ref_index,
                            raw_text=item.raw_text,
                            parsed=ParsedReferenceItemSchema(
                                title=item.parsed_title,
                                authors=item.parsed_authors or [],
                                year=item.parsed_year,
                                arxiv_id=item.arxiv_id,
                                doi=item.doi,
                            ),
                        )
                        for item in cached_items
                    ],
                )

        # 3. Read binary PDF blob from storage
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

        pdf_bytes = await self.storage.read_blob(content_hash)

        # 4. Extract references from PDF offloaded to background thread
        extracted_refs: list[ExtractedReference] = await asyncio.to_thread(
            self._extract_references_from_pdf_stream, pdf_bytes
        )

        # 5. Clear previous references in database if re-extracting
        if force_reextract:
            del_stmt = delete(ReferenceItemModel).where(
                ReferenceItemModel.document_id == document_id
            )
            await db.execute(del_stmt)

        # 6. Persist extracted references
        for ref in extracted_refs:
            ref_model = ReferenceItemModel(
                user_id=doc.user_id,
                document_id=document_id,
                ref_index=ref.ref_index,
                raw_text=ref.raw_text,
                parsed_title=ref.parsed.title,
                parsed_authors=ref.parsed.authors,
                parsed_year=ref.parsed.year,
                doi=ref.parsed.doi,
                arxiv_id=ref.parsed.arxiv_id,
            )
            db.add(ref_model)

        await db.flush()

        return DocumentExtractReferencesResponseData(
            document_id=document_id,
            total_extracted=len(extracted_refs),
            references=[
                ReferenceItemResponse(
                    ref_index=r.ref_index,
                    raw_text=r.raw_text,
                    parsed=ParsedReferenceItemSchema(
                        title=r.parsed.title,
                        authors=r.parsed.authors,
                        year=r.parsed.year,
                        arxiv_id=r.parsed.arxiv_id,
                        doi=r.parsed.doi,
                    ),
                )
                for r in extracted_refs
            ],
        )

    @staticmethod
    def _extract_references_from_pdf_stream(pdf_bytes: bytes) -> list[ExtractedReference]:
        """Synchronously scan PDF pages and extract reference entries (runs in thread pool)."""
        import re

        import pymupdf

        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        total_pages = len(doc)
        if total_pages == 0:
            return []

        ref_pattern = re.compile(
            r"(?im)(?:^|\n)\s*(?:\[?\d+\]?|\d+\.)?\s*"
            r"(?:references|bibliography|works\s+cited)\s*(?:\n|$)"
        )
        stop_pattern = re.compile(
            r"(?im)(?:^|\n)\s*(?:appendix|attention visualizations|"
            r"acknowledgements|author contributions)\b"
        )

        full_ref_text = ""
        found_ref_heading = False

        for page_idx in range(total_pages):
            page_text = doc[page_idx].get_text()
            if not found_ref_heading:
                match = ref_pattern.search(page_text)
                if match:
                    found_ref_heading = True
                    full_ref_text += page_text[match.end() :]
            else:
                stop_match = stop_pattern.search(page_text)
                if stop_match:
                    full_ref_text += page_text[: stop_match.start()]
                    break
                full_ref_text += "\n" + page_text

        if not found_ref_heading or not full_ref_text.strip():
            return []

        return extract_references_from_text(full_ref_text)

    async def resolve_document_references(
        self,
        document_id: UUID,
        user_id: UUID,
        db: AsyncSession,
        ref_indices: list[int] | None = None,
        force_refresh: bool = False,
        resolver: IAcademicSearchResolverPort | None = None,
    ) -> DocumentResolveReferencesResponseData:
        """Resolve extracted scholarly references to rich academic metadata via resolver.

        Args:
            document_id: Unique document identifier.
            user_id: Authenticated user identifier (enforces multi-tenant scoping).
            db: Active async database session.
            ref_indices: Optional list of reference indices to resolve. If None, resolves all.
            force_refresh: If True, bypass cache and re-query resolver.
            resolver: Optional resolver port override.

        Returns:
            DocumentResolveReferencesResponseData containing resolved reference list.

        Raises:
            HTTPException(404): If document not found or belongs to another user.
        """
        # 1. Enforce multi-tenant scoping
        doc_stmt = select(DocumentModel).where(
            DocumentModel.id == document_id,
            DocumentModel.user_id == user_id,
        )
        doc_res = await db.execute(doc_stmt)
        doc = doc_res.scalar_one_or_none()

        if doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DOCUMENT_NOT_FOUND",
                    "message": f"Document '{document_id}' not found.",
                    "field": "id",
                    "action": "Verify document ID or check access permissions.",
                },
            )

        # 2. Retrieve reference items from database, extracting if not present
        cached_stmt = (
            select(ReferenceItemModel)
            .where(ReferenceItemModel.document_id == document_id)
            .order_by(ReferenceItemModel.ref_index.asc())
        )
        cached_res = await db.execute(cached_stmt)
        ref_items = list(cached_res.scalars().all())

        if not ref_items:
            # Auto-extract if references have not been extracted yet
            await self.extract_document_references(
                document_id=document_id,
                user_id=user_id,
                db=db,
                force_reextract=False,
            )
            cached_res = await db.execute(cached_stmt)
            ref_items = list(cached_res.scalars().all())

        # 3. Filter by ref_indices if specified
        if ref_indices is not None:
            target_indices = set(ref_indices)
            items_to_resolve = [item for item in ref_items if item.ref_index in target_indices]
        else:
            items_to_resolve = ref_items

        active_resolver = resolver or InMemoryAcademicResolverAdapter()

        # 4. Resolve references
        resolved_responses: list[ResolvedAcademicReferenceResponse] = []
        for item in items_to_resolve:
            extracted_ref = ExtractedReference(
                ref_index=item.ref_index,
                raw_text=item.raw_text,
                parsed=ParsedReferenceInfo(
                    title=item.parsed_title,
                    authors=item.parsed_authors or [],
                    year=item.parsed_year,
                    arxiv_id=item.arxiv_id,
                    doi=item.doi,
                ),
            )
            resolved = await active_resolver.resolve_reference(extracted_ref)

            # Update DB item if newly discovered metadata exists
            if not item.doi and resolved.doi:
                item.doi = resolved.doi
            if not item.arxiv_id and resolved.arxiv_id:
                item.arxiv_id = resolved.arxiv_id
            if not item.parsed_title and resolved.title:
                item.parsed_title = resolved.title
            if not item.parsed_authors and resolved.authors:
                item.parsed_authors = resolved.authors
            if not item.parsed_year and resolved.year:
                item.parsed_year = resolved.year

            is_ingested = item.resolved_document_id is not None
            resolved_doc_id = item.resolved_document_id

            resolved_responses.append(
                ResolvedAcademicReferenceResponse(
                    ref_index=resolved.ref_index,
                    raw_text=resolved.raw_text,
                    title=resolved.title,
                    authors=resolved.authors,
                    year=resolved.year,
                    doi=resolved.doi,
                    arxiv_id=resolved.arxiv_id,
                    open_access_pdf_url=resolved.open_access_pdf_url,
                    abstract=resolved.abstract,
                    citation_count=resolved.citation_count,
                    sources=resolved.sources,
                    landing_url=resolved.landing_url,
                    is_ingested=is_ingested,
                    resolved_document_id=resolved_doc_id,
                )
            )

        await db.commit()

        return DocumentResolveReferencesResponseData(
            document_id=document_id,
            total_resolved=len(resolved_responses),
            references=resolved_responses,
        )

    async def get_document_structure(
        self,
        document_id: UUID,
        user_id: UUID,
        db: AsyncSession,
        force_refresh: bool = False,
    ) -> DocumentStructureData:
        """Retrieve or extract hierarchical document structure (TOC, abstract, and sections).

        Args:
            document_id: UUID of the target scholarly document.
            user_id: Authenticated user identifier for tenant isolation.
            db: Active async database session.
            force_refresh: If True, bypass cached structure and re-extract from PDF.

        Returns:
            DocumentStructureData containing title, abstract, and sections.
        """
        # 1. Fetch document and enforce multi-tenant isolation
        stmt = select(DocumentModel).where(DocumentModel.id == document_id)
        res = await db.execute(stmt)
        doc = res.scalar_one_or_none()

        if not doc or doc.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DOCUMENT_NOT_FOUND",
                    "message": f"Document '{document_id}' not found.",
                    "field": "id",
                    "action": "Verify document ID or check access permissions.",
                },
            )

        # 2. Check cached structure in parsed_metadata
        cached_meta = dict(doc.parsed_metadata) if doc.parsed_metadata else {}
        if (
            not force_refresh
            and "structure" in cached_meta
            and isinstance(cached_meta["structure"], dict)
        ):
            struct_cache = cached_meta["structure"]
            sections_data = [
                DocumentSectionResponse(
                    title=s.get("title", ""),
                    page_number=s.get("page_number", 1),
                    bounding_boxes=s.get("bounding_boxes", []),
                )
                for s in struct_cache.get("sections", [])
            ]
            return DocumentStructureData(
                document_id=doc.id,
                title=struct_cache.get("title") or doc.title,
                abstract=struct_cache.get("abstract"),
                abstract_bounding_boxes=struct_cache.get("abstract_bounding_boxes", []),
                sections=sections_data,
            )

        # 3. Read raw PDF binary from CAS Storage
        pdf_bytes = await self.storage.read_blob(doc.content_hash)

        # 4. Extract structure in worker thread (CPU-bound)
        structure_entity = await asyncio.to_thread(
            self.structure_extractor.extract_structure,
            pdf_bytes,
            doc.id,
        )

        # 5. Build cache payload and persist to PostgreSQL
        sections_cache = [
            {
                "title": s.title,
                "page_number": s.page_number,
                "bounding_boxes": [b.to_list() for b in s.bounding_boxes],
            }
            for s in structure_entity.sections
        ]
        abstract_boxes = [b.to_list() for b in structure_entity.abstract_bounding_boxes]

        cached_meta["structure"] = {
            "title": structure_entity.title,
            "abstract": structure_entity.abstract,
            "abstract_bounding_boxes": abstract_boxes,
            "sections": sections_cache,
            "extracted_at": datetime.now(UTC).isoformat(),
        }
        doc.parsed_metadata = cached_meta

        # Backfill document title if empty
        if not doc.title and structure_entity.title:
            doc.title = structure_entity.title

        doc.updated_at = datetime.now(UTC)
        await db.flush()

        sections_resp = [
            DocumentSectionResponse(
                title=s.title,
                page_number=s.page_number,
                bounding_boxes=[b.to_list() for b in s.bounding_boxes],
            )
            for s in structure_entity.sections
        ]

        return DocumentStructureData(
            document_id=doc.id,
            title=structure_entity.title or doc.title,
            abstract=structure_entity.abstract,
            abstract_bounding_boxes=abstract_boxes,
            sections=sections_resp,
        )

    async def get_document_chunks(
        self,
        document_id: UUID,
        user_id: UUID,
        db: AsyncSession,
        page: int = 1,
        per_page: int = 50,
        page_number: int | None = None,
        include_content: bool = True,
    ) -> DocumentChunkPaginatedEnvelope:
        """Retrieve paginated chunks of a document with optional projection and page filtering.

        1. Multi-tenant guard: Check document exists and belongs to current user.
        2. Check existing chunks in document_chunks table.
        3. If empty and document has blob, extract chunks on-demand and persist.
        4. Filter by page_number if specified, paginate, and project include_content.
        5. Return DocumentChunkPaginatedEnvelope with RFC 8288 links.
        """
        # 1. Fetch document and enforce multi-tenant isolation
        stmt = select(DocumentModel).where(DocumentModel.id == document_id)
        res = await db.execute(stmt)
        doc = res.scalar_one_or_none()

        if not doc or doc.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DOCUMENT_NOT_FOUND",
                    "message": f"Document '{document_id}' not found.",
                    "field": "id",
                    "action": "Verify document ID or check access permissions.",
                },
            )

        # 2. Check existing chunks in database
        count_existing_stmt = (
            select(func.count())
            .select_from(DocumentChunkModel)
            .where(DocumentChunkModel.document_id == document_id)
        )
        count_res = await db.execute(count_existing_stmt)
        existing_count = count_res.scalar() or 0

        # 3. If no chunks exist and document has physical file blob, perform on-demand extraction
        if existing_count == 0 and doc.content_hash:
            if await self.storage.blob_exists(doc.content_hash):
                pdf_bytes = await self.storage.read_blob(doc.content_hash)
                extracted_chunks = await asyncio.to_thread(
                    self.chunk_extractor.extract_chunks,
                    pdf_bytes,
                    doc.id,
                )
                if extracted_chunks:
                    now = datetime.now(UTC)
                    chunk_models = await self._build_chunk_models(
                        extracted_chunks, doc.user_id, doc.id, now
                    )
                    try:
                        async with _safe_nested_transaction(db):
                            db.add_all(chunk_models)
                            doc.chunk_count = len(chunk_models)
                            doc.status = DocumentStatus.COMPLETED.value
                            doc.stage = DocumentStage.COMPLETED.value
                            doc.updated_at = datetime.now(UTC)
                            await db.flush()
                    except IntegrityError:
                        pass
                    # Ingestion Pre-computation: Pre-generate summary if missing
                    try:
                        await self._precompute_summary_if_missing(doc, chunk_models, pdf_bytes, db)
                    except Exception:
                        pass

        # 4. Build query with optional page_number filtering
        where_clauses = [DocumentChunkModel.document_id == document_id]
        if page_number is not None:
            where_clauses.append(DocumentChunkModel.page_number == page_number)

        total_stmt = select(func.count()).select_from(DocumentChunkModel).where(*where_clauses)
        total_res = await db.execute(total_stmt)
        total = total_res.scalar() or 0

        total_pages = max(1, math.ceil(total / per_page))
        offset = (page - 1) * per_page

        items_stmt = (
            select(DocumentChunkModel)
            .where(*where_clauses)
            .order_by(DocumentChunkModel.chunk_index.asc())
            .offset(offset)
            .limit(per_page)
        )
        items_res = await db.execute(items_stmt)
        chunk_rows = items_res.scalars().all()

        data = [
            DocumentChunkItem(
                id=row.id,
                document_id=row.document_id,
                chunk_index=row.chunk_index,
                page_number=row.page_number,
                content=row.content if include_content else None,
                bounding_boxes=row.bounding_boxes or [],
                token_count=row.token_count,
            )
            for row in chunk_rows
        ]

        # 5. Build RFC 8288 pagination links
        def _build_url(p: int) -> str:
            base = f"/api/v1/documents/{document_id}/chunks?page={p}&per_page={per_page}"
            if page_number is not None:
                base += f"&page_number={page_number}"
            if not include_content:
                base += "&include_content=false"
            return base

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

        return DocumentChunkPaginatedEnvelope(
            success=True,
            data=data,
            meta=meta,
            links=links,
        )

    async def get_document_chunk_detail(
        self,
        db: AsyncSession,
        user_id: UUID,
        document_id: UUID,
        chunk_id: UUID,
    ) -> DocumentChunkDetailEnvelope:
        """Retrieve detailed content, bounding boxes, and navigation links for a chunk.

        Execution flow:
        1. Fetch document and enforce multi-tenant isolation (user_id check).
           Raise 404 DOCUMENT_NOT_FOUND if missing or unauthorized.
        2. If document has 0 chunks and has physical blob, perform on-demand extraction.
        3. Query DocumentChunkModel where document_id == document_id and id == chunk_id.
           Raise 404 CHUNK_NOT_FOUND if chunk does not exist for this document.
        4. Query adjacent chunk IDs (prev_chunk for chunk_index - 1, next_chunk for chunk_index + 1)
           using fast indexed lookup.
        5. Construct hypermedia navigation links and return DocumentChunkDetailEnvelope.
        """
        # 1. Fetch document and enforce multi-tenant isolation
        stmt = select(DocumentModel).where(DocumentModel.id == document_id)
        res = await db.execute(stmt)
        doc = res.scalar_one_or_none()

        if not doc or doc.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DOCUMENT_NOT_FOUND",
                    "message": f"Document '{document_id}' not found.",
                    "field": "id",
                    "action": "Verify document ID or check access permissions.",
                },
            )

        # 2. If no chunks exist and document has physical file blob, perform on-demand extraction
        count_existing_stmt = (
            select(func.count())
            .select_from(DocumentChunkModel)
            .where(DocumentChunkModel.document_id == document_id)
        )
        count_res = await db.execute(count_existing_stmt)
        existing_count = count_res.scalar() or 0

        if existing_count == 0 and doc.content_hash:
            if await self.storage.blob_exists(doc.content_hash):
                pdf_bytes = await self.storage.read_blob(doc.content_hash)
                extracted_chunks = await asyncio.to_thread(
                    self.chunk_extractor.extract_chunks,
                    pdf_bytes,
                    doc.id,
                )
                if extracted_chunks:
                    now = datetime.now(UTC)
                    chunk_models = await self._build_chunk_models(
                        extracted_chunks, doc.user_id, doc.id, now
                    )
                    try:
                        async with _safe_nested_transaction(db):
                            db.add_all(chunk_models)
                            doc.chunk_count = len(chunk_models)
                            doc.status = DocumentStatus.COMPLETED.value
                            doc.stage = DocumentStage.COMPLETED.value
                            doc.updated_at = datetime.now(UTC)
                            await db.flush()
                    except IntegrityError:
                        pass

        # 3. Query the requested chunk
        chunk_stmt = select(DocumentChunkModel).where(
            DocumentChunkModel.document_id == document_id,
            DocumentChunkModel.id == chunk_id,
        )
        chunk_res = await db.execute(chunk_stmt)
        chunk = chunk_res.scalar_one_or_none()

        if not chunk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "CHUNK_NOT_FOUND",
                    "message": f"Chunk '{chunk_id}' not found for document '{document_id}'.",
                    "field": "chunk_id",
                    "action": (
                        f"Verify chunk ID or query GET /api/v1/documents/{document_id}/chunks "
                        "for available chunks."
                    ),
                },
            )

        # 4. Resolve previous and next chunk IDs for reader traversal
        prev_chunk_id: UUID | None = None
        next_chunk_id: UUID | None = None

        if chunk.chunk_index > 0:
            prev_stmt = select(DocumentChunkModel.id).where(
                DocumentChunkModel.document_id == document_id,
                DocumentChunkModel.chunk_index == chunk.chunk_index - 1,
            )
            prev_res = await db.execute(prev_stmt)
            prev_chunk_id = prev_res.scalar_one_or_none()

        next_stmt = select(DocumentChunkModel.id).where(
            DocumentChunkModel.document_id == document_id,
            DocumentChunkModel.chunk_index == chunk.chunk_index + 1,
        )
        next_res = await db.execute(next_stmt)
        next_chunk_id = next_res.scalar_one_or_none()

        # 5. Build navigational links
        base_doc_url = f"/api/v1/documents/{document_id}"
        links = DocumentChunkNavigationLinks(
            self=f"{base_doc_url}/chunks/{chunk.id}",
            document=base_doc_url,
            chunks=f"{base_doc_url}/chunks",
            prev_chunk=f"{base_doc_url}/chunks/{prev_chunk_id}" if prev_chunk_id else None,
            next_chunk=f"{base_doc_url}/chunks/{next_chunk_id}" if next_chunk_id else None,
        )

        embedding_dim = (
            len(chunk.embedding) if chunk.embedding and isinstance(chunk.embedding, list) else None
        )

        now = datetime.now(UTC)
        data = DocumentChunkDetailData(
            id=chunk.id,
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
            page_number=chunk.page_number,
            content=chunk.content,
            bounding_boxes=chunk.bounding_boxes or [],
            token_count=chunk.token_count,
            embedding_dimension=embedding_dim,
            created_at=chunk.created_at or now,
            updated_at=chunk.updated_at or now,
            links=links,
        )

        return DocumentChunkDetailEnvelope(
            success=True,
            data=data,
        )

    async def _precompute_summary_if_missing(
        self,
        doc: DocumentModel,
        chunk_models: list[DocumentChunkModel],
        pdf_bytes: bytes | None,
        db: AsyncSession,
    ) -> DocumentSummaryModel:
        """Precompute and persist 3-point grounded summary to DB cache if not already present."""
        sum_stmt = select(DocumentSummaryModel).where(DocumentSummaryModel.document_id == doc.id)
        sum_res = await db.execute(sum_stmt)
        existing = sum_res.scalar_one_or_none()
        if existing is not None:
            if not doc.parsed_metadata or "summary_metadata" not in doc.parsed_metadata:
                summary_meta = self._extract_summary_metadata(
                    problem_statement=existing.problem_statement,
                    contributions=existing.contributions,
                    limitations=existing.limitations,
                    chunks=chunk_models,
                    abstract=None,
                )
                current_meta = dict(doc.parsed_metadata or {})
                current_meta["summary_metadata"] = summary_meta
                doc.parsed_metadata = current_meta
                db.add(doc)
                await db.flush()
            return existing

        domain_chunks = []
        for cm in chunk_models:
            boxes = []
            if cm.bounding_boxes:
                for b in cm.bounding_boxes:
                    if isinstance(b, (list, tuple)) and len(b) >= 5:
                        try:
                            boxes.append(
                                BoundingBox(
                                    x0=float(b[0]),
                                    y0=float(b[1]),
                                    x1=float(b[2]),
                                    y1=float(b[3]),
                                    page=int(b[4]),
                                )
                            )
                        except Exception:
                            pass
            domain_chunks.append(
                DocumentChunk(
                    id=cm.id,
                    document_id=cm.document_id,
                    chunk_index=cm.chunk_index,
                    page_number=cm.page_number,
                    content=cm.content,
                    bounding_boxes=boxes,
                    token_count=cm.token_count,
                )
            )

        abstract_text = None
        if doc.parsed_metadata and isinstance(doc.parsed_metadata, dict):
            struct_data = doc.parsed_metadata.get("structure")
            if isinstance(struct_data, dict):
                abstract_text = struct_data.get("abstract")

        generated = await self.summarizer.summarize(
            document_id=doc.id,
            title=doc.title,
            abstract=abstract_text,
            chunks=domain_chunks,
            pdf_bytes=pdf_bytes,
        )

        def _serialize_boxes(boxes_in):
            out = []
            for b in boxes_in:
                if hasattr(b, "to_list"):
                    out.append(b.to_list())
                elif isinstance(b, (list, tuple)):
                    out.append(list(b))
            return out

        now = datetime.now(UTC)
        summary_record = DocumentSummaryModel(
            id=uuid4(),
            user_id=doc.user_id,
            document_id=doc.id,
            problem_statement=generated.problem_statement.text,
            problem_citations=_serialize_boxes(generated.problem_statement.bounding_boxes),
            contributions=generated.contributions.text,
            contribution_citations=_serialize_boxes(generated.contributions.bounding_boxes),
            limitations=generated.limitations.text,
            limitation_citations=_serialize_boxes(generated.limitations.bounding_boxes),
            total_tokens=generated.total_tokens,
            latency_ms=generated.latency_ms,
            created_at=now,
            updated_at=now,
        )
        try:
            async with _safe_nested_transaction(db):
                db.add(summary_record)
                summary_meta = self._extract_summary_metadata(
                    problem_statement=summary_record.problem_statement,
                    contributions=summary_record.contributions,
                    limitations=summary_record.limitations,
                    chunks=chunk_models,
                    abstract=abstract_text,
                )
                current_meta = dict(doc.parsed_metadata or {})
                current_meta["summary_metadata"] = summary_meta
                doc.parsed_metadata = current_meta
                db.add(doc)
                await db.flush()
            return summary_record
        except IntegrityError:
            sum_res = await db.execute(sum_stmt)
            return sum_res.scalar_one()

    async def get_document_summary(
        self,
        document_id: UUID,
        user_id: UUID,
        db: AsyncSession,
    ) -> DocumentSummaryEnvelope:
        """Retrieve the singleton 3-point grounded summary for a document.

        Adheres strictly to Google Cloud AIP-130 and AIP-136 Singleton sub-resource design.

        Execution flow:
        1. Fetch document and enforce multi-tenant isolation (user_id check).
           Raise 404 DOCUMENT_NOT_FOUND if missing or unauthorized.
        2. Status check:
           - If status in ('pending', 'processing'), raise 409 DOCUMENT_PROCESSING.
           - If status == 'failed', raise 422 DOCUMENT_FAILED.
        3. Query DocumentSummaryModel where document_id == document_id.
           - Cache Hit: Map stored JSONB and fields to DocumentSummaryData and return.
           - Cache Miss (On-demand synthesis fallback):
             a. Ensure document chunks exist (extract on-demand from storage if needed).
             b. Call self.summarizer.summarize(...) with pdf_bytes.
             c. Persist to document_summaries table.
             d. Map and return DocumentSummaryEnvelope.
        """
        # 1. Fetch document and enforce multi-tenant isolation
        stmt = select(DocumentModel).where(DocumentModel.id == document_id)
        res = await db.execute(stmt)
        doc = res.scalar_one_or_none()

        if not doc or doc.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DOCUMENT_NOT_FOUND",
                    "message": f"Document '{document_id}' not found.",
                    "field": "id",
                    "action": "Verify document ID or check access permissions.",
                },
            )

        # 2. Lifecycle Status Guard
        pending_states = (
            DocumentStatus.PENDING.value,
            DocumentStatus.PROCESSING.value,
            "pending",
            "processing",
        )
        if (doc.chunk_count and doc.chunk_count > 0) and doc.status in pending_states:
            doc.status = DocumentStatus.COMPLETED.value
            doc.stage = DocumentStage.COMPLETED.value
            await db.flush()

        if doc.status in pending_states:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "DOCUMENT_PROCESSING",
                    "message": (
                        f"Document '{document_id}' is still being processed. "
                        "Wait for completion before querying summary."
                    ),
                    "field": "id",
                    "action": f"Poll GET /api/v1/documents/{document_id}/status until completed.",
                },
            )
        if doc.status in (DocumentStatus.FAILED.value, "failed"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "code": "DOCUMENT_FAILED",
                    "message": (
                        f"Document '{document_id}' failed processing. Summary cannot be extracted."
                    ),
                    "field": "id",
                    "action": f"Check error_message in /documents/{document_id}/status.",
                },
            )

        # 3. Query DocumentSummaryModel
        sum_stmt = select(DocumentSummaryModel).where(
            DocumentSummaryModel.document_id == document_id
        )
        sum_res = await db.execute(sum_stmt)
        summary_record = sum_res.scalar_one_or_none()

        if summary_record is None:
            # 4. On-demand Synthesis Fallback
            pdf_bytes = None
            if doc.content_hash and await self.storage.blob_exists(doc.content_hash):
                pdf_bytes = await self.storage.read_blob(doc.content_hash)

            # Ensure chunks exist
            chunks_stmt = (
                select(DocumentChunkModel)
                .where(DocumentChunkModel.document_id == document_id)
                .order_by(DocumentChunkModel.chunk_index.asc())
            )
            chunks_res = await db.execute(chunks_stmt)
            chunk_models = list(chunks_res.scalars().all())

            if not chunk_models and pdf_bytes:
                extracted_chunks = await asyncio.to_thread(
                    self.chunk_extractor.extract_chunks,
                    pdf_bytes,
                    doc.id,
                )
                if extracted_chunks:
                    now = datetime.now(UTC)
                    new_chunks = await self._build_chunk_models(
                        extracted_chunks, doc.user_id, doc.id, now
                    )
                    db.add_all(new_chunks)
                    doc.chunk_count = len(new_chunks)
                    doc.updated_at = datetime.now(UTC)
                    await db.flush()
                    chunk_models = new_chunks

            summary_record = await self._precompute_summary_if_missing(
                doc=doc,
                chunk_models=chunk_models,
                pdf_bytes=pdf_bytes,
                db=db,
            )

        return self._map_summary_model_to_envelope(summary_record)

    def _map_summary_model_to_envelope(
        self, summary_record: DocumentSummaryModel
    ) -> DocumentSummaryEnvelope:
        """Map DocumentSummaryModel ORM record to DocumentSummaryEnvelope schema."""
        now = datetime.now(UTC)
        data = DocumentSummaryData(
            document_id=summary_record.document_id,
            problem_statement=SummaryPointResponse(
                text=summary_record.problem_statement,
                bounding_boxes=summary_record.problem_citations or [],
            ),
            contributions=SummaryPointResponse(
                text=summary_record.contributions,
                bounding_boxes=summary_record.contribution_citations or [],
            ),
            limitations=SummaryPointResponse(
                text=summary_record.limitations,
                bounding_boxes=summary_record.limitation_citations or [],
            ),
            total_tokens=summary_record.total_tokens,
            latency_ms=summary_record.latency_ms,
            created_at=summary_record.created_at or now,
            updated_at=summary_record.updated_at or now,
        )
        return DocumentSummaryEnvelope(
            success=True,
            data=data,
        )

    async def generate_document_summary(
        self,
        document_id: UUID,
        user_id: UUID,
        force: bool,
        db: AsyncSession,
    ) -> tuple[DocumentSummaryEnvelope, str]:
        """Generate or retrieve a 3-point grounded summary according to Google AIP-136.

        Args:
            document_id: Target document identifier.
            user_id: Authenticated user identifier for ownership check.
            force: If True, forces re-synthesis even if a cached summary already exists.
            db: Active async database session.

        Returns:
            Tuple of (DocumentSummaryEnvelope, cache_status) where cache_status is
            'Cache-Hit' or 'Generated'.
        """
        # 1. Multi-tenant & Document Existence Guard
        stmt = select(DocumentModel).where(DocumentModel.id == document_id)
        res = await db.execute(stmt)
        doc = res.scalar_one_or_none()

        if doc is None or doc.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DOCUMENT_NOT_FOUND",
                    "message": f"Document '{document_id}' not found.",
                    "field": "id",
                    "action": "Ensure UUID exists and belongs to the authenticated user.",
                },
            )

        # 2. Lifecycle Status Guard
        pending_states = (
            DocumentStatus.PENDING.value,
            DocumentStatus.PROCESSING.value,
            "pending",
            "processing",
        )
        if (doc.chunk_count and doc.chunk_count > 0) and doc.status in pending_states:
            doc.status = DocumentStatus.COMPLETED.value
            doc.stage = DocumentStage.COMPLETED.value
            await db.flush()

        if doc.status in pending_states:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "DOCUMENT_PROCESSING",
                    "message": (
                        f"Document '{document_id}' is still being processed. "
                        "Wait for completion before generating summary."
                    ),
                    "field": "id",
                    "action": f"Poll GET /api/v1/documents/{document_id}/status until completed.",
                },
            )
        if doc.status in (DocumentStatus.FAILED.value, "failed"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "code": "DOCUMENT_FAILED",
                    "message": (
                        f"Document '{document_id}' failed processing. Summary cannot be generated."
                    ),
                    "field": "id",
                    "action": f"Check error_message in /documents/{document_id}/status.",
                },
            )

        with self.ai_tracing.trace(
            name="document_summary",
            user_id=user_id,
            document_id=document_id,
            metadata={"force": force, "doc_title": doc.title},
        ) as trace_span:
            # 3. Query existing summary
            with self.ai_tracing.span(
                name="summary_retrieval",
                input={"document_id": str(document_id), "force": force},
            ) as ret_span:
                sum_stmt = select(DocumentSummaryModel).where(
                    DocumentSummaryModel.document_id == document_id
                )
                sum_res = await db.execute(sum_stmt)
                summary_record = sum_res.scalar_one_or_none()
                ret_span.set_output({"cache_hit": summary_record is not None and not force})

            # If summary exists and force is False -> Immediate Cache-Hit
            if summary_record is not None and not force:
                trace_span.set_output({"status": "Cache-Hit"})
                return self._map_summary_model_to_envelope(summary_record), "Cache-Hit"

            # 4. Perform synthesis (initial or forced re-synthesis)
            pdf_bytes = None
            if doc.content_hash and await self.storage.blob_exists(doc.content_hash):
                pdf_bytes = await self.storage.read_blob(doc.content_hash)

            chunks_stmt = (
                select(DocumentChunkModel)
                .where(DocumentChunkModel.document_id == document_id)
                .order_by(DocumentChunkModel.chunk_index.asc())
            )
            chunks_res = await db.execute(chunks_stmt)
            chunk_models = list(chunks_res.scalars().all())

            if not chunk_models and pdf_bytes:
                extracted_chunks = await asyncio.to_thread(
                    self.chunk_extractor.extract_chunks,
                    pdf_bytes,
                    doc.id,
                )
                if extracted_chunks:
                    now = datetime.now(UTC)
                    new_chunks = await self._build_chunk_models(
                        extracted_chunks, doc.user_id, doc.id, now
                    )
                    db.add_all(new_chunks)
                    doc.chunk_count = len(new_chunks)
                    doc.updated_at = datetime.now(UTC)
                    await db.flush()
                    chunk_models = new_chunks

            domain_chunks = [
                DocumentChunk(
                    id=c.id,
                    document_id=c.document_id,
                    chunk_index=c.chunk_index,
                    page_number=c.page_number,
                    content=c.content,
                    bounding_boxes=[BoundingBox.from_list(b) for b in (c.bounding_boxes or [])],
                    token_count=c.token_count,
                )
                for c in chunk_models
            ]

            abstract_text = None
            if doc.parsed_metadata and isinstance(doc.parsed_metadata, dict):
                struct_data = doc.parsed_metadata.get("structure")
                if isinstance(struct_data, dict):
                    abstract_text = struct_data.get("abstract")

            with self.ai_tracing.generation(
                name="summary_generation",
                model=getattr(self.summarizer, "model", "summarizer"),
                input={"title": doc.title, "chunk_count": len(domain_chunks)},
            ) as gen_span:
                domain_summary = await self.summarizer.summarize(
                    document_id=doc.id,
                    title=doc.title,
                    abstract=abstract_text,
                    chunks=domain_chunks,
                    pdf_bytes=pdf_bytes,
                )
                gen_span.set_output(
                    {
                        "total_tokens": domain_summary.total_tokens,
                        "latency_ms": domain_summary.latency_ms,
                    }
                )

            prob_boxes = [b.to_list() for b in domain_summary.problem_statement.bounding_boxes]
            contr_boxes = [b.to_list() for b in domain_summary.contributions.bounding_boxes]
            limit_boxes = [b.to_list() for b in domain_summary.limitations.bounding_boxes]

            now = datetime.now(UTC)
            if summary_record is not None:
                summary_record.problem_statement = domain_summary.problem_statement.text
                summary_record.problem_citations = prob_boxes
                summary_record.contributions = domain_summary.contributions.text
                summary_record.contribution_citations = contr_boxes
                summary_record.limitations = domain_summary.limitations.text
                summary_record.limitation_citations = limit_boxes
                summary_record.total_tokens = domain_summary.total_tokens
                summary_record.latency_ms = domain_summary.latency_ms
                summary_record.updated_at = now
            else:
                summary_record = DocumentSummaryModel(
                    id=uuid4(),
                    user_id=doc.user_id,
                    document_id=doc.id,
                    problem_statement=domain_summary.problem_statement.text,
                    problem_citations=prob_boxes,
                    contributions=domain_summary.contributions.text,
                    contribution_citations=contr_boxes,
                    limitations=domain_summary.limitations.text,
                    limitation_citations=limit_boxes,
                    total_tokens=domain_summary.total_tokens,
                    latency_ms=domain_summary.latency_ms,
                    created_at=now,
                    updated_at=now,
                )
                db.add(summary_record)
            summary_meta = self._extract_summary_metadata(
                problem_statement=summary_record.problem_statement,
                contributions=summary_record.contributions,
                limitations=summary_record.limitations,
                chunks=chunk_models,
                abstract=abstract_text,
            )
            current_meta = dict(doc.parsed_metadata or {})
            current_meta["summary_metadata"] = summary_meta
            doc.parsed_metadata = current_meta
            db.add(doc)
            try:
                await db.commit()
            except IntegrityError:
                await db.rollback()
                latest_stmt = select(DocumentSummaryModel).where(
                    DocumentSummaryModel.document_id == document_id
                )
                latest_res = await db.execute(latest_stmt)
                summary_record = latest_res.scalar_one_or_none()
                if summary_record is None:
                    raise

            trace_span.set_output(
                {
                    "status": "Generated",
                    "total_tokens": domain_summary.total_tokens,
                    "latency_ms": domain_summary.latency_ms,
                }
            )
            return self._map_summary_model_to_envelope(summary_record), "Generated"

    async def stream_summary(
        self,
        document_id: UUID,
        user_id: UUID,
        db: AsyncSession,
        is_disconnected: Any = None,
        request_id: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream 3-point grounded summary tokens and spatial bounding boxes via SSE."""
        try:
            envelope, _ = await self.generate_document_summary(
                document_id=document_id,
                user_id=user_id,
                force=False,
                db=db,
            )
            data = envelope.data

            start_dict = {
                "document_id": str(document_id),
                "status": "streaming",
                "request_id": request_id,
            }
            start_payload = json.dumps(start_dict, ensure_ascii=False)
            yield f"event: summary_start\ndata: {start_payload}\n\n"

            sections = [
                (
                    "problem_statement",
                    data.problem_statement.text if data.problem_statement else "",
                    data.problem_statement.bounding_boxes if data.problem_statement else [],
                ),
                (
                    "contributions",
                    data.contributions.text if data.contributions else "",
                    data.contributions.bounding_boxes if data.contributions else [],
                ),
                (
                    "limitations",
                    data.limitations.text if data.limitations else "",
                    data.limitations.bounding_boxes if data.limitations else [],
                ),
            ]

            for section_name, text, citations in sections:
                tokens = (text or "").split(" ")
                for t in tokens:
                    if is_disconnected and await is_disconnected():
                        return
                    tok_str = t + " "
                    ch_dict = {"section": section_name, "token": tok_str}
                    chunk_payload = json.dumps(ch_dict, ensure_ascii=False)
                    yield f"event: summary_chunk\ndata: {chunk_payload}\n\n"
                    await asyncio.sleep(0.01)

                boxes = [c.model_dump() if hasattr(c, "model_dump") else c for c in citations or []]
                bx_dict = {"section": section_name, "bounding_boxes": boxes}
                box_payload = json.dumps(bx_dict, ensure_ascii=False)
                yield f"event: summary_box\ndata: {box_payload}\n\n"

            end_dict = {"document_id": str(document_id), "finish_reason": "completed"}
            end_payload = json.dumps(end_dict, ensure_ascii=False)
            yield f"event: summary_end\ndata: {end_payload}\n\n"
        except Exception as exc:
            err_dict = {
                "code": "STREAM_RUNTIME_ERROR",
                "message": str(exc),
                "request_id": request_id,
            }
            err_payload = json.dumps(err_dict, ensure_ascii=False)
            yield f"event: error\ndata: {err_payload}\n\n"
