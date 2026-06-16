import pytest

from conftest import CDC_THRESHOLDS, load_alert_service

pytestmark = pytest.mark.unit

COUNTRY_THRESHOLDS = [
    ("bresil", 29.0, 55.0),
    ("equateur", 31.0, 60.0),
    ("colombie", 26.0, 80.0),
]


@pytest.mark.parametrize("country,temp_ok,hum_ok", COUNTRY_THRESHOLDS)
def test_no_alert_at_ideal_thresholds(country, temp_ok, hum_ok):
    alert_service = load_alert_service(country)
    assert alert_service.check_alerts({"temp": temp_ok, "humidity": hum_ok}) == []


@pytest.mark.parametrize("country,temp_bad,hum_ok", [
    ("bresil", 33.5, 55.0),
    ("equateur", 35.0, 60.0),
    ("colombie", 30.0, 80.0),
])
def test_temp_alert_per_country(country, temp_bad, hum_ok):
    alert_service = load_alert_service(country)
    alerts = alert_service.check_alerts({"temp": temp_bad, "humidity": hum_ok})
    assert any("temp" in alert.lower() for alert in alerts)


@pytest.mark.parametrize("country,temp_ok,hum_bad", [
    ("bresil", 29.0, 50.0),
    ("equateur", 31.0, 55.0),
    ("colombie", 26.0, 75.0),
])
def test_humidity_alert_per_country(country, temp_ok, hum_bad):
    alert_service = load_alert_service(country)
    alerts = alert_service.check_alerts({"temp": temp_ok, "humidity": hum_bad})
    assert any("humidit" in alert.lower() for alert in alerts)


@pytest.mark.parametrize("country", CDC_THRESHOLDS)
def test_lot_perime_after_one_year(country):
    from datetime import datetime, timedelta

    alert_service = load_alert_service(country)
    assert alert_service.is_lot_perime(datetime.utcnow() - timedelta(days=400))
