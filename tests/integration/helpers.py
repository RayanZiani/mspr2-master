"""Accès aux données pays : API directe (Docker) ou agrégation siège (Render)."""

from __future__ import annotations

import httpx

from .conftest import (
    API_BRESIL,
    API_COLOMBIE,
    API_EQUATEUR,
    API_SIEGE,
    IS_RENDER,
    _request_with_retry,
)

COUNTRY_BASE = {
    "bresil": API_BRESIL,
    "equateur": API_EQUATEUR,
    "colombie": API_COLOMBIE,
}

COUNTRIES = list(COUNTRY_BASE)


def fetch_country_lots(pays: str, auth_headers: dict | None = None) -> list:
    if IS_RENDER:
        if not auth_headers:
            raise ValueError("auth_headers requis sur Render")
        response = _request_with_retry(
            "GET",
            f"{API_SIEGE}/stocks/",
            headers=auth_headers,
            timeout=15.0,
        )
        assert response.status_code == 200, response.text
        block = next((entry for entry in response.json() if entry.get("pays") == pays), None)
        if block is None:
            return []
        return block.get("data") or []

    response = _request_with_retry(
        "GET",
        f"{COUNTRY_BASE[pays]}/lots/",
        timeout=10.0,
    )
    assert response.status_code == 200, response.text
    return response.json()


def fetch_country_alertes(pays: str, auth_headers: dict | None = None) -> list:
    if IS_RENDER:
        if not auth_headers:
            raise ValueError("auth_headers requis sur Render")
        response = _request_with_retry(
            "GET",
            f"{API_SIEGE}/alertes/",
            headers=auth_headers,
            timeout=15.0,
        )
        assert response.status_code == 200, response.text
        return [alerte for alerte in response.json() if alerte.get("pays") == pays]

    response = _request_with_retry(
        "GET",
        f"{COUNTRY_BASE[pays]}/alertes/",
        timeout=10.0,
    )
    assert response.status_code == 200, response.text
    return response.json()


def fetch_mesures_for_lot(
    lot_id: str,
    pays: str = "bresil",
    auth_headers: dict | None = None,
) -> list:
    if IS_RENDER:
        if not auth_headers:
            raise ValueError("auth_headers requis sur Render")
        response = _request_with_retry(
            "GET",
            f"{API_SIEGE}/mesures/",
            params={"lot_id": lot_id},
            headers=auth_headers,
            timeout=15.0,
        )
    else:
        response = _request_with_retry(
            "GET",
            f"{COUNTRY_BASE[pays]}/mesures/",
            params={"lot_id": lot_id},
            timeout=15.0,
        )
    assert response.status_code == 200, response.text
    return response.json()


def fetch_all_mesures(pays: str = "bresil", auth_headers: dict | None = None) -> list:
    if IS_RENDER:
        if not auth_headers:
            raise ValueError("auth_headers requis sur Render")
        response = _request_with_retry(
            "GET",
            f"{API_SIEGE}/mesures/",
            headers=auth_headers,
            timeout=15.0,
        )
    else:
        response = _request_with_retry(
            "GET",
            f"{COUNTRY_BASE[pays]}/mesures/",
            timeout=15.0,
        )
    assert response.status_code == 200, response.text
    return response.json()


def assert_country_health(pays: str, auth_headers: dict | None = None) -> None:
    if IS_RENDER:
        if not auth_headers:
            raise ValueError("auth_headers requis sur Render")
        health = _request_with_retry("GET", f"{API_SIEGE}/health", timeout=15.0)
        assert health.status_code == 200, health.text
        assert health.json().get("status") == "ok"

        stocks = _request_with_retry(
            "GET",
            f"{API_SIEGE}/stocks/",
            headers=auth_headers,
            timeout=15.0,
        )
        assert stocks.status_code == 200, stocks.text
        pays_codes = {entry.get("pays") for entry in stocks.json()}
        assert pays in pays_codes
        return

    response = _request_with_retry(
        "GET",
        f"{COUNTRY_BASE[pays]}/health",
        timeout=10.0,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload.get("status") == "ok"
    assert payload.get("pays") == pays


def fetch_lot_detail(lot_id: str, pays: str) -> dict | None:
    if IS_RENDER:
        return None
    response = _request_with_retry(
        "GET",
        f"{COUNTRY_BASE[pays]}/lots/{lot_id}",
        timeout=10.0,
    )
    assert response.status_code == 200, response.text
    return response.json()
