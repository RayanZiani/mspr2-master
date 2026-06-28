"""Tests unitaires pour la gestion des seuils IoT (siège)."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from conftest import load_siege_service, mock_mappings_result

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "siege"))

pytestmark = pytest.mark.unit

BR_ROW = {
    "id": 1,
    "code": "BR",
    "nom": "Brésil",
    "temperature_ideale_c": 29.0,
    "humidite_ideale_pct": 55.0,
    "tolerance_temperature_c": 3.0,
    "tolerance_humidite_pct": 2.0,
}


def test_row_to_seuils_bresil():
    threshold = load_siege_service("threshold_service")
    seuils = threshold.row_to_seuils(BR_ROW)
    assert seuils.code == "BR"
    assert seuils.slug == "bresil"
    assert seuils.temperature.min == 26.0
    assert seuils.temperature.max == 32.0
    assert seuils.humidity.min == 53.0
    assert seuils.humidity.max == 57.0


def test_seuils_to_dict_structure():
    threshold = load_siege_service("threshold_service")
    seuils = threshold.row_to_seuils(BR_ROW)
    data = threshold.seuils_to_dict(seuils)
    assert data["code"] == "BR"
    assert data["temperature"]["ideal"] == 29.0
    assert data["humidity"]["max"] == 57.0


def test_ranges_to_db_values_roundtrip():
    threshold = load_siege_service("threshold_service")
    values = threshold.ranges_to_db_values(26.0, 32.0, 53.0, 57.0)
    assert values["temperature_ideale_c"] == 29.0
    assert values["tolerance_temperature_c"] == 3.0
    assert values["humidite_ideale_pct"] == 55.0
    assert values["tolerance_humidite_pct"] == 2.0


def test_ranges_to_db_values_rejects_invalid_temp():
    threshold = load_siege_service("threshold_service")
    with pytest.raises(ValueError, match="temperature_min"):
        threshold.ranges_to_db_values(30.0, 30.0, 53.0, 57.0)


def test_ranges_to_db_values_rejects_invalid_humidity():
    threshold = load_siege_service("threshold_service")
    with pytest.raises(ValueError, match="humidity_min"):
        threshold.ranges_to_db_values(26.0, 32.0, 60.0, 55.0)


@pytest.mark.asyncio
async def test_get_pays_seuils_found():
    threshold = load_siege_service("threshold_service")
    session = AsyncMock()
    session.execute = AsyncMock(return_value=mock_mappings_result([BR_ROW]))
    result = await threshold.get_pays_seuils(session, "BR")
    assert result is not None
    assert result.slug == "bresil"


@pytest.mark.asyncio
async def test_get_pays_seuils_not_found():
    threshold = load_siege_service("threshold_service")
    session = AsyncMock()
    session.execute = AsyncMock(return_value=mock_mappings_result([]))
    result = await threshold.get_pays_seuils(session, "XX")
    assert result is None


@pytest.mark.asyncio
async def test_list_pays_seuils():
    threshold = load_siege_service("threshold_service")
    session = AsyncMock()
    session.execute = AsyncMock(return_value=mock_mappings_result([BR_ROW, {**BR_ROW, "code": "EC", "id": 2}]))
    results = await threshold.list_pays_seuils(session)
    assert len(results) == 2
    assert {s.code for s in results} == {"BR", "EC"}


@pytest.mark.asyncio
async def test_update_pays_seuils():
    threshold = load_siege_service("threshold_service")
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    updated_row = {**BR_ROW, "temperature_ideale_c": 30.0, "tolerance_temperature_c": 2.0}

    with patch.object(threshold, "get_pays_seuils", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = threshold.row_to_seuils(updated_row)
        result = await threshold.update_pays_seuils(session, "BR", 28.0, 32.0, 53.0, 57.0)

    session.execute.assert_called_once()
    session.commit.assert_called_once()
    assert result is not None
    assert result.temperature.ideal == 30.0
