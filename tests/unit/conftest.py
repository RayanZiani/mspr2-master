"""Fixtures et helpers partagés pour les tests unitaires."""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import AsyncMock

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]

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


def load_alert_service(country: str):
    """Charge alert_service d'un pays en isolant api.config."""
    for name in list(sys.modules):
        if name == "api.config" or name.startswith(f"api.config.{country}"):
            del sys.modules[name]

    config_path = ROOT / "pays" / country / "api" / "config.py"
    config_spec = importlib.util.spec_from_file_location(f"api.config.{country}", config_path)
    config_module = importlib.util.module_from_spec(config_spec)
    assert config_spec.loader is not None
    config_spec.loader.exec_module(config_module)
    sys.modules["api.config"] = config_module

    module_path = ROOT / "pays" / country / "api" / "services" / "alert_service.py"
    spec = importlib.util.spec_from_file_location(f"alert_service_{country}", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_aggregator_module():
    """Charge aggregator siège avec redis mocké."""
    for name in list(sys.modules):
        if name == "api" or name.startswith("api."):
            del sys.modules[name]

    siege_path = str(ROOT / "siege")
    if siege_path not in sys.path:
        sys.path.insert(0, siege_path)

    config_path = ROOT / "siege" / "api" / "config.py"
    config_spec = importlib.util.spec_from_file_location("api.config", config_path)
    config_module = importlib.util.module_from_spec(config_spec)
    assert config_spec.loader is not None
    config_spec.loader.exec_module(config_module)
    sys.modules["api.config"] = config_module

    redis_cache = ModuleType("api.services.redis_cache")
    redis_cache.get_cache = AsyncMock(return_value=None)
    redis_cache.set_cache = AsyncMock()
    sys.modules["api.services.redis_cache"] = redis_cache

    module_path = ROOT / "siege" / "api" / "services" / "aggregator.py"
    spec = importlib.util.spec_from_file_location("api.services.aggregator", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    sys.modules["api.services.aggregator"] = module
    return module
