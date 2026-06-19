import os
import time

import httpx
import pytest

# Détection de l'environnement Render
IS_RENDER = os.getenv("RENDER", "").lower() == "true"

# Utiliser les URLs Render par défaut (backend centralisé)
# Sur Render, seul le backend Siège est déployé, pas les APIs pays séparées
API_SIEGE = os.getenv("API_SIEGE_URL", "https://mspr2-master.onrender.com")

# Les APIs pays ne sont déployées séparément qu'en local Docker
# Sur Render, utiliser l'API Siège pour tout
API_BRESIL = os.getenv("API_BRESIL_URL", "http://localhost:8001")
API_EQUATEUR = os.getenv("API_EQUATEUR_URL", "http://localhost:8002")
API_COLOMBIE = os.getenv("API_COLOMBIE_URL", "http://localhost:8003")

E2E_USER = os.getenv("E2E_USER", "admin_siege")
E2E_PASSWORD = os.getenv("E2E_PASSWORD", "Admin@2025!")

# Codes HTTP transitoires (cold start Render, redémarrage, gateway)
RETRYABLE_STATUS = {502, 503, 504}
RENDER_MAX_ATTEMPTS = int(os.getenv("RENDER_RETRY_ATTEMPTS", "6"))
RENDER_RETRY_DELAY = float(os.getenv("RENDER_RETRY_DELAY", "3"))

# Marker pour skip les tests qui ne fonctionnent pas sur Render
skip_on_render = pytest.mark.skipif(
    IS_RENDER,
    reason="APIs pays non déployées séparément sur Render - utiliser l'API Siège"
)

USERS = {
    "admin": ("admin_siege", "Admin@2025!"),
    "siege_user": ("direction_siege", "Direction@2025!"),
    "bresil_user": ("resp_bresil", "Bresil@2025!"),
}


def _request_with_retry(method: str, url: str, **kwargs) -> httpx.Response:
    """Réessaie les requêtes en cas d'erreur transitoire (502/503/504)."""
    max_attempts = RENDER_MAX_ATTEMPTS if IS_RENDER else 1
    last_response = None

    for attempt in range(1, max_attempts + 1):
        try:
            response = httpx.request(method, url, **kwargs)
        except httpx.RequestError:
            if attempt >= max_attempts:
                raise
            time.sleep(RENDER_RETRY_DELAY)
            continue

        if response.status_code not in RETRYABLE_STATUS:
            return response

        last_response = response
        if attempt < max_attempts:
            time.sleep(RENDER_RETRY_DELAY)

    return last_response


def _wait_for_api_ready() -> None:
    """Attend que l'API Siège réponde correctement avant les tests."""
    health_url = f"{API_SIEGE}/health"
    login_url = f"{API_SIEGE}/auth/login"
    max_attempts = 12 if IS_RENDER else 3

    for attempt in range(1, max_attempts + 1):
        try:
            health = httpx.get(health_url, timeout=15.0)
            if health.status_code != 200:
                raise RuntimeError(f"health -> {health.status_code}")

            login = httpx.post(
                login_url,
                json={"username": E2E_USER, "password": E2E_PASSWORD},
                timeout=15.0,
            )
            if login.status_code == 200:
                return
            if login.status_code not in RETRYABLE_STATUS:
                raise RuntimeError(f"login -> {login.status_code}: {login.text}")
        except (httpx.RequestError, RuntimeError):
            if attempt >= max_attempts:
                pytest.fail(f"API Siège indisponible après {max_attempts} tentatives: {API_SIEGE}")
            time.sleep(5)


@pytest.fixture(scope="session", autouse=True)
def ensure_api_ready():
    _wait_for_api_ready()


def _login(username: str, password: str) -> dict:
    response = _request_with_retry(
        "POST",
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
    if IS_RENDER:
        pytest.skip("API Brésil non déployée sur Render - utiliser l'API Siège")
    response = httpx.get(f"{API_BRESIL}/lots/", timeout=10.0)
    assert response.status_code == 200
    lots = response.json()
    if not lots:
        pytest.skip("Aucun lot Brésil en base")
    return lots[0]["id"]
