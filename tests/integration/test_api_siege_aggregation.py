"""Tests d'intégration pour l'agrégation des données pays via l'API Siège.

Ces tests fonctionnent avec l'API Siège déployée sur Render ou en local.
Sur Render, l'API Siège est le seul point d'entrée pour toutes les données pays.
"""

import httpx
import pytest

from .conftest import API_SIEGE


@pytest.mark.integration
def test_siege_stocks_aggregation_structure(auth_headers):
    """Vérifie que l'API Siège retourne les stocks de tous les pays agrégés."""
    response = httpx.get(f"{API_SIEGE}/stocks/", headers=auth_headers, timeout=15.0)
    assert response.status_code == 200
    
    stocks = response.json()
    assert isinstance(stocks, list)
    
    # Vérifier qu'on a au moins les 3 pays
    pays_codes = {entry.get("pays") for entry in stocks}
    assert "bresil" in pays_codes
    assert "equateur" in pays_codes
    assert "colombie" in pays_codes
    
    # Vérifier la structure de chaque pays
    for entry in stocks:
        assert "pays" in entry
        assert "data" in entry
        assert isinstance(entry["data"], list)


@pytest.mark.integration
def test_siege_stocks_bresil_data_via_aggregation(auth_headers):
    """Teste l'accès aux données du Brésil via l'API Siège."""
    response = httpx.get(f"{API_SIEGE}/stocks/", headers=auth_headers, timeout=15.0)
    assert response.status_code == 200
    
    stocks = response.json()
    bresil_data = next((s for s in stocks if s["pays"] == "bresil"), None)
    
    assert bresil_data is not None
    assert "data" in bresil_data
    assert isinstance(bresil_data["data"], list)
    
    # Vérifier qu'il y a au moins un lot
    if bresil_data["data"]:
        lot = bresil_data["data"][0]
        assert "id" in lot
        # Vérifier qu'il y a des informations de stockage
        assert "date_stockage" in lot or "entrepot" in lot or "exploitation" in lot


@pytest.mark.integration
def test_siege_stocks_equateur_data_via_aggregation(auth_headers):
    """Teste l'accès aux données de l'Équateur via l'API Siège."""
    response = httpx.get(f"{API_SIEGE}/stocks/", headers=auth_headers, timeout=15.0)
    assert response.status_code == 200
    
    stocks = response.json()
    equateur_data = next((s for s in stocks if s["pays"] == "equateur"), None)
    
    assert equateur_data is not None
    assert "data" in equateur_data
    assert isinstance(equateur_data["data"], list)


@pytest.mark.integration
def test_siege_stocks_colombie_data_via_aggregation(auth_headers):
    """Teste l'accès aux données de la Colombie via l'API Siège."""
    response = httpx.get(f"{API_SIEGE}/stocks/", headers=auth_headers, timeout=15.0)
    assert response.status_code == 200
    
    stocks = response.json()
    colombie_data = next((s for s in stocks if s["pays"] == "colombie"), None)
    
    assert colombie_data is not None
    assert "data" in colombie_data
    assert isinstance(colombie_data["data"], list)


@pytest.mark.integration
def test_siege_alertes_all_countries(auth_headers):
    """Vérifie que les alertes de tous les pays sont accessibles via l'API Siège."""
    response = httpx.get(f"{API_SIEGE}/alertes/", headers=auth_headers, timeout=15.0)
    assert response.status_code == 200
    
    alertes = response.json()
    assert isinstance(alertes, list)
    
    # Vérifier que chaque alerte a un champ pays
    for alerte in alertes[:10]:  # Vérifier les 10 premières
        assert "pays" in alerte
        assert alerte["pays"] in ["bresil", "equateur", "colombie"]


@pytest.mark.integration
def test_siege_mesures_aggregation(auth_headers):
    """Vérifie que les mesures IoT sont accessibles via l'API Siège."""
    # D'abord récupérer un lot pour avoir un lot_id
    stocks_response = httpx.get(f"{API_SIEGE}/stocks/", headers=auth_headers, timeout=15.0)
    assert stocks_response.status_code == 200
    
    stocks = stocks_response.json()
    # Trouver le premier lot disponible dans n'importe quel pays
    lot_id = None
    for country_data in stocks:
        if country_data.get("data"):
            lot_id = country_data["data"][0].get("id")
            break
    
    if lot_id:
        # Tester l'accès aux mesures via l'API Siège
        mesures_response = httpx.get(
            f"{API_SIEGE}/mesures/",
            params={"lot_id": lot_id},
            headers=auth_headers,
            timeout=15.0,
        )
        assert mesures_response.status_code == 200
        
        mesures = mesures_response.json()
        assert isinstance(mesures, list)


@pytest.mark.integration
def test_siege_stocks_permission_filtering(auth_headers):
    """Vérifie que les permissions utilisateur sont respectées dans l'agrégation."""
    response = httpx.get(f"{API_SIEGE}/stocks/", headers=auth_headers, timeout=15.0)
    assert response.status_code == 200
    
    stocks = response.json()
    # L'admin_siege devrait voir tous les pays
    pays_codes = {entry.get("pays") for entry in stocks}
    assert len(pays_codes) >= 3


@pytest.mark.integration
def test_siege_stocks_auth_required():
    """Vérifie que l'authentification est requise pour accéder aux stocks."""
    response = httpx.get(f"{API_SIEGE}/stocks/", timeout=10.0)
    assert response.status_code == 401


@pytest.mark.integration
def test_siege_health_public_access():
    """Vérifie que le endpoint health est accessible sans authentification."""
    response = httpx.get(f"{API_SIEGE}/health", timeout=10.0)
    assert response.status_code == 200
    
    health = response.json()
    assert health.get("status") == "ok"
    assert health.get("service") == "siege"
