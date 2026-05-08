import asyncio
import httpx
from api.config import API_URLS
from api.services.redis_cache import get_cache, set_cache


async def fetch_pays(client: httpx.AsyncClient, pays: str, endpoint: str) -> dict:
    url = f"{API_URLS[pays]}/{endpoint}"
    response = await client.get(url, timeout=10.0)
    response.raise_for_status()
    return {"pays": pays, "data": response.json()}


async def fetch_all_pays(endpoint: str) -> list[dict]:
    cache_key = f"aggregator:{endpoint}"
    cached = await get_cache(cache_key)
    if cached:
        return cached

    async with httpx.AsyncClient() as client:
        tasks = [fetch_pays(client, pays, endpoint) for pays in API_URLS]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    data = [r for r in results if not isinstance(r, Exception)]
    await set_cache(cache_key, data)
    return data
