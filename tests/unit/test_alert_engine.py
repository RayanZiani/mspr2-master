"""Tests unitaires pour le moteur d'alertes siège."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from conftest import load_siege_service, mock_mappings_result

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "siege"))

pytestmark = pytest.mark.unit

CTX_ROW = {
    "id": 1,
    "pays_id": 1,
    "code": "BR",
    "nom": "Brésil",
    "temperature_ideale_c": 29.0,
    "humidite_ideale_pct": 55.0,
    "tolerance_temperature_c": 3.0,
    "tolerance_humidite_pct": 2.0,
    "entrepot_id": "ent-1",
    "entrepot_nom": "Entrepot SP",
}


def _make_seuils():
    threshold = load_siege_service("threshold_service")
    return threshold.row_to_seuils(CTX_ROW)


def test_check_reading_no_alert_in_range():
    engine = load_siege_service("alert_engine")
    seuils = _make_seuils()
    assert engine.check_reading(seuils, 29.0, 55.0) == []


def test_check_reading_temp_out_of_range():
    engine = load_siege_service("alert_engine")
    seuils = _make_seuils()
    alerts = engine.check_reading(seuils, 40.0, 55.0)
    assert len(alerts) == 1
    assert "Temperature" in alerts[0]


def test_check_reading_humidity_out_of_range():
    engine = load_siege_service("alert_engine")
    seuils = _make_seuils()
    alerts = engine.check_reading(seuils, 29.0, 40.0)
    assert len(alerts) == 1
    assert "Humidite" in alerts[0]


def test_check_reading_both_out_of_range():
    engine = load_siege_service("alert_engine")
    seuils = _make_seuils()
    alerts = engine.check_reading(seuils, 40.0, 40.0)
    assert len(alerts) == 2


@pytest.mark.asyncio
async def test_process_releve_unknown_capteur_is_noop():
    engine = load_siege_service("alert_engine")
    session = AsyncMock()
    session.execute = AsyncMock(return_value=mock_mappings_result([]))
    await engine.process_releve_for_capteur(session, "unknown", 40.0, 40.0)
    session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_process_releve_no_lot_is_noop():
    engine = load_siege_service("alert_engine")
    session = AsyncMock()
    session.execute = AsyncMock(
        side_effect=[
            mock_mappings_result([CTX_ROW]),
            mock_mappings_result([]),
        ]
    )
    await engine.process_releve_for_capteur(session, "cap-1", 40.0, 40.0)
    session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_process_releve_conforme_to_alerte():
    engine = load_siege_service("alert_engine")
    lot_row = {"id": "lot-abc-123", "statut": "CONFORME"}
    session = AsyncMock()
    session.execute = AsyncMock(
        side_effect=[
            mock_mappings_result([CTX_ROW]),
            mock_mappings_result([lot_row]),
            AsyncMock(),
            AsyncMock(),
        ]
    )
    session.commit = AsyncMock()

    with patch("api.services.alert_engine.send_condition_alert", new_callable=AsyncMock) as mock_notify:
        await engine.process_releve_for_capteur(session, "cap-1", 40.0, 40.0)

    assert session.execute.call_count == 4
    session.commit.assert_called_once()
    mock_notify.assert_called_once()


@pytest.mark.asyncio
async def test_process_releve_alerte_to_conforme():
    engine = load_siege_service("alert_engine")
    lot_row = {"id": "lot-abc-123", "statut": "ALERTE"}
    session = AsyncMock()
    session.execute = AsyncMock(
        side_effect=[
            mock_mappings_result([CTX_ROW]),
            mock_mappings_result([lot_row]),
            AsyncMock(),
        ]
    )
    session.commit = AsyncMock()

    with patch("api.services.alert_engine.send_condition_alert", new_callable=AsyncMock) as mock_notify:
        await engine.process_releve_for_capteur(session, "cap-1", 29.0, 55.0)

    session.commit.assert_called_once()
    mock_notify.assert_not_called()


@pytest.mark.asyncio
async def test_process_releve_stays_alerte_no_duplicate():
    engine = load_siege_service("alert_engine")
    lot_row = {"id": "lot-abc-123", "statut": "ALERTE"}
    session = AsyncMock()
    session.execute = AsyncMock(
        side_effect=[
            mock_mappings_result([CTX_ROW]),
            mock_mappings_result([lot_row]),
        ]
    )
    session.commit = AsyncMock()

    with patch("api.services.alert_engine.send_condition_alert", new_callable=AsyncMock) as mock_notify:
        await engine.process_releve_for_capteur(session, "cap-1", 40.0, 40.0)

    session.commit.assert_not_called()
    mock_notify.assert_not_called()
