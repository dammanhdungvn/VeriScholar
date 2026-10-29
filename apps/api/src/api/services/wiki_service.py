"""Academic Wiki Persistence and Exploration Service (Spec 05 §1.D, §3).

Provides database persistence and retrieval for Compiled Academic LLM Wiki pages,
supporting slug lookup, tenant-isolated listings, in-place upserts, and
seamless compilation of WikiPageDraft domain models into Markdown with [[wikilinks]].
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import structlog
from api.db.models.wiki import WikiPageModel
from core.models.wiki import WikiPageDraft
from core.services.wiki_compiler import WikiCompiler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger("api.services.wiki_service")


class WikiService:
    """Service managing compiled academic markdown pages stored in wiki_pages."""

    def __init__(
        self,
        db: AsyncSession | None = None,
        compiler: WikiCompiler | None = None,
    ) -> None:
        self.db = db
        self.compiler = compiler or WikiCompiler()

    def _resolve_session(
        self,
        explicit_db: AsyncSession | None = None,
    ) -> AsyncSession:
        """Resolve database session from method argument or instance binding."""
        session = explicit_db or self.db
        if session is None:
            raise ValueError(
                "AsyncSession must be provided either when instantiating WikiService "
                "or passed explicitly to service methods."
            )
        return session

    async def get_page_by_slug(
        self,
        *args: Any,
        user_id: UUID | None = None,
        slug: str | None = None,
        db: AsyncSession | None = None,
    ) -> WikiPageModel | None:
        """Retrieve a wiki page by user_id and slug.

        Supports both:
            await service.get_page_by_slug(user_id, slug)
            await service.get_page_by_slug(db, user_id, slug)
        """
        resolved_db = db
        resolved_user_id = user_id
        resolved_slug = slug

        if len(args) == 3 and isinstance(args[0], AsyncSession):
            resolved_db = args[0]
            resolved_user_id = args[1]
            resolved_slug = args[2]
        elif len(args) == 2:
            if isinstance(args[0], AsyncSession):
                resolved_db = args[0]
                resolved_user_id = args[1]
            else:
                resolved_user_id = args[0]
                resolved_slug = args[1]
        elif len(args) == 1:
            if isinstance(args[0], AsyncSession):
                resolved_db = args[0]
            else:
                resolved_user_id = args[0]

        session = self._resolve_session(resolved_db)
        if resolved_user_id is None or resolved_slug is None:
            raise ValueError("Both user_id and slug must be provided.")

        if not isinstance(resolved_user_id, UUID):
            resolved_user_id = UUID(str(resolved_user_id))

        stmt = select(WikiPageModel).where(
            WikiPageModel.user_id == resolved_user_id,
            WikiPageModel.slug == str(resolved_slug),
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_pages(
        self,
        *args: Any,
        user_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
        folder_id: UUID | None = None,
        db: AsyncSession | None = None,
    ) -> list[WikiPageModel]:
        """List wiki pages belonging to a user with pagination and optional folder filter.

        Supports both:
            await service.list_pages(user_id, limit=50, offset=0)
            await service.list_pages(db, user_id, limit=50, offset=0)
        """
        resolved_db = db
        resolved_user_id = user_id

        if len(args) >= 2 and isinstance(args[0], AsyncSession):
            resolved_db = args[0]
            resolved_user_id = args[1]
            if len(args) >= 3 and isinstance(args[2], int):
                limit = args[2]
            if len(args) >= 4 and isinstance(args[3], int):
                offset = args[3]
        elif len(args) >= 1:
            if isinstance(args[0], AsyncSession):
                resolved_db = args[0]
            else:
                resolved_user_id = args[0]
                if len(args) >= 2 and isinstance(args[1], int):
                    limit = args[1]
                if len(args) >= 3 and isinstance(args[2], int):
                    offset = args[2]

        session = self._resolve_session(resolved_db)
        if resolved_user_id is None:
            raise ValueError("user_id must be provided to list_pages.")

        if not isinstance(resolved_user_id, UUID):
            resolved_user_id = UUID(str(resolved_user_id))

        stmt = (
            select(WikiPageModel)
            .where(WikiPageModel.user_id == resolved_user_id)
            .order_by(WikiPageModel.updated_at.desc(), WikiPageModel.title.asc())
            .offset(offset)
            .limit(limit)
        )

        if folder_id is not None:
            stmt = stmt.where(WikiPageModel.folder_id == folder_id)

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def upsert_page(
        self,
        *args: Any,
        user_id: UUID | None = None,
        title: str | None = None,
        markdown: str | None = None,
        markdown_content: str | None = None,
        yaml_metadata: dict[str, Any] | None = None,
        metadata_json: dict[str, Any] | None = None,
        wikilinks: list[str] | None = None,
        slug: str | None = None,
        embedding: list[float] | None = None,
        page_type: str = "topic",
        folder_id: UUID | None = None,
        db: AsyncSession | None = None,
    ) -> WikiPageModel:
        """Create or update a wiki page.

        If a page with (user_id, slug) exists, it is updated in-place;
        otherwise, a new WikiPageModel row is inserted.
        """
        resolved_db = db
        resolved_user_id = user_id

        # Normalize positional arguments whether starting with db or user_id
        if len(args) >= 1 and isinstance(args[0], AsyncSession):
            resolved_db = args[0]
            pos_args = args[1:]
        else:
            pos_args = args

        if len(pos_args) >= 1 and pos_args[0] is not None:
            resolved_user_id = pos_args[0]
        if len(pos_args) >= 2 and pos_args[1] is not None:
            title = pos_args[1]
        if len(pos_args) >= 3 and pos_args[2] is not None:
            markdown = pos_args[2]
        if len(pos_args) >= 4 and pos_args[3] is not None:
            yaml_metadata = pos_args[3]
        if len(pos_args) >= 5 and pos_args[4] is not None:
            wikilinks = pos_args[4]
        if len(pos_args) >= 6 and pos_args[5] is not None:
            slug = pos_args[5]
        if len(pos_args) >= 7 and pos_args[6] is not None:
            embedding = pos_args[6]
        if len(pos_args) >= 8 and pos_args[7] is not None:
            page_type = pos_args[7]
        if len(pos_args) >= 9 and pos_args[8] is not None:
            folder_id = pos_args[8]

        session = self._resolve_session(resolved_db)
        if resolved_user_id is None:
            raise ValueError("user_id must be provided to upsert_page.")

        if not isinstance(resolved_user_id, UUID):
            resolved_user_id = UUID(str(resolved_user_id))

        raw_content = markdown or markdown_content or ""
        meta = yaml_metadata or metadata_json or {}

        if not title:
            # Fallback title from metadata or slug
            title = str(meta.get("title") or slug or "Untitled Academic Concept")

        page_slug = slug or self.compiler.slugify(title)
        links = wikilinks if wikilinks is not None else self.compiler.extract_wikilinks(raw_content)

        # Check existing
        stmt = select(WikiPageModel).where(
            WikiPageModel.user_id == resolved_user_id,
            WikiPageModel.slug == page_slug,
        )
        existing = (await session.execute(stmt)).scalar_one_or_none()

        if existing is not None:
            existing.title = title
            existing.markdown_content = raw_content
            existing.yaml_metadata = meta
            existing.wikilinks = links
            existing.page_type = page_type
            if folder_id is not None:
                existing.folder_id = folder_id
            if embedding is not None:
                existing.embedding = embedding
            existing.updated_at = datetime.now(UTC)
            await session.flush()
            logger.info("wiki_page_updated", user_id=str(resolved_user_id), slug=page_slug)
            return existing

        new_page = WikiPageModel(
            user_id=resolved_user_id,
            folder_id=folder_id,
            slug=page_slug,
            title=title,
            page_type=page_type,
            markdown_content=raw_content,
            yaml_metadata=meta,
            wikilinks=links,
            embedding=embedding,
        )
        session.add(new_page)
        await session.flush()
        logger.info("wiki_page_created", user_id=str(resolved_user_id), slug=page_slug)
        return new_page

    async def save_page(
        self,
        *args: Any,
        user_id: UUID | None = None,
        draft: WikiPageDraft | None = None,
        embedding: list[float] | None = None,
        folder_id: UUID | None = None,
        page_type: str = "topic",
        db: AsyncSession | None = None,
    ) -> WikiPageModel:
        """Compile a WikiPageDraft domain model into structured markdown and persist."""
        resolved_db = db
        resolved_user_id = user_id
        resolved_draft = draft

        if len(args) >= 3 and isinstance(args[0], AsyncSession):
            resolved_db = args[0]
            resolved_user_id = args[1]
            resolved_draft = args[2]
        elif len(args) >= 2:
            if isinstance(args[0], AsyncSession):
                resolved_db = args[0]
                resolved_user_id = args[1]
            else:
                resolved_user_id = args[0]
                resolved_draft = args[1]
        elif len(args) >= 1:
            if isinstance(args[0], AsyncSession):
                resolved_db = args[0]
            else:
                resolved_user_id = args[0]

        if resolved_draft is None:
            raise ValueError("WikiPageDraft must be provided to save_page.")

        if isinstance(resolved_draft, WikiPageDraft):
            compiled = self.compiler.compile_page(resolved_draft)
        elif isinstance(resolved_draft, str):
            compiled = self.compiler.parse_markdown(resolved_draft)
        elif isinstance(resolved_draft, dict):
            compiled = self.compiler.compile_page(WikiPageDraft(**resolved_draft))
        else:
            raise TypeError(f"Unsupported draft type: {type(resolved_draft)}")

        return await self.upsert_page(
            user_id=resolved_user_id,
            title=compiled.title,
            markdown=compiled.markdown,
            yaml_metadata=compiled.yaml_metadata,
            wikilinks=compiled.wikilinks,
            slug=compiled.slug,
            embedding=embedding,
            folder_id=folder_id,
            page_type=page_type,
            db=resolved_db,
        )

    async def delete_page(
        self,
        *args: Any,
        user_id: UUID | None = None,
        slug: str | None = None,
        db: AsyncSession | None = None,
    ) -> bool:
        """Delete a wiki page by slug. Returns True if deleted, False if not found."""
        page = await self.get_page_by_slug(*args, user_id=user_id, slug=slug, db=db)
        if page is None:
            return False

        explicit_session = db or (args[0] if args and isinstance(args[0], AsyncSession) else None)
        session = self._resolve_session(explicit_session)
        await session.delete(page)
        await session.flush()
        logger.info("wiki_page_deleted", user_id=str(page.user_id), slug=page.slug)
        return True
