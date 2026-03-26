import asyncpg
from typing import Optional
from app.core.config import get_settings

settings = get_settings()
_pool: Optional[asyncpg.Pool] = None

async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=settings.database_url,
            min_size=2,
            max_size=10,
        )
    return _pool

async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None

async def get_db():
    """FastAPI dependency — yields a connection from the pool."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        yield conn