"""Database session factory and FastAPI dependency."""

from collections.abc import AsyncGenerator

from api.core.config import ROOT_DIR, settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.SQL_ECHO,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_sqlite_fallback() -> None:
    """Initializes local SQLite database fallback when PostgreSQL is unreachable."""
    global engine, AsyncSessionLocal
    sqlite_dir = ROOT_DIR / "storage"
    sqlite_dir.mkdir(parents=True, exist_ok=True)
    sqlite_url = f"sqlite+aiosqlite:///{sqlite_dir / 'verischolar.db'}"

    await engine.dispose()
    engine = create_async_engine(
        sqlite_url,
        echo=settings.SQL_ECHO,
    )
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional asynchronous database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
