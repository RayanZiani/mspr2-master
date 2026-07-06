"""Tests unitaires pour data_service (agrégation données siège)."""

import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from conftest import load_siege_service, mock_mappings_result

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "siege"))

pytestmark = pytest.mark.unit

LOT_ROW = {
    "id": "lot-001",
    "pays_code": "BR",
    "exploitation": "Fazenda Aurora",
    "entrepot": "Entrepot SP",
    "date_stockage": datetime(2025, 1, 15, 10, 0, 0),
    "statut": "CONFORME",
}

MESURE_ROW = {
    "id": 42,
    "lot_id": "lot-001",
    "timestamp": datetime(2025, 6, 1, 12, 0, 0),
    "temperature": 28.5,
    "humidity": 54.0,
}


def test_map_lot():
    data = load_siege_service("data_service", mock_db=True, mock_redis=True)
    mapped = data._map_lot(LOT_ROW)
    assert mapped["id"] == "lot-001"
    assert mapped["pays"] == "bresil"
    assert mapped["statut"] == "conforme"
    assert mapped["date_stockage"].startswith("2025-01-15")


def test_map_lot_alerte_statut():
    data = load_siege_service("data_service", mock_db=True, mock_redis=True)
    mapped = data._map_lot({**LOT_ROW, "statut": "ALERTE"})
    assert mapped["statut"] == "alerte"


def test_map_mesure():
    data = load_siege_service("data_service", mock_db=True, mock_redis=True)
    mapped = data._map_mesure(MESURE_ROW)
    assert mapped["lot_id"] == "lot-001"
    assert mapped["temperature"] == 28.5
    assert mapped["humidity"] == 54.0
    assert mapped["timestamp"] == "2025-06-01T12:00:00Z"


def test_dt_iso_handles_none():
    data = load_siege_service("data_service", mock_db=True, mock_redis=True)
    assert data._dt_iso(None) is None


def test_group_by_pays():
    data = load_siege_service("data_service", mock_db=True, mock_redis=True)
    lots = [
        {"pays": "bresil", "id": "1"},
        {"pays": "colombie", "id": "2"},
        {"pays": "bresil", "id": "3"},
    ]
    grouped = data._group_by_pays(lots)
    assert len(grouped) == 2
    bresil_block = next(g for g in grouped if g["pays"] == "bresil")
    assert len(bresil_block["data"]) == 2


@pytest.mark.asyncio
async def test_get_stocks_grouped_uses_cache():
    data = load_siege_service("data_service", mock_db=True, mock_redis=True)
    cached = [{"pays": "bresil", "data": []}]
    with patch.object(data, "get_cache", new_callable=AsyncMock, return_value=cached):
        result = await data.get_stocks_grouped()
    assert result == cached


@pytest.mark.asyncio
async def test_get_stocks_grouped_fetches_and_caches():
    data = load_siege_service("data_service", mock_db=True, mock_redis=True)
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_mappings_result([LOT_ROW]))
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    with patch.object(data, "get_cache", new_callable=AsyncMock, return_value=None):
        with patch.object(data, "set_cache", new_callable=AsyncMock) as mock_set:
            with patch.object(data, "SessionLocal", return_value=mock_cm):
                result = await data.get_stocks_grouped()

    assert len(result) == 1
    assert result[0]["pays"] == "bresil"
    mock_set.assert_called_once()


@pytest.mark.asyncio
async def test_get_mesures_for_lot():
    data = load_siege_service("data_service", mock_db=True, mock_redis=True)
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_mappings_result([MESURE_ROW]))
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    with patch.object(data, "get_cache", new_callable=AsyncMock, return_value=None):
        with patch.object(data, "set_cache", new_callable=AsyncMock) as mock_set:
            with patch.object(data, "SessionLocal", return_value=mock_cm):
                mesures = await data.get_mesures_for_lot("lot-001")

    assert len(mesures) == 1
    assert mesures[0]["temperature"] == 28.5
    mock_set.assert_called_once()


@pytest.mark.asyncio
async def test_get_lot_pays_slug_found():
    data = load_siege_service("data_service", mock_db=True, mock_redis=True)
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_mappings_result([{"pays_code": "EC"}]))
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    with patch.object(data, "SessionLocal", return_value=mock_cm):
        slug = await data.get_lot_pays_slug("lot-001")

    assert slug == "equateur"


@pytest.mark.asyncio
async def test_get_alertes_grouped_filters_non_conforme():
    data = load_siege_service("data_service", mock_db=True, mock_redis=True)
    grouped = [
        {
            "pays": "bresil",
            "data": [
                {"id": "1", "statut": "conforme"},
                {"id": "2", "statut": "alerte"},
            ],
        },
        {
            "pays": "colombie",
            "data": [{"id": "3", "statut": "conforme"}],
        },
    ]
    with patch.object(data, "get_stocks_grouped", new_callable=AsyncMock, return_value=grouped):
        alertes = await data.get_alertes_grouped()

    assert len(alertes) == 1
    assert alertes[0]["pays"] == "bresil"
    assert len(alertes[0]["data"]) == 1
    assert alertes[0]["data"][0]["statut"] == "alerte"
