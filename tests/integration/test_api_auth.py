import httpx
import pytest

from .conftest import API_SIEGE, E2E_PASSWORD, E2E_USER, _request_with_retry


@pytest.mark.integration
def test_login_returns_bearer_token():
    response = _request_with_retry(
        "POST",
        f"{API_SIEGE}/auth/login",
        json={"username": E2E_USER, "password": E2E_PASSWORD},
        timeout=15.0,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["role"] == "ADMIN"
    assert body["username"] == "admin_siege"
    assert len(body["access_token"]) > 20


@pytest.mark.integration
@pytest.mark.parametrize("username,password", [
    ("admin_siege", "wrong-password"),
    ("unknown_user", "Admin@2025!"),
])
def test_login_rejects_invalid_credentials(username, password):
    response = httpx.post(
        f"{API_SIEGE}/auth/login",
        json={"username": username, "password": password},
        timeout=10.0,
    )
    assert response.status_code == 401


@pytest.mark.integration
def test_me_requires_authentication():
    response = httpx.get(f"{API_SIEGE}/auth/me", timeout=10.0)
    assert response.status_code == 401


@pytest.mark.integration
def test_me_rejects_malformed_token():
    response = httpx.get(
        f"{API_SIEGE}/auth/me",
        headers={"Authorization": "Bearer not-valid"},
        timeout=10.0,
    )
    assert response.status_code == 401


@pytest.mark.integration
def test_protected_stocks_requires_auth():
    response = httpx.get(f"{API_SIEGE}/stocks/", timeout=10.0)
    assert response.status_code == 401


@pytest.mark.integration
def test_mesures_requires_lot_id(auth_headers):
    response = httpx.get(f"{API_SIEGE}/mesures/", headers=auth_headers, timeout=10.0)
    assert response.status_code == 400
    assert "lot_id" in response.json().get("detail", "").lower()


@pytest.mark.integration
def test_mesures_unknown_lot_returns_empty_for_admin(auth_headers):
    """L'admin n'a pas de filtre pays : lot inconnu -> liste vide (200)."""
    response = httpx.get(
        f"{API_SIEGE}/mesures/",
        params={"lot_id": "00000000-0000-0000-0000-000000000000"},
        headers=auth_headers,
        timeout=15.0,
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration
def test_siege_user_can_access_stocks(siege_user_headers):
    response = httpx.get(f"{API_SIEGE}/stocks/", headers=siege_user_headers, timeout=15.0)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
