import sys
sys.path.insert(0, "pays/bresil")

from api.services.alert_service import check_alerts, is_lot_perime
from datetime import datetime, timedelta


def test_no_alert_within_thresholds():
    assert check_alerts({"temp": 29.0, "humidity": 55.0}) == []


def test_alert_temp_too_high():
    alerts = check_alerts({"temp": 33.0, "humidity": 55.0})
    assert any("température" in a for a in alerts)


def test_alert_humidity_too_low():
    alerts = check_alerts({"temp": 29.0, "humidity": 52.0})
    assert any("humidité" in a for a in alerts)


def test_lot_not_perime():
    assert not is_lot_perime(datetime.utcnow() - timedelta(days=100))


def test_lot_perime():
    assert is_lot_perime(datetime.utcnow() - timedelta(days=400))
