"""Proactive Scholarly Associative Memory Service (Pillar 3).

Cross-references active writing drafts against historical user research notes
to deliver real-time associative insights, citation links, and knowledge retrieval.
"""

from __future__ import annotations

import re
from uuid import UUID

import structlog
from api.db.models.document import DocumentModel
from api.db.models.folder import FolderModel
from api.db.models.note import ResearchNoteModel
from api.services.ai_tracing_service import AITracingService
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger("api.services.associative_memory")


class AssociativeSuggestionItem(BaseModel):
    """A proactive suggestion linking draft text to a user's past research note."""

    model_config = ConfigDict(extra="ignore")

    note_id: UUID = Field(description="Unique identifier of the matching research note.")
    document_id: UUID | None = Field(default=None, description="Source paper UUID.")
    document_title: str = Field(description="Title of the source paper.")
    paper_title: str | None = Field(default=None, description="Alias for document_title.")
    folder_name: str | None = Field(default=None, description="Folder containing the source paper.")
    page_number: int = Field(description="Page number where the note was taken.")
    selected_text: str = Field(description="Original quote excerpt from the paper.")
    user_note: str | None = Field(default=None, description="User's personal synthetic insight.")
    note_content: str = Field(default="", description="Alias for user_note or selected_text.")
    similarity_score: float = Field(ge=0.0, le=1.0, description="Relevance score (0.0 to 1.0).")
    suggested_citation: str = Field(description="Ready-to-insert LaTeX citation tag.")
    reason: str = Field(description="Explanation of the conceptual alignment.")
    relevance_explanation: str = Field(default="", description="Alias for reason.")
    matched_keywords: list[str] = Field(default_factory=list)


class AssociativeSuggestionsRequest(BaseModel):
    """Payload for retrieving associative memory suggestions."""

    model_config = ConfigDict(extra="ignore")

    content: str | None = Field(
        default=None,
        max_length=10000,
        description="Current paragraph or sentence being drafted. If omitted, uses draft body.",
        examples=["Multi-head attention allows the model to jointly attend to information."],
    )
    text: str | None = Field(
        default=None,
        max_length=10000,
        description="Alias for content.",
    )
    max_results: int = Field(
        default=3,
        ge=1,
        le=50,
        description="Maximum number of proactive suggestions to return.",
    )
    limit: int | None = Field(
        default=None,
        ge=1,
        le=50,
        description="Alias for max_results.",
    )
    min_similarity: float = Field(
        default=0.15,
        ge=0.0,
        le=1.0,
        description="Minimum threshold for similarity.",
    )


class AssociativeSuggestionsResponse(BaseModel):
    """Response containing proactive associative knowledge suggestions."""

    model_config = ConfigDict(extra="ignore")

    draft_id: UUID = Field(description="ID of the draft.")
    query_excerpt: str = Field(description="Evaluated text excerpt.")
    total_found: int = Field(description="Total candidate notes matching the conceptual domain.")
    suggestions: list[AssociativeSuggestionItem] = Field(
        default_factory=list,
        description="Ranked list of relevant historical notes.",
    )


class AssociativeMemoryService:
    """Service providing proactive associative memory recall for academic writing."""

    def __init__(self, db: AsyncSession, ai_tracing: AITracingService | None = None) -> None:
        self.db = db
        self.ai_tracing = ai_tracing or AITracingService()

    def _tokenize(self, text: str) -> set[str]:
        """Extract normalized alphanumeric words for lexical overlap calculation."""
        words = re.findall(r"\b[a-zA-Z0-9_\u00C0-\u024F\u1EA0-\u1EF9]{3,}\b", text.lower())
        stopwords = {
            "the",
            "and",
            "for",
            "with",
            "that",
            "this",
            "from",
            "which",
            "were",
            "have",
            "been",
            "their",
            "more",
            "also",
            "using",
            "into",
            "then",
            "them",
            "some",
            "trong",
            "nhung",
            "duoc",
            "chung",
            "theo",
            "nghien",
            "cuu",
            "tong",
            "hop",
        }
        return {w for w in words if w not in stopwords}

    def _compute_relevance(self, draft_tokens: set[str], note_text: str) -> float:
        """Compute jaccard/lexical similarity score between draft tokens and note."""
        note_tokens = self._tokenize(note_text)
        if not draft_tokens or not note_tokens:
            return 0.0

        intersection = draft_tokens & note_tokens
        if not intersection:
            return 0.0

        overlap_score = len(intersection) / max(len(draft_tokens), 1)
        jaccard = len(intersection) / len(draft_tokens | note_tokens)
        score = 0.7 * overlap_score + 0.3 * jaccard
        return min(0.99, max(0.0, score))

    async def get_suggestions_for_draft(
        self,
        user_id: UUID,
        draft_id: UUID,
        request: AssociativeSuggestionsRequest,
    ) -> AssociativeSuggestionsResponse:
        """Scan user's historical notes and return ranked conceptual associations."""
        effective_content = request.content or request.text
        if not effective_content or not effective_content.strip():
            from api.db.models.draft import DraftModel

            draft_stmt = select(DraftModel).where(
                (DraftModel.id == draft_id) & (DraftModel.user_id == user_id)
            )
            draft_obj = (await self.db.execute(draft_stmt)).scalar_one_or_none()
            effective_content = draft_obj.content if draft_obj and draft_obj.content else ""

        draft_tokens = self._tokenize(effective_content)
        query_excerpt = effective_content[:120].strip()
        if len(effective_content) > 120:
            query_excerpt += "..."

        target_limit = request.limit or request.max_results or 3
        min_thresh = request.min_similarity if request.min_similarity is not None else 0.15

        with self.ai_tracing.retriever(
            name="associative_memory_recall",
            input={"draft_id": str(draft_id), "excerpt": query_excerpt},
            metadata={"target_limit": target_limit, "min_thresh": min_thresh},
        ) as trace_span:
            # 1. Fetch user's research notes with attached documents
            stmt = (
                select(ResearchNoteModel, DocumentModel)
                .outerjoin(DocumentModel, ResearchNoteModel.document_id == DocumentModel.id)
                .where(ResearchNoteModel.user_id == user_id)
                .order_by(ResearchNoteModel.created_at.desc())
                .limit(100)
            )
            result = await self.db.execute(stmt)
            records = result.all()

            scored_candidates: list[tuple[float, ResearchNoteModel, DocumentModel | None]] = []
            for note, doc in records:
                combined_text = f"{note.user_note or ''} {note.selected_text or ''}"
                score = self._compute_relevance(draft_tokens, combined_text)
                if score >= min_thresh:
                    scored_candidates.append((score, note, doc))

            # Sort descending by relevance score
            scored_candidates.sort(key=lambda x: x[0], reverse=True)
            top_candidates = scored_candidates[:target_limit]

            suggestions: list[AssociativeSuggestionItem] = []
            for score, note, doc in top_candidates:
                doc_title = (doc.title or doc.filename) if doc else "Ghi chú tri thức"
                year_val = doc.publication_year if doc else None
                year_str = str(year_val) if year_val else "2024"
                author_tag = (
                    doc.authors[0].split()[-1].lower()
                    if (doc and doc.authors and len(doc.authors) > 0)
                    else "author"
                )
                citation_key = f"\\cite{{{author_tag}{year_str}}}"

                # Fetch folder name if document is in a folder
                folder_name: str | None = None
                if doc and doc.folder_id:
                    folder_stmt = (
                        select(FolderModel.name).where(FolderModel.id == doc.folder_id).limit(1)
                    )
                    folder_res = await self.db.execute(folder_stmt)
                    folder_name = folder_res.scalar_one_or_none()

                relevance_reason = (
                    f"Đoạn văn đang viết có các thuật ngữ tương đồng cao với ghi chú tại bài "
                    f"'{doc_title}' (Trang {note.page_number})."
                )
                combined_note_text = f"{note.user_note or ''} {note.selected_text or ''}"
                matched_kw = sorted(list(draft_tokens & self._tokenize(combined_note_text)))

                suggestions.append(
                    AssociativeSuggestionItem(
                        note_id=note.id,
                        document_id=doc.id if doc else None,
                        document_title=doc_title,
                        paper_title=doc_title,
                        folder_name=folder_name,
                        page_number=note.page_number,
                        selected_text=note.selected_text[:200],
                        user_note=note.user_note,
                        note_content=note.user_note or note.selected_text,
                        similarity_score=round(score, 3),
                        suggested_citation=citation_key,
                        reason=relevance_reason,
                        relevance_explanation=relevance_reason,
                        matched_keywords=matched_kw,
                    )
                )

            trace_span.set_output(
                {
                    "returned_suggestions": len(suggestions),
                    "total_found": len(scored_candidates),
                }
            )
            if suggestions:
                top_score = float(suggestions[0].similarity_score)
                trace_span.score(name="top_note_similarity", value=top_score)

        logger.info(
            "associative_suggestions_generated",
            user_id=str(user_id),
            draft_id=str(draft_id),
            total_found=len(scored_candidates),
            returned=len(suggestions),
        )

        return AssociativeSuggestionsResponse(
            draft_id=draft_id,
            query_excerpt=query_excerpt,
            total_found=len(scored_candidates),
            suggestions=suggestions,
        )
