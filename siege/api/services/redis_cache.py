import json
import redis.asyncio as aioredis
from api.config import REDIS_URL, REDIS_CACHE_TTL

_redis = aioredis.from_url(REDIS_URL, decode_responses=True)


async def get_cache(key: str):
    value = await _redis.get(key)
    return json.loads(value) if value else None


async def set_cache(key: str, data) -> None:
    await _redis.setex(key, REDIS_CACHE_TTL, json.dumps(data))
