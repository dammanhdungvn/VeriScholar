"""Dependencies for FastAPI endpoints."""

import os
from uuid import UUID

from core.adapters.cache.idempotency import InMemoryIdempotencyAdapter, RedisIdempotencyAdapter
from core.adapters.storage.local import LocalStorageAdapter
from core.ports.academic_resolver import IAcademicSearchResolverPort
from core.ports.idempotency import IIdempotencyPort
from core.ports.scholarly_search import IScholarlySearchPort
from core.ports.storage import IBlobStoragePort
from core.ports.summary import IDocumentSummarizerPort
from core.services.academic_cache import GlobalAcademicCache
from core.services.exa_resolver import ExaAcademicResolverAdapter
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.adapters.heuristic_summarizer import HeuristicGroundedSummarizer
from api.adapters.llm_summarizer import LLMGroundedSummarizer
from api.core.config import settings
from api.db.models.user import UserModel
from api.db.session import get_db
from api.services.ai_tracing_service import AITracingService
from api.services.auth_service import AuthService
from api.services.benchmark_runner_service import BenchmarkRunnerService
from api.services.document_service import DocumentService
from api.services.draft_service import DraftService
from api.services.embedding_service import EmbeddingService
from api.services.folder_service import FolderService
from api.services.graph_extraction_service import GraphExtractionService
from api.services.graph_rag_service import GraphRAGService
from api.services.library_synthesis_service import LibrarySynthesisService
from api.services.note_service import NoteService
from api.services.session_chat_service import SessionChatService
from api.services.session_service import SessionService
from api.services.wiki_service import WikiService

DEFAULT_DEV_USER_ID = UUID("00000000-0000-0000-0000-000000000001")

_idempotency_adapter: IIdempotencyPort | None = None
_ai_tracing_service: AITracingService | None = None
_academic_cache: GlobalAcademicCache | None = None
_academic_resolver: IAcademicSearchResolverPort | None = None
_scholarly_search_port: IScholarlySearchPort | None = None


def get_academic_cache() -> GlobalAcademicCache:
    """Dependency providing GlobalAcademicCache singleton."""
    global _academic_cache
    if _academic_cache is None:
        _academic_cache = GlobalAcademicCache()
    return _academic_cache


def get_academic_resolver(
    cache: GlobalAcademicCache = Depends(get_academic_cache),
) -> IAcademicSearchResolverPort:
    """Dependency providing ExaAcademicResolverAdapter with InMemory fallback."""
    global _academic_resolver
    if _academic_resolver is None:
        api_key = settings.EXA_API_KEY.get_secret_value() if settings.EXA_API_KEY else None
        _academic_resolver = ExaAcademicResolverAdapter(
            api_key=api_key,
            cache=cache,
        )
    return _academic_resolver


def get_ai_tracing_service() -> AITracingService:
    """Dependency providing AITracingService singleton instance."""
    global _ai_tracing_service
    if _ai_tracing_service is None:
        _ai_tracing_service = AITracingService()
    return _ai_tracing_service


def get_scholarly_search_port(
    ai_tracing: AITracingService = Depends(get_ai_tracing_service),
) -> IScholarlySearchPort:
    """Dependency providing IScholarlySearchPort instance."""
    global _scholarly_search_port
    if _scholarly_search_port is None:
        from api.adapters.scholarly_search_adapter import ScholarlySearchAdapter

        _scholarly_search_port = ScholarlySearchAdapter(ai_tracing=ai_tracing)
    elif hasattr(_scholarly_search_port, "ai_tracing"):
        _scholarly_search_port.ai_tracing = ai_tracing
    return _scholarly_search_port


def get_storage() -> IBlobStoragePort:
    """Dependency providing Blob Storage Port instance."""
    return LocalStorageAdapter(base_directory=settings.STORAGE_DIR)


def get_idempotency_port() -> IIdempotencyPort:
    """Dependency providing Idempotency Port singleton instance."""
    global _idempotency_adapter
    if _idempotency_adapter is None:
        try:
            _idempotency_adapter = RedisIdempotencyAdapter(
                redis_url=settings.REDIS_URL,
                fallback=InMemoryIdempotencyAdapter(),
            )
        except Exception:
            _idempotency_adapter = InMemoryIdempotencyAdapter()
    return _idempotency_adapter


def get_document_summarizer() -> IDocumentSummarizerPort:
    """Dependency providing LLMGroundedSummarizer with heuristic fallback."""
    api_key = settings.OPENAI_API_KEY.get_secret_value() if settings.OPENAI_API_KEY else None
    return LLMGroundedSummarizer(
        api_key=api_key,
        base_url=settings.OPENAI_BASE_URL,
        model=settings.OPENAI_MODEL,
        fallback=HeuristicGroundedSummarizer(),
    )


def get_embedding_service() -> EmbeddingService | None:
    """Dependency providing EmbeddingService instance if configured."""
    try:
        return EmbeddingService()
    except Exception:
        return None


def get_document_service(
    storage: IBlobStoragePort = Depends(get_storage),
    summarizer: IDocumentSummarizerPort = Depends(get_document_summarizer),
    ai_tracing: AITracingService = Depends(get_ai_tracing_service),
    embedding_service: EmbeddingService | None = Depends(get_embedding_service),
) -> DocumentService:
    """Dependency providing DocumentService instance."""
    real_storage = get_storage() if hasattr(storage, "dependency") else storage
    real_summarizer = get_document_summarizer() if hasattr(summarizer, "dependency") else summarizer
    real_ai_tracing = get_ai_tracing_service() if hasattr(ai_tracing, "dependency") else ai_tracing
    real_embedding = (
        get_embedding_service() if hasattr(embedding_service, "dependency") else embedding_service
    )
    return DocumentService(
        storage=real_storage,
        summarizer=real_summarizer,
        ai_tracing=real_ai_tracing,
        embedding_service=real_embedding,
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
    embedding_service: EmbeddingService | None = Depends(get_embedding_service),
) -> SessionChatService:
    """Dependency providing SessionChatService instance bound to request database session."""
    real_ai_tracing = get_ai_tracing_service() if hasattr(ai_tracing, "dependency") else ai_tracing
    real_embedding = (
        get_embedding_service() if hasattr(embedding_service, "dependency") else embedding_service
    )
    return SessionChatService(db=db, ai_tracing=real_ai_tracing, embedding_service=real_embedding)


def get_note_service(
    db: AsyncSession = Depends(get_db),
) -> NoteService:
    """Dependency providing NoteService instance bound to request database session."""
    return NoteService(db=db)


def get_auth_service(
    db: AsyncSession = Depends(get_db),
) -> AuthService:
    """Dependency providing AuthService bound to request database session."""
    return AuthService(db=db)


def get_draft_service(
    db: AsyncSession = Depends(get_db),
    ai_tracing: AITracingService = Depends(get_ai_tracing_service),
) -> DraftService:
    """Dependency providing DraftService bound to request database session."""
    return DraftService(db=db, ai_tracing=ai_tracing)


def get_folder_service(
    db: AsyncSession = Depends(get_db),
) -> FolderService:
    """Dependency providing FolderService bound to request database session."""
    return FolderService(db=db)


def get_wiki_service(
    db: AsyncSession = Depends(get_db),
) -> WikiService:
    """Dependency providing WikiService bound to request database session."""
    return WikiService(db=db)


def get_library_synthesis_service(
    db: AsyncSession = Depends(get_db),
    ai_tracing: AITracingService = Depends(get_ai_tracing_service),
    idempotency_port: IIdempotencyPort = Depends(get_idempotency_port),
) -> LibrarySynthesisService:
    """Dependency providing LibrarySynthesisService bound to request database session."""
    return LibrarySynthesisService(db=db, ai_tracing=ai_tracing, cache=idempotency_port)


def get_graph_rag_service(
    embedding_service: EmbeddingService | None = Depends(get_embedding_service),
) -> GraphRAGService:
    """Dependency providing GraphRAGService for dual-level knowledge graph queries."""
    real_embedding = (
        get_embedding_service() if hasattr(embedding_service, "dependency") else embedding_service
    )
    return GraphRAGService(embedding_service=real_embedding)


def get_graph_extraction_service(
    embedding_service: EmbeddingService | None = Depends(get_embedding_service),
) -> GraphExtractionService:
    """Dependency providing GraphExtractionService for academic graph parsing & ingestion."""
    real_embedding = (
        get_embedding_service() if hasattr(embedding_service, "dependency") else embedding_service
    )
    return GraphExtractionService(embedding_service=real_embedding)


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
    token = None
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
    elif request.query_params.get("token"):
        token = request.query_params.get("token", "").strip()

    if token:
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

    # Restricted fallback compatibility strictly for isolated unit test harness (X-User-Id).
    # Completely blocked in network/live/staging/prod to prevent auth bypass (OWASP BOLA/IDOR).
    is_unit_test_harness = bool(os.environ.get("PYTEST_CURRENT_TEST"))
    if is_unit_test_harness:
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


async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """Retrieve current active authenticated user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "USER_INACTIVE",
                "message": "Tài khoản người dùng đã bị vô hiệu hóa.",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def get_benchmark_runner_service() -> BenchmarkRunnerService:
    """Dependency providing BenchmarkRunnerService instance."""
    return BenchmarkRunnerService()
