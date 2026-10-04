"""Dependencies for FastAPI endpoints."""

from uuid import UUID

from core.adapters.cache.idempotency import InMemoryIdempotencyAdapter
from core.adapters.storage.local import LocalStorageAdapter
from core.ports.idempotency import IIdempotencyPort
from core.ports.pdf_annotator import IPdfAnnotatorPort
from core.ports.storage import IBlobStoragePort
from core.ports.summary import IDocumentSummarizerPort
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.adapters.heuristic_summarizer import HeuristicGroundedSummarizer
from api.adapters.llm_summarizer import LLMGroundedSummarizer
from api.adapters.pdf_annotator import PyMuPdfAnnotator
from api.core.config import settings
from api.db.models.user import UserModel
from api.db.session import get_db
from api.services.auth_service import AuthService
from api.services.document_service import DocumentService
from api.services.draft_service import DraftService
from api.services.folder_service import FolderService
from api.services.library_service import LibraryService
from api.services.note_service import NoteService
from api.services.note_synthesis_service import NoteSynthesisService
from api.services.reference_service import ReferenceService
from api.services.session_chat_service import SessionChatService
from api.services.session_service import SessionService
from api.services.share_service import ShareService

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


def get_folder_service(
    db: AsyncSession = Depends(get_db),
) -> FolderService:
    """Dependency providing FolderService instance bound to request database session."""
    return FolderService(db=db)


def get_library_service(
    db: AsyncSession = Depends(get_db),
) -> LibraryService:
    """Dependency providing LibraryService instance bound to request database session."""
    return LibraryService(db=db)


def get_reference_service(
    db: AsyncSession = Depends(get_db),
) -> ReferenceService:
    """Dependency providing ReferenceService instance bound to request database session."""
    return ReferenceService(db=db)


def get_share_service(
    db: AsyncSession = Depends(get_db),
    storage: IBlobStoragePort = Depends(get_storage),
) -> ShareService:
    """Dependency providing ShareService instance bound to request database session and storage."""
    return ShareService(db=db, storage=storage)


def get_draft_service(
    db: AsyncSession = Depends(get_db),
    storage: IBlobStoragePort = Depends(get_storage),
) -> DraftService:
    """Dependency providing DraftService instance bound to request database session and storage."""
    return DraftService(db=db, storage=storage)


_auth_service: AuthService | None = None


def get_auth_service() -> AuthService:
    """Dependency providing AuthService singleton instance."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserModel:
    """Provide authenticated user from Bearer JWT token or fallback to dev user when permitted."""
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        payload = auth_service.decode_token(token, expected_type="access")
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_TOKEN",
                    "message": "Token subject is missing.",
                    "field": "Authorization",
                    "action": "Authenticate with valid token.",
                },
            )
        try:
            user_id = UUID(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_TOKEN",
                    "message": "Token subject is invalid UUID.",
                    "field": "Authorization",
                    "action": "Authenticate with valid token.",
                },
            )
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "USER_NOT_FOUND_OR_INACTIVE",
                    "message": "Authenticated user account does not exist or is inactive.",
                    "field": "Authorization",
                    "action": "Log in again.",
                },
            )
        return user

    # If no Bearer token provided, check if dev auth bypass is allowed
    if not settings.allow_dev_auth_bypass:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "AUTHENTICATION_REQUIRED",
                "message": "Authentication required. Missing Bearer token in Authorization header.",
                "field": "Authorization",
                "action": "Provide valid Bearer token in Authorization header.",
            },
        )

    # Dev auth bypass for local testing & backwards compatibility
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
