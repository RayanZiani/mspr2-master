import httpx
import pytest

from .conftest import API_BRESIL, API_EQUATEUR, API_COLOMBIE, API_SIEGE


@pytest.mark.integration
@pytest.mark.parametrize(
    "url,pays",
    [
        (f"{API_BRESIL}/health", "bresil"),
        (f"{API_EQUATEUR}/health", "equateur"),
        (f"{API_COLOMBIE}/health", "colombie"),
    ],
)
def test_country_health(url, pays):
    response = httpx.get(url, timeout=10.0)
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("status") == "ok"
    assert payload.get("pays") == pays


@pytest.mark.integration
def test_siege_health():
    response = httpx.get(f"{API_SIEGE}/health", timeout=10.0)
    assert response.status_code == 200
    body = response.json()
    assert body.get("status") == "ok"
    assert "version" in body or "service" in body or body.get("status") == "ok"


@pytest.mark.integration
@pytest.mark.parametrize("base_url", [API_BRESIL, API_EQUATEUR, API_COLOMBIE])
def test_country_lots_endpoint_returns_list(base_url):
    response = httpx.get(f"{base_url}/lots/", timeout=10.0)
    assert response.status_code == 200
    lots = response.json()
    assert isinstance(lots, list)
    if lots:
        lot = lots[0]
        assert "id" in lot
        assert "date_stockage" in lot or "statut" in lot
