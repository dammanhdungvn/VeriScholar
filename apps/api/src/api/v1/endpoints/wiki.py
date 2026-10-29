"""Compiled Academic LLM Wiki & Research Gaps REST Endpoints (Spec 05 §1.D, §4).

Provides:
- GET /api/v1/library/wiki: List compiled wiki pages with optional filtering & pagination
- GET /api/v1/library/wiki/{slug}: Retrieve full compiled wiki page by slug
- POST /api/v1/library/research-gaps: Synthesize cross-paper research gaps & novel thesis topics
"""

from __future__ import annotations

import re
from uuid import UUID

import structlog
from api.db.models.document import DocumentModel
from api.db.models.folder import FolderModel
from api.db.models.user import UserModel
from api.db.models.wiki import WikiPageModel
from api.db.session import get_db
from api.deps import get_current_user, get_wiki_service
from api.schemas.error import ErrorResponse
from api.schemas.wiki import (
    ResearchGapsRequest,
    ResearchGapsResponse,
    ResearchGapsResponseEnvelope,
    SuggestedTopicItem,
    UnsolvedFrontierItem,
    WikiListResponse,
    WikiListResponseEnvelope,
    WikiPageResponse,
    WikiPageResponseEnvelope,
    WikiPageSummary,
)
from api.services.wiki_service import WikiService
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger("api.endpoints.wiki")

router = APIRouter(prefix="/library", tags=["wiki"])


@router.get(
    "/wiki",
    response_model=WikiListResponseEnvelope,
    summary="Lấy danh mục các trang Wiki học thuật đã biên soạn",
    description=(
        "Tra cứu danh sách các trang Wiki tri thức đã biên soạn từ các bài báo trong kho cá nhân. "
        "Hỗ trợ phân trang, lọc theo thư mục (folder_id) và loại trang (page_type)."
    ),
    responses={
        200: {"description": "Danh mục các trang Wiki học thuật."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực người dùng."},
        404: {"model": ErrorResponse, "description": "Thư mục không tồn tại."},
    },
)
async def list_wiki_pages(
    folder_id: UUID | None = Query(default=None, description="Lọc theo ID thư mục đề tài"),
    page_type: str | None = Query(default=None, description="Lọc theo loại trang"),
    limit: int = Query(default=50, ge=1, le=100, description="Số lượng bản ghi tối đa"),
    offset: int = Query(default=0, ge=0, description="Vị trí bắt đầu"),
    current_user: UserModel = Depends(get_current_user),
    wiki_service: WikiService = Depends(get_wiki_service),
    db: AsyncSession = Depends(get_db),
) -> WikiListResponseEnvelope:
    """List compiled academic wiki pages belonging to the current user."""
    # 1. Validate folder existence if folder_id is provided
    if folder_id is not None:
        folder_stmt = select(FolderModel).where(
            FolderModel.id == folder_id,
            FolderModel.user_id == current_user.id,
        )
        folder_res = await db.execute(folder_stmt)
        if folder_res.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "FOLDER_NOT_FOUND",
                    "message": "Không tìm thấy thư mục đề tài yêu cầu.",
                    "field": "folder_id",
                    "action": "Chọn thư mục tồn tại trong cây thư mục cá nhân.",
                },
            )

    # 2. Get total matching count
    total = await wiki_service.count_pages(
        user_id=current_user.id,
        folder_id=folder_id,
        page_type=page_type,
        db=db,
    )

    # 3. Retrieve paginated records
    pages = await wiki_service.list_pages(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        folder_id=folder_id,
        page_type=page_type,
        db=db,
    )

    # 4. Map to summary DTOs
    page_summaries: list[WikiPageSummary] = []
    for p in pages:
        meta = p.yaml_metadata or {}
        summary_val = meta.get("summary") or meta.get("description")
        if not summary_val and p.markdown_content:
            first_p = p.markdown_content.strip().split("\n\n")[0]
            clean_first_p = re.sub(r"^#+\s*", "", first_p).strip()
            summary_val = clean_first_p[:200]

        page_summaries.append(
            WikiPageSummary(
                id=p.id,
                slug=p.slug,
                title=p.title,
                page_type=p.page_type,
                summary=summary_val,
                wikilinks=p.wikilinks or [],
                backlinks_count=meta.get("backlinks_count", 0),
                folder_id=p.folder_id,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
        )

    return WikiListResponseEnvelope(
        success=True,
        data=WikiListResponse(
            total=total,
            pages=page_summaries,
        ),
    )


@router.get(
    "/wiki/{slug}",
    response_model=WikiPageResponseEnvelope,
    summary="Đọc chi tiết một trang Wiki tri thức học thuật",
    description="Truy xuất toàn văn trang Wiki Markdown kèm YAML frontmatter và [[wikilinks]].",
    responses={
        200: {"description": "Thông tin chi tiết trang Wiki học thuật."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực người dùng."},
        404: {"model": ErrorResponse, "description": "Không tìm thấy trang Wiki."},
    },
)
async def get_wiki_page(
    slug: str,
    current_user: UserModel = Depends(get_current_user),
    wiki_service: WikiService = Depends(get_wiki_service),
    db: AsyncSession = Depends(get_db),
) -> WikiPageResponseEnvelope:
    """Retrieve an individual compiled academic wiki page by concept slug."""
    page = await wiki_service.get_page_by_slug(user_id=current_user.id, slug=slug, db=db)
    if page is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "WIKI_PAGE_NOT_FOUND",
                "message": f"Không tìm thấy trang Wiki học thuật cho khái niệm '{slug}'.",
                "field": "slug",
                "action": "Kiểm tra slug hoặc biên soạn trang wiki mới từ bài báo.",
            },
        )

    meta = page.yaml_metadata or {}
    summary_val = meta.get("summary") or meta.get("description")
    if not summary_val and page.markdown_content:
        first_p = page.markdown_content.strip().split("\n\n")[0]
        summary_val = re.sub(r"^#+\s*", "", first_p).strip()[:200]

    page_detail = WikiPageResponse(
        id=page.id,
        user_id=page.user_id,
        folder_id=page.folder_id,
        slug=page.slug,
        title=page.title,
        page_type=page.page_type,
        markdown_content=page.markdown_content,
        content_markdown=page.markdown_content,
        yaml_metadata=meta,
        metadata_json=meta,
        wikilinks=page.wikilinks or [],
        summary=summary_val,
        backlinks_count=meta.get("backlinks_count", 0),
        created_at=page.created_at,
        updated_at=page.updated_at,
    )

    return WikiPageResponseEnvelope(
        success=True,
        data=page_detail,
    )


@router.post(
    "/research-gaps",
    response_model=ResearchGapsResponseEnvelope,
    summary="Khai phá khoảng trống nghiên cứu và đề xuất đề tài mới (Spec 05 §4.E)",
    description=(
        "Tự động quét và tổng hợp các hạn chế (Limitations), điểm nghẽn chưa giải quyết "
        "(Unsolved Frontiers) từ siêu dữ liệu bài báo hoặc trang wiki, đồng thời gợi ý đề tài mới."
    ),
    responses={
        200: {"description": "Tổng hợp khoảng trống nghiên cứu và gợi ý đề tài thành công."},
        401: {"model": ErrorResponse, "description": "Chưa xác thực người dùng."},
        404: {"model": ErrorResponse, "description": "Thư mục không tồn tại."},
    },
)
async def synthesize_research_gaps(
    payload: ResearchGapsRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResearchGapsResponseEnvelope:
    """Synthesize cross-paper research limitations and suggest novel thesis topics."""
    # 1. Validate folder if provided
    if payload.folder_id is not None:
        folder_stmt = select(FolderModel).where(
            FolderModel.id == payload.folder_id,
            FolderModel.user_id == current_user.id,
        )
        folder_res = await db.execute(folder_stmt)
        if folder_res.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "FOLDER_NOT_FOUND",
                    "message": "Không tìm thấy thư mục đề tài yêu cầu.",
                    "field": "folder_id",
                    "action": "Chọn thư mục tồn tại trong cây thư mục cá nhân.",
                },
            )

    # 2. Fetch accessible documents
    stmt_docs = select(DocumentModel).where(DocumentModel.user_id == current_user.id)
    if payload.folder_id is not None:
        stmt_docs = stmt_docs.where(DocumentModel.folder_id == payload.folder_id)
    stmt_docs = stmt_docs.order_by(DocumentModel.created_at.desc()).limit(100)
    docs = list((await db.execute(stmt_docs)).scalars().all())

    # 3. Fetch any wiki research_gap pages
    stmt_wiki = select(WikiPageModel).where(
        WikiPageModel.user_id == current_user.id,
        WikiPageModel.page_type == "research_gap",
    )
    if payload.folder_id is not None:
        stmt_wiki = stmt_wiki.where(WikiPageModel.folder_id == payload.folder_id)
    gap_pages = list((await db.execute(stmt_wiki)).scalars().all())

    # 4. Extract and synthesize limitations
    unsolved_frontiers: list[UnsolvedFrontierItem] = []
    suggested_topics: list[SuggestedTopicItem] = []

    # Process explicit wiki gap pages
    for wp in gap_pages:
        meta = wp.yaml_metadata or {}
        domain_name = meta.get("domain") or wp.title
        bottleneck = meta.get("bottleneck") or wp.markdown_content[:250]
        acknowledged = meta.get("acknowledged_by") or [wp.title]
        if isinstance(acknowledged, str):
            acknowledged = [acknowledged]
        unsolved_frontiers.append(
            UnsolvedFrontierItem(
                domain=domain_name,
                acknowledged_by=acknowledged,
                bottleneck_description=bottleneck,
                potential_solution=meta.get(
                    "potential_solution", "Cần nghiên cứu phương pháp khắc phục."
                ),
            )
        )

    # Process document limitations & metadata
    for doc in docs:
        parsed_meta = doc.parsed_metadata or {}
        doc_citation = (
            f"{doc.title} ({doc.publication_year})"
            if doc.publication_year and doc.title
            else (doc.title or doc.filename or "Scholarly Document")
        )

        # Check for explicit limitations in metadata
        raw_limits: list[str] = []
        if isinstance(parsed_meta.get("limitations"), list):
            raw_limits.extend([str(item) for item in parsed_meta["limitations"] if item])
        elif isinstance(parsed_meta.get("limitations"), str):
            raw_limits.append(parsed_meta["limitations"])

        # Check in summary_metadata
        summary_meta = parsed_meta.get("summary_metadata")
        if isinstance(summary_meta, dict) and summary_meta.get("limitations"):
            sm_limits = summary_meta["limitations"]
            if isinstance(sm_limits, list):
                raw_limits.extend([str(item) for item in sm_limits if item])
            elif isinstance(sm_limits, str):
                raw_limits.append(sm_limits)

        # Check for open_challenges or future_work
        for alt_key in ("open_challenges", "future_work", "weaknesses"):
            if isinstance(parsed_meta.get(alt_key), list):
                raw_limits.extend([str(item) for item in parsed_meta[alt_key] if item])

        for limit_text in raw_limits:
            domain = "Computational Complexity & Efficiency"
            clean_limit = limit_text.strip()
            low_limit = clean_limit.lower()
            if any(
                term in low_limit
                for term in ["memory", "footprint", "scale", "scalability", "complexity", "o(n"]
            ):
                domain = "Efficiency & Long-Context Scalability"
            elif any(
                term in low_limit
                for term in [
                    "accuracy",
                    "robustness",
                    "adversarial",
                    "noise",
                    "hallucination",
                ]
            ):
                domain = "Robustness & Trustworthiness"
            elif any(
                term in low_limit
                for term in ["generalization", "domain", "cross-lingual", "out-of-distribution"]
            ):
                domain = "Domain Generalization"

            unsolved_frontiers.append(
                UnsolvedFrontierItem(
                    domain=domain,
                    acknowledged_by=[doc_citation],
                    bottleneck_description=clean_limit,
                    potential_solution="Khảo sát kiến trúc thích ứng động hoặc nén mô hình.",
                )
            )

    # If query is specified or frontiers are still empty, synthesize frontier matching context
    if payload.query:
        query_text = payload.query.strip()
        matching_citations = [
            f"{d.title} ({d.publication_year or 2024})" for d in docs[:3] if d.title
        ] or ["Scholarly Literature Review"]
        unsolved_frontiers.append(
            UnsolvedFrontierItem(
                domain=query_text,
                acknowledged_by=matching_citations,
                bottleneck_description=(
                    f"Rào cản học thuật và điểm nghẽn chưa có lời giải liên quan '{query_text}'."
                ),
                potential_solution=(
                    "Áp dụng cấu trúc lai (Hybrid Architecture), State Space Models "
                    "hoặc kỹ thuật tối ưu hóa tham số thích ứng."
                ),
            )
        )

    # Deduplicate frontiers by domain / bottleneck similarity
    seen_bottlenecks: set[str] = set()
    deduped_frontiers: list[UnsolvedFrontierItem] = []
    for f in unsolved_frontiers:
        key = f.bottleneck_description.strip().lower()
        if key not in seen_bottlenecks:
            seen_bottlenecks.add(key)
            deduped_frontiers.append(f)

    # Synthesize suggested thesis / research topics from identified frontiers
    if deduped_frontiers:
        for frontier in deduped_frontiers[:3]:
            suggested_topics.append(
                SuggestedTopicItem(
                    title=f"Nghiên cứu nâng cao hiệu quả và giải quyết {frontier.domain.lower()}",
                    rationale=(
                        f"Khắc phục điểm nghẽn: '{frontier.bottleneck_description[:100]}' "
                        f"đã được chỉ ra bởi {', '.join(frontier.acknowledged_by[:2])}."
                    ),
                )
            )
    elif payload.query:
        suggested_topics.append(
            SuggestedTopicItem(
                title=f"Giải pháp tối ưu hóa toàn diện cho {payload.query}",
                rationale="Khắc phục các rào cản tính toán và cải thiện độ chuẩn xác thực nghiệm.",
            )
        )

    response_data = ResearchGapsResponse(
        folder_id=payload.folder_id,
        unsolved_frontiers=deduped_frontiers,
        suggested_topics=suggested_topics,
        total_papers_analyzed=len(docs),
    )

    return ResearchGapsResponseEnvelope(
        success=True,
        data=response_data,
    )
