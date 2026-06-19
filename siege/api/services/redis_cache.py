import json
import redis.asyncio as aioredis
from api.config import REDIS_URL, REDIS_CACHE_TTL

# Connexion Redis optionnelle
try:
    _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    _redis_available = True
except Exception:
    _redis = None
    _redis_available = False


async def get_cache(key: str):
    """Récupère une valeur du cache Redis. Retourne None si Redis n'est pas disponible."""
    if not _redis_available or _redis is None:
        return None
    try:
        value = await _redis.get(key)
        return json.loads(value) if value else None
    except Exception:
        # Si Redis échoue, on continue sans cache
        return None


async def set_cache(key: str, data, ttl: int | None = None) -> None:
    """Sauvegarde une valeur dans Redis. Ne fait rien si Redis n'est pas disponible."""
    if not _redis_available or _redis is None:
        return
    try:
        await _redis.setex(key, ttl if ttl is not None else REDIS_CACHE_TTL, json.dumps(data))
    except Exception:
        # Si Redis échoue, on continue sans cache
        pass
