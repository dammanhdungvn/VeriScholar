"""FastAPI Dependencies for Services, Storage Ports, and User Context."""

from uuid import UUID

from core.adapters.storage.local import LocalStorageAdapter
from core.ports.storage import IBlobStoragePort
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models.user import UserModel
from api.db.session import get_db
from api.services.document_service import DocumentService

DEFAULT_DEV_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


def get_storage() -> IBlobStoragePort:
    """Dependency providing the configured blob storage port."""
    return LocalStorageAdapter(base_directory="storage/blobs")


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
            email="researcher@verischolar.org",
            full_name="VeriScholar Researcher",
            hashed_password="insecure_dev_password",
            is_active=True,
        )
        db.add(user)
        await db.flush()

    return user
