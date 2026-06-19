"""Connexion SQLAlchemy asynchrone pour l'API Brésil."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from api.config import DATABASE_URL


class Base(DeclarativeBase):
    """Base déclarative SQLAlchemy."""


engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    """Crée les tables si nécessaire."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Fournit une session SQLAlchemy par requête."""
    async with SessionLocal() as session:
        yield session
