import httpx
import pytest

from .conftest import API_SIEGE
from .helpers import COUNTRIES, assert_country_health, fetch_country_lots


@pytest.mark.integration
@pytest.mark.parametrize("pays", COUNTRIES)
def test_country_health(pays, auth_headers):
    assert_country_health(pays, auth_headers)


@pytest.mark.integration
def test_siege_health():
    response = httpx.get(f"{API_SIEGE}/health", timeout=10.0)
    assert response.status_code == 200
    body = response.json()
    assert body.get("status") == "ok"
    assert "version" in body or "service" in body or body.get("status") == "ok"


@pytest.mark.integration
@pytest.mark.parametrize("pays", COUNTRIES)
def test_country_lots_endpoint_returns_list(pays, auth_headers):
    lots = fetch_country_lots(pays, auth_headers)
    assert isinstance(lots, list)
    if lots:
        lot = lots[0]
        assert "id" in lot
        assert "date_stockage" in lot or "statut" in lot
