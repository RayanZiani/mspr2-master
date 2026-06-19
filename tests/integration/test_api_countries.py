from datetime import datetime

import httpx
import pytest

from .conftest import API_BRESIL, API_EQUATEUR, API_COLOMBIE

COUNTRY_APIS = [
    (API_BRESIL, "bresil"),
    (API_EQUATEUR, "equateur"),
    (API_COLOMBIE, "colombie"),
]


@pytest.mark.integration
@pytest.mark.parametrize("base_url,pays", COUNTRY_APIS)
def test_country_lots_fifo_order(base_url, pays):
    response = httpx.get(f"{base_url}/lots/", timeout=10.0)
    assert response.status_code == 200
    lots = response.json()
    if len(lots) < 2:
        pytest.skip(f"Pas assez de lots {pays} pour valider le FIFO")

    dates = []
    for lot in lots:
        raw = lot.get("date_stockage")
        if raw:
            dates.append(datetime.fromisoformat(raw.replace("Z", "+00:00")))
    assert dates == sorted(dates), f"Lots {pays} non triés FIFO"


@pytest.mark.integration
@pytest.mark.parametrize("base_url,pays", COUNTRY_APIS)
def test_country_lot_detail(base_url, pays):
    list_resp = httpx.get(f"{base_url}/lots/", timeout=10.0)
    assert list_resp.status_code == 200
    lots = list_resp.json()
    if not lots:
        pytest.skip(f"Aucun lot {pays}")

    lot_id = lots[0]["id"]
    detail_resp = httpx.get(f"{base_url}/lots/{lot_id}", timeout=10.0)
    assert detail_resp.status_code == 200
    lot = detail_resp.json()
    assert lot is not None
    assert lot.get("id") == lot_id


@pytest.mark.integration
@pytest.mark.parametrize("base_url,pays", COUNTRY_APIS)
def test_country_alertes_endpoint(base_url, pays):
    response = httpx.get(f"{base_url}/alertes/", timeout=10.0)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.integration
def test_bresil_mesures_filter_by_lot(bresil_lot_id):
    all_resp = httpx.get(f"{API_BRESIL}/mesures/", timeout=15.0)
    assert all_resp.status_code == 200
    all_mesures = all_resp.json()

    filtered_resp = httpx.get(
        f"{API_BRESIL}/mesures/",
        params={"lot_id": bresil_lot_id},
        timeout=15.0,
    )
    assert filtered_resp.status_code == 200
    filtered = filtered_resp.json()

    assert len(filtered) <= len(all_mesures)
    if filtered:
        assert all(m.get("lot_id") == bresil_lot_id for m in filtered)


@pytest.mark.integration
def test_bresil_mesures_newest_first(bresil_lot_id):
    response = httpx.get(
        f"{API_BRESIL}/mesures/",
        params={"lot_id": bresil_lot_id},
        timeout=15.0,
    )
    assert response.status_code == 200
    mesures = response.json()
    if len(mesures) < 2:
        pytest.skip("Pas assez de mesures pour valider le tri")

    timestamps = [m.get("timestamp") for m in mesures if m.get("timestamp")]
    assert timestamps == sorted(timestamps, reverse=True)
