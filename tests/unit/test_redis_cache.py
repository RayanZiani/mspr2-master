"""Tests unitaires pour le cache Redis (siège)."""

import importlib
import json
from unittest.mock import AsyncMock, patch

import pytest
from redis.exceptions import RedisError

from conftest import load_siege_config

pytestmark = pytest.mark.unit


@pytest.fixture
def redis_module():
    load_siege_config()
    import api.services.redis_cache as mod
    return importlib.reload(mod)


@pytest.mark.asyncio
async def test_get_cache_returns_none_when_redis_unavailable(redis_module):
    with patch.object(redis_module, "redis_available", False):
        assert await redis_module.get_cache("key") is None


@pytest.mark.asyncio
async def test_get_cache_hit(redis_module):
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=json.dumps({"data": 1}))
    with patch.object(redis_module, "redis_available", True):
        with patch.object(redis_module, "redis_client", mock_client):
            result = await redis_module.get_cache("siege:stocks")
    assert result == {"data": 1}


@pytest.mark.asyncio
async def test_get_cache_miss(redis_module):
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=None)
    with patch.object(redis_module, "redis_available", True):
        with patch.object(redis_module, "redis_client", mock_client):
            result = await redis_module.get_cache("missing")
    assert result is None


@pytest.mark.asyncio
async def test_get_cache_redis_error_returns_none(redis_module):
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=RedisError("down"))
    with patch.object(redis_module, "redis_available", True):
        with patch.object(redis_module, "redis_client", mock_client):
            result = await redis_module.get_cache("key")
    assert result is None


@pytest.mark.asyncio
async def test_set_cache_uses_default_ttl(redis_module):
    mock_client = AsyncMock()
    mock_client.setex = AsyncMock()
    with patch.object(redis_module, "redis_available", True):
        with patch.object(redis_module, "redis_client", mock_client):
            with patch.object(redis_module, "REDIS_CACHE_TTL", 60):
                await redis_module.set_cache("key", {"a": 1})
    mock_client.setex.assert_called_once()
    args = mock_client.setex.call_args[0]
    assert args[0] == "key"
    assert args[1] == 60


@pytest.mark.asyncio
async def test_set_cache_custom_ttl(redis_module):
    mock_client = AsyncMock()
    mock_client.setex = AsyncMock()
    with patch.object(redis_module, "redis_available", True):
        with patch.object(redis_module, "redis_client", mock_client):
            await redis_module.set_cache("key", [1, 2], ttl=30)
    assert mock_client.setex.call_args[0][1] == 30


@pytest.mark.asyncio
async def test_get_cache_unavailable_at_import():
    """Couvre le chemin d'initialisation Redis indisponible."""
    load_siege_config()
    with patch("api.services.redis_cache.aioredis.from_url", side_effect=OSError("refused")):
        import api.services.redis_cache as mod
        reloaded = importlib.reload(mod)
    assert reloaded.redis_available is False
    assert await reloaded.get_cache("key") is None


@pytest.mark.asyncio
async def test_delete_cache_prefix(redis_module):
    mock_client = AsyncMock()

    async def scan_iter(*_args, **_kwargs):
        for key in ("siege:stocks:1", "siege:stocks:2"):
            yield key

    mock_client.scan_iter = scan_iter
    mock_client.delete = AsyncMock()
    with patch.object(redis_module, "redis_available", True):
        with patch.object(redis_module, "redis_client", mock_client):
            await redis_module.delete_cache_prefix("siege:stocks")
    assert mock_client.delete.await_count == 2
