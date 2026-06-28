"""Fixtures et helpers partagés pour les tests unitaires."""

import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import AsyncMock, MagicMock

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]
COUNTRIES = ("bresil", "colombie", "equateur")


def pytest_configure(config):
    # URLs réseau Docker interne — injectées via .env en CI, défauts pour pytest local
    os.environ.setdefault("API_BRESIL_URL", "http://api-bresil:8000")
    os.environ.setdefault("API_EQUATEUR_URL", "http://api-equateur:8000")
    os.environ.setdefault("API_COLOMBIE_URL", "http://api-colombie:8000")

# Seuils CDC (plan_tests.md §2)
CDC_THRESHOLDS = {
    "bresil": {"temp": 29.0, "humidity": 55.0, "tol_temp": 3.0, "tol_hum": 2.0},
    "equateur": {"temp": 31.0, "humidity": 60.0, "tol_temp": 3.0, "tol_hum": 2.0},
    "colombie": {"temp": 26.0, "humidity": 80.0, "tol_temp": 3.0, "tol_hum": 2.0},
}


@pytest.fixture
def sample_mesure():
    return {
        "temp": 29.0,
        "humidity": 55.0,
        "timestamp": "2025-01-01T00:00:00Z",
        "lot_id": "test-lot",
    }


def _clear_api_modules(prefix: str = "api") -> None:
    for name in list(sys.modules):
        if name == prefix or name.startswith(f"{prefix}."):
            del sys.modules[name]


def _ensure_path(path: Path) -> None:
    """Place le chemin en tête de sys.path pour garantir le bon package api."""
    path_str = str(path)
    if path_str in sys.path:
        sys.path.remove(path_str)
    sys.path.insert(0, path_str)


def _load_module_from_path(module_name: str, module_path: Path):
    """Charge un module Python et l'enregistre dans sys.modules avant exec (dataclasses)."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _mock_siege_db() -> None:
    db_module = ModuleType("api.db.database")
    db_module.SessionLocal = MagicMock()
    db_module.get_session = MagicMock()
    sys.modules["api.db.database"] = db_module


def load_pays_config(country: str):
    """Charge api.config d'un pays et l'enregistre dans sys.modules."""
    _clear_api_modules()
    _ensure_path(ROOT / "pays" / country)
    config_path = ROOT / "pays" / country / "api" / "config.py"
    config_spec = importlib.util.spec_from_file_location("api.config", config_path)
    config_module = importlib.util.module_from_spec(config_spec)
    assert config_spec.loader is not None
    config_spec.loader.exec_module(config_module)
    sys.modules["api.config"] = config_module
    return config_module


def load_pays_service(country: str, service: str):
    """Charge un module api.services.{service} pour un pays donné."""
    load_pays_config(country)
    module_path = ROOT / "pays" / country / "api" / "services" / f"{service}.py"
    module_name = f"api.services.{service}"
    return _load_module_from_path(module_name, module_path)


def load_alert_service(country: str):
    """Charge alert_service d'un pays en isolant api.config."""
    return load_pays_service(country, "alert_service")


def load_webhook_service(country: str = "bresil"):
    """Charge webhook_service d'un pays."""
    return load_pays_service(country, "webhook_service")


def load_siege_config():
    """Charge api.config siège."""
    _clear_api_modules()
    _ensure_path(ROOT / "siege")
    config_path = ROOT / "siege" / "api" / "config.py"
    config_spec = importlib.util.spec_from_file_location("api.config", config_path)
    config_module = importlib.util.module_from_spec(config_spec)
    assert config_spec.loader is not None
    config_spec.loader.exec_module(config_module)
    sys.modules["api.config"] = config_module
    return config_module


def load_siege_service(service: str, *, mock_redis: bool = False, mock_db: bool = False):
    """Charge un module api.services.{service} du siège."""
    load_siege_config()
    if mock_db or service in ("auth_service", "data_service"):
        _mock_siege_db()
    if mock_redis or service in ("aggregator", "data_service"):
        redis_cache = ModuleType("api.services.redis_cache")
        redis_cache.get_cache = AsyncMock(return_value=None)
        redis_cache.set_cache = AsyncMock()
        redis_cache.delete_cache_prefix = AsyncMock()
        sys.modules["api.services.redis_cache"] = redis_cache

    module_path = ROOT / "siege" / "api" / "services" / f"{service}.py"
    module_name = f"api.services.{service}"
    return _load_module_from_path(module_name, module_path)


def load_aggregator_module():
    """Charge aggregator siège avec redis mocké."""
    return load_siege_service("aggregator", mock_redis=True)


def reset_mqtt_state(mqtt_module) -> None:
    """Réinitialise l'état global du subscriber MQTT entre les tests."""
    mqtt_module._last_seen.clear()
    mqtt_module._capteur_connected.clear()


def make_async_client_mock(mock_resp):
    """Crée un mock httpx.AsyncClient utilisable comme context manager async."""
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=None)
    return mock_cm, mock_client


def mock_mappings_result(rows: list[dict]):
    """Simule le résultat SQLAlchemy result.mappings()."""
    result = MagicMock()
    mappings = MagicMock()
    if len(rows) == 1:
        mappings.first.return_value = rows[0]
    else:
        mappings.first.return_value = rows[0] if rows else None
    mappings.all.return_value = rows
    result.mappings.return_value = mappings
    return result
