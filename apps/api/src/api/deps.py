"""FastAPI Dependencies for Services, Storage Ports, and User Context."""

from uuid import UUID

from core.adapters.cache.idempotency import InMemoryIdempotencyAdapter, RedisIdempotencyAdapter
from core.adapters.storage.local import LocalStorageAdapter
from core.ports.idempotency import IIdempotencyPort
from core.ports.storage import IBlobStoragePort
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import settings
from api.db.models.user import UserModel
from api.db.session import get_db
from api.services.document_service import DocumentService

DEFAULT_DEV_USER_ID = UUID("00000000-0000-0000-0000-000000000001")

_idempotency_adapter: IIdempotencyPort | None = None


def get_storage() -> IBlobStoragePort:
    """Dependency providing the configured blob storage port."""
    return LocalStorageAdapter(base_directory=settings.STORAGE_DIR)


def get_idempotency_port() -> IIdempotencyPort:
    """Dependency providing the configured idempotency port (Redis with in-memory fallback)."""
    global _idempotency_adapter
    if _idempotency_adapter is None:
        _idempotency_adapter = RedisIdempotencyAdapter(
            redis_url="redis://localhost:6379/0",
            fallback=InMemoryIdempotencyAdapter(),
        )
    return _idempotency_adapter


def get_document_service(
    storage: IBlobStoragePort = Depends(get_storage),
) -> DocumentService:
    """Dependency providing DocumentService with bound storage port."""
    return DocumentService(storage=storage)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
) -> UserModel:
    """Provide authenticated user, or ensure deterministic seed user for development/Swagger."""
    stmt = select(UserModel).where(UserModel.id == DEFAULT_DEV_USER_ID)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        user = UserModel(
            id=DEFAULT_DEV_USER_ID,
            email="developer@verischolar.org",
            display_name="VeriScholar Developer",
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user
