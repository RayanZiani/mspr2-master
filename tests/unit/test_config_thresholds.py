import importlib.util
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]

CDC_THRESHOLDS = {
    "bresil": {"temp": 29.0, "humidity": 55.0, "tol_temp": 3.0, "tol_hum": 2.0},
    "equateur": {"temp": 31.0, "humidity": 60.0, "tol_temp": 3.0, "tol_hum": 2.0},
    "colombie": {"temp": 26.0, "humidity": 80.0, "tol_temp": 3.0, "tol_hum": 2.0},
}


def load_alert_service(country: str):
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


@pytest.mark.parametrize("country", CDC_THRESHOLDS)
def test_cdc_thresholds_match_config(country):
    load_alert_service(country)
    config = sys.modules["api.config"]
    expected = CDC_THRESHOLDS[country]
    assert config.SEUIL_TEMP == expected["temp"]
    assert config.SEUIL_HUMIDITY == expected["humidity"]
    assert config.TOLERANCE_TEMP == expected["tol_temp"]
    assert config.TOLERANCE_HUMIDITY == expected["tol_hum"]
    assert config.PEREMPTION_JOURS == 365


@pytest.mark.parametrize("country", CDC_THRESHOLDS)
def test_boundary_temp_within_tolerance_no_alert(country):
    svc = load_alert_service(country)
    t = CDC_THRESHOLDS[country]
    at_limit = t["temp"] + t["tol_temp"]
    assert svc.check_alerts({"temp": at_limit, "humidity": t["humidity"]}) == []


@pytest.mark.parametrize("country", CDC_THRESHOLDS)
def test_boundary_temp_beyond_tolerance_alerts(country):
    svc = load_alert_service(country)
    t = CDC_THRESHOLDS[country]
    beyond = t["temp"] + t["tol_temp"] + 0.1
    alerts = svc.check_alerts({"temp": beyond, "humidity": t["humidity"]})
    assert len(alerts) == 1
    assert "temp" in alerts[0].lower()


@pytest.mark.parametrize("country", CDC_THRESHOLDS)
def test_boundary_humidity_within_tolerance_no_alert(country):
    svc = load_alert_service(country)
    t = CDC_THRESHOLDS[country]
    at_limit = t["humidity"] - t["tol_hum"]
    assert svc.check_alerts({"temp": t["temp"], "humidity": at_limit}) == []


@pytest.mark.parametrize("country", CDC_THRESHOLDS)
def test_dual_alerts_temp_and_humidity(country):
    svc = load_alert_service(country)
    t = CDC_THRESHOLDS[country]
    alerts = svc.check_alerts({
        "temp": t["temp"] + t["tol_temp"] + 5,
        "humidity": t["humidity"] - t["tol_hum"] - 5,
    })
    assert len(alerts) == 2
    lowered = [a.lower() for a in alerts]
    assert any("temp" in a for a in lowered)
    assert any("humidit" in a for a in lowered)


@pytest.mark.parametrize("country", CDC_THRESHOLDS)
def test_missing_sensors_returns_no_alert(country):
    svc = load_alert_service(country)
    assert svc.check_alerts({}) == []
    assert svc.check_alerts({"temp": None, "humidity": None}) == []


@pytest.mark.parametrize("country", CDC_THRESHOLDS)
def test_lot_not_perime_at_364_days(country):
    from datetime import datetime, timedelta

    svc = load_alert_service(country)
    assert not svc.is_lot_perime(datetime.utcnow() - timedelta(days=364))


@pytest.mark.parametrize("country", CDC_THRESHOLDS)
def test_lot_perime_at_366_days(country):
    from datetime import datetime, timedelta

    svc = load_alert_service(country)
    assert svc.is_lot_perime(datetime.utcnow() - timedelta(days=366))
