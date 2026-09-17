"""Dependencies for FastAPI endpoints."""

from uuid import UUID

from core.adapters.cache.idempotency import InMemoryIdempotencyAdapter
from core.adapters.storage.local import LocalStorageAdapter
from core.ports.idempotency import IIdempotencyPort
from core.ports.pdf_annotator import IPdfAnnotatorPort
from core.ports.storage import IBlobStoragePort
from core.ports.summary import IDocumentSummarizerPort
from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.adapters.heuristic_summarizer import HeuristicGroundedSummarizer
from api.adapters.llm_summarizer import LLMGroundedSummarizer
from api.adapters.pdf_annotator import PyMuPdfAnnotator
from api.core.config import settings
from api.db.models.user import UserModel
from api.db.session import get_db
from api.services.document_service import DocumentService
from api.services.note_service import NoteService
from api.services.note_synthesis_service import NoteSynthesisService
from api.services.session_chat_service import SessionChatService
from api.services.session_service import SessionService

DEFAULT_DEV_USER_ID = UUID("00000000-0000-0000-0000-000000000001")

_idempotency_adapter: IIdempotencyPort | None = None
_pdf_annotator_adapter: IPdfAnnotatorPort | None = None


def get_storage() -> IBlobStoragePort:
    """Dependency providing Blob Storage Port instance."""
    return LocalStorageAdapter(base_directory=settings.STORAGE_DIR)


def get_idempotency_port() -> IIdempotencyPort:
    """Dependency providing Idempotency Port singleton instance."""
    global _idempotency_adapter
    if _idempotency_adapter is None:
        _idempotency_adapter = InMemoryIdempotencyAdapter()
    return _idempotency_adapter


def get_pdf_annotator() -> IPdfAnnotatorPort:
    """Dependency providing PDF annotation engine adapter."""
    global _pdf_annotator_adapter
    if _pdf_annotator_adapter is None:
        _pdf_annotator_adapter = PyMuPdfAnnotator()
    return _pdf_annotator_adapter


def get_document_summarizer() -> IDocumentSummarizerPort:
    """Dependency providing LLMGroundedSummarizer with heuristic fallback."""
    api_key = settings.OPENAI_API_KEY.get_secret_value() if settings.OPENAI_API_KEY else None
    return LLMGroundedSummarizer(
        api_key=api_key,
        base_url=settings.OPENAI_BASE_URL,
        model=settings.OPENAI_MODEL,
        fallback=HeuristicGroundedSummarizer(),
    )


def get_document_service(
    storage: IBlobStoragePort = Depends(get_storage),
    summarizer: IDocumentSummarizerPort = Depends(get_document_summarizer),
    pdf_annotator: IPdfAnnotatorPort = Depends(get_pdf_annotator),
) -> DocumentService:
    """Dependency providing DocumentService instance."""
    return DocumentService(
        storage=storage,
        summarizer=summarizer,
        pdf_annotator=pdf_annotator,
    )


def get_session_service(
    db: AsyncSession = Depends(get_db),
) -> SessionService:
    """Dependency providing SessionService instance bound to request database session."""
    return SessionService(db=db)


def get_session_chat_service(
    db: AsyncSession = Depends(get_db),
) -> SessionChatService:
    """Dependency providing SessionChatService instance bound to request database session."""
    return SessionChatService(db=db)


def get_note_service(
    db: AsyncSession = Depends(get_db),
) -> NoteService:
    """Dependency providing NoteService instance bound to request database session."""
    return NoteService(db=db)


def get_note_synthesis_service(
    db: AsyncSession = Depends(get_db),
) -> NoteSynthesisService:
    """Dependency providing NoteSynthesisService instance bound to request database session."""
    return NoteSynthesisService(db=db)


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> UserModel:
    """Provide authenticated user from X-User-Id header or fallback to default dev user."""
    user_id = DEFAULT_DEV_USER_ID
    custom_uid_header = request.headers.get("x-user-id") or request.headers.get("X-User-Id")
    if custom_uid_header:
        try:
            user_id = UUID(custom_uid_header)
        except (ValueError, TypeError):
            user_id = DEFAULT_DEV_USER_ID

    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        user = UserModel(
            id=user_id,
            email=f"user_{user_id.hex[:8]}@verischolar.org"
            if user_id != DEFAULT_DEV_USER_ID
            else "developer@verischolar.org",
            full_name="VeriScholar User"
            if user_id != DEFAULT_DEV_USER_ID
            else "VeriScholar Developer",
            hashed_password="dev_dummy_password",
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user
