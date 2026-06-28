from datetime import datetime

import pytest

from .conftest import IS_RENDER
from .helpers import (
    COUNTRIES,
    fetch_all_mesures,
    fetch_country_alertes,
    fetch_country_lots,
    fetch_lot_detail,
    fetch_mesures_for_lot,
)


@pytest.mark.integration
@pytest.mark.parametrize("pays", COUNTRIES)
def test_country_lots_fifo_order(pays, auth_headers):
    lots = fetch_country_lots(pays, auth_headers)
    if len(lots) < 2:
        pytest.skip(f"Pas assez de lots {pays} pour valider le FIFO")

    dates = []
    for lot in lots:
        raw = lot.get("date_stockage")
        if raw:
            dates.append(datetime.fromisoformat(raw.replace("Z", "+00:00")))
    assert dates == sorted(dates), f"Lots {pays} non triés FIFO"


@pytest.mark.integration
@pytest.mark.parametrize("pays", COUNTRIES)
def test_country_lot_detail(pays, auth_headers):
    lots = fetch_country_lots(pays, auth_headers)
    if not lots:
        pytest.skip(f"Aucun lot {pays}")

    lot_id = lots[0]["id"]
    detail = fetch_lot_detail(lot_id, pays)
    if detail is not None:
        assert detail.get("id") == lot_id
        return

    lot = lots[0]
    assert lot.get("id") == lot_id
    assert "date_stockage" in lot or "statut" in lot


@pytest.mark.integration
@pytest.mark.parametrize("pays", COUNTRIES)
def test_country_alertes_endpoint(pays, auth_headers):
    alertes = fetch_country_alertes(pays, auth_headers)
    assert isinstance(alertes, list)


@pytest.mark.integration
def test_bresil_mesures_filter_by_lot(bresil_lot_id, auth_headers):
    filtered = fetch_mesures_for_lot(bresil_lot_id, "bresil", auth_headers)
    assert isinstance(filtered, list)
    if filtered:
        assert all(m.get("lot_id") == bresil_lot_id for m in filtered)

    if IS_RENDER:
        return

    all_mesures = fetch_all_mesures("bresil", auth_headers)
    assert len(filtered) <= len(all_mesures)


@pytest.mark.integration
def test_bresil_mesures_newest_first(bresil_lot_id, auth_headers):
    mesures = fetch_mesures_for_lot(bresil_lot_id, "bresil", auth_headers)
    if len(mesures) < 2:
        pytest.skip("Pas assez de mesures pour valider le tri")

    timestamps = [
        datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00"))
        for m in mesures
        if m.get("timestamp")
    ]
    assert timestamps == sorted(timestamps, reverse=True)
