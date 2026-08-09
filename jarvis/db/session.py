from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator
from jarvis.core.config import settings

# Motor asíncrono para PostgreSQL
engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True
)

# Fábrica de sesiones asíncronas
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependencia generadora para inyectar la sesión de base de datos asíncrona.
    """
    async with AsyncSessionLocal() as session:
        yield session
