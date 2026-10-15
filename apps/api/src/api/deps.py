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
from api.services.ai_tracing_service import AITracingService
from api.services.auth_service import AuthService
from api.services.document_service import DocumentService
from api.services.draft_service import DraftService
from api.services.note_service import NoteService
from api.services.note_synthesis_service import NoteSynthesisService
from api.services.session_chat_service import SessionChatService
from api.services.session_service import SessionService

DEFAULT_DEV_USER_ID = UUID("00000000-0000-0000-0000-000000000001")

_idempotency_adapter: IIdempotencyPort | None = None
_pdf_annotator_adapter: IPdfAnnotatorPort | None = None
_ai_tracing_service: AITracingService | None = None


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


def get_ai_tracing_service() -> AITracingService:
    """Dependency providing AITracingService singleton instance."""
    global _ai_tracing_service
    if _ai_tracing_service is None:
        _ai_tracing_service = AITracingService()
    return _ai_tracing_service


def get_document_service(
    storage: IBlobStoragePort = Depends(get_storage),
    summarizer: IDocumentSummarizerPort = Depends(get_document_summarizer),
    pdf_annotator: IPdfAnnotatorPort = Depends(get_pdf_annotator),
    ai_tracing: AITracingService = Depends(get_ai_tracing_service),
) -> DocumentService:
    """Dependency providing DocumentService instance."""
    return DocumentService(
        storage=storage,
        summarizer=summarizer,
        pdf_annotator=pdf_annotator,
        ai_tracing=ai_tracing,
    )


def get_session_service(
    db: AsyncSession = Depends(get_db),
    document_service: DocumentService = Depends(get_document_service),
) -> SessionService:
    """Dependency providing SessionService instance bound to request database session."""
    return SessionService(db=db, document_service=document_service)


def get_session_chat_service(
    db: AsyncSession = Depends(get_db),
    ai_tracing: AITracingService = Depends(get_ai_tracing_service),
) -> SessionChatService:
    """Dependency providing SessionChatService instance bound to request database session."""
    return SessionChatService(db=db, ai_tracing=ai_tracing)


def get_note_service(
    db: AsyncSession = Depends(get_db),
) -> NoteService:
    """Dependency providing NoteService instance bound to request database session."""
    return NoteService(db=db)


def get_note_synthesis_service(
    db: AsyncSession = Depends(get_db),
    ai_tracing: AITracingService = Depends(get_ai_tracing_service),
) -> NoteSynthesisService:
    """Dependency providing NoteSynthesisService instance bound to request database session."""
    return NoteSynthesisService(db=db, ai_tracing=ai_tracing)


def get_auth_service(
    db: AsyncSession = Depends(get_db),
) -> AuthService:
    """Dependency providing AuthService bound to request database session."""
    return AuthService(db=db)


def get_draft_service(
    db: AsyncSession = Depends(get_db),
) -> DraftService:
    """Dependency providing DraftService bound to request database session."""
    return DraftService(db=db)


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> UserModel:
    """Authenticate and retrieve current user.

    1. Checks Authorization header for Bearer JWT token.
       - Decodes and verifies HMAC-SHA256 JWT.
       - Rejects with 401 Unauthorized if invalid/expired/missing claims.
    2. Fallback for unit tests:
       - If no Authorization header, checks X-User-Id header.
       - Returns or creates test user.
    3. Rejects with 401 Unauthorized if neither valid token nor X-User-Id header is provided.
    """
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    if auth_header:
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_AUTH_HEADER",
                    "message": "Header Authorization phải bắt đầu bằng scheme 'Bearer '.",
                    "action": "Use Authorization: Bearer <token>",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = auth_header[7:].strip()
        try:
            claims = AuthService.decode_token(token)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_TOKEN",
                    "message": f"Token xác thực không hợp lệ hoặc đã hết hạn: {exc}",
                    "action": "Log in again to obtain a valid access token.",
                },
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        user_id_str = claims.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_TOKEN_CLAIMS",
                    "message": "Token thiếu thông tin định danh người dùng.",
                    "action": "Log in again.",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        try:
            user_id = UUID(user_id_str)
        except (ValueError, TypeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_USER_ID",
                    "message": "ID người dùng trong token không hợp lệ.",
                },
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": "Người dùng không tồn tại hoặc tài khoản bị khóa.",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    # Fallback compatibility for unit tests (X-User-Id)
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
                role="researcher",
                institution="VeriScholar Lab",
                academic_rank="Core Developer",
                is_verified=True,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return user

    # Neither Authorization nor X-User-Id provided -> reject with 401 Unauthorized
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "code": "UNAUTHORIZED",
            "message": "Yêu cầu cần xác thực. Vui lòng cung cấp Authorization header.",
            "action": "Provide Authorization: Bearer <token> in request headers.",
        },
        headers={"WWW-Authenticate": "Bearer"},
    )
