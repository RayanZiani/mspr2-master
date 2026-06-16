import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from conftest import load_aggregator_module

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "siege"))


@pytest.mark.asyncio
async def test_fetch_pays_returns_payload():
    aggregator = load_aggregator_module()

    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": "lot-1"}]
    mock_response.raise_for_status = MagicMock()

    client = AsyncMock()
    client.get.return_value = mock_response

    result = await aggregator.fetch_pays(client, "bresil", "lots/")

    assert result == {"pays": "bresil", "data": [{"id": "lot-1"}]}
    client.get.assert_called_once()
    call_kwargs = client.get.call_args
    assert "lots/" in call_kwargs[0][0]
    assert call_kwargs[1]["timeout"] == 10.0


@pytest.mark.asyncio
async def test_fetch_pays_propagates_http_errors():
    aggregator = load_aggregator_module()

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404", request=MagicMock(), response=MagicMock()
    )

    client = AsyncMock()
    client.get.return_value = mock_response

    with pytest.raises(httpx.HTTPStatusError):
        await aggregator.fetch_pays(client, "bresil", "lots/")


@pytest.mark.asyncio
async def test_fetch_all_pays_ignores_failed_country():
    aggregator = load_aggregator_module()

    async def fetch_side_effect(client, pays, endpoint, params=None):
        if pays == "equateur":
            raise ConnectionError("down")
        return {"pays": pays, "data": []}

    with patch.object(aggregator, "fetch_pays", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = fetch_side_effect
        results = await aggregator.fetch_all_pays("lots/")

    assert len(results) == 2
    assert {r["pays"] for r in results} == {"bresil", "colombie"}


@pytest.mark.asyncio
async def test_fetch_all_pays_uses_cache_when_available():
    aggregator = load_aggregator_module()
    cached = [{"pays": "bresil", "data": [{"id": "cached"}]}]

    with patch.object(aggregator, "get_cache", new_callable=AsyncMock) as mock_cache:
        mock_cache.return_value = cached
        with patch.object(aggregator, "fetch_pays", new_callable=AsyncMock) as mock_fetch:
            results = await aggregator.fetch_all_pays("stocks/")

    assert results == cached
    mock_fetch.assert_not_called()


@pytest.mark.asyncio
async def test_fetch_all_pays_skips_cache_when_params_present():
    aggregator = load_aggregator_module()
    ok = {"pays": "bresil", "data": []}

    with patch.object(aggregator, "get_cache", new_callable=AsyncMock) as mock_cache:
        with patch.object(aggregator, "fetch_pays", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = ok
            await aggregator.fetch_all_pays("mesures/", params={"lot_id": "x"})

    mock_cache.assert_not_called()


@pytest.mark.asyncio
async def test_fetch_all_pays_writes_cache_after_fetch():
    aggregator = load_aggregator_module()

    async def fetch_side_effect(client, pays, endpoint, params=None):
        return {"pays": pays, "data": []}

    with patch.object(aggregator, "fetch_pays", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = fetch_side_effect
        with patch.object(aggregator, "set_cache", new_callable=AsyncMock) as mock_set:
            results = await aggregator.fetch_all_pays("alertes/")

    assert len(results) == 3
    mock_set.assert_called_once()
    cache_key, cached_data = mock_set.call_args[0]
    assert cache_key == "aggregator:alertes/"
    assert len(cached_data) == 3
