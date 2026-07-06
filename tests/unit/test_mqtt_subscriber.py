"""Tests unitaires pour le subscriber MQTT (pays)."""

import json
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from conftest import COUNTRIES, load_pays_service, reset_mqtt_state

pytestmark = pytest.mark.unit


@pytest.fixture(params=COUNTRIES)
def mqtt(request):
    mod = load_pays_service(request.param, "mqtt_subscriber")
    reset_mqtt_state(mod)
    return mod


class TestParseTimestamp:
    def test_iso8601_string(self, mqtt):
        ts = mqtt._parse_timestamp("2025-06-01T12:00:00Z")
        assert ts.year == 2025
        assert ts.month == 6

    def test_unix_epoch_string(self, mqtt):
        ts = mqtt._parse_timestamp("1609459200")
        assert isinstance(ts, datetime)

    def test_none_returns_now(self, mqtt):
        before = datetime.now(timezone.utc).replace(tzinfo=None)
        ts = mqtt._parse_timestamp(None)
        after = datetime.now(timezone.utc).replace(tzinfo=None)
        assert before <= ts <= after

    def test_invalid_returns_now(self, mqtt):
        ts = mqtt._parse_timestamp("not-a-date")
        assert isinstance(ts, datetime)


class TestCapteurStatus:
    def test_connected_within_timeout(self, mqtt):
        mqtt._last_seen["ent-a"] = datetime.now(timezone.utc)
        status = mqtt.get_capteur_status()
        assert status["ent-a"]["connected"] is True
        assert status["ent-a"]["age_seconds"] == 0

    def test_disconnected_after_timeout(self, mqtt):
        mqtt.CAPTEUR_TIMEOUT_SECONDS = 60
        mqtt._last_seen["ent-b"] = datetime.now(timezone.utc) - timedelta(seconds=120)
        status = mqtt.get_capteur_status()
        assert status["ent-b"]["connected"] is False
        assert status["ent-b"]["age_seconds"] >= 120


class TestHandleStatusMessage:
    def test_online_from_offline_notifies(self, mqtt):
        mqtt._capteur_connected["ent-a"] = False
        with patch("asyncio.run") as mock_run:
            mqtt._handle_status_message("ent-a", {"status": "online", "source": "simulator"})
        mock_run.assert_called_once()
        assert mqtt._capteur_connected["ent-a"] is True

    def test_offline_from_connected_notifies(self, mqtt):
        mqtt._capteur_connected["ent-a"] = True
        with patch("asyncio.run") as mock_run:
            mqtt._handle_status_message("ent-a", {"status": "offline", "source": "lwt"})
        mock_run.assert_called_once()
        assert mqtt._capteur_connected["ent-a"] is False

    def test_online_while_already_online_no_notify(self, mqtt):
        mqtt._capteur_connected["ent-a"] = True
        with patch("asyncio.run") as mock_run:
            mqtt._handle_status_message("ent-a", {"status": "online", "source": "simulator"})
        mock_run.assert_not_called()


class TestOnMessage:
    def _make_msg(self, topic: str, payload: dict):
        msg = MagicMock()
        msg.topic = topic
        msg.payload = json.dumps(payload).encode()
        return msg

    def test_ignores_short_topic(self, mqtt):
        with patch("asyncio.run") as mock_run:
            mqtt.on_message(None, None, self._make_msg("futurekawa/bresil", {}))
        mock_run.assert_not_called()

    def test_ignores_invalid_json(self, mqtt):
        msg = MagicMock()
        msg.topic = "futurekawa/bresil/ent-a/sensors"
        msg.payload = b"not-json"
        with patch("asyncio.run") as mock_run:
            mqtt.on_message(None, None, msg)
        mock_run.assert_not_called()

    def test_sensors_message_triggers_persist(self, mqtt):
        payload = {"temp": 29.0, "humidity": 55.0, "timestamp": "2025-01-01T00:00:00Z"}
        with patch.object(mqtt, "_persist", new_callable=AsyncMock) as mock_persist:
            with patch("asyncio.run") as mock_run:
                mock_run.side_effect = lambda coro: None
                mqtt.on_message(
                    None, None,
                    self._make_msg("futurekawa/bresil/ent-a/sensors", payload),
                )
        mock_run.assert_called()

    def test_status_message_delegates(self, mqtt):
        with patch.object(mqtt, "_handle_status_message") as mock_handle:
            mqtt.on_message(
                None, None,
                self._make_msg("futurekawa/bresil/ent-a/status", {"status": "online"}),
            )
        mock_handle.assert_called_once_with("ent-a", {"status": "online"})


class TestPersist:
    @pytest.mark.asyncio
    async def test_skips_when_temp_or_humidity_missing(self, mqtt):
        await mqtt._persist({"temp": 29.0}, "ent-a")
        # Pas d'exception, retour immédiat

    @pytest.mark.asyncio
    async def test_notifies_on_conforme_to_alerte_transition(self, mqtt):
        mock_lot = MagicMock()
        mock_lot.statut = "conforme"
        mock_lot.date_stockage = datetime.utcnow() - timedelta(days=10)
        mock_lot.id = "lot-abc-12345"

        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_lot)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_lot
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_cm.__aexit__ = AsyncMock(return_value=None)

        payload = {"temp": 40.0, "humidity": 55.0, "lot_id": "lot-abc-12345", "timestamp": "2025-01-01T00:00:00Z"}

        with patch.object(mqtt, "SessionLocal", return_value=mock_cm):
            with patch.object(mqtt, "notify", new_callable=AsyncMock) as mock_notify:
                await mqtt._persist(payload, "ent-a")

        mock_notify.assert_called_once()
        mock_session.commit.assert_called_once()


@pytest.mark.parametrize("country", COUNTRIES)
def test_module_loads_for_each_country(country):
    mod = load_pays_service(country, "mqtt_subscriber")
    assert hasattr(mod, "get_capteur_status")
    assert hasattr(mod, "on_message")
