"""Discovery endpoints implementing academic search and 1-click Zero-to-Reading."""

import hashlib
from uuid import uuid4

from api.db.models.document import DocumentModel
from api.db.models.session import ResearchSessionModel, SessionDocumentModel
from api.db.models.user import UserModel
from api.db.session import get_db
from api.deps import get_current_user, get_scholarly_search_port
from api.schemas.discovery import (
    DiscoverySearchRequest,
    OpenReadingRequest,
    OpenReadingResponse,
)
from api.schemas.envelope import ResponseMeta, SingleResponseEnvelope
from core.ports.scholarly_search import IScholarlySearchPort, ScholarlyPaperSearchResult
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/discovery", tags=["Module 2: Discovery"])


@router.post(
    "/search",
    status_code=status.HTTP_200_OK,
    response_model=SingleResponseEnvelope[list[ScholarlyPaperSearchResult]],
    summary="Tìm kiếm tài liệu học thuật (Scholarly Literature Search)",
)
async def search_scholarly_literature(
    payload: DiscoverySearchRequest,
    current_user: UserModel = Depends(get_current_user),
    search_port: IScholarlySearchPort = Depends(get_scholarly_search_port),
) -> SingleResponseEnvelope[list[ScholarlyPaperSearchResult]]:
    """Search academic papers across open-access sources and arXiv."""
    clean_query = payload.query.strip()
    if not clean_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "SEARCH_QUERY_EMPTY",
                "message": "Từ khóa tìm kiếm không được để trống.",
                "field": "query",
            },
        )

    if payload.limit < 1 or payload.limit > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "SEARCH_LIMIT_OUT_OF_RANGE",
                "message": "Số lượng kết quả phải nằm trong khoảng từ 1 đến 50.",
                "field": "limit",
            },
        )

    results = await search_port.search(clean_query, limit=payload.limit)
    return SingleResponseEnvelope(
        data=results,
        meta=ResponseMeta(total_results=len(results)),
    )


@router.post(
    "/open-reading",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleResponseEnvelope[OpenReadingResponse],
    summary="Mở phiên đọc tức thì 1-Click Zero-to-Reading",
)
async def open_reading_session(
    payload: OpenReadingRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SingleResponseEnvelope[OpenReadingResponse]:
    """Create a research session and ingest paper metadata < 500ms for immediate reading."""
    clean_title = payload.title.strip()
    has_pdf = bool(payload.pdf_url and payload.pdf_url.strip())
    doc_status = "parsing" if has_pdf else "abstract_only"
    access_status = "open_access_pdf" if has_pdf else "abstract_only"

    # Create dummy SHA-256 content_hash for initial metadata record
    hash_seed = f"{payload.doi or payload.arxiv_id or clean_title}_{current_user.id}"
    initial_hash = hashlib.sha256(hash_seed.encode("utf-8")).hexdigest()

    doc_id = uuid4()
    session_id = uuid4()

    new_doc = DocumentModel(
        id=doc_id,
        user_id=current_user.id,
        filename=f"{clean_title[:80]}.pdf",
        title=clean_title,
        authors=payload.authors,
        publication_year=payload.publication_year,
        doi=payload.doi,
        content_hash=initial_hash,
        file_size_bytes=0,
        status=doc_status,
        stage="metadata_ingested",
        progress=100 if not has_pdf else 10,
        access_status=access_status,
        parsed_metadata={
            "abstract": payload.abstract,
            "arxiv_id": payload.arxiv_id,
            "venue": payload.venue,
        },
    )
    db.add(new_doc)

    new_session = ResearchSessionModel(
        id=session_id,
        user_id=current_user.id,
        title=clean_title[:100],
        active_document_id=doc_id,
        viewport_state={"page": 1, "zoom_ratio": 1.0, "scroll_top": 0.0},
        active_tab="chat",
    )
    db.add(new_session)

    junction = SessionDocumentModel(
        session_id=session_id,
        document_id=doc_id,
        tab_order=0,
    )
    db.add(junction)

    await db.commit()

    return SingleResponseEnvelope(
        data=OpenReadingResponse(
            session_id=session_id,
            document_id=doc_id,
            status=doc_status,
            access_status=access_status,
        ),
        meta=ResponseMeta(),
    )
