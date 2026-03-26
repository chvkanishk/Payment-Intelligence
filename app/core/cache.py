import redis.asyncio as aioredis
import hashlib
import json
from typing import Optional, Any
from app.core.config import get_settings

settings = get_settings()
_redis: Optional[aioredis.Redis] = None

async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis

async def close_redis():
    global _redis
    if _redis:
        await _redis.close()
        _redis = None

def make_cache_key(prefix: str, text: str) -> str:
    digest = hashlib.sha256(text.encode()).hexdigest()[:16]
    return f"{prefix}:{digest}"

async def cache_get(key: str) -> Optional[Any]:
    r = await get_redis()
    value = await r.get(key)
    return json.loads(value) if value else None

async def cache_set(key: str, value: Any, ttl: int = None) -> None:
    r = await get_redis()
    await r.set(key, json.dumps(value), ex=ttl or settings.cache_ttl)