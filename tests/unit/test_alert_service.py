from datetime import datetime, timedelta

import pytest

ROOT_IMPORT = True  # noqa: marker for encoding utf-8

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pays" / "bresil"))

pytestmark = pytest.mark.unit

from api.services.alert_service import check_alerts, is_lot_perime


def test_no_alert_within_thresholds():
    assert check_alerts({"temp": 29.0, "humidity": 55.0}) == []


def test_alert_temp_too_high():
    alerts = check_alerts({"temp": 33.0, "humidity": 55.0})
    assert len(alerts) == 1
    assert "33" in alerts[0]
    assert "29" in alerts[0]
    assert "temp" in alerts[0].lower()


def test_alert_temp_too_low():
    alerts = check_alerts({"temp": 24.0, "humidity": 55.0})
    assert len(alerts) == 1
    assert "temp" in alerts[0].lower()


def test_alert_humidity_too_low():
    alerts = check_alerts({"temp": 29.0, "humidity": 52.0})
    assert len(alerts) == 1
    assert "humidit" in alerts[0].lower()


def test_alert_humidity_too_high():
    alerts = check_alerts({"temp": 29.0, "humidity": 60.0})
    assert len(alerts) == 1
    assert "humidit" in alerts[0].lower()


@pytest.mark.parametrize("temp", [26.0, 32.0])
def test_temp_at_exact_tolerance_boundary_no_alert(temp):
    """+-3C autour de 29C : pas d'alerte aux bornes incluses."""
    assert check_alerts({"temp": temp, "humidity": 55.0}) == []


@pytest.mark.parametrize("humidity", [53.0, 57.0])
def test_humidity_at_exact_tolerance_boundary_no_alert(humidity):
    assert check_alerts({"temp": 29.0, "humidity": humidity}) == []


def test_both_sensors_out_of_range_returns_two_alerts():
    alerts = check_alerts({"temp": 40.0, "humidity": 40.0})
    assert len(alerts) == 2


def test_only_temp_checked_when_humidity_missing():
    alerts = check_alerts({"temp": 40.0})
    assert len(alerts) == 1
    assert "temp" in alerts[0].lower()


def test_lot_not_perime():
    assert not is_lot_perime(datetime.utcnow() - timedelta(days=100))


def test_lot_perime():
    assert is_lot_perime(datetime.utcnow() - timedelta(days=400))


def test_lot_exactly_at_peremption_limit_not_perime():
    assert not is_lot_perime(datetime.utcnow() - timedelta(days=365))
