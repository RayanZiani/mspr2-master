"""Agrégation HTTP des APIs pays (mode local docker-compose)."""

import asyncio

import httpx

from api.config import API_URLS
from api.services.redis_cache import get_cache, set_cache


async def fetch_pays(
    client: httpx.AsyncClient,
    pays: str,
    endpoint: str,
    params: dict | None = None,
) -> dict:
    """Appelle un endpoint d'une API pays."""
    url = f"{API_URLS[pays]}/{endpoint}"
    response = await client.get(url, params=params, timeout=10.0)
    response.raise_for_status()
    return {"pays": pays, "data": response.json()}


async def fetch_all_pays(endpoint: str, params: dict | None = None) -> list[dict]:
    """Interroge toutes les APIs pays en parallèle avec cache Redis."""
    cache_key = f"aggregator:{endpoint}"
    if not params:
        cached = await get_cache(cache_key)
        if cached:
            return cached

    async with httpx.AsyncClient() as client:
        tasks = [fetch_pays(client, pays, endpoint, params) for pays in API_URLS]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    data = [r for r in results if not isinstance(r, Exception)]
    if not params:
        await set_cache(cache_key, data)
    return data
