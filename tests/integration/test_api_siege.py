import httpx
import pytest

from .conftest import API_SIEGE


@pytest.mark.integration
def test_siege_login(auth_headers):
    response = httpx.get(f"{API_SIEGE}/auth/me", headers=auth_headers, timeout=10.0)
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("username") == "admin_siege"
    assert payload.get("role") == "ADMIN"
    assert payload.get("email") == "admin@futurekawa.com"


@pytest.mark.integration
def test_siege_stocks_aggreges(auth_headers):
    response = httpx.get(f"{API_SIEGE}/stocks/", headers=auth_headers, timeout=15.0)
    assert response.status_code == 200
    stocks = response.json()
    assert isinstance(stocks, list)
    assert len(stocks) >= 1
    for entry in stocks:
        assert "pays" in entry
        assert "data" in entry
        assert isinstance(entry["data"], list)


@pytest.mark.integration
def test_siege_stocks_contains_all_countries(auth_headers):
    response = httpx.get(f"{API_SIEGE}/stocks/", headers=auth_headers, timeout=15.0)
    pays_codes = {entry.get("pays") for entry in response.json()}
    assert {"bresil", "equateur", "colombie"}.issubset(pays_codes)


@pytest.mark.integration
def test_siege_alertes(auth_headers):
    response = httpx.get(f"{API_SIEGE}/alertes/", headers=auth_headers, timeout=15.0)
    assert response.status_code == 200
    alertes = response.json()
    assert isinstance(alertes, list)
    for alerte in alertes[:3]:
        assert "pays" in alerte


@pytest.mark.integration
def test_siege_mesures(auth_headers, first_lot_id):
    response = httpx.get(
        f"{API_SIEGE}/mesures/",
        params={"lot_id": first_lot_id},
        headers=auth_headers,
        timeout=15.0,
    )
    assert response.status_code == 200
    mesures = response.json()
    assert isinstance(mesures, list)
    if mesures:
        sample = mesures[0]
        assert "temperature" in sample or "temp" in sample or "timestamp" in sample


@pytest.mark.integration
def test_siege_users_list_admin_only(auth_headers):
    response = httpx.get(f"{API_SIEGE}/users/", headers=auth_headers, timeout=15.0)
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert any(u.get("username") == "admin_siege" for u in users)


@pytest.mark.integration
def test_siege_users_forbidden_for_siege_user(siege_user_headers):
    response = httpx.get(f"{API_SIEGE}/users/", headers=siege_user_headers, timeout=15.0)
    assert response.status_code == 403
