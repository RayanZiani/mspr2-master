import os

import httpx
import pytest

# Utiliser les URLs Render par défaut (toujours disponibles)
API_BRESIL = os.getenv("API_BRESIL_URL", "https://futurekawa-api-bresil.onrender.com")
API_EQUATEUR = os.getenv("API_EQUATEUR_URL", "https://futurekawa-api-equateur.onrender.com")
API_COLOMBIE = os.getenv("API_COLOMBIE_URL", "https://futurekawa-api-colombie.onrender.com")
API_SIEGE = os.getenv("API_SIEGE_URL", "https://futurekawa-api-siege.onrender.com")

E2E_USER = os.getenv("E2E_USER", "admin_siege")
E2E_PASSWORD = os.getenv("E2E_PASSWORD", "Admin@2025!")

USERS = {
    "admin": ("admin_siege", "Admin@2025!"),
    "siege_user": ("direction_siege", "Direction@2025!"),
    "bresil_user": ("resp_bresil", "Bresil@2025!"),
}


def _login(username: str, password: str) -> dict:
    response = httpx.post(
        f"{API_SIEGE}/auth/login",
        json={"username": username, "password": password},
        timeout=15.0,
    )
    assert response.status_code == 200, response.text
    return response.json()


@pytest.fixture(scope="session")
def siege_token():
    return _login(E2E_USER, E2E_PASSWORD)["access_token"]


@pytest.fixture(scope="session")
def auth_headers(siege_token):
    return {"Authorization": f"Bearer {siege_token}"}


@pytest.fixture(scope="session")
def siege_user_headers():
    token = _login(*USERS["siege_user"])["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def first_lot_id(auth_headers):
    response = httpx.get(f"{API_SIEGE}/stocks/", headers=auth_headers, timeout=15.0)
    assert response.status_code == 200
    for country in response.json():
        for lot in country.get("data") or []:
            lot_id = lot.get("id")
            if lot_id:
                return lot_id
    pytest.skip("Aucun lot en base")


@pytest.fixture(scope="session")
def bresil_lot_id():
    response = httpx.get(f"{API_BRESIL}/lots/", timeout=10.0)
    assert response.status_code == 200
    lots = response.json()
    if not lots:
        pytest.skip("Aucun lot Brésil en base")
    return lots[0]["id"]
