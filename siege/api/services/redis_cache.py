"""Cache Redis optionnel pour l'API siège."""

import json

import redis.asyncio as aioredis
from redis.exceptions import RedisError

from api.config import REDIS_URL, REDIS_CACHE_TTL

STOCKS_CACHE_PREFIX = "siege:stocks"

# Connexion Redis optionnelle
try:
    redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    redis_available = True
except (OSError, RedisError, ValueError):
    redis_client = None
    redis_available = False


async def get_cache(key: str):
    """Récupère une valeur du cache Redis. Retourne None si Redis n'est pas disponible."""
    if not redis_available or redis_client is None:
        return None
    try:
        value = await redis_client.get(key)
        return json.loads(value) if value else None
    except (RedisError, json.JSONDecodeError):
        # Si Redis échoue, on continue sans cache
        return None


async def set_cache(key: str, data, ttl: int | None = None) -> None:
    """Sauvegarde une valeur dans Redis. Ne fait rien si Redis n'est pas disponible."""
    if not redis_available or redis_client is None:
        return
    try:
        await redis_client.setex(key, ttl if ttl is not None else REDIS_CACHE_TTL, json.dumps(data))
    except (RedisError, TypeError):
        # Si Redis échoue, on continue sans cache
        pass


async def delete_cache_prefix(prefix: str) -> None:
    """Supprime les cles Redis commencant par prefix (ex: STOCKS_CACHE_PREFIX)."""
    if not redis_available or redis_client is None:
        return
    try:
        async for key in redis_client.scan_iter(match=f"{prefix}*"):
            await redis_client.delete(key)
    except RedisError:
        pass
